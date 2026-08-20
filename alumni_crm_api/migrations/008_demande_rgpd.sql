-- ============================================================================
-- MIGRATION : Table DEMANDE_RGPD (droit d'accès / droit à l'oubli) + acteur
-- But : traiter les demandes RGPD des alumni (export de données, suppression
--       de compte) avec une traçabilité complète dans AUDIT_LOG.
-- ============================================================================

-- 1. Table des demandes RGPD
CREATE TABLE IF NOT EXISTS DEMANDE_RGPD (
    id_demande       SERIAL PRIMARY KEY,
    id_etudiant      INT          REFERENCES ETUDIANT(id_etudiant) ON DELETE SET NULL,
    type_demande     VARCHAR(20)  NOT NULL,
    statut           VARCHAR(20)  NOT NULL DEFAULT 'en_attente',
    date_demande     TIMESTAMP    NOT NULL DEFAULT NOW(),
    date_traitement  TIMESTAMP,
    traitee_par      VARCHAR(255),
    motif_refus      TEXT,
    nom_complet      VARCHAR(255),
    email            VARCHAR(255),
    CONSTRAINT chk_demande_type   CHECK (type_demande IN ('export', 'suppression')),
    CONSTRAINT chk_demande_statut CHECK (statut IN ('en_attente', 'traitee', 'rejetee'))
);

CREATE INDEX IF NOT EXISTS idx_demande_rgpd_statut  ON DEMANDE_RGPD(statut);
CREATE INDEX IF NOT EXISTS idx_demande_rgpd_etudiant ON DEMANDE_RGPD(id_etudiant);
CREATE INDEX IF NOT EXISTS idx_demande_rgpd_date    ON DEMANDE_RGPD(date_demande DESC);

COMMENT ON TABLE DEMANDE_RGPD IS
    'Demandes RGPD des alumni : export de données (droit d''accès) et suppression de compte (droit à l''oubli).';
COMMENT ON COLUMN DEMANDE_RGPD.traitee_par IS
    'Nom de l''administrateur ayant réellement traité la demande (acteur). Reste NULL pour les exports auto-service (traitement automatique sans review admin).';
COMMENT ON COLUMN DEMANDE_RGPD.nom_complet IS
    'Snapshot du nom complet au moment de la demande, conservé même après anonymisation du compte.';

-- 2. Traçabilité : ajout du champ acteur dans le journal d'audit
ALTER TABLE AUDIT_LOG ADD COLUMN IF NOT EXISTS acteur VARCHAR(255) DEFAULT NULL;

COMMENT ON COLUMN AUDIT_LOG.acteur IS
    'Identité de l''acteur (admin:nom, alumni:<id>, system) à l''origine de l''opération.';
