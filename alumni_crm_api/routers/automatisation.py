import io
import logging

import pandas as pd
import pg8000.dbapi
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import ValidationError

import schemas
from config import settings
from database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Automatisation"])

ALLOWED_EXTENSIONS = (".csv", ".xlsx")
MAX_UPLOAD_SIZE = settings.max_upload_size_mb * 1024 * 1024


@router.post("/upload-etudiants/")
async def upload_etudiants(file: UploadFile = File(...), db=Depends(get_db)):
    filename = (file.filename or "").lower()

    # --- Validation du fichier avant tout traitement -----------------------
    if not filename.endswith(ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail="Seuls les fichiers .csv ou .xlsx sont acceptés.")

    contents = await file.read()
    if len(contents) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Fichier trop volumineux (max {settings.max_upload_size_mb} Mo).",
        )

    buffer = io.BytesIO(contents)
    try:
        df = pd.read_csv(buffer) if filename.endswith(".csv") else pd.read_excel(buffer)
        df = df.astype(object).where(pd.notnull(df), None)

        if "poste_actuel" in df.columns:
            df["poste_actuel"] = df["poste_actuel"].map({
                1.0: True, 0.0: False,
                1: True, 0: False,
                "TRUE": True, "FALSE": False,
                True: True, False: False,
                None: None,
            })
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur lors de la lecture du fichier : {e}")

    cursor = db.cursor()
    inserted_etudiants = 0
    inserted_experiences = 0

    try:
        # Optimisation : on précharge les entreprises existantes en UNE requête
        # au lieu de faire un SELECT par ligne du fichier (N+1).
        cursor.execute("SELECT id_entreprise, nom_entreprise FROM ENTREPRISE;")
        entreprises_existantes = {nom: id_ for id_, nom in cursor.fetchall()}

        for index, row in df.iterrows():
            # Validation de la ligne : avant, les valeurs brutes du fichier
            # étaient insérées telles quelles, sans passer par Pydantic.
            try:
                etudiant_data = schemas.EtudiantCreate(
                    nom=row["nom"],
                    prenom=row["prenom"],
                    email=row["email"],
                    email_academique=row.get("email_academique"),
                    telephone=row["telephone"],
                    date_naissance=row["date_naissance"],
                    parcours_anterieur=row["parcours_anterieur"],
                    date_inscription=row["date_inscription"],
                    id_promotion=row["id_promotion"],
                )
            except (KeyError, ValidationError) as e:
                raise HTTPException(status_code=400, detail=f"Ligne {index + 1} invalide : {e}")

            query_etudiant = """
                INSERT INTO ETUDIANT (nom, prenom, email, email_academique, telephone,
                                       date_naissance, parcours_anterieur, date_inscription, id_promotion)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_etudiant;
            """
            cursor.execute(query_etudiant, (
                etudiant_data.nom, etudiant_data.prenom, etudiant_data.email,
                etudiant_data.email_academique, etudiant_data.telephone,
                etudiant_data.date_naissance, etudiant_data.parcours_anterieur,
                etudiant_data.date_inscription, etudiant_data.id_promotion,
            ))
            id_etudiant = cursor.fetchone()[0]
            inserted_etudiants += 1

            nom_entreprise = row.get("nom_entreprise")
            if nom_entreprise is not None:
                id_entreprise = entreprises_existantes.get(nom_entreprise)

                if id_entreprise is None:
                    query_entreprise = """
                        INSERT INTO ENTREPRISE (nom_entreprise, secteur_activite, pays, ville)
                        VALUES (%s, %s, %s, %s) RETURNING id_entreprise;
                    """
                    cursor.execute(query_entreprise, (
                        nom_entreprise,
                        row.get("secteur_activite", "Non renseigné"),
                        row.get("pays_entreprise", "Non renseigné"),
                        row.get("ville_entreprise", "Non renseignée"),
                    ))
                    id_entreprise = cursor.fetchone()[0]
                    # Mise à jour du cache local pour éviter de recréer la même
                    # entreprise si elle réapparaît plus loin dans le fichier.
                    entreprises_existantes[nom_entreprise] = id_entreprise

                query_exp = """
                    INSERT INTO EXPERIENCE_PRO (intitule_poste, type_contrat, date_debut, date_fin,
                                                 salaire, poste_actuel, id_entreprise, id_etudiant)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                """
                cursor.execute(query_exp, (
                    row["intitule_poste"],
                    row["type_contrat"],
                    row["date_debut_exp"],
                    row.get("date_fin_exp"),
                    row.get("salaire", 0),
                    row.get("poste_actuel", True),
                    id_entreprise,
                    id_etudiant,
                ))
                inserted_experiences += 1

        db.commit()
        return {
            "message": f"Importation réussie : {inserted_etudiants} étudiants et "
                       f"{inserted_experiences} expériences ajoutés."
        }

    except HTTPException:
        db.rollback()
        raise
    except pg8000.dbapi.IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Contrainte violée autour de la ligne {inserted_etudiants + 1} "
                   f"(promotion inexistante, email en doublon...).",
        )
    except Exception:
        db.rollback()
        logger.exception("Erreur d'import autour de la ligne %s", inserted_etudiants + 1)
        raise HTTPException(
            status_code=400,
            detail=f"Erreur d'insertion autour de la ligne {inserted_etudiants + 1}.",
        )
    finally:
        cursor.close()
