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

    TABLE_LINE_H = 5.8
    TABLE_PAD_X = 1.8
    TABLE_BORDER = (196, 210, 226)
    TABLE_HEADER_FILL = (219, 234, 254)
    TABLE_BODY_FILL = (255, 255, 255)
    TABLE_BODY_FILL_ALT = (244, 247, 252)
    TABLE_HEADER_TEXT = (30, 41, 59)
    TABLE_TEXT = (55, 65, 81)

    def _normalize_widths(self, widths):
        total = self.w - self.l_margin - self.r_margin
        if abs(sum(widths) - total) > 0.01:
            scale = total / float(sum(widths))
            widths = [w * scale for w in widths]
        widths = [round(w, 2) for w in widths]
        widths[-1] = round(total - sum(widths[:-1]), 2)
        return widths

    def _draw_table_row(self, cols, widths, fill, bold=False, min_h=7.0, text_color=TABLE_TEXT):
        self.set_font("SegoeUI", "B" if bold else "", 10)
        self.set_text_color(*text_color)
        line_h = self.TABLE_LINE_H
        pad = self.TABLE_PAD_X
        x0 = self.get_x()
        y_start = self.get_y()

        heights = []
        for w, txt in zip(widths, cols):
            nb = self.multi_cell(w - 2 * pad, line_h, txt, border=0, split_only=True, padding=0)
            heights.append(len(nb) * line_h)
        row_h = max(heights) if heights else min_h
        row_h = max(row_h, min_h)

        self.set_draw_color(*self.TABLE_BORDER)
        self.set_line_width(0.2)
        self.set_fill_color(*fill)
        for i, (w, txt) in enumerate(zip(widths, cols)):
            cx = x0 + sum(widths[:i])
            self.rect(cx, y_start, w, row_h, style="FD")
            self.set_xy(cx + pad, y_start)
            self.multi_cell(w - 2 * pad, line_h, txt, border=0, padding=0)
        self.set_xy(x0, y_start + row_h)
        return row_h

    def table_header(self, cols, widths):
        self._t_cols = list(cols)
        self._t_widths = self._normalize_widths(list(widths))
        self._draw_table_row(self._t_cols, self._t_widths,
                             fill=self.TABLE_HEADER_FILL, bold=True, min_h=8.0,
                             text_color=self.TABLE_HEADER_TEXT)

    def table_row(self, cols, widths, fill=False):
        cols = list(cols)
        widths = self._normalize_widths(list(widths))
        line_h = self.TABLE_LINE_H
        pad = self.TABLE_PAD_X

        self.set_font("SegoeUI", "", 10)
        heights = []
        for w, txt in zip(widths, cols):
            nb = self.multi_cell(w - 2 * pad, line_h, txt, border=0, split_only=True, padding=0)
            heights.append(len(nb) * line_h)
        row_h = max(heights) if heights else 7.0
        row_h = max(row_h, 7.0)

        if self.get_y() + row_h > self.page_break_trigger - 1:
            self.add_page()
            if getattr(self, "_t_cols", None):
                self.table_header(self._t_cols, self._t_widths)

        self._draw_table_row(cols, widths,
                             fill=self.TABLE_BODY_FILL_ALT if fill else self.TABLE_BODY_FILL,
                             text_color=self.TABLE_TEXT)


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

    headers = ["Categorie", "Champs (Code)", "Description (simplifiee)", "Exemple"]
    widths = [31, 73, 58, 28]
    pdf.table_header(headers, widths)
    rows = [
        ["Identite et Coordonnees", "nom, prenom, email, telephone", "Identification unique de l'alumni.", "Alice Martin"],
        ["Identite et Coordonnees", "date_naissance", "Statistiques demographiques.", "1999-04-12"],
        ["Identite et Coordonnees", "email_academique", "Contact institutionnel (optionnel).", "alice@ionis-stm.com"],
        ["Identite et Coordonnees", "address, city, country", "Localisation geographique.", "Paris, France"],
        ["Identite et Coordonnees", "linkedin", "URL du profil LinkedIn.", "linkedin.com/in/alice"],
        ["Identite et Coordonnees", "availability_status", "Statut : en_poste, a_lecoute, en_recherche.", "en_recherche"],
        ["Identite et Coordonnees", "skills", "Competences techniques (tags).", "Python, SQL, DevOps"],
        ["Historique Academique", "parcours_anterieur", "Cursus suivi avant integration.", "BTS SIO"],
        ["Historique Academique", "previous_school (inscription)", "Etablissement precedent.", "Lycee Voltaire"],
        ["Rattachement Scolaire", "id_promotion -> nom_promotion, annee_diplome, filiere", "Lien PROMOTION (filtres promotion/filiere).", "Promo 2025, Data"],
        ["Donnees complementaires", "date_inscription", "Date de creation du profil.", "2023-09-01"],
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

    headers = ["Categorie", "Champs (Code)", "Description (simplifiee)", "Exemple"]
    widths = [41, 44, 73, 32]
    pdf.table_header(headers, widths)
    rows2 = [
        ["Suivi des Postes", "company (nom_entreprise)", "Entreprise employeuse.", "Capgemini"],
        ["Suivi des Postes", "position (intitule_poste)", "Intitule du poste.", "Developpeur Data"],
        ["Suivi des Postes", "type_contrat", "CDI, CDD, Freelance, Alternance, Stage...", "CDI"],
        ["Suivi des Postes", "start_date, end_date", "Periode du poste (mois annee).", "09/2024 - 06/2025"],
        ["Suivi des Postes", "is_current (poste_actuel)", "Poste occupe actuellement.", "true"],
        ["Suivi des Postes", "description", "Missions et responsabilites.", "Pipeline data, API"],
        ["Informations Salariales", "salary_range (salaire)", "Ancien champ texte (retrocomp.).", "35-45k EUR"],
        ["Informations Salariales", "salary_annuel (NUMERIC)", "Salaire brut annuel (chiffre).", "42000"],
        ["Geographie", "pays, ville", "Localisation de l'entreprise.", "France, Paris"],
        ["Secteur d'activite", "sector (secteur_activite)", "37 categories + Autre.", "Conseil"],
        ["Certifications", "name (nom_certification)", "Certification post-diplome.", "AWS Certified"],
        ["Certifications", "issuer (organisme)", "Organisme emetteur.", "Amazon AWS"],
        ["Certifications", "date_obtained", "Date d'obtention.", "2025-03-15"],
        ["Reponse Questionnaire", "reponses (JSON)", "Reponses enquetes annuelles.", "{\"salaire\": \"42k\"}"],
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

    headers3 = ["Champ", "Type / Valeurs", "Description (simplifiee)", "Exemple"]
    widths3 = [45, 51, 67, 27]
    pdf.table_header(headers3, widths3)
    rgpd_rows = [
        ["id_etudiant", "Entier (FK)", "Reference vers l\u0027alumni.", "42"],
        ["type_consentement", "4 types (voir 5.2)", "Nature de l\u0027autorisation.", "newsletter"],
        ["date_consentement", "Date (AAAA-MM-JJ)", "Date du recueil.", "2025-09-14"],
        ["statut", "actif | refuse", "Etat du consentement.", "actif"],
        ["canal", "web | questionnaire", "Origine de l\u0027accord.", "web"],
    ]
    for i, r in enumerate(rgpd_rows):
        pdf.table_row(r, widths3, fill=(i % 2 == 0))
    pdf.ln(4)

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
    headers_rgpd = ["Type (Backend)", "Cle Frontend", "Description (simplifiee)", "Exemple"]
    widths_rgpd = [27, 34, 74, 55]
    pdf.table_header(headers_rgpd, widths_rgpd)
    rgpd_types = [
        ["prise_de_contact", "contact_allowed", "Ecole / partenaires peuvent contacter.", "Offres de postes, evenements"],
        ["partage_donnees", "data_sharing", "Donnees statistiques anonymisees partagees.", "Secteur, poste"],
        ["enquetes", "survey_participation", "Participation aux enquetes alumni.", "Evolution carriere, satisfaction"],
        ["newsletter", "newsletter", "Reception de la newsletter.", "Actualites, offres d\u0027emploi"],
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

    headers = ["Type (Backend)", "Cle Frontend", "Description (simplifiee)", "Exemple"]
    widths = [27, 34, 74, 55]
    pdf.table_header(headers, widths)
    rows = [
        ["prise_de_contact", "contact_allowed", "Ecole / partenaires peuvent contacter.", "Offres de postes, evenements"],
        ["partage_donnees", "data_sharing", "Donnees statistiques anonymisees partagees.", "Secteur, poste"],
        ["enquetes", "survey_participation", "Participation aux enquetes alumni.", "Evolution carriere, satisfaction"],
        ["newsletter", "newsletter", "Reception de la newsletter.", "Actualites, offres d\u0027emploi"],
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

    headers2 = ["Champ", "Type", "Contraintes (simplifiees)", "Exemple"]
    widths2 = [44, 33, 87, 26]
    pdf.table_header(headers2, widths2)
    rows2 = [
        ["id_etudiant", "Entier (FK)", "REFERENCES ETUDIANT, NOT NULL.", "42"],
        ["type_consentement", "Enum / Chaine", "4 valeurs possibles.", "newsletter"],
        ["date_consentement", "Date", "NOT NULL, date du jour.", "2025-09-14"],
        ["statut", "Chaine", "actif (accorde) / refuse (retire).", "actif"],
        ["canal", "Chaine", "web | questionnaire.", "web"],
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

    headers = ["Indicateur", "Definition (simplifiee)", "Metier / Utilisation", "Exemple"]
    widths = [32, 76, 41, 41]
    pdf.table_header(headers, widths)
    rows = [
        ["Taux d'emploi a 6 mois", "Diplomes en activite 6 mois apres la sortie (CDI, CDD...).", "Rapports ministeriels et audits.", "Promo 2025 : 9/12 en poste = 75 %"],
        ["Taux d'emploi global (brut)", "(Alumni en poste / total alumni) x 100.", "Efficacite globale de la formation.", "30 alumni en poste / 40 = 75 %"],
        ["Adequation formation/emploi", "Correspondance filiere suivie / secteur du poste (question KPI).", "Pertinence de l'offre de formation.", "3 reponses Oui / 4 = 75 %"],
        ["Salaire moyen par filiere", "Salaire brut annuel moyen (AVG/MIN/MAX sur salary_annuel).", "Valorisation des debouches.", "38000+42000+50000 / 3 = 43 333 EUR"],
        ["Alumni actifs", "Alumni avec au moins une experience enregistree.", "Engagement des anciens eleves.", "45 alumni actifs sur 60"],
        ["Taux de completion", "Alumni avec profil + experience completes.", "Qualite des donnees collectees.", "32 profils complets / 60 = 53 %"],
        ["Alumni par promotion", "Effectif et taux d'emploi par promotion (ETUDIANT + PROMOTION).", "Comparatif des cohortes.", "2024 : 10 / 80 % ; 2025 : 12 / 75 %"],
        ["Repartition par secteur", "Nombre d'alumni par secteur d'activite.", "Debouches et secteurs recruteurs.", "Info 3, Finance 2, Sante 1"],
    ]
    for i, r in enumerate(rows):
        pdf.table_row(r, widths, fill=(i % 2 == 0))

    pdf.ln(4)

    # 3. Implementation technique
    pdf.chapter_title("3", "Implementation Technique des Indicateurs")
    pdf.section_title("3.1 Endpoints API")

    headers2 = ["Endpoint", "Description (simplifiee)", "Donnees retournees (extrait)"]
    widths2 = [35, 62, 93]
    pdf.table_header(headers2, widths2)
    rows2 = [
        ["GET /admin/indicateurs", "Indicateurs principaux du tableau de bord.", "total_alumni, taux_emploi_6mois, taux_couverture, alumni_actifs, taux_reponse, salaire_moyen/min/max."],
        ["GET /admin/indicateurs/secteurs", "Repartition par secteur d'activite.", "{secteur, count}, total_alumni."],
        ["GET /admin/indicateurs/types-contrat", "Repartition par type de contrat (des experiences en cours).", "{type_contrat, count} ; vides = 'Non renseigne'."],
        ["GET /admin/indicateurs/kpi-tag?tag=X", "Valeur d'un indicateur KPI (question taggee).", "valeur, unite (% ou moyenne), total_repondants, question_texte, distribution."],
        ["GET /admin/indicateurs/kpi-tags", "Tous les tags KPI des questionnaires actifs.", "[{tag, libelle, pourcentage, nb_repondants, valeur, unite, distribution}]."],
        ["GET /admin/indicateurs/kpi-tags-actifs", "Liste des tags DISTINCT utilises.", "{tags: [...]}"],
        ["GET /admin/indicateurs/partenaires", "Indicateurs anonymises pour les partenaires (partage_donnees actif).", "nb_consentants, taux_emploi_pourcentage, en_emploi, salaire_moyen, par_promotion, top_secteurs."],
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
    widths_info = [50, 140]
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
    headers_kpi = ["Indicateur", "Valeur attendue", "Calcul (simplifie)", "Exemple"]
    widths_kpi = [34, 48, 68, 40]
    pdf.table_header(headers_kpi, widths_kpi)
    kpi_rows = [
        ["Effectif de la promotion", "Nombre total d'inscrits", "COUNT(etudiants WHERE id_promotion = X)", "Promo 2025 : 128"],
        ["Taux d'emploi a 6 mois", "Pourcentage (%)", "Experience debutant <= 6 mois apres diplomation / total", "120 alumni : 90 en poste = 75 %"],
        ["Taux d'emploi a 12 mois", "Pourcentage (%) - non calcule a ce jour", "Identique avec une fenetre de 12 mois", "En cours de definition"],
        ["Taux d'insertion totale", "Pourcentage (%)", "Au moins 1 experience / total", "128 alumni : 101 en poste = 79 %"],
        ["Adequation formation-emploi", "Pourcentage (%)", "Reponses KPI / total repondants", "3 reponses Oui / 4 = 75 %"],
        ["Salaire moyen par filiere", "Euros (moyen, min, max)", "AVG/MIN/MAX salary_annuel (>0)", "38000+42000+50000/3 = 43333"],
        ["Repartition par secteur", "Tableau (secteur, %)", "COUNT(experiences WHERE secteur = X)", "Info 3 (33 %), Finance 2"],
        ["Repartition geographique", "Tableau (pays, ville, %)", "COUNT(alumni WHERE pays = X)", "France 8 (62 %), Maroc 3"],
    ]
    for i, r in enumerate(kpi_rows):
        pdf.table_row(r, widths_kpi, fill=(i % 2 == 0))
    pdf.ln(4)

    pdf.bullet("Frequence : annuelle, coincidant avec la campagne de collecte du questionnaire.")
    pdf.bullet("Destinataires : Ministere de l'Enseignement Superieur, organes de certification (CTI, HCERES), direction de l'etablissement.")
    pdf.bullet("Diffusion : via le tableau de bord admin (AdminDashboard.jsx) avec bouton d'export.")
    pdf.bullet("Archivage : chaque edition est horodatee et conservee pour audit de conformite.")

    pdf.section_title("5.4 Exemple de Tableau de Synthese par Promotion")
    headers_syn = ["Promotion", "Nb Alumni", "Emploi 6 mois", "Emploi 12 mois", "Adequation"]
    widths_syn = [33, 30, 47, 47, 33]
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

    # Résumé
    pdf.section_title("Résumé")
    pdf.body_text(
        "Ce rapport présente le travail réalisé dans le cadre du stage de substitution Pré-MSc 2026 "
        "au sein d'IONIS-STM : la conception et le développement d'un Alumni CRM, système de suivi "
        "du parcours étudiant et de valorisation du réseau des anciens diplômés. Le projet couvre "
        "l'ensemble du cycle de vie : modélisation des données (MCD/MLD, 14 tables), développement "
        "d'une application web complète (backend FastAPI, frontend React, base PostgreSQL), "
        "intégration de la conformité au RGPD, pilotage de l'insertion professionnelle par "
        "indicateurs, et livraison des documents du volet Management (cartographie des données, "
        "charte RGPD, stratégie de mise à jour, guide des processus)."
    )
    pdf.body_text(
        "L'application met à disposition un espace administrateur (tableau de bord, annuaire, "
        "gestion des promotions, import/export, questionnaires, demandes RGPD) et un espace alumni "
        "(inscription avec authentification OTP, profil, parcours professionnel, consentements, "
        "questionnaire annuel). Le prototype est complet et opérationnel, ses limites sont "
        "documentées et hiérarchisées en axes d'amélioration en vue d'une éventuelle mise en "
        "production."
    )

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
        "Ce positionnement est cohérent avec les pratiques des autres acteurs privés de "
        "l'enseignement supérieur, pour lesquels la valorisation des débouchés professionnels est "
        "devenue un argument décisif auprès des candidats comme des partenaires."
    )

    pdf.section_title("1.7 Analyse des solutions existantes et positionnement")
    pdf.body_text(
        "Avant le lancement du développement, une analyse des solutions existantes a été conduite. "
        "Deux grandes familles d'outils ont été étudiées : les CRM généralistes (Salesforce, HubSpot) "
        "et les plateformes low-code (Budibase, Appsmith). Ces solutions offrent des fonctionnalités "
        "de base de gestion de contacts, mais ne répondent pas spécifiquement aux besoins d'un "
        "établissement d'enseignement supérieur : le cycle de vie étudiant, le calcul automatique des "
        "taux d'insertion, la conformité RGPD intégrée au processus de collecte et la gestion des "
        "questionnaires annuels ne figurent pas dans leurs modules standards."
    )
    pdf.body_text(
        "À l'inverse, les solutions métiers spécialisées dans le suivi alumni existent mais impliquent "
        "un coût de licence élevé et une dépendance au fournisseur. Le choix d'un développement sur "
        "mesure s'est donc imposé pour trois raisons : le contrôle total sur la conformité RGPD (sans "
        "transfert de données vers un éditeur tiers), la maîtrise des algorithmes de calcul des "
        "indicateurs (qui doivent être transparents et auditables pour les organismes de tutelle), et "
        "l'absence de coût de licence pour un établissement de taille moyenne."
    )

    pdf.section_title("1.8 Méthodologie de conception et cycle itératif")
    pdf.body_text(
        "La démarche a suivi un cycle itératif en cinq phases : modélisation du MCD/MLD, "
        "développement du backend, développement du frontend, audit de sécurité, puis rédaction des "
        "livrables documentaires. Cette organisation itérative a permis de détecter tôt des "
        "incohérences de modélisation (par exemple le drift de migration sur "
        "reponse_questionnaire.id_etudiant) et de corriger les écarts entre le modèle et l'implémentation "
        "avant que le périmètre ne s'étende."
    )
    pdf.body_text(
        "Chaque itération se concluait par une validation fonctionnelle manuelle des parcours "
        "utilisateur, couvrant les deux profils (admin et alumni). Le rejeu complet des 16 migrations "
        "sur une base vide constituait le test d'intégration structurel. Cette discipline a révélé "
        "deux classes de problèmes : des routes fonctionnellement cassées (DELETE /entreprises/{id} "
        "renvoyant une erreur d'intégrité au lieu de la suppression en cascade prévue) et des "
        "endpoints renvoyant un statut 200 OK avec un corps d'erreur au lieu d'une véritable "
        "exception HTTP, masquant les fautes de frappe dans les requêtes."
    )
    pdf.body_text(
        "L'audit de sécurité, conduit en phase finale, a permis de corriger des failles "
        "d'authentification (routes admin non protégées), des failles d'autorisation (un alumni "
        "pouvant modifier les réponses d'un autre via IDOR) et des failles de validation (upload "
        "sans vérification d'extension ni de taille). Les correctifs ont été appliqués avant la "
        "rédaction des livrables, afin que le prototype reflète un niveau de sécurité cohérent avec "
        "les exigences du RGPD."
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

    pdf.section_title("2.3 Périmètre fonctionnel détaillé")
    pdf.body_text(
        "Le périmètre du prototype s'est structuré autour de deux espaces et de fonctionnalités "
        "transverses. Côté administration, l'application couvre le pilotage de l'insertion (tableau de "
        "bord avec KPI et graphiques), la gestion du référentiel (promotions, entreprises, "
        "certifications), l'annuaire filtrable, l'import/export de données, la gestion des "
        "questionnaires et le traitement des demandes RGPD. Côté alumni, elle couvre l'inscription "
        "multi-étapes avec vérification OTP, l'édition du profil, le parcours professionnel "
        "(expériences et certifications), la gestion des consentements et la réponse au questionnaire "
        "annuel."
    )
    pdf.body_text(
        "Trois fonctionnalités transverses traversent ces deux espaces : la conformité RGPD, appliquée "
        "à chaque collecte et chaque suppression ; les indicateurs d'insertion, alimentés aussi bien "
        "par les données de parcours que par les réponses aux questionnaires ; et l'animation du "
        "réseau, via la newsletter et les relances annuelles. Ce découpage garantit qu'aucune "
        "collecte n'échappe aux règles de consentement et que toutes les données utiles au pilotage "
        "sont disponibles pour le calcul des indicateurs."
    )

    pdf.section_title("2.4 Expression détaillée des besoins")
    pdf.body_text(
        "L'analyse des besoins a abouti à une liste hiérarchisée de fonctions attendues, classées en "
        "trois niveaux de priorité. Les besoins de premier niveau (obligatoires) couvrent la "
        "gestion des profils alumni et de leur parcours, le tableau de bord d'insertion, la "
        "conformité RGPD et l'import/export. Les besoins de second niveau (souhaitables) couvrent la "
        "newsletter, les questions conditionnelles et les indicateurs partenaires. Les besoins de "
        "troisième niveau (optionnels) concernent le mentorat et l'application mobile."
    )
    pdf.body_text(
        "Deux contraintes transverses ont structuré l'ensemble de la conception. La première est la "
        "contrainte réglementaire : toute donnée personnelle doit être collectée sur la base d'un "
        "consentement explicite, pouvoir être exportée et effacée, et toute opération sensible doit "
        "être tracée. La deuxième est la contrainte de fiabilité des indicateurs : un chiffre "
        "d'insertion affiché dans le tableau de bord doit être reproductible et vérifiable, ce qui a "
        "conduit à définir une source de données et une formule explicites pour chaque indicateur, "
        "et à privilégier l'affichage d'une valeur non disponible plutôt que d'un chiffre trompeur."
    )

    pdf.section_title("2.5 Contraintes, hypothèses et risques")
    pdf.body_text(
        "Plusieurs contraintes ont borné le périmètre du prototype. La contrainte de temps "
        "s'imposait naturellement puisque le stage était mené en parallèle de la formation Pré-MSc : "
        "le périmètre a donc été découpé en tranches fonctionnelles hiérarchisées, et les "
        "fonctionnalités jugées non essentielles (mentorat, application mobile) ont été reportées en "
        "axes d'amélioration plutôt que d'être livrées partiellement. La contrainte d'environnement "
        "portait sur l'absence de serveur de production dédié : le développement et la validation se "
        "sont faits en local, et le mode OTP « console » a remplacé l'envoi d'emails réel pour les "
        "tests."
    )
    pdf.body_text(
        "Les principales hypothèses formulées portaient sur la structure du référentiel : une "
        "école, un identifiant de promotion par année et programme, un référentiel de secteurs "
        "standardisé, et la présence d'un champ salaire annuel à des fins statistiques. Ces "
        "hypothèses, explicitées dès la phase d'analyse, sont documentées dans le modèle de données "
        "et le guide des processus afin que tout écart ultérieur soit tracé."
    )
    pdf.body_text(
        "Les risques identifiés ont été cartographiés et traités au fil du projet : risque de "
        "dérive entre le modèle et la base réelle (couvert par l'introspection et le rejeu des "
        "migrations), risque de fuite de secrets (couvert par le .gitignore et les variables "
        "d'environnement), risque de fuite d'informations via les messages d'erreur (couvert par "
        "leur sanitisation), et risque de chiffre d'insertion trompeur (couvert par un calcul "
        "contrôlé et l'affichage d'une valeur non disponible dans les cas douteux)."
    )

    pdf.section_title("2.6 Acteurs et principaux cas d'usage")
    pdf.body_text(
        "Le système identifie trois acteurs principaux. L'administrateur (service Relations "
        "Entreprises) pilote l'insertion, enrichit le référentiel, importe les listes d'admis, gère "
        "les questionnaires et traite les demandes RGPD. L'alumni gère son profil, son parcours "
        "professionnel, ses consentements et répond au questionnaire. Enfin, le tuteur pédagogique "
        "exerce un rôle de supervision et de validation des choix, sans utilisation directe des "
        "fonctionnalités métier."
    )
    pdf.body_text(
        "Les principaux cas d'usage couvrent : l'inscription d'un nouvel alumnus avec vérification "
        "OTP ; la consultation et la mise à jour du profil et du parcours ; la gestion des "
        "consentements ; la réponse au questionnaire annuel ; l'export des données personnelles ; "
        "la demande de suppression ; le suivi des indicateurs d'insertion par l'administrateur ; "
        "le filtrage de l'annuaire ; l'import en masse des admis ; la création et l'activation de "
        "questionnaires ; le traitement des demandes RGPD ; et l'envoi de newsletter. Chaque cas "
        "d'usage associe un acteur, un déclencheur, des étapes et l'outil CRM mobilisé, conformément "
        "au guide des processus d'animation du réseau."
    )

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

    pdf.section_title("3.6 Choix technologiques et arbitrages")
    pdf.body_text(
        "Le choix de la stack a été guidé par quatre critères : vitesse de développement, lisibilité "
        "du code, robustesse relationnelle et coût de maintenance. Les arbitrages suivants ont été "
        "effectués et documentés :"
    )
    pdf.bullet("Backend FastAPI (Python) : retenu pour sa rapidité de développement, sa validation intégrée via Pydantic et sa documentation automatique Swagger. Alternative écartée : Node.js/Express, jugé moins adapté à la validation de schémas métier complexes.")
    pdf.bullet("Base PostgreSQL : modèle relationnel robuste, support JSONB (compétences et réponses de questionnaire), transactions et contraintes d'intégrité. Le driver pg8000 (Python pur sans ORM) a été choisi pour sa simplicité, au prix de particularités documentées (sérialisation JSONB, RETURNING, pool artisanal).")
    pdf.bullet("Frontend React + Vite : expérience utilisateur fluide en SPA, écosystème riche, build rapide. Le ling et le build de production (oxlint, vite build) servent de garde-fous en l'absence de tests automatisés.")
    pdf.bullet("Migrations versionnées maison (run_migrations.py) : script SQL numéroté avec table de suivi schema_migrations, plutôt qu'un outil lourd (Alembic), pour rester simple et transparent. Le principe 'une migration appliquée ne se modifie jamais' est strictement respecté.")
    pdf.bullet("Envoi d'emails Resend : OTP et newsletter, avec un mode console en développement qui affiche le code dans les logs pour les tests locaux.")
    pdf.body_text(
        "Ces choix ont été régulièrement ré-interrogés au fil du stage. Par exemple, le remplacement "
        "des vérifications d'existence en deux temps (SELECT puis INSERT, vulnérables aux race "
        "conditions de type TOCTOU) par la gestion des erreurs d'intégrité a amélioré à la fois la "
        "sécurité et la performance, en réduisant le nombre d'allers-retours base de données."
    )

    pdf.section_title("3.7 Environnement et outils de développement")
    pdf.body_text(
        "L'environnement de développement reposait sur un poste de travail local. Le backend "
        "FastAPI s'exécutait dans un environnement virtuel Python dédié, avec uvicorn comme serveur "
        "de développement ; le frontend React était servi par le serveur de développement Vite sur "
        "le port 3000, avec un proxy redirigeant les requêtes /api vers le backend sur le port 8000. "
        "La base PostgreSQL était gérée localement, et les migrations étaient appliquées via un "
        "script Python dédié."
    )
    pdf.body_text(
        "À des fins de démonstration et de test, un jeu de données réaliste a été injecté dans la "
        "base de démonstration : trente-deux alumni répartis sur huit promotions, plus de trente "
        "entreprises, une cinquantaine d'expériences professionnelles, des certifications, les "
        "consentements associés et un questionnaire actif avec plus de vingt réponses. Ce jeu de "
        "données, insérable de façon rejouable grâce à un marqueur de boîte mail de démonstration, "
        "a permis d'illustrer de manière crédible le tableau de bord et les parcours utilisateur "
        "lors de la soutenance."
    )
    pdf.body_text(
        "L'ensemble des livrables documentaires (rapport de stage, indicateurs, charte, cartographie, "
        "stratégie, guide des processus) est généré par les scripts Python du dossier Rapport, ce qui "
        "garantit leur mise à jour cohérente et leur régénérabilité à tout moment. Cette approche de "
        "« documentation comme du code » a été adoptée dès le départ pour éviter les dérives entre le "
        "contenu du rapport et l'état réel du projet."
    )

    pdf.section_title("3.8 Démarche de recette et de validation")
    pdf.body_text(
        "La recette du prototype a été menée selon une démarche progressive, articulée autour de "
        "plusieurs niveaux de vérification. Au niveau structurel, le rejeu complet des seize "
        "migrations sur une base vierge a confirmé l'absence de différence structurelle par "
        "rapport au schéma de référence. Au niveau fonctionnel, les parcours utilisateur des deux "
        "profils ont été exercés manuellement et de façon reproductible, à l'aide de jeux de "
        "données de démonstration."
    )
    pdf.body_text(
        "Au niveau sécurité, l'audit d'introspection a croisé le schéma réel de la base, les "
        "routeurs FastAPI et les schémas Pydantic, afin de détecter les incohérences entre le "
        "modèle déclaré et l'implémentation réelle. Ces contrôles ont fait émerger des anomalies "
        "réelles (routes de suppression cassées, endpoints renvoyant un statut trompeur, écarts de "
        "migration), chacune corrigée puis consignée dans le rapport avec la solution retenue."
    )
    pdf.body_text(
        "La recette a été documentée dans le journal de bord du projet, qui trace l'ensemble des "
        "anomalies détectées, leur gravité, la correction appliquée et la leçon retenue. Cette "
        "démarche, bien que reposant majoritairement sur des contrôles manuels faute de suite de "
        "tests automatisés, a garanti un niveau de fiabilité cohérent avec les attentes d'un "
        "prototype de démonstration, et a identifié les points à automatiser en priorité avant "
        "une éventuelle mise en production."
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

    pdf.section_title("4.5 Authentification, sessions et sécurité")
    pdf.body_text(
        "Le système distingue strictement deux profils, avec des mécanismes d'authentification adaptés : "
        "les alumni s'authentifient par code OTP à 6 chiffres envoyé par email (mode console en "
        "développement, Resend en production), tandis que l'administrateur se connecte par un code "
        "d'accès comparé via un hash SHA-256. Les sessions reposent sur des jetons JWT, avec un "
        "maillage de sécurité sur l'ensemble des routes sensibles :"
    )
    pdf.bullet("Les routes /admin/*, l'import de fichiers et la newsletter sont protégées par une clé API (header X-API-Key).")
    pdf.bullet("Les sessions admin et alumni sont stockées sous des clés distinctes dans le navigateur, avec vérification du rôle contenu dans le JWT à chaque appel sensible et purge des sessions orphelines à la réception d'un 401.")
    pdf.bullet("Les routes accédant aux données d'un étudiant vérifient que l'appelant est bien le propriétaire du compte (require_owner_or_admin), corrigeant les failles de type IDOR.")
    pdf.bullet("Un garde centralisé (refuser_compte_anonymise) interdit toute écriture sur un compte anonymisé, sur les 12 points d'écriture concernés.")
    pdf.bullet("Les messages d'erreur renvoyés au client sont sanitaires (aucun détail d'exception), la protection repose sur des mises à jour de sécurité (rapport de sécurité des en-têtes, limites de taille d'upload, extension contrôlée).")

    pdf.section_title("4.6 Import / export de données")
    pdf.body_text(
        "L'automatisation de la saisie était un objectif explicite du sujet. Le module d'import/export "
        "permet à l'administration de charger une liste d'admis depuis un fichier Excel ou CSV, et "
        "d'exporter l'ensemble des alumni :"
    )
    pdf.bullet("Template Excel téléchargeable (GET /import/template) décrivant les colonnes attendues.")
    pdf.bullet("Import avec détection automatique du séparateur CSV, aperçu des dix premières lignes, coloration des en-têtes reconnus/ignorés et compte rendu détaillé par ligne en cas d'échec partiel.")
    pdf.bullet("Validation de chaque ligne via le schéma Pydantic avant insertion (au lieu d'insérer les valeurs brutes), préchargement des entreprises existantes en une seule requête pour éviter un SELECT par ligne.")
    pdf.bullet("Export complet (GET /import/export/alumni) et exports RGPD en auto-service (JSON, Excel, CSV) côté alumni, avec exports unitaires ou groupés côté administration.")

    pdf.section_title("4.7 Validation et qualité")
    pdf.body_text(
        "En l'absence de suite de tests automatisés conservée dans le dépôt, la validation s'est appuyée "
        "sur plusieurs dispositifs complémentaires : le rejeu complet des 16 migrations sur une base "
        "vide (aucune différence structurelle constatée), l'exercice manuel des parcours utilisateur "
        "des deux profils, un audit d'introspection SQL croisant le schéma réel avec les routers et les "
        "schémas Pydantic, et des scripts ad hoc exerçant les routes réelles via l'API HTTP. Ces "
        "dispositifs ont permis d'intercepter une route de suppression cassée et des endpoints renvoyant "
        "un statut 200 trompeur."
    )

    pdf.section_title("4.8 Parcours utilisateur détaillés")
    pdf.body_text(
        "Le prototype repose sur deux parcours principaux, dont l'exhaustivité est essentielle à la "
        "validité de la démonstration. Le parcours alumni commence par une inscription multi-étapes : "
        "saisie des informations personnelles, choix d'une promotion, puis vérification du code OTP "
        "envoyé par email. Une fois authentifié, l'alumni accède à quatre espaces : la consultation et "
        "la modification de son profil, la gestion de son parcours professionnel (ajout d'expériences "
        "et de certifications), la gestion de ses consentements RGPD, et la réponse au questionnaire "
        "annuel."
    )
    pdf.body_text(
        "Le parcours administrateur s'ouvre sur un tableau de bord synthétisant les indicateurs clés "
        "sous forme de cartes et de graphiques. À partir de cet écran, l'administrateur navigue vers "
        "l'annuaire filtrable, la gestion des promotions, l'import/export de données, la gestion des "
        "questionnaires et le suivi des demandes RGPD. La cohérence des rôles est assurée à chaque "
        "étape par le garde ProtégedRoute côté frontend et par les dépendances role sur les endpoints "
        "côté backend."
    )
    pdf.body_text(
        "Le cycle de vie d'une demande RGPD illustre la robustesse du modélisation : un alumni effectue "
        "une demande de suppression depuis son espace personnel ; la demande apparaît avec le statut "
        "'envoyée' dans le tableau de bord admin ; un administrateur la prend en charge (statut 'en "
        "cours de traitement'), ce qui verrouille la demande contre tout traitement parallèle ; la "
        "validation de la prise en charge déclenche l'anonymisation automatique du compte et le statut "
        "'traitée'. L'alumni ne peut plus écrire sur son compte anonymisé, mais ses données conservées "
        "continuent d'alimenter les statistiques agrégées. Un journal d'audit retrace chaque "
        "changement d'état."
    )
    pdf.body_text(
        "Le cycle annuel du questionnaire suit un déroulement similaire : l'administrateur crée un "
        "questionnaire et ses questions, l'active, puis les alumni y répondent depuis leur espace "
        "personnel. La soumission est validée par le backend (les clés doivent correspondre aux "
        "questions du questionnaire) et les réponses alimentent les indicateurs par le biais des tags "
        "KPI. L'endpoint de relance POST /admin/questionnaires/notififier cible les non-répondants, "
        "hors alumni ayant refusé les enquêtes, dans le respect du RGPD."
    )

    pdf.section_title("4.9 Gamme d'endpoints et répartition")
    pdf.body_text(
        "Les 82 endpoints applicatifs recensés se répartissent en 60 chemins et par méthode HTTP : "
        "35 opérations GET (lectures et filtrages), 27 opérations POST (créations, soumissions, "
        "authentification), 4 opérations PUT, 3 opérations PATCH et 13 opérations DELETE. Cette "
        "répartition reflète une API riche et conforme aux conventions REST : chaque ressource "
        "fondamentale (promotions, étudiants, entreprises, expériences, certifications, "
        "questionnaires) dispose d'un CRUD complet, tandis que les actions métier (envoi d'OTP, "
        "soumission de questionnaire, traitement des demandes RGPD, import/export, newsletter) sont "
        "modélisées comme des POST dédiés."
    )
    pdf.section_title("4.10 Structure du dépôt et organisation du code")
    pdf.body_text(
        "Le dépôt s'organise en trois dossiers principaux. Le dossier backend alumni_crm_api regroupe "
        "le point d'entrée main.py (montage des 16 routeurs), le dossier routers contenant les 14 "
        "fichiers de routes, la configuration config.py (variables d'environnement, secrets), les "
        "helpers métier et le dossier migrations avec les 16 scripts SQL versionnés. Le dossier "
        "frontend alumni_crm_front contient le code React (Vite), l'arborescence des composants, les "
        "pages métier par rôle, les utilitaires API et les gestionnaires d'authentification. Enfin, "
        "le dossier Racine du projet contient la documentation, les livrables et les scripts de "
        "génération de rapports."
    )
    pdf.body_text(
        "Le fichier .env centralise les variables de configuration : accès PostgreSQL, clé API admin, "
        "clé Resend et mode d'envoi d'emails. Le .env.example fournit un gabarit sans secrets, "
        "conformément à la bonne pratique de ne jamais versionner de données sensibles. Le mode OTP "
        "console, activé en développement, affiche les codes dans les logs du serveur, ce qui permet "
        "de tester le parcours d'inscription sans dépendre d'un service d'emails externe."
    )

    pdf.section_title("4.11 Mise en œuvre détaillée de la conformité RGPD")
    pdf.body_text(
        "La conformité au RGPD ne se limite pas à un écran de consentement : elle imprègne le modèle "
        "de données, les flux et les interfaces. Elle repose sur quatre piliers mis en œuvre "
        "concrètement dans le prototype."
    )
    pdf.body_text(
        "Le premier pilier est le consentement explicite et conforme. La table CONSENTEMENT_RGPD "
        "stocke, pour chaque étudiant et chaque type de consentement (prise de contact, partage des "
        "données partenaires, enquêtes, newsletter), la valeur (1/0), la date associée et le canal de "
        "collecte. Le choix est proposé au moment de l'inscription mais reste modifiable à tout moment "
        "depuis l'espace alumni. L'information de l'alumni est garantie par un texte de politique de "
        "confidentialité indiquant la durée de conservation et le contact du délégué à la protection "
        "des données."
    )
    pdf.body_text(
        "Le deuxième pilier est l'exercice des droits des personnes. Le droit d'accès et la "
        "portabilité sont assurés par un export en auto-service : l'alumni peut télécharger, depuis "
        "son espace personnel, l'ensemble de ses données personnelles au format JSON, Excel ou CSV. "
        "Le droit à l'effacement est mis en œuvre via une demande de suppression, dont le traitement "
        "par l'administration peut aboutir à une anonymisation ou à une suppression définitive."
    )
    pdf.body_text(
        "Le troisième pilier est la traçabilité des traitements. La table AUDIT_LOG consigne les "
        "opérations sensibles (accès, modification, suppression), et chaque demande RGPD suit un "
        "workflow d'états (envoyée, en cours, traitée, rejetée) dont les changements sont journalisés. "
        "Le quatrième pilier est la purge des données : les comptes anonymisés sont conservés pour les "
        "statistiques agrégées mais purgés après un délai configurable (6 mois par défaut) par "
        "l'outil purge.py, avec mode dry-run pour valider l'impact avant application."
    )
    pdf.section_title("4.12 Développement du tableau de bord et des indicateurs")
    pdf.body_text(
        "Le tableau de bord constitue la vitrine de l'application pour le pilotage de l'insertion. "
        "Il agrège, en une seule page, plusieurs cartes KPI (alumni total, taux d'emploi, salaire "
        "moyen, taux de complétion, etc.) et des graphiques d'évolution (nouvelles inscriptions par "
        "période, répartition par promotion ou par secteur). Les données sont servies par des "
        "endpoints dédiés qui effectuent les agrégations SQL directement en base, plutôt que de "
        "transférer l'ensemble des lignes au frontend pour un traitement en mémoire."
    )
    pdf.body_text(
        "Le calcul d'un indicateur suit un principe de reproductibilité : chaque indicateur est "
        "défini par une formule et une source de données explicites. Par exemple, le taux d'emploi "
        "à 6 mois n'est calculé que sur les expériences actives à la date de référence, et les "
        "cohortes trop récentes pour être significatives sont exclues du calcul (le taux affiché "
        "vaut alors « non disponible »). Les indicateurs issus du questionnaire exploitent les "
        "tags KPI attribués aux questions, ce qui permet d'ajouter un nouvel indicateur sans "
        "modifier le code backend."
    )
    pdf.body_text(
        "L'interface AdminDashboard est alimentée par plusieurs appels parallèles et gère les états "
        "de chargement et d'erreur avec des composants réutilisables (LoadingSpinner, ErrorMessage). "
        "Les filtres de l'annuaire (nom, promotion, secteur, statut, disponibilité) sont appliqués "
        "via des paramètres de requête, et l'annuaire propose un affichage en cartes ou en tableau."
    )

    pdf.section_title("4.13 Gestion des erreurs, journalisation et maintenance")
    pdf.body_text(
        "Une attention particulière a été portée à la qualité des retours applicatifs. Le principe "
        "retenu est de ne jamais mentir au client : un endpoint qui échoue doit renvoyer une "
        "véritable exception HTTP avec le statut approprié (400, 404, 409, 422, 500), et non un statut "
        "200 avec un corps d'erreur. Ce principe, appliqué après la détection de plusieurs endpoints "
        "trompeurs, améliore nettement la fiabilité des diagnostics autant côté client que lors des "
        "tests."
    )
    pdf.body_text(
        "La gestion centralisée des erreurs du pilote pg8000 a été encapsulée dans des helpers : "
        "analyse des IntegrityError (contrainte violée ou doublon), gestion des RETURNING (absence "
        "d'ID automatique côté serveur), et sérialisation JSONB uniforme. Ces helpers évitent la "
        "duplication de logique fragile et garantissent un comportement cohérent sur l'ensemble des "
        "16 routeurs."
    )
    pdf.body_text(
        "La maintenance du schéma repose sur un principe strict : une migration appliquée ne se "
        "modifie jamais. Les évolutions se font exclusivement par des migrations correctives "
        "incrémentales, et le rejeu complet des migrations sur une base vide sert de test "
        "structurel systématique. Cette discipline, associée à l'utilisation de variables "
        "d'environnement pour tous les secrets, rend l'application déployable et maintenable dans "
        "la durée."
    )

    pdf.section_title("4.14 Installation et mise en route")
    pdf.body_text(
        "Le déploiement du prototype en local suit une procédure documentée dans le README. Après "
        "la création de la base PostgreSQL et le renseignement du fichier .env (copié depuis "
        ".env.example), les migrations sont appliquées via le script de migration, puis le backend "
        "est lancé avec uvicorn et le frontend avec le serveur de développement Vite. Le "
        "proxy configuré dans vite.config.js (port 3000 → port 8000) permet d'atteindre l'API "
        "sans configuration CORS supplémentaire en développement."
    )
    pdf.body_text(
        "Quelques points d'attention ont été consignés pour une mise en production ultérieure : "
        "la rotation de la clé API administrateur avant tout déploiement public, l'activation du "
        "mode d'envoi d'emails réel (Resend) à la place du mode console, la configuration d'un "
        "serveur PostgreSQL de production avec sauvegardes régulières, la planification des tâches "
        "de purge et de relance, et l'ajout d'un reverse proxy avec le protocole HTTPS. Ces points "
        "sont détaillés dans les axes d'amélioration."
    )

    pdf.section_title("4.15 Sécurité applicative détaillée")
    pdf.body_text(
        "L'audit de sécurité mené en phase finale a identifié et corrigé plusieurs classes de "
        "failles, dont voici la synthèse. En matière d'authentification, toutes les routes "
        "d'administration sont protégées par une clé API, les sessions reposent sur des JWT "
        "signés, et les mots de passe temporaires (OTP) sont à usage unique et expirants."
    )
    pdf.body_text(
        "En matière d'autorisation, les failles d'accès inter-utilisateurs de type IDOR ont été "
        "corrigées : chaque route accédant aux données d'un étudiant vérifie que l'appelant est "
        "bien le propriétaire du compte (sauf rôle administrateur). Un garde centralisé bloque "
        "toute écriture sur un compte anonymisé, sur les douze points d'écriture concernés, "
        "empêchant qu'une donnée « supprimée » soit accidentellement réécrite."
    )
    pdf.body_text(
        "En matière de validation des entrées, l'upload n'accepte désormais que des extensions "
        "autorisées avec une limite de taille maximale (5 Mo), et chaque ligne de l'import est "
        "validée par un schéma Pydantic avant insertion. En matière de confidentialité, les "
        "messages d'erreur renvoyés au client sont sanitaires (aucun détail d'exception interne), "
        "le détail étant conservé dans les logs serveur uniquement."
    )
    pdf.body_text(
        "Enfin, une vigilance particulière a porté sur la gestion des secrets : aucun identifiant "
        "ou mot de passe ne figure en dur dans le code (variables d'environnement via config.py), "
        "le fichier .env est exclu du versionnement par le .gitignore, et la rotation régulière "
        "des clés d'accès est documentée avant toute mise en production."
    )

    pdf.section_title("4.17 Performance et volumétrie")
    pdf.body_text(
        "Les choix d'implémentation ont pris en compte la montée en charge probable d'un annuaire "
        "d'anciens. Le transfert de l'agrégation des indicateurs vers le serveur de base de données "
        "(plutôt que le chargement de toutes les lignes en mémoire côté frontend) limite la "
        "quantité de données transitant sur le réseau et permet au moteur PostgreSQL d'optimiser "
        "les calculs via ses index et son optimiseur de requêtes."
    )
    pdf.body_text(
        "Les consultations de l'annuaire et du profil enrichi reposent sur des jointures contrôlées "
        "entre les tables ETUDIANT, PROMOTION, ENTREPRISE, EXPERIENCE_PRO et CERTIFICATION, avec une "
        "sélection des colonnes utiles plutôt qu'un SELECT * systématique. La table otp_codes, dont "
        "les lignes sont temporaires, est destinée à être purgée régulièrement pour éviter "
        "l'accumulation. Ces dispositions assurent des temps de réponse confortables pour le "
        "volume cible de quelques centaines de diplômés par promotion, tout en laissant la place "
        "à une optimisation (indexation complémentaire, agrégats matérialisés) si l'usage "
        "devenait plus intensif."
    )

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
    pdf.body_text(
        "Les tables du modèle se répartissent en cinq domaines. Le domaine « données étudiantes » "
        "comprend les tables ETUDIANT et PROMOTION : un étudiant appartient à une promotion (relation "
        "N:1), chaque promotion étant identifiée par son année et son programme. Le domaine « parcours "
        "professionnel » comprend ENTREPRISE, EXPERIENCE_PRO et CERTIFICATION, reliées à l'étudiant, "
        "ainsi que la table de jonction OBTIENT pour l'association N:M entre étudiants et certifications."
    )
    pdf.body_text(
        "Le domaine RGPD comprend CONSENTEMENT_RGPD (un enregistrement par type de consentement et "
        "par étudiant, avec date et canal), DEMANDE_RGPD (workflow des demandes de suppression avec "
        "ensemble de statuts contraint) et AUDIT_LOG (trace des opérations sensibles). Le domaine "
        "questionnaires comprend QUESTIONNAIRE, QUESTION (avec un champ pour les 4 types de réponse) "
        "et REPONSE_QUESTIONNAIRE, dont le contenu est stocké en JSON pour absorber la variété des "
        "types de questions. Enfin, le domaine infrastructure comprend otp_codes (codes d'authentification "
        "temporaires) et schema_migrations (suivi des versions du schéma)."
    )
    pdf.body_text(
        "Ce découpage a été choisi pour séparer les préoccupations : les données de parcours sont "
        "indépendantes des données de consentement, ce qui permet une gestion fine du RGPD sans "
        "impacter le calcul des indicateurs. Le stockage JSON des réponses de questionnaire, bien que "
        "moins relationnel, a été retenu pour sa flexibilité face à des questionnaires dont le "
        "contenu évolue chaque année. À l'inverse, les associations N:M (étudiants-certifications) "
        "sont matérialisées par une table de jonction, garantissant l'intégrité référentielle."
    )
    pdf.section_title("5.4 Indicateurs d'insertion professionnelle")
    pdf.body_text(
        "La mission Indicateurs a consisté à modéliser les rapports d'insertion demandés par les "
        "autorités de tutelle (ministères, organismes de certification) et à les automatiser dans le "
        "tableau de bord. Huit indicateurs ont été définis, chacun avec une formule et une source de "
        "données précise, afin que le chiffre affiché soit reproductible et vérifiable :"
    )
    pdf.bullet("Taux d'emploi à 6 mois : proportion des diplômés en activité six mois après l'obtention du diplôme. Calcul fondé sur la table EXPERIENCE_PRO, en ne retenant que les expériences actives à la date de référence.")
    pdf.bullet("Taux d'emploi global brut : (alumni ayant au moins une expérience / total des alumni) x 100. Source : tables ETUDIANT et EXPERIENCE_PRO.")
    pdf.bullet("Adéquation formation/emploi : proportion de réponses positives à la question taggée 'adequation_formation' dans le questionnaire annuel.")
    pdf.bullet("Salaire moyen / minimum / maximum : statistiques calculées sur le champ numérique salary_annuel, avec repli sur le champ texte historique lorsque la valeur annuelle est absente.")
    pdf.bullet("Alumni actifs : nombre d'alumni ayant au moins une expérience enregistrée.")
    pdf.bullet("Taux de complétion : proportion d'alumni ayant complété leur profil et leur parcours professionnel.")
    pdf.bullet("Alumni par promotion : répartition par id_promotion, avec notion de maturité des cohortes.")
    pdf.bullet("Répartition par secteur : agrégation du champ secteur_activite des entreprises.")
    pdf.body_text(
        "Un effort particulier a porté sur la fiabilisation du taux d'emploi à 6 mois. Un calcul trop "
        "simple comptait des expériences déjà terminées, ce qui surestimait les résultats pour les "
        "promotions récentes. Le calcul retenu ne retient que les expériences actives à la date de "
        "référence et exclut les cohortes trop récentes (valeur 'null' plutôt qu'un chiffre trompeur). "
        "Le système de tags KPI permet par ailleurs d'ajouter de nouveaux indicateurs d'enquête sans "
        "modifier le code backend : étiqueter une question suffit à faire apparaître l'indicateur "
        "correspondant dans le tableau de bord."
    )
    pdf.section_title("5.5 Conformité RGPD")
    pdf.body_text(
        "La conformité au Règlement général sur la protection des données a été intégrée dès la "
        "conception, et non ajoutée a posteriori. Quatre axes ont été traités :"
    )
    pdf.bullet("Consentement : quatre types de consentement gérés de façon indépendante (prise de contact, partage de données partenaires, enquêtes, newsletter). Chaque choix est horodaté, lié à un canal ('web') et réellement consommé par le reste du système.")
    pdf.bullet("Droits des personnes : droit d'accès et de portabilité via un export en auto-service (JSON, Excel ou CSV) côté alumni, et droit à l'effacement via une demande de suppression traitée par l'administration.")
    pdf.bullet("Anonymisation vs suppression : l'anonymisation (masquage des données personnelles tout en conservant un compte pour les statistiques) est distinguée de la suppression définitive, réservée aux doublons ou erreurs.")
    pdf.bullet("Traçabilité : un journal d'audit (AUDIT_LOG) enregistre les opérations sensibles, et les demandes RGPD suivent un workflow verrouillé (envoyée, en cours de traitement, traitée, rejetée) empêchant le traitement parallèle par deux administrateurs.")
    pdf.body_text(
        "La purge différée des comptes anonymisés (délai configurable, 6 mois par défaut) est traitée "
        "par l'outil purge.py avec un mode dry-run. L'interface de consentement informe l'alumni de la "
        "durée de conservation et du contact du délégué à la protection des données."
    )
    pdf.section_title("5.6 Volet Management - Gouvernance des données")
    pdf.body_text(
        "Le sujet prévoyait un volet Management complémentaire au développement informatique. Celui-ci "
        "a été traité sous la forme de quatre livrables documentaires, générés par script et donc "
        "régénérables et maintenables :"
    )
    pdf.bullet("Cartographie des données : inventaire des données collectées à l'entrée (coordonnées, parcours antérieur) et à la sortie (entreprises, postes, salaires), avec leur classification RGPD.")
    pdf.bullet("Charte RGPD : règlement intérieur encadrant le traitement des données des anciens, les durées de conservation et les canaux de contact autorisés.")
    pdf.bullet("Stratégie de mise à jour des données : processus managériaux (questionnaire annuel automatisé, newsletter) destinés à lutter contre la péremption rapide d'un annuaire d'anciens.")
    pdf.bullet("Analyse des indicateurs : modélisation des KPI et exemple structuré de rapport ministériel d'insertion.")
    pdf.bullet("Guide des processus d'animation du réseau : à destination du service Relations Entreprises, décrivant sept processus opérationnels (inscription, suivi d'insertion, questionnaire, newsletter, animation, conformité, maintenance).")
    pdf.body_text(
        "Cette gouvernance répond directement à la difficulté intrinsèque d'un annuaire d'anciens : "
        "ses données périment vite. Le couplage entre l'application (collecte) et ces processus "
        "(relance) vise à maintenir la fraîcheur des données dans la durée."
    )

    pdf.section_title("5.7 Fonctionnalités du prototype par module")
    pdf.body_text(
        "Le prototype peut être présenté selon quatre modules complémentaires. Le module "
        "« Administration » offre le tableau de bord (KPI, graphiques d'évolution, répartition), "
        "l'annuaire filtrable, la gestion des promotions et des entreprises, l'import/export et la "
        "gestion des questionnaires. Chaque écran est conçu pour réduire le temps de traitement "
        "administratif : l'annuaire autorise une recherche multicritère en temps réel, et "
        "l'import Excel évite la saisie manuelle ligne à ligne."
    )
    pdf.body_text(
        "Le module « Espace alumni » permet à un ancien élève d'accomplir l'ensemble de ses démarches "
        "en autonomie : s'inscrire avec vérification OTP, renseigner son profil et son parcours, "
        "gérer ses consentements, répondre au questionnaire annuel ou demander la suppression de ses "
        "données. Cette autonomie décharge le service Relations Entreprises d'une partie du travail "
        "de mise à jour."
    )
    pdf.body_text(
        "Le module « RGPD » traite les droits des personnes : export en auto-service, demande de "
        "suppression avec workflow, anonymisation automatique, journal d'audit et purge différée. "
        "Le module « Indicateurs » alimente le pilotage avec huit KPI reproductibles, appuyés sur "
        "des formules et des sources de données documentées, et ouvre la possibilité de rapports "
        "ministériels standardisés et d'indicateurs partenaires agrégés."
    )
    pdf.section_title("5.8 Jeu de données de démonstration")
    pdf.body_text(
        "Pour rendre la démonstration du prototype crédible et illustrer les parcours avec des "
        "données réalistes, un jeu de données de démonstration a été élaboré et injecté dans la base : "
        "trente-deux alumni fictifs répartis sur huit promotions, trente-quatre entreprises, plus de "
        "cinquante expériences professionnelles, des certifications, les consentements RGPD associés, "
        "et un questionnaire actif comptant six questions et plus de vingt réponses."
    )
    pdf.body_text(
        "Ce jeu de données est insérable de façon rejouable grâce à un marqueur de boîte mail de "
        "démonstration (domaine @demo-alumni-crm.io), ce qui permet de reconstituer un environnement "
        "de démonstration propre en quelques secondes, sans risquer de polluer la base réelle. Les "
        "captures d'écran présentées en annexe (B et C) ont été réalisées sur la base de ces données, "
        "garantissant la cohérence entre le contenu affiché à l'écran et le texte du rapport."
    )

    pdf.section_title("5.9 Revue de conformité au cahier des charges")
    pdf.body_text(
        "Une revue finale a confronté les livrables aux exigences du sujet de stage. Chaque "
        "fonctionnalité attendue a été vérifiée fonctionnellement, et le résultat est consigné ici :"
    )
    pdf.bullet("Suivi du parcours étudiant : fonctionnel (profil, expériences, certifications, promotion) — réalisé.")
    pdf.bullet("Valorisation du réseau des anciens : fonctionnelle (annuaire, espace alumni, newsletter backend) — réalisé.")
    pdf.bullet("Tableau de bord avec indicateurs d'insertion : fonctionnel (8 KPI reproductibles, graphiques) — réalisé.")
    pdf.bullet("Conformité RGPD : fonctionnelle (consentement, export, suppression, anonymisation, audit, purge) — réalisé.")
    pdf.bullet("Import/export automatisé : fonctionnel (template, import validé, exports JSON/Excel/CSV) — réalisé.")
    pdf.bullet("Schéma MCD/MLD : livré (14 tables, règles d'intégrité) — réalisé.")
    pdf.bullet("Volet Management : livré (cartographie, charte, stratégie, indicateurs, guide des processus) — réalisé.")
    pdf.body_text(
        "Les écarts relevés sont de deux ordres. Des écarts fonctionnels assumés : l'absence "
        "d'interface frontend de newsletter, l'absence d'automatisation du questionnaire annuel, et "
        "l'absence de mise à jour directe d'une expérience. Des écarts de qualité : l'absence de "
        "suite de tests automatisés conservée dans le dépôt. Ces écarts, tous documentés et "
        "hiérarchisés dans le chapitre 7, ne remettent pas en cause la conformité d'ensemble du "
        "prototype avec les objectifs du sujet."
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
    pdf.body_text(
        "Le développement d'un projet de cette ampleur en autonomie a mis en évidence de nombreuses "
        "difficultés, plus nombreuses que ne le laisse paraître la synthèse initiale. Les principales "
        "sont détaillées ci-dessous avec la solution retenue :"
    )
    pdf.bullet("Authentification croisée admin/alumni : les tokens partageaient la même clé de stockage, provoquant des erreurs 403 inexpliquées. Correction : clés de stockage distinctes, contrôle du rôle dans le JWT, purge automatique des sessions orphelines.")
    pdf.bullet("Dérive entre le modèle et la base réelle : des écarts de migration ont été détectés par introspection (clés étrangères, routes cassées, doublons). Solution : migrations correctives et rejeu complet des migrations sur base vide comme test de validation systématique.")
    pdf.bullet("Deux admins pouvaient traiter la même demande RGPD : ajout d'un statut intermédiaire 'en traitement' et verrou applicatif pour éviter le traitement parallèle.")
    pdf.bullet("Indicateur d'insertion trompeur : le taux d'emploi à 6 mois comptait des expériences terminées. Correction : filtrage sur les expériences actives à la date de référence, exclusion des cohortes immatures.")
    pdf.bullet("Absence de versionnement Git (incident OneDrive) : perte de fichiers sans historique. Solution : dépôt Git avec .gitignore consolidé. Leçon : versionner avant la première ligne de code.")
    pdf.bullet("Modification non atomique d'une expérience : l'alumni devait supprimer puis recréer une expérience, soit deux transactions HTTP distinctes, avec risque de perte en cas d'échec. Une route PUT/PATCH et un formulaire dédié sont prévus en évolution, non livrés dans le délai du stage.")
    pdf.bullet("Messages d'erreur trompeurs : certains endpoints renvoyaient un statut 200 avec un corps d'erreur au lieu d'une véritable exception HTTP, masquant les fautes de frappe dans les requêtes. Correction : remplacement des 200 trompeurs par de vraies exceptions HTTP.")
    pdf.bullet("Filtres invalides ignorés silencieusement : un paramètre de filtre inconnu était ignoré et la liste complète renvoyée. Point laissé ouvert et consigné dans l'audit de cohérence pour traitement ultérieur.")
    pdf.bullet("Accumulation de données temporaires : lignes OTP et journal d'audit sans procédure de rétention. La purge différée couvre les comptes anonymisés ; une rétention sur ces tables est en piste d'amélioration.")
    pdf.bullet("Spécificités du driver PostgreSQL pg8000 : sérialisation JSONB non uniforme (gérée par isinstance + json.dumps + cast ::jsonb), absence d'ID automatique (clause RETURNING), erreurs d'intégrité via IntegrityError à analyser. Traitement centralisé dans des helpers.")
    pdf.bullet("Identifiants PostgreSQL en dur dans le code : risque de secrets versionnés. Migration vers des variables d'environnement via config.py et .env.example.")
    pdf.bullet("Messages d'erreur exposant le détail des exceptions : risque de fuite d'informations sur la structure interne. Sanitisation côté serveur, détail conservé dans les logs.")
    pdf.bullet("Upload de fichier sans contrôle : l'import acceptait un fichier sans vérifier l'extension ni limiter la taille. Ajout de la vérification d'extension, d'une limite de taille (5 Mo) et de la validation de chaque ligne via le schéma Pydantic.")
    pdf.body_text(
        "Chaque difficulté a fait l'objet d'une leçon retenue, formalisée dans le journal de bord du "
        "projet : vérifier le rôle à chaque appel sensible, rejouer les migrations à chaque évolution, "
        "tracer toute prise en charge, refuser d'afficher un chiffre trompeur, versionner avant de "
        "développer, ne jamais mélanger statut et corps d'erreur, valider toute entrée externe avant "
        "insertion, et ne jamais publier de secret dans le code ou une capture."
    )
    pdf.section_title("6.3 Compétences transversales")
    pdf.bullet("Autonomie et prise de décision : projet mené en solo, choix d'architecture assumés et documentés, arbitrages justifiés tout au long du rapport.")
    pdf.bullet("Documentation traitée comme du code : livrables PDF et DOCX générés par script (fpdf2, python-docx), donc régénérables et maintenables.")
    pdf.bullet("Rigueur méthodologique : audit de cohérence modèle/implémentation mené par introspection SQL, rédigé avant tout correctif, et principe strict 'une migration appliquée ne se modifie jamais'.")
    pdf.bullet("Compréhension des enjeux réglementaires : mise en pratique concrète du RGPD (consentement, portabilité, effacement, traçabilité) dans un contexte éducatif.")
    pdf.body_text(
        "Ce stage de substitution, proposé par IONIS-STM aux étudiants n'ayant pas trouvé de placement "
        "en entreprise, m'a permis d'appréhender l'ensemble du cycle de vie d'un projet logiciel, de la "
        "modélisation des besoins à la documentation de production, en passant par le développement, la "
        "sécurité et la conformité réglementaire."
    )

    pdf.section_title("6.4 Évaluation par rapport aux objectifs du sujet")
    pdf.body_text(
        "Au regard du contenu du sujet de stage, l'ensemble des livrables attendus a été produit : un "
        "système de suivi du parcours étudiant et de valorisation du réseau des anciens (prototype "
        "fonctionnel), le schéma MCD/MLD, un rapport de stage, ainsi que les documents de la mission "
        "Indicateurs et du volet Management (cartographie des données, charte RGPD, stratégie de mise "
        "à jour, analyse des indicateurs, guide des processus)."
    )
    pdf.body_text(
        "Les fonctionnalités cœur — gestion des profils, du parcours professionnel, des certifications, "
        "des questionnaires et des demandes RGPD — sont entièrement opérationnelles. Le tableau de "
        "bord d'insertion est alimenté par huit indicateurs calculés de façon reproductible. "
        "L'automatisation de la saisie par import Excel réduit un travail administratif important de "
        "saisie manuelle. La conformité RGPD, intégrée dès la conception, couvre le consentement, les "
        "droits des personnes et la traçabilité."
    )
    pdf.body_text(
        "Des écarts volontaires et assumés subsistent et sont détaillés dans le chapitre 7 : "
        "l'absence de suite de tests automatisés conservée dans le dépôt, l'absence de composant "
        "frontend pour la newsletter et l'automatisation du questionnaire annuel, et l'absence de "
        "route de mise à jour directe d'une expérience. Ces écarts ne remettent pas en cause la "
        "démonstration du concept, mais constituent les chantiers prioritaires d'une éventuelle mise "
        "en production."
    )
    pdf.section_title("6.5 Analyse critique du travail réalisé")
    pdf.body_text(
        "Le principal atout du travail réalisé est la maîtrise de bout en bout du cycle de vie : de "
        "la modélisation des données à la documentation, en passant par le développement, la "
        "sécurité et la conformité réglementaire. La documentation des livrables par script garantit "
        "leur régénérabilité et leur cohérence avec le code. Le fait d'avoir mené un audit de "
        "cohérence par introspection SQL, plutôt que de prétendre que tout fonctionnait, a permis de "
        "détecter des écarts réels et d'appliquer des correctifs documentés."
    )
    pdf.body_text(
        "Le principal point faible est la couverture des tests automatisés. Faute de suite de tests "
        "conservée dans le dépôt, la détection de régressions repose sur le rejeu des migrations et "
        "sur des tests manuels, ce qui ne garantit pas la stabilité à long terme. Cette limite est "
        "honnêtement documentée, et les axes d'amélioration du chapitre 7 en font la priorité "
        "absolue avant toute mise en production."
    )

    pdf.section_title("6.6 Récapitulatif des livrables et de l'organisation du travail")
    pdf.body_text(
        "Le travail réalisé s'est matérialisé en une série de livrables, répartis entre le "
        "développement et le volet documentaire : le prototype fonctionnel Alumni CRM (backend "
        "FastAPI, frontend React, base PostgreSQL), le schéma MCD/MLD (14 tables), le rapport de "
        "stage rédigé de façon « code » et régénérable, le volet Indicateurs (analyse et exemples "
        "de rapports), le volet Management (cartographie des données, charte RGPD, stratégie de "
        "mise à jour, guide des processus) ainsi que les captures d'écran présentées en annexe."
    )
    pdf.body_text(
        "Le projet a été mené de manière autonome et itérative. Le découpage en tranches "
        "fonctionnelles, la documentation continue, la revue régulière des décisions et la "
        "traçabilité des anomalies ont constitué le cadre de travail. Cette organisation, bien que "
        "sans équipe ni gestionnaire de projet dédié, a permis de livrer un prototype complet et "
        "cohérent, dont les limites sont clairement identifiées et hiérarchisées en vue d'une "
        "éventuelle poursuite."
    )

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

    # Conclusion
    pdf.chapter_title("8", "Conclusion")
    pdf.body_text(
        "Ce stage de substitution, mené au sein d'IONIS-STM dans le cadre du programme Pré-MSc 2026, "
        "m'a permis de concevoir et de développer de bout en bout un Alumni CRM : une plateforme de "
        "suivi du parcours étudiant et de valorisation du réseau des anciens, intégrant un espace "
        "administration, un espace alumni, un module d'indicateurs d'insertion et une conformité RGPD "
        "intégrée dès la conception."
    )
    pdf.body_text(
        "Le prototype livré couvre l'ensemble des fonctionnalités cœur du cahier des charges : "
        "inscription et authentification OTP, gestion du profil et du parcours professionnel, "
        "questionnaires annuels, tableau de bord avec huit indicateurs d'insertion calculés de façon "
        "reproductible, import/export automatisé, et traitement des demandes RGPD avec anonymisation "
        "et traçabilité. Le tout repose sur une architecture 3-tiers (React, FastAPI, PostgreSQL) "
        "documentée par 14 tables et 16 migrations versionnées."
    )
    pdf.body_text(
        "Le principal apport humain de ce stage est l'acquisition d'une vision complète du cycle de "
        "vie d'un projet logiciel : analyser un besoin, le modéliser, le développer, le sécuriser, le "
        "documenter et l'évaluer. Le principal apport méthodologique est la démonstration qu'un audit "
        "honnête, appuyé sur l'introspection du système réel, vaut mieux qu'une présentation "
        "superficielle de fonctionnalités supposées fonctionnelles."
    )
    pdf.body_text(
        "Les perspectives d'évolution sont nombreuses et documentées : automatisation du "
        "questionnaire annuel, composant frontend de newsletter, suite de tests automatisés, module "
        "de mentorat, application mobile et renforcement du chiffrement. Par leur réalisme et leur "
        "hiérarchisation par horizon, elles constituent une feuille de route crédible pour une "
        "éventuelle mise en production du prototype."
    )

    # Références
    pdf.chapter_title("9", "Références bibliographiques")

    pdf.section_title("Cadre réglementaire")
    pdf.bullet("Règlement (UE) 2016/679 du Parlement européen et du Conseil du 27 avril 2016 "
        "(RGPD).")
    pdf.bullet("Commission Nationale de l'Informatique et des Libertés (CNIL) — Guide pratique du "
        "RGPD : https://www.cnil.fr/fr/le-rgpd-et-les-etablissements-denseignement-superieur-et-de-recherche")

    pdf.section_title("Documentation technique — Backend")
    pdf.bullet("FastAPI — Documentation officielle : https://fastapi.tiangolo.com/")
    pdf.bullet("Pydantic — Documentation : https://docs.pydantic.dev/")
    pdf.bullet("pg8000 — Documentation : https://pypi.org/project/pg8000/")
    pdf.bullet("Python — Documentation officielle : https://docs.python.org/3/")

    pdf.section_title("Documentation technique — Frontend")
    pdf.bullet("React — Documentation officielle : https://react.dev/")
    pdf.bullet("Vite — Documentation officielle : https://vitejs.dev/")
    pdf.bullet("Vitest — Documentation : https://vitest.dev/")

    pdf.section_title("Documentation technique — Base de données")
    pdf.bullet("PostgreSQL — Documentation : https://www.postgresql.org/docs/")

    pdf.section_title("Référentiels et organismes de certification")
    pdf.bullet("Commission des Titres d'Ingénieur (CTI) — Référentiel d'accréditation : "
        "https://www.cti-commission.fr/referentiel-de-formation")
    pdf.bullet("Haute Autorité pour l'Évaluation de la Recherche et de l'Enseignement Supérieur "
        "(HCERES) — Référentiel d'évaluation : https://www.hceres.fr/")

    pdf.section_title("Services tierces")
    pdf.bullet("Resend — API email : https://resend.com/")

    pdf.section_title("Référence au groupe")
    pdf.bullet("IONIS Education Group — Site officiel : https://www.ionis-group.com/")

    pdf.section_title("Sources internes")
    pdf.bullet("Cahier des charges du sujet de stage — IONIS-STM, 2026.")
    pdf.bullet("Instructions Livrables & Soutenance 2026 v4 — IONIS-STM.")

    pdf.section_title("Glossaire et sigles")
    pdf.bullet("API : Application Programming Interface (interface de programmation applicative).")
    pdf.bullet("CRM : Customer Relationship Management (gestion de la relation client / des anciens élèves).")
    pdf.bullet("CTI : Commission des Titres d'Ingénieur (organisme de certification des formations d'ingénieur).")
    pdf.bullet("E2E : End-to-End (test couvrant l'ensemble du flux applicatif).")
    pdf.bullet("FK : Foreign Key (clé étrangère, contrainte de liaison entre tables).")
    pdf.bullet("HCERES : Haut Conseil de l'évaluation de la recherche et de l'enseignement supérieur.")
    pdf.bullet("HTTP : HyperText Transfer Protocol (protocole de transfert hypertexte).")
    pdf.bullet("IONIS : Groupe IONIS Education (groupe d'enseignement supérieur privé).")
    pdf.bullet("JWT : JSON Web Token (jeton d'authentification).")
    pdf.bullet("MCD/MCD : Modèle Conceptuel de Données / Modèle Logique de Données.")
    pdf.bullet("KPI : Key Performance Indicator (indicateur clé de performance).")
    pdf.bullet("OTP : One-Time Password (mot de passe à usage unique).")
    pdf.bullet("ORM : Object-Relational Mapping (correspondance objet-relationnel).")
    pdf.bullet("pg8000 : Pilote PostgreSQL pur Python utilisé pour la connexion à la base de données.")
    pdf.bullet("PostgreSQL : Système de gestion de base de données relationnelle open source.")
    pdf.bullet("PWA : Progressive Web App (application web installable).")
    pdf.bullet("Pydantic : Bibliothèque Python de validation de données basée sur les annotations de type.")
    pdf.bullet("React : Bibliothèque JavaScript pour la construction d'interfaces utilisateur.")
    pdf.bullet("RGPD : Règlement Général sur la Protection des Données (UE 2016/679).")
    pdf.bullet("REST : Representational State Transfer (style d'architecture d'API).")
    pdf.bullet("SQL : Structured Query Language (langage de requêtes relationnel).")
    pdf.bullet("SPA : Single Page Application (application monopage).")
    pdf.bullet("Swagger : Interface de documentation et d'essai des API, auto-générée par FastAPI.")
    pdf.bullet("Vite : Outil de build et serveur de développement frontend rapide.")

    # ---------- Annexes : captures d'écran ----------
    fig_dir = os.path.join(OUTPUT_DIR, "..", "image")
    annexe_b = [
        ("Annexe B.1 - Tableau de bord administrateur (KPI et graphiques)", "anB_dashboard.png"),
        ("Annexe B.2 - Annuaire filtrable des alumni", "anB_annuaire.png"),
        ("Annexe B.3 - Traitement des demandes RGPD", "anB_demandes_rgpd.png"),
    ]
    annexe_c = [
        ("Annexe C.1 - Espace alumni - Mon Profil", "anC_profil.png"),
        ("Annexe C.2 - Espace alumni - Mon Parcours professionnel", "anC_parcours.png"),
        ("Annexe C.3 - Espace alumni - Consentement RGPD", "anC_consentement.png"),
        ("Annexe C.4 - Espace alumni - Questionnaire annuel", "anC_questionnaire.png"),
    ]

    def _capture_page(title, filename):
        path = os.path.join(fig_dir, filename)
        if not os.path.exists(path):
            pdf.body_text("[Capture manquante : %s]" % filename)
            return
        try:
            from PIL import Image
            with Image.open(path) as im:
                ratio = im.height / im.width
        except Exception:
            ratio = 0.625
        pdf.add_page()
        pdf.section_title(title)
        pdf.image(path, x=10, w=180.0, h=180.0 * ratio)
        pdf.ln(2)

    pdf.section_title("10. Annexes - Captures d'écran de l'application")
    pdf.body_text(
        "Les captures suivantes illustrent l'interface du prototype. Elles ont été réalisées sur la "
        "base de données de démonstration (domaine @demo-alumni-crm.io) et servent d'appui à la "
        "présentation orale. L'annexe B présente l'espace administrateur : le tableau de bord avec "
        "les KPI et graphiques d'insertion, l'annuaire filtrable des alumni et le suivi des demandes "
        "RGPD. L'annexe C présente l'espace alumni : le profil, le parcours professionnel, la "
        "gestion des consentements et le questionnaire annuel."
    )
    for t, f in annexe_b:
        _capture_page(t, f)
    for t, f in annexe_c:
        _capture_page(t, f)

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