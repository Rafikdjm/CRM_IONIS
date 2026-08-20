"""
Router OTP : authentification par code à 6 chiffres envoyé par email.

En mode console (OTP_MODE=console), le code est affiché dans les logs
du serveur pour faciliter les tests en dev.
"""
import hashlib
import logging
import math
import random
import secrets
import string
from datetime import datetime, timedelta, timezone

import pg8000.dbapi
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr

from config import settings
from database import get_db
from utils import rows_to_dicts

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth/otp", tags=["Auth OTP"])

# ── Rate-limiting simple (en mémoire) ───────────────────────────
# Anti-spam : au plus une demande OTP toutes les 4 minutes, pour un
# même email et pour une même IP. Après un envoi autorisé, il faut
# attendre 4 minutes avant de pouvoir en demander un nouveau.
# Désactivé en développement (ENV=development) pour ne pas bloquer
# les tests locaux ; le comportement de production reste inchangé.
_RATE_MIN_INTERVAL = 240  # 4 minutes entre deux demandes autorisées
_rate_limits: dict[str, datetime] = {}


def _rate_limiting_enabled() -> bool:
    return settings.env != "development"


def _seconds_until_allowed(key: str) -> int:
    last = _rate_limits.get(key)
    if last is None:
        return 0
    elapsed = (datetime.now(timezone.utc) - last).total_seconds()
    if elapsed >= _RATE_MIN_INTERVAL:
        return 0
    return math.ceil(_RATE_MIN_INTERVAL - elapsed)


def _record_request(key: str) -> None:
    _rate_limits[key] = datetime.now(timezone.utc)


def _rate_limit_message(remaining: int) -> str:
    if remaining >= 60:
        minutes = math.ceil(remaining / 60)
        suffix = "s" if minutes > 1 else ""
        return (
            "Trop de demandes. Réessayez dans "
            f"{minutes} minute{suffix}."
        )
    return (
        "Trop de demandes. Réessayez dans "
        f"{remaining} seconde{'s' if remaining > 1 else ''}."
    )


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def _generate_code() -> str:
    return ''.join(random.choices(string.digits, k=6))


def _send_otp_email(email: str, code: str) -> None:
    mode = getattr(settings, "otp_mode", "console")
    
    if mode == "console":
        logger.info("=" * 60)
        logger.info("OTP CODE POUR %s : %s", email, code)
        logger.info("=" * 60)
        return

    if mode == "resend":
        import resend
        
        if not settings.resend_api_key or not settings.email_from:
            logger.error("RESEND_API_KEY ou EMAIL_FROM non configuré dans .env")
            return

        resend.api_key = settings.resend_api_key

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; background-color: #f4f7f9; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f7f9; padding: 40px 0;">
                <tr>
                    <td align="center">
                        <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                            <!-- Header -->
                            <tr>
                                <td style="background-color: #2563eb; padding: 30px; text-align: center;">
                                    <h1 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: 600;">Alumni CRM</h1>
                                </td>
                            </tr>
                            <!-- Body -->
                            <tr>
                                <td style="padding: 40px;">
                                    <h2 style="color: #1f2937; font-size: 20px; margin-bottom: 20px;">Votre code de connexion</h2>
                                    <p style="color: #4b5563; line-height: 1.6; margin-bottom: 30px;">
                                        Bonjour,<br><br>
                                        Voici votre code de connexion pour accéder à Alumni CRM :
                                    </p>
                                    
                                    <!-- Code Box -->
                                    <div style="background-color: #f3f4f6; border-radius: 8px; padding: 20px; text-align: center; margin-bottom: 30px; border: 1px dashed #d1d5db;">
                                        <span style="font-size: 32px; font-weight: bold; color: #2563eb; letter-spacing: 4px;">{code}</span>
                                    </div>

                                    <p style="color: #6b7280; font-size: 14px; line-height: 1.6;">
                                        Ce code est valide pendant <strong>10 minutes</strong>.
                                    </p>
                                    
                                    <!-- Security Notice -->
                                    <div style="background-color: #fffbeb; border-left: 4px solid #f59e0b; padding: 15px; margin-top: 30px; border-radius: 0 4px 4px 0;">
                                        <p style="color: #92400e; font-size: 13px; margin: 0;">
                                            <strong>Note de sécurité :</strong> Si vous n'êtes pas à l'origine de cette demande, veuillez ignorer cet email. Aucune action n'est requise.
                                        </p>
                                    </div>
                                </td>
                            </tr>
                            <!-- Footer -->
                            <tr>
                                <td style="background-color: #f9fafb; padding: 20px; text-align: center; border-top: 1px solid #e5e7eb;">
                                    <p style="color: #9ca3af; font-size: 12px; margin: 0;">
                                        © {datetime.now().year} Alumni CRM. Tous droits réservés.
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        try:
            params = {
                "from": settings.email_from,
                "to": [email],
                "subject": "Votre code de connexion Alumni CRM",
                "html": html_content,
            }
            email_response = resend.Emails.send(params)
            logger.info("Email OTP envoyé à %s via Resend (ID: %s)", email, email_response.get("id", "N/A"))
        except Exception as e:
            logger.error("Échec de l'envoi de l'email OTP à %s via Resend: %s", email, str(e))
            # Ne pas planter la demande OTP si l'email échoue, mais logger l'erreur


