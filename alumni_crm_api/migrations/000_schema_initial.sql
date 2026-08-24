-- ============================================================================
-- MIGRATION 000 : Schéma initial (bootstrap)
-- ----------------------------------------------------------------------------
-- Contexte : les migrations 001+ font évoluer un schéma qui, historiquement,
-- n'était créé par AUCUN fichier versionné (tables métier créées avant la mise
-- en place du système de migrations). Un rejeu sur base vide échouait dès la
-- 002 (« relation etudiant n'existe pas »).
--
-- Cette migration reconstruit l'état INITIAL des 7 tables métier de base,
-- c'est-à-dire l'état final (cf. docs/erd_alumni_crm.mmd) MOINS ce que les
-- migrations suivantes ajoutent :
--   - ETUDIANT          : sans address/city/country/linkedin/availability_status/
--                         skills (002), sans date_anonymisation (008),
--                         email_academique SANS contrainte UNIQUE (010)
--   - CONSENTEMENT_RGPD : sans UNIQUE (id_etudiant, type_consentement) (006)
--   - EXPERIENCE_PRO    : sans salary_annuel (012)
--   - AUDIT_LOG (001), QUESTIONNAIRE/QUESTION/REPONSE_QUESTIONNAIRE (003),
--     DEMANDE_RGPD (007), otp_codes (013) sont créés par leurs migrations.
--
-- Idempotente (CREATE TABLE IF NOT EXISTS partout) : sur une base existante
-- déjà à jour, elle ne modifie rien et se contente d'être enregistrée dans
-- schema_migrations.
-- ============================================================================

CREATE TABLE IF NOT EXISTS PROMOTION (
    id_promotion   SERIAL PRIMARY KEY,
    nom_promotion  VARCHAR(100) NOT NULL,
    annee_diplome  INT          NOT NULL,
    filiere        VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS ETUDIANT (
    id_etudiant       SERIAL PRIMARY KEY,
    nom               VARCHAR(100) NOT NULL,
    prenom            VARCHAR(100) NOT NULL,
    email             VARCHAR(150) NOT NULL,
    email_academique  VARCHAR(150),
    telephone         VARCHAR(20)  NOT NULL,
    date_naissance    DATE         NOT NULL,
    parcours_anterieur TEXT        NOT NULL,
    date_inscription  DATE         NOT NULL,
    id_promotion      INT          NOT NULL REFERENCES PROMOTION(id_promotion) ON DELETE CASCADE,
    CONSTRAINT etudiant_email_key UNIQUE (email)
);

CREATE TABLE IF NOT EXISTS ENTREPRISE (
    id_entreprise    SERIAL PRIMARY KEY,
    nom_entreprise   VARCHAR(150) NOT NULL,
    secteur_activite VARCHAR(150) NOT NULL,
    pays             VARCHAR(100) NOT NULL,
    ville            VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS EXPERIENCE_PRO (
    id_experience   SERIAL PRIMARY KEY,
    id_etudiant     INT          NOT NULL REFERENCES ETUDIANT(id_etudiant) ON DELETE CASCADE,
    id_entreprise   INT          NOT NULL REFERENCES ENTREPRISE(id_entreprise) ON DELETE CASCADE,
    intitule_poste  VARCHAR(150) NOT NULL,
    type_contrat    VARCHAR(50)  NOT NULL,
    date_debut      DATE         NOT NULL,
    date_fin        DATE,
    salaire         NUMERIC      NOT NULL,
    poste_actuel    BOOLEAN      DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS CERTIFICATION (
    id_certification  SERIAL PRIMARY KEY,
    nom_certification VARCHAR(150) NOT NULL,
    organisme         VARCHAR(150) NOT NULL
);

CREATE TABLE IF NOT EXISTS OBTIENT (
    id_etudiant       INT NOT NULL REFERENCES ETUDIANT(id_etudiant) ON DELETE CASCADE,
    id_certification  INT NOT NULL REFERENCES CERTIFICATION(id_certification) ON DELETE CASCADE,
    date_obtention    DATE NOT NULL,
    PRIMARY KEY (id_etudiant, id_certification)
);

CREATE TABLE IF NOT EXISTS CONSENTEMENT_RGPD (
    id_consentement   SERIAL PRIMARY KEY,
    id_etudiant       INT NOT NULL REFERENCES ETUDIANT(id_etudiant) ON DELETE CASCADE,
    date_consentement DATE NOT NULL,
    type_consentement VARCHAR(100) NOT NULL,
    statut            VARCHAR(50)  NOT NULL,
    canal             VARCHAR(50)  NOT NULL
);
