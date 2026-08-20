import logging
from typing import Optional

import pg8000.dbapi
from fastapi import APIRouter, Depends, HTTPException, Query, status

import schemas
from database import get_db
from security import check_owner_or_admin, current_identity, require_admin_api_key, require_owner_or_admin
from utils import refuser_compte_anonymise, rows_to_dicts

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Expériences Professionnelles"])


@router.get("/etudiants/{id_etudiant}/experiences")
def get_experiences_etudiant(id_etudiant: int, db=Depends(get_db), _auth=Depends(require_owner_or_admin)):
    cursor = db.cursor()
    query = """
        SELECT exp.id_experience, exp.intitule_poste, exp.type_contrat,
               exp.date_debut, exp.date_fin, exp.salaire, exp.poste_actuel,
               ent.nom_entreprise, ent.secteur_activite, ent.pays, ent.ville
        FROM EXPERIENCE_PRO exp
        JOIN ENTREPRISE ent ON exp.id_entreprise = ent.id_entreprise
        WHERE exp.id_etudiant = %s
        ORDER BY exp.date_debut DESC;
    """
    try:
        cursor.execute(query, (id_etudiant,))
        return rows_to_dicts(cursor, cursor.fetchall())
    except Exception:
        logger.exception("Erreur lors de la récupération des expériences de l'étudiant %s", id_etudiant)
        raise HTTPException(status_code=400, detail="Impossible de récupérer les expériences.")
    finally:
        cursor.close()


@router.get("/experiences/", response_model=schemas.PaginatedResponse, dependencies=[Depends(require_admin_api_key)])
def search_experiences(
    type_contrat: Optional[str] = Query(None, description="Filtrer par type de contrat (CDI, CDD...)"),
    poste_actuel: Optional[bool] = Query(None, description="Filtrer par poste actuel"),
    salaire_min: Optional[float] = Query(None, ge=0, description="Salaire minimum"),
    salaire_max: Optional[float] = Query(None, ge=0, description="Salaire maximum"),
    id_entreprise: Optional[int] = Query(None, description="Filtrer par entreprise"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1),
    db=Depends(get_db),
):
    cursor = db.cursor()
    try:
        base_query = """
            FROM EXPERIENCE_PRO exp
            JOIN ENTREPRISE ent ON exp.id_entreprise = ent.id_entreprise
            JOIN ETUDIANT e ON exp.id_etudiant = e.id_etudiant
            WHERE 1=1
        """
        params: list = []

        if type_contrat:
            base_query += " AND exp.type_contrat ILIKE %s"
            params.append(f"%{type_contrat}%")

        if poste_actuel is not None:
            base_query += " AND exp.poste_actuel = %s"
            params.append(poste_actuel)

        if salaire_min is not None:
            base_query += " AND exp.salaire >= %s"
            params.append(salaire_min)

        if salaire_max is not None:
            base_query += " AND exp.salaire <= %s"
            params.append(salaire_max)

        if id_entreprise is not None:
            base_query += " AND exp.id_entreprise = %s"
            params.append(id_entreprise)

        cursor.execute(f"SELECT COUNT(*) {base_query}", tuple(params))
        total = cursor.fetchone()[0]

        data_query = f"""
            SELECT exp.id_experience, exp.intitule_poste, exp.type_contrat,
                   exp.date_debut, exp.date_fin, exp.salaire, exp.poste_actuel,
                   ent.nom_entreprise, e.nom, e.prenom
            {base_query}
            ORDER BY exp.date_debut DESC
            OFFSET %s LIMIT %s
        """
        params.extend([skip, limit])
        cursor.execute(data_query, tuple(params))

        return schemas.PaginatedResponse(
            items=rows_to_dicts(cursor, cursor.fetchall()),
            total=total,
            skip=skip,
            limit=limit,
            has_next=(skip + limit) < total,
        )
    except Exception:
        logger.exception("Erreur lors de la recherche d'expériences")
        raise HTTPException(status_code=400, detail="Impossible de rechercher les expériences.")
    finally:
        cursor.close()


