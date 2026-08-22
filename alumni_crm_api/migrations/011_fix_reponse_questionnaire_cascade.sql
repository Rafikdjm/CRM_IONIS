-- ============================================================================
-- MIGRATION : Correction drift FK REPONSE_QUESTIONNAIRE.id_etudiant
-- ----------------------------------------------------------------------------
-- Contexte : la migration 003 créait REPONSE_QUESTIONNAIRE.id_etudiant avec
-- une FK en NO ACTION (pas de ON DELETE). La base LIVE, elle, porte la FK en
-- ON DELETE CASCADE (appliquée au fil de l'eau via la 008). Une base
-- reconstruite depuis les migrations devait donc reproduire le même état.
--
-- Cette migration garantit l'état CASCADE de façon idempotente :
--   - si une FK REPONSE_QUESTIONNAIRE -> ETUDIANT en CASCADE existe déjà,
--     elle ne fait rien ;
--   - sinon elle supprime toute FK existante (quel que soit son nom) et la
--     recrée avec ON DELETE CASCADE.
--
-- La 003 n'est volontairement PAS modifiée (une migration déjà appliquée
-- ne doit jamais être éditée rétroactivement) : la correction passe par
-- une nouvelle migration.
-- ============================================================================

DO $$
DECLARE
    fk_nom TEXT;
BEGIN
    -- 1. Une FK en CASCADE existe déjà ?
    SELECT conname INTO fk_nom
    FROM pg_constraint
    WHERE conrelid = 'REPONSE_QUESTIONNAIRE'::regclass
      AND contype = 'f'
      AND confrelid = 'ETUDIANT'::regclass
      AND confdeltype = 'c'
    ORDER BY conname
    LIMIT 1;

    -- 2. Sinon : supprimer toutes les FK vers ETUDIANT et la recréer en CASCADE
    IF fk_nom IS NULL THEN
        FOR fk_nom IN
            SELECT conname
            FROM pg_constraint
            WHERE conrelid = 'REPONSE_QUESTIONNAIRE'::regclass
              AND contype = 'f'
              AND confrelid = 'ETUDIANT'::regclass
        LOOP
            EXECUTE format('ALTER TABLE REPONSE_QUESTIONNAIRE DROP CONSTRAINT %I;', fk_nom);
        END LOOP;

        ALTER TABLE REPONSE_QUESTIONNAIRE
            ADD CONSTRAINT reponse_questionnaire_id_etudiant_fkey
            FOREIGN KEY (id_etudiant) REFERENCES ETUDIANT(id_etudiant) ON DELETE CASCADE;
    END IF;
END
$$;
