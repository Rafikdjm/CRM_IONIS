import json
import logging
from typing import List, Optional

import pg8000.dbapi
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

import schemas
from config import settings
from database import get_db
from routers.cleanup import _write_audit_log
from routers.demandes_rgpd import _anonymiser_compte
from security import require_admin_api_key, require_owner_or_admin
from utils import normalize_academic_slug, refuser_compte_anonymise, rows_to_dicts

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/etudiants", tags=["Étudiants"])

ACADEMIC_EMAIL_DOMAIN = settings.academic_email_domain

# Colonnes du profil étendu (à maintenir en cohérence avec la migration 002)
_EXTENDED_COLUMNS = (
    "e.address, e.city, e.country, e.linkedin, "
    "e.availability_status, e.skills"
)

# Statut de disponibilité : champ obligatoire du profil alumni
# (à maintenir en cohérence avec la migration 002 et le frontend Mon Profil)
_VALID_AVAILABILITY_STATUS = {"en_poste", "a_lecoute", "en_recherche"}


def _validate_availability_status(value: str | None) -> None:
    """Valide le statut de disponibilité d'un profil alumni.

    Champ obligatoire : refuse les valeurs vides/null (422) et les valeurs
    inconnues, pour ne pas dépendre de la seule validation frontend.
    """
    if value is None or str(value).strip() == "":
        raise HTTPException(
            status_code=422,
            detail="Le statut de disponibilité est obligatoire.",
        )
    if value not in _VALID_AVAILABILITY_STATUS:
        raise HTTPException(
            status_code=422,
            detail=(
                "Statut de disponibilité invalide. Valeurs attendues : "
                "en_poste, a_lecoute, en_recherche."
            ),
        )


def _email_academique_exists(cursor, email: str, exclude_id: int | None = None) -> bool:
    """Indique si un email académique est déjà pris, hors étudiant exclu."""
    if exclude_id is None:
        cursor.execute(
            "SELECT 1 FROM ETUDIANT WHERE email_academique = %s;",
            (email,),
        )
    else:
        cursor.execute(
            "SELECT 1 FROM ETUDIANT WHERE email_academique = %s AND id_etudiant <> %s;",
            (email, exclude_id),
        )
    return cursor.fetchone() is not None


def _email_personnel_exists(cursor, email: str, exclude_id: int | None = None) -> bool:
    """Indique si l'email personnel est déjà pris, hors étudiant exclu."""
    if exclude_id is None:
        cursor.execute(
            "SELECT 1 FROM ETUDIANT WHERE email = %s;",
            (email,),
        )
    else:
        cursor.execute(
            "SELECT 1 FROM ETUDIANT WHERE email = %s AND id_etudiant <> %s;",
            (email, exclude_id),
        )
    return cursor.fetchone() is not None


def _promotion_existe(cursor, id_promotion: int) -> bool:
    """Indique si une promotion existe."""
    cursor.execute("SELECT 1 FROM PROMOTION WHERE id_promotion = %s;", (id_promotion,))
    return cursor.fetchone() is not None


def _integrity_error_response(exc) -> tuple[int, str] | None:
    """Retourne (status, message) explicite selon la contrainte réellement
    violée, ou None si la cause n'est pas identifiable.

    Filet de sécurité : les pré-checks (email, email_academique, id_promotion)
    couvrent le cas nominal, mais une violation peut encore survenir en cas de
    course (TOCTOU) entre le SELECT et l'INSERT — le message doit alors
    refléter la vraie cause, pas un message passe-partout.
    """
    msg = str(exc)
    if "etudiant_email_key" in msg:
        return (409, "Cet email est déjà utilisé par un autre étudiant.")
    if "etudiant_email_academique_key" in msg:
        return (409, "Cet email académique est déjà utilisé par un autre étudiant.")
    if "etudiant_id_promotion_fkey" in msg:
        return (422, "La promotion spécifiée n'existe pas.")
    return None


