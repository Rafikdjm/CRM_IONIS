import json
import logging
from typing import List

import pg8000.dbapi
from fastapi import APIRouter, Depends, HTTPException, status

import schemas
from database import get_db
from security import require_admin_api_key, require_owner_or_admin
from utils import refuser_compte_anonymise, rows_to_dicts

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/questionnaires", tags=["Questionnaire Annuel"])

admin_router = APIRouter(
    prefix="/admin/questionnaires",
    tags=["Questionnaire Annuel - Admin"],
    dependencies=[Depends(require_admin_api_key)],
)


# ─────────────────────────────────────────────
# ROUTES ADMIN : creer, lister, desactiver
# ─────────────────────────────────────────────


@admin_router.post("/", response_model=schemas.Questionnaire, status_code=status.HTTP_201_CREATED)
def creer_questionnaire(data: schemas.QuestionnaireCreate, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO QUESTIONNAIRE (titre, description) VALUES (%s, %s) RETURNING id_questionnaire;",
            (data.titre, data.description),
        )
        id_q = cursor.fetchone()[0]

        for i, q in enumerate(data.questions):
            options_json = json.dumps(q.options) if q.options else "[]"
            cursor.execute(
                "INSERT INTO QUESTION (id_questionnaire, texte, type, options, ordre, tag, conditionnee_statut_emploi) "
                "VALUES (%s, %s, %s, %s::jsonb, %s, %s, %s);",
                (id_q, q.texte, q.type, options_json, q.ordre if q.ordre else i, q.tag, q.conditionnee_statut_emploi),
            )

        db.commit()
        return {"id_questionnaire": id_q, "titre": data.titre, "description": data.description,
                "actif": True, "questions": []}
    except Exception:
        db.rollback()
        logger.exception("Erreur lors de la creation du questionnaire")
        raise HTTPException(status_code=400, detail="Impossible de creer le questionnaire.")
    finally:
        cursor.close()


@admin_router.get("/", response_model=List[schemas.Questionnaire])
def lister_questionnaires(db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT qn.id_questionnaire, qn.titre, qn.description, qn.date_creation, qn.actif,"
            "  COUNT(q.id_question) AS nb_questions,"
            "  ARRAY_REMOVE(ARRAY_AGG(DISTINCT q.tag), NULL) AS tags "
            "FROM QUESTIONNAIRE qn "
            "LEFT JOIN QUESTION q ON q.id_questionnaire = qn.id_questionnaire "
            "GROUP BY qn.id_questionnaire ORDER BY qn.date_creation DESC;"
        )
        return rows_to_dicts(cursor, cursor.fetchall())
    finally:
        cursor.close()


@admin_router.get("/{id_questionnaire}", response_model=schemas.QuestionnaireDetail)
def detail_questionnaire_admin(id_questionnaire: int, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT id_questionnaire, titre, description, date_creation, actif "
            "FROM QUESTIONNAIRE WHERE id_questionnaire = %s;",
            (id_questionnaire,),
        )
        qrow = cursor.fetchone()
        if not qrow:
            raise HTTPException(status_code=404, detail="Questionnaire introuvable.")

        cols = [d[0] for d in cursor.description]
        qdata = dict(zip(cols, qrow))

        cursor.execute(
            "SELECT id_question, id_questionnaire, texte, type, options, ordre, tag, conditionnee_statut_emploi "
            "FROM QUESTION WHERE id_questionnaire = %s ORDER BY ordre;",
            (id_questionnaire,),
        )
        questions_raw = rows_to_dicts(cursor, cursor.fetchall())
        for qr in questions_raw:
            if isinstance(qr.get("options"), str):
                try:
                    qr["options"] = json.loads(qr["options"])
                except (json.JSONDecodeError, TypeError):
                    qr["options"] = []
            qr["conditionnee_statut_emploi"] = bool(qr.get("conditionnee_statut_emploi"))

        return {**qdata, "questions": questions_raw}
    except HTTPException:
        raise
    finally:
        cursor.close()


