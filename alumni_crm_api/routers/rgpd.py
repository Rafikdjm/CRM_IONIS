import logging

import pg8000.dbapi
from fastapi import APIRouter, Depends, HTTPException, status

import schemas
from database import get_db
from security import check_owner_or_admin, current_identity, require_owner_or_admin
from utils import refuser_compte_anonymise, rows_to_dicts

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/consentements", tags=["RGPD"])


@router.get("/etudiant/{id_etudiant}")
def get_consentements_etudiant(id_etudiant: int, db=Depends(get_db), _auth=Depends(require_owner_or_admin)):
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id_etudiant FROM ETUDIANT WHERE id_etudiant = %s;", (id_etudiant,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Etudiant introuvable.")

        query = """
            SELECT id_consentement, date_consentement, type_consentement,
                   statut, canal, id_etudiant
            FROM CONSENTEMENT_RGPD
            WHERE id_etudiant = %s
            ORDER BY date_consentement DESC;
        """
        cursor.execute(query, (id_etudiant,))
        return rows_to_dicts(cursor, cursor.fetchall())
    except HTTPException:
        raise
    except Exception:
        logger.exception("Erreur lors de la récupération des consentements de l'étudiant %s", id_etudiant)
        raise HTTPException(status_code=400, detail="Impossible de récupérer les consentements.")
    finally:
        cursor.close()


@router.post("/", response_model=schemas.ConsentementRgpd, status_code=status.HTTP_201_CREATED)
def create_consentement(
    consentement: schemas.ConsentementRgpdCreate,
    db=Depends(get_db),
    identity: dict = Depends(current_identity),
):
    check_owner_or_admin(identity, consentement.id_etudiant)
    cursor = db.cursor()
    try:
        refuser_compte_anonymise(cursor, consentement.id_etudiant)
        query = """
            INSERT INTO CONSENTEMENT_RGPD (date_consentement, type_consentement, statut, canal, id_etudiant)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id_etudiant, type_consentement)
            DO UPDATE SET date_consentement = EXCLUDED.date_consentement,
                          statut = EXCLUDED.statut,
                          canal = EXCLUDED.canal
            RETURNING id_consentement;
        """
        cursor.execute(query, (
            consentement.date_consentement, consentement.type_consentement,
            consentement.statut, consentement.canal, consentement.id_etudiant,
        ))
        id_generated = cursor.fetchone()[0]
        db.commit()
        return {**consentement.model_dump(), "id_consentement": id_generated}
    except HTTPException:
        db.rollback()
        raise
    except pg8000.dbapi.IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="L'étudiant spécifié n'existe pas.")
    except Exception:
        db.rollback()
        logger.exception("Erreur lors de l'enregistrement d'un consentement RGPD")
        raise HTTPException(status_code=400, detail="Impossible d'enregistrer le consentement.")
    finally:
        cursor.close()


@router.delete("/{id_consentement}", status_code=status.HTTP_204_NO_CONTENT)
def delete_consentement(
    id_consentement: int,
    db=Depends(get_db),
    identity: dict = Depends(current_identity),
):
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT id_etudiant FROM CONSENTEMENT_RGPD WHERE id_consentement = %s;",
            (id_consentement,),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Consentement introuvable.")
        check_owner_or_admin(identity, row[0])
        refuser_compte_anonymise(cursor, row[0])

        cursor.execute(
            "DELETE FROM CONSENTEMENT_RGPD WHERE id_consentement = %s;",
            (id_consentement,),
        )
        db.commit()
        return
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception("Erreur lors de la suppression du consentement %s", id_consentement)
        raise HTTPException(status_code=400, detail="Impossible de supprimer le consentement.")
    finally:
        cursor.close()
