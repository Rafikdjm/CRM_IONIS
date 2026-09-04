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
    generate_guide_animation()
    print("\nTous les rapports ont ete generes dans :", OUTPUT_DIR)