import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

import schemas
from database import get_db
from security import require_admin_api_key, require_owner_or_admin
from utils import refuser_compte_anonymise, rows_to_dicts

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Certifications"])


def _pg_sqlstate(exc: Exception) -> str | None:
    """SQLSTATE (code 'C') de l'erreur PostgreSQL transportée par pg8000."""
    args = getattr(exc, "args", None)
    if args and isinstance(args[0], dict):
        return args[0].get("C")
    return None


@router.post("/certifications/", response_model=schemas.Certification, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin_api_key)])
def create_certification(cert: schemas.CertificationCreate, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        query = "INSERT INTO CERTIFICATION (nom_certification, organisme) VALUES (%s, %s) RETURNING id_certification;"
        cursor.execute(query, (cert.nom_certification, cert.organisme))
        id_generated = cursor.fetchone()[0]
        db.commit()
        return {**cert.model_dump(), "id_certification": id_generated}
    except Exception:
        db.rollback()
        logger.exception("Erreur lors de la création d'une certification")
        raise HTTPException(status_code=400, detail="Impossible de créer la certification.")
    finally:
        cursor.close()


@router.get("/certifications/", response_model=List[schemas.Certification], dependencies=[Depends(require_admin_api_key)])
def get_all_certifications(db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id_certification, nom_certification, organisme FROM CERTIFICATION;")
        return rows_to_dicts(cursor, cursor.fetchall())
    finally:
        cursor.close()


@router.post("/etudiants-certifications/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin_api_key)])
def associer_certification_etudiant(obtient: schemas.ObtientCreate, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        refuser_compte_anonymise(cursor, obtient.id_etudiant)
        query = "INSERT INTO OBTIENT (id_etudiant, id_certification, date_obtention) VALUES (%s, %s, %s);"
        cursor.execute(query, (obtient.id_etudiant, obtient.id_certification, obtient.date_obtention))
        db.commit()
        return {"message": "Certification associée avec succès à l'étudiant."}
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        sqlstate = _pg_sqlstate(exc)
        if sqlstate == "23505":
            raise HTTPException(
                status_code=409,
                detail="Cet étudiant possède déjà cette certification.",
            )
        if sqlstate == "23503":
            raise HTTPException(
                status_code=400,
                detail="L'étudiant ou la certification spécifié n'existe pas.",
            )
        logger.exception("Erreur lors de l'association étudiant/certification")
        raise HTTPException(status_code=400, detail="Impossible d'associer la certification.")
    finally:
        cursor.close()


@router.delete("/certifications/{id_certification}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin_api_key)])
def delete_certification(id_certification: int, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM OBTIENT WHERE id_certification = %s;", (id_certification,))
        cursor.execute("DELETE FROM CERTIFICATION WHERE id_certification = %s;", (id_certification,))
        if cursor.rowcount == 0:
            db.rollback()
            raise HTTPException(status_code=404, detail="Certification introuvable.")
        db.commit()
        return
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception("Erreur lors de la suppression de la certification %s", id_certification)
        raise HTTPException(status_code=400, detail="Impossible de supprimer la certification.")
    finally:
        cursor.close()


@router.delete("/etudiants-certifications/", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin_api_key)])
def dissocier_certification_etudiant(obtient: schemas.ObtientCreate, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        refuser_compte_anonymise(cursor, obtient.id_etudiant)
        cursor.execute(
            "DELETE FROM OBTIENT WHERE id_etudiant = %s AND id_certification = %s;",
            (obtient.id_etudiant, obtient.id_certification),
        )
        if cursor.rowcount == 0:
            db.rollback()
            raise HTTPException(status_code=404, detail="Association étudiant/certification introuvable.")
        db.commit()
        return
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception("Erreur lors de la dissociation étudiant/certification")
        raise HTTPException(status_code=400, detail="Impossible de dissocier la certification.")
    finally:
        cursor.close()


@router.get("/etudiants/{id_etudiant}/certifications", tags=["Interface Étudiant / Alumni"])
def get_certifications_etudiant(id_etudiant: int, db=Depends(get_db), _auth=Depends(require_owner_or_admin)):
    cursor = db.cursor()
    try:
        query = """
            SELECT c.id_certification,
                   c.nom_certification AS nom,
                   c.organisme,
                   o.date_obtention
            FROM CERTIFICATION c
            JOIN OBTIENT o ON c.id_certification = o.id_certification
            WHERE o.id_etudiant = %s
            ORDER BY o.date_obtention DESC;
        """
        cursor.execute(query, (id_etudiant,))
        return rows_to_dicts(cursor, cursor.fetchall())
    except Exception:
        logger.exception("Erreur lors de la récupération des certifications de l'étudiant %s", id_etudiant)
        raise HTTPException(status_code=400, detail="Impossible de récupérer les certifications.")
    finally:
        cursor.close()


@router.post(
    "/etudiants/{id_etudiant}/certifications",
    status_code=status.HTTP_201_CREATED,
    tags=["Interface Étudiant / Alumni"],
)
def ajouter_certification_etudiant(
    id_etudiant: int,
    data: schemas.CertificationAlumniCreate,
    db=Depends(get_db),
    _auth=Depends(require_owner_or_admin),
):
    cursor = db.cursor()
    try:
        refuser_compte_anonymise(cursor, id_etudiant)

        if data.date_obtention is None:
            raise HTTPException(
                status_code=422,
                detail="La date d'obtention est obligatoire pour associer une certification.",
            )

        cursor.execute(
            "SELECT id_certification FROM CERTIFICATION WHERE nom_certification ILIKE %s LIMIT 1",
            (data.nom,),
        )
        row = cursor.fetchone()
        if row:
            id_certification = row[0]
        else:
            cursor.execute(
                "INSERT INTO CERTIFICATION (nom_certification, organisme) "
                "VALUES (%s, %s) RETURNING id_certification",
                (data.nom, data.organisme),
            )
            id_certification = cursor.fetchone()[0]

        date_val = data.date_obtention
        cursor.execute(
            "INSERT INTO OBTIENT (id_etudiant, id_certification, date_obtention) "
            "VALUES (%s, %s, %s) "
            "ON CONFLICT (id_etudiant, id_certification) "
            "DO UPDATE SET date_obtention = EXCLUDED.date_obtention",
            (id_etudiant, id_certification, date_val),
        )

        db.commit()
        return {"message": "Certification enregistrée avec succès."}

    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        sqlstate = _pg_sqlstate(exc)
        if sqlstate == "23502":
            raise HTTPException(
                status_code=400,
                detail="La date d'obtention est obligatoire pour associer une certification.",
            )
        if sqlstate == "23505":
            raise HTTPException(
                status_code=409,
                detail="Cet étudiant possède déjà cette certification.",
            )
        logger.exception("Erreur lors de l'ajout d'une certification par l'étudiant %s", id_etudiant)
        raise HTTPException(status_code=400, detail="Impossible d'enregistrer la certification.")
    finally:
        cursor.close()


@router.delete(
    "/etudiants/{id_etudiant}/certifications/{id_certification}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Interface Étudiant / Alumni"],
)
def retirer_certification_etudiant(
    id_etudiant: int,
    id_certification: int,
    db=Depends(get_db),
    _auth=Depends(require_owner_or_admin),
):
    """Dissocie une certification d'un étudiant (supprime le lien OBTIENT uniquement).

    Contrairement a DELETE /certifications/{id} (admin), cette route ne supprime
    PAS la certification elle-meme dans la table CERTIFICATION.
    """
    cursor = db.cursor()
    try:
        refuser_compte_anonymise(cursor, id_etudiant)
        cursor.execute(
            "DELETE FROM OBTIENT WHERE id_etudiant = %s AND id_certification = %s;",
            (id_etudiant, id_certification),
        )
        if cursor.rowcount == 0:
            db.rollback()
            raise HTTPException(status_code=404, detail="Association etudiant/certification introuvable.")
        db.commit()
        return
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception("Erreur lors de la dissociation etudiant/certification %s/%s", id_etudiant, id_certification)
        raise HTTPException(status_code=400, detail="Impossible de dissocier la certification.")
    finally:
        cursor.close()
