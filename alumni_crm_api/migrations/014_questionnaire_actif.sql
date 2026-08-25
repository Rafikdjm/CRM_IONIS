-- Migration 014 : Ajout de la colonne actif sur QUESTIONNAIRE
-- La colonne est utilisee par l'API (filtres, activation/desactivation) mais
-- n'avait pas ete formalisee dans les migrations initiales. Idempotente.

ALTER TABLE QUESTIONNAIRE
ADD COLUMN IF NOT EXISTS actif BOOLEAN NOT NULL DEFAULT TRUE;
