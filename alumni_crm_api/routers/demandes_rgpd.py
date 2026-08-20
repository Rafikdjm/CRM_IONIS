"""
Router des demandes RGPD.

Côté alumni (JWT, propriétaire uniquement) :
  - POST   /rgpd/demandes          : créer une demande (export ou suppression)
  - GET    /rgpd/demandes/moi      : lister ses demandes + statuts
  - DELETE /rgpd/demandes/{id}     : annuler une demande non traitée
  - GET    /rgpd/export            : export auto-service immédiat (JSON)

Côté admin (clé API ou JWT admin) :
  - GET    /admin/demandes-rgpd                          : liste + filtres
  - POST   /admin/demandes-rgpd/{id}/prendre-en-charge   : 'envoyee' -> 'en_traitement'
  - POST   /admin/demandes-rgpd/{id}/traiter             : traiter / rejeter
  - GET    /admin/demandes-rgpd/{id}/export              : export d'un alumni
  - POST   /admin/demandes-rgpd/bulk/traiter             : traiter/rejeter plusieurs demandes
  - POST   /admin/demandes-rgpd/bulk/delete              : supprimer plusieurs demandes
  - POST   /admin/demandes-rgpd/bulk/export              : export groupé (JSON) de plusieurs demandes
  - POST   /admin/demandes-rgpd/purge-cloturees          : supprime les demandes traitées/rejetées

Cycle de statut d'une demande :
  'envoyee' -> 'en_traitement' (prise en charge admin, verrou anti-parallélisme)
           -> 'traitee' (avec traitee_par = nom réel de l'admin) | 'rejetee'

Toutes les opérations sont tracées dans AUDIT_LOG avec un champ acteur
("admin:<nom>" / "alumni:<id>" / "system").
"""
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from database import get_db
from purge import comptes_purgeables, purge_comptes_anonymises
from routers.cleanup import _write_audit_log
from schemas import DemandeRgpdCreate, DemandeRgpdPriseEnCharge, DemandeRgpdTraiter
from security import (
    current_identity,
    require_admin_api_key,
)
from utils import rows_to_dicts

logger = logging.getLogger(__name__)

alumni_router = APIRouter(prefix="/rgpd", tags=["RGPD"])
admin_router = APIRouter(
    prefix="/admin/demandes-rgpd",
    tags=["Interface Administration"],
    dependencies=[Depends(require_admin_api_key)],
)

_VALID_TYPES = ("export", "suppression")
_VALID_STATUTS = ("envoyee", "en_traitement", "traitee", "rejetee")
# Statuts « actifs » : la demande n'a pas encore de décision finale.
_ACTIF_STATUTS = ("envoyee", "en_traitement")


class BulkIds(BaseModel):
    ids: List[int] = Field(..., min_length=1)


class BulkTraiter(BaseModel):
    ids: List[int] = Field(..., min_length=1)
    decision: str = Field(..., pattern="^(traitee|rejetee)$")
    traitee_par: str = ""
    motif_refus: str | None = None


# ---------------------------------------------------------------------------
# Aides internes
# ---------------------------------------------------------------------------

def _acteur_identity(identity: dict) -> str:
    """Acteur pour l'audit : alumni:<id> pour un alumni, admin sinon."""
    if identity["kind"] == "alumni":
        return f"alumni:{identity['id_etudiant']}"
    return "admin"


def _require_alumni(identity: dict) -> int:
    """Retourne l'id_etudiant si l'appelant est un alumni connecté (JWT)."""
    if identity.get("kind") != "alumni" or not identity.get("id_etudiant"):
        logger.warning(
            "Accès RGPD refusé : identité reçue=%s (attendu kind='alumni' avec id_etudiant)",
            identity,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Cette action requiert un compte alumni connecté. "
                "Si vous êtes connecté en tant qu'administrateur dans un autre onglet, "
                "déconnectez-vous puis reconnectez-vous avec votre compte alumni."
            ),
        )
    return int(identity["id_etudiant"])


def _get_student(cursor, id_etudiant: int) -> dict | None:
    cursor.execute(
        "SELECT id_etudiant, nom, prenom, email FROM ETUDIANT WHERE id_etudiant = %s;",
        (id_etudiant,),
    )
    row = cursor.fetchone()
    if not row:
        return None
    return {"id_etudiant": row[0], "nom": row[1], "prenom": row[2], "email": row[3]}


