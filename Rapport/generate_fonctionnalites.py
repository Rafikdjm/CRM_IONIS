# -*- coding: utf-8 -*-
import os
import generate_reports
from generate_reports import ReportPDF

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def generate_fonctionnalites():
    pdf = ReportPDF("Fonctionnalites")
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_font("SegoeUI", "B", 20)
    pdf.set_text_color(30, 64, 175)
    pdf.cell(0, 12, "Cartographie des Fonctionnalites - Alumni CRM", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("SegoeUI", "", 10)
    pdf.set_text_color(107, 114, 128)
    pdf.cell(0, 7, "Vue d'ensemble des fonctionnalites de l'application, cote administration et cote alumni.", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(8)

    # Authentification
    pdf.chapter_title("1", "Authentification")
    pdf.bullet("Connexion par email vers un code OTP, verifie cote backend.")
    pdf.bullet("Espaces separes : admin (JWT admin) et alumni (JWT alumni).")
    pdf.bullet("Inscription alumni en 3 sections (infos personnelles / parcours academique / reseaux sociaux) avec stepper de progression et validation a la volee.")

    # Espace Admin
    pdf.chapter_title("2", "Espace ADMINISTRATION - /admin")
    pdf.body_text("Menu : Dashboard, Annuaire, Promotions, Import/Export, Questionnaires, Demandes RGPD")
    pdf.section_title("2.1 Dashboard")
    pdf.bullet("KPI cards : Total Alumni actifs, Taux d'emploi 6 mois, Taux d'emploi global, Taux de completion.")
    pdf.bullet("Indicateurs d'enquete generes depuis les tags KPI des questions actives.")
    pdf.bullet("Graphiques : donut des secteurs, barres des promotions (avec maturite des cohortes), jauge salaire moyen, barres des types de contrat.")
    pdf.bullet("Endpoints : GET /admin/indicateurs, /secteurs, /kpi-tags, /types-contrat.")
    pdf.section_title("2.2 Annuaire")
    pdf.bullet("Recherche et filtres : promotion, secteur, entreprise, disponibilite, contact autorise, statut du compte, competence.")
    pdf.bullet("Tri sur les colonnes.")
    pdf.bullet("Actions : Modifier (modal complet), Anonymiser (RGPD), Supprimer definitivement (doublons/erreurs), Voir le detail.")
    pdf.section_title("2.3 Promotions (CRUD complet)")
    pdf.bullet("Ajouter / Modifier / Supprimer une promotion.")
    pdf.bullet("Suppression en cascade avec avertissement irreverssible si la promotion contient des etudiants.")
    pdf.section_title("2.4 Import / Export")
    pdf.bullet("Upload Excel/CSV d'une liste d'admis avec drag & drop, apercu des 10 premieres lignes, coloration des en-tetes, compte rendu d'import.")
    pdf.bullet("Telecharger le modele et Exporter les donnees.")
    pdf.section_title("2.5 Questionnaires")
    pdf.bullet("Creer / Modifier / Activer - Desactiver / Supprimer un questionnaire annuel.")
    pdf.bullet("Editeur de questions : texte, choix multiple, oui/non, note 1-5, tag KPI optionnel, conditionnement au statut d'emploi.")
    pdf.bullet("Consulter les reponses des alumni.")
    pdf.section_title("2.6 Demandes RGPD")
    pdf.bullet("Suivi des demandes (export / suppression) avec filtres.")
    pdf.bullet("Workflow : Prendre en charge, Traiter / Rejeter, actions groupees.")
    pdf.bullet("Purge des demandes cloturees et purge definitive des comptes anonymises (delai 6 mois).")

    # Espace Alumni
    pdf.chapter_title("3", "Espace ALUMNI - /alumni")
    pdf.body_text("Menu : Mon Profil, Mon Parcours, RGPD & Consentement, Enquete annuelle")
    pdf.section_title("3.1 Mon Profil")
    pdf.bullet("Edition : nom, prenom, contact, adresse, LinkedIn, parcours anterieur.")
    pdf.bullet("Statut de disponibilite (obligatoire) : En poste / A l'ecoute / En recherche active.")
    pdf.bullet("Secteur en lecture seule (deduit de l'experience) ; competences en tags.")
    pdf.section_title("3.2 Mon Parcours")
    pdf.bullet("CRUD des experiences : entreprise, poste, type de contrat, secteur (avec Autre), salaire, ville/pays, dates, case poste actuel.")
    pdf.bullet("CRUD des certifications.")
    pdf.bullet("Blocage des modifications si le compte est anonymise (RGPD).")
    pdf.section_title("3.3 RGPD & Consentement")
    pdf.bullet("4 interrupteurs de consentement : prise de contact, partage partenaires, enquetes, newsletter.")
    pdf.bullet("Export de ses donnees (droit d'acces) en JSON / Excel / CSV.")
    pdf.bullet("Demande de suppression de compte (droit a l'effacement) avec confirmation.")
    pdf.bullet("Suivi de ses demandes + rappel des droits RGPD et duree de conservation (6 mois apres anonymisation).")
    pdf.section_title("3.4 Enquete annuelle")
    pdf.bullet("Repondre au questionnaire actif, pre-remplissage de la derniere reponse.")
    pdf.bullet("Questions conditionnees masquees si en recherche active, bloquees si consentement enquetes refuse.")

    # Interactions
    pdf.chapter_title("4", "Interactions")
    pdf.bullet("Le dashboard admin est alimente par les donnees des alumni (profil, parcours, enquetes).")
    pdf.bullet("L'anonymisation RGPD retire un alumni de tous les indicateurs.")
    pdf.bullet("L'identite alumni est lue dans localStorage, le token JWT ajoute automatiquement par l'intercepteur axios.")

    pdf.output(os.path.join(OUTPUT_DIR, "FONCTIONNALITES.pdf"))
    print("FONCTIONNALITES genere.")


if __name__ == "__main__":
    generate_fonctionnalites()
