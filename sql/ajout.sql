-- ========================
-- AJOUT SYSTÈME PAIEMENT SIMPLE
-- ========================

-- Ajout des colonnes pour paiement (espèces uniquement pour l'instant)
ALTER TABLE vente ADD COLUMN IF NOT EXISTS montant_recu DECIMAL(10,2);
ALTER TABLE vente ADD COLUMN IF NOT EXISTS monnaie_rendue DECIMAL(10,2);
ALTER TABLE vente ADD COLUMN IF NOT EXISTS mode_paiement VARCHAR(20) DEFAULT 'ESPECES';