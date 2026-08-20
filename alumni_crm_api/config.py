"""
Configuration centralisée de l'application.

Correction majeure : les identifiants de connexion ne sont plus codés en dur
dans le code source (risque critique si le dépôt est public ou partagé).
Ils sont désormais lus depuis des variables d'environnement, avec un fichier
.env optionnel en local (voir .env.example).
"""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv est optionnel : si absent, on lit simplement les vraies
    # variables d'environnement du système (cas d'un déploiement classique).
    pass


class Settings:
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_name: str = os.getenv("DB_NAME", "alumni_crm")
    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "")
    db_port: int = int(os.getenv("DB_PORT", "5432"))

    # Environnement : "development" désactive le rate-limiting OTP,
    # "production" (ou toute autre valeur) garde le comportement strict.
    # Défaut prudent : production, pour ne jamais affaiblir la sécurité
    # si la variable est oubliée au déploiement.
    env: str = os.getenv("ENV", "production")

    # Clé simple pour protéger les routes d'administration (RGPD, indicateurs).
    # À remplacer par une vraie authentification (OAuth2 / JWT) si l'application
    # doit servir plusieurs utilisateurs avec des rôles différents.
    admin_api_key: str = os.getenv("ADMIN_API_KEY", "")

    pool_size: int = int(os.getenv("DB_POOL_SIZE", "5"))
    max_upload_size_mb: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "5"))

    # Délai (en mois) avant la purge définitive d'un compte anonymisé.
    # La suppression de compte RGPD passe d'abord par une anonymisation ;
    # purge.py supprime définitivement les comptes dont la date
    # d'anonymisation dépasse ce délai.
    purge_delay_months: int = int(os.getenv("PURGE_DELAY_MONTHS", "6"))

    jwt_secret: str = os.getenv("JWT_SECRET", "")
    otp_mode: str = os.getenv("OTP_MODE", "console")
    academic_email_domain: str = os.getenv("ACADEMIC_EMAIL_DOMAIN", "ionis-stm.com")
    resend_api_key: str = os.getenv("RESEND_API_KEY", "")
    email_from: str = os.getenv("EMAIL_FROM", "")
    admin_access_code: str = os.getenv("ADMIN_ACCESS_CODE", "")


settings = Settings()

if not settings.db_password:
    raise RuntimeError(
        "DB_PASSWORD n'est pas défini. Créez un fichier .env "
        "(voir .env.example) ou exportez la variable d'environnement."
    )

if not settings.admin_api_key:
    raise RuntimeError(
        "ADMIN_API_KEY n'est pas défini. Cette clé protège les routes "
        "d'administration et RGPD : elle est obligatoire."
    )

if not settings.jwt_secret or len(settings.jwt_secret) < 32:
    raise RuntimeError(
        "JWT_SECRET n'est pas défini ou est trop court (< 32 caractères). "
        "Générez une clé avec : python -c \"import secrets; print(secrets.token_hex(32))\""
    )
