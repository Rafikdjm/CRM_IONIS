import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

import schemas
from database import get_db
from security import require_admin_api_key
from utils import rows_to_dicts

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/promotions", tags=["Promotions"])


@router.post("/", response_model=schemas.Promotion, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin_api_key)])
def create_promotion(promotion: schemas.PromotionCreate, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        query = """
            INSERT INTO PROMOTION (nom_promotion, annee_diplome, filiere)
            VALUES (%s, %s, %s) RETURNING id_promotion;
        """
        cursor.execute(query, (promotion.nom_promotion, promotion.annee_diplome, promotion.filiere))
        id_generated = cursor.fetchone()[0]
        db.commit()
        return {**promotion.model_dump(), "id_promotion": id_generated}
    except Exception:
        db.rollback()
        logger.exception("Erreur lors de la création d'une promotion")
        raise HTTPException(status_code=400, detail="Impossible de créer la promotion.")
    finally:
        cursor.close()


@router.get("/", response_model=schemas.PaginatedResponse[schemas.Promotion])
def get_all_promotions(
    search: Optional[str] = Query(None, description="Recherche par nom de promotion"),
    annee_min: Optional[int] = Query(None, ge=1950, le=2100, description="Année de diplôme minimum"),
    annee_max: Optional[int] = Query(None, ge=1950, le=2100, description="Année de diplôme maximum"),
    filiere: Optional[str] = Query(None, description="Filtrer par filière"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1),
    db=Depends(get_db),
):
    cursor = db.cursor()
    try:
        base_query = """
            FROM PROMOTION p
            LEFT JOIN ETUDIANT e ON p.id_promotion = e.id_promotion
            WHERE 1=1
        """
        params: list = []

        if search:
            base_query += " AND p.nom_promotion ILIKE %s"
            params.append(f"%{search}%")

        if annee_min is not None:
            base_query += " AND p.annee_diplome >= %s"
            params.append(annee_min)

        if annee_max is not None:
            base_query += " AND p.annee_diplome <= %s"
            params.append(annee_max)

        if filiere:
            base_query += " AND p.filiere ILIKE %s"
            params.append(f"%{filiere}%")

        cursor.execute(f"SELECT COUNT(DISTINCT p.id_promotion) {base_query}", tuple(params))
        total = cursor.fetchone()[0]

        data_query = f"""
            SELECT p.id_promotion, p.nom_promotion, p.annee_diplome, p.filiere,
                   COUNT(e.id_etudiant) AS nb_etudiants
            {base_query}
            GROUP BY p.id_promotion, p.nom_promotion, p.annee_diplome, p.filiere
            ORDER BY p.annee_diplome DESC, p.nom_promotion
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


@router.get("/{id_promotion}", response_model=schemas.Promotion)
def get_promotion(id_promotion: int, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            SELECT p.id_promotion, p.nom_promotion, p.annee_diplome, p.filiere,
                   COUNT(e.id_etudiant) AS nb_etudiants
            FROM PROMOTION p
            LEFT JOIN ETUDIANT e ON p.id_promotion = e.id_promotion
            WHERE p.id_promotion = %s
            GROUP BY p.id_promotion, p.nom_promotion, p.annee_diplome, p.filiere;
            """,
            (id_promotion,),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Promotion introuvable.")
        return rows_to_dicts(cursor, [row])[0]
    except HTTPException:
        raise
    except Exception:
        logger.exception("Erreur lors de la récupération de la promotion %s", id_promotion)
        raise HTTPException(status_code=400, detail="Impossible de récupérer la promotion.")
    finally:
        cursor.close()


@router.put("/{id_promotion}", response_model=schemas.Promotion, dependencies=[Depends(require_admin_api_key)])
def update_promotion(id_promotion: int, promotion: schemas.PromotionCreate, db=Depends(get_db)):
    """Modifie une promotion (nom, année de diplôme, filière). Même validation
    que la création : les champs nom_promotion, annee_diplome et filiere sont
    obligatoires via schemas.PromotionCreate."""
    cursor = db.cursor()
    try:
        query = """
            UPDATE PROMOTION
            SET nom_promotion = %s, annee_diplome = %s, filiere = %s
            WHERE id_promotion = %s;
        """
        cursor.execute(query, (
            promotion.nom_promotion,
            promotion.annee_diplome,
            promotion.filiere,
            id_promotion,
        ))
        if cursor.rowcount == 0:
            db.rollback()
            raise HTTPException(status_code=404, detail="Promotion introuvable.")
        db.commit()
        return {**promotion.model_dump(), "id_promotion": id_promotion}
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception("Erreur lors de la modification de la promotion %s", id_promotion)
        raise HTTPException(status_code=400, detail="Impossible de modifier la promotion.")
    finally:
        cursor.close()


@router.delete("/{id_promotion}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin_api_key)])
def delete_promotion(id_promotion: int, force: bool = Query(False), db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id_etudiant FROM ETUDIANT WHERE id_promotion = %s;", (id_promotion,))
        etudiants_ids = [row[0] for row in cursor.fetchall()]

        if etudiants_ids and not force:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Impossible de supprimer cette promotion : {len(etudiants_ids)} "
                    "étudiant(s) y sont rattachés. Confirmez la suppression en cascade "
                    "explicite (force=true) pour continuer."
                ),
            )

        if etudiants_ids:
            placeholders = ",".join(["%s"] * len(etudiants_ids))
            cursor.execute(
                f"DELETE FROM CONSENTEMENT_RGPD WHERE id_etudiant IN ({placeholders});",
                etudiants_ids,
            )
            cursor.execute(
                f"DELETE FROM OBTIENT WHERE id_etudiant IN ({placeholders});",
                etudiants_ids,
            )
            cursor.execute(
                f"DELETE FROM EXPERIENCE_PRO WHERE id_etudiant IN ({placeholders});",
                etudiants_ids,
            )
            cursor.execute(
                f"DELETE FROM ETUDIANT WHERE id_promotion = %s;", (id_promotion,),
            )

        cursor.execute("DELETE FROM PROMOTION WHERE id_promotion = %s;", (id_promotion,))
        if cursor.rowcount == 0:
            db.rollback()
            raise HTTPException(status_code=404, detail="Promotion introuvable.")
        db.commit()
        return
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception("Erreur lors de la suppression de la promotion %s", id_promotion)
        raise HTTPException(status_code=400, detail="Impossible de supprimer la promotion.")
    finally:
        cursor.close()
