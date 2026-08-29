"""
Router Newsletter : envoi de newsletters aux alumni avec consentement actif.

Filtre de ciblage : promotion, secteur, consentement newsletter.
En mode console (OTP_MODE=console), les emails sont loggés en local.
En mode resend, les emails sont envoyés via l'API Resend.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

import bleach
import pg8000.dbapi
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from config import settings
from database import get_db
from security import require_admin_api_key
from utils import rows_to_dicts

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/newsletter", tags=["Newsletter"])


# ── Schémas ──────────────────────────────────────────────────────
class NewsletterRequest(BaseModel):
    """Paramètres de ciblage pour l'envoi de newsletter."""
    sujet: str
    corps_html: str
    id_promotion: Optional[int] = None
    secteur_activite: Optional[str] = None


class NewsletterResponse(BaseModel):
    message: str
    envoyer: int
    cibles: int


ALLOWED_TAGS = list(bleach.ALLOWED_TAGS) + [
    "h1", "h2", "h3", "p", "br", "hr", "ul", "ol", "li", "strong", "em",
    "a", "img", "table", "thead", "tbody", "tr", "th", "td", "div", "span",
    "blockquote", "pre", "code",
]
ALLOWED_ATTRS = {
    **bleach.ALLOWED_ATTRIBUTES,
    "a": ["href", "title", "target"],
    "img": ["src", "alt", "width", "height"],
    "div": ["style"],
    "span": ["style"],
    "p": ["style"],
    "td": ["style"],
    "th": ["style"],
}


def _sanitize_html(raw_html: str) -> str:
    return bleach.clean(raw_html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True)


# ── Fonction d'envoi email ──────────────────────────────────────
def _send_newsletter_email(email: str, prenom: str, sujet: str, corps_html: str) -> bool:
    mode = getattr(settings, "otp_mode", "console")

    if mode == "console":
        logger.info("=" * 60)
        logger.info("NEWSLETTER → %s (%s) | Sujet : %s", email, prenom, sujet)
        logger.info("=" * 60)
        return True

    if mode == "resend":
        import resend

        if not settings.resend_api_key or not settings.email_from:
            logger.error("RESEND_API_KEY ou EMAIL_FROM non configuré")
            return False

        resend.api_key = settings.resend_api_key
        safe_html = _sanitize_html(corps_html)

        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"></head>
        <body style="margin:0;padding:0;background:#f4f7f9;font-family:'Segoe UI',Roboto,Arial,sans-serif;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f7f9;padding:40px 0;">
                <tr><td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 4px 6px rgba(0,0,0,.05);">
                        <tr>
                            <td style="background:#2563eb;padding:30px;text-align:center;">
                                <h1 style="color:#fff;margin:0;font-size:24px;">Alumni CRM — Newsletter</h1>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding:40px;">
                                <p style="color:#4b5563;line-height:1.6;">Bonjour {prenom},</p>
                                <div style="color:#1f2937;line-height:1.8;margin-top:20px;">
                                    {safe_html}
                                </div>
                                <div style="margin-top:30px;text-align:center;">
                                    <a href="#" style="display:inline-block;background:#2563eb;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;">
                                        Mettre à jour mon profil
                                    </a>
                                </div>
                            </td>
                        </tr>
                        <tr>
                            <td style="background:#f9fafb;padding:20px;text-align:center;border-top:1px solid #e5e7eb;">
                                <p style="color:#9ca3af;font-size:12px;margin:0;">
                                    © {datetime.now().year} Alumni CRM. Vous recevez cet email car vous avez accepté la newsletter.
                                    <a href="#" style="color:#6366f1;">Se désinscrire</a>
                                </p>
                            </td>
                        </tr>
                    </table>
                </td></tr>
            </table>
        </body>
        </html>
        """

        try:
            params = {
                "from": settings.email_from,
                "to": [email],
                "subject": sujet,
                "html": full_html,
            }
            email_response = resend.Emails.send(params)
            logger.info("Newsletter envoyée à %s (ID: %s)", email, email_response.get("id", "N/A"))
            return True
        except Exception as e:
            logger.error("Échec envoi newsletter à %s : %s", email, str(e))
            return False

    return False


# ── Endpoint principal ──────────────────────────────────────────
@router.post("/envoyer", response_model=NewsletterResponse, dependencies=[Depends(require_admin_api_key)])
def envoyer_newsletter(body: NewsletterRequest, db=Depends(get_db)):
    """
    Envoie une newsletter aux alumni ayant le consentement newsletter actif.
    Filtres optionnels : id_promotion, secteur_activite.

    RGPD : en plus du consentement 'newsletter' actif, un refus explicite
    du consentement 'prise_de_contact' exclut l'alumni de l'envoi (le
    contact est refusé). Un alumni sans vote 'prise_de_contact' reste
    éligible, comme pour les relances questionnaire.
    """
    cursor = db.cursor()
    try:
        # Construire la requête de ciblage
        base_query = """
            SELECT e.id_etudiant, e.nom, e.prenom, e.email
            FROM ETUDIANT e
            JOIN CONSENTEMENT_RGPD c ON e.id_etudiant = c.id_etudiant
            WHERE c.type_consentement = 'newsletter'
              AND c.statut = 'actif'
              AND COALESCE((
                  SELECT pd.statut FROM CONSENTEMENT_RGPD pd
                  WHERE pd.id_etudiant = e.id_etudiant
                    AND pd.type_consentement = 'prise_de_contact'
                  ORDER BY pd.date_consentement DESC, pd.id_consentement DESC
                  LIMIT 1
              ), 'inconnu') <> 'refuse'
              AND e.date_anonymisation IS NULL
              AND e.email IS NOT NULL
              AND e.email != ''
        """
        params: list = []

        if body.id_promotion is not None:
            base_query += " AND e.id_promotion = %s"
            params.append(body.id_promotion)

        if body.secteur_activite:
            base_query += """
                AND EXISTS (
                    SELECT 1 FROM EXPERIENCE_PRO exp
                    JOIN ENTREPRISE ent ON exp.id_entreprise = ent.id_entreprise
                    WHERE exp.id_etudiant = e.id_etudiant
                      AND ent.secteur_activite ILIKE %s
                )
            """
            params.append(f"%{body.secteur_activite}%")

        base_query += " ORDER BY e.nom, e.prenom"

        cursor.execute(base_query, tuple(params))
        alumni_list = rows_to_dicts(cursor, cursor.fetchall())

        if not alumni_list:
            return NewsletterResponse(
                message="Aucun alumni trouvé avec les critères de ciblage spécifiés.",
                envoyer=0,
                cibles=0,
            )

        # Envoi
        envoyer_count = 0
        for alumni in alumni_list:
            email = alumni.get("email", "")
            prenom = alumni.get("prenom", "")
            if not email:
                continue

            sent = _send_newsletter_email(email, prenom, body.sujet, body.corps_html)
            if sent:
                envoyer_count += 1

        logger.info(
            "Newsletter envoyée : %d/%d emails envoyés avec succès",
            envoyer_count,
            len(alumni_list),
        )

        return NewsletterResponse(
            message=f"Newsletter envoyée avec succès à {envoyer_count}/{len(alumni_list)} alumni.",
            envoyer=envoyer_count,
            cibles=len(alumni_list),
        )

    except Exception:
        logger.exception("Erreur lors de l'envoi de la newsletter")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'envoi de la newsletter.",
        )
    finally:
        cursor.close()
