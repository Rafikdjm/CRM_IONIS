"""
Authentification pour les routes sensibles (admin, indicateurs, données RGPD).

Deux mécanismes coexistent :
- Clé API partagée (X-API-Key) pour les outils/scripts serveur ;
- JWT (via l'en-tête Authorization: Bearer <token>) pour les utilisateurs du
  front-end (administrateur ou alumni connecté par OTP).

Pour les données personnelles (/etudiants/*, /consentements/*), on applique
une règle "propriétaire ou admin" : un alumni ne peut lire/modifier que ses
propres données, jamais celles d'un autre alumni.
"""
import jwt
from fastapi import Depends, Header, HTTPException, status

from config import settings


def _decode_jwt(authorization: str | None) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentification requise.",
        )
    token = authorization[7:].strip()
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expirée. Reconnectez-vous.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide.",
        )


def require_admin_api_key(
    x_api_key: str | None = Header(None, alias="X-API-Key"),
    authorization: str | None = Header(None, alias="Authorization"),
) -> None:
    """Accès admin : clé API partagée OU token JWT de rôle `admin`."""
    if x_api_key and x_api_key == settings.admin_api_key:
        return
    if authorization:
        try:
            payload = _decode_jwt(authorization)
        except HTTPException:
            payload = None
        if payload and payload.get("role") == "admin":
            return
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Accès administrateur requis (clé API ou session admin).",
    )


def current_identity(
    x_api_key: str | None = Header(None, alias="X-API-Key"),
    authorization: str | None = Header(None, alias="Authorization"),
) -> dict:
    """Identité de l'appelant.

    Retourne {"kind": "admin"} (clé API ou token admin) ou
    {"kind": "alumni", "id_etudiant": int}. Lève 401 si aucun mécanisme valide.
    """
    if x_api_key and x_api_key == settings.admin_api_key:
        return {"kind": "admin"}
    payload = _decode_jwt(authorization)
    if payload.get("role") == "admin":
        return {"kind": "admin"}
    if payload.get("role") == "alumni" and payload.get("id_etudiant"):
        return {"kind": "alumni", "id_etudiant": int(payload["id_etudiant"])}
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Authentification alumni requise.",
    )


def check_owner_or_admin(identity: dict, id_etudiant: int) -> None:
    """Lève 403 si l'appelant n'est ni admin ni l'alumni ciblé."""
    if identity["kind"] == "admin":
        return
    if identity["kind"] == "alumni" and identity["id_etudiant"] == id_etudiant:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Accès refusé : vous ne pouvez consulter ou modifier que vos propres données.",
    )


def require_owner_or_admin(
    id_etudiant: int,
    identity: dict = Depends(current_identity),
) -> None:
    """Dépendance FastAPI pour les routes "/etudiants/{id}" (propriétaire ou admin)."""
    check_owner_or_admin(identity, id_etudiant)
