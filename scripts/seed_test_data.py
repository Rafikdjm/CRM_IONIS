#!/usr/bin/env python3
"""Jeu de donnees de test pour l'application Alumni CRM.

Insertion DIRECTE en base (pas via l'API ni l'import Excel) pour alimenter
le dashboard admin, l'annuaire, les filtres, les fiches alumni et les
indicateurs avec un volume realiste :
  - 4 promotions (2022 -> 2025)
  - 50 etudiants identifies par le domaine email @test-seed.local
  - experiences pro (poste courant + historique), entreprises partagees/uniques
  - consentements RGPD (4 types, mix actif/refuse)
  - questionnaire annuel actif + questions (text/choice/boolean/rating,
    tags KPI, questions conditionnees au statut d'emploi)
  - reponses partielles (~65%) pour tester le taux de completion

Usage :
    python scripts/seed_test_data.py            # generation (refuse si des
                                                # donnees seed existent deja)
    python scripts/seed_test_data.py --clean    # purge des SEULES donnees seed
                                                # puis regeneration

Securite : aucune donnee reelle n'est modifiee ni supprimee. Les suppressions
du mode --clean sont strictement limitees aux lignes marquees :
  - ETUDIANT.email se terminant par @test-seed.local
  - PROMOTION.nom_promotion contenant '[seed]'
  - QUESTIONNAIRE.description contenant '[seed:test-seed.local]'
  - ENTREPRISE referencee UNIQUEMENT par des experiences d'etudiants seed
"""

import argparse
import datetime
import json
import random
import sys
import unicodedata
from pathlib import Path

# ---------------------------------------------------------------------------
# Connexion : reutilise la configuration du backend (.env / variables d'env).
# ---------------------------------------------------------------------------
API_ROOT = Path(__file__).resolve().parent.parent / "alumni_crm_api"

try:
    from dotenv import load_dotenv

    load_dotenv(API_ROOT / ".env")
except ImportError:
    pass  # config.py lit alors les vraies variables d'environnement

sys.path.insert(0, str(API_ROOT))

import pg8000.dbapi  # noqa: E402

from config import settings  # noqa: E402

TEST_DOMAIN = "test-seed.local"
SEED_PROMO_MARKER = "[seed]"
SEED_QUESTIONNAIRE_MARKER = "[seed:test-seed.local]"
NB_ETUDIANTS = 50

rng = random.Random(20260823)  # graine fixe -> jeu de donnees reproducible

# ---------------------------------------------------------------------------
# Donnees de reference (alignees sur l'application)
# ---------------------------------------------------------------------------

SECTORS = [
    'Technologie', 'Informatique', 'Finance', 'Santé', 'Éducation',
    'Industrie', 'Commerce', 'Marketing', 'Juridique', 'Construction',
    'Transport', 'Énergie', 'Média', 'Agroalimentaire', 'Consulting',
    'Immobilier', 'Tourisme / Hôtellerie', 'Sport', 'Culture',
    'Public / Administration', 'Association / ONG', 'Recherche', 'Assurance',
    'Arts / Design', 'Environnement', 'Logistique', 'Hôtellerie / Restauration',
    'Automobile', 'Aéronautique / Spatial', 'Telecom', 'Banque', 'BTP',
    'Audiovisuel / Cinéma', 'Commerce de détail', 'Secteur public',
    'Freelance / Entrepreneur', 'Autre',
]

PRENOMS = [
    "Alice", "Julien", "Camille", "Thomas", "Léa", "Nicolas", "Emma", "Hugo",
    "Chloé", "Maxime", "Sarah", "Antoine", "Manon", "Lucas", "Clara",
    "Romain", "Justine", "Pierre", "Inès", "Guillaume", "Anaïs", "Victor",
    "Charlotte", "Baptiste", "Zoé", "Théo", "Margaux", "Adrien", "Pauline",
    "Étienne", "Louise", "Damien", "Céline", "François", "Aurélie",
    "Vincent", "Élise", "Mathieu", "Noémie", "Alexandre",
]

