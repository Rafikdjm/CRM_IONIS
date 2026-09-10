-- ============================================================================
-- MIGRATION 016 : Contraintes CHECK alignées code API <-> base de données
-- ----------------------------------------------------------------------------
-- Objectif (audit de cohérence) : les mêmes règles que celles validées côté
-- Pydantic sont désormais portées par la base, pour que le SQL direct (imports,
-- scripts, purge, home-made requêtes) ne puisse plus les contourner :
--   - CONSENTEMENT_RGPD.statut      -> 'actif' | 'refuse' (convention du code)
--   - EXPERIENCE_PRO.date_fin       -> >= date_debut (ou NULL)
--   - EXPERIENCE_PRO.poste_actuel   -> interdit avec date_fin renseignée
--   - EXPERIENCE_PRO.salaire        -> >= 0 (idem salary_annuel)
--   - QUESTION.type                 -> valeurs gérées par le frontend
--   - PROMOTION.annee_diplome       -> 1950..2100 (borne Pydantic)
--
-- Idempotente : chaque contrainte est créée avec un nom fixe et précédée d'un
-- DROP CONSTRAINT IF EXISTS. Sans effet sur une base déjà alignée.
-- ============================================================================

ALTER TABLE CONSENTEMENT_RGPD DROP CONSTRAINT IF EXISTS chk_consentement_statut;
ALTER TABLE CONSENTEMENT_RGPD ADD CONSTRAINT chk_consentement_statut
    CHECK (statut IN ('actif', 'refuse'));

ALTER TABLE EXPERIENCE_PRO DROP CONSTRAINT IF EXISTS chk_experience_dates;
ALTER TABLE EXPERIENCE_PRO ADD CONSTRAINT chk_experience_dates
    CHECK (date_fin IS NULL OR date_fin >= date_debut);

ALTER TABLE EXPERIENCE_PRO DROP CONSTRAINT IF EXISTS chk_experience_poste_actuel;
ALTER TABLE EXPERIENCE_PRO ADD CONSTRAINT chk_experience_poste_actuel
    CHECK (NOT (poste_actuel = TRUE AND date_fin IS NOT NULL));

ALTER TABLE EXPERIENCE_PRO DROP CONSTRAINT IF EXISTS chk_experience_salaire;
ALTER TABLE EXPERIENCE_PRO ADD CONSTRAINT chk_experience_salaire
    CHECK (salaire >= 0);

ALTER TABLE EXPERIENCE_PRO DROP CONSTRAINT IF EXISTS chk_experience_salaire_annuel;
ALTER TABLE EXPERIENCE_PRO ADD CONSTRAINT chk_experience_salaire_annuel
    CHECK (salary_annuel IS NULL OR salary_annuel >= 0);

ALTER TABLE QUESTION DROP CONSTRAINT IF EXISTS chk_question_type;
ALTER TABLE QUESTION ADD CONSTRAINT chk_question_type
    CHECK (type IN ('text', 'choice', 'boolean', 'rating', 'single_choice', 'dropdown'));

ALTER TABLE PROMOTION DROP CONSTRAINT IF EXISTS chk_promotion_annee;
ALTER TABLE PROMOTION ADD CONSTRAINT chk_promotion_annee
    CHECK (annee_diplome BETWEEN 1950 AND 2100);

COMMENT ON CONSTRAINT chk_consentement_statut ON CONSENTEMENT_RGPD IS
    'Statut consentement limité à la convention du code ('')actif''/''refuse'') : le filtre "prise_de_contact" de cleanup.py repose dessus.';
COMMENT ON CONSTRAINT chk_experience_dates ON EXPERIENCE_PRO IS
    'date_fin >= date_debut (ou NULL) — même règle que le validator Pydantic ExperienceProCreate.';
COMMENT ON CONSTRAINT chk_experience_poste_actuel ON EXPERIENCE_PRO IS
    'Impossible d''être "poste actuel" avec une date_fin renseignée (contradiction).';
COMMENT ON CONSTRAINT chk_experience_salaire ON EXPERIENCE_PRO IS
    'Salaire négatif interdit (ge=0 côté Pydantic).';
COMMENT ON CONSTRAINT chk_experience_salaire_annuel ON EXPERIENCE_PRO IS
    'Salaire annuel négatif interdit.';
COMMENT ON CONSTRAINT chk_question_type ON QUESTION IS
    'Types de question gérés par le frontend (AdminQuestionnaires.jsx / AlumniSurvey.jsx).';
COMMENT ON CONSTRAINT chk_promotion_annee ON PROMOTION IS
    'Année de diplôme bornée 1950-2100 (même contrainte que Pydantic).';