def _anonymiser_compte(cursor, id_etudiant: int) -> None:
    """Anonymisation irréversible (pattern ARCHIVAGE_RGPD) : masque les champs
    personnels et salariaux, conserve les lignes pour les indicateurs agrégés."""
    cursor.execute(
        """
        UPDATE ETUDIANT
        SET nom = 'ANONYMISE',
            prenom = 'ANONYMISE',
            email = 'ANONYMISE_' || id_etudiant || '@anonymise.io',
            email_academique = NULL,
            telephone = 'ANONYMISE',
            date_naissance = '1900-01-01',
            parcours_anterieur = 'ANONYMISE',
            address = NULL,
            city = NULL,
            country = NULL,
            linkedin = NULL,
            availability_status = '',
            skills = '[]'::jsonb,
            date_anonymisation = NOW()
        WHERE id_etudiant = %s;
        """,
        (id_etudiant,),
    )
    cursor.execute(
        """
        UPDATE EXPERIENCE_PRO
        SET intitule_poste = 'ANONYMISE',
            salaire = 0
        WHERE id_etudiant = %s;
        """,
        (id_etudiant,),
    )


def _build_export(cursor, id_etudiant: int) -> dict:
    """Construit le paquet de données personnelles d'un alumni (droit d'accès)."""
    cursor.execute(
        """
        SELECT e.id_etudiant, e.nom, e.prenom, e.email, e.email_academique,
               e.telephone, e.date_naissance, e.parcours_anterieur,
               e.date_inscription, e.address, e.city, e.country, e.linkedin,
               e.availability_status, e.skills, p.nom_promotion
        FROM ETUDIANT e
        LEFT JOIN PROMOTION p ON e.id_promotion = p.id_promotion
        WHERE e.id_etudiant = %s;
        """,
        (id_etudiant,),
    )
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Étudiant introuvable.")

    columns = [desc[0] for desc in cursor.description]
    profil = dict(zip(columns, row))
    profil["skills"] = profil.get("skills") or []

    cursor.execute(
        """
        SELECT exp.id_experience, exp.intitule_poste, exp.type_contrat,
               exp.date_debut, exp.date_fin, exp.salaire, exp.poste_actuel,
               ent.nom_entreprise, ent.secteur_activite
        FROM EXPERIENCE_PRO exp
        LEFT JOIN ENTREPRISE ent ON exp.id_entreprise = ent.id_entreprise
        WHERE exp.id_etudiant = %s
        ORDER BY exp.date_debut DESC;
        """,
        (id_etudiant,),
    )
    experiences = rows_to_dicts(cursor, cursor.fetchall())

    cursor.execute(
        """
        SELECT c.nom_certification, c.organisme, o.date_obtention
        FROM OBTIENT o
        JOIN CERTIFICATION c ON o.id_certification = c.id_certification
        WHERE o.id_etudiant = %s
        ORDER BY o.date_obtention;
        """,
        (id_etudiant,),
    )
    certifications = rows_to_dicts(cursor, cursor.fetchall())

    cursor.execute(
        """
        SELECT id_consentement, date_consentement, type_consentement,
               statut, canal
        FROM CONSENTEMENT_RGPD
        WHERE id_etudiant = %s
        ORDER BY date_consentement DESC;
        """,
        (id_etudiant,),
    )
    consentements = rows_to_dicts(cursor, cursor.fetchall())

    cursor.execute(
        """
        SELECT r.id_reponse, r.date_reponse, q.titre AS questionnaire, r.reponses
        FROM REPONSE_QUESTIONNAIRE r
        LEFT JOIN QUESTIONNAIRE q ON r.id_questionnaire = q.id_questionnaire
        WHERE r.id_etudiant = %s
        ORDER BY r.date_reponse DESC;
        """,
        (id_etudiant,),
    )
    reponses = rows_to_dicts(cursor, cursor.fetchall())

    return {
        "etudiant": profil,
        "experiences": experiences,
        "certifications": certifications,
        "consentements": consentements,
        "reponses_questionnaires": reponses,
        "date_generation": None,  # remplacé par le timestamp FastAPI à la sérialisation
    }


# ---------------------------------------------------------------------------
# Côté alumni
# ---------------------------------------------------------------------------