NOMS = [
    "Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit",
    "Durand", "Leroy", "Moreau", "Simon", "Laurent", "Lefebvre", "Michel",
    "Garcia", "David", "Bertrand", "Roux", "Vincent", "Fournier", "Morel",
    "Girard", "André", "Mercier", "Blanc", "Guerin", "Boyer", "Rousseau",
    "Chevalier", "Gauthier", "Perrin", "Morin", "Marchand", "Fontaine",
    "Perrot", "Lambert", "Maillard", "Renard", "Dupont", "Bonnet",
]

SKILLS_POOL = [
    "Python", "SQL", "JavaScript", "React", "Node.js", "Excel", "Power BI",
    "Tableau", "Communication", "Gestion de projet", "SEO", "SEA",
    "Photoshop", "Figma", "Comptabilité", "Contrôle de gestion",
    "Droit des sociétés",
    "Recrutement", "Salesforce", "Docker", "AWS", "Machine Learning",
    "Rédaction web", "Négociation",
]

PARCOURS_POOL = [
    "Bac+2 Biotechnologies", "Licence MIASHS", "BTS SIO", "Prépa PCSI/PC",
    "Licence Économie-Gestion", "BUT Techniques de Commercialisation",
    "Licence Droit", "BTS Communication", "Licence AES",
    "Classe préparatoire ECG", "BUT GEA", "Licence STAPS",
    "Master 1 Management", "BTS MCO", "Licence Information-Communication",
]

VILLES_FR = [
    ("Paris", "France"), ("Lyon", "France"), ("Bordeaux", "France"),
    ("Toulouse", "France"), ("Nantes", "France"), ("Lille", "France"),
    ("Marseille", "France"), ("Rennes", "France"), ("Strasbourg", "France"),
    ("Nice", "France"), ("Montpellier", "France"),
    ("Bruxelles", "Belgique"), ("Genève", "Suisse"),
    ("Montréal", "Canada"), ("Luxembourg", "Luxembourg"),
]

ENTREPRISES_PARTAGEES = [
    ("NovaSys", "Technologie", "Paris"), ("DataSphere", "Informatique", "Lyon"),
    ("Meridian Finance", "Banque", "Paris"), ("Helios Santé", "Santé", "Nantes"),
    ("Atelier Vert", "Environnement", "Bordeaux"),
    ("Kairos Consulting", "Consulting", "Paris"),
    ("Oriel Immobilier", "Immobilier", "Lille"),
    ("Solaris Énergie", "Énergie", "Toulouse"),
    ("Lumen Média", "Média", "Paris"), ("Vecteur Logistique", "Logistique", "Rouen"),
    ("Altis Assurance", "Assurance", "Strasbourg"),
    ("Brume Studio", "Arts / Design", "Montpellier"),
    ("Cortex Retail", "Commerce de détail", "Marseille"),
    ("Nordwind Aéro", "Aéronautique / Spatial", "Toulouse"),
]

ENTREPRISES_UNIQUES = [
    ("Papillon Tourisme", "Tourisme / Hôtellerie", "Nice"),
    ("Forge & Béton", "BTP", "Grenoble"),
    ("Studio Kinéo", "Audiovisuel / Cinéma", "Paris"),
    ("Verdis Agro", "Agroalimentaire", "Angers"),
    ("Lexica Avocats", "Juridique", "Paris"),
    ("Orbite Telecom", "Telecom", "Rennes"),
    ("Sel & Braise", "Hôtellerie / Restauration", "Lyon"),
    ("Cime Auto", "Automobile", "Mulhouse"),
]

ROLES_PAR_SECTEUR = {
    "Technologie": ["Développeur Back End", "Ingénieur DevOps", "Product Manager"],
    "Informatique": ["Développeur Full Stack", "Analyste cybersécurité", "Administrateur systèmes"],
    "Finance": ["Analyste financier", "Chargé de clientèle", "Contrôleur de gestion"],
    "Banque": ["Conseiller bancaire", "Analyste crédit"],
    "Santé": ["Chargé de projet e-santé", "Responsable qualité"],
    "Marketing": ["Chargé de marketing digital", "Traffic Manager"],
    "Consulting": ["Consultant junior", "Analyste conseil"],
    "Environnement": ["Chargé de mission RSE", "Analyste énergie"],
    "Média": ["Journaliste web", "Community Manager"],
    "Logistique": ["Coordinateur logistique", "Responsable exploitation"],
    "Immobilier": ["Chargé d'investissement", "Gestionnaire locatif"],
    "Assurance": ["Souscripteur", "Gestionnaire sinistres"],
    "Aéronautique / Spatial": ["Ingénieur méthodes", "Acheteur industriel"],
}
ROLES_GENERIQUES = ["Chargé de projet", "Assistant chef de produit",
                    "Coordinateur opérationnel", "Analyste"]

