-- Migration 012 : Ajout du champ salary_annuel (numerique) a EXPERIENCE_PRO
-- Permet le calcul automatique du salaire moyen par filiere.
-- Le champ salaire (texte libre) est conserve pour retrocompatibilite.

ALTER TABLE EXPERIENCE_PRO
ADD COLUMN IF NOT EXISTS salary_annuel NUMERIC(10, 2) DEFAULT 0;

COMMENT ON COLUMN EXPERIENCE_PRO.salary_annuel IS 'Salaire annuel brut en euros (numerique). Utilise pour les calculs statistiques.';