@alumni_router.post("/demandes", status_code=status.HTTP_201_CREATED)
def creer_demande(
    body: DemandeRgpdCreate,
    db=Depends(get_db),
    identity: dict = Depends(current_identity),
):
    id_etudiant = _require_alumni(identity)
    cursor = db.cursor()
    try:
        etudiant = _get_student(cursor, id_etudiant)
        if not etudiant:
            raise HTTPException(status_code=404, detail="Compte alumni introuvable.")

        # Une seule demande active par type (envoyée ou en cours de traitement).
        cursor.execute(
            "SELECT id_demande FROM DEMANDE_RGPD "
            "WHERE id_etudiant = %s AND type_demande = %s "
            "AND statut IN ('envoyee', 'en_traitement') LIMIT 1;",
            (id_etudiant, body.type_demande),
        )
        if cursor.fetchone():
            raise HTTPException(
                status_code=409,
                detail="Une demande de ce type est déjà envoyée ou en cours de traitement.",
            )

        nom_complet = f"{etudiant['prenom']} {etudiant['nom']}".strip()
        cursor.execute(
            """
            INSERT INTO DEMANDE_RGPD (id_etudiant, type_demande, statut,
                                      nom_complet, email)
            VALUES (%s, %s, 'envoyee', %s, %s)
            RETURNING id_demande, date_demande;
            """,
            (id_etudiant, body.type_demande, nom_complet, etudiant["email"]),
        )
        id_demande, date_demande = cursor.fetchone()

        _write_audit_log(
            cursor,
            "DEMANDE_RGPD_CREEE",
            f"Demande '{body.type_demande}' créée par l'alumni id={id_etudiant}",
            1,
            acteur=_acteur_identity(identity),
        )
        db.commit()

        return {
            "id_demande": id_demande,
            "id_etudiant": id_etudiant,
            "type_demande": body.type_demande,
            "statut": "envoyee",
            "date_demande": date_demande,
            "nom_complet": nom_complet,
            "email": etudiant["email"],
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        logger.exception("Erreur lors de la création d'une demande RGPD")
        raise HTTPException(status_code=400, detail="Impossible de créer la demande RGPD.")
    finally:
        cursor.close()


@alumni_router.get("/demandes/moi")
def mes_demandes(db=Depends(get_db), identity: dict = Depends(current_identity)):
    id_etudiant = _require_alumni(identity)
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            SELECT id_demande, id_etudiant, type_demande, statut,
                   date_demande, date_prise_en_charge, date_traitement,
                   prise_en_charge_par, traitee_par, motif_refus,
                   nom_complet, email
            FROM DEMANDE_RGPD
            WHERE id_etudiant = %s
            ORDER BY date_demande DESC;
            """,
            (id_etudiant,),
        )
        return {"demandes": rows_to_dicts(cursor, cursor.fetchall())}
    except Exception:
        logger.exception("Erreur lors de la lecture des demandes RGPD")
        raise HTTPException(status_code=400, detail="Impossible de lire vos demandes RGPD.")
    finally:
        cursor.close()


@alumni_router.delete("/demandes/{id_demande}", status_code=status.HTTP_204_NO_CONTENT)
def annuler_demande(
    id_demande: int,
    db=Depends(get_db),
    identity: dict = Depends(current_identity),
):
    id_etudiant = _require_alumni(identity)
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT id_etudiant, statut FROM DEMANDE_RGPD WHERE id_demande = %s;",
            (id_demande,),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Demande introuvable.")
        if row[0] != id_etudiant:
            raise HTTPException(
                status_code=403,
                detail="Vous ne pouvez annuler que vos propres demandes.",
            )
        if row[1] not in _ACTIF_STATUTS:
            raise HTTPException(
                status_code=400,
                detail="Seules les demandes envoyées ou en cours de traitement peuvent être annulées.",
            )

        cursor.execute("DELETE FROM DEMANDE_RGPD WHERE id_demande = %s;", (id_demande,))
        _write_audit_log(
            cursor,
            "DEMANDE_RGPD_ANNULEE",
            f"Demande id={id_demande} annulée par l'alumni id={id_etudiant}",
            1,
            acteur=_acteur_identity(identity),
        )
        db.commit()
        return
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        logger.exception("Erreur lors de l'annulation d'une demande RGPD")
        raise HTTPException(status_code=400, detail="Impossible d'annuler la demande RGPD.")
    finally:
        cursor.close()


@alumni_router.get("/export")
def exporter_mes_donnees(db=Depends(get_db), identity: dict = Depends(current_identity)):
    """Export auto-service immédiat (droit d'accès). Crée une demande 'export'
    automatiquement marquée 'traitee' pour la traçabilité.

    traitee_par reste NULL : cet export est auto-traité sans intervention
    admin — seul un VRAI traitement admin (traiter / bulk) doit renseigner ce
    champ. Le champ date_traitement conserve le moment de l'auto-export."""
    id_etudiant = _require_alumni(identity)
    cursor = db.cursor()
    try:
        etudiant = _get_student(cursor, id_etudiant)
        if not etudiant:
            raise HTTPException(status_code=404, detail="Compte alumni introuvable.")

        payload = _build_export(cursor, id_etudiant)
        payload["date_generation"] = None  # JSON via FastAPI (datetime) ; None évite une date figée

        nom_complet = f"{etudiant['prenom']} {etudiant['nom']}".strip()
        cursor.execute(
            """
            INSERT INTO DEMANDE_RGPD (id_etudiant, type_demande, statut,
                                      date_traitement, traitee_par,
                                      nom_complet, email)
            VALUES (%s, 'export', 'traitee', NOW(), NULL, %s, %s)
            RETURNING id_demande;
            """,
            (id_etudiant, nom_complet, etudiant["email"]),
        )
        id_demande = cursor.fetchone()[0]

        _write_audit_log(
            cursor,
            "EXPORT_RGPD",
            f"Export auto-service des données de l'alumni id={id_etudiant} (demande id={id_demande})",
            1,
            acteur=_acteur_identity(identity),
        )
        db.commit()

        return payload
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        logger.exception("Erreur lors de l'export RGPD")
        raise HTTPException(status_code=400, detail="Impossible de générer l'export de vos données.")
    finally:
        cursor.close()


# ---------------------------------------------------------------------------
# Côté admin — actions groupées (déclarées AVANT /{id_demande} pour éviter
# que "bulk" ou "purge-cloturees" soit capturé comme paramètre de chemin)
# ---------------------------------------------------------------------------

def _traiter_une_demande(cursor, id_demande: int, decision: str, acteur: str,
                         motif_refus: str | None) -> dict:
    """Applique la décision sur une demande non clôturée. Ne commit pas
    (transaction gérée par l'appelant).

    Cycle respecté :
      - 'envoyee'        : prise en charge implicite (acteur) puis décision ;
      - 'en_traitement'  : décision, verrouillée si déjà prise en charge par
                           un autre admin (évite le traitement en parallèle).
    """
    cursor.execute(
        "SELECT id_etudiant, type_demande, statut, nom_complet, prise_en_charge_par "
        "FROM DEMANDE_RGPD WHERE id_demande = %s;",
        (id_demande,),
    )
    row = cursor.fetchone()
    if not row:
        return {"id_demande": id_demande, "ok": False, "erreur": "Demande introuvable."}

    id_etudiant, type_demande, statut, nom_complet, prise_en_charge_par = row
    if statut in ("traitee", "rejetee"):
        return {"id_demande": id_demande, "ok": False, "erreur": "Déjà traitée."}

    if statut == "en_traitement":
        if prise_en_charge_par and acteur and prise_en_charge_par != acteur:
            return {
                "id_demande": id_demande,
                "ok": False,
                "erreur": f"Déjà en cours de traitement par {prise_en_charge_par}.",
            }
    elif statut == "envoyee":
        # Prise en charge implicite au moment de la décision (bulk / legacy).
        cursor.execute(
            "UPDATE DEMANDE_RGPD SET statut = 'en_traitement', prise_en_charge_par = %s, "
            "date_prise_en_charge = NOW() WHERE id_demande = %s;",
            (acteur, id_demande),
        )
    else:
        return {"id_demande": id_demande, "ok": False, "erreur": "Statut de demande inconnu."}

    if decision == "traitee":
        if type_demande == "suppression":
            if id_etudiant is None:
                return {"id_demande": id_demande, "ok": False, "erreur": "Compte déjà supprimé."}
            cursor.execute(
                "SELECT email FROM ETUDIANT WHERE id_etudiant = %s;",
                (id_etudiant,),
            )
            if not cursor.fetchone():
                return {"id_demande": id_demande, "ok": False, "erreur": "Compte déjà supprimé."}
            _anonymiser_compte(cursor, id_etudiant)
            action_log = "SUPPRESSION_COMPTE_RGPD"
            detail_log = (
                f"Suppression de compte (anonymisation) de l'alumni "
                f"id={id_etudiant} ({nom_complet}) — demande id={id_demande}"
            )
        else:
            action_log = "EXPORT_RGPD_VALIDE"
            detail_log = (
                f"Export de données validé pour l'alumni id={id_etudiant} "
                f"({nom_complet}) — demande id={id_demande}"
            )
        cursor.execute(
            "UPDATE DEMANDE_RGPD SET statut = 'traitee', date_traitement = NOW(), "
            "traitee_par = %s, motif_refus = NULL WHERE id_demande = %s;",
            (acteur, id_demande),
        )
    else:  # rejetee
        cursor.execute(
            "UPDATE DEMANDE_RGPD SET statut = 'rejetee', date_traitement = NOW(), "
            "traitee_par = %s, motif_refus = %s WHERE id_demande = %s;",
            (acteur, motif_refus or "", id_demande),
        )
        action_log = "DEMANDE_RGPD_REJETEE"
        detail_log = f"Demande id={id_demande} rejetée ({nom_complet})"

    _write_audit_log(cursor, action_log, detail_log, 1, acteur=acteur)
    return {"id_demande": id_demande, "ok": True, "statut": decision}


# ---------------------------------------------------------------------------
# Côté admin — purge définitive différée des comptes anonymisés
# (déclarées AVANT /{id_demande} pour éviter la capture en paramètre de chemin)
# ---------------------------------------------------------------------------

class PurgeConfirm(BaseModel):
    """Payload obligatoire : la purge n'est jamais déclenchée par un simple
    clic ou un GET — le flag explicite `confirm: true` est requis."""
    confirm: bool = False


@admin_router.get("/purge-anonymises")
def preview_purge_anonymises(db=Depends(get_db)):
    """Aperçu des comptes anonymisés éligibles à la purge définitive.
    Lecture seule : aucune suppression n'est effectuée."""
    cursor = db.cursor()
    try:
        from config import settings
        candidats = comptes_purgeables(cursor)
        return {
            "delay_months": settings.purge_delay_months,
            "candidats": len(candidats),
            "comptes": candidats,
        }
    except Exception:
        logger.exception("Erreur lors de la prévisualisation de la purge RGPD")
        raise HTTPException(status_code=400, detail="Impossible de calculer l'aperçu de purge.")
    finally:
        cursor.close()


@admin_router.post("/purge-anonymises")
def lancer_purge_anonymises(body: PurgeConfirm, db=Depends(get_db)):
    """Déclenche la purge définitive des comptes anonymisés éligibles.

    Sécurité : réservé admin (clé API) + flag de confirmation explicite.
    Ne touche jamais un compte non-anonymisé ni une demande en attente.
    """
    if not body.confirm:
        raise HTTPException(
            status_code=400,
            detail="Confirmation explicite requise : envoyez {\"confirm\": true}.",
        )
    cursor = db.cursor()
    try:
        resultat = purge_comptes_anonymises(cursor, acteur="admin", commit=True)
        return {
            "message": f"Purge terminée : {resultat['purges']} compte(s) anonymisé(s) supprimé(s) définitivement.",
            **resultat,
        }
    except Exception:
        db.rollback()
        logger.exception("Erreur lors de la purge des comptes anonymisés")
        raise HTTPException(status_code=500, detail="Erreur lors de la purge des comptes anonymisés.")
    finally:
        cursor.close()


@admin_router.post("/bulk/traiter")
def bulk_traiter(body: BulkTraiter, db=Depends(get_db)):
    """Marque plusieurs demandes comme 'traitee' ou 'rejetee'.

    Seules les demandes encore actives ('envoyee' / 'en_traitement') sont
    modifiées ; une demande 'en_traitement' prise en charge par un autre
    admin est verrouillée. Les suppressions de compte déclenchent
    l'anonymisation comme le traitement individuel.
    """
    acteur = (body.traitee_par or "").strip() or "system"
    cursor = db.cursor()
    resultats, erreurs = [], 0
    try:
        for id_demande in body.ids:
            res = _traiter_une_demande(cursor, id_demande, body.decision, acteur,
                                       body.motif_refus)
            resultats.append(res)
            if not res["ok"]:
                erreurs += 1
        db.commit()
        return {
            "total": len(body.ids),
            "succes": len(body.ids) - erreurs,
            "erreurs": erreurs,
            "resultats": resultats,
        }
    except Exception:
        db.rollback()
        logger.exception("Erreur lors du traitement groupé de demandes RGPD")
        raise HTTPException(status_code=400, detail="Impossible de traiter les demandes sélectionnées.")
    finally:
        cursor.close()


@admin_router.post("/bulk/delete")
def bulk_delete(body: BulkIds, db=Depends(get_db)):
    """Suppression définitive de demandes RGPD (tous statuts confondus).

    Ne touche qu'à la table DEMANDE_RGPD : les étudiants ne sont pas modifiés.
    """
    cursor = db.cursor()
    try:
        ids = list(dict.fromkeys(body.ids))  # dédoublonne en conservant l'ordre
        placeholders = ",".join(["%s"] * len(ids))
        cursor.execute(
            f"DELETE FROM DEMANDE_RGPD WHERE id_demande IN ({placeholders}) "
            f"RETURNING id_demande;",
            tuple(ids),
        )
        supprimes = [r[0] for r in cursor.fetchall()]
        _write_audit_log(
            cursor,
            "DEMANDES_RGPD_SUPPRIMEES",
            f"Suppression définitive de {len(supprimes)} demande(s) RGPD : ids={supprimes}",
            len(supprimes),
            acteur="admin",
        )
        db.commit()
        return {"supprimees": len(supprimes), "ids": supprimes}
    except Exception:
        db.rollback()
        logger.exception("Erreur lors de la suppression groupée de demandes RGPD")
        raise HTTPException(status_code=400, detail="Impossible de supprimer les demandes sélectionnées.")
    finally:
        cursor.close()


@admin_router.post("/bulk/export")
def bulk_export(body: BulkIds, db=Depends(get_db)):
    """Export groupé : un objet JSON {"<id_demande>": export} pour les demandes
    dont le compte alumni existe encore."""
    cursor = db.cursor()
    try:
        ids = list(dict.fromkeys(body.ids))
        placeholders = ",".join(["%s"] * len(ids))
        cursor.execute(
            f"SELECT id_demande, id_etudiant FROM DEMANDE_RGPD "
            f"WHERE id_demande IN ({placeholders}) ORDER BY id_demande;",
            tuple(ids),
        )
        exports = {}
        erreurs = {}
        for id_demande, id_etudiant in cursor.fetchall():
            key = str(id_demande)
            if id_etudiant is None:
                erreurs[key] = "Compte supprimé/anonymisé, export impossible."
                continue
            try:
                exports[key] = _build_export(cursor, id_etudiant)
            except HTTPException as exc:
                erreurs[key] = str(exc.detail)
        return {"exports": exports, "erreurs": erreurs}
    except Exception:
        logger.exception("Erreur lors de l'export groupé RGPD")
        raise HTTPException(status_code=400, detail="Impossible de générer l'export groupé.")
    finally:
        cursor.close()


@admin_router.post("/purge-cloturees")
def purge_cloturees(db=Depends(get_db)):
    """Supprime toutes les demandes dont le statut est 'traitee' ou 'rejetee'.
    Les demandes actives ('envoyee' / 'en_traitement') ne sont pas touchées."""
    cursor = db.cursor()
    try:
        cursor.execute(
            "DELETE FROM DEMANDE_RGPD WHERE statut IN ('traitee', 'rejetee') "
            "RETURNING id_demande;"
        )
        supprimes = [r[0] for r in cursor.fetchall()]
        _write_audit_log(
            cursor,
            "DEMANDES_RGPD_PURGEES",
            f"Purge des demandes clôturées : {len(supprimes)} supprimée(s) (ids={supprimes})",
            len(supprimes),
            acteur="admin",
        )
        db.commit()
        return {"supprimees": len(supprimes), "ids": supprimes}
    except Exception:
        db.rollback()
        logger.exception("Erreur lors de la purge des demandes RGPD clôturées")
        raise HTTPException(status_code=400, detail="Impossible de purger les demandes clôturées.")
    finally:
        cursor.close()


# ---------------------------------------------------------------------------
# Côté admin — lecture et traitement individuel
# ---------------------------------------------------------------------------

@admin_router.get("")
def lister_demandes(
    statut: str = Query(None, description="Filtrer par statut (envoyee/en_traitement/traitee/rejetee)"),
    type_demande: str = Query(None, description="Filtrer par type (export/suppression)"),
    db=Depends(get_db),
):
    if statut and statut not in _VALID_STATUTS:
        raise HTTPException(
            status_code=422,
            detail=f"Parametre 'statut' invalide. Valeurs attendues : {', '.join(_VALID_STATUTS)}.",
        )
    if type_demande and type_demande not in _VALID_TYPES:
        raise HTTPException(
            status_code=422,
            detail=f"Parametre 'type_demande' invalide. Valeurs attendues : {', '.join(_VALID_TYPES)}.",
        )
    cursor = db.cursor()
    try:
        query = """
            SELECT d.id_demande, d.id_etudiant, d.type_demande, d.statut,
                   d.date_demande, d.date_prise_en_charge, d.date_traitement,
                   d.prise_en_charge_par, d.traitee_par,
                   d.motif_refus, d.nom_complet, d.email,
                   e.nom AS etudiant_nom, e.prenom AS etudiant_prenom,
                   e.availability_status, e.date_anonymisation
            FROM DEMANDE_RGPD d
            LEFT JOIN ETUDIANT e ON e.id_etudiant = d.id_etudiant
            WHERE 1=1
        """
        params = []
        if statut:
            query += " AND d.statut = %s"
            params.append(statut)
        if type_demande:
            query += " AND d.type_demande = %s"
            params.append(type_demande)
        query += " ORDER BY d.date_demande DESC, d.id_demande DESC"

        cursor.execute(query, tuple(params))
        demandes = rows_to_dicts(cursor, cursor.fetchall())
        # Statut du compte (actif si l'email n'a pas été anonymisé)
        # + indicateur d'éligibilité à la purge définitive différée.
        from config import settings
        delay = settings.purge_delay_months
        eligibles = {c["id_etudiant"] for c in comptes_purgeables(cursor)}
        for d in demandes:
            id_etudiant = d.get("id_etudiant")
            if id_etudiant is not None:
                d["compte_active"] = not (d.get("etudiant_nom") == "ANONYMISE")
                d["eligible_purge"] = id_etudiant in eligibles
                if d.get("date_anonymisation") and delay:
                    from datetime import datetime
                    jours_ecoules = (datetime.now() - d["date_anonymisation"]).days
                    # 30 jours par mois, convention suffisante pour un affichage
                    jours_restants = max(0, delay * 30 - jours_ecoules)
                    d["purge_dans_jours"] = jours_restants
                else:
                    d["purge_dans_jours"] = None
            else:
                d["compte_active"] = False
                d["eligible_purge"] = False
                d["purge_dans_jours"] = None
        return {"demandes": demandes}
    except Exception:
        logger.exception("Erreur lors de la liste des demandes RGPD")
        raise HTTPException(status_code=400, detail="Impossible de lister les demandes RGPD.")
    finally:
        cursor.close()


@admin_router.get("/{id_demande}/export")
def export_admin(
    id_demande: int,
    db=Depends(get_db),
    _auth=Depends(require_admin_api_key),
):
    """Génère l'export JSON des données d'un alumni (pour un export ou une vérification)."""
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT id_etudiant, type_demande, statut FROM DEMANDE_RGPD WHERE id_demande = %s;",
            (id_demande,),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Demande introuvable.")
        id_etudiant = row[0]
        if id_etudiant is None:
            raise HTTPException(status_code=410, detail="Compte supprimé/anonymisé, export impossible.")
        return _build_export(cursor, id_etudiant)
    except HTTPException:
        raise
    except Exception:
        logger.exception("Erreur lors de l'export admin RGPD")
        raise HTTPException(status_code=400, detail="Impossible de générer l'export.")
    finally:
        cursor.close()


@admin_router.post("/{id_demande}/prendre-en-charge")
def prendre_en_charge(
    id_demande: int,
    body: DemandeRgpdPriseEnCharge,
    db=Depends(get_db),
):
    """L'admin ouvre la demande et la réserve : 'envoyee' -> 'en_traitement'.

    La demande devient alors verrouillée : un autre admin ne pourra ni la
    prendre en charge ni la traiter tant qu'elle n'est pas décidée.
    """
    acteur = (body.traitee_par or "").strip()
    if not acteur:
        raise HTTPException(
            status_code=422,
            detail="Le nom de l'administrateur (traitee_par) est requis pour la prise en charge.",
        )
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT statut, nom_complet, prise_en_charge_par FROM DEMANDE_RGPD "
            "WHERE id_demande = %s;",
            (id_demande,),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Demande introuvable.")
        statut, nom_complet, prise_en_charge_par = row

        if statut in ("traitee", "rejetee"):
            raise HTTPException(status_code=400, detail="Cette demande a déjà été traitée.")
        if statut == "en_traitement":
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Cette demande est déjà en cours de traitement par "
                    f"{prise_en_charge_par or 'un autre administrateur'}."
                ),
            )

        cursor.execute(
            "UPDATE DEMANDE_RGPD SET statut = 'en_traitement', prise_en_charge_par = %s, "
            "date_prise_en_charge = NOW() WHERE id_demande = %s;",
            (acteur, id_demande),
        )
        _write_audit_log(
            cursor,
            "DEMANDE_RGPD_PRISE_EN_CHARGE",
            f"Demande id={id_demande} prise en charge par {acteur} ({nom_complet})",
            1,
            acteur=acteur,
        )
        db.commit()
        return {
            "id_demande": id_demande,
            "statut": "en_traitement",
            "prise_en_charge_par": acteur,
            "date_prise_en_charge": None,  # remplacé par la sérialisation FastAPI
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        logger.exception("Erreur lors de la prise en charge d'une demande RGPD")
        raise HTTPException(status_code=400, detail="Impossible de prendre en charge la demande RGPD.")
    finally:
        cursor.close()


@admin_router.post("/{id_demande}/traiter")
def traiter_demande(
    id_demande: int,
    body: DemandeRgpdTraiter,
    db=Depends(get_db),
):
    """Décision admin : 'traitee' (suppression → anonymisation) ou 'rejetee'.

    Accepte une demande 'en_traitement' (verrouillée au profit de l'admin
    acteur) ou 'envoyee' (prise en charge implicite au moment de la décision).
    """
    cursor = db.cursor()
    acteur = (body.traitee_par or "").strip() or "system"
    try:
        cursor.execute(
            "SELECT id_etudiant, type_demande, statut, nom_complet, prise_en_charge_par "
            "FROM DEMANDE_RGPD WHERE id_demande = %s;",
            (id_demande,),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Demande introuvable.")
        id_etudiant, type_demande, statut, nom_complet, prise_en_charge_par = row

        if statut in ("traitee", "rejetee"):
            raise HTTPException(status_code=400, detail="Cette demande a déjà été traitée.")
        if statut == "en_traitement":
            if prise_en_charge_par and acteur != prise_en_charge_par:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        f"Cette demande est déjà en cours de traitement par "
                        f"{prise_en_charge_par}. Elle ne peut être traitée que par cet administrateur."
                    ),
                )
        elif statut == "envoyee":
            # Prise en charge implicite au moment de la décision (legacy).
            cursor.execute(
                "UPDATE DEMANDE_RGPD SET statut = 'en_traitement', prise_en_charge_par = %s, "
                "date_prise_en_charge = NOW() WHERE id_demande = %s;",
                (acteur, id_demande),
            )
        else:
            raise HTTPException(status_code=400, detail="Statut de demande inconnu.")

        if body.decision == "traitee":
            if type_demande == "suppression":
                if id_etudiant is None:
                    raise HTTPException(status_code=410, detail="Compte déjà supprimé/anonymisé.")
                # Vérifier que le compte n'est pas déjà anonymisé.
                cursor.execute(
                    "SELECT email FROM ETUDIANT WHERE id_etudiant = %s;",
                    (id_etudiant,),
                )
                current_email = cursor.fetchone()
                if not current_email:
                    raise HTTPException(status_code=410, detail="Compte déjà supprimé.")
                _anonymiser_compte(cursor, id_etudiant)
                detail_log = (
                    f"Suppression de compte (anonymisation) de l'alumni "
                    f"id={id_etudiant} ({nom_complet}) — demande id={id_demande}"
                )
                action_log = "SUPPRESSION_COMPTE_RGPD"
            else:
                detail_log = (
                    f"Export de données validé pour l'alumni id={id_etudiant} "
                    f"({nom_complet}) — demande id={id_demande}"
                )
                action_log = "EXPORT_RGPD_VALIDE"

            cursor.execute(
                "UPDATE DEMANDE_RGPD SET statut = 'traitee', date_traitement = NOW(), "
                "traitee_par = %s, motif_refus = NULL WHERE id_demande = %s;",
                (acteur, id_demande),
            )
        else:  # rejetee
            cursor.execute(
                "UPDATE DEMANDE_RGPD SET statut = 'rejetee', date_traitement = NOW(), "
                "traitee_par = %s, motif_refus = %s WHERE id_demande = %s;",
                (acteur, body.motif_refus or "", id_demande),
            )
            detail_log = f"Demande id={id_demande} rejetée ({nom_complet})"
            action_log = "DEMANDE_RGPD_REJETEE"

        _write_audit_log(
            cursor,
            action_log,
            detail_log,
            1,
            acteur=acteur,
        )
        db.commit()

        return {
            "id_demande": id_demande,
            "statut": body.decision,
            "traitee_par": acteur,
            "motif_refus": body.motif_refus if body.decision == "rejetee" else None,
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        logger.exception("Erreur lors du traitement d'une demande RGPD")
        raise HTTPException(status_code=400, detail="Impossible de traiter la demande RGPD.")
    finally:
        cursor.close()