CONTRATS = ["CDI", "CDD", "Stage", "Alternance", "Freelance"]
POIDS_CONTRATS_PREMIER = [15, 15, 35, 30, 5]     # stage/alternance dominants
POIDS_CONTRATS_SUIVANT = [55, 20, 0, 10, 15]     # CDI dominant

STATUTS_DISPONIBILITE = [("en_poste", 60), ("en_recherche", 25), ("a_lecoute", 15)]

TYPES_CONSENTEMENT = [
    ("prise_de_contact", 85),
    ("partage_donnees", 70),
    ("enquetes", 75),
    ("newsletter", 55),
]
CANAUX_CONSENTEMENT = ["plateforme", "email", "papier"]


def slug(texte: str) -> str:
    """Equivalent simplifie de normalize_academic_slug (minuscule, sans accent)."""
    nfkd = unicodedata.normalize("NFD", texte.lower())
    return "".join(c for c in nfkd if unicodedata.category(c) != "Mn")


def choisir_pondere(paires):
    total = sum(poids for _, poids in paires)
    tirage = rng.uniform(0, total)
    cumul = 0
    for valeur, poids in paires:
        cumul += poids
        if tirage <= cumul:
            return valeur
    return paires[-1][0]


def connecter():
    return pg8000.dbapi.connect(
        host=settings.db_host,
        database=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
        port=settings.db_port,
    )


# ---------------------------------------------------------------------------
# Purge des donnees de seed uniquement (--clean)
# ---------------------------------------------------------------------------

def purger_seed(cur) -> dict:
    supprimes = {}
    cur.execute(
        """DELETE FROM REPONSE_QUESTIONNAIRE r USING QUESTIONNAIRE q
           WHERE r.id_questionnaire = q.id_questionnaire
             AND q.description LIKE %s""",
        (f"%{SEED_QUESTIONNAIRE_MARKER}%",),
    )
    supprimes["reponses (questionnaire seed)"] = cur.rowcount
    cur.execute(
        "DELETE FROM REPONSE_QUESTIONNAIRE WHERE id_etudiant IN "
        "(SELECT id_etudiant FROM ETUDIANT WHERE email LIKE %s)",
        (f"%@{TEST_DOMAIN}",),
    )
    supprimes["reponses (etudiants seed)"] = cur.rowcount
    cur.execute(
        "DELETE FROM CONSENTEMENT_RGPD WHERE id_etudiant IN "
        "(SELECT id_etudiant FROM ETUDIANT WHERE email LIKE %s)",
        (f"%@{TEST_DOMAIN}",),
    )
    supprimes["consentements"] = cur.rowcount
    # Capture des entreprises touchees par le seed AVANT de perdre les
    # references (les experiences vont etre supprimees ci-dessous).
    cur.execute(
        """CREATE TEMP TABLE tmp_seed_entreprises AS
           SELECT DISTINCT x.id_entreprise FROM EXPERIENCE_PRO x
           JOIN ETUDIANT s ON s.id_etudiant = x.id_etudiant
           WHERE s.email LIKE %s""",
        (f"%@{TEST_DOMAIN}",),
    )
    cur.execute(
        "DELETE FROM EXPERIENCE_PRO WHERE id_etudiant IN "
        "(SELECT id_etudiant FROM ETUDIANT WHERE email LIKE %s)",
        (f"%@{TEST_DOMAIN}",),
    )
    supprimes["experiences"] = cur.rowcount
    cur.execute(
        "DELETE FROM ETUDIANT WHERE email LIKE %s",
        (f"%@{TEST_DOMAIN}",),
    )
    supprimes["etudiants"] = cur.rowcount
    # Entreprises devenues orphelines (plus aucune experience, tous profils).
    cur.execute(
        """DELETE FROM ENTREPRISE e
           WHERE e.id_entreprise IN (SELECT id_entreprise FROM tmp_seed_entreprises)
           AND NOT EXISTS (SELECT 1 FROM EXPERIENCE_PRO x
                           WHERE x.id_entreprise = e.id_entreprise)"""
    )
    supprimes["entreprises (orphelines seed)"] = cur.rowcount
    cur.execute("DROP TABLE tmp_seed_entreprises")
    cur.execute(
        "DELETE FROM QUESTIONNAIRE WHERE description LIKE %s",
        (f"%{SEED_QUESTIONNAIRE_MARKER}%",),
    )
    supprimes["questionnaires (+questions en cascade)"] = cur.rowcount
    cur.execute(
        "DELETE FROM PROMOTION WHERE nom_promotion LIKE %s",
        (f"%{SEED_PROMO_MARKER}%",),
    )
    supprimes["promotions"] = cur.rowcount
    return supprimes


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------

