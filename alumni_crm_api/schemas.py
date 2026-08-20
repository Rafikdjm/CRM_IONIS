from datetime import date, datetime
from typing import Any, Generic, List, Literal, Optional, TypeVar

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

T = TypeVar("T")


# ==========================================
# SCHÉMAS DE PAGINATION
# ==========================================
class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    skip: int
    limit: int
    has_next: bool


class CleanupReport(BaseModel):
    action: str
    rows_affected: int
    details: Optional[str] = None
    timestamp: datetime


# ==========================================
# 1. SCHÉMAS POUR LA TABLE PROMOTION
# ==========================================
class PromotionBase(BaseModel):
    nom_promotion: str
    annee_diplome: int = Field(ge=1950, le=2100)
    filiere: str


class PromotionCreate(PromotionBase):
    pass


class Promotion(PromotionBase):
    id_promotion: int
    nb_etudiants: int = 0

    class Config:
        from_attributes = True


# ==========================================
# 2. SCHÉMAS POUR LA TABLE ETUDIANT
# ==========================================
def _valider_date_naissance(value: date) -> date:
    """Cohérence de la date de naissance : pas de date future, âge réaliste."""
    if value > date.today():
        raise ValueError("La date de naissance ne peut pas être dans le futur.")
    age_approx = (date.today() - value).days / 365.25
    if age_approx > 100:
        raise ValueError("La date de naissance indique un âge manifestement absurde (> 100 ans).")
    return value


def _valider_dates_coherence(date_inscription: date, date_naissance: date) -> None:
    if date_inscription < date_naissance:
        raise ValueError("date_inscription ne peut pas être antérieure à date_naissance.")


class EtudiantBase(BaseModel):
    nom: str
    prenom: str
    email: EmailStr
    email_academique: Optional[EmailStr] = None
    telephone: str
    date_naissance: date
    parcours_anterieur: str
    date_inscription: date
    id_promotion: int
    address: Optional[str] = ""
    city: Optional[str] = ""
    country: Optional[str] = ""
    linkedin: Optional[str] = ""
    availability_status: Optional[str] = ""
    skills: Optional[list[str]] = Field(default_factory=list)


class EtudiantCreate(EtudiantBase):
    @field_validator("date_naissance")
    @classmethod
    def _check_date_naissance(cls, value: date) -> date:
        return _valider_date_naissance(value)

    @model_validator(mode="after")
    def _check_dates_coherence(self):
        _valider_dates_coherence(self.date_inscription, self.date_naissance)
        return self


class EtudiantUpdate(BaseModel):
    """Schéma pour mise à jour partielle : tous les champs sont optionnels."""
    nom: Optional[str] = None
    prenom: Optional[str] = None
    email: Optional[EmailStr] = None
    email_academique: Optional[EmailStr] = None
    telephone: Optional[str] = None
    date_naissance: Optional[date] = None
    parcours_anterieur: Optional[str] = None
    date_inscription: Optional[date] = None
    id_promotion: Optional[int] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    linkedin: Optional[str] = None
    availability_status: Optional[str] = None
    skills: Optional[list[str]] = None

    @field_validator("date_naissance")
    @classmethod
    def _check_date_naissance(cls, value: date) -> date:
        return _valider_date_naissance(value)

    @model_validator(mode="after")
    def _check_dates_coherence(self):
        fournis = self.model_fields_set
        if "date_inscription" in fournis and "date_naissance" in fournis:
            _valider_dates_coherence(self.date_inscription, self.date_naissance)
        return self


class Etudiant(EtudiantBase):
    id_etudiant: int

    class Config:
        from_attributes = True


class EtudiantDetail(Etudiant):
    promotion_nom: Optional[str] = None
    entreprise_actuelle: Optional[str] = None
    secteur_activite: Optional[str] = None  # dérivé de ENTREPRISE via expérience courante
    experiences_count: int = 0
    date_anonymisation: Optional[datetime] = None  # non nulle si compte anonymisé (RGPD)


