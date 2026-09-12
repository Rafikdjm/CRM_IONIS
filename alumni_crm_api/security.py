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
from fastapi import Depends, Header, HTTPException, Query, status

from config import settings


def _decode_jwt(authorization: str | None = None, token: str | None = None) -> dict:
    """Décode un JWT depuis l'en-tête Authorization OU le paramètre `token`.

    Permet aux téléchargements natifs du navigateur (anchor `<a href>`), qui
    ne peuvent pas envoyer l'en-tête Authorization, de s'authentifier via
    `?token=<jwt>` (cas des exports sur mobile notamment).
    """
    if not token:
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


def _is_admin(x_api_key: str | None, authorization: str | None, token: str | None = None) -> bool:
    """Vrai si l'appelant est authentifié comme administrateur (clé API ou
    JWT avec role=admin). Sans lever d'exception : l'appelant décide du 401."""
    if x_api_key and x_api_key == settings.admin_api_key:
        return True
    try:
        payload = _decode_jwt(authorization, token)
    except HTTPException:
        return False
    return bool(payload and payload.get("role") == "admin")


def require_admin_api_key(
    x_api_key: str | None = Header(None, alias="X-API-Key"),
    authorization: str | None = Header(None, alias="Authorization"),
) -> None:
    """Accès admin : clé API partagée OU token JWT (header Authorization).

    N'accepte PAS de token en query string `?token=` : un token dans une URL
    peut fuiter via les logs de proxy, l'historique ou l'en-tête Referer. Les
    seules routes qui tolèrent `?token=` sont les téléchargements natifs du
    navigateur (exports mobiles via `<a href>`, impossible d'envoyer un header)
    — elles utilisent explicitement require_admin_api_key_download.
    """
    if not _is_admin(x_api_key, authorization):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Accès administrateur requis (clé API ou session admin).",
        )


def require_admin_api_key_download(
    x_api_key: str | None = Header(None, alias="X-API-Key"),
    authorization: str | None = Header(None, alias="Authorization"),
    token: str | None = Query(None),
) -> None:
    """Variante de require_admin_api_key réservée aux téléchargements natifs.

    Autorise le token JWT en query string (`?token=`) car un lien `<a href>`
    ne peut pas transporter l'en-tête Authorization (cas des exports sur
    mobile). À n'utiliser QUE sur les routes de téléchargement.
    """
    if not _is_admin(x_api_key, authorization, token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Accès administrateur requis (clé API ou session admin).",
        )


def _decode_identity(
    x_api_key: str | None, authorization: str | None, token: str | None = None
) -> dict:
    """Identité de l'appelant (sans lever de 403 si non authentifié)."""
    if x_api_key and x_api_key == settings.admin_api_key:
        return {"kind": "admin"}
    payload = _decode_jwt(authorization, token)
    if payload.get("role") == "admin":
        return {"kind": "admin"}
    if payload.get("role") == "alumni" and payload.get("id_etudiant"):
        return {"kind": "alumni", "id_etudiant": int(payload["id_etudiant"])}
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Authentification alumni requise.",
    )


def current_identity(
    x_api_key: str | None = Header(None, alias="X-API-Key"),
    authorization: str | None = Header(None, alias="Authorization"),
) -> dict:
    """Identité de l'appelant.

    Retourne {"kind": "admin"} (clé API ou token admin) ou
    {"kind": "alumni", "id_etudiant": int}. Lève 401/403 si aucun mécanisme
    valide. N'accepte PAS de token en query string (voir
    current_identity_download pour les seuls téléchargements natifs mobiles).
    """
    return _decode_identity(x_api_key, authorization)


def current_identity_download(
    x_api_key: str | None = Header(None, alias="X-API-Key"),
    authorization: str | None = Header(None, alias="Authorization"),
    token: str | None = Query(None),
) -> dict:
    """Variante de current_identity réservée aux téléchargements natifs du
    navigateur : autorise le token JWT en query string (`?token=`), car un
    lien `<a href>` ne peut pas transporter l'en-tête Authorization.
    """
    return _decode_identity(x_api_key, authorization, token)


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