def creer_promotions(cur) -> list:
    promotions = []
    for i, (annee, filiere) in enumerate([
        (2022, "Data & Intelligence Artificielle"),
        (2023, "Cybersécurité"),
        (2024, "Marketing Digital"),
        (2025, "Finance d'Entreprise"),
    ]):
        cur.execute(
            """INSERT INTO PROMOTION (nom_promotion, annee_diplome, filiere)
               VALUES (%s, %s, %s) RETURNING id_promotion""",
            (f"Promo {annee} - {filiere} {SEED_PROMO_MARKER}", annee, filiere),
        )
        promotions.append({"id": cur.fetchone()[0], "annee": annee,
                           "nom": f"Promo {annee} - {filiere}"})
    return promotions


def creer_etudiants(cur, promotions) -> list:
    etudiants = []
    effectifs = [14, 13, 12, NB_ETUDIANTS - 39]  # 14/13/12/11 sur 4 promos
    repartition = []
    for promo, n in zip(promotions, effectifs):
        repartition.extend([promo] * n)

    paires_utilisees = set()
    for i, promo in enumerate(repartition):
        while True:
            paire = (PRENOMS[rng.randrange(len(PRENOMS))],
                     NOMS[rng.randrange(len(NOMS))])
            if paire not in paires_utilisees:
                paires_utilisees.add(paire)
                break
        prenom, nom = paire
        slug_p, slug_n = slug(prenom), slug(nom)
        email = f"{slug_p}.{slug_n}@{TEST_DOMAIN}"
        email_academique = f"{slug_p}.{slug_n}@{settings.academic_email_domain}"

        annee_diplome = promo["annee"]
        duree_etudes = rng.choice([2, 3])
        date_inscription = datetime.date(
            annee_diplome - duree_etudes, 9, rng.randint(1, 28))
        date_naissance = datetime.date(
            annee_diplome - 22 - rng.randint(0, 3),
            rng.randint(1, 12), rng.randint(1, 28))
        telephone = "06 " + " ".join(
            f"{rng.randint(0, 99):02d}" for _ in range(4))
        parcours = rng.choice(PARCOURS_POOL)
        statut = choisir_pondere(STATUTS_DISPONIBILITE)

        # ~15% de profils incomplets pour tester l'affichage admin.
        profil_incomplet = rng.random() < 0.15
        ville, pays = ("", "") if profil_incomplet else rng.choice(VILLES_FR)
        linkedin = "" if profil_incomplet else \
            f"https://www.linkedin.com/in/{slug_p}-{slug_n}-{rng.randint(100, 999)}"
        address = "" if profil_incomplet and rng.random() < 0.5 \
            else f"{rng.randint(1, 120)} rue {rng.choice(['Victor Hugo', 'de la Paix', 'des Lilas', 'Nationale'])}"
        competences = [] if rng.random() < 0.10 else rng.sample(SKILLS_POOL, rng.randint(2, 5))

        cur.execute(
            """INSERT INTO ETUDIANT (nom, prenom, email, email_academique, telephone,
                   date_naissance, parcours_anterieur, date_inscription, id_promotion,
                   address, city, country, linkedin, availability_status, skills)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
               RETURNING id_etudiant""",
            (nom, prenom, email, email_academique, telephone,
             date_naissance, parcours, date_inscription, promo["id"],
             address, ville, pays, linkedin, statut,
             json.dumps(competences)),
        )
        etudiants.append({
            "id": cur.fetchone()[0], "prenom": prenom, "nom": nom,
            "promo": promo, "statut": statut,
            "date_inscription": date_inscription, "annee_diplome": annee_diplome,
            "ville": ville, "pays": pays,
        })
    return etudiants


