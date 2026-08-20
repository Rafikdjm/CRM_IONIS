SELECT 
    e.id_etudiant,
    e.nom AS nom_etudiant,
    e.prenom AS prenom_etudiant,
    e.email_academique,
    p.nom_promotion,
    p.filiere,
    exp.intitule_poste,
    exp.type_contrat,
    ent.nom_entreprise,
    ent.ville AS ville_entreprise
FROM ETUDIANT e
INNER JOIN PROMOTION p ON e.id_promotion = p.id_promotion
LEFT JOIN EXPERIENCE_PRO exp ON e.id_etudiant = exp.id_etudiant
LEFT JOIN ENTREPRISE ent ON exp.id_entreprise = ent.id_entreprise;