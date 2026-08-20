-- ============================================================================
-- MIGRATION : Purge définitive différée des comptes anonymisés (RGPD)
--
-- Contexte : les demandes de suppression de compte sont traitées par
-- anonymisation (valeurs ANONYMISE_*). Cette migration ajoute le socle
-- nécessaire à la purge définitive automatique des comptes anonymisés
-- depuis plus de PURGE_DELAY_MONTHS mois (6 mois par défaut).
--
--   1. Colonne ETUDIANT.date_anonymisation : date à laquelle le compte a
--      été anonymisé (point de départ du délai de purge).
--   2. FK REPONSE_QUESTIONNAIRE -> ETUDIANT repassée en ON DELETE CASCADE :
--      les réponses aux questionnaires sont des données personnelles, elles
--      doivent disparaître avec le compte (sinon la suppression échoue sur
--      la contrainte NO ACTION initiale).
--
-- Rappel des règles de suppression sur ETUDIANT après migration :
--   CASCADE  : EXPERIENCE_PRO, OBTIENT, CONSENTEMENT_RGPD,
--              REPONSE_QUESTIONNAIRE (données personnelles).
--   SET NULL : DEMANDE_RGPD (la demande reste pour l'historique juridique,
--              elle contient déjà un snapshot nom/email et perd sa FK).
--   Sans FK : AUDIT_LOG.
-- ============================================================================

-- 1. Date d'anonymisation sur ETUDIANT
ALTER TABLE ETUDIANT ADD COLUMN IF NOT EXISTS date_anonymisation TIMESTAMP DEFAULT NULL;

-- Semi-couvrant : seuls les comptes anonymisés portent la valeur, l'index
-- reste donc minuscule.
CREATE INDEX IF NOT EXISTS idx_etudiant_date_anonymisation
    ON ETUDIANT(date_anonymisation)
    WHERE date_anonymisation IS NOT NULL;

COMMENT ON COLUMN ETUDIANT.date_anonymisation IS
    'Date d''anonymisation RGPD du compte. NULL pour un compte actif. '
    'Sert de référence à la purge définitive différée (PURGE_DELAY_MONTHS).';

-- 2. FK REPONSE_QUESTIONNAIRE : NO ACTION -> CASCADE
ALTER TABLE REPONSE_QUESTIONNAIRE
    DROP CONSTRAINT IF EXISTS reponse_questionnaire_id_etudiant_fkey;

ALTER TABLE REPONSE_QUESTIONNAIRE
    ADD CONSTRAINT reponse_questionnaire_id_etudiant_fkey
    FOREIGN KEY (id_etudiant) REFERENCES ETUDIANT(id_etudiant) ON DELETE CASCADE;