def creer_entreprises(cur) -> tuple:
    """Retourne ({nom: id}, liste_ids_uniques_non_attribues)."""
    ids_par_nom = {}
    for nom, secteur, ville in ENTREPRISES_PARTAGEES + ENTREPRISES_UNIQUES:
        cur.execute(
            """INSERT INTO ENTREPRISE (nom_entreprise, secteur_activite, pays, ville)
               VALUES (%s,%s,%s,%s) RETURNING id_entreprise""",
            (nom, secteur, "France", ville),
        )
        ids_par_nom[nom] = cur.fetchone()[0]
    return ids_par_nom


def _periodes_experiences(etu) -> list:
    """Construit 1 a 3 periodes d'emploi chronologiques et coherentes."""
    diplome = datetime.date(etu["annee_diplome"], 6, 30)
    aujourd_hui = datetime.date.today()
    en_recherche = etu["statut"] == "en_recherche"
    periodes = []

    def duree_mois(debut, mois):
        mois_total = debut.month - 1 + mois
        return datetime.date(debut.year + mois_total // 12, mois_total % 12 + 1, 1)

    if en_recherche:
        # Derniere experience terminee recemment, pas de poste courant.
        debut = diplome + datetime.timedelta(days=rng.randint(0, 120))
        fin = min(aujourd_hui - datetime.timedelta(days=rng.randint(15, 180)), aujourd_hui)
        if fin <= debut:
            fin = min(debut + datetime.timedelta(days=200), aujourd_hui)
        periodes.append({"debut": debut, "fin": fin, "actuel": False})
        if rng.random() < 0.5:  # une experience anterieure chez quelqu'un d'autre
            prec_fin = debut - datetime.timedelta(days=rng.randint(15, 90))
            prec_debut = max(duree_mois(prec_fin, -rng.randint(8, 18)),
                             datetime.date(etu["annee_diplome"], 1, 1))
            if prec_debut < prec_fin:
                periodes.insert(0, {"debut": prec_debut, "fin": prec_fin, "actuel": False})
    else:
        nb_anciennes = rng.choices([0, 1, 2], weights=[55, 30, 15])[0]
        curseur = diplome + datetime.timedelta(days=rng.randint(-120, 150))  # stage possible avant diplome
        curseur = min(curseur, aujourd_hui)
        for _ in range(nb_anciennes):
            fin = min(duree_mois(curseur, rng.randint(8, 24)), aujourd_hui)
            if fin <= curseur:
                break
            periodes.append({"debut": curseur, "fin": fin, "actuel": False})
            curseur = fin + datetime.timedelta(days=rng.randint(0, 90))
            if curseur >= aujourd_hui:
                break
        if curseur < aujourd_hui:
            periodes.append({"debut": curseur, "fin": None, "actuel": True})
        if not any(p["actuel"] for p in periodes):
            # Securite : un alumni non "en recherche" garde un poste courant.
            periodes.append({
                "debut": max(diplome, aujourd_hui - datetime.timedelta(days=90)),
                "fin": None, "actuel": True})

    return periodes


def creer_experiences(cur, etudiants, entreprise_ids) -> int:
    noms_partages = [n for n, _, _ in ENTREPRISES_PARTAGEES]
    total = 0
    for etu in etudiants:
        periodes = _periodes_experiences(etu)
        for idx, periode in enumerate(periodes):
            premiere = idx == 0
            contrat = rng.choices(
                CONTRATS,
                POIDS_CONTRATS_PREMIER if premiere else POIDS_CONTRATS_SUIVANT)[0]
            if premiere and contrat in ("Stage", "Alternance"):
                debut = min(periode["debut"],
                            datetime.date(etu["annee_diplome"], rng.choice([3, 5]), 1))
            else:
                debut = periode["debut"]
            # Entreprises partagees surtout pour le poste courant.
            if periode["actuel"] or rng.random() < 0.7:
                nom_ent = rng.choice(noms_partages)
            else:
                nom_ent = rng.choice([n for n, _, _ in ENTREPRISES_UNIQUES])
            secteur = dict((n, s) for n, s, _ in
                           ENTREPRISES_PARTAGEES + ENTREPRISES_UNIQUES)[nom_ent]
            role = rng.choice(ROLES_PAR_SECTEUR.get(secteur, ROLES_GENERIQUES))
            # Salaire annuel renseigne sur ~60% des postes courants uniquement.
            salary_annuel = 0
            if periode["actuel"] and rng.random() < 0.60:
                base = rng.choice(range(30000, 68000, 500))
                salary_annuel = base if contrat == "CDI" \
                    else int(base * 0.75 / 500 + 0.5) * 500
            cur.execute(
                """INSERT INTO EXPERIENCE_PRO
                   (intitule_poste, type_contrat, date_debut, date_fin, salaire,
                    salary_annuel, poste_actuel, id_entreprise, id_etudiant)
                   VALUES (%s,%s,%s,%s,0,%s,%s,%s,%s)""",
                (role, contrat, debut, periode["fin"], salary_annuel,
                 periode["actuel"], entreprise_ids[nom_ent], etu["id"]),
            )
            total += 1
    return total


def creer_consentements(cur, etudiants) -> dict:
    compteurs = {}
    for etu in etudiants:
        for type_c, probabilite_actif in TYPES_CONSENTEMENT:
            statut = "actif" if rng.random() * 100 < probabilite_actif else "refuse"
            date_c = etu["date_inscription"] + datetime.timedelta(days=rng.randint(0, 14))
            cur.execute(
                """INSERT INTO CONSENTEMENT_RGPD
                   (date_consentement, type_consentement, statut, canal, id_etudiant)
                   VALUES (%s,%s,%s,%s,%s)
                   ON CONFLICT (id_etudiant, type_consentement) DO NOTHING""",
                (date_c, type_c, statut, rng.choice(CANAUX_CONSENTEMENT), etu["id"]),
            )
            cle = (type_c, statut)
            compteurs[cle] = compteurs.get(cle, 0) + 1
    return compteurs


QUESTIONS = [
    {"texte": "Quel module de votre formation vous sert le plus au quotidien ?",
     "type": "text", "options": [], "tag": None, "cond": False},
    {"texte": "Par quel canal principal avez-vous obtenu votre premier emploi ?",
     "type": "choice",
     "options": ["Plateforme emploi de l'école", "Candidature spontanée",
                 "Réseau alumni", "LinkedIn / réseaux sociaux", "Autre"],
     "tag": None, "cond": False},
    {"texte": "Recommanderiez-vous votre formation à un proche ?",
     "type": "boolean", "options": [], "tag": None, "cond": False},
    {"texte": "Évaluez l'adéquation entre la formation et votre poste actuel (1 = faible, 5 = excellente)",
     "type": "rating", "options": [], "tag": "adequation_formation_emploi", "cond": True},
    {"texte": "Votre poste actuel relève-t-il du domaine visé par vos études ?",
     "type": "choice",
     "options": ["Oui, totalement", "Partiellement", "Non"],
     "tag": "adequation_formation_emploi", "cond": True},
    {"texte": "Quelles compétences aimeriez-vous renforcer dans les 2 prochaines années ?",
     "type": "text", "options": [], "tag": None, "cond": False},
    {"texte": "Seriez-vous prêt à intervenir auprès des étudiants (témoignage, mentorat) ?",
     "type": "boolean", "options": [], "tag": "engagement_reseau", "cond": False},
]


def creer_questionnaire(cur) -> int:
    cur.execute("SELECT COUNT(*) FROM QUESTIONNAIRE WHERE actif = TRUE")
    autre_actif = cur.fetchone()
    if autre_actif and autre_actif[0] > 0:
        print("ATTENTION : un autre questionnaire actif existe deja en base "
              "(non touche). Le questionnaire seed sera lui aussi actif.")
    cur.execute(
        """INSERT INTO QUESTIONNAIRE (titre, description, actif)
           VALUES (%s,%s,TRUE) RETURNING id_questionnaire""",
        ("Enquête d'insertion professionnelle 2026",
         f"Questionnaire annuel genere pour tests {SEED_QUESTIONNAIRE_MARKER}"),
    )
    idq = cur.fetchone()[0]
    for ordre, q in enumerate(QUESTIONS, start=1):
        cur.execute(
            """INSERT INTO QUESTION
               (id_questionnaire, texte, type, options, ordre, tag,
                conditionnee_statut_emploi)
               VALUES (%s,%s,%s,%s::jsonb,%s,%s,%s)""",
            (idq, q["texte"], q["type"], json.dumps(q["options"]), ordre,
             q["tag"], q["cond"]),
        )
    return idq


REPONSES_TEXTE = [
    "Le projet de groupe en dernière année.", "Les cours de data visualisation.",
    "La gestion de projet agile.", "Le module de négociation.",
    "Les stages en entreprise.", "Le droit appliqué.",
    "La communication écrite professionnelle.", "Les ateliers techniques.",
]
COMPETENCES_A_RENFORCER = [
    "Le management d'équipe.", "L'anglais technique.",
    "La data science avancée.", "La vente complexe.",
    "La finance d'entreprise.", "Le pilotage budgétaire.",
]


def creer_reponses(cur, etudiants, id_questionnaire) -> int:
    cibles = rng.sample(etudiants, k=int(NB_ETUDIANTS * 0.65))
    # Recuperation des questions avec leur definition pour respecter
    # type / tag / conditionnement.
    cur.execute(
        """SELECT id_question, type, options, texte, conditionnee_statut_emploi
           FROM QUESTION WHERE id_questionnaire = %s ORDER BY ordre""",
        (id_questionnaire,),
    )
    questions = cur.fetchall()
    nb_reponses = 0
    for etu in cibles:
        a_un_poste = etu["statut"] in ("en_poste", "a_lecoute")
        reponses = {}
        for id_q, type_q, options, texte_q, cond in questions:
            if cond and not a_un_poste:
                continue  # question conditionnee : non posee
            if rng.random() > 0.92:
                continue  # trou realiste (~8% de non-reponse ponctuelle)
            if type_q == "text":
                pool = COMPETENCES_A_RENFORCER if "renforcer" in texte_q \
                    else REPONSES_TEXTE
                reponses[str(id_q)] = rng.choice(pool)
            elif type_q == "choice":
                reponses[str(id_q)] = rng.choice(options)
            elif type_q == "boolean":
                reponses[str(id_q)] = rng.random() < 0.65
            elif type_q == "rating":
                reponses[str(id_q)] = rng.choice([2, 3, 4, 4, 5, 5, 5])
        cur.execute(
            """INSERT INTO REPONSE_QUESTIONNAIRE
               (id_etudiant, id_questionnaire, reponses)
               VALUES (%s,%s,%s::jsonb)
               ON CONFLICT (id_etudiant, id_questionnaire) DO NOTHING""",
            (etu["id"], id_questionnaire, json.dumps(reponses)),
        )
        nb_reponses += 1
    return nb_reponses


# ---------------------------------------------------------------------------
# Resume console
# ---------------------------------------------------------------------------

def afficher_resume(cur, promotions, etudiants, nb_experiences):
    print("\n" + "=" * 62)
    print("RESUME DU SEED")
    print("=" * 62)

    print("\nEtudiants par promotion :")
    for promo in promotions:
        n = sum(1 for e in etudiants if e["promo"]["id"] == promo["id"])
        print(f"  {promo['nom']:<48} {n:>3}")

    print("\nEtudiants par statut de disponibilite :")
    for statut in ("en_poste", "en_recherche", "a_lecoute"):
        n = sum(1 for e in etudiants if e["statut"] == statut)
        print(f"  {statut:<48} {n:>3}")

    cur.execute("""SELECT COUNT(*) FROM EXPERIENCE_PRO x
                   JOIN ETUDIANT s ON s.id_etudiant = x.id_etudiant
                   WHERE s.email LIKE %s""", (f"%@{TEST_DOMAIN}",))
    print(f"\nExperiences inserees                        : {cur.fetchone()[0]:>3}")
    cur.execute("""SELECT COUNT(*) FROM ENTREPRISE e
                   WHERE EXISTS (SELECT 1 FROM EXPERIENCE_PRO x
                                 JOIN ETUDIANT s ON s.id_etudiant = x.id_etudiant
                                 WHERE x.id_entreprise = e.id_entreprise
                                   AND s.email LIKE %s)""",
                (f"%@{TEST_DOMAIN}",))
    print(f"Entreprises utilisees par le seed           : {cur.fetchone()[0]:>3}")
    print(f"(detail insertion                           : {nb_experiences:>3})")

    cur.execute("""SELECT COUNT(*) FROM REPONSE_QUESTIONNAIRE r
                   JOIN ETUDIANT s ON s.id_etudiant = r.id_etudiant
                   WHERE s.email LIKE %s""", (f"%@{TEST_DOMAIN}",))
    repondants = cur.fetchone()[0]
    taux = 100.0 * repondants / max(len(etudiants), 1)
    print(f"Taux de reponse au questionnaire            : {repondants:>3}/{len(etudiants)} ({taux:.0f}%)")

    print("\nConsentements par type :")
    cur.execute("""SELECT type_consentement,
                          SUM(CASE WHEN statut='actif' THEN 1 ELSE 0 END),
                          SUM(CASE WHEN statut='refuse' THEN 1 ELSE 0 END)
                   FROM CONSENTEMENT_RGPD c
                   JOIN ETUDIANT s ON s.id_etudiant = c.id_etudiant
                   WHERE s.email LIKE %s
                   GROUP BY type_consentement ORDER BY type_consentement""",
                (f"%@{TEST_DOMAIN}",))
    for type_c, actifs, refuses in cur.fetchall():
        print(f"  {type_c:<20} actif={actifs:>3}  refuse={refuses:>3}")

    print("\nProfils incomplets (ville/pays/linkedin vides) :",
          sum(1 for e in etudiants if not e["ville"] and not e["pays"]))
    print("=" * 62)


# ---------------------------------------------------------------------------
# Programme principal
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--clean", action="store_true",
                        help="purge les donnees seed existantes avant regeneration")
    args = parser.parse_args()

    conn = connecter()
    try:
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM ETUDIANT WHERE email LIKE %s",
                    (f"%@{TEST_DOMAIN}",))
        existants = cur.fetchone()[0]
        if existants and not args.clean:
            print(f"ABANDON : {existants} etudiant(s) seed existent deja "
                  f"(domaine @{TEST_DOMAIN}).")
            print("Relancez avec --clean pour les purger puis regenerer.")
            sys.exit(1)

        if args.clean:
            supprimes = purger_seed(cur)
            print("Purge des donnees seed :")
            for table, n in supprimes.items():
                print(f"  {table:<38} {n:>4} supprime(s)")

        print("\nGeneration en cours...")
        promotions = creer_promotions(cur)
        etudiants = creer_etudiants(cur, promotions)
        entreprise_ids = creer_entreprises(cur)
        nb_exp = creer_experiences(cur, etudiants, entreprise_ids)
        creer_consentements(cur, etudiants)
        id_questionnaire = creer_questionnaire(cur)
        nb_repondants = creer_reponses(cur, etudiants, id_questionnaire)

        conn.commit()
        print(f"OK : {len(promotions)} promotions, {len(etudiants)} etudiants, "
              f"{nb_exp} experiences, {nb_repondants} repondants au questionnaire.")

        afficher_resume(cur, promotions, etudiants, nb_exp)
        print(f"\nNettoyage ulterieur : relancez ce script avec --clean, ou :")
        print(f"  DELETE FROM ETUDIANT WHERE email LIKE '%@{TEST_DOMAIN}';")

    except Exception:
        conn.rollback()
        print("ERREUR : transaction annulee (rollback complet), base inchangee.")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
