-- ============================================================================
-- MIGRATION : Déduplication des consentements + contrainte UNIQUE
-- But : garantir un seul consentement par (étudiant, type) pour permettre
--       l'UPSERT côté API (POST /consentements/ en ON CONFLICT DO UPDATE).
-- ============================================================================

-- 1. Supprimer les doublons en gardant le consentement le plus récent
--    pour chaque couple (id_etudiant, type_consentement).
DELETE FROM CONSENTEMENT_RGPD c
USING CONSENTEMENT_RGPD c2
WHERE c.id_consentement <> c2.id_consentement
  AND c.id_etudiant = c2.id_etudiant
  AND c.type_consentement = c2.type_consentement
  AND (c.date_consentement, c.id_consentement) < (c2.date_consentement, c2.id_consentement);

-- 2. Contrainte d'unicité pour l'UPSERT
ALTER TABLE CONSENTEMENT_RGPD
    ADD CONSTRAINT uq_consentement_etudiant_type UNIQUE (id_etudiant, type_consentement);
