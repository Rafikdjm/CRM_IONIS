-- ============================================================================
-- MIGRATION : Contrainte UNIQUE sur ETUDIANT.email_academique
-- ----------------------------------------------------------------------------
-- Garantit qu'aucun doublon silencieux d'email académique ne peut apparaître,
-- indépendamment de la génération automatique côté API (suffixes numeriques).
--
-- La contrainte peut déjà exister selon les environnements : le bloc DO n'ajoute
-- la contrainte que si elle est absente (PostgreSQL ne supporte pas
-- ALTER TABLE ... ADD CONSTRAINT IF NOT EXISTS).
-- ============================================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'etudiant_email_academique_key'
          AND conrelid = 'ETUDIANT'::regclass
    ) THEN
        ALTER TABLE ETUDIANT
            ADD CONSTRAINT etudiant_email_academique_key UNIQUE (email_academique);
    END IF;
END
$$;