def _resolve_email_academique(
    cursor,
    prenom: str,
    nom: str,
    provided: str | None,
    exclude_id: int | None = None,
) -> str | None:
    """Résout la valeur de email_academique à persister.

    - Si aucun email n'est fourni, ou que celui-ci correspond à l'email
      auto-généré à partir du prénom/nom (pré-remplissage frontend), on
      génère "prenom.nom@ionis-stm.com" et, en cas de doublon, on ajoute un
      suffixe numérique : prenom.nom2@…, prenom.nom3@… jusqu'à une valeur libre.
    - Si l'étudiant a fourni manuellement une autre valeur, on respecte son
      choix mais on refuse l'enregistrement (422) si elle est déjà prise par
      un autre étudiant.
    """
    slug_prenom = normalize_academic_slug(prenom)
    slug_nom = normalize_academic_slug(nom)
    base = f"{slug_prenom}.{slug_nom}" if slug_prenom and slug_nom else ""
    candidate = (provided or "").strip().lower()

    if base:
        auto_generated = f"{base}@{ACADEMIC_EMAIL_DOMAIN}"
        if not candidate or candidate == auto_generated:
            candidate = auto_generated
            suffix = 2
            while _email_academique_exists(cursor, candidate, exclude_id):
                candidate = f"{base}{suffix}@{ACADEMIC_EMAIL_DOMAIN}"
                suffix += 1
            return candidate

    if candidate and _email_academique_exists(cursor, candidate, exclude_id):
        raise HTTPException(
            status_code=422,
            detail=(
                "Cet email académique est déjà utilisé par un autre étudiant. "
                "Choisissez-en un autre."
            ),
        )
    return candidate or None


@router.post("/", response_model=schemas.Etudiant, status_code=status.HTTP_201_CREATED)
def create_etudiant(etudiant: schemas.EtudiantCreate, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        # Le statut de disponibilité est validé dès qu'une valeur est fournie
        # (même règle que PUT/PATCH). Non fourni -> valeur par défaut ''.
        if etudiant.availability_status:
            _validate_availability_status(etudiant.availability_status)

        # Pré-checks explicites avant insertion : email personnel unique et
        # promotion existante (les IntegrityError restent le filet de secours).
        if _email_personnel_exists(cursor, etudiant.email):
            raise HTTPException(
                status_code=409,
                detail="Cet email est déjà utilisé par un autre étudiant.",
            )
        if not _promotion_existe(cursor, etudiant.id_promotion):
            raise HTTPException(
                status_code=422,
                detail="La promotion spécifiée n'existe pas.",
            )

        email_academique = _resolve_email_academique(
            cursor, etudiant.prenom, etudiant.nom, etudiant.email_academique
        )
        skills_json = json.dumps(etudiant.skills) if etudiant.skills else '[]'
        query = """
            INSERT INTO ETUDIANT (nom, prenom, email, email_academique, telephone,
                                   date_naissance, parcours_anterieur, date_inscription, id_promotion,
                                   address, city, country, linkedin, availability_status, skills)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s::jsonb) RETURNING id_etudiant;
        """
        cursor.execute(query, (
            etudiant.nom, etudiant.prenom, etudiant.email, email_academique,
            etudiant.telephone, etudiant.date_naissance, etudiant.parcours_anterieur,
            etudiant.date_inscription, etudiant.id_promotion,
            etudiant.address or "", etudiant.city or "", etudiant.country or "",
            etudiant.linkedin or "", etudiant.availability_status or "", skills_json,
        ))
        id_generated = cursor.fetchone()[0]
        db.commit()

        # Réponse alignée sur ce qui est réellement persisté (les champs
        # optionnels nuls/absents retombent sur les défauts du schéma).
        persisted = etudiant.model_dump()
        persisted.update({
            "email_academique": email_academique,
            "id_etudiant": id_generated,
            "address": etudiant.address or "",
            "city": etudiant.city or "",
            "country": etudiant.country or "",
            "linkedin": etudiant.linkedin or "",
            "availability_status": etudiant.availability_status or "",
            "skills": etudiant.skills or [],
        })
        return persisted
    except HTTPException:
        db.rollback()
        raise
    except pg8000.dbapi.IntegrityError as exc:
        db.rollback()
        response = _integrity_error_response(exc)
        if response:
            raise HTTPException(status_code=response[0], detail=response[1])
        raise HTTPException(
            status_code=400,
            detail="Impossible de créer l'étudiant (contrainte de base violée).",
        )
    except Exception:
        db.rollback()
        logger.exception("Erreur lors de la création d'un étudiant")
        raise HTTPException(status_code=400, detail="Impossible de créer l'étudiant.")
    finally:
        cursor.close()


@router.get("/", response_model=schemas.PaginatedResponse[schemas.Etudiant], dependencies=[Depends(require_admin_api_key)])
def get_all_etudiants(
    search: Optional[str] = Query(None, description="Recherche par nom, prénom ou email"),
    id_promotion: Optional[int] = Query(None, description="Filtrer par ID promotion"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1),
    db=Depends(get_db),
):
    cursor = db.cursor()
    try:
        base_query = """
            FROM ETUDIANT e
            LEFT JOIN PROMOTION p ON e.id_promotion = p.id_promotion
            WHERE 1=1
        """
        params: list = []

        if search:
            base_query += """
                AND (
                    e.nom ILIKE %s OR e.prenom ILIKE %s
                    OR e.email ILIKE %s
                    OR (e.nom || ' ' || e.prenom) ILIKE %s
                )
            """
            like = f"%{search}%"
            params.extend([like, like, like, like])

        if id_promotion is not None:
            base_query += " AND e.id_promotion = %s"
            params.append(id_promotion)

        # Compte total
        cursor.execute(f"SELECT COUNT(*) {base_query}", tuple(params))
        total = cursor.fetchone()[0]

        # Données paginées
        data_query = f"""
            SELECT e.id_etudiant, e.nom, e.prenom, e.email, e.email_academique,
                   e.telephone, e.date_naissance, e.parcours_anterieur,
                   e.date_inscription, e.id_promotion,
                   {_EXTENDED_COLUMNS}
            {base_query}
            ORDER BY e.nom, e.prenom
            OFFSET %s LIMIT %s
        """
        params.extend([skip, limit])
        cursor.execute(data_query, tuple(params))
        items = rows_to_dicts(cursor, cursor.fetchall())

        return schemas.PaginatedResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_next=(skip + limit) < total,
        )
    except Exception:
        logger.exception("Erreur lors de la récupération des étudiants")
        raise HTTPException(status_code=400, detail="Impossible de récupérer les étudiants.")
    finally:
        cursor.close()


