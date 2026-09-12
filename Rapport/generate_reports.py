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
        self._pending_headings = []
        self._pending_heading_h = 0.0

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

    def _queue_heading(self, height, text, font, style, size, color, ln):
        self._pending_headings.append({
            "text": text, "font": font, "style": style,
            "size": size, "color": color, "height": height, "ln": ln,
        })
        self._pending_heading_h += height + ln

    def _flush_headings(self, min_follow=0.0):
        if not self._pending_headings:
            return
        total = self._pending_heading_h
        if self.get_y() + total + min_follow > self.page_break_trigger - 1:
            self.add_page()
        for h in self._pending_headings:
            self.set_font(h["font"], h["style"], h["size"])
            self.set_text_color(*h["color"])
            self.cell(0, h["height"], h["text"], new_x="LMARGIN", new_y="NEXT")
            self.ln(h["ln"])
        self._pending_headings = []
        self._pending_heading_h = 0.0

    def chapter_title(self, num, title):
        self._queue_heading(10, f"{num}. {title}", "SegoeUI", "B", 14, (30, 64, 175), 2)

    def section_title(self, title):
        self._queue_heading(8, title, "SegoeUI", "B", 11, (55, 65, 81), 1)

    def body_text(self, text):
        self._flush_headings(min_follow=12)
        self.set_font("SegoeUI", "", 10)
        self.set_text_color(55, 65, 81)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def bullet(self, text, indent=10):
        self._flush_headings(min_follow=8)
        self.set_font("SegoeUI", "", 10)
        self.set_text_color(55, 65, 81)
        x0 = self.l_margin + indent
        bullet_w = 6
        text_x = x0 + bullet_w
        width = self.w - self.r_margin - text_x
        line_h = 5.5
        lines = self.multi_cell(width, line_h, text, dry_run=True, output="LINES")
        self.set_xy(x0, self.get_y())
        self.cell(bullet_w, line_h, "\u2022")
        for line in lines:
            if self.get_y() + line_h > self.page_break_trigger:
                self.add_page()
            self.set_x(text_x)
            self.cell(width, line_h, line, new_x="LMARGIN", new_y="NEXT")
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
            self.multi_cell(w - 2 * pad, line_h, txt, border=0, padding=0, align="L")
        self.set_xy(x0, y_start + row_h)
        return row_h

    def table_header(self, cols, widths):
        self._t_cols = list(cols)
        self._t_widths = self._normalize_widths(list(widths))
        self._t_header_drawn = False

    def _ensure_header(self):
        if getattr(self, "_t_header_drawn", False):
            return
        self._draw_table_row(self._t_cols, self._t_widths,
                             fill=self.TABLE_HEADER_FILL, bold=True, min_h=8.0,
                             text_color=self.TABLE_HEADER_TEXT)
        self._t_header_drawn = True

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

        reserve = self._pending_heading_h
        if not getattr(self, "_t_header_drawn", False):
            reserve += 8.0
        if self.get_y() + row_h + reserve > self.page_break_trigger - 1:
            self.add_page()

        self._flush_headings()
        self._ensure_header()
        self._draw_table_row(cols, widths,
                             fill=self.TABLE_BODY_FILL_ALT if fill else self.TABLE_BODY_FILL,
                             text_color=self.TABLE_TEXT)