@router.post("/experiences/", response_model=schemas.ExperiencePro, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin_api_key)])
def create_experience(exp: schemas.ExperienceProCreate, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        refuser_compte_anonymise(cursor, exp.id_etudiant)
        query = """
            INSERT INTO EXPERIENCE_PRO (intitule_poste, type_contrat, date_debut, date_fin,
                                         salaire, salary_annuel, poste_actuel, id_entreprise, id_etudiant)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_experience;
        """
        cursor.execute(query, (
            exp.intitule_poste, exp.type_contrat, exp.date_debut, exp.date_fin, exp.salaire,
            exp.salary_annuel, exp.poste_actuel, exp.id_entreprise, exp.id_etudiant,
        ))
        id_generated = cursor.fetchone()[0]
        db.commit()
        return {**exp.model_dump(), "id_experience": id_generated}
    except HTTPException:
        db.rollback()
        raise
    except pg8000.dbapi.IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="L'étudiant ou l'entreprise spécifié n'existe pas.")
    except Exception:
        db.rollback()
        logger.exception("Erreur lors de la création d'une expérience")
        raise HTTPException(status_code=400, detail="Impossible de créer l'expérience.")
    finally:
        cursor.close()


@router.delete("/experiences/{id_experience}", status_code=status.HTTP_204_NO_CONTENT)
def delete_experience(
    id_experience: int,
    db=Depends(get_db),
    identity: dict = Depends(current_identity),
):
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT id_etudiant FROM EXPERIENCE_PRO WHERE id_experience = %s;",
            (id_experience,),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Expérience introuvable.")
        check_owner_or_admin(identity, row[0])
        refuser_compte_anonymise(cursor, row[0])

        cursor.execute("DELETE FROM EXPERIENCE_PRO WHERE id_experience = %s;", (id_experience,))
        db.commit()
        return
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception("Erreur lors de la suppression d'une expérience")
        raise HTTPException(status_code=400, detail="Impossible de supprimer l'expérience.")
    finally:
        cursor.close()


@router.post("/etudiants/{id_etudiant}/experiences", tags=["Interface Étudiant / Alumni"])
def ajouter_experience(
    id_etudiant: int,
    experience: schemas.NouvelleExperience,
    db=Depends(get_db),
    _auth=Depends(require_owner_or_admin),
):
    cursor = db.cursor()
    try:
        refuser_compte_anonymise(cursor, id_etudiant)

        cursor.execute(
            "SELECT id_entreprise FROM ENTREPRISE WHERE nom_entreprise ILIKE %s LIMIT 1",
            (experience.nom_entreprise,),
        )
        row = cursor.fetchone()
        if row:
            id_entreprise = row[0]
            if experience.pays or experience.ville:
                cursor.execute(
                    "UPDATE ENTREPRISE SET "
                    "pays = CASE WHEN pays = 'Non renseigné' THEN COALESCE(%s, pays) ELSE pays END, "
                    "ville = CASE WHEN ville = 'Non renseigné' THEN COALESCE(%s, ville) ELSE ville END "
                    "WHERE id_entreprise = %s",
                    (experience.pays, experience.ville, id_entreprise),
                )
        else:
            cursor.execute(
                "INSERT INTO ENTREPRISE (nom_entreprise, secteur_activite, pays, ville) "
                "VALUES (%s, %s, %s, %s) RETURNING id_entreprise",
                (
                    experience.nom_entreprise,
                    experience.secteur_activite or "Non renseigné",
                    experience.pays or "Non renseigné",
                    experience.ville or "Non renseigné",
                ),
            )
            id_entreprise = cursor.fetchone()[0]

        if experience.poste_actuel:
            cursor.execute(
                "UPDATE EXPERIENCE_PRO SET poste_actuel = FALSE WHERE id_etudiant = %s",
                (id_etudiant,),
            )

        query = """
            INSERT INTO EXPERIENCE_PRO
                (intitule_poste, type_contrat, date_debut, date_fin, salaire, salary_annuel,
                 poste_actuel, id_entreprise, id_etudiant)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        cursor.execute(query, (
            experience.intitule_poste,
            experience.type_contrat,
            experience.date_debut,
            experience.date_fin,
            experience.salaire,
            experience.salary_annuel,
            experience.poste_actuel,
            id_entreprise,
            id_etudiant,
        ))

        db.commit()
        return {"message": "Parcours professionnel enregistré avec succès."}

    except HTTPException:
        db.rollback()
        raise
    except pg8000.dbapi.IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="L'étudiant spécifié n'existe pas.")
    except Exception:
        db.rollback()
        logger.exception("Erreur lors de l'ajout d'une expérience par l'étudiant %s", id_etudiant)
        raise HTTPException(status_code=400, detail="Impossible d'enregistrer le parcours professionnel.")
    finally:
        cursor.close()