# ── Schémas ──────────────────────────────────────────────────────
class OTPRequest(BaseModel):
    email: EmailStr


class OTPVerify(BaseModel):
    email: EmailStr
    code: str


class OTPVerifyResponse(BaseModel):
    token: str
    alumni: dict | None = None
    role: str = "alumni"


# ── Endpoints ────────────────────────────────────────────────────
@router.post("/request", status_code=status.HTTP_200_OK)
def request_otp(body: OTPRequest, request: Request, db=Depends(get_db)):
    email = body.email.strip().lower()
    ip = request.client.host if request.client else "unknown"

    if _rate_limiting_enabled():
        remaining_email = _seconds_until_allowed(f"email:{email}")
        if remaining_email > 0:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=_rate_limit_message(remaining_email),
                headers={"Retry-After": str(remaining_email)},
            )

        remaining_ip = _seconds_until_allowed(f"ip:{ip}")
        if remaining_ip > 0:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Trop de demandes depuis votre adresse IP.",
                headers={"Retry-After": str(remaining_ip)},
            )

        # Les deux contrôles sont passés : on horodate les deux clés.
        _record_request(f"email:{email}")
        _record_request(f"ip:{ip}")
    else:
        logger.debug("Rate-limiting OTP désactivé (ENV=%s)", settings.env)

    cursor = db.cursor()
    try:
        logger.info("TMP-DEBUG OTP request — brut=%r normalisé=%r", body.email, email)
        cursor.execute("SELECT id_etudiant FROM etudiant WHERE LOWER(email) = %s;", (email,))
        found = cursor.fetchone()

        if not found:
            logger.info("OTP demandé pour email inconnu: %s — AUCUN CODE GÉNÉRÉ", email)
            return {"message": "Si ce compte existe, un code a été envoyé."}

        code = _generate_code()
        code_hashed = _hash_code(code)
        now = datetime.now(timezone.utc)
        expires = now + timedelta(minutes=10)

        # Un seul code valide à la fois : on invalide les demandes
        # précédentes pour éviter que /verify ne retombe sur un vieux code.
        cursor.execute(
            "UPDATE otp_codes SET used = TRUE WHERE LOWER(email) = %s AND used = FALSE;",
            (email,),
        )

        cursor.execute(
            """
            INSERT INTO otp_codes (email, code_hash, attempts, created_at, expires_at, used, ip_address)
            VALUES (%s, %s, 0, %s, %s, FALSE, %s);
            """,
            (email, code_hashed, now, expires, ip),
        )
        db.commit()

        _send_otp_email(email, code)

        return {"message": "Si ce compte existe, un code a été envoyé."}
    except Exception:
        db.rollback()
        logger.exception("Erreur lors de la demande OTP pour %s", email)
        raise HTTPException(status_code=500, detail="Erreur interne.")
    finally:
        cursor.close()


@router.post("/verify", response_model=OTPVerifyResponse)
def verify_otp(body: OTPVerify, db=Depends(get_db)):
    email = body.email.strip().lower()
    code = body.code.strip()

    if len(code) != 6 or not code.isdigit():
        raise HTTPException(status_code=400, detail="Code invalide.")

    cursor = db.cursor()
    try:
        code_hashed = _hash_code(code)

        cursor.execute(
            """
            SELECT id, attempts, expires_at, code_hash
            FROM otp_codes
            WHERE LOWER(email) = %s AND used = FALSE
            ORDER BY created_at DESC;
            """,
            (email,),
        )
        rows = cursor.fetchall()

        if not rows:
            raise HTTPException(status_code=400, detail="Code invalide.")

        now = datetime.now(timezone.utc)
        matched_id = None
        matched_expired = False
        matched_attempts = 0
        latest_active_id = None
        latest_active_attempts = 0

        # On recherche le code saisi parmi TOUS les codes non utilisés :
        # le bon code peut provenir d'une demande récente qui n'est pas
        # forcément la dernière créée.
        for otp_id, attempts, expires_at, stored_hash in rows:
            expires_utc = expires_at
            if isinstance(expires_utc, datetime) and expires_utc.tzinfo is None:
                expires_utc = expires_utc.replace(tzinfo=timezone.utc)
            expired = isinstance(expires_utc, datetime) and now > expires_utc

            if latest_active_id is None and not expired:
                latest_active_id = otp_id
                latest_active_attempts = attempts or 0

            if matched_id is None and stored_hash == code_hashed:
                matched_id = otp_id
                matched_expired = expired
                matched_attempts = attempts or 0

        if matched_id is not None and not matched_expired and matched_attempts >= 5:
            cursor.execute("UPDATE otp_codes SET used = TRUE WHERE id = %s;", (matched_id,))
            db.commit()
            raise HTTPException(status_code=429, detail="Trop de tentatives. Demandez un nouveau code.")

        if matched_id is None and latest_active_id is None:
            # Tous les codes de cet email sont expirés.
            raise HTTPException(status_code=410, detail="Code expiré. Demandez un nouveau code.")

        if matched_id is not None:
            if matched_expired:
                raise HTTPException(status_code=410, detail="Code expiré. Demandez un nouveau code.")

            # Succès : on invalide tous les codes en attente de cet email.
            cursor.execute(
                "UPDATE otp_codes SET used = TRUE WHERE LOWER(email) = %s AND used = FALSE;",
                (email,),
            )
            db.commit()
        else:
            new_attempts = latest_active_attempts + 1
            remaining = 5 - new_attempts
            cursor.execute(
                "UPDATE otp_codes SET attempts = %s WHERE id = %s;",
                (new_attempts, latest_active_id),
            )
            db.commit()

            if remaining <= 0:
                cursor.execute("UPDATE otp_codes SET used = TRUE WHERE id = %s;", (latest_active_id,))
                db.commit()
                raise HTTPException(status_code=429, detail="Trop de tentatives. Demandez un nouveau code.")

            raise HTTPException(
                status_code=400,
                detail=f"Code incorrect. {remaining} tentative{'s' if remaining > 1 else ''} restante{'s' if remaining > 1 else ''}.",
            )

        cursor.execute(
            "SELECT id_etudiant, nom, prenom, email FROM etudiant WHERE LOWER(email) = %s;",
            (email,),
        )
        alumni_row = cursor.fetchone()
        if not alumni_row:
            raise HTTPException(status_code=400, detail="Compte introuvable.")

        columns = [desc[0] for desc in cursor.description]
        alumni_data = dict(zip(columns, alumni_row))

        import jwt
        token_payload = {
            "sub": email,
            "role": "alumni",
            "id_etudiant": alumni_data["id_etudiant"],
            "exp": datetime.now(timezone.utc) + timedelta(hours=24),
        }
        token = jwt.encode(token_payload, settings.jwt_secret, algorithm="HS256")

        return OTPVerifyResponse(
            token=token,
            alumni={
                "id_etudiant": alumni_data["id_etudiant"],
                "nom": alumni_data["nom"],
                "prenom": alumni_data["prenom"],
                "email": alumni_data["email"],
            },
            role="alumni",
        )
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception("Erreur lors de la vérification OTP pour %s", email)
        raise HTTPException(status_code=500, detail="Erreur interne lors de la vérification.")
    finally:
        cursor.close()
