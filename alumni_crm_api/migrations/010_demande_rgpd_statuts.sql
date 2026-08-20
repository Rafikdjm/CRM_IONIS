-- ============================================================================
-- MIGRATION : Workflow de statut des demandes RGPD
-- ----------------------------------------------------------------------------
-- Ancien cycle : en_attente -> traitee / rejetee (traitement direct)
-- Nouveau cycle :
--   envoyee        : statut initial, créé par l'alumni
--   en_traitement  : l'admin a pris la demande en charge (avant décision
--                    finale) — évite que deux admins traitent en parallèle
--   traitee        : décision finale positive (traitee_par = admin)
--   rejetee        : décision finale négative (traitee_par + motif_refus)
-- ============================================================================

-- 1. Faire migrer les anciennes demandes « en attente » vers « envoyee »
UPDATE DEMANDE_RGPD
SET statut = 'envoyee'
WHERE statut = 'en_attente';

-- 2. Nouveau cycle de statuts (remplace la contrainte existante)
ALTER TABLE DEMANDE_RGPD DROP CONSTRAINT IF EXISTS chk_demande_statut;
ALTER TABLE DEMANDE_RGPD ADD CONSTRAINT chk_demande_statut
    CHECK (statut IN ('envoyee', 'en_traitement', 'traitee', 'rejetee'));

-- 3. Nouveau statut par défaut à la création
ALTER TABLE DEMANDE_RGPD ALTER COLUMN statut SET DEFAULT 'envoyee';

-- 4. Traçabilité de la prise en charge (qui bloque la demande, à quel moment)
ALTER TABLE DEMANDE_RGPD ADD COLUMN IF NOT EXISTS prise_en_charge_par VARCHAR(255);
ALTER TABLE DEMANDE_RGPD ADD COLUMN IF NOT EXISTS date_prise_en_charge TIMESTAMP;

COMMENT ON COLUMN DEMANDE_RGPD.statut IS
    'Cycle : envoyee (créée par l''alumni) -> en_traitement (prise en charge admin) -> traitee / rejetee.';
COMMENT ON COLUMN DEMANDE_RGPD.prise_en_charge_par IS
    'Nom de l''administrateur ayant pris la demande en charge (verrou anti-traitement parallèle).';
COMMENT ON COLUMN DEMANDE_RGPD.date_prise_en_charge IS
    'Date/heure de prise en charge par un administrateur.';