@admin_router.delete("/{id_questionnaire}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer_questionnaire(id_questionnaire: int, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM REPONSE_QUESTIONNAIRE WHERE id_questionnaire = %s;", (id_questionnaire,))
        cursor.execute("DELETE FROM QUESTION WHERE id_questionnaire = %s;", (id_questionnaire,))
        cursor.execute("DELETE FROM QUESTIONNAIRE WHERE id_questionnaire = %s;", (id_questionnaire,))
        if cursor.rowcount == 0:
            db.rollback()
            raise HTTPException(status_code=404, detail="Questionnaire introuvable.")
        db.commit()
        return
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception("Erreur lors de la suppression du questionnaire %s", id_questionnaire)
        raise HTTPException(status_code=400, detail="Impossible de supprimer le questionnaire.")
    finally:
        cursor.close()


@admin_router.get("/{id_questionnaire}/reponses")
def voir_reponses(id_questionnaire: int, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT id_question, texte, type, options, ordre, tag, conditionnee_statut_emploi "
            "FROM QUESTION WHERE id_questionnaire = %s ORDER BY ordre;",
            (id_questionnaire,),
        )
        questions_raw = rows_to_dicts(cursor, cursor.fetchall())
        questions_map = {}
        for q in questions_raw:
            if isinstance(q.get("options"), str):
                try:
                    q["options"] = json.loads(q["options"])
                except (json.JSONDecodeError, TypeError):
                    q["options"] = []
            q["conditionnee_statut_emploi"] = bool(q.get("conditionnee_statut_emploi"))
            questions_map[str(q["id_question"])] = q

        cursor.execute(
            "SELECT r.id_reponse, r.id_etudiant, r.id_questionnaire, r.reponses, r.date_reponse,"
            " e.nom, e.prenom, e.email "
            "FROM REPONSE_QUESTIONNAIRE r "
            "JOIN ETUDIANT e ON r.id_etudiant = e.id_etudiant "
            "WHERE r.id_questionnaire = %s "
            "ORDER BY r.date_reponse DESC;",
            (id_questionnaire,),
        )
        rows = rows_to_dicts(cursor, cursor.fetchall())
        for r in rows:
            raw = r.get("reponses")
            if isinstance(raw, str):
                try:
                    r["reponses"] = json.loads(raw)
                except (json.JSONDecodeError, TypeError):
                    r["reponses"] = {}
        return {"reponses": rows, "questions": questions_map, "total": len(rows)}
    finally:
        cursor.close()


