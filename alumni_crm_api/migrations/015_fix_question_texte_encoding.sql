-- 015: Correction du texte des questions tronques (perte du premier caractere)
-- Bug : "Évaluer" affiche comme "valuer" — le texte en base est tronqué.
--
-- La cause probable est une insertion/admin avec perte du 1er octet multi-octet
-- (É = U+00C9 = 0xC3 0x89 en UTF-8). Le fix doit etre fait cote base :
-- corriger le texte exact dans la table QUESTION.
--
-- Exemples de corrections (adapter selon les donnees reelles) :
-- UPDATE QUESTION SET texte = 'Évaluer la qualité de la formation' WHERE texte = 'valuer la qualité de la formation';
-- UPDATE QUESTION SET texte = 'Évaluez votre parcours' WHERE texte = 'valuez votre parcours';

-- Garde-fou : afficher toute question dont le texte commence par une minuscule
-- (les labels de questionnaire devraient toujours commencer par une majuscule).
SELECT id_question, id_questionnaire, texte
FROM QUESTION
WHERE texte ~ '^[a-z]';