@router.get("/{id_etudiant}", response_model=schemas.EtudiantDetail)
def get_etudiant_detail(id_etudiant: int, db=Depends(get_db), _auth=Depends(require_owner_or_admin)):
    cursor = db.cursor()
    try:
        cursor.execute(
            f"""
            SELECT e.id_etudiant, e.nom, e.prenom, e.email, e.email_academique,
                   e.telephone, e.date_naissance, e.parcours_anterieur,
                   e.date_inscription, e.id_promotion,
                   {_EXTENDED_COLUMNS},
                   p.nom_promotion,
                   ent.nom_entreprise,
                   ent.secteur_activite,
                   (SELECT COUNT(*) FROM EXPERIENCE_PRO WHERE id_etudiant = e.id_etudiant),
                   e.date_anonymisation
            FROM ETUDIANT e
            LEFT JOIN PROMOTION p ON e.id_promotion = p.id_promotion
            LEFT JOIN EXPERIENCE_PRO exp ON e.id_etudiant = exp.id_etudiant AND exp.poste_actuel = TRUE
            LEFT JOIN ENTREPRISE ent ON exp.id_entreprise = ent.id_entreprise
            WHERE e.id_etudiant = %s;
            """,
            (id_etudiant,),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Étudiant introuvable.")

        columns = [desc[0] for desc in cursor.description]
        data = dict(zip(columns, row))

        # Parser skills depuis JSONB (peut revenir comme str ou list selon pg8000)
        raw_skills = data.get("skills") or []
        if isinstance(raw_skills, str):
            try:
                raw_skills = json.loads(raw_skills)
            except (json.JSONDecodeError, TypeError):
                raw_skills = []

        return schemas.EtudiantDetail(
            id_etudiant=data["id_etudiant"],
            nom=data["nom"],
            prenom=data["prenom"],
            email=data["email"],
            email_academique=data.get("email_academique"),
            telephone=data["telephone"],
            date_naissance=data["date_naissance"],
            parcours_anterieur=data["parcours_anterieur"],
            date_inscription=data["date_inscription"],
            id_promotion=data["id_promotion"],
            promotion_nom=data.get("nom_promotion"),
            entreprise_actuelle=data.get("nom_entreprise"),
            experiences_count=data.get("count", 0),
            secteur_activite=data.get("secteur_activite") or "",
            address=data.get("address", ""),
            city=data.get("city", ""),
            country=data.get("country", ""),
            linkedin=data.get("linkedin", ""),
            availability_status=data.get("availability_status", ""),
            skills=raw_skills,
            date_anonymisation=data.get("date_anonymisation"),
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("Erreur lors de la récupération de l'étudiant %s", id_etudiant)
        raise HTTPException(status_code=400, detail="Impossible de récupérer l'étudiant.")
    finally:
        cursor.close()


@router.put("/{id_etudiant}", response_model=schemas.Etudiant)
def update_etudiant(id_etudiant: int, etudiant: schemas.EtudiantCreate, db=Depends(get_db), _auth=Depends(require_owner_or_admin)):
    cursor = db.cursor()
    try:
        refuser_compte_anonymise(cursor, id_etudiant)
        _validate_availability_status(etudiant.availability_status)
        if _email_personnel_exists(cursor, etudiant.email, exclude_id=id_etudiant):
            raise HTTPException(
                status_code=409,
                detail="Cet email est déjà utilisé par un autre étudiant.",
            )
        if not _promotion_existe(cursor, etudiant.id_promotion):
            raise HTTPException(
                status_code=422,
                detail="La promotion spécifiée n'existe pas.",
            )
        email_academique = _resolve_email_academique(
            cursor, etudiant.prenom, etudiant.nom, etudiant.email_academique,
            exclude_id=id_etudiant,
        )
        # Serializer les skills en JSONB
        skills_json = json.dumps(etudiant.skills) if etudiant.skills else '[]'
        query = """
            UPDATE ETUDIANT
            SET nom = %s, prenom = %s, email = %s, email_academique = %s,
                telephone = %s, date_naissance = %s, parcours_anterieur = %s,
                date_inscription = %s, id_promotion = %s,
                address = %s, city = %s, country = %s, linkedin = %s,
                availability_status = %s, skills = %s::jsonb
            WHERE id_etudiant = %s;
        """
        cursor.execute(query, (
            etudiant.nom, etudiant.prenom, etudiant.email, email_academique,
            etudiant.telephone, etudiant.date_naissance, etudiant.parcours_anterieur,
            etudiant.date_inscription, etudiant.id_promotion,
            etudiant.address, etudiant.city, etudiant.country, etudiant.linkedin,
            etudiant.availability_status, skills_json,
            id_etudiant,
        ))
        if cursor.rowcount == 0:
            db.rollback()
            raise HTTPException(status_code=404, detail="Étudiant introuvable.")
        db.commit()
        return {**etudiant.model_dump(), "email_academique": email_academique, "id_etudiant": id_etudiant}
    except HTTPException:
        raise
    except pg8000.dbapi.IntegrityError as exc:
        db.rollback()
        response = _integrity_error_response(exc)
        if response:
            raise HTTPException(status_code=response[0], detail=response[1])
        raise HTTPException(status_code=400, detail="Contrainte de base violée lors de la mise à jour.")
    except Exception:
        db.rollback()
        logger.exception("Erreur lors de la mise à jour d'un étudiant")
        raise HTTPException(status_code=400, detail="Impossible de mettre à jour l'étudiant.")
    finally:
        cursor.close()


@router.patch("/{id_etudiant}", response_model=schemas.EtudiantDetail)
def partial_update_etudiant(id_etudiant: int, updates: schemas.EtudiantUpdate, db=Depends(get_db), _auth=Depends(require_owner_or_admin)):
    """Mise à jour partielle : seul les champs fournis (non-null) sont modifiés."""
    cursor = db.cursor()
    try:
        # Vérifie l'existence ET refuse les comptes déjà anonymisés (RGPD).
        refuser_compte_anonymise(cursor, id_etudiant)

        payload = updates.model_dump(exclude_unset=True, exclude_defaults=False)
        if not payload:
            raise HTTPException(status_code=400, detail="Aucun champ à mettre à jour.")

        # Le statut de disponibilité est obligatoire dès qu'il est envoyé :
        # on refuse explicitement une valeur vide/null (ne dépend pas du frontend).
        if "availability_status" in payload:
            _validate_availability_status(payload["availability_status"])

        # Unicité de l'email personnel côté backend (409 si déjà pris).
        if "email" in payload:
            if _email_personnel_exists(cursor, payload["email"], exclude_id=id_etudiant):
                raise HTTPException(
                    status_code=409,
                    detail="Cet email est déjà utilisé par un autre étudiant.",
                )

        # Existence de la promotion cible (422 si inconnue).
        if "id_promotion" in payload:
            if not _promotion_existe(cursor, payload["id_promotion"]):
                raise HTTPException(
                    status_code=422,
                    detail="La promotion spécifiée n'existe pas.",
                )

        # Unicité de l'email académique côté backend (422 si déjà pris).
        if "email_academique" in payload:
            payload["email_academique"] = _resolve_email_academique(
                cursor,
                payload.get("prenom") or None,
                payload.get("nom") or None,
                payload["email_academique"],
                exclude_id=id_etudiant,
            )

        # Mapper les champs du payload aux noms de colonnes SQL
        set_clauses = []
        params = []
        field_map = {
            "nom": "nom",
            "prenom": "prenom",
            "email": "email",
            "email_academique": "email_academique",
            "telephone": "telephone",
            "date_naissance": "date_naissance",
            "parcours_anterieur": "parcours_anterieur",
            "date_inscription": "date_inscription",
            "id_promotion": "id_promotion",
            "address": "address",
            "city": "city",
            "country": "country",
            "linkedin": "linkedin",
            "availability_status": "availability_status",
        }

        for field, col in field_map.items():
            if field in payload:
                set_clauses.append(f"{col} = %s")
                params.append(payload[field])

        if "skills" in payload:
            set_clauses.append("skills = %s::jsonb")
            params.append(json.dumps(payload["skills"]))

        if not set_clauses:
            raise HTTPException(status_code=400, detail="Aucun champ valide à mettre à jour.")

        params.append(id_etudiant)
        query = f"UPDATE ETUDIANT SET {', '.join(set_clauses)} WHERE id_etudiant = %s;"
        cursor.execute(query, tuple(params))
        db.commit()

        # Retourner l'étudiant mis à jour
        cursor.execute(
            f"""
            SELECT e.id_etudiant, e.nom, e.prenom, e.email, e.email_academique,
                   e.telephone, e.date_naissance, e.parcours_anterieur,
                   e.date_inscription, e.id_promotion,
                   {_EXTENDED_COLUMNS},
                   p.nom_promotion,
                   ent.nom_entreprise,
                   ent.secteur_activite,
                   (SELECT COUNT(*) FROM EXPERIENCE_PRO WHERE id_etudiant = e.id_etudiant)
            FROM ETUDIANT e
            LEFT JOIN PROMOTION p ON e.id_promotion = p.id_promotion
            LEFT JOIN EXPERIENCE_PRO exp ON e.id_etudiant = exp.id_etudiant AND exp.poste_actuel = TRUE
            LEFT JOIN ENTREPRISE ent ON exp.id_entreprise = ent.id_entreprise
            WHERE e.id_etudiant = %s;
            """,
            (id_etudiant,),
        )
        row = cursor.fetchone()
        columns = [desc[0] for desc in cursor.description]
        data = dict(zip(columns, row))

        raw_skills = data.get("skills") or []
        if isinstance(raw_skills, str):
            try:
                raw_skills = json.loads(raw_skills)
            except (json.JSONDecodeError, TypeError):
                raw_skills = []

        return schemas.EtudiantDetail(
            id_etudiant=data["id_etudiant"],
            nom=data["nom"],
            prenom=data["prenom"],
            email=data["email"],
            email_academique=data.get("email_academique"),
            telephone=data["telephone"],
            date_naissance=data["date_naissance"],
            parcours_anterieur=data["parcours_anterieur"],
            date_inscription=data["date_inscription"],
            id_promotion=data["id_promotion"],
            promotion_nom=data.get("nom_promotion"),
            entreprise_actuelle=data.get("nom_entreprise"),
            experiences_count=data.get("count", 0),
            secteur_activite=data.get("secteur_activite") or "",
            address=data.get("address", ""),
            city=data.get("city", ""),
            country=data.get("country", ""),
            linkedin=data.get("linkedin", ""),
            availability_status=data.get("availability_status", ""),
            skills=raw_skills,
        )
    except HTTPException:
        raise
    except pg8000.dbapi.IntegrityError as exc:
        db.rollback()
        response = _integrity_error_response(exc)
        if response:
            raise HTTPException(status_code=response[0], detail=response[1])
        raise HTTPException(status_code=400, detail="Contrainte de base violée lors de la mise à jour partielle.")
    except Exception:
        db.rollback()
        logger.exception("Erreur lors de la mise à jour partielle de l'étudiant %s", id_etudiant)
        raise HTTPException(status_code=400, detail="Impossible de mettre à jour l'étudiant.")
    finally:
        cursor.close()


class AnonymisationRequest(BaseModel):
    """Body de l'anonymisation directe par un admin depuis l'annuaire.

    `acteur` : nom réel de l'admin, pour la traçabilité AUDIT_LOG
    (réutilisé par le frontend via adminIdentityAPI.getName())."""
    acteur: Optional[str] = None


@router.delete("/{id_etudiant}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin_api_key)])
def delete_etudiant(
    id_etudiant: int,
    acteur: Optional[str] = Query(None, description="Nom de l'admin, pour la traçabilité AUDIT_LOG"),
    db=Depends(get_db),
):
    cursor = db.cursor()
    admin = (acteur or "").strip() or "admin"
    try:
        cursor.execute("SELECT nom, prenom FROM ETUDIANT WHERE id_etudiant = %s;", (id_etudiant,))
        row = cursor.fetchone()
        if not row:
            db.rollback()
            raise HTTPException(status_code=404, detail="Étudiant introuvable.")
        nom_complet = f"{row[1]} {row[0]}".strip()
        cursor.execute("DELETE FROM CONSENTEMENT_RGPD WHERE id_etudiant = %s;", (id_etudiant,))
        cursor.execute("DELETE FROM OBTIENT WHERE id_etudiant = %s;", (id_etudiant,))
        cursor.execute("DELETE FROM EXPERIENCE_PRO WHERE id_etudiant = %s;", (id_etudiant,))
        cursor.execute("DELETE FROM ETUDIANT WHERE id_etudiant = %s;", (id_etudiant,))
        if cursor.rowcount == 0:
            db.rollback()
            raise HTTPException(status_code=404, detail="Étudiant introuvable.")
        _write_audit_log(
            cursor,
            "SUPPRESSION_DEFINITIVE_ADMIN",
            f"Suppression définitive (hard delete) de l'alumni id={id_etudiant} "
            f"({nom_complet}) initiée directement par l'admin '{admin}' — "
            "action irréversible réservée aux erreurs de saisie ou doublons, "
            "pas aux demandes de suppression RGPD normales.",
            1,
            acteur=f"admin:{admin}",
        )
        db.commit()
        return
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        logger.exception("Erreur lors de la suppression de l'étudiant %s", id_etudiant)
        raise HTTPException(status_code=400, detail="Impossible de supprimer l'étudiant.")
    finally:
        cursor.close()


@router.post(
    "/{id_etudiant}/anonymiser",
    dependencies=[Depends(require_admin_api_key)],
)
def anonymiser_etudiant(
    id_etudiant: int,
    body: AnonymisationRequest,
    db=Depends(get_db),
):
    """Anonymisation RGPD directe par un admin (annuaire), hors demande RGPD.

    Réutilise la même logique que le traitement d'une demande de suppression
    (`_anonymiser_compte`) : masquage irréversible des données personnelles,
    conservation des lignes pour les indicateurs agrégés. Aucune suppression
    physique : la purge définitive différée reste gérée par /admin/cleanup
    et /admin/demandes-rgpd/purge-anonymises.
    """
    cursor = db.cursor()
    admin = (body.acteur or "").strip() or "admin"
    try:
        cursor.execute(
            "SELECT nom, prenom, email, date_anonymisation FROM ETUDIANT "
            "WHERE id_etudiant = %s;",
            (id_etudiant,),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Étudiant introuvable.")
        nom_complet = f"{row[1]} {row[0]}".strip()
        if row[3] is not None:
            raise HTTPException(
                status_code=409,
                detail="Ce compte est déjà anonymisé. Utilisez la purge RGPD différée pour une suppression définitive.",
            )
        _anonymiser_compte(cursor, id_etudiant)
        _write_audit_log(
            cursor,
            "ANONYMISATION_ADMIN",
            f"Anonymisation RGPD de l'alumni id={id_etudiant} ({nom_complet}) "
            f"initiée directement par l'admin '{admin}' (hors demande RGPD).",
            1,
            acteur=f"admin:{admin}",
        )
        db.commit()
        return {"id_etudiant": id_etudiant, "statut": "anonymise", "acteur": admin}
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        logger.exception("Erreur lors de l'anonymisation de l'étudiant %s", id_etudiant)
        raise HTTPException(status_code=400, detail="Impossible d'anonymiser l'étudiant.")
    finally:
        cursor.close()