# ==========================================
# 3. SCHÉMAS POUR LA TABLE CERTIFICATION
# ==========================================
class CertificationBase(BaseModel):
    nom_certification: str
    organisme: str


class CertificationCreate(CertificationBase):
    pass


class Certification(CertificationBase):
    id_certification: int

    class Config:
        from_attributes = True


# ==========================================
# 4. SCHÉMAS POUR LA TABLE D'ASSOCIATION OBTIENT
# ==========================================
def _valider_date_obtention(value: date) -> date:
    """Borne raisonnable sur date_obtention : pas de date future ni
    antérieure à 1950 (même convention que annee_diplome)."""
    if value < date(1950, 1, 1):
        raise ValueError("La date d'obtention ne peut pas être antérieure à 1950.")
    if value > date.today():
        raise ValueError("La date d'obtention ne peut pas être dans le futur.")
    return value


class ObtientBase(BaseModel):
    id_etudiant: int
    id_certification: int
    date_obtention: date


class ObtientCreate(ObtientBase):
    @field_validator("date_obtention")
    @classmethod
    def _check_date_obtention(cls, value: date) -> date:
        return _valider_date_obtention(value)


# ==========================================
# 5. SCHÉMAS POUR LA TABLE ENTREPRISE
# ==========================================
class EntrepriseBase(BaseModel):
    nom_entreprise: str
    secteur_activite: str
    pays: str
    ville: str


class EntrepriseCreate(EntrepriseBase):
    pass


class Entreprise(EntrepriseBase):
    id_entreprise: int

    class Config:
        from_attributes = True


# ==========================================
# 6. SCHÉMAS POUR LA TABLE EXPERIENCE_PRO
# ==========================================
class ExperienceProBase(BaseModel):
    intitule_poste: str
    type_contrat: str
    date_debut: date
    date_fin: Optional[date] = None
    salaire: float = Field(ge=0)
    salary_annuel: Optional[float] = Field(default=0, ge=0)
    poste_actuel: bool
    id_entreprise: int
    id_etudiant: int


class ExperienceProCreate(ExperienceProBase):
    @model_validator(mode="after")
    def _check_dates_poste(self):
        if self.poste_actuel and self.date_fin is not None:
            raise ValueError("Une expérience actuelle (poste_actuel=true) ne peut pas avoir de date_fin.")
        if self.date_fin is not None and self.date_fin < self.date_debut:
            raise ValueError("date_fin ne peut pas être antérieure à date_debut.")
        return self


class ExperiencePro(ExperienceProBase):
    id_experience: int

    class Config:
        from_attributes = True


class NouvelleExperience(BaseModel):
    intitule_poste: str
    type_contrat: str
    date_debut: date
    date_fin: Optional[date] = None
    salaire: float = Field(ge=0)
    salary_annuel: Optional[float] = Field(default=0, ge=0)
    nom_entreprise: str
    secteur_activite: Optional[str] = ""
    poste_actuel: bool = True
    pays: Optional[str] = ""
    ville: Optional[str] = ""

    @model_validator(mode="after")
    def _check_dates_poste(self):
        if self.poste_actuel and self.date_fin is not None:
            raise ValueError("Une expérience actuelle (poste_actuel=true) ne peut pas avoir de date_fin.")
        if self.date_fin is not None and self.date_fin < self.date_debut:
            raise ValueError("date_fin ne peut pas être antérieure à date_debut.")
        return self


class CertificationAlumniCreate(BaseModel):
    nom: str
    organisme: str = ""
    date_obtention: Optional[date] = None

    @field_validator("date_obtention")
    @classmethod
    def _check_date_obtention(cls, value: Optional[date]) -> Optional[date]:
        if value is None:
            return value
        return _valider_date_obtention(value)


