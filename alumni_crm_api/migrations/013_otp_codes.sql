-- Migration 013 : table otp_codes
-- Formalise dans le versionnage la table creee initialement hors migrations
-- (ancien create_otp_table.sql a la racine). Idempotente : sans effet sur les
-- bases ou la table existe deja.
CREATE TABLE IF NOT EXISTS otp_codes (
    id SERIAL PRIMARY KEY,
    email TEXT NOT NULL,
    code_hash TEXT NOT NULL,
    attempts INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    ip_address TEXT DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_otp_email ON otp_codes(email);
