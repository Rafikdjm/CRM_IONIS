"""
Router d'authentification administrateur.

Connexion par code d'accès fixe (pas d'email, pas d'OTP).
Le code est comparé via hash SHA-256 — la valeur clair ne passe jamais dans le code source.
Rate-limiting : 5 tentatives échouées par IP dans une fenêtre de 10 minutes.
"""
import hashlib
import logging
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

from config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth/admin", tags=["Auth Admin"])

# ── Rate-limiting (en mémoire, même pattern que otp.py) ──────────
_rate_limits: dict[str, list[datetime]] = {}
_RATE_WINDOW = 600   # 10 minutes
_MAX_ATTEMPTS = 5


def _check_rate_limit(key: str) -> bool:
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(seconds=_RATE_WINDOW)
    hits = _rate_limits.get(key, [])
    _rate_limits[key] = [t for t in hits if t > cutoff]
    if len(_rate_limits[key]) >= _MAX_ATTEMPTS:
        return False
    _rate_limits[key].append(now)
    return True


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


# ── Schémas ──────────────────────────────────────────────────────
class AdminLoginRequest(BaseModel):
    code: str


class AdminLoginResponse(BaseModel):
    token: str
    role: str = "admin"


# ── Endpoints ────────────────────────────────────────────────────
@router.post("/login", response_model=AdminLoginResponse, status_code=status.HTTP_200_OK)
def admin_login(body: AdminLoginRequest, request: Request):
    ip = request.client.host if request.client else "unknown"

    if not settings.admin_access_code:
        logger.error("ADMIN_ACCESS_CODE n'est pas défini dans la configuration.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service d'authentification indisponible.",
        )

    if not _check_rate_limit(f"admin_login:{ip}"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Trop de tentatives. Réessayez dans quelques minutes.",
        )

    code = body.code.strip()
    if not code:
        raise HTTPException(status_code=400, detail="Le code d'accès est requis.")

    submitted_hash = _hash_code(code)
    expected_hash = _hash_code(settings.admin_access_code)

    if submitted_hash != expected_hash:
        hits = _rate_limits.get(f"admin_login:{ip}", [])
        remaining = max(0, _MAX_ATTEMPTS - len(hits))
        logger.warning("Tentative de connexion admin échouée depuis l'IP %s (%d restante(s))", ip, remaining)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Code d'accès incorrect. {remaining} tentative{'s' if remaining != 1 else ''} restante{'s' if remaining != 1 else ''}.",
        )

    token_payload = {
        "sub": "admin",
        "role": "admin",
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }
    token = jwt.encode(token_payload, settings.jwt_secret, algorithm="HS256")

    logger.info("Connexion admin réussie depuis l'IP %s", ip)
    return AdminLoginResponse(token=token, role="admin")
