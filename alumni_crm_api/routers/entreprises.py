import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

import schemas
from database import get_db
from security import require_admin_api_key
from utils import rows_to_dicts

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/entreprises", tags=["Entreprises"])


@router.post("/", response_model=schemas.Entreprise, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin_api_key)])
def create_entreprise(entreprise: schemas.EntrepriseCreate, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        query = """
            INSERT INTO ENTREPRISE (nom_entreprise, secteur_activite, pays, ville)
            VALUES (%s, %s, %s, %s) RETURNING id_entreprise;
        """
        cursor.execute(query, (entreprise.nom_entreprise, entreprise.secteur_activite, entreprise.pays, entreprise.ville))
        id_generated = cursor.fetchone()[0]
        db.commit()
        return {**entreprise.model_dump(), "id_entreprise": id_generated}
    except Exception:
        db.rollback()
        logger.exception("Erreur lors de la création d'une entreprise")
        raise HTTPException(status_code=400, detail="Impossible de créer l'entreprise.")
    finally:
        cursor.close()


@router.get("/", response_model=schemas.PaginatedResponse[schemas.Entreprise])
def get_all_entreprises(
    search: Optional[str] = Query(None, description="Recherche par nom d'entreprise"),
    secteur: Optional[str] = Query(None, description="Filtrer par secteur d'activité"),
    pays: Optional[str] = Query(None, description="Filtrer par pays"),
    ville: Optional[str] = Query(None, description="Filtrer par ville"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1),
    db=Depends(get_db),
):
    cursor = db.cursor()
    try:
        base_query = " FROM ENTREPRISE WHERE 1=1"
        params: list = []

        if search:
            base_query += " AND nom_entreprise ILIKE %s"
            params.append(f"%{search}%")

        if secteur:
            base_query += " AND secteur_activite ILIKE %s"
            params.append(f"%{secteur}%")

        if pays:
            base_query += " AND pays ILIKE %s"
            params.append(f"%{pays}%")

        if ville:
            base_query += " AND ville ILIKE %s"
            params.append(f"%{ville}%")

        cursor.execute(f"SELECT COUNT(*) {base_query}", tuple(params))
        total = cursor.fetchone()[0]

        data_query = f"""
            SELECT id_entreprise, nom_entreprise, secteur_activite, pays, ville
            {base_query}
            ORDER BY nom_entreprise
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
    finally:
        cursor.close()


@router.get("/{id_entreprise}", response_model=schemas.Entreprise)
def get_entreprise(id_entreprise: int, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT id_entreprise, nom_entreprise, secteur_activite, pays, ville FROM ENTREPRISE WHERE id_entreprise = %s;",
            (id_entreprise,),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Entreprise introuvable.")
        return rows_to_dicts(cursor, [row])[0]
    except HTTPException:
        raise
    except Exception:
        logger.exception("Erreur lors de la récupération de l'entreprise %s", id_entreprise)
        raise HTTPException(status_code=400, detail="Impossible de récupérer l'entreprise.")
    finally:
        cursor.close()


@router.put("/{id_entreprise}", response_model=schemas.Entreprise, dependencies=[Depends(require_admin_api_key)])
def update_entreprise(id_entreprise: int, entreprise: schemas.EntrepriseCreate, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        query = """
            UPDATE ENTREPRISE
            SET nom_entreprise = %s, secteur_activite = %s, pays = %s, ville = %s
            WHERE id_entreprise = %s;
        """
        cursor.execute(query, (entreprise.nom_entreprise, entreprise.secteur_activite, entreprise.pays, entreprise.ville, id_entreprise))
        if cursor.rowcount == 0:
            db.rollback()
            raise HTTPException(status_code=404, detail="Entreprise introuvable.")
        db.commit()
        return {**entreprise.model_dump(), "id_entreprise": id_entreprise}
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception("Erreur lors de la mise à jour d'une entreprise")
        raise HTTPException(status_code=400, detail="Impossible de mettre à jour l'entreprise.")
    finally:
        cursor.close()


@router.delete("/{id_entreprise}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin_api_key)])
def delete_entreprise(id_entreprise: int, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM ENTREPRISE WHERE id_entreprise = %s;", (id_entreprise,))
        if cursor.rowcount == 0:
            db.rollback()
            raise HTTPException(status_code=404, detail="Entreprise introuvable.")
        db.commit()
        return
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception("Erreur lors de la suppression de l'entreprise %s", id_entreprise)
        raise HTTPException(status_code=400, detail="Impossible de supprimer l'entreprise.")
    finally:
        cursor.close()
