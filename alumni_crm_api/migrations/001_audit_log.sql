-- ============================================================================
-- MIGRATION : Ajout de la table AUDIT_LOG et colonne archived_at
-- Exécuter avant de lancer l'API avec le nouveau router cleanup
-- ============================================================================

-- Table d'audit pour tracer toutes les opérations de nettoyage
CREATE TABLE IF NOT EXISTS AUDIT_LOG (
    id_log SERIAL PRIMARY KEY,
    action VARCHAR(100) NOT NULL,
    details TEXT,
    rows_affected INT DEFAULT 0,
    executed_at TIMESTAMP DEFAULT NOW()
);

-- Index pour les requêtes fréquentes sur l'audit
CREATE INDEX IF NOT EXISTS idx_audit_log_action ON AUDIT_LOG(action);
CREATE INDEX IF NOT EXISTS idx_audit_log_executed_at ON AUDIT_LOG(executed_at DESC);

-- Commentaires pour documentation
COMMENT ON TABLE AUDIT_LOG IS 'Journal des opérations de nettoyage et maintenance de la base';
COMMENT ON COLUMN AUDIT_LOG.action IS 'Type d''opération (ex: SUPPR_ORPHELINE, ARCHIVAGE_RGPD)';
COMMENT ON COLUMN AUDIT_LOG.details IS 'Description textuelle de l''opération';
COMMENT ON COLUMN AUDIT_LOG.rows_affected IS 'Nombre de lignes affectées par l''opération';