@admin_router.patch("/{id_questionnaire}/desactiver")
def desactiver_questionnaire(id_questionnaire: int, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute(
            "UPDATE QUESTIONNAIRE SET actif = FALSE WHERE id_questionnaire = %s;",
            (id_questionnaire,),
        )
        if cursor.rowcount == 0:
            db.rollback()
            raise HTTPException(status_code=404, detail="Questionnaire introuvable.")
        db.commit()
        return {"message": "Questionnaire desactive."}
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Impossible de desactiver le questionnaire.")
    finally:
        cursor.close()


@admin_router.put("/{id_questionnaire}", response_model=schemas.QuestionnaireDetail)
def modifier_questionnaire(id_questionnaire: int, data: schemas.QuestionnaireCreate, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT id_questionnaire FROM QUESTIONNAIRE WHERE id_questionnaire = %s;",
            (id_questionnaire,),
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Questionnaire introuvable.")

        cursor.execute(
            "SELECT id_question FROM QUESTION WHERE id_questionnaire = %s;",
            (id_questionnaire,),
        )
        existing_ids = {row[0] for row in cursor.fetchall()}

        submitted_ids = {q.id_question for q in data.questions if q.id_question}
        ids_to_delete = existing_ids - submitted_ids

        if ids_to_delete:
            placeholders = ",".join(["%s"] * len(ids_to_delete))
            cursor.execute(
                f"SELECT COUNT(*) FROM REPONSE_QUESTIONNAIRE "
                f"WHERE id_questionnaire = %s AND reponses ?| array[{placeholders}];",
                [id_questionnaire] + list(ids_to_delete),
            )
            has_responses = cursor.fetchone()[0] > 0
            if has_responses:
                db.rollback()
                raise HTTPException(
                    status_code=400,
                    detail="Impossible de supprimer des questions qui ont deja recu des reponses. "
                           "Desactivez le questionnaire et créez-en un nouveau si besoin.",
                )

        cursor.execute("UPDATE QUESTIONNAIRE SET titre = %s, description = %s WHERE id_questionnaire = %s;",
                        (data.titre, data.description, id_questionnaire))

        if ids_to_delete:
            placeholders = ",".join(["%s"] * len(ids_to_delete))
            cursor.execute(
                f"DELETE FROM QUESTION WHERE id_question IN ({placeholders});",
                list(ids_to_delete),
            )

        for i, q in enumerate(data.questions):
            options_json = json.dumps(q.options) if q.options else "[]"
            if q.id_question and q.id_question in existing_ids:
                cursor.execute(
                    "UPDATE QUESTION SET texte = %s, type = %s, options = %s::jsonb, ordre = %s, tag = %s, conditionnee_statut_emploi = %s "
                    "WHERE id_question = %s AND id_questionnaire = %s;",
                    (q.texte, q.type, options_json, q.ordre if q.ordre is not None else i, q.tag, q.conditionnee_statut_emploi, q.id_question, id_questionnaire),
                )
            else:
                cursor.execute(
                    "INSERT INTO QUESTION (id_questionnaire, texte, type, options, ordre, tag, conditionnee_statut_emploi) "
                    "VALUES (%s, %s, %s, %s::jsonb, %s, %s, %s);",
                    (id_questionnaire, q.texte, q.type, options_json, q.ordre if q.ordre is not None else i, q.tag, q.conditionnee_statut_emploi),
                )

        db.commit()

        cursor.execute(
            "SELECT id_question, id_questionnaire, texte, type, options, ordre, tag, conditionnee_statut_emploi "
            "FROM QUESTION WHERE id_questionnaire = %s ORDER BY ordre;",
            (id_questionnaire,),
        )
        questions_raw = rows_to_dicts(cursor, cursor.fetchall())
        for qr in questions_raw:
            if isinstance(qr.get("options"), str):
                try:
                    qr["options"] = json.loads(qr["options"])
                except (json.JSONDecodeError, TypeError):
                    qr["options"] = []
            qr["conditionnee_statut_emploi"] = bool(qr.get("conditionnee_statut_emploi"))

        return {"id_questionnaire": id_questionnaire, "titre": data.titre,
                "description": data.description, "actif": True, "questions": questions_raw}
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        logger.exception("Erreur lors de la modification du questionnaire %s", id_questionnaire)
        raise HTTPException(status_code=400, detail="Impossible de modifier le questionnaire.")
    finally:
        cursor.close()


# ─────────────────────────────────────────────
# ROUTES ALUMNI : consulter + repondre
# ─────────────────────────────────────────────


@admin_router.patch("/{id_questionnaire}/reactiver")
def reactiver_questionnaire(id_questionnaire: int, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute("SELECT actif FROM QUESTIONNAIRE WHERE id_questionnaire = %s;", (id_questionnaire,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Questionnaire introuvable.")
        if row[0]:
            return {"message": "Questionnaire deja actif."}

        cursor.execute(
            "UPDATE QUESTIONNAIRE SET actif = TRUE WHERE id_questionnaire = %s;",
            (id_questionnaire,),
        )
        db.commit()
        return {"message": "Questionnaire reactive."}
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Impossible de reactiver le questionnaire.")
    finally:
        cursor.close()


@router.get("/actif", response_model=schemas.QuestionnaireDetail)
def get_questionnaire_actif(db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT id_questionnaire, titre, description, date_creation, actif "
            "FROM QUESTIONNAIRE WHERE actif = TRUE "
            "ORDER BY date_creation DESC LIMIT 1;"
        )
        qrow = cursor.fetchone()
        if not qrow:
            raise HTTPException(status_code=404, detail="Aucun questionnaire actif.")

        cols = [d[0] for d in cursor.description]
        qdata = dict(zip(cols, qrow))

        cursor.execute(
            "SELECT id_question, id_questionnaire, texte, type, options, ordre, tag, conditionnee_statut_emploi "
            "FROM QUESTION WHERE id_questionnaire = %s ORDER BY ordre;",
            (qdata["id_questionnaire"],),
        )
        questions_raw = rows_to_dicts(cursor, cursor.fetchall())
        for qr in questions_raw:
            if isinstance(qr.get("options"), str):
                try:
                    qr["options"] = json.loads(qr["options"])
                except (json.JSONDecodeError, TypeError):
                    qr["options"] = []
            qr["conditionnee_statut_emploi"] = bool(qr.get("conditionnee_statut_emploi"))

        return {**qdata, "questions": questions_raw}
    except HTTPException:
        raise
    finally:
        cursor.close()


@router.get("/etudiant/{id_etudiant}/reponses")
def mes_reponses(id_etudiant: int, db=Depends(get_db), _auth=Depends(require_owner_or_admin)):
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT id_reponse, id_questionnaire, reponses, date_reponse "
            "FROM REPONSE_QUESTIONNAIRE WHERE id_etudiant = %s "
            "ORDER BY date_reponse DESC;",
            (id_etudiant,),
        )
        rows = rows_to_dicts(cursor, cursor.fetchall())
        for r in rows:
            raw = r.get("reponses")
            if isinstance(raw, str):
                try:
                    r["reponses"] = json.loads(raw)
                except (json.JSONDecodeError, TypeError):
                    r["reponses"] = {}
        return rows
    finally:
        cursor.close()


@router.post(
    "/{id_questionnaire}/repondre",
    status_code=status.HTTP_201_CREATED,
    tags=["Interface Etudiant / Alumni"],
)
def repondre_questionnaire(
    id_questionnaire: int,
    id_etudiant: int,
    data: schemas.ReponseCreate,
    db=Depends(get_db),
    _auth=Depends(require_owner_or_admin),
):
    cursor = db.cursor()
    try:
        refuser_compte_anonymise(cursor, id_etudiant)
        cursor.execute("SELECT actif FROM QUESTIONNAIRE WHERE id_questionnaire = %s;", (id_questionnaire,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Questionnaire introuvable.")
        if not row[0]:
            raise HTTPException(status_code=400, detail="Ce questionnaire n'est plus actif.")

        # Cohérence a minima : chaque clé de `reponses` doit correspondre à une
        # question du questionnaire visé. Choix documenté : erreur 422 explicite
        # (plutôt qu'un rejet silencieux) pour que l'alumni corrige son envoi.
        cursor.execute(
            "SELECT id_question FROM QUESTION WHERE id_questionnaire = %s;",
            (id_questionnaire,),
        )
        questions_valides = {str(rowq[0]) for rowq in cursor.fetchall()}
        cles_inconnues = [str(k) for k in data.reponses if str(k) not in questions_valides]
        if cles_inconnues:
            db.rollback()
            raise HTTPException(
                status_code=422,
                detail=(
                    "La réponse contient des clés qui ne correspondent à aucune "
                    f"question de ce questionnaire : {', '.join(sorted(cles_inconnues))}."
                ),
            )

        reponses_json = json.dumps(data.reponses)
        cursor.execute(
            "INSERT INTO REPONSE_QUESTIONNAIRE (id_etudiant, id_questionnaire, reponses) "
            "VALUES (%s, %s, %s::jsonb) "
            "ON CONFLICT (id_etudiant, id_questionnaire) "
            "DO UPDATE SET reponses = EXCLUDED.reponses, date_reponse = NOW();",
            (id_etudiant, id_questionnaire, reponses_json),
        )
        db.commit()
        return {"message": "Reponse enregistree avec succes."}
    except HTTPException:
        db.rollback()
        raise
    except pg8000.dbapi.IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Etudiant ou questionnaire introuvable.")
    except Exception:
        db.rollback()
        logger.exception("Erreur lors de l'enregistrement de la reponse")
        raise HTTPException(status_code=400, detail="Impossible d'enregistrer la reponse.")
    finally:
        cursor.close()


# ─────────────────────────────────────────────
# NOTIFICATION : relance alumni pour questionnaire
# ─────────────────────────────────────────────
from pydantic import BaseModel as _BaseModel
from typing import Optional as _Optional


class NotificationQuestionnaireRequest(_BaseModel):
    id_questionnaire: int
    id_promotion: _Optional[int] = None


@admin_router.post("/notififier")
def notifier_questionnaire(body: NotificationQuestionnaireRequest, db=Depends(get_db)):
    """
    Envoie une notification email aux alumni n'ayant pas encore répondu
    au questionnaire spécifié. Filtre optionnel par promotion.
    """
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT id_questionnaire, titre FROM QUESTIONNAIRE WHERE id_questionnaire = %s AND actif = TRUE;",
            (body.id_questionnaire,),
        )
        q = cursor.fetchone()
        if not q:
            raise HTTPException(status_code=404, detail="Questionnaire introuvable ou inactif.")

        query = """
            SELECT e.id_etudiant, e.nom, e.prenom, e.email
            FROM ETUDIANT e
            WHERE e.date_anonymisation IS NULL
              AND e.email IS NOT NULL
              AND e.email != ''
              AND NOT EXISTS (
                  SELECT 1 FROM REPONSE_QUESTIONNAIRE r
                  WHERE r.id_etudiant = e.id_etudiant
                    AND r.id_questionnaire = %s
              )
        """
        params: list = [body.id_questionnaire]

        if body.id_promotion is not None:
            query += " AND e.id_promotion = %s"
            params.append(body.id_promotion)

        query += " ORDER BY e.nom, e.prenom"
        cursor.execute(query, tuple(params))
        alumni_list = rows_to_dicts(cursor, cursor.fetchall())

        if not alumni_list:
            return {"message": "Tous les alumni ont déjà répondu ou aucun alumni éligible.", "notifies": 0, "cibles": 0}

        from routers.newsletter import _send_newsletter_email

        notifies = 0
        for alumni in alumni_list:
            email = alumni.get("email", "")
            prenom = alumni.get("prenom", "")
            if not email:
                continue

            sujet = f"Questionnaire Alumni CRM : {q[1]}"
            corps = (
                f"<p>Vous n'avez pas encore répondu au questionnaire "
                f"<strong>« {q[1]} »</strong>.</p>"
                f"<p>Ce questionnaire nous aide à suivre l'insertion professionnelle "
                f"des diplômés. Vos réponses sont anonymisées dans les statistiques.</p>"
                f"<p>Prenez 5 minutes pour le compléter depuis votre espace Alumni CRM.</p>"
            )
            sent = _send_newsletter_email(email, prenom, sujet, corps)
            if sent:
                notifies += 1

        logger.info("Relance questionnaire %d : %d/%d notifications envoyées",
                     body.id_questionnaire, notifies, len(alumni_list))

        return {
            "message": f"Relance envoyée à {notifies}/{len(alumni_list)} alumni.",
            "notifies": notifies,
            "cibles": len(alumni_list),
        }

    except HTTPException:
        raise
    except Exception:
        logger.exception("Erreur lors de la notification questionnaire")
        raise HTTPException(status_code=500, detail="Erreur lors de l'envoi des notifications.")
    finally:
        cursor.close()
