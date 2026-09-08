"""
Jeu de données démo pour les captures d'écran du rapport.

Insère dans la base `alumni_crm` un jeu de données réaliste et riche :
13 nouveaux alumni (statuts variés), 4 nouvelles promotions, entreprises,
expériences, certifications, consentements RGPD, réponses au questionnaire
annuel et demandes RGPD.

Le script est idempotent : relancé, il supprime d'abord les données démo
qu'il a insérées précédemment (repérées par adresse e-mail), puis les
ré-insère. Les lignes d'origine (Rafik id 10, yacin3 id 476) sont laissées
intactes.

Usage :
    cd alumni_crm_api
    python seed_test_data.py
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_db_connection  # noqa: E402

# ---------------------------------------------------------------------------
# Données démo
# ---------------------------------------------------------------------------

PROMOS = [
    ("MSc ArtiA", 2026, "Intelligence Artificielle"),
    ("MSc Cybersécurité", 2025, "Cybersécurité"),
    ("MSc Data Engineering", 2023, "Informatique"),
    ("MSc Interaction", 2022, "Design"),
]

ENTREPRISES = [
    ("Google France", "Technologies", "France", "Paris"),
    ("Capgemini", "Conseil", "France", "Paris"),
    ("Sopra Steria", "Informatique", "France", "Lyon"),
    ("Thales", "Défense", "France", "Toulouse"),
    ("SAP", "Éditeur logiciel", "Allemagne", "Paris"),
    ("Microsoft France", "Technologies", "France", "Issy-les-Moulineaux"),
    ("Tesla", "Automobile", "France", "Paris"),
    ("TOTAL Energies", "Énergie", "France", "Courbevoie"),
    ("Airbus", "Aéronautique", "France", "Toulouse"),
    ("BNP Paribas", "Banque", "France", "Paris"),
    ("Dassault Systèmes", "Logiciels", "France", "Vélizy-Villacoublay"),
    ("Deezer", "Musique en ligne", "France", "Paris"),
    ("Décathlon", "Sport", "France", "Villeneuve-d'Ascq"),
    ("Sanofi", "Pharmacie", "France", "Paris"),
    ("Accenture", "Conseil", "France", "Paris"),
    ("OVHcloud", "Cloud", "France", "Roubaix"),
    ("Doctolib", "Santé", "France", "Paris"),
    ("Aixia", "Conseil", "France", "Lyon"),
    ("Alibaba Cloud", "Cloud", "Chine", "Shenzhen"),
    ("Schneider Electric", "Électronique", "France", "Rueil-Malmaison"),
    ("Safran", "Aéronautique", "France", "Paris"),
    ("Institut Pasteur", "Recherche", "France", "Paris"),
    ("AWS", "Cloud", "États-Unis", "Paris"),
]

# (nom, prenom, email, email_academique, tel, date_naissance, parcours,
#  date_inscription, promotion, adresse, ville, pays, linkedin, statut, skills)
ETUDIANTS = [
    ("Martin", "Léa", "lea.martin@gmail.com", "lea.martin@ionis-stm.com", "+33 6 12 34 56 78", "2000-03-15",
     "BTS SIO - Lycée Marcelin Berthelot", "2021-09-01", "MSc ArtiA", "12 rue de la Paix", "Paris", "France",
     "https://linkedin.com/in/leamartin", "en_poste", ["Python", "Machine Learning", "IA", "Data Science"]),
    ("Bernard", "Thomas", "thomas.bernard@gmail.com", "thomas.bernard@ionis-stm.com", "+33 6 98 76 54 32", "1999-07-22",
     "Licence MIASHS - Université Paris 1", "2020-09-01", "MSc Cybersécurité", "8 avenue des Champs", "Lyon", "France",
     "https://linkedin.com/in/thomasbernard", "en_poste", ["Cybersécurité", "Réseau", "Pentest"]),
    ("Petit", "Julie", "julie.petit@gmail.com", "julie.petit@ionis-stm.com", "+33 6 33 44 55 66", "1999-01-10",
     "BTS SIO - Lycée Ozanam", "2021-09-01", "MSc ArtiA", "25 bd Haussmann", "Paris", "France",
     "https://linkedin.com/in/juliepetit", "en_recherche", ["IA", "Deep Learning", "TensorFlow", "Python"]),
    ("Dubois", "Nicolas", "nicolas.dubois@gmail.com", "nicolas.dubois@ionis-stm.com", "+33 6 55 44 33 22", "1998-11-05",
     "DUT Informatique - IUT de Lille", "2019-09-01", "MSc Data Engineering", "3 rue Nationale", "Lille", "France",
     "https://linkedin.com/in/nicolasdubois", "en_poste", ["SQL", "Spark", "Hadoop", "Airflow", "Python"]),
    ("Moreau", "Emma", "emma.moreau@gmail.com", "emma.moreau@ionis-stm.com", "+33 6 22 11 00 99", "2000-05-30",
     "Bac S - Lycée Saint-Exupéry", "2021-09-01", "MSc Interaction", "18 place Bellecour", "Lyon", "France",
     "https://linkedin.com/in/emmaMoreau", "a_lecoute", ["UX Design", "Figma", "JavaScript"]),
    ("Lefebvre", "Hugo", "hugo.lefebvre@gmail.com", "hugo.lefebvre@ionis-stm.com", "+33 6 77 88 99 00", "1999-12-18",
     "Prépa PTSI - Lycée Carnot", "2020-09-01", "MSc Data Engineering", "4 rue du Général Leclerc", "Rennes", "France",
     "https://linkedin.com/in/hugolefebvre", "en_poste", ["Databricks", "Kafka", "Python", "dbt"]),
    ("Garcia", "Camille", "camille.garcia@gmail.com", "camille.garcia@ionis-stm.com", "+33 6 44 55 66 77", "2000-09-02",
     "BTS SIO - Lycée La Tournelle", "2021-09-01", "MSc Cybersécurité", "72 route de Genas", "Lyon", "France",
     "https://linkedin.com/in/camilleGarcia", "en_poste", ["SOC", "Forensique", "SIEM", "Powershell"]),
    ("Roux", "Antoine", "antoine.roux@gmail.com", "antoine.roux@ionis-stm.com", "+33 6 66 55 44 33", "1999-04-14",
     "Bac S - Lycée Montaigne", "2021-09-01", "MSc ArtiA", "9 rue de Bordeaux", "Bordeaux", "France",
     "https://linkedin.com/in/antoineroux", "en_recherche", ["Computer Vision", "PyTorch", "OpenCV"]),
    ("Fournier", "Chloé", "chloe.fournier@gmail.com", "chloe.fournier@ionis-stm.com", "+33 6 88 77 66 55", "2001-02-25",
     "DUT MMI - IUT de Bordeaux", "2022-09-01", "MSc Cybersécurité", "21 allée des Cybères", "Bordeaux", "France",
     "https://linkedin.com/in/chloefournier", "en_poste", ["Reverse Engineering", "C", "Malware Analysis"]),
    ("Girard", "Louis", "louis.girard@gmail.com", "louis.girard@ionis-stm.com", "+33 6 11 22 33 44", "2000-06-08",
     "Prépa MP - Lycée du Parc", "2021-09-01", "MSc ArtiA", "14 quai des Chartrons", "Bordeaux", "France",
     "https://linkedin.com/in/louisgirard", "en_formation", ["NLP", "Transformers", "HuggingFace"]),
    ("Lambert", "Manon", "manon.lambert@gmail.com", "manon.lambert@ionis-stm.com", "+33 6 99 88 77 66", "1999-08-19",
     "Bac ES - Lycée Descartes", "2020-09-01", "MSc Interaction", "6 rue de la République", "Lyon", "France",
     "https://linkedin.com/in/manonlambert", "en_poste", ["Produit", "Design System", "Accessibilité"]),
    ("Bonnet", "Nathan", "nathan.bonnet@gmail.com", "nathan.bonnet@ionis-stm.com", "+33 6 32 43 54 65", "1999-06-27",
     "DUT GEA - IUT de Nice", "2021-09-01", "MSc Data Engineering", "10 av de la Californie", "Nice", "France",
     "https://linkedin.com/in/nathanbonnet", "entrepreneur", ["Startup", "Data", "Business"]),
    ("Blanc", "Sarah", "sarah.blanc@gmail.com", "sarah.blanc@ionis-stm.com", "+33 6 12 98 76 54", "2000-10-11",
     "Bac S - Lycée Mermoz", "2021-09-01", "MSc Cybersécurité", "5 rue de la Paix", "Nice", "France",
     "https://linkedin.com/in/sarahblanc", "en_poste", ["Cloud", "DevSecOps", "Terraform", "AWS"]),
]

CERTIFICATIONS = [
    ("TOGAF 9.2 Foundation", "The Open Group"),
    ("Certified AWS Cloud Practitioner", "Amazon Web Services"),
    ("PMP - Project Management Professional", "PMI"),
    ("CISSP", "ISC2"),
    ("Google Analytics Certification", "Google"),
    ("SAFe Scrum Master", "Scaled Agile"),
    ("Microsoft Azure Fundamentals", "Microsoft"),
    ("CCNA Routing & Switching", "Cisco"),
]

# (email, entreprise, poste, contrat, debut, fin, salaire_annuel, actuel, salaire_mensuel)
EXPERIENCES = [
    ("lea.martin@gmail.com", "Google France", "Data Scientist", "CDI", "2024-02-01", None, 52000, True, 4333),
    ("lea.martin@gmail.com", "Décathlon", "Analyst Data (Alternance)", "Alternance", "2022-09-01", "2023-08-31", None, False, 2100),
    ("thomas.bernard@gmail.com", "Capgemini", "Consultant Cybersécurité", "CDI", "2023-10-01", None, 45000, True, 3750),
    ("thomas.bernard@gmail.com", "Sopra Steria", "Pentester (Stage)", "Stage", "2023-03-01", "2023-08-31", None, False, 1300),
    ("julie.petit@gmail.com", "Doctolib", "Data Scientist (En cours de recrutement)", "CDD", "2025-02-01", None, 48000, True, 4000),
    ("julie.petit@gmail.com", "Aixia", "Data Analyst (Stage)", "Stage", "2024-01-01", "2024-06-30", None, False, 1200),
    ("nicolas.dubois@gmail.com", "Deezer", "Ingénieur Data (CDI)", "CDI", "2023-06-15", None, 47000, True, 3917),
    ("nicolas.dubois@gmail.com", "Thales", "Data Engineer (Alternance)", "Alternance", "2021-09-01", "2023-05-31", None, False, 1700),
    ("emma.moreau@gmail.com", "OVHcloud", "UX Designer (CDI)", "CDI", "2024-01-10", None, 41000, True, 3417),
    ("emma.moreau@gmail.com", "Microsoft France", "UI Designer (Stage)", "Stage", "2023-06-01", "2023-11-30", None, False, 1400),
    ("hugo.lefebvre@gmail.com", "Airbus", "Data Engineer (CDI)", "CDI", "2023-09-01", None, 48000, True, 4000),
    ("hugo.lefebvre@gmail.com", "Microsoft France", "BI Consultant (Alternance)", "Alternance", "2022-09-01", "2023-08-31", None, False, 1800),
    ("camille.garcia@gmail.com", "Schneider Electric", "Analyste SOC (CDI)", "CDI", "2024-03-01", None, 43000, True, 3583),
    ("camille.garcia@gmail.com", "SAP", "Analyste SOC (Stage)", "Stage", "2023-02-01", "2023-07-31", None, False, 1250),
    ("antoine.roux@gmail.com", "TOTAL Energies", "Ingénieur Vision (CDD)", "CDD", "2025-03-01", None, 46000, True, 3833),
    ("antoine.roux@gmail.com", "Décathlon", "Data Scientist (Stage)", "Stage", "2024-02-01", "2024-07-31", None, False, 1300),
    ("chloe.fournier@gmail.com", "Microsoft France", "Malware Analyst (CDI)", "CDI", "2024-06-01", None, 49000, True, 4083),
    ("chloe.fournier@gmail.com", "Accenture", "Analyste RSSI (Stage)", "Stage", "2023-02-01", "2023-07-31", None, False, 1250),
    ("louis.girard@gmail.com", "Dassault Systèmes", "Ingénieur NLP (Alternance + CDI proposé)", "Alternance", "2023-09-01", None, None, True, 1600),
    ("louis.girard@gmail.com", "Capgemini", "Data Scientist (Alternance)", "Alternance", "2022-09-01", "2023-08-31", None, False, 1500),
    ("manon.lambert@gmail.com", "Safran", "Cheffe de Produit (CDI)", "CDI", "2023-11-15", None, 50000, True, 4167),
    ("manon.lambert@gmail.com", "Institut Pasteur", "Product Designer (Stage)", "Stage", "2023-02-01", "2023-07-31", None, False, 1350),
    ("nathan.bonnet@gmail.com", "Alibaba Cloud", "Analyste Fonctionnel Études (CDI)", "CDI", "2022-08-01", "2024-09-30", 40000, False, 3333),
    ("nathan.bonnet@gmail.com", "SAP", "Analyste Fonctionnel (Stage)", "Stage", "2023-02-01", "2023-07-31", None, False, 1250),
    ("sarah.blanc@gmail.com", "AWS", "Cloud Security Engineer", "CDI", "2024-04-01", None, 58000, True, 4833),
    ("sarah.blanc@gmail.com", "Thales", "DevSecOps (Alternance)", "Alternance", "2022-09-01", "2024-03-31", None, False, 2200),
]

# (email, certification, date_obtention)
OBTENTIONS = [
    ("lea.martin@gmail.com", "Google Analytics Certification", "2022-06-01"),
    ("lea.martin@gmail.com", "Certified AWS Cloud Practitioner", "2023-11-15"),
    ("thomas.bernard@gmail.com", "CISSP", "2024-07-12"),
    ("julie.petit@gmail.com", "TOGAF 9.2 Foundation", "2023-03-25"),
    ("nicolas.dubois@gmail.com", "CCNA Routing & Switching", "2023-08-20"),
    ("chloe.fournier@gmail.com", "Certified AWS Cloud Practitioner", "2023-10-05"),
    ("sarah.blanc@gmail.com", "Certified AWS Cloud Practitioner", "2023-06-10"),
    ("sarah.blanc@gmail.com", "Microsoft Azure Fundamentals", "2024-02-18"),
    ("manon.lambert@gmail.com", "SAFe Scrum Master", "2022-09-01"),
    ("hugo.lefebvre@gmail.com", "PMP - Project Management Professional", "2023-12-01"),
]

# (email, type, statut, date_demande, date_traitement, traitee_par, motif_refus)
DEMANDES_RGPD = [
    ("lea.martin@gmail.com", "export", "traitee", "2025-06-01 10:00:00", "2025-06-02 09:30:00", "admin", None),
    ("thomas.bernard@gmail.com", "export", "en_traitement", "2025-07-15 14:20:00", None, None, None),
    ("julie.petit@gmail.com", "suppression", "envoyee", "2025-08-05 08:45:00", None, None, None),
    ("camille.garcia@gmail.com", "export", "traitee", "2025-05-20 11:10:00", "2025-05-21 15:00:00", "admin", None),
    ("nicolas.dubois@gmail.com", "suppression", "rejetee", "2025-04-10 16:30:00", "2025-04-12 10:00:00", "admin",
     "Données requises pour l'enquête annuelle en cours"),
    ("sarah.blanc@gmail.com", "export", "en_traitement", "2025-08-10 09:15:00", None, None, None),
]

# Question 109 (statut) -> cleared condition pour les questions 110/111/114/117
# (email, dict {109..117})
REPONSES = [
    ("lea.martin@gmail.com", {"109": "En poste", "110": "Technologies / IA", "111": "Data Scientist", "112": "Oui",
                              "113": "5", "114": "45-55k\u20ac", "115": "5", "116": "Oui", "117": "1 - 2 ans"}),
    ("thomas.bernard@gmail.com", {"109": "En poste", "110": "Cybersécurité", "111": "Consultant Cybersécurité", "112": "Oui",
                                 "113": "4", "114": "35-45k\u20ac", "115": "4", "116": "Oui", "117": "1 - 2 ans"}),
    ("julie.petit@gmail.com", {"109": "En recherche d'emploi", "110": "Non applicable", "111": "Non applicable", "112": "Non",
                               "113": "3", "114": "Non applicable", "115": "3", "116": "Oui", "117": "Non applicable"}),
    ("nicolas.dubois@gmail.com", {"109": "En poste", "110": "Informatique / Data", "111": "Ingénieur Data", "112": "Oui",
                                 "113": "4", "114": "45-55k\u20ac", "115": "4", "116": "Non", "117": "1 - 2 ans"}),
    ("emma.moreau@gmail.com", {"109": "En poste", "110": "Design / Produit", "111": "UX Designer", "112": "Oui",
                              "113": "4", "114": "35-45k\u20ac", "115": "5", "116": "Oui", "117": "6 mois - 1 an"}),
    ("hugo.lefebvre@gmail.com", {"109": "En poste", "110": "Aéronautique", "111": "Data Engineer", "112": "Oui",
                                "113": "5", "114": "45-55k\u20ac", "115": "5", "116": "Oui", "117": "1 - 2 ans"}),
    ("camille.garcia@gmail.com", {"109": "En poste", "110": "Cybersécurité", "111": "Analyste SOC", "112": "Oui",
                                "113": "4", "114": "35-45k\u20ac", "115": "4", "116": "Oui", "117": "6 mois - 1 an"}),
    ("chloe.fournier@gmail.com", {"109": "En poste", "110": "Cybersécurité", "111": "Malware Analyst", "112": "Oui",
                                "113": "5", "114": "45-55k\u20ac", "115": "5", "116": "Oui", "117": "1 - 2 ans"}),
    ("sarah.blanc@gmail.com", {"109": "En poste", "110": "Cloud / Sécurité", "111": "Cloud Security Engineer", "112": "Oui",
                              "113": "5", "114": "+55k\u20ac", "115": "5", "116": "Oui", "117": "6 mois - 1 an"}),
]


def q(txt):
    """Échappe une chaîne pour une requête SQL (mode débogage)."""
    return "'" + txt.replace("'", "''") + "'"


def main():
    with get_db_connection() as conn:
        cur = conn.cursor()

        # --- Nettoyage des données démo précédentes (idempotence) ---
        demo_emails = [e[2] for e in ETUDIANTS]
        placeholders = ",".join(["%s"] * len(demo_emails))
        cur.execute(f"SELECT id_etudiant FROM etudiant WHERE email IN ({placeholders})", demo_emails)
        demo_ids = [r[0] for r in cur.fetchall()]
        id_placeholders = ",".join(["%s"] * len(demo_ids)) if demo_ids else "NULL"
        if demo_ids:
            for tbl, fk in [("consentement_rgpd", "id_etudiant"), ("experience_pro", "id_etudiant"),
                            ("obtient", "id_etudiant"), ("reponse_questionnaire", "id_etudiant"),
                            ("demande_rgpd", "id_etudiant")]:
                cur.execute(f"DELETE FROM {tbl} WHERE {fk} IN ({id_placeholders})", demo_ids)
            cur.execute(f"DELETE FROM etudiant WHERE id_etudiant IN ({id_placeholders})", demo_ids)
            print(f"anciennes données démo nettoyées ({len(demo_ids)} alumni)")

        # --- Promotions ---
        promo_ids = {}
        cur.execute("SELECT nom_promotion, id_promotion FROM promotion")
        existing = dict(cur.fetchall())
        for nom, annee, filiere in PROMOS:
            if nom in existing:
                promo_ids[nom] = existing[nom]
            else:
                cur.execute("INSERT INTO promotion (nom_promotion, annee_diplome, filiere) VALUES (%s,%s,%s) RETURNING id_promotion",
                            (nom, annee, filiere))
                promo_ids[nom] = cur.fetchone()[0]
        print("promotions OK")

        # --- Entreprises ---
        entra_ids = {}
        cur.execute("SELECT nom_entreprise, id_entreprise FROM entreprise")
        existing_ent = dict(cur.fetchall())
        for nom, secteur, pays, ville in ENTREPRISES:
            if nom in existing_ent:
                entra_ids[nom] = existing_ent[nom]
            else:
                cur.execute("INSERT INTO entreprise (nom_entreprise, secteur_activite, pays, ville) VALUES (%s,%s,%s,%s) RETURNING id_entreprise",
                            (nom, secteur, pays, ville))
                entra_ids[nom] = cur.fetchone()[0]
        print("entreprises OK")

        # --- Étudiants ---
        etu_ids = {}
        for (nom, prenom, email, email_ac, tel, naiss, parcours, insc, promo, adr, ville, pays, link, avail, skills) in ETUDIANTS:
            cur.execute("""INSERT INTO etudiant (nom, prenom, email, email_academique, telephone, date_naissance,
                parcours_anterieur, date_inscription, id_promotion, address, city, country, linkedin,
                availability_status, skills)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id_etudiant""",
                (nom, prenom, email, email_ac, tel, naiss, parcours, insc, promo_ids[promo], adr, ville, pays,
                 link, avail, json.dumps(skills)))
            eid = cur.fetchone()[0]
            etu_ids[email] = (eid, prenom, nom)
        print(f"étudiants OK ({len(ETUDIANTS)})")

        # --- Certifications ---
        cert_ids = {}
        cur.execute("SELECT nom_certification, id_certification FROM certification")
        existing_cert = dict(cur.fetchall())
        for nom, organisme in CERTIFICATIONS:
            if nom in existing_cert:
                cert_ids[nom] = existing_cert[nom]
            else:
                cur.execute("INSERT INTO certification (nom_certification, organisme) VALUES (%s,%s) RETURNING id_certification",
                            (nom, organisme))
                cert_ids[nom] = cur.fetchone()[0]
        for email, cert, date_obt in OBTENTIONS:
            cur.execute("INSERT INTO obtient (id_etudiant, id_certification, date_obtention) VALUES (%s,%s,%s)",
                        (etu_ids[email][0], cert_ids[cert], date_obt))
        print("certifications OK")

        # --- Expériences ---
        for (email, entreprise, poste, contrat, debut, fin, salaire_annuel, actuel, salaire_mensuel) in EXPERIENCES:
            cur.execute("""INSERT INTO experience_pro (intitule_poste, type_contrat, date_debut, date_fin, salaire,
                poste_actuel, id_entreprise, id_etudiant, salary_annuel)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (poste, contrat, debut, fin, salaire_mensuel, actuel, entra_ids[entreprise], etu_ids[email][0],
                 salaire_annuel))
        print("expériences OK")

        # --- Consentements RGPD (4 types par alumni) ---
        types = ["generale", "newsletter", "prise_de_contact", "enquetes", "partage_donnees"]
        for email, (eid, _, _) in etu_ids.items():
            for i, tc in enumerate(types):
                statut = "actif"
                if email == "julie.petit@gmail.com" and tc == "enquetes":
                    statut = "actif"  # Julie participe à l'enquête, mais en recherche -> "Non applicable"
                if email == "sarah.blanc@gmail.com" and tc == "partage_donnees":
                    statut = "refuse"
                cur.execute("""INSERT INTO consentement_rgpd (id_etudiant, date_consentement, type_consentement,
                    statut, canal) VALUES (%s,%s,%s,%s,%s)""",
                    (eid, "2025-09-01", tc, statut, "email"))
        print("consentements OK")

        # --- Réponses au questionnaire annuel (id 28) ---
        for email, reps in REPONSES:
            cur.execute("""INSERT INTO reponse_questionnaire (id_etudiant, id_questionnaire, reponses, date_reponse)
                VALUES (%s, 28, %s, NOW())""",
                (etu_ids[email][0], json.dumps(reps)))
        print("réponses OK")

        # --- Demandes RGPD ---
        for (email, tpe, statut, date_demande, date_traitement, traitee_par, motif) in DEMANDES_RGPD:
            cur.execute("""INSERT INTO demande_rgpd (id_etudiant, type_demande, statut, date_demande,
                date_traitement, traitee_par, motif_refus)
                VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                (etu_ids[email][0], tpe, statut, date_demande, date_traitement, traitee_par, motif))
        print("demandes RGPD OK")

        conn.commit()
        print("\nSEED TERMINÉ :", len(ETUDIANTS), "alumni,", len(PROMOS), "promotions,",
              len(ENTREPRISES), "entreprises,", len(EXPERIENCES), "expériences.",
              file=sys.stderr)


if __name__ == "__main__":
    main()