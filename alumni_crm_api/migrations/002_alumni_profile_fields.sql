-- ============================================================================
-- MIGRATION : Ajout des colonnes de profil alumni (adresse, ville, pays,
-- linkedin, secteur d'activité, statut de disponibilité, compétences)
-- ============================================================================

-- Colonnes textuelles pour le profil
ALTER TABLE ETUDIANT ADD COLUMN IF NOT EXISTS address VARCHAR(255) DEFAULT '';
ALTER TABLE ETUDIANT ADD COLUMN IF NOT EXISTS city VARCHAR(100) DEFAULT '';
ALTER TABLE ETUDIANT ADD COLUMN IF NOT EXISTS country VARCHAR(100) DEFAULT '';
ALTER TABLE ETUDIANT ADD COLUMN IF NOT EXISTS linkedin VARCHAR(255) DEFAULT '';

-- Statut de disponibilité : en_poste | a_lecoute | en_recherche
ALTER TABLE ETUDIANT ADD COLUMN IF NOT EXISTS availability_status VARCHAR(50) DEFAULT '';

-- Compétences (tableau de chaînes en JSONB pour requêtes flexibles)
ALTER TABLE ETUDIANT ADD COLUMN IF NOT EXISTS skills JSONB DEFAULT '[]'::jsonb;

-- Index pour filtrage par statut (recherches admin fréquentes)
-- NOTE: secteur_activite est sur ENTREPRISE (dérivé via JOIN), pas sur ETUDIANT
CREATE INDEX IF NOT EXISTS idx_etudiant_availability ON ETUDIANT(availability_status);

-- Commentaires
COMMENT ON COLUMN ETUDIANT.address IS 'Adresse postale complète de l''alumni';
COMMENT ON COLUMN ETUDIANT.city IS 'Ville de résidence';
COMMENT ON COLUMN ETUDIANT.country IS 'Pays de résidence';
COMMENT ON COLUMN ETUDIANT.linkedin IS 'URL du profil LinkedIn';
COMMENT ON COLUMN ETUDIANT.availability_status IS 'Disponibilité : en_poste, a_lecoute, en_recherche';
COMMENT ON COLUMN ETUDIANT.skills IS 'Liste de compétences au format JSONB (ex: ["Python","Marketing"])';
