-- 006: Add conditionnee_statut_emploi column to QUESTION
-- Permet de marquer les questions qui ne doivent etre posees qu'aux alumni
-- ayant un poste (disponibilite autre que "en_recherche").

ALTER TABLE QUESTION
  ADD COLUMN IF NOT EXISTS conditionnee_statut_emploi BOOLEAN NOT NULL DEFAULT FALSE;