def generate_cartographie():
    pdf = ReportPDF("Cartographie des Données")
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_font("SegoeUI", "B", 20)
    pdf.set_text_color(30, 64, 175)
    pdf.cell(0, 12, "Cartographie des Données", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("SegoeUI", "", 10)
    pdf.set_text_color(107, 114, 128)
    pdf.cell(0, 7, "Projet Alumni CRM - Version complete et fidele au code source", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(8)

    # 1. Contexte
    pdf.chapter_title("1", "Contexte et Objectifs")
    pdf.body_text(
        "Ce document dresse l'inventaire des données que l'Alumni CRM collecte et conserve. Il "
        "répond au cahier des charges : un outil de suivi du parcours étudiant et de valorisation du "
        "réseau des anciens. J'ai détaillé ce qui est recueilli à l'entrée (l'inscription), ce qui "
        "s'ajoute après le diplôme (parcours, certifications, enquêtes), et enfin ce qui touche au "
        "consentement RGPD, un point sensible dès qu'on manipule des données personnelles."
    )

    # 2. Donnees Entree
    pdf.chapter_title("2", "Données collectées à l'entrée (Phase d'Inscription)")
    pdf.body_text(
        "Ce sont les données qui servent à créer le profil initial de l'étudiant lors de son "
        "intégration, à partir des entités ETUDIANT et PROMOTION du modèle."
    )

    headers = ["Catégorie", "Champs (Code)", "Description (simplifiée)", "Exemple"]
    widths = [31, 73, 58, 28]
    pdf.table_header(headers, widths)
    rows = [
        ["Identité et Coordonnées", "nom, prenom, email, telephone", "Identification de l'alumni.", "Alice Martin"],
        ["Identité et Coordonnées", "date_naissance", "Statistiques démographiques.", "1999-04-12"],
        ["Identité et Coordonnées", "email_academique", "Contact institutionnel (facultatif).", "alice@ionis-stm.com"],
        ["Identité et Coordonnées", "address, city, country", "Localisation géographique.", "Paris, France"],
        ["Identité et Coordonnées", "linkedin", "Lien vers le profil LinkedIn.", "linkedin.com/in/alice"],
        ["Identité et Coordonnées", "availability_status", "Statut : en_poste, a_lecoute, en_recherche.", "en_recherche"],
        ["Identité et Coordonnées", "skills", "Compétences techniques (tags).", "Python, SQL, DevOps"],
        ["Historique Académique", "parcours_anterieur", "Cursus suivi avant l'intégration.", "BTS SIO"],
        ["Historique Académique", "previous_school (inscription)", "Établissement précédent.", "Lycée Voltaire"],
        ["Rattachement Scolaire", "id_promotion -> nom_promotion, annee_diplome, filiere", "Rattachement promotion (filtres promo/filière).", "Promo 2025, Data"],
        ["Données complémentaires", "date_inscription", "Date de création du profil.", "2023-09-01"],
    ]
    for i, r in enumerate(rows):
        pdf.table_row(r, widths, fill=(i % 2 == 0))


    pdf.ln(4)

    # 3. Donnees Sortie
    pdf.chapter_title("3", "Données collectées à la sortie (Évolution Post-Diplôme)")
    pdf.body_text(
        "Après le diplôme, le système suit l'évolution de la carrière des alumni à partir des tables "
        "EXPERIENCE_PRO, ENTREPRISE et CERTIFICATION. S'y ajoutent les données déclaratives "
        "recueillies chaque année via QUESTIONNAIRE et REPONSE."
    )

    headers = ["Catégorie", "Champs (Code)", "Description (simplifiée)", "Exemple"]
    widths = [41, 44, 73, 32]
    pdf.table_header(headers, widths)
    rows2 = [
        ["Suivi des Postes", "company (nom_entreprise)", "Entreprise employeuse.", "Capgemini"],
        ["Suivi des Postes", "position (intitule_poste)", "Intitulé du poste.", "Développeur Data"],
        ["Suivi des Postes", "type_contrat", "CDI, CDD, Freelance, Alternance, Stage...", "CDI"],
        ["Suivi des Postes", "start_date, end_date", "Période du poste (mois/année).", "09/2024 - 06/2025"],
        ["Suivi des Postes", "is_current (poste_actuel)", "Poste occupé actuellement.", "true"],
        ["Suivi des Postes", "description", "Missions et responsabilités.", "Pipeline data, API"],
        ["Informations Salariales", "salary_range (salaire)", "Ancien champ texte (rétrocompatibilité).", "35-45k EUR"],
        ["Informations Salariales", "salary_annuel (NUMERIC)", "Salaire brut annuel (chiffre).", "42000"],
        ["Géographie", "pays, ville", "Localisation de l'entreprise.", "France, Paris"],
        ["Secteur d'activité", "sector (secteur_activite)", "37 catégories + Autre.", "Conseil"],
        ["Certifications", "name (nom_certification)", "Certification post-diplôme.", "AWS Certified"],
        ["Certifications", "issuer (organisme)", "Organisme émetteur.", "Amazon AWS"],
        ["Certifications", "date_obtained", "Date d'obtention.", "2025-03-15"],
        ["Réponse Questionnaire", "reponses (JSON)", "Réponses enquêtes annuelles.", "{\"salaire\": \"42k\"}"],
    ]
    for i, r in enumerate(rows2):
        pdf.table_row(r, widths, fill=(i % 2 == 0))


    pdf.ln(4)

    # 4. Donnees RGPD
    pdf.chapter_title("4", "Données de Consentement RGPD")
    pdf.body_text(
        "La table CONSENTEMENT_RGPD conserve une trace complète des choix de confidentialité de "
        "chaque alumni : le type d'autorisation accordée, son statut (actif ou refusé), la date et le "
        "canal de recueil."
    )

    headers3 = ["Champ", "Type / Valeurs", "Description (simplifiée)", "Exemple"]
    widths3 = [45, 51, 67, 27]
    pdf.table_header(headers3, widths3)
    rgpd_rows = [
        ["id_etudiant", "Entier (FK)", "Référence vers l'alumni.", "42"],
        ["type_consentement", "4 types (voir Charte RGPD)", "Nature de l'autorisation.", "newsletter"],
        ["date_consentement", "Date (AAAA-MM-JJ)", "Date du recueil.", "2025-09-14"],
        ["statut", "actif | refuse", "État du consentement.", "actif"],
        ["canal", "web | questionnaire", "Origine de l'accord.", "web"],
    ]
    for i, r in enumerate(rgpd_rows):
        pdf.table_row(r, widths3, fill=(i % 2 == 0))
    pdf.ln(4)

    pdf.bullet("DEMANDE_RGPD : les demandes d'export ou de suppression lancées par l'alumni, avec leur cycle envoyée -> en_traitement -> traitée/rejetée et un verrou anti-traitement parallèle (prise_en_charge_par).")
    pdf.bullet("AUDIT_LOG : journal horodaté des opérations sensibles (anonymisations, purges, nettoyages), avec acteur, action, détail et nombre de lignes.")
    pdf.bullet("ETUDIANT.date_anonymisation : horodatage d'anonymisation ; un compte anonymisé refuse toute nouvelle écriture et reste exclu des indicateurs jusqu'à la purge différée.")

    pdf.ln(2)
    pdf.body_text(
        "Le mécanisme complet du consentement — recueil, modification, retrait, droits des personnes, "
        "workflow d'effacement — est détaillé dans la Charte de Conformité RGPD, livrée séparément. "
        "Pas la peine de le dupliquer ici : ce document reste une photographie des données gérées, "
        "pas un guide juridique."
    )

    pdf.output(os.path.join(OUTPUT_DIR, "Cartographie des Donnees - Alumni CRM.pdf"))
    print("Cartographie generee.")


def generate_rgpd():
    pdf = ReportPDF("Charte RGPD")
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_font("SegoeUI", "B", 20)
    pdf.set_text_color(30, 64, 175)
    pdf.cell(0, 12, "Charte de Conformité RGPD", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("SegoeUI", "", 10)
    pdf.set_text_color(107, 114, 128)
    pdf.cell(0, 7, "Projet Alumni CRM - Version complete et fidele au code source", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(8)

    # 1. Contexte
    pdf.chapter_title("1", "Contexte Juridique")
    pdf.body_text(
        "Un annuaire d'anciens manipule avant tout des données personnelles : c'est le point de "
        "vigilance numéro un. La conformité repose ici sur une traçabilité complète des choix via la "
        "table CONSENTEMENT_RGPD, dans le cadre du Règlement (UE) 2016/679 (RGPD) et de la loi "
        "Informatique et Libertés. Deux limites à connaître : les données de consentement ne sont pas "
        "chiffrées au niveau applicatif (leur protection repose sur l'infrastructure PostgreSQL), et "
        "aucune fonctionnalité de notification de violation de données n'existe à ce jour."
    )

    # 2. Types de consentement
    pdf.chapter_title("2", "Les 4 Types de Consentement Implémentés")
    pdf.body_text(
        "Quatre consentements distincts sont proposés, chacun géré indépendamment par un toggle "
        "dédié dans l'interface alumni (AlumniConsent.jsx)."
    )

    headers = ["Type (Backend)", "Clé Frontend", "Description (simplifiée)", "Exemple"]
    widths = [27, 34, 74, 55]
    pdf.table_header(headers, widths)
    rows = [
        ["prise_de_contact", "contact_allowed", "L'école ou ses partenaires peuvent contacter l'alumni.", "Offres de postes, événements"],
        ["partage_donnees", "data_sharing", "Données statistiques anonymisées partagées.", "Secteur, poste"],
        ["enquetes", "survey_participation", "Participation aux enquêtes alumni.", "Évolution de carrière, satisfaction"],
        ["newsletter", "newsletter", "Réception de la newsletter.", "Actualités, offres d'emploi"],
    ]
    for i, r in enumerate(rows):
        pdf.table_row(r, widths, fill=(i % 2 == 0))
    pdf.ln(4)


    # 3. Gestion du consentement
    pdf.chapter_title("3", "Mécanisme de Gestion du Consentement")
    pdf.section_title("3.1 Collecte du consentement")
    pdf.bullet("Canal principal : le formulaire d'inscription web (AlumniRegistration.jsx).")
    pdf.bullet("Canal secondaire prévu : le questionnaire annuel (AlumniSurvey.jsx). À ce jour, seul le canal 'web' est réellement émis par le frontend.")
    pdf.bullet("Chaque vote enregistre : type_consentement, statut (actif ou refuse), date_consentement, canal et id_etudiant.")
    pdf.bullet("L'endpoint POST /consentements/ crée ou met à jour le consentement pour chaque type.")
    pdf.bullet("L'interface de consentement rappelle la durée de conservation des données (suppression 6 mois après anonymisation) et affiche le contact du DPO (dpo@ionis-stm.com).")

    pdf.section_title("3.2 Modification et retrait")
    pdf.bullet("L'alumni peut changer ses préférences à tout moment via l'interface de consentement.")
    pdf.bullet("Le retrait est modélisé par un nouveau vote 'refuse', horodaté comme les autres.")
    pdf.bullet("L'interface affiche la date de dernière mise à jour du consentement.")
    pdf.bullet("Une suppression physique reste possible via DELETE /consentements/{id_consentement} (propriétaire ou admin) ; le retrait usuel, lui, conserve l'historique complet des votes.")

    pdf.section_title("3.3 Traçabilité")
    pdf.bullet("Date exacte du recueil enregistrée (date_consentement).")
    pdf.bullet("Canal de collecte identifié de façon formelle (inscription ou questionnaire).")
    pdf.bullet("Historique complet des votes conservé dans la base de données.")

    pdf.section_title("3.4 Consommation des consentements (relations fonctionnelles)")
    pdf.body_text(
        "Chaque consentement est relié à un usage réel du système : un refus (statut 'refuse') "
        "désactive l'usage concerné. Tant que l'alumni n'a pas voté pour un type, il reste éligible "
        "(statut 'inconnu' toléré), ce qui est cohérent avec la suppression d'un consentement via "
        "DELETE /consentements/{id_consentement}. Le vote le plus récent est toujours déterminé par la "
        "même sous-requête corrélée (ORDER BY date_consentement DESC, id_consentement DESC LIMIT 1)."
    )
    pdf.bullet("'newsletter' : autorise l'envoi des newsletters (POST /newsletter/envoyer, ciblage par promotion, secteur et consentements actifs).")
    pdf.bullet("'enquetes' : donne accès au questionnaire actif (GET /questionnaires/actif) et aux relances (POST /admin/questionnaires/notififier). Un refus bloque la restitution du questionnaire (HTTP 403) et masque le lien 'Enquête annuelle' dans la navigation alumni (AlumniLayout.jsx).")
    pdf.bullet("'prise_de_contact' : couvre newsletter et relances ; un refus exclut l'alumni des deux envois et c'est le seul consentement dont le refus déclenche l'anonymisation du profil (cleanup.py, CONSENTEMENT_ARCHIVE_TYPE = 'prise_de_contact').")
    pdf.bullet("'partage_donnees' : seuls les alumni ayant accepté le partage alimentent les indicateurs partenaires GET /admin/indicateurs/partenaires (comptages et moyennes anonymisés, aucune donnée personnelle transmise).")

    # 4. Droits RGPD
    pdf.chapter_title("4", "Droits RGPD Implémentés dans l'Interface")
    pdf.body_text("Dans l'interface alumni, ces droits sont à la fois affichés et réellement implémentés :")
    pdf.bullet("Droit d'accès : page de profil en lecture seule, suivi des demandes via GET /rgpd/demandes/moi et export auto-service JSON/Excel/CSV via GET /rgpd/export.")
    pdf.bullet("Droit de rectification et de mise à jour (AlumniProfile.jsx).")
    pdf.bullet("Droit à l'effacement (droit à l'oubli) : workflow auto-service (POST /rgpd/demandes) traité par anonymisation puis purge différée.")
    pdf.bullet("Droit de retirer son consentement à tout moment (AlumniConsent.jsx avec toggles).")

    # 5. Valeurs du statut
    pdf.chapter_title("5", "Modèle de Données CONSENTEMENT_RGPD")

    headers2 = ["Champ", "Type", "Contraintes (simplifiées)", "Exemple"]
    widths2 = [44, 33, 87, 26]
    pdf.table_header(headers2, widths2)
    rows2 = [
        ["id_etudiant", "Entier (FK)", "REFERENCES ETUDIANT, NOT NULL.", "42"],
        ["type_consentement", "Enum / Chaîne", "4 valeurs possibles.", "newsletter"],
        ["date_consentement", "Date", "NOT NULL, date du jour.", "2025-09-14"],
        ["statut", "Chaîne", "actif (accordé) / refuse (retiré).", "actif"],
        ["canal", "Chaîne", "web | questionnaire.", "web"],
    ]
    for i, r in enumerate(rows2):
        pdf.table_row(r, widths2, fill=(i % 2 == 0))

    pdf.ln(4)

    # 6. Workflow des demandes RGPD
    pdf.chapter_title("6", "Workflow des Demandes RGPD (Effacement et Portabilité)")
    pdf.body_text(
        "Au-delà des consentements, le CRM met en place un vrai circuit de traitement des droits "
        "d'accès, d'effacement et de portabilité, appuyé sur la table DEMANDE_RGPD :"
    )
    pdf.bullet("Dépôt auto-service : POST /rgpd/demandes (types 'export' ou 'suppression') ; l'alumni suit et annule ses demandes via GET /rgpd/demandes/moi et DELETE /rgpd/demandes/{id}.")
    pdf.bullet("Cycle de statuts : envoyee -> en_traitement -> traitee/rejetee (contrainte SQL, migration 009), avec un verrou anti-traitement parallèle (prise_en_charge_par, date_prise_en_charge).")
    pdf.bullet("Une demande de suppression est traitée par anonymisation irréversible (email remplacé par ANONYMISE_<id>@anonymise.io, données personnelles effacées), puis par purge physique différée après PURGE_DELAY_MONTHS mois (défaut 6) via purge.py (--dry-run disponible) ou POST /admin/demandes-rgpd/purge-anonymises.")
    pdf.bullet("Portabilité : export auto-service JSON/Excel/CSV via GET /rgpd/export ; exports admin unitaires et en masse.")
    pdf.bullet("Chaque opération est tracée dans AUDIT_LOG (acteur, action, détails).")

    pdf.output(os.path.join(OUTPUT_DIR, "Charte de Conformite RGPD - Alumni CRM.pdf"))
    print("Charte RGPD generee.")


def generate_strategie():
    pdf = ReportPDF("Stratégie de Mise à Jour")
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_font("SegoeUI", "B", 20)
    pdf.set_text_color(30, 64, 175)
    pdf.cell(0, 12, "Stratégie de Mise à Jour des Données", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("SegoeUI", "", 10)
    pdf.set_text_color(107, 114, 128)
    pdf.cell(0, 7, "Projet Alumni CRM - Version complete et fidele au code source", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(8)

    # 1. Defi
    pdf.chapter_title("1", "Le Défi de l'Obsolescence des Données")
    pdf.body_text(
        "Le problème de fond d'un annuaire d'anciens, c'est que les informations périment vite. "
        "Sans rien faire, les données d'insertion (postes, entreprises, salaires) deviennent "
        "rapidement fausses. La gouvernance du CRM part donc d'une idée simple : inciter "
        "régulièrement les diplômés à mettre à jour leur profil."
    )

    # 2. Mise a jour manuelle
    pdf.chapter_title("2", "Mise à Jour Manuelle par l'Alumni")

    pdf.section_title("2.1 Gestion du profil (AlumniProfile.jsx)")
    pdf.bullet("L'alumni peut modifier presque tout son profil : prenom, nom, email, telephone, adresse, ville, pays, LinkedIn, date de naissance, email académique et parcours antérieur.")
    pdf.bullet("Le statut de disponibilité (en_poste / a_lecoute / en_recherche) est obligatoire et conditionne le comportement du système.")
    pdf.bullet("Les compétences (skills) sont gérées via un système dynamique d'ajout/suppression de tags.")

    pdf.section_title("2.2 Gestion du parcours (AlumniCareer.jsx)")
    pdf.bullet("Ajout et suppression d'expériences professionnelles (entreprise, poste, secteur, contrat, dates, salaire, localisation). Modifier une expérience existante passe par PUT /experiences/{id_experience}, en une seule transaction atomique : plus besoin de supprimer puis recréer.")
    pdf.bullet("Ajout et suppression de certifications (nom, organisme, date d'obtention).")
    pdf.bullet("Poste actuel détecté automatiquement : si aucun poste n'est coché 'actuel', le système affiche l'expérience la plus récente.")
    pdf.bullet("Un message d'alerte s'affiche dans l'interface Parcours quand l'alumni est en 'en_poste' sans avoir coché de poste actuel.")

    # 3. Questionnaire annuel
    pdf.chapter_title("3", "Questionnaire Annuel Automatisé")

    pdf.section_title("3.1 Côté administration (AdminQuestionnaires.jsx)")
    pdf.bullet("Crée, modifie et supprime des questionnaires via une interface dédiée.")
    pdf.bullet("6 types de questions : texte libre, choix multiple (radio), choix unique (radio, une seule réponse), liste déroulante (select, une seule réponse), oui/non (boolean) et note 1-5 (rating).")
    pdf.bullet("Tags KPI : une question peut être étiquetée (ex. 'adequation_formation') pour alimenter automatiquement les indicateurs de pilotage.")
    pdf.bullet("Questions conditionnées : une question peut être masquée automatiquement si l'alumni est en recherche active (conditionnee_statut_emploi).")
    pdf.bullet("Cycle de vie : activation, désactivation puis réactivation d'un questionnaire.")
    pdf.bullet("Consultation des réponses avec nom, prénom, email, date et détails.")

    pdf.section_title("3.2 Côté alumni (AlumniSurvey.jsx)")
    pdf.bullet("L'alumni accède au questionnaire actif depuis le menu latéral ; en cas de refus du consentement 'enquetes', la restitution est bloquée (HTTP 403) et le menu latéral masqué, pour respecter le RGPD.")
    pdf.bullet("Les réponses précédentes sont pré-remplies pour faciliter la mise à jour ; le pré-remplissage s'appuie sur le dernier questionnaire renseigné, sans historique complet dans l'interface.")
    pdf.bullet("Les questions non applicables (conditionnées au statut) sont masquées et enregistrées comme 'Non applicable'.")
    pdf.bullet("L'alumni peut modifier ses réponses à tout moment.")
    pdf.bullet("Validation : toutes les questions visibles doivent être répondues avant soumission.")

    # 4. Guide processus
    pdf.chapter_title("4", "Guide des Processus pour le Service des Relations Entreprises")

    pdf.section_title("4.1 Pilotage des campagnes")
    pdf.bullet("Le service crée et administre les questionnaires via l'interface AdminQuestionnaires.")
    pdf.bullet("Toute question taguée 'adequation_formation' alimente automatiquement l'indicateur d'adéquation formation/emploi du tableau de bord.")
    pdf.bullet("Activation et désactivation des questionnaires selon le calendrier de collecte. L'activation reste manuelle : aucun déclenchement planifié automatiquement à ce jour.")
    pdf.bullet("Relances : l'endpoint POST /admin/questionnaires/notififier envoie des rappels par email aux alumni n'ayant pas répondu au questionnaire actif (filtre par promotion ; RGPD : exclusion des alumni ayant refusé 'enquetes' ou 'prise_de_contact', sur le vote le plus récent). Pas d'interface admin dédiée pour déclencher ces envois pour l'instant.")

    pdf.section_title("4.2 Valorisation du réseau")
    pdf.bullet("Le tableau de bord admin permet de filtrer les alumni par entreprise, secteur et promotion.")
    pdf.bullet("L'annuaire enrichi aide à repérer les opportunités de stages ou de partenariats.")
    pdf.bullet("Le réseau s'enrichit au fil des mises à jour des alumni et des réponses aux questionnaires.")

    pdf.section_title("4.3 Newsletter Alumni - Processus Détailé")
    pdf.body_text(
        "La newsletter est l'un des leviers les plus directs pour animer le réseau et faire remonter "
        "des données à jour. Autant la traiter comme un vrai processus — un rythme, un contenu — que "
        "comme un envoi de temps en temps."
    )
    pdf.bullet("Ciblage : seuls les alumni ayant activé le consentement 'newsletter' (type_consentement = 'newsletter', statut = 'actif') sont contactés.")
    pdf.bullet("Fréquence : mensuelle ou bimestrielle, avec un calendrier éditorial défini par le service des Relations Entreprises.")
    pdf.bullet("Contenu type : actualités de l'écosystème, offres d'emploi partenaires, événements (réunions, conférences) et appel à mise à jour du profil.")
    pdf.bullet("Call-to-Action obligatoire : chaque newsletter pointe directement vers la page de mise à jour du profil alumni (AlumniProfile.jsx).")
    pdf.bullet("Personnalisation : ciblage affinable par promotion, secteur d'activité, géographie ou disponibilité (en_poste / en_recherche).")
    pdf.bullet("Suivi : taux d'ouverture, taux de clic sur le CTA et part de profils mis à jour après l'envoi.")
    pdf.bullet("RGPD : chaque campagne rappelle le droit de se désabonner. Le lien de désinscription automatique n'est pas encore branché sur le consentement (liens placeholder dans le gabarit HTML — reste à faire).")
    pdf.bullet("Côté technique : l'endpoint POST /newsletter/envoyer est en place (filtres promotion/secteur, consentement newsletter actif, 'prise_de_contact' non refusé ; mode console en dev, Resend en prod). Le composant d'envoi côté frontend n'est pas encore développé.")
    pdf.bullet("À terme : un cron pourrait planifier les envois récurrents, avec une notification à l'admin pour valider le contenu avant envoi.")

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
    pdf.chapter_title("1", "Objectif de la Modélisation")
    pdf.body_text(
        "Ce document reprend les indicateurs d'insertion que l'Alumni CRM sait calculer, et montre "
        "comment on passe des données brutes du réseau à des chiffres exploitables. Le cahier des "
        "charges impose en effet de pouvoir produire des rapports d'insertion professionnelle à "
        "destination des organismes de certification et des autorités de tutelle. J'ai donc essayé de "
        "couvrir trois choses : quels indicateurs on affiche, comment ils sont calculés dans le code, "
        "et sous quelle forme on peut les retrouver dans un rapport."
    )

    # 2. Indicateurs
    pdf.chapter_title("2", "Indicateurs Clés de Pilotage")
    pdf.body_text(
        "Voici les indicateurs qui remontent dans le tableau de bord admin. Pour chacun d'eux, on "
        "trouve une définition simple, l'usage métier, et un mini-exemple pour illustrer la formule. "
        "Les chiffres sont fictifs, mais ils appliquent exactement les requêtes du backend."
    )
    headers = ["Indicateur", "Définition (simplifiée)", "Métier / Utilisation", "Exemple"]
    widths = [40, 68, 41, 41]
    pdf.table_header(headers, widths)
    rows = [
        ["Taux d'emploi à 6 mois", "Diplômés en activité 6 mois après la sortie (CDI, CDD...).", "Rapports ministériels et audits.", "Promo 2025 : 9/12 en poste = 75 %"],
        ["Taux d'emploi global (brut)", "(Alumni en poste / total alumni) x 100.", "Efficacité globale de la formation.", "30 alumni en poste / 40 = 75 %"],
        ["Adéquation formation/emploi", "Correspondance filière suivie / secteur du poste (question KPI).", "Pertinence de l'offre de formation.", "3 réponses Oui / 4 = 75 %"],
        ["Salaire moyen par filière", "Salaire brut annuel moyen (AVG/MIN/MAX sur salary_annuel).", "Valorisation des débouchés.", "38000 + 42000 + 50000 / 3 = 43 333 EUR"],
        ["Alumni actifs", "Alumni avec au moins une expérience enregistrée.", "Engagement des anciens élèves.", "45 alumni actifs sur 60"],
        ["Taux de complétion", "Alumni avec profil + expérience complètes.", "Qualité des données collectées.", "32 profils complets / 60 = 53 %"],
        ["Alumni par promotion", "Effectif et taux d'emploi par promotion (ETUDIANT + PROMOTION).", "Comparatif des cohortes.", "2024 : 10 / 80 % ; 2025 : 12 / 75 %"],
        ["Répartition par secteur", "Nombre d'alumni par secteur d'activité.", "Débouchés et secteurs recruteurs.", "Info 3, Finance 2, Santé 1"],
    ]
    for i, r in enumerate(rows):
        pdf.table_row(r, widths, fill=(i % 2 == 0))

    pdf.ln(4)

    # 3. Implementation technique
    pdf.chapter_title("3", "Implémentation Technique des Indicateurs")
    pdf.section_title("3.1 Endpoints API")

    headers2 = ["Endpoint", "Description (simplifiée)", "Données retournées (extrait)"]
    widths2 = [50, 56, 84]
    pdf.table_header(headers2, widths2)
    rows2 = [
        ["GET /admin/indicateurs", "Indicateurs principaux du tableau de bord.", "total_alumni, taux_emploi_6mois, taux_couverture, alumni_actifs, taux_reponse, salaire_moyen/min/max."],
        ["GET /admin/indicateurs/\nsecteurs", "Répartition par secteur d'activité.", "{secteur, count}, total_alumni."],
        ["GET /admin/indicateurs/\ntypes-contrat", "Répartition par type de contrat (expériences en cours).", "{type_contrat, count} ; vides = 'Non renseigné'."],
        ["GET /admin/indicateurs/\nkpi-tag?tag=X", "Valeur d'un indicateur KPI (question taguée).", "valeur, unité (% ou moyenne), total_repondants, question_texte, distribution."],
        ["GET /admin/indicateurs/\nkpi-tags", "Tous les tags KPI des questionnaires actifs.", "[{tag, libelle, pourcentage, nb_repondants, valeur, unité, distribution}]."],
        ["GET /admin/indicateurs/\nkpi-tags-actifs", "Liste des tags DISTINCT utilisés.", "{tags: [...]}"],
        ["GET /admin/indicateurs/\npartenaires", "Indicateurs anonymisés pour les partenaires (partage_donnees actif).", "nb_consentants, taux_emploi_pourcentage, en_emploi, salaire_moyen, par_promotion, top_secteurs."],
    ]
    for i, r in enumerate(rows2):
        pdf.table_row(r, widths2, fill=(i % 2 == 0))

    pdf.ln(4)

    pdf.section_title("3.2 Calcul des indicateurs")
    pdf.bullet("Taux d'emploi à 6 mois : calculé côté backend. Une expérience compte si sa date_debut tombe dans les 6 mois qui suivent le 1er décembre de l'année de diplôme (on suppose une diplomation en juin). Les promotions dont la fenêtre de 6 mois n'est pas encore écoulée sont laissées de côté : taux à null, statut 'en_attente'.")
    pdf.bullet("Taux d'emploi global : rapport (alumni en poste / total alumni) x 100, recalculé côté frontend à partir des indicateurs par promotion.")
    pdf.bullet("Adéquation formation/emploi : le frontend appelle /admin/indicateurs/kpi-tag?tag=adequation_formation, qui agrège les réponses à la question portant ce tag.")
    pdf.bullet("Tags KPI : une question peut recevoir un tag (ex. 'adequation_formation'). Tant qu'une question est taguée, l'indicateur associé apparaît dans le dashboard sans toucher au code backend — c'est ce qui rend le mécanisme simple à faire évoluer.")
    pdf.bullet("Répartition par secteur : une simple agrégation SQL du champ secteur_activite, avec comptage.")
    pdf.bullet("Salaire moyen : calculé côté backend (AVG/MIN/MAX) sur les expériences en cours, en privilégiant salary_annuel (champ numérique) et en se rabattant sur le champ salaire historique si besoin ; les salaires à zéro sont exclus.")
    pdf.bullet("Cohérence déclaratif / réel : l'indicateur coherence_availability_poste_actuel mesure l'écart entre le statut déclaré (availability_status) et la présence d'un poste en cours bien réel dans EXPERIENCE_PRO, qui reste la source de vérité.")

    pdf.section_title("3.3 Visualisation (AdminDashboard.jsx)")
    pdf.bullet("KPI cards principales : Total Alumni actifs, Taux d'emploi à 6 mois, Taux d'emploi global.")
    pdf.bullet("KPI secondaires : Taux de complétion, Adéquation formation/emploi, Salaire moyen avec une jauge dynamique (bornes min/max recalculées sur les données réelles).")
    pdf.bullet("Donut : répartition par secteur, avec un maximum de 5 catégories visibles et un regroupement 'Autres'.")
    pdf.bullet("Barres horizontales : alumni par promotion, avec le % d'emploi et une timeline de maturité des cohortes (statut_maturite).")
    pdf.bullet("Barres verticales : répartition des types de contrat des expériences en cours.")

    # 4. Alertes
    pdf.chapter_title("4", "Alertes et Signaux Faibles")
    pdf.bullet("Si un alumni est en 'en_poste' sans qu'aucun poste soit coché 'actuel', une alerte ambrée s'affiche dans l'interface Parcours.")
    pdf.bullet("Si le tag 'adequation_formation' n'a aucune réponse, le dashboard affiche un état vide avec un rappel pour taguer une question.")
    pdf.bullet("Le taux de complétion sert aussi de signal : un taux bas trahit surtout des profils laissés incomplets.")

    # 5. Modele de Rapport Ministeriel
    pdf.chapter_title("5", "Modèle de Rapport d'Insertion pour les Autorités de Tutelle")
    pdf.body_text(
        "Le dashboard ne suffit pas : il faut aussi pouvoir sortir un document propre, à transmettre "
        "tel quel au ministère ou aux organismes de certification (CTI, HCERES). Voici le gabarit que "
        "j'ai retenu. Les indicateurs listés ci-dessous sont les mêmes que ceux vus en section 2, "
        "simplement mis sous une forme directement exploitable pour un rapport."
    )

    pdf.section_title("5.1 Informations Générales du Rapport")
    headers_info = ["Champ", "Valeur / Source"]
    widths_info = [50, 140]
    pdf.table_header(headers_info, widths_info)
    info_rows = [
        ["Institution", "Nom de l'établissement (ex: Ionis Education Group)"],
        ["Période couverte", "Année universitaire en cours (ex: 2025-2026)"],
        ["Promotion concernée", "Filtrée par annee_diplome (ex: Promo 2025)"],
        ["Date de génération", "Date courante au moment de l'export"],
        ["Source des données", "CRM Alumni - tables ETUDIANT, EXPERIENCE_PRO, REPONSE"],
    ]
    for i, r in enumerate(info_rows):
        pdf.table_row(r, widths_info, fill=(i % 2 == 0))
    pdf.ln(4)

    pdf.section_title("5.2 Indicateurs Clés du Rapport")
    headers_kpi = ["Indicateur", "Valeur attendue", "Calcul (simplifié)", "Exemple"]
    widths_kpi = [40, 48, 62, 40]
    pdf.table_header(headers_kpi, widths_kpi)
    kpi_rows = [
        ["Effectif de la promotion", "Nombre total d'inscrits", "Comptage des étudiants de la promo", "Promo 2025 : 128"],
        ["Taux d'emploi à 6 mois", "Pourcentage (%)", "Expériences démarrant <= 6 mois après la diplomation / effectif", "90 en poste sur 128 = 70 %"],
        ["Taux d'emploi à 12 mois", "Pourcentage (%) - pas encore calculé", "Même principe avec une fenêtre de 12 mois", "À définir"],
        ["Taux d'insertion totale", "Pourcentage (%)", "Alumni en poste à la date du rapport / effectif", "101 en poste sur 128 = 79 %"],
        ["Adéquation formation-emploi", "Pourcentage (%)", "Réponses 'Oui' au tag KPI / réponses exploitables", "33 'Oui' sur 42 = 79 %"],
        ["Salaire moyen par filière", "Euros (moyen, min, max)", "AVG / MIN / MAX des salaires annuels (> 0)", "moy. 41 200, min 35 000, max 49 000"],
        ["Répartition par secteur", "Tableau (secteur, %)", "Comptage des postes actuels par secteur", "Informatique 41 %, Finance 23 %"],
        ["Répartition géographique", "Tableau (pays / ville, %)", "Comptage des alumni par pays", "France 62 %, Maroc 23 %"],
    ]
    for i, r in enumerate(kpi_rows):
        pdf.table_row(r, widths_kpi, fill=(i % 2 == 0))
    pdf.ln(4)

    pdf.section_title("5.3 Diffusion du rapport")
    pdf.bullet("Fréquence : une publication annuelle, calée sur la campagne de collecte du questionnaire.")
    pdf.bullet("Destinataires : ministère de l'Enseignement supérieur, organismes de certification (CTI, HCERES) et direction de l'établissement.")
    pdf.bullet("Génération : depuis le dashboard admin (AdminDashboard.jsx), via un bouton d'export.")
    pdf.bullet("Archivage : chaque édition est horodatée et conservée, pour pouvoir répondre à un éventuel audit de conformité.")

    pdf.section_title("5.4 Exemple de Tableau de Synthèse par Promotion")
    headers_syn = ["Promotion", "Nb Alumni", "Emploi 6 mois", "Emploi 12 mois", "Adéquation"]
    widths_syn = [33, 30, 47, 47, 33]
    pdf.table_header(headers_syn, widths_syn)
    synth_rows = [
        ["Promo 2023", "120", "74%", "82%", "70%"],
        ["Promo 2024", "135", "78%", "85%", "73%"],
        ["Promo 2025", "128", "70%", "à définir", "70%"],
    ]
    for i, r in enumerate(synth_rows):
        pdf.table_row(r, widths_syn, fill=(i % 2 == 0))
    pdf.ln(2)
    pdf.body_text(
        "Tableau fictif, juste pour illustrer le format : à l'export, ces valeurs sont calculées "
        "automatiquement par le CRM à partir des données réelles."
    )

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
        "Ce guide decrit les processus qui permettent d'animer le reseau des anciens eleves et de le "
        "garder a jour via l'Alumni CRM. Il est destine au service Relations Entreprises et a "
        "l'equipe pedagogique. Chaque processus indique qui fait quoi : acteurs, etapes, outils "
        "utilises et indicateurs de suivi."
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
    pdf.bullet("Etapes : acces a la page Parcours (/alumni/career), ajout/modification/suppression d'une experience (entreprise, poste, secteur, contrat, dates, salaire, localisation), ajout de certifications (nom, organisme, date). La modification d'une experience existante passe par PUT /experiences/{id_experience} (transaction atomique, plus de delete+recreate en bloc). Ces mises a jour s'effectuent exclusivement depuis l'interface web ; aucune application mobile n'existe a ce jour.")
    pdf.bullet("Detection du poste actuel : si aucun poste n'est coche comme actuel, le systeme affiche automatiquement l'experience la plus recente. Une alerte ambrée est affichee si le statut est 'en_poste' mais aucun poste actuel n'est coche.")
    pdf.bullet("Outil CRM : page AlumniCareer.jsx -> endpoints POST /etudiants/{id}/experiences, PUT /experiences/{id_experience} (mise a jour atomique) et /etudiants/{id}/certifications.")
    pdf.section_title("3.2 Enrichissement du referentiel secteurs")
    pdf.bullet("Declencheur : un alumni saisit un secteur non encore enregistre.")
    pdf.bullet("Etape : le systeme propose 37 categories standardisees + 'Autre' avec saisie libre.")
    pdf.bullet("Outil CRM : composant de selection dans AlumniCareer.jsx, constantes dans constants.js (tableau SECTORS).")

    # Processus 3 : Questionnaire annuel
    pdf.chapter_title("4", "Processus de Questionnaire Annuel")
    pdf.section_title("4.1 Creation du questionnaire (admin)")
    pdf.bullet("Declencheur : le service des Relations Entreprises definit le questionnaire annuel.")
    pdf.bullet("Etapes : creation via l'interface (/admin/questionnaires), ajout de questions (texte, choix multiple, choix unique, liste deroulante, boolean, rating), attribution de tags KPI (ex: 'adequation_formation'), definition des conditions (masquage si en_recherche).")
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