# ==========================================
# 7. SCHÉMAS POUR LA TABLE CONSENTEMENT_RGPD
# ==========================================
# Valeurs de statut réellement utilisées par le code (admin.py:78,
# cleanup.py:37/159/381) : 'actif' / 'refuse'. Le Literal est volontairement
# restreint à cette convention stricte ; les lectures ne passent pas par ce
# schéma (dicts bruts), une éventuelle valeur historique hors liste ne casse
# donc aucune lecture existante.
class ConsentementRgpdBase(BaseModel):
    date_consentement: date
    type_consentement: str
    statut: Literal["actif", "refuse"]
    canal: str
    id_etudiant: int


class ConsentementRgpdCreate(ConsentementRgpdBase):
    pass


class ConsentementRgpd(ConsentementRgpdBase):
    id_consentement: int

    class Config:
        from_attributes = True


# ==========================================
# 8. SCHÉMAS POUR LES DEMANDES RGPD
# ==========================================
class DemandeRgpdCreate(BaseModel):
    type_demande: str = Field(..., pattern="^(export|suppression)$")


class DemandeRgpd(BaseModel):
    id_demande: int
    id_etudiant: Optional[int] = None
    type_demande: str
    statut: str
    date_demande: Optional[datetime] = None
    date_prise_en_charge: Optional[datetime] = None
    date_traitement: Optional[datetime] = None
    prise_en_charge_par: Optional[str] = None
    traitee_par: Optional[str] = None
    motif_refus: Optional[str] = None
    nom_complet: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True


class DemandeRgpdTraiter(BaseModel):
    decision: str = Field(..., pattern="^(traitee|rejetee)$")
    motif_refus: Optional[str] = None
    traitee_par: Optional[str] = None


class DemandeRgpdPriseEnCharge(BaseModel):
    """Body de la route admin « prendre en charge » : seul le nom de l'admin
    (acteur, pour traçabilité) est requis, il n'y a pas encore de décision."""
    traitee_par: Optional[str] = None


# ==========================================
# 8. SCHÉMAS POUR LE NETTOYAGE / AUDIT
# ==========================================
class OrphanReport(BaseModel):
    table_name: str
    orphan_count: int
    sample_ids: List[int]


class DuplicateGroup(BaseModel):
    duplicate_key: str
    count: int
    ids: List[int]


class CleanupDryRun(BaseModel):
    orphans: List[OrphanReport]
    duplicates: List[DuplicateGroup]
    rgpd_pending_archive: int
    total_rows_at_risk: int


# ==========================================
# 9. SCHEMAS POUR LE QUESTIONNAIRE ANNUEL
# ==========================================
# Types réellement gérés par le frontend (AdminQuestionnaires.jsx et
# AlumniSurvey.jsx) : 'text', 'choice', 'boolean', 'rating'.
class QuestionCreate(BaseModel):
    id_question: Optional[int] = None
    texte: str
    type: Literal["text", "choice", "boolean", "rating"] = "text"
    options: Optional[list] = []
    ordre: int = 0
    tag: Optional[str] = None
    conditionnee_statut_emploi: bool = False

    @model_validator(mode="after")
    def _check_options(self):
        if self.type == "choice" and not self.options:
            raise ValueError("Une question de type 'choice' doit avoir au moins une option.")
        return self


class Question(BaseModel):
    id_question: int
    id_questionnaire: int
    texte: str
    type: str
    options: Optional[list] = []
    ordre: int
    tag: Optional[str] = None
    conditionnee_statut_emploi: bool = False

    class Config:
        from_attributes = True


class QuestionnaireCreate(BaseModel):
    titre: str
    description: str = ""
    questions: Optional[List[QuestionCreate]] = []


class Questionnaire(BaseModel):
    id_questionnaire: int
    titre: str
    description: str
    date_creation: Optional[date] = None
    actif: bool = True
    nb_questions: int = 0
    tags: list = []

    class Config:
        from_attributes = True


class QuestionnaireDetail(Questionnaire):
    questions: List[Question] = []


class ReponseCreate(BaseModel):
    reponses: dict


class Reponse(BaseModel):
    id_reponse: int
    id_etudiant: int
    id_questionnaire: int
    reponses: dict
    date_reponse: Optional[datetime] = None

    class Config:
        from_attributes = True
