import logging


from fastapi import FastAPI


from routers import (
    admin,
    admin_auth,
    certifications,
    cleanup,
    demandes_rgpd,
    entreprises,
    etudiants,
    experiences,
    import_export,
    otp,
    promotions,
    questionnaires,
    rgpd,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="CRM Alumni API",
    description="API de gestion des étudiants, promotions, expériences et consentements RGPD",
    version="2.1.0",
)

app.include_router(promotions.router)
app.include_router(etudiants.router)
app.include_router(entreprises.router)
app.include_router(experiences.router)
app.include_router(certifications.router)
app.include_router(rgpd.router)
app.include_router(demandes_rgpd.alumni_router)
app.include_router(demandes_rgpd.admin_router)
app.include_router(admin.router)
app.include_router(cleanup.router)
app.include_router(import_export.router)
app.include_router(questionnaires.router)
app.include_router(questionnaires.admin_router)
app.include_router(otp.router)
app.include_router(admin_auth.router)


@app.on_event("startup")
def log_startup_config():
    from config import settings
    logger.info("=" * 60)
    logger.info("OTP_MODE actif : %s", settings.otp_mode)
    logger.info("=" * 60)


@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API de gestion du CRM Alumni !"}



from fastapi.middleware.cors import CORSMiddleware

# Configurer les origines autorisées
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Autorise GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # Autorise tous les headers (comme X-API-Key)
)