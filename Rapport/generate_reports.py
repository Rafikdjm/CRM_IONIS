# -*- coding: utf-8 -*-
import os
from fpdf import FPDF

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_REGULAR = r"C:\Windows\Fonts\segoeui.ttf"
FONT_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"


class ReportPDF(FPDF):
    def __init__(self, title):
        super().__init__()
        self.report_title = title
        self.add_font("SegoeUI", "", FONT_REGULAR)
        self.add_font("SegoeUI", "B", FONT_BOLD)
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        self.set_font("SegoeUI", "B", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"Alumni CRM - {self.report_title}", align="L")
        self.ln(10)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font("SegoeUI", "", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def chapter_title(self, num, title):
        self.set_font("SegoeUI", "B", 14)
        self.set_text_color(30, 64, 175)
        self.cell(0, 10, f"{num}. {title}", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def section_title(self, title):
        self.set_font("SegoeUI", "B", 11)
        self.set_text_color(55, 65, 81)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body_text(self, text):
        self.set_font("SegoeUI", "", 10)
        self.set_text_color(55, 65, 81)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def bullet(self, text, indent=10):
        x = self.get_x()
        self.set_font("SegoeUI", "", 10)
        self.set_text_color(55, 65, 81)
        self.set_x(x + indent)
        self.cell(4, 5.5, "\u2022")
        self.multi_cell(0, 5.5, f"  {text}")
        self.ln(1)

    def table_header(self, cols, widths):
        self.set_font("SegoeUI", "B", 9)
        self.set_fill_color(243, 244, 246)
        self.set_text_color(30, 41, 59)
        for i, col in enumerate(cols):
            self.cell(widths[i], 7, col, border=1, fill=True)
        self.ln()

    def table_row(self, cols, widths, fill=False):
        self.set_font("SegoeUI", "", 9)
        self.set_text_color(55, 65, 81)
        if fill:
            self.set_fill_color(249, 250, 251)
        max_h = 7
        x_start = self.get_x()
        y_start = self.get_y()

        heights = []
        for i, col in enumerate(cols):
            nb = self.multi_cell(widths[i], 5, col, border=0, split_only=True)
            heights.append(len(nb) * 5)

        row_h = max(heights) if heights else 7
        if row_h < 7:
            row_h = 7

        if self.get_y() + row_h > 270:
            self.add_page()
            y_start = self.get_y()

        for i, col in enumerate(cols):
            self.set_xy(x_start + sum(widths[:i]), y_start)
            self.multi_cell(widths[i], 5, col, border=1, fill=fill)

        self.set_xy(x_start, y_start + row_h)


def generate_cartographie():
    pdf = ReportPDF("Cartographie des Donnees")
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_font("SegoeUI", "B", 20)
    pdf.set_text_color(30, 64, 175)
    pdf.cell(0, 12, "Cartographie des Donnees", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("SegoeUI", "", 10)
    pdf.set_text_color(107, 114, 128)
    pdf.cell(0, 7, "Projet Alumni CRM - Version complete et fidele au code source", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(8)

    # 1. Contexte
    pdf.chapter_title("1", "Contexte et Objectifs")
    pdf.body_text(
        "Conformement au cahier des charges du projet de conception et de developpement d'un systeme "
        "de suivi du parcours etudiant et de valorisation du reseau des anciens, cette cartographie "
        "definit precisement les donnees traitees par le systeme. L'objectif est de structurer la "
        "collecte d'informations a l'entree (inscription) et a la sortie (insertion professionnelle) "
        "tout en garantissant la stricte conformite RGPD exigee pour le pilotage de l'insertion."
    )

    # 2. Donnees Entree
    pdf.chapter_title("2", "Donnees collectees a l'entree (Phase d'Inscription)")
    pdf.body_text(
        "Ces donnees permettent de creer le profil initial de l'etudiant au moment de son integration "
        "dans l'etablissement, en s'appuyant sur les entites ETUDIANT et PROMOTION du modele de donnees."
    )

    headers = ["Categorie", "Champs (Code)", "Description"]
    widths = [38, 55, 97]
    pdf.table_header(headers, widths)

    rows = [
        ["Identite et Coordonnees", "nom, prenom, email, telephone", "Informations d'etat civil et moyens de contact personnels permettant l'identification unique de l'alumni."],
        ["Identite et Coordonnees", "date_naissance", "Date de naissance, utile pour les statistiques demographiques."],
        ["Identite et Coordonnees", "email_academique", "Adresse email institutionnelle (optionnel), pour le contact via les canaux universitaires."],
        ["Identite et Coordonnees", "address, city, country", "Adresse postale et localisation geographique de l'alumni."],
        ["Identite et Coordonnees", "linkedin", "URL du profil LinkedIn, pour le reseautage et la valorisation du profil."],
        ["Identite et Coordonnees", "availability_status", "Statut de disponibilite obligatoire : en_poste, a_lecoute, en_recherche. Conditionne l'affichage de certaines questions du questionnaire."],
        ["Identite et Coordonnees", "skills", "Tags de competences (tableau de chaines). Mots-cles decrivant les competences techniques et transversales."],
        ["Historique Academique", "parcours_anterieur", "Detail du cursus suivi avant l'integration, utile pour analyser la diversite des profils recrutes."],
        ["Historique Academique", "previous_school (inscription)", "Nom de l'etablissement precedent (collecte a l'inscription uniquement)."],
        ["Rattachement Scolaire", "id_promotion -> nom_promotion, annee_diplome, filiere", "Lien vers l'entite PROMOTION, permettant les filtrages par promotion et filiere."],
        ["Donnees complementaires", "date_inscription", "Date de creation du profil dans le systeme."],
    ]
    for i, r in enumerate(rows):
        pdf.table_row(r, widths, fill=(i % 2 == 0))

    pdf.ln(4)

    # 3. Donnees Sortie
    pdf.chapter_title("3", "Donnees collectees a la sortie (Evolution Post-Diplome)")
    pdf.body_text(
        "Le systeme assure un suivi rigoureux de l'evolution de la carriere professionnelle des alumni "
        "via les tables EXPERIENCE_PRO, ENTREPRISE et CERTIFICATION, completees par les entites "
        "QUESTIONNAIRE et REPONSE pour les donnees declaratives collectees chaque annee."
    )

    pdf.table_header(headers, widths)
    rows2 = [
        ["Suivi des Postes", "company (nom_entreprise)", "Nom de l'entreprise employeuse."],
        ["Suivi des Postes", "position (intitule_poste)", "Intitule du poste occupe."],
        ["Suivi des Postes", "type_contrat", "Type de contrat : CDI, CDD, Freelance, Alternance, Stage, Intérim, Autre."],
        ["Suivi des Postes", "start_date, end_date (date_debut/fin)", "Periode d'occupation du poste (format mois annee)."],
        ["Suivi des Postes", "is_current (poste_actuel)", "Booleen indiquant si le poste est actuellement occupe. En l'absence de coche, le systeme affiche automatiquement l'experience la plus recente."],
        ["Suivi des Postes", "description", "Description des missions et responsabilites du poste."],
        ["Informations Salariales", "salary_range (salaire)", "Champ historique en saisie libre (ex: '35k-45k EUR'), conserve pour retrocompatibilite."],
        ["Informations Salariales", "salary_annuel (NUMERIC)", "Salaire annuel brut en euros saisi via un select de tranches chiffrees (migration 012). Sert aux calculs statistiques (moyenne, min, max) avec repli sur l'ancien champ texte."],
        ["Geographie", "pays, ville", "Localisation geographique de l'entreprise (pays et ville)."],
        ["Secteur d'activite", "sector (secteur_activite)", "Secteur d'activite choisi parmi 37 categories standardisees + 'Autre' avec saisie libre."],
        ["Certifications", "name (nom_certification)", "Nom de la certification obtenue post-diplome."],
        ["Certifications", "issuer (organisme)", "Organisme émetteur de la certification."],
        ["Certifications", "date_obtained (date_obtention)", "Date d'obtention de la certification."],
        ["Reponse Questionnaire", "reponses (JSON, table REPONSE)", "Reponses aux questionnaires annuels, stockees au format JSON. Permettent le calcul d'indicateurs d'insertion."],
    ]
    for i, r in enumerate(rows2):
        pdf.table_row(r, widths, fill=(i % 2 == 0))

    pdf.ln(4)

    # 4. Donnees RGPD
    pdf.chapter_title("4", "Donnees de Consentement RGPD")
    pdf.body_text(
        "La table CONSENTEMENT_RGPD assure une traçabilité native et inaltérable des choix de "
        "confidentialite de chaque alumni."
    )

    headers3 = ["Champ", "Type / Valeurs", "Description"]
    widths3 = [42, 48, 100]
    pdf.table_header(headers3, widths3)
    rgpd_rows = [
        ["id_etudiant", "Entier (FK)", "Reference vers l'alumni concerne."],
        ["type_consentement", "4 types : prise_de_contact, partage_donnees, enquetes, newsletter", "Nature precise de l'autorisation accordee."],
        ["date_consentement", "Date (AAAA-MM-JJ)", "Date exacte du recueil du consentement."],
        ["statut", "actif | refuse", "Etat actuel du consentement ; seuls 'actif' (accorde) et 'refuse' (refuse ou retire) existent, sans statut 'revoque' distinct. Le retrait est modelise par un nouveau consentement a 'refuse'."],
        ["canal", "Formulaire inscription Web, Questionnaire annuel", "Origine formelle de l'accord, essentielle pour tout audit de conformite."],
    ]
    for i, r in enumerate(rgpd_rows):
        pdf.table_row(r, widths3, fill=(i % 2 == 0))

    pdf.section_title("4.1 Workflow et tracabilite associes")
    pdf.bullet("DEMANDE_RGPD : demandes d'export ou de suppression initiees par l'alumni ; cycle envoyee -> en_traitement -> traitee/rejetee avec verrou de prise en charge (prise_en_charge_par).")
    pdf.bullet("AUDIT_LOG : journal horodate des operations sensibles (anonymisations, purges, nettoyages) avec acteur, action, details et nombre de lignes.")
    pdf.bullet("ETUDIANT.date_anonymisation : horodatage d'anonymisation RGPD ; un compte anonymise refuse toute nouvelle ecriture et reste exclu des indicateurs jusqu'a la purge differee.")

    pdf.ln(4)

    # 5. Charte RGPD integree
    pdf.chapter_title("5", "Charte de Conformite RGPD")

    pdf.section_title("5.1 Contexte Juridique")
    pdf.body_text(
        "Le principal defi juridique d'un annuaire d'anciens reside dans le respect strict des donnees "
        "personnelles. Le CRM integre une tracabilite native et inalterable via la table CONSENTEMENT_RGPD, "
        "conforme au Reglement (UE) 2016/679 (RGPD) et a la loi Informatique et Libertes."
    )

    pdf.section_title("5.2 Les 4 Types de Consentement")
    pdf.body_text(
        "Le systeme differencie quatre categories precises de consentement, chacune etant geree "
        "independamment via des toggles dedies dans l'interface alumni (AlumniConsent.jsx)."
    )
    headers_rgpd = ["Type (Backend)", "Cle Frontend", "Description"]
    widths_rgpd = [40, 38, 112]
    pdf.table_header(headers_rgpd, widths_rgpd)
    rgpd_types = [
        ["prise_de_contact", "contact_allowed", "Autoriser l'ecole et les partenaires a contacter l'alumni pour des opportunites professionnelles, des evenements ou des enquetes."],
        ["partage_donnees", "data_sharing", "Autoriser le partage anonymise de donnees statistiques (secteur, poste) avec les entreprises partenaires."],
        ["enquetes", "survey_participation", "Accepter de recevoir et de repondre aux enquetes alumni sur l'evolution professionnelle et la satisfaction."],
        ["newsletter", "newsletter", "Recevoir la newsletter alumni avec les actualites, evenements et offres d'emploi."],
    ]
    for i, r in enumerate(rgpd_types):
        pdf.table_row(r, widths_rgpd, fill=(i % 2 == 0))
    pdf.ln(4)

    pdf.section_title("5.3 Mecanisme de Gestion du Consentement")
    pdf.bullet("Canal principal : formulaire d'inscription Web (AlumniRegistration.jsx).")
    pdf.bullet("Canal secondaire prevu : questionnaire annuel (AlumniSurvey.jsx) ; a ce jour seul le canal 'web' est reellement emis par le frontend.")
    pdf.bullet("Chaque consentement est enregistre avec : type_consentement, statut (actif/refuse), date_consentement, canal, id_etudiant.")
    pdf.bullet("L'endpoint POST /consentements/ cree ou met a jour le consentement pour chaque type.")
    pdf.bullet("L'alumni peut modifier ses preferences a tout moment via l'interface de consentement.")
    pdf.bullet("Le retrait du consentement est modelise par un nouveau vote 'refuse' avec la date courante.")
    pdf.bullet("Enregistrement de la date exacte du recueil et identification du canal de collecte pour tout audit de conformite.")
    pdf.bullet("Information de l'alumni dans l'interface de consentement (AlumniConsent.jsx) : duree de conservation des donnees (suppression 6 mois apres anonymisation) et contact du DPO (contact@ionis-stm.com).")

    pdf.section_title("5.4 Droits RGPD Implementes")
    pdf.bullet("Droit d'acces a vos donnees personnelles : page de profil en lecture seule, suivi des demandes via GET /rgpd/demandes/moi et export json/Excel/CSV auto-service via GET /rgpd/export.")
    pdf.bullet("Droit de rectification et de mise a jour (AlumniProfile.jsx).")
    pdf.bullet("Droit a l'effacement (droit a l'oubli) : workflow de demandes auto-service (POST /rgpd/demandes) traite par anonymisation ANONYMISE_<id>@anonymise.io puis purge differee ; anonymisation admin directe possible via POST /etudiants/{id}/anonymiser.")
    pdf.bullet("Droit de retrait du consentement a tout moment (AlumniConsent.jsx avec toggles).")
    pdf.bullet("Les donnees de consentement ne font l'objet d'aucun chiffrement specifique au niveau applicatif : leur protection repose sur les mecanismes standard de l'infrastructure PostgreSQL.")
    pdf.bullet("La notification de violation de donnees (article 33 du RGPD) n'est pas couverte par une fonctionnalite dediee du systeme a ce jour.")

    pdf.output(os.path.join(OUTPUT_DIR, "Cartographie des Donnees - Alumni CRM.pdf"))
    print("Cartographie generee.")


def generate_rgpd():
    pdf = ReportPDF("Charte RGPD")
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_font("SegoeUI", "B", 20)
    pdf.set_text_color(30, 64, 175)
    pdf.cell(0, 12, "Charte de Conformite RGPD", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("SegoeUI", "", 10)
    pdf.set_text_color(107, 114, 128)
    pdf.cell(0, 7, "Projet Alumni CRM - Version complete et fidele au code source", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(8)

    # 1. Contexte
    pdf.chapter_title("1", "Contexte Juridique")
    pdf.body_text(
        "Le principal defi juridique d'un annuaire d'anciens reside dans le respect strict des donnees "
        "personnelles. Le CRM integre une tracabilite native et inalterable via la table CONSENTEMENT_RGPD, "
        "conforme au Reglement (UE) 2016/679 (RGPD) et a la loi Informatique et Libertes. Le chiffrement "
        "specifique des donnees de consentement n'est pas implemente au niveau applicatif (protection confiee "
        "aux mecanismes de l'infrastructure), et aucune fonctionnalite de notification de violation de donnees "
        "n'existe a ce jour."
    )

    # 2. Types de consentement
    pdf.chapter_title("2", "Les 4 Types de Consentement Implementes")
    pdf.body_text(
        "Le systeme differencie quatre categories precises de consentement, chacune etant gerée "
        "independamment via des toggles dedies dans l'interface alumni (AlumniConsent.jsx)."
    )

    headers = ["Type (Backend)", "Cle Frontend", "Description"]
    widths = [40, 38, 112]
    pdf.table_header(headers, widths)
    rows = [
        ["prise_de_contact", "contact_allowed", "Autoriser l'ecole et les partenaires a contacter l'alumni pour des opportunites professionnelles, des evenements ou des enquetes."],
        ["partage_donnees", "data_sharing", "Autoriser le partage anonymise de donnees statistiques (secteur, poste) avec les entreprises partenaires."],
        ["enquetes", "survey_participation", "Accepter de recevoir et de repondre aux enquetes alumni sur l'evolution professionnelle et la satisfaction."],
        ["newsletter", "newsletter", "Recevoir la newsletter alumni avec les actualites, evenements et offres d'emploi."],
    ]
    for i, r in enumerate(rows):
        pdf.table_row(r, widths, fill=(i % 2 == 0))

    pdf.ln(4)

    # 3. Gestion du consentement
    pdf.chapter_title("3", "Mecanisme de Gestion du Consentement")
    pdf.section_title("3.1 Collecte du consentement")
    pdf.bullet("Canal principal : formulaire d'inscription Web (AlumniRegistration.jsx).")
    pdf.bullet("Canal secondaire prevu : questionnaire annuel (AlumniSurvey.jsx) ; a ce jour seul le canal 'web' est reellement emis par le frontend.")
    pdf.bullet("Chaque consentement est enregistre avec : type_consentement, statut (actif/refuse), date_consentement, canal, id_etudiant.")
    pdf.bullet("L'endpoint POST /consentements/ cree ou met a jour le consentement pour chaque type.")
    pdf.bullet("L'interface de consentement informe l'alumni de la duree de conservation des donnees (suppression 6 mois apres anonymisation) et affiche le contact du DPO (contact@ionis-stm.com).")

    pdf.section_title("3.2 Modification et retrait")
    pdf.bullet("L'alumni peut modifier ses preferences a tout moment via l'interface de consentement.")
    pdf.bullet("Le retrait du consentement est modelise par un nouveau vote 'refuse' avec la date courante.")
    pdf.bullet("L'interface affiche la date de derniere mise a jour du consentement.")
    pdf.bullet("Une suppression physique d'un enregistrement reste possible via DELETE /consentements/{id_consentement} (proprietaire ou admin) ; le retrait usuel conserve l'historique complet des votes.")

    pdf.section_title("3.3 Traçabilite")
    pdf.bullet("Enregistrement de la date exacte du recueil (date_consentement).")
    pdf.bullet("Identification formelle du canal de collecte (formulaire inscription, questionnaire).")
    pdf.bullet("Historique complet des votes de consentement dans la base de donnees.")

    pdf.section_title("3.4 Consommation des consentements (relations fonctionnelles)")
    pdf.body_text(
        "Chaque consentement est reellement consomme par une fonctionnalite du systeme : un refus "
        "(statut 'refuse') desactive l'usage correspondant. Un alumni sans vote sur un type reste "
        "eligible ('inconnu' tolere), par coherence avec l'emission du consentement. Le vote le plus "
        "recent est determine par une sous-requete correlee identique partout (ORDER BY "
        "date_consentement DESC, id_consentement DESC LIMIT 1)."
    )
    pdf.bullet("'newsletter' : recevoir les newsletters (POST /newsletter/envoyer, ciblage par promotion / secteur / consents actifs).")
    pdf.bullet("'enquetes' : acceder au questionnaire actif (GET /questionnaires/actif) et recevoir les relances (POST /admin/questionnaires/notififier). Un refus bloque la restitution du questionnaire (HTTP 403) et masque le lien 'Enquete annuelle' dans la navigation alumni (AlumniLayout.jsx).")
    pdf.bullet("'prise_de_contact' : recevoir newsletter et relances questionnaire ; un refus exclut l'alumni des deux envois (newsletter.py et questionnaires.py). C'est le seul consentement dont le refus declenche l'anonymisation du profil via cleanup.py (CONSENTEMENT_ARCHIVE_TYPE = 'prise_de_contact').")
    pdf.bullet("'partage_donnees' : seul ce perimetre (alumni ayant accepte le partage) alimente les indicateurs partenaires GET /admin/indicateurs/partenaires (comptages et moyennes d'insertion anonymises, aucune donnee personnelle avec le partenaire).")

    # 4. Droits RGPD
    pdf.chapter_title("4", "Droits RGPD Implementes dans l'Interface")
    pdf.body_text("L'interface alumni affiche et implemente les droits suivants :")
    pdf.bullet("Droit d'acces a vos donnees personnelles : page de profil en lecture seule, suivi des demandes via GET /rgpd/demandes/moi et export json/Excel/CSV auto-service via GET /rgpd/export.")
    pdf.bullet("Droit de rectification et de mise a jour (AlumniProfile.jsx).")
    pdf.bullet("Droit a l'effacement (droit a l'oubli) : mentionne dans l'interface, implemente via un workflow de demandes auto-service (POST /rgpd/demandes) traite par anonymisation puis purge differee.")
    pdf.bullet("Droit de retrait du consentement a tout moment (AlumniConsent.jsx avec toggles).")

    # 5. Valeurs du statut
    pdf.chapter_title("5", "Modele de Donnees CONSENTEMENT_RGPD")

    headers2 = ["Champ", "Type", "Contraintes"]
    widths2 = [42, 48, 100]
    pdf.table_header(headers2, widths2)
    rows2 = [
        ["id_etudiant", "Entier (FK)", "NOT NULL, reference vers ETUDIANT.id_etudiant."],
        ["type_consentement", "Enum / Chaine", "Valeurs : 'prise_de_contact', 'partage_donnees', 'enquetes', 'newsletter'."],
        ["date_consentement", "Date", "NOT NULL, date du jour au moment de l'operation."],
        ["statut", "Chaine", "Deux valeurs implementees : 'actif' (consentement accorde), 'refuse' (refuse ou retire). Aucun statut 'revoque' distinct n'existe : le retrait passe par un nouveau vote 'refuse' horodate."],
        ["canal", "Chaine", "Origine : 'web' (formulaire inscription), 'questionnaire' (enquete annuelle, valeur acceptee par l'API mais non encore emise par le frontend a ce jour)."],
    ]
    for i, r in enumerate(rows2):
        pdf.table_row(r, widths2, fill=(i % 2 == 0))

    pdf.ln(4)

    # 6. Workflow des demandes RGPD
    pdf.chapter_title("6", "Workflow des Demandes RGPD (Effacement et Portabilite)")
    pdf.body_text(
        "Au-dela du consentement, le CRM met en oeuvre un workflow complet de traitement des droits "
        "d'acces, d'effacement et de portabilite, base sur la table DEMANDE_RGPD :"
    )
    pdf.bullet("Depot auto-service : POST /rgpd/demandes (types 'export' ou 'suppression') ; suivi et annulation par l'alumni via GET /rgpd/demandes/moi et DELETE /rgpd/demandes/{id}.")
    pdf.bullet("Cycle de statuts : envoyee -> en_traitement -> traitee/rejetee (contrainte SQL, migration 009), avec verrou anti-traitement parallele (prise_en_charge_par, date_prise_en_charge).")
    pdf.bullet("Traitement d'une demande de suppression = anonymisation irreversible (email remplace par ANONYMISE_<id>@anonymise.io, donnees personnelles effacees), puis purge physique differee apres PURGE_DELAY_MONTHS mois (defaut 6) via purge.py (--dry-run disponible) ou POST /admin/demandes-rgpd/purge-anonymises.")
    pdf.bullet("Portabilite : export json/Excel/CSV auto-service via GET /rgpd/export ; exports admin unitaires et en masse.")
    pdf.bullet("Operations tracees dans AUDIT_LOG (acteur, action, details).")

    pdf.output(os.path.join(OUTPUT_DIR, "Charte de Conformite RGPD - Alumni CRM.pdf"))
    print("Charte RGPD generee.")


def generate_strategie():
    pdf = ReportPDF("Strategie de Mise a Jour")
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_font("SegoeUI", "B", 20)
    pdf.set_text_color(30, 64, 175)
    pdf.cell(0, 12, "Strategie de Mise a Jour des Donnees", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("SegoeUI", "", 10)
    pdf.set_text_color(107, 114, 128)
    pdf.cell(0, 7, "Projet Alumni CRM - Version complete et fidele au code source", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(8)

    # 1. Defi
    pdf.chapter_title("1", "Le Defi de l'Obsolescence des Donnees")
    pdf.body_text(
        "Le principal defi d'un annuaire d'anciens est la peremption rapide des informations. Sans un "
        "processus proactif, les donnees d'insertion (postes, entreprises, salaires) deviennent "
        "rapidement obsoletes. La gouvernance du CRM repose sur un processus concu pour inciter "
        "continuellement les diplomes a actualiser leurs profils."
    )

    # 2. Mise a jour manuelle
    pdf.chapter_title("2", "Mise a Jour Manuelle par l'Alumni")

    pdf.section_title("2.1 Gestion du profil (AlumniProfile.jsx)")
    pdf.bullet("L'alumni peut modifier : prenom, nom, email, telephone, adresse, ville, pays, LinkedIn, date de naissance, email academique, parcours anterieur.")
    pdf.bullet("Le statut de disponibilite (en_poste / a_lecoute / en_recherche) est obligatoire et conditionne le comportement du systeme.")
    pdf.bullet("Les tags de competences (skills) sont geres via un systeme d'ajout/suppression dynamique.")

    pdf.section_title("2.2 Gestion du parcours (AlumniCareer.jsx)")
    pdf.bullet("Ajout/suppression d'experiences professionnelles (entreprise, poste, secteur, contrat, dates, salaire, localisation). La modification directe d'une experience existante n'est pas disponible a ce jour : il faut la supprimer puis la recreer (limite assumee du prototype).")
    pdf.bullet("Ajout/suppression de certifications (nom, organisme, date d'obtention).")
    pdf.bullet("Detection automatique du 'poste actuel' : si aucun poste n'est coche comme actuel, le systeme affiche l'experience la plus recente.")
    pdf.bullet("Alerte visuelle si le statut est 'en_poste' mais aucun poste n'est coche comme actuel.")

    # 3. Questionnaire annuel
    pdf.chapter_title("3", "Questionnaire Annuel Automatise")

    pdf.section_title("3.1 Cote administration (AdminQuestionnaires.jsx)")
    pdf.bullet("Creation, modification, suppression de questionnaires via une interface dediee.")
    pdf.bullet("4 types de questions : texte libre, choix multiple (radio), oui/non (boolean), note 1-5 (rating).")
    pdf.bullet("Systeme de Tags KPI : chaque question peut etre etiquetee (ex: 'adequation_formation') pour alimenter des indicateurs de pilotage.")
    pdf.bullet("Questions conditionnees : masquage automatique d'une question si l'alumni est en recherche active (conditionnee_statut_emploi).")
    pdf.bullet("Cycle de vie : activation / desactivation / reactivation d'un questionnaire.")
    pdf.bullet("Consultation des reponses avec affichage nom, prenom, email, date et details.")

    pdf.section_title("3.2 Cote alumni (AlumniSurvey.jsx)")
    pdf.bullet("L'alumni accede au questionnaire actif depuis le menu lateral ; un refus du consentement 'enquetes' bloque la restitution (HTTP 403) et masque le menu lateral, RGPD.")
    pdf.bullet("Les reponses precedentes sont pre-remplies pour faciliter la mise a jour ; le pre-remplissage s'appuie sur le dernier questionnaire renseigne, sans historique complet des reponses dans l'interface.")
    pdf.bullet("Les questions non applicables (conditionnees au statut) sont automatiquement masquees et enregistrees comme 'Non applicable'.")
    pdf.bullet("Possibilite de modifier ses reponses a tout moment.")
    pdf.bullet("Validation : toutes les questions visibles doivent etre repondues avant soumission.")

    # 4. Guide processus
    pdf.chapter_title("4", "Guide des Processus pour le Service des Relations Entreprises")

    pdf.section_title("4.1 Pilotage des campagnes")
    pdf.bullet("Le service cree et administre les questionnaires via l'interface AdminQuestionnaires.")
    pdf.bullet("Les questions avec le tag 'adequation_formation' alimentent automatiquement l'indicateur d'adequation formation/emploi du tableau de bord.")
    pdf.bullet("Activation/desactivation des questionnaires selon le calendrier de collecte ; l'activation reste manuelle, sans declenchement automatique planifie a ce jour.")
    pdf.bullet("Relances automatiques : l'endpoint POST /admin/questionnaires/notififier envoie des relances email aux alumni n'ayant pas repondu au questionnaire actif (filtre par promotion ; RGPD : exclusion des alumni ayant refuse le consentement 'enquetes' OU 'prise_de_contact', sur le vote le plus recent), sans interface admin dediee pour cet envoi a ce jour.")

    pdf.section_title("4.2 Valorisation du reseau")
    pdf.bullet("Utilisation du tableau de bord admin pour filtrer les alumni par entreprise, secteur, promotion.")
    pdf.bullet("Identification des opportunites de stages ou de partenariats via l'annuaire enrichi.")
    pdf.bullet("Enrichissement progressif du reseau par les mises a jour alumni et les reponses aux questionnaires.")

    pdf.section_title("4.3 Newsletter Alumni - Processus Detaille")
    pdf.body_text(
        "La newsletter est un levier strategique d'animation du reseau et de mise a jour des donnees. "
        "Elle doit etre geree comme un processus managérial structuré, pas comme un envoi ponctuel."
    )
    pdf.bullet("Ciblage : seuls les alumni ayant active le consentement 'newsletter' (type_consentement = 'newsletter', statut = 'actif') sont contactes.")
    pdf.bullet("Frequence : mensuelle ou bimestrielle, avec un calendrier editorial defini par le service des Relations Entreprises.")
    pdf.bullet("Contenu type : actualites de l'ecosysteme alumni, offres d'emploi partenaires, evenements (reunions, conferences), appel a mise a jour du profil.")
    pdf.bullet("Call-to-Action (CTA) obligatoire : chaque newsletter doit contenir un lien direct vers la page de mise a jour du profil alumni (AlumniProfile.jsx).")
    pdf.bullet("Personnalisation : le ciblage peut etre affine par promotion, secteur d'activite, geographie ou disponibilite (en_poste / en_recherche).")
    pdf.bullet("Suivi des metriques : taux d'ouverture, taux de clic sur le CTA, taux de mise a jour du profil suite a l'envoi.")
    pdf.bullet("Integration RGPD : chaque enquete est precedee d'un rappel du droit de desabonnement. Le mecanisme de desinscription automatique (lien mettant le consentement a 'refuse') n'est pas encore implemente — liens placeholder dans le gabarit HTML (manque encore ouvert).")
    pdf.bullet("Implementation technique : l'endpoint backend POST /newsletter/envoyer a ete implemente (filtres de ciblage promotion/secteur, ciblage sur consentement newsletter actif ET 'prise_de_contact' non refuse, mode console en dev / Resend en prod). Le composant d'envoi cote frontend n'est pas encore developpe (manque encore ouvert).")
    pdf.bullet("Calendrier automatique : prevision d'un mecanisme de planification (cron job) pour l'envoi recurrent, avec notification admin avant envoi pour validation du contenu.")

    pdf.output(os.path.join(OUTPUT_DIR, "Strategie de Mise a Jour des Donnees - Alumni CRM.pdf"))
    print("Strategie generee.")


def generate_indicateurs():
    pdf = ReportPDF("Indicateurs d'Insertion")
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_font("SegoeUI", "B", 20)
    pdf.set_text_color(30, 64, 175)
    pdf.cell(0, 12, "Analyse des Indicateurs d'Insertion", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("SegoeUI", "", 10)
    pdf.set_text_color(107, 114, 128)
    pdf.cell(0, 7, "Projet Alumni CRM - Version complete et fidele au code source", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(8)

    # 1. Objectif
    pdf.chapter_title("1", "Objectif de la Modelisation")
    pdf.body_text(
        "Conformement aux exigences du cahier des charges, cette section modelise les rapports "
        "d'insertion professionnelle requis par les organismes de certification et les autorites de "
        "tutelle. L'enjeu est de transformer les donnees brutes collectees dans le CRM en indicateurs "
        "de performance strategiques pour le pilotage de l'ecole."
    )

    # 2. Indicateurs
    pdf.chapter_title("2", "Indicateurs Cles de Pilotage")

    headers = ["Indicateur", "Definition", "Metier / Utilisation Strategique"]
    widths = [42, 62, 86]
    pdf.table_header(headers, widths)
    rows = [
        ["Taux d'emploi a 6 mois", "Proportion des diplomes en activite (CDI, CDD, etc.) six mois apres l'obtention du diplome. Source : table EXPERIENCE_PRO filtree par date_debut.", "Indicateur indispensable pour les rapports ministeriels et les audits de certification qualite de l'etablissement."],
        ["Taux d'emploi global (brut)", "Proportion de tous les diplomes ayant au moins une experience professionnelle enregistree, quel que soit le delai. Calcule par : (alumni en poste / total alumni) x 100.", "Vue d'ensemble de l'efficacite du systeme de formation sur l'ensemble des promotions."],
        ["Adequation formation/emploi", "Mesure du taux de correspondance entre la filiere suivie et le secteur d'activite des postes occupes. Source : question KPI taggee 'adequation_formation' dans le questionnaire.", "Evaluation de la pertinence de l'offre de formation au regard des besoins reels du marche du travail."],
        ["Salaire moyen par filiere", "Calcul du salaire brut annuel moyen des diplomes, segmente par promotion (moyenne, min et max globaux egalement exposes). Le calcul par secteur d'activite n'est pas implemente a ce jour.", "Outil de valorisation des debouches aupres des futurs candidats et des entreprises partenaires."],
        ["Alumni actifs", "Nombre d'alumni ayant au moins une experience professionnelle enregistree dans le CRM.", "Indicateur d'engagement : mesure l'adoption du systeme par les anciens eleves."],
        ["Taux de completion", "Pourcentage d'alumni ayant complete au moins leur profil + une experience professionnelle.", "Mesure de la qualite des donnees collectees, essentielle pour la fiabilite des indicateurs."],
        ["Alumni par promotion", "Nombre d'alumni inscrits et taux d'emploi pour chaque promotion. Source : table ETUDIANT jointe a PROMOTION.", "Analyse comparative des cohortes pour identifier les promotions necessitant un accompagnement renforce."],
        ["Repartition par secteur", "Nombre d'alumni par secteur d'activite. Source : agrégation du champ secteur_activite.", "Cartographie des debouches et identification des secteurs recrutant le plus de diplomes."],
    ]
    for i, r in enumerate(rows):
        pdf.table_row(r, widths, fill=(i % 2 == 0))

    pdf.ln(4)

    # 3. Implementation technique
    pdf.chapter_title("3", "Implementation Technique des Indicateurs")
    pdf.section_title("3.1 Endpoints API")

    headers2 = ["Endpoint", "Description", "Donnees retournees"]
    widths2 = [55, 60, 75]
    pdf.table_header(headers2, widths2)
    rows2 = [
        ["GET /admin/indicateurs", "Indicateurs principaux du tableau de bord.", "total_alumni, taux_emploi_6mois (global et par promotion avec statut_maturite/date_reference), taux_couverture, coherence_availability_poste_actuel, alumni_actifs, taux_reponse, salaire_moyen/min/max, salaires_renseignes, hypothese, source_de_verite."],
        ["GET /admin/indicateurs/secteurs", "Repartition des alumni par secteur d'activite.", "tableau de {secteur, count} + total_alumni."],
        ["GET /admin/indicateurs/types-contrat", "Repartition des experiences en cours par type de contrat.", "tableau de {type_contrat, count} (valeurs vides groupees sous 'Non renseigne')."],
        ["GET /admin/indicateurs/kpi-tag?tag=X", "Valeur d'un indicateur KPI calcule a partir des reponses taggees.", "valeur, unite (% ou moyenne), total_repondants, question_texte, distribution."],
        ["GET /admin/indicateurs/kpi-tags", "Tous les tags KPI des questionnaires actifs, calcules automatiquement ; un echec sur un tag ne fait pas echouer la route.", "[{tag, libelle, pourcentage, nb_repondants, valeur, unite, distribution}, ...]"],
        ["GET /admin/indicateurs/kpi-tags-actifs", "Liste des tags DISTINCT utilises par les questions des questionnaires actifs.", "{tags: [...]}"],
        ["GET /admin/indicateurs/partenaires", "Indicateurs d'insertion agregees et anonymisees restreints aux alumni ayant accepte le partage de donnees ('partage_donnees' actif) : perimetre transmissible aux partenaires.", "nb_consentants, taux_emploi_pourcentage, en_emploi, salaire_moyen, par_promotion, top_secteurs, perimetre."],
    ]
    for i, r in enumerate(rows2):
        pdf.table_row(r, widths2, fill=(i % 2 == 0))

    pdf.ln(4)

    pdf.section_title("3.2 Calcul des indicateurs")
    pdf.bullet("Taux d'emploi a 6 mois : calcule par le backend ; une experience compte si sa date_debut tombe dans les 6 mois suivant le 1er decembre de l'annee de diplome (hypothese de diplomation en juin). Les cohortes dont la fenetre de 6 mois n'est pas ecoulee sont exclues (taux null, statut 'en_attente').")
    pdf.bullet("Taux d'emploi global : (alumni avec experience / total alumni) x 100, calcule dans le frontend a partir des indicateurs par promotion.")
    pdf.bullet("Adequation formation/emploi : le frontend interroge l'endpoint /admin/indicateurs/kpi-tag?tag=adequation_formation, qui agrege les reponses a la question taggee.")
    pdf.bullet("Tags KPI : chaque question de questionnaire peut porter un tag (ex: 'adequation_formation') ; les indicateurs correspondants sont calcules et exposes automatiquement via /kpi-tags, l'ajout d'un tag sur une question faisant apparaitre l'indicateur dans le tableau de bord sans modification du code backend.")
    pdf.bullet("Repartition par secteur : aggregation SQL du champ secteur_activite avec comptage.")
    pdf.bullet("Salaire moyen : desormais calcule cote backend (AVG/MIN/MAX) sur les experiences en cours, en privilegiant salary_annuel (numerique) avec repli sur le champ salaire historique ; salaires a zero exclus.")
    pdf.bullet("Coherence declarative : l'indicateur coherence_availability_poste_actuel mesure l'ecart entre le statut declare (availability_status) et la presence d'un poste en cours reel dans EXPERIENCE_PRO (source de verite).")

    pdf.section_title("3.3 Visualisation (AdminDashboard.jsx)")
    pdf.bullet("KPI cards principales : Total Alumni actifs, Taux d'emploi 6 mois, Taux d'emploi global.")
    pdf.bullet("KPI secondaires : Taux de completion, Adequation formation/emploi, Salaire moyen avec jauge dynamique (fourchettes min/max calculees sur les donnees reelles).")
    pdf.bullet("Graphique donut : Repartition par secteur (maximum 5 categories visibles + segment 'Autres').")
    pdf.bullet("Graphique barres horizontales : Alumni par promotion avec pourcentage d'emploi et timeline de maturite des cohortes (statut_maturite).")
    pdf.bullet("Graphique barres : repartition des types de contrat des experiences en cours.")

    # 4. Alertes
    pdf.chapter_title("4", "Alertes et Signaux Faibles")
    pdf.bullet("Si le statut est 'en_poste' mais aucun poste n'est coche comme 'actuel', une alerte ambrée est affichee dans l'interface Parcours.")
    pdf.bullet("Si le KPI 'adequation_formation' n'a aucune reponse, le dashboard affiche un etat vide avec des instructions pour taguer une question.")
    pdf.bullet("Le taux de completion permet de detecter les alumni n'ayant pas complete leur profil.")

    # 5. Modele de Rapport Ministeriel
    pdf.chapter_title("5", "Modele de Rapport d'Insertion pour les Autorites de Tutelle")
    pdf.body_text(
        "Conformement aux exigences du cahier des charges, les rapports d'insertion professionnelle "
        "doivent etre transmis aux ministères et organismes de certification (CTI, HCERES). "
        "Voici le format standardise genere a partir des indicateurs du CRM."
    )

    pdf.section_title("5.1 Informations Generales du Rapport")
    headers_info = ["Champ", "Valeur / Source"]
    widths_info = [60, 130]
    pdf.table_header(headers_info, widths_info)
    info_rows = [
        ["Institution", "Nom de l'etablissement (ex: Ionis Education Group)"],
        ["Periode couverte", "Annee universitaire en cours (ex: 2025-2026)"],
        ["Promotion concernee", "Filtree par annee_diplome (ex: Promo 2025)"],
        ["Date de generation", "Date courante au moment de l'export"],
        ["Source des donnees", "CRM Alumni - tables ETUDIANT, EXPERIENCE_PRO, REPONSE"],
    ]
    for i, r in enumerate(info_rows):
        pdf.table_row(r, widths_info, fill=(i % 2 == 0))
    pdf.ln(4)

    pdf.section_title("5.2 Indicateurs Cles du Rapport")
    headers_kpi = ["Indicateur", "Valeur attendue", "Calcul"]
    widths_kpi = [52, 50, 88]
    pdf.table_header(headers_kpi, widths_kpi)
    kpi_rows = [
        ["Effectif de la promotion", "Nombre total d'inscrits", "COUNT(etudiants WHERE id_promotion = X)"],
        ["Taux d'emploi a 6 mois", "Pourcentage (%)", "Alumni avec experience debutant <= 6 mois apres diplomation / total promotion"],
        ["Taux d'emploi a 12 mois", "Pourcentage (%) - non calcule a ce jour", "Formule : alumni avec experience debutant <= 12 mois apres diplomation / total promotion"],
        ["Taux d'insertion totale", "Pourcentage (%)", "Alumni avec au moins 1 experience / total promotion"],
        ["Adequation formation-emploi", "Pourcentage (%)", "Reponses KPI tag 'adequation_formation' / total repondants"],
        ["Salaire moyen par filiere", "Euros (moyen, min, max)", "AVG/MIN/MAX sur EXPERIENCE_PRO.salary_annuel (>0) des experiences en cours, avec repli sur le champ salaire texte ; moyennes exposees par promotion"],
        ["Repartition par secteur", "Tableau (secteur, %)", "COUNT(experiences WHERE secteur = X) / total experiences"],
        ["Repartition geographique", "Tableau (pays, ville, %)", "COUNT(alumni WHERE pays = X) / total alumni"],
    ]
    for i, r in enumerate(kpi_rows):
        pdf.table_row(r, widths_kpi, fill=(i % 2 == 0))
    pdf.ln(4)

    pdf.section_title("5.3 Format et Cadriciel du Rapport")
    pdf.bullet("Format : PDF genere automatiquement depuis le CRM ou export Excel/CSV.")
    pdf.bullet("Frequence : annuelle, coincidant avec la campagne de collecte du questionnaire.")
    pdf.bullet("Destinataires : Ministere de l'Enseignement Superieur, organes de certification (CTI, HCERES), direction de l'etablissement.")
    pdf.bullet("Diffusion : via le tableau de bord admin (AdminDashboard.jsx) avec bouton d'export.")
    pdf.bullet("Archivage : chaque edition est horodatee et conservee pour audit de conformite.")

    pdf.section_title("5.4 Exemple de Tableau de Synthese par Promotion")
    headers_syn = ["Promotion", "Nb Alumni", "Emploi 6 mois", "Emploi 12 mois", "Adequation"]
    widths_syn = [35, 30, 40, 40, 45]
    pdf.table_header(headers_syn, widths_syn)
    synth_rows = [
        ["Promo 2023", "120", "78%", "85%", "72%"],
        ["Promo 2024", "135", "81%", "88%", "76%"],
        ["Promo 2025", "128", "75% (en cours)", "N/A", "70%"],
    ]
    for i, r in enumerate(synth_rows):
        pdf.table_row(r, widths_syn, fill=(i % 2 == 0))

    pdf.output(os.path.join(OUTPUT_DIR, "Analyse des Indicateurs d'Insertion - Alumni CRM.pdf"))
    print("Indicateurs genere.")


def generate_rapport_stage():
    pdf = ReportPDF("Rapport de Stage")
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_font("SegoeUI", "B", 20)
    pdf.set_text_color(30, 64, 175)
    pdf.cell(0, 12, "Rapport de Stage PreMsc 2026", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("SegoeUI", "", 10)
    pdf.set_text_color(107, 114, 128)
    pdf.cell(0, 7, "Conception et Développement d'un Alumni CRM", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.cell(0, 7, "Ionis Education Group", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(10)

    # Introduction
    pdf.chapter_title("1", "Introduction et Contexte")
    pdf.section_title("1.1 Présentation de l'entreprise")
    pdf.body_text(
        "Ce stage s'est déroulé au sein d'Ionis Education Group, groupe d'enseignement supérieur "
        "regroupant plusieurs écoles d'ingénieurs et de management. L'établissement forme chaque année "
        "des dizaines de diplômés dans les domaines du numérique, du management et de l'ingénierie. "
        "Le suivi de l'insertion professionnelle de ces anciens élèves constitue un enjeu stratégique "
        "pour le pilotage de la formation et l'animation du réseau alumni."
    )
    pdf.section_title("1.2 Sujet de stage")
    pdf.body_text(
        "Le sujet confié est la 'Conception et développement d'un système de suivi du parcours "
        "étudiant et de valorisation du réseau des anciens (Alumni CRM)'. L'objectif était de créer "
        "une solution centralisée permettant de suivre le cycle de vie de l'étudiant, de son inscription "
        "administrative jusqu'à son évolution professionnelle post-diplôme, afin de faciliter le pilotage "
        "de l'insertion et l'animation du réseau."
    )
    pdf.section_title("1.3 Objectifs du stage")
    pdf.bullet("Créer un CRM alumni complet avec côté administration et côté alumni.")
    pdf.bullet("Modéliser et implémenter une base de données relationnelle SQL (14 tables).")
    pdf.bullet("Développer un tableau de bord admin avec indicateurs d'insertion professionnelle.")
    pdf.bullet("Implémenter la conformité RGPD (consentement, export, suppression, audit).")
    pdf.bullet("Automatiser l'import/export de données via des fichiers Excel.")
    pdf.bullet("Documenter les processus managériaux (gouvernance, newsletter, questionnaire annuel).")

    # 1.4 Positionnement du groupe
    pdf.section_title("1.4 Positionnement du groupe IONIS Education Group")
    pdf.body_text(
        "IONIS Education Group constitue l'un des principaux groupes d'enseignement supérieur privés "
        "en France. Le groupe fédère un portefeuille d'écoles spécialisées dans les domaines du "
        "numérique, de l'ingénierie et du management, couvrant un spectre large de formations allant "
        "du Pré-MSc au niveau Bac+5."
    )
    pdf.body_text(
        "Chaque école du groupe (EPITECH pour le développement informatique, ESGI pour l'informatique "
        "et le management, IIM pour le management du numérique, ESM pour le management, ISA pour "
        "l'agronomie, entre autres) cible des parcours spécifiques mais partage une même exigence de "
        "placement professionnel et de suivi des diplômés. Cette organisation en écosystème multi-écoles "
        "crée un enjeu commun : disposer d'un dispositif de suivi alumni scalable, capable de fonctionner "
        "à l'échelle de plusieurs centaines de diplômés par promotion sur l'ensemble du groupe."
    )
    pdf.body_text(
        "[A COMPLETER : donnees chiffrees sur le nombre total d'etudiants, le nombre de promotions, "
        "le nombre d'ecoles du groupe — sources internes Ionis Education Group]"
    )

    # 1.5 Enjeux du suivi alumni
    pdf.section_title("1.5 Enjeux du suivi alumni dans le contexte Ionis")
    pdf.body_text(
        "Le suivi de l'insertion professionnelle des anciens élèves constitue un enjeu à plusieurs "
        "niveaux dans le contexte d'un groupe comme Ionis Education Group :"
    )
    pdf.bullet("Enjeu réglementaire : les organismes de tutelle et de certification (CTI, HCERES) "
        "exigent des rapports d'insertion professionnelle réguliers contenant des indicateurs "
        "standardisés (taux d'emploi à 6 et 12 mois, adéquation formation-emploi, répartition par "
        "secteur et type de contrat).")
    pdf.bullet("Enjeu pédagogique : le taux d'insertion et la nature des postes occupés constituent "
        "des indicateurs de pertinence de l'offre de formation. Le suivi alumni alimente la boucle de "
        "rétroaction entre la formation et l'emploi.")
    pdf.bullet("Enjeu managérial : le service des relations entreprises a besoin de données structurées "
        "pour piloter les partenariats, identifier les secteurs recrutant le plus de diplômés et "
        "préparer les événements de networking.")
    pdf.bullet("Enjeu technique : la collecte et le traitement des données personnelles des alumni "
        "sont soumis au RGPD. Un outil centralisé doit intégrer ces exigences dès la conception.")

    # 1.6 Positionnement du projet
    pdf.section_title("1.6 Positionnement du projet Alumni CRM")
    pdf.body_text(
        "Le projet Alumni CRM s'inscrit dans une démarche de professionnalisation du suivi des anciens "
        "élèves au sein d'IONIS-STM. Il vise à remplacer les processus manuels de collecte de données "
        "(emails ponctuels, formulaires papier, appels téléphoniques) par un système structuré et "
        "traçable, capable de produire automatiquement les indicateurs requis par les autorités de tutelle."
    )
    pdf.body_text(
        "Le système devait répondre à quatre objectifs fonctionnels définis dans le sujet de stage : "
        "suivre le cycle de vie de l'étudiant de l'inscription à l'évolution post-diplôme, fournir "
        "des indicateurs d'insertion, assurer la conformité RGPD, et produire un guide des processus "
        "d'animation du réseau alumni."
    )
    pdf.body_text(
        "[A COMPLETER : positionnement strategique d'Ionis Education Group par rapport aux autres "
        "acteurs prives de l'enseignement superieur — si information disponible]"
    )

    # Problematique
    pdf.chapter_title("2", "Problématique et Enjeux")
    pdf.section_title("2.1 Problématique identifiée")
    pdf.body_text(
        "Sans système centralisé, les données d'insertion des diplômés deviennent rapidement obsolètes. "
        "Les services des relations entreprises manquent d'outils fiables pour piloter les indicateurs "
        "d'insertion (taux d'emploi à 6 mois, adéquation formation-emploi) exigés par les ministères "
        "et organismes de certification (CTI, HCERES). Le réseau alumni reste inanimé et les anciens "
        "élèves n'ont pas de canal structuré pour maintenir leurs informations à jour."
    )
    pdf.section_title("2.2 Enjeux")
    pdf.bullet("Enjeu pédagogique : évaluer la pertinence de l'offre de formation par les débouchés réels.")
    pdf.bullet("Enjeu réglementaire : fournir les rapports d'insertion aux autorités de tutelle.")
    pdf.bullet("Enjeu managérial : fidéliser le réseau alumni pour les partenariats et le mentorat.")
    pdf.bullet("Enjeu technique : concevoir une architecture évolutive et conforme RGPD.")

    # Methodologie
    pdf.chapter_title("3", "Méthodologie et Démarche")
    pdf.section_title("3.1 Phase d'analyse (Semaines 1-2)")
    pdf.bullet("Étude du cahier des charges et des besoins fonctionnels.")
    pdf.bullet("Analyse des solutions existantes (CRM low-code vs développement sur mesure).")
    pdf.bullet("Choix technologique : FastAPI (Python) pour le backend, React + Vite pour le frontend, PostgreSQL pour la base de données.")
    pdf.bullet("Définition du modèle de données conceptuel (MCD) puis logique (MLD).")
    pdf.section_title("3.2 Phase de conception (Semaines 3-4)")
    pdf.bullet("Élaboration du MCD avec 14 tables : ETUDIANT, PROMOTION, ENTREPRISE, EXPERIENCE_PRO, CERTIFICATION, OBTIENT, CONSENTEMENT_RGPD, DEMANDE_RGPD, QUESTIONNAIRE, QUESTION, REPONSE_QUESTIONNAIRE, AUDIT_LOG, otp_codes, schema_migrations.")
    pdf.bullet("Mise en place des règles d'intégrité (clés étrangères, cascade, contraintes UNIQUE).")
    pdf.bullet("Prototype du schéma API (endpoints REST, authentification OTP + JWT).")
    pdf.section_title("3.3 Phase de développement (Semaines 5-10)")
    pdf.bullet("Développement itératif du backend (API REST complète, 82 endpoints).")
    pdf.bullet("Développement du frontend React (14 pages, composants partagés).")
    pdf.bullet("Intégration de la conformité RGPD (consentement, export, suppression, audit).")
    pdf.bullet("Validation fonctionnelle par tests manuels des parcours, scripts ad hoc d'exercice des routes réelles et rejeu complet des migrations sur base vide (aucune suite de tests automatisés conservée dans le dépôt).")
    pdf.section_title("3.4 Phase de consolidation (Semaines 11-12)")
    pdf.bullet("Revue de conformité par rapport au cahier des charges.")
    pdf.bullet("Documentation des rapports (cartographie, RGPD, indicateurs, stratégie).")
    pdf.bullet("Préparation du guide des processus d'animation du réseau.")

    pdf.section_title("3.5 Organisation du travail et ressources")
    pdf.body_text(
        "Ce stage est un stage de substitution, proposé directement par IONIS-STM aux étudiants "
        "n'ayant pas trouvé de placement en entreprise. La structure d'accueil est IONIS-STM elle-même "
        "et l'encadrement est assuré par un tuteur pédagogique interne."
    )
    pdf.body_text(
        "Le projet a été réalisé en solo : aucune équipe technique n'était dédiée au développement "
        "de l'Alumni CRM. L'ensemble des responsabilités — modélisation du MCD/MLD, développement "
        "du backend FastAPI, développement du frontend React, intégration de la conformité RGPD, "
        "audit de sécurité, rédaction des livrables documentaires — reposait sur un seul développeur. "
        "Cette organisation a rendu le projet formateur sur le plan de l'autonomie et de la prise de "
        "décision technique."
    )
    pdf.body_text(
        "Le suivi régulier avec le tuteur pédagogique a fourni un cadre de validation des choix "
        "d'architecture et des priorités fonctionnelles. Les points de suivi ont permis de poser un "
        "regard extérieur sur les choix techniques et d'aligner le développement avec les attendus "
        "du sujet de stage."
    )
    pdf.body_text(
        "Le projet était initialement stocké en local sous OneDrive avec synchronisation active, "
        "sans dépôt Git. Cette organisation a provoqué un incident : un conflit de synchronisation "
        "concurrente a entraîné le retour à une version antérieure de plusieurs fichiers frontend en "
        "cours de développement. Cet incident a conduit à l'initialisation d'un dépôt Git avec un "
        ".gitignore racine consolidé (couvrant .env, node_modules/, venv/). La leçon retenue est "
        "que le versionnement doit précéder la première ligne de code."
    )
    pdf.body_text(
        "Les ressources techniques comprenaient un poste de développement local, l'accès aux APIs "
        "tierces — en particulier Resend pour l'envoi d'emails OTP — et les polices système pour "
        "la mise en forme des documents."
    )
    pdf.body_text(
        "[A COMPLETER : informations complementaires sur les ressources materielles, frequence des "
        "points de suivi, modalites de communication utilisees]"
    )

    # Developpement technique
    pdf.chapter_title("4", "Développement Technique")
    pdf.section_title("4.1 Architecture générale")
    pdf.body_text(
        "Le système suit une architecture 3-tiers : un frontend React (SPA) communique avec un backend "
        "FastAPI via une API REST JSON, le tout lié à une base PostgreSQL. L'authentification alumni "
        "utilise un code OTP envoyé par email ; l'authentification admin utilise un code d'accès "
        "validé par API key. Un système JWT gère les sessions."
    )

    pdf.section_title("4.2 Modèle de données")
    pdf.body_text("Le schéma comprend 14 tables réparties en 5 domaines :")
    pdf.bullet("Données étudiantes : ETUDIANT, PROMOTION (lien N:1).")
    pdf.bullet("Parcours professionnel : ENTREPRISE, EXPERIENCE_PRO (lien N:1 avec ETUDIANT et ENTREPRISE), CERTIFICATION, OBTIENT (association N:M).")
    pdf.bullet("RGPD : CONSENTEMENT_RGPD, DEMANDE_RGPD (export/suppression), AUDIT_LOG.")
    pdf.bullet("Questionnaires : QUESTIONNAIRE, QUESTION (4 types : texte, choix multiple, boolean, rating), REPONSE_QUESTIONNAIRE (stockage JSON).")
    pdf.bullet("Infrastructure : otp_codes (authentification temporaire), schema_migrations (suivi des migrations).")
    pdf.body_text(
        "Les règles de cascade garantissent la cohérence : la suppression d'un étudiant entraîne la "
        "suppression CASCADE de ses expériences, certifications, consentements et réponses. Les demandes "
        "RGPD sont en SET NULL pour préserver l'historique même après anonymisation."
    )

    pdf.section_title("4.3 Backend API (FastAPI)")
    pdf.body_text("L'API expose 82 endpoints REST organisés en 16 routeurs montés (14 fichiers) :")
    pdf.bullet("Authentification : OTP send/verify, admin login, API key validation.")
    pdf.bullet("Gestion des promotions : CRUD complet.")
    pdf.bullet("Gestion des étudiants/alumni : CRUD + profil enrichi (jointures promotion, entreprise, expériences, certifications).")
    pdf.bullet("Entreprises et expériences pro : CRUD avec création automatique de l'entreprise si elle n'existe pas.")
    pdf.bullet("Certifications : catalogue + association N:M avec les étudiants.")
    pdf.bullet("RGPD : consentement (upsert), demandes (exports json/Excel/CSV, suppression/anonymisation), audit log.")
    pdf.bullet("Questionnaires : CRUD admin + soumission alumni avec validation des clés.")
    pdf.bullet("Dashboard admin : indicateurs, stats, filtrage alumni, évolution temporelle.")
    pdf.bullet("Import/Export : template Excel, import alumni protégé par clé API admin, export complet.")
    pdf.bullet("Newsletter et relances : envoi ciblé via POST /newsletter/envoyer (filtres promotion, secteur, consentement 'newsletter' actif ET 'prise_de_contact' non refusé) et rappels de questionnaire via POST /admin/questionnaires/notififier (ciblage des non-répondants, hors alumni ayant refusé 'enquetes' OU 'prise_de_contact', RGPD). Indicateurs partenaires : GET /admin/indicateurs/partenaires, périmètre restreint aux alumni ayant accepté 'partage_donnees' (données agrégées anonymisées).")
    pdf.bullet("Nettoyage : orphelins, doublons, archivage, purge différée.")

    pdf.section_title("4.4 Frontend React")
    pdf.body_text("Le frontend comprend 14 routes principales :")
    pdf.bullet("Espace Admin : Dashboard (KPI + graphiques), Annuaire filtrable, Promotions, Import/Export Excel, Questionnaires, Demandes RGPD.")
    pdf.bullet("Espace Alumni : Inscription multi-étapes, Vérification OTP, Profil (édition), Parcours (expériences + certifications), Consentement RGPD, Questionnaire annuel.")
    pdf.bullet("Composants partagés : ThemeToggle (clair/sombre), LoadingSpinner, KPICard, ErrorMessage, ProtectedRoute (garde de route par rôle).")

    # Resultats
    pdf.chapter_title("5", "Résultats et Livrables")
    pdf.section_title("5.1 Prototype fonctionnel")
    pdf.body_text(
        "Le système est opérationnel avec les fonctionnalités suivantes : inscription alumni, "
        "authentification OTP, gestion du profil, ajout d'expériences professionnelles et de "
        "certifications, questionnaire annuel, tableau de bord admin avec KPI, import/export Excel, "
        "gestion des consentements RGPD, demandes de suppression avec anonymisation automatique, "
        "calculs statistiques du salaire (moyenne, minimum, maximum) fondés sur le champ numérique salary_annuel."
    )
    pdf.section_title("5.2 Livrables documents")
    pdf.bullet("Cartographie des données : inventaire complet des données entrée/sortie avec charte RGPD intégrée.")
    pdf.bullet("Charte de conformité RGPD : 4 types de consentement, droits implémentés, modèle de données.")
    pdf.bullet("Stratégie de mise à jour : processus managériaux (questionnaire, newsletter, guide des processus).")
    pdf.bullet("Indicateurs d'insertion : modélisation des KPI et rapport ministériel standardisé.")
    pdf.bullet("Guide des processus d'animation du réseau : document séparé décrivant les flux opérationnels.")
    pdf.section_title("5.3 Schéma MCD/MLD")
    pdf.body_text(
        "Le modèle conceptuel et logique de données a été élaboré et validé. Le MLD comprend 14 tables "
        "avec les règles d'intégrité référentielle (clés étrangères, cascade, contraintes d'unicité). "
        "Le passage du MCD au MLD a été effectué en respectant les règles de transformation "
        "(entité forte -> table, association -> table de jonction ou FK)."
    )

    # Bilan
    pdf.chapter_title("6", "Bilan et Perspectives")
    pdf.section_title("6.1 Compétences acquises")
    pdf.body_text(
        "Ce stage m'a permis de développer des compétences techniques solides en développement web "
        "full-stack (Python/FastAPI, React/Vite, PostgreSQL), en migrations de base de données "
        "versionnées (règle retenue : une migration appliquée ne se modifie jamais, on corrige par "
        "une migration corrective) et en sécurité applicative (failles IDOR, race conditions "
        "éliminées par gestion des IntegrityError, garde centralisé sur les 12 points d'écriture "
        "touchant un compte anonymisé). J'ai également acquis une compréhension concrète des enjeux "
        "réglementaires (RGPD) dans un contexte éducatif, et une rigueur méthodologique : audit de "
        "cohérence par introspection SQL, écrit et daté avant tout correctif."
    )
    pdf.section_title("6.2 Difficultés rencontrées et solutions")
    pdf.bullet("Authentification croisée admin/alumni : les tokens partageaient la même clé de stockage, provoquant des erreurs 403 inexpliquées. Correction : clés de stockage distinctes, contrôle du rôle dans le JWT, purge automatique des sessions orphelines.")
    pdf.bullet("Dérive entre le modèle et la base réelle : des écarts de migration ont été détectés par introspection (clés étrangères, routes cassées, doublons). Solution : migrations correctives et rejeu complet des migrations sur base vide comme test de validation systématique.")
    pdf.bullet("Deux admins pouvaient traiter la même demande RGPD : ajout d'un statut intermédiaire 'en traitement' et verrou applicatif pour éviter le traitement parallèle.")
    pdf.bullet("Indicateur d'insertion trompeur : le taux d'emploi à 6 mois comptait des expériences terminées. Correction : filtrage sur les expériences actives à la date de référence, exclusion des cohortes immatures.")
    pdf.bullet("Absence de versionnement Git (incident OneDrive) : perte de fichiers sans historique. Solution : dépôt Git avec .gitignore consolidé. Leçon : versionner avant la première ligne de code.")

    # Axes d'amélioration
    pdf.chapter_title("7", "Axes d'amélioration")
    pdf.body_text(
        "Cette section recense les axes d'amélioration identifiés au cours du stage, hiérarchisés "
        "par horizon de réalisation."
    )

    pdf.section_title("7.1 Axes à traiter en priorité (court terme)")
    pdf.bullet("Tests automatisés : le principal chantier technique restant avant la mise en "
        "production est l'introduction durable d'une suite de tests (pytest côté backend, Vitest côté "
        "frontend), absente du dépôt à l'issue du stage. Quelques tests d'intégration auraient "
        "intercepté la route DELETE /entreprises cassée comme les endpoints renvoyant 200 OK avec un "
        "corps d'erreur. Le script de test E2E documenté dans le README n'est plus présent dans le "
        "dépôt et doit être reconstitué.")
    pdf.bullet("Automatisation de l'envoi du questionnaire annuel (cron job) : l'activation des "
        "questionnaires reste manuelle. Un mécanisme de planification automatique permettrait d'envoyer "
        "les relances email aux alumni n'ayant pas répondu. L'endpoint backend POST /admin/"
        "questionnaires/notififier est déjà implémenté ; il manque le déclenchement automatique "
        "périodique et une interface dédiée côté frontend.")
    pdf.bullet("Composant frontend d'envoi de newsletter : l'endpoint backend POST /newsletter/envoyer "
        "est opérationnel avec filtres de ciblage, mais le composant frontend permettant à "
        "l'administrateur de rédiger et d'envoyer la newsletter n'est pas encore développé. Le "
        "mécanisme de désinscription automatique (lien mettant le consentement à 'refusé') n'est pas "
        "non plus implémenté.")
    pdf.bullet("Standardisation des contraintes de validation : le statut des consentements dans la "
        "table CONSENTEMENT_RGPD reste libre (ni Literal côté API, ni CHECK côté base). La date "
        "d'obtention des certifications n'est pas validée. La mise en place de contraintes à la source "
        "est une bonne pratique à généraliser.")

    pdf.section_title("7.2 Évolutions fonctionnelles (moyen terme)")
    pdf.bullet("Module de mentorat : un système de mise en relation entre alumni seniors et étudiants "
        "actuels permettrait d'exploiter le réseau alumni à des fins pédagogiques. Il pourrait prendre "
        "la forme d'un système de candidatures et de parrainage, avec matching par secteur ou compétences.")
    pdf.bullet("Chiffrement applicatif des données sensibles : les données de consentement et les "
        "données personnelles ne font l'objet d'aucun chiffrement spécifique au niveau applicatif. "
        "L'ajout d'un chiffrement au repos renforcerait la protection en cas d'accès non autorisé.")
    pdf.bullet("Route de mise à jour d'une expérience professionnelle : la modification directe d'une "
        "expérience existante n'est pas disponible. L'alumni doit supprimer puis recréer. Une route "
        "PUT/PATCH dédiée et un formulaire de modification amélioreraient l'expérience utilisateur.")

    pdf.section_title("7.3 Perspectives à plus long terme")
    pdf.bullet("Application mobile : une application mobile dédiée permettrait aux alumni de mettre à "
        "jour leur profil depuis un smartphone, améliorant la fraîcheur des données collectées. Cette "
        "évolution suppose des compétences en développement mobile (React Native, Flutter) et un choix "
        "stratégique entre application native et progressive web app (PWA).")
    pdf.bullet("Tests end-to-end complets : le script de test E2E documenté dans le README (parcours "
        "alumni + parcours admin contre le vrai backend) a disparu du dépôt. Sa reconstitution et son "
        "exécution automatisée dans un pipeline d'intégration continue constitueraient un filet de "
        "sécurité essentiel avant la mise en production.")
    pdf.bullet("Notification de violation de données : la notification prévue par l'article 33 du "
        "RGPD n'est pas couverte par une fonctionnalité dédiée. L'ajout d'un mécanisme d'alerte "
        "automatisé pourrait être envisagé.")

    # Références
    pdf.chapter_title("8", "Références bibliographiques")

    pdf.section_title("Cadre réglementaire")
    pdf.bullet("Règlement (UE) 2016/679 du Parlement européen et du Conseil du 27 avril 2016 "
        "(RGPD).")
    pdf.bullet("Commission Nationale de l'Informatique et des Libertés (CNIL) — Guide pratique du "
        "RGPD : [A COMPLETER : URL si utilisée].")

    pdf.section_title("Documentation technique — Backend")
    pdf.bullet("FastAPI — Documentation officielle : https://fastapi.tiangolo.com/")
    pdf.bullet("Pydantic — Documentation : https://docs.pydantic.dev/")
    pdf.bullet("pg8000 — Documentation : [A COMPLETER : URL si référencée]")
    pdf.bullet("Python — Documentation officielle : https://docs.python.org/3/")

    pdf.section_title("Documentation technique — Frontend")
    pdf.bullet("React — Documentation officielle : https://react.dev/")
    pdf.bullet("Vite — Documentation officielle : https://vitejs.dev/")
    pdf.bullet("Vitest — Documentation : https://vitest.dev/")

    pdf.section_title("Documentation technique — Base de données")
    pdf.bullet("PostgreSQL — Documentation : https://www.postgresql.org/docs/")

    pdf.section_title("Référentiels et organismes de certification")
    pdf.bullet("Commission des Titres d'Ingénieur (CTI) — Référentiel d'accréditation : "
        "[A COMPLETER : URL ou référence exacte].")
    pdf.bullet("Haute Autorité pour l'Évaluation de la Recherche et l'Enseignement Supérieur "
        "(HCERES) — Référentiel d'évaluation : [A COMPLETER : URL ou référence exacte].")

    pdf.section_title("Services tierces")
    pdf.bullet("Resend — API email : https://resend.com/")

    pdf.section_title("Référence au groupe")
    pdf.bullet("IONIS Education Group — Site officiel : https://www.ionis-group.com/")

    pdf.section_title("Sources internes")
    pdf.bullet("Cahier des charges du sujet de stage — IONIS-STM, 2026.")
    pdf.bullet("Instructions Livrables & Soutenance 2026 v4 — IONIS-STM.")

    pdf.output(os.path.join(OUTPUT_DIR, "Rapport de Stage - Alumni CRM.pdf"))
    print("Rapport de stage genere.")


def generate_guide_animation():
    pdf = ReportPDF("Guide d'Animation du Reseau")
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_font("SegoeUI", "B", 20)
    pdf.set_text_color(30, 64, 175)
    pdf.cell(0, 12, "Guide des Processus d'Animation du Reseau Alumni", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("SegoeUI", "", 10)
    pdf.set_text_color(107, 114, 128)
    pdf.cell(0, 7, "Projet Alumni CRM - Ionis Education Group", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(10)

    # Introduction
    pdf.chapter_title("1", "Objectif du Guide")
    pdf.body_text(
        "Ce document decrit les processus operationnels pour animer et maintenir vivant le reseau "
        "des anciens eleves via l'Alumni CRM. Il s'adresse au service des Relations Entreprises et "
        "a l'equipe pedagogique. Chaque processus identifie les acteurs, les etapes, les outils "
        "utilises et les indicateurs de suivi."
    )

    # Processus 1 : Inscription
    pdf.chapter_title("2", "Processus d'Inscription et Collecte Initiale")
    pdf.section_title("2.1 Inscription de l'alumni")
    pdf.bullet("Declencheur : l'alumni accede au formulaire d'inscription (/alumni/register) apres l'obtention de son diplome.")
    pdf.bullet("Etapes : saisie des informations personnelles (nom, prenom, email, telephone, date de naissance), choix de la promotion, parcours anterieur, etablissement precedent, disponibilite (en_poste / a_lecoute / en_recherche), competences (skills), profil LinkedIn.")
    pdf.bullet("Validation : l'email academique est valide (domaine ionis-stm.com, construit automatiquement au format prenom.nom@ionis-stm.com). Le statut de disponibilite est obligatoire.")
    pdf.bullet("Creation du consentement RGPD : 4 toggles proposes lors de l'inscription (contact, partage de donnees, enquetes, newsletter). Chaque choix est enregistre avec la date et le canal ('web').")
    pdf.bullet("Outil CRM : formulaire AlumniRegistration.jsx -> endpoints POST /etudiants/ (profil) puis POST /consentements/ (4 toggles) -> tables ETUDIANT + CONSENTEMENT_RGPD.")
    pdf.section_title("2.2 Import en masse (admin)")
    pdf.bullet("Declencheur : le service recupere la liste officielle des admis (fichier Excel).")
    pdf.bullet("Etapes : telechargement du template Excel (/import/template), remplissage du fichier, import via l'interface (/admin/import). Validation Pydantic de chaque ligne.")
    pdf.bullet("Outil CRM : page ExcelImport.jsx -> endpoint POST /import/excel -> table ETUDIANT. Export complet inverse disponible via GET /import/export/alumni.")
    pdf.bullet("Controle : l'admin recoit un rapport d'erreur detaille par ligne en cas d'echec partiel.")

    # Processus 2 : Suivi de l'insertion
    pdf.chapter_title("3", "Processus de Suivi de l'Insertion Professionnelle")
    pdf.section_title("3.1 Mise a jour du parcours par l'alumni")
    pdf.bullet("Declencheur : l'alumni change de poste ou obtient une certification.")
    pdf.bullet("Etapes : acces a la page Parcours (/alumni/career), ajout/suppression d'une experience (entreprise, poste, secteur, contrat, dates, salaire, localisation), ajout de certifications (nom, organisme, date). La modification directe d'une experience existante n'est pas disponible a ce jour : il faut la supprimer puis la recreer (limite assumee du prototype). Ces mises a jour s'effectuent exclusivement depuis l'interface web ; aucune application mobile n'existe a ce jour.")
    pdf.bullet("Detection du poste actuel : si aucun poste n'est coche comme actuel, le systeme affiche automatiquement l'experience la plus recente. Une alerte ambrée est affichee si le statut est 'en_poste' mais aucun poste actuel n'est coche.")
    pdf.bullet("Outil CRM : page AlumniCareer.jsx -> endpoints POST /etudiants/{id}/experiences et /etudiants/{id}/certifications.")
    pdf.section_title("3.2 Enrichissement du referentiel secteurs")
    pdf.bullet("Declencheur : un alumni saisit un secteur non encore enregistre.")
    pdf.bullet("Etape : le systeme propose 37 categories standardisees + 'Autre' avec saisie libre.")
    pdf.bullet("Outil CRM : composant de selection dans AlumniCareer.jsx, constantes dans constants.js (tableau SECTORS).")

    # Processus 3 : Questionnaire annuel
    pdf.chapter_title("4", "Processus de Questionnaire Annuel")
    pdf.section_title("4.1 Creation du questionnaire (admin)")
    pdf.bullet("Declencheur : le service des Relations Entreprises definit le questionnaire annuel.")
    pdf.bullet("Etapes : creation via l'interface (/admin/questionnaires), ajout de questions (texte, choix multiple, boolean, rating), attribution de tags KPI (ex: 'adequation_formation'), definition des conditions (masquage si en_recherche).")
    pdf.bullet("Cycle de vie : creation -> activation -> desactivation -> reactivation. Un seul questionnaire peut etre actif a la fois.")
    pdf.bullet("Outil CRM : page AdminQuestionnaires.jsx -> endpoint POST /admin/questionnaires/.")
    pdf.section_title("4.2 Reponse par l'alumni")
    pdf.bullet("Declencheur : l'alumni recoit une notification (email ou rappel) l'invitant a repondre ; les relances email sont envoyees cote backend via POST /admin/questionnaires/notififier (ciblage des non-repondants du questionnaire actif, filtre par promotion ; RGPD : exclusion des alumni ayant refuse 'enquetes' OU 'prise_de_contact', sur le vote le plus recent), sans interface admin dediee pour cet envoi a ce jour.")
    pdf.bullet("Etapes : acces a la page Questionnaire (/alumni/survey), lecture des questions, pre-remplissage des reponses precedentes, soumission.")
    pdf.bullet("Validation : les questions non applicables (conditionnees au statut) sont masquees et enregistrees comme 'Non applicable'. Toutes les questions visibles doivent etre repondues.")
    pdf.bullet("Outil CRM : page AlumniSurvey.jsx -> endpoint POST /questionnaires/{id}/repondre -> table REPONSE_QUESTIONNAIRE.")
    pdf.section_title("4.3 Exploitation des resultats")
    pdf.bullet("Les reponses avec tag KPI alimentent automatiquement les indicateurs du tableau de bord admin.")
    pdf.bullet("L'admin peut consulter les reponses par questionnaire (/admin/questionnaires/{id}/reponses).")
    pdf.bullet("L'indicateur adequation formation/emploi est calcule automatiquement a partir des reponses taggees 'adequation_formation'.")

    # Processus 4 : Newsletter
    pdf.chapter_title("5", "Processus de Newsletter")
    pdf.section_title("5.1 Preparation")
    pdf.bullet("Ciblage : seuls les alumni ayant active le consentement 'newsletter' sont contactes.")
    pdf.bullet("Calendrier : mensuel ou bimestrielle, selon la capacite du service.")
    pdf.bullet("Contenu : actualites alumni, offres d'emploi partenaires, evenements, call-to-action (mise a jour du profil).")
    pdf.section_title("5.2 Envoi")
    pdf.bullet("Envoi : l'endpoint backend POST /newsletter/envoyer a ete implemente avec filtres de ciblage (promotion, secteur, consentement newsletter actif ET 'prise_de_contact' non refuse) ; mode console en dev, Resend en prod. Le composant d'envoi cote frontend n'est pas encore developpe (manque encore ouvert).")
    pdf.bullet("Personnalisation possible par promotion, secteur, geographie, disponibilite.")
    pdf.section_title("5.3 Suivi")
    pdf.bullet("Metriques : taux d'ouverture, taux de clic sur le CTA, taux de mise a jour du profil suite a l'envoi.")
    pdf.bullet("Desabonnement : le principe retenu est que le lien de desinscription mette a jour le consentement a 'refuse' ; ce mecanisme n'est pas encore implemente (liens placeholder dans le gabarit HTML — manque encore ouvert).")

    # Processus 5 : Animation du reseau
    pdf.chapter_title("6", "Processus d'Animation du Reseau")
    pdf.section_title("6.1 Valorisation du reseau via le tableau de bord")
    pdf.bullet("L'admin utilise l'annuaire filtrable (/admin/annuaire) pour identifier les alumni par entreprise, secteur, promotion ou competence.")
    pdf.bullet("Identification des opportunites de stages, de partenariats ou de mentorat via l'annuaire enrichi.")
    pdf.bullet("Filtrage par disponibilite : les alumni 'en_recherche' sont prioritaires pour les mises en relation.")
    pdf.bullet("Mentorat : un module dedie de mise en relation entre alumni seniors et etudiants actuels n'existe pas encore a ce jour ; ces mises en relation s'appuient aujourd'hui sur l'annuaire filtrable.")
    pdf.section_title("6.2 Entretiens de suivi")
    pdf.bullet("Le service peut planifier des entretiens de suivi avec les alumni pour alimenter le CRM.")
    pdf.bullet("Pendant l'entretien, l'agent met a jour le profil, les experiences et les certifications directement via l'interface admin.")
    pdf.section_title("6.3 Evenements alumni")
    pdf.bullet("Les evenements (reunions, conferences, portes ouvertes), planifies de facon recurrente (ex : trimestrielle), sont communiques via la newsletter.")
    pdf.bullet("L'objectif est de creer des occasions de rencontre entre alumni et etudiants actuels.")
    pdf.section_title("6.4 Partenariats entreprises")
    pdf.bullet("L'annuaire enrichi (entreprises, secteurs, postes) permet d'identifier les entreprises avec le plus d'alumni.")
    pdf.bullet("Ces donnees alimentent les discussions de partenariat avec les entreprises (offres de stages, d'alternance, de recrutement).")

    # Processus 6 : RGPD
    pdf.chapter_title("7", "Processus de Conformite RGPD")
    pdf.section_title("7.1 Gestion du consentement")
    pdf.bullet("L'alumni peut modifier ses preferences a tout moment via /alumni/consent.")
    pdf.bullet("Chaque modification est horodatee et liee au canal de collecte.")
    pdf.bullet("L'admin peut consulter l'etat du consentement via l'annuaire.")
    pdf.section_title("7.2 Demandes de suppression")
    pdf.bullet("L'alumni soumet une demande via /alumni/consent -> endpoint POST /rgpd/demandes.")
    pdf.bullet("L'admin recoit la demande dans l'interface (/admin/demandes-rgpd), la prend en charge, puis la traite (anonymisation du compte : email remplace par ANONYMISE_<id>@anonymise.io, PII efface).")
    pdf.bullet("Les comptes anonymises sont purges definitivement apres un delai configurable (defaut : 6 mois) via l'outil purge.py.")
    pdf.bullet("Anonymisation admin directe : POST /etudiants/{id}/anonymiser permet d'anonymiser un compte hors workflow de demande (meme logique _anonymiser_compte, tracee dans AUDIT_LOG).")
    pdf.section_title("7.3 Export de donnees")
    pdf.bullet("L'alumni peut telecharger ses donnees personnelles aux formats JSON, Excel (.xlsx) ou CSV via GET /rgpd/export (auto-service : l'identite provient du token JWT).")
    pdf.bullet("L'admin peut traiter une demande d'export via l'interface admin et telecharger les exports unitaires ou groupes aux memes formats (section 'Erreurs' incluse pour les comptes introuvables).")
    pdf.section_title("7.4 Audit")
    pdf.bullet("Toutes les operations sont tracees dans la table AUDIT_LOG avec l'acteur, l'action, les details et la date.")
    pdf.bullet("L'admin peut consulter le journal d'audit via GET /admin/cleanup/audit.")

    # Processus 7 : Nettoyage
    pdf.chapter_title("8", "Processus de Nettoyage et Maintenance")
    pdf.section_title("8.1 Detection des orphelins")
    pdf.bullet("Detection via GET /admin/cleanup/orphelins (previsualisation), suppression via DELETE /admin/cleanup/orphelins — experiences et certifications sans etudiant associe.")
    pdf.section_title("8.2 Fusion des doublons")
    pdf.bullet("Detection via GET /admin/cleanup/doublons, fusion via DELETE /admin/cleanup/doublons (entreprises en double, meme nom).")
    pdf.section_title("8.3 Archivage")
    pdf.bullet("Utilisation de l'endpoint POST /admin/cleanup/rgpd/archiver pour archiver (masquer) les donnees des alumni ayant refuse le consentement de prise de contact.")
    pdf.section_title("8.4 Purge differee")
    pdf.bullet("L'outil purge.py (CLI) supprime definitivement les comptes anonymises plus vieux que PURGE_DELAY_MONTHS (defaut : 6 mois).")
    pdf.bullet("Support du mode dry-run pour preview avant suppression reelle.")

    pdf.output(os.path.join(OUTPUT_DIR, "Guide des Processus - Animation du Reseau Alumni.pdf"))
    print("Guide d'animation du reseau genere.")


if __name__ == "__main__":
    generate_cartographie()
    generate_rgpd()
    generate_strategie()
    generate_indicateurs()
    generate_rapport_stage()
    generate_guide_animation()
    print("\nTous les rapports ont ete generes dans :", OUTPUT_DIR)

