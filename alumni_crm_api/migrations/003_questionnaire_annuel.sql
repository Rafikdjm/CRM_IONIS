-- 003: Tables pour le questionnaire annuel

CREATE TABLE IF NOT EXISTS QUESTIONNAIRE (
    id_questionnaire SERIAL PRIMARY KEY,
    titre VARCHAR(255) NOT NULL,
    description TEXT DEFAULT '',
    date_creation DATE DEFAULT CURRENT_DATE,
    actif BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS QUESTION (
    id_question SERIAL PRIMARY KEY,
    id_questionnaire INT NOT NULL REFERENCES QUESTIONNAIRE(id_questionnaire) ON DELETE CASCADE,
    texte TEXT NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'text',
    options JSONB DEFAULT '[]',
    ordre INT NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS REPONSE_QUESTIONNAIRE (
    id_reponse SERIAL PRIMARY KEY,
    id_etudiant INT NOT NULL REFERENCES ETUDIANT(id_etudiant),
    id_questionnaire INT NOT NULL REFERENCES QUESTIONNAIRE(id_questionnaire),
    reponses JSONB NOT NULL DEFAULT '{}',
    date_reponse TIMESTAMP DEFAULT NOW(),
    UNIQUE(id_etudiant, id_questionnaire)
);

CREATE INDEX IF NOT EXISTS idx_question_questionnaire ON QUESTION(id_questionnaire);
CREATE INDEX IF NOT EXISTS idx_reponse_etudiant ON REPONSE_QUESTIONNAIRE(id_etudiant);
CREATE INDEX IF NOT EXISTS idx_reponse_questionnaire ON REPONSE_QUESTIONNAIRE(id_questionnaire);
