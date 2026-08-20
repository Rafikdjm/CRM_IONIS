"""Génère le rapport d'audit Word (Audit Final Alumni CRM)."""

from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import datetime

doc = Document()

# ── Styles globaux ────────────────────────────────────────────────
style = doc.styles["Normal"]
style.font.name = "Calibri"
style.font.size = Pt(11)
style.paragraph_format.space_after = Pt(6)
style.paragraph_format.line_spacing = 1.15

for level in range(1, 4):
    hs = doc.styles[f"Heading {level}"]
    hs.font.color.rgb = RGBColor(0x1B, 0x3A, 0x5C)

# ── Helper : couleur de fond d'en-tête de tableau ────────────────
def set_cell_shading(cell, color_hex):
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), color_hex)
    shading.set(qn("w:val"), "clear")
    cell._tc.get_or_add_tcPr().append(shading)


def add_status_cell(cell, status):
    color_map = {
        "FAIT": "27AE60",
        "PARTIEL": "F39C12",
        "MANQUANT": "E74C3C",
    }
    cell.text = status
    for p in cell.paragraphs:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            run.bold = True
            run.font.color.rgb = RGBColor.from_string(color_map.get(status, "000000"))
            run.font.size = Pt(10)


def make_table(doc, headers, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    # en-tête
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = h
        set_cell_shading(cell, "1B3A5C")
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.bold = True
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                run.font.size = Pt(10)
    # données
    for r_idx, row_data in enumerate(rows):
        for c_idx, val in enumerate(row_data):
            cell = table.rows[r_idx + 1].cells[c_idx]
            if headers[c_idx] == "Statut":
                add_status_cell(cell, val)
            else:
                cell.text = str(val)
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.font.size = Pt(10)
    return table


# ═══════════════════════════════════════════════════════════════════
# PAGE DE GARDE
# ═══════════════════════════════════════════════════════════════════
for _ in range(6):
    doc.add_paragraph("")

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("AUDIT FINAL & COMPLET")
run.bold = True
run.font.size = Pt(28)
run.font.color.rgb = RGBColor(0x1B, 0x3A, 0x5C)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("Projet Alumni CRM")
run.font.size = Pt(20)
run.font.color.rgb = RGBColor(0x1B, 0x3A, 0x5C)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("par rapport au cahier des charges\ndu sujet de stage PreMsc 2026")
run.font.size = Pt(14)
run.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

doc.add_paragraph("")

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run(f"Date de l'audit : 19 août 2026\nÉchéance soutenance : 19 septembre 2026")
run.font.size = Pt(12)
run.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# TABLE DES MATIÈRES (texte)
# ═══════════════════════════════════════════════════════════════════
doc.add_heading("Table des matières", level=1)
toc_items = [
    "1. MANAGEMENT",
    "   1.1 Cartographie des données",
    "   1.2 Charte RGPD / consentement",
    "   1.3 Stratégie de mise à jour des données",
    "   1.4 Indicateurs d'insertion",
    "2. INFORMATIQUE",
    "   2.1 Modélisation de la base de données",
    "   2.2 Interface admin",
    "   2.3 Interface étudiant / alumni",
    "   2.4 Import / Export",
    "3. LIVRABLES ATTENDUS",
    "   3.1 Rapport de stage",
    "   3.2 MCD / MLD",
    "   3.3 Prototype fonctionnel",
    "   3.4 Guide des processus d'animation du réseau",
    "4. TABLEAU RÉCAPITULATIF",
    "5. PLAN D'ACTION PRIORITAIRE AVANT LA SOUTENANCE",
]
for item in toc_items:
    p = doc.add_paragraph(item)
    p.paragraph_format.space_after = Pt(2)
doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# 1. MANAGEMENT
# ═══════════════════════════════════════════════════════════════════
doc.add_heading("1. MANAGEMENT", level=1)

# ── 1.1 Cartographie des données ─────────────────────────────────
doc.add_heading("1.1 Cartographie des données", level=2)
p = doc.add_paragraph()
run = p.add_run("Statut : FAIT")
run.bold = True
run.font.color.rgb = RGBColor(0x27, 0xAE, 0x60)

doc.add_heading("Données d'entrée (collectées via l'interface)", level=3)
doc.add_paragraph(
    "• Coordonnées : address, city, country, telephone, linkedin, email, "
    "email_academique, date_naissance — collectés à l'inscription "
    "(AlumniRegistration.jsx) et modifiables via le profil "
    "(AlumniProfile.jsx, AlumniProfileUpdate.jsx)",
    style="List Bullet",
)
doc.add_paragraph(
    "• Parcours antérieur : parcours_anterieur (text) — collecté à l'inscription "
    "(champs previous_education + previous_school dans AlumniRegistration.jsx:18-19) "
    "et affiché/modifiable dans AlumniProfile.jsx:257 et AlumniEditModal.jsx:236",
    style="List Bullet",
)
doc.add_paragraph(
    "• Compétences : skills (JSONB) — géré via tags dans AlumniProfile.jsx",
    style="List Bullet",
)

doc.add_heading("Données de sortie", level=3)
doc.add_paragraph(
    "• Entreprise : table ENTREPRISE (nom, secteur, pays, ville) liée via EXPERIENCE_PRO",
    style="List Bullet",
)
doc.add_paragraph(
    "• Poste : intitule_poste, type_contrat, poste_actuel dans EXPERIENCE_PRO",
    style="List Bullet",
)
doc.add_paragraph(
    "• Salaire : colonne salaire (numeric) dans EXPERIENCE_PRO — collecté dans "
    "AlumniCareer.jsx:121-122 et AlumniProfileUpdate.jsx:96-97, exposé dans le "
    "dashboard (admin.py:338-387)",
    style="List Bullet",
)

doc.add_heading("Modélisation", level=3)
doc.add_paragraph(
    "Toutes ces colonnes existent dans erd_alumni_crm.mmd (lignes 34-70). "
    "La relation ENTREPRISE → EXPERIENCE_PRO est de type 1-N confirmée."
)

# ── 1.2 Charte RGPD ──────────────────────────────────────────────
doc.add_heading("1.2 Charte RGPD / consentement", level=2)
p = doc.add_paragraph()
run = p.add_run("Statut : FAIT")
run.bold = True
run.font.color.rgb = RGBColor(0x27, 0xAE, 0x60)

rgpd_items = [
    ("Consentement horodaté",
     "CONSENTEMENT_RGPD.date_consentement (DATE NOT NULL) — erd_alumni_crm.mmd:84"),
    ("Modifiable",
     "UPSERT sur (id_etudiant, type_consentement) UNIQUE — migration 007_consentement_upsert.sql, endpoint rgpd.py:46"),
    ("Traçé en base",
     "Chaque action loguée dans AUDIT_LOG avec acteur (admin:nom | alumni:id | system) — erd_alumni_crm.mmd:119"),
    ("Export fonctionnel",
     "demandes_rgpd.py — workflow complet : demande → traitement → export JSON / anonymisation avec CASCADE (purge.py)"),
    ("Suppression fonctionnelle",
     "Anonymisation différée (6 mois par défaut via PURGE_DELAY_MONTHS) avec date_anonymisation sur ETUDIANT, FK CASCADE sur REPONSE_QUESTIONNAIRE — migration 009_purge_anonymises.sql"),
    ("Interface alumni",
     "AlumniConsent.jsx — toggle avec sauvegarde serveur"),
    ("Interface admin",
     "AdminRgpdDemandes.jsx (618 lignes) — workflow complet avec prise en charge, traitement, rejet, export, suppression"),
]
for title, desc in rgpd_items:
    doc.add_paragraph(f"• {title} : {desc}", style="List Bullet")

# ── 1.3 Stratégie de mise à jour ─────────────────────────────────
doc.add_heading("1.3 Stratégie de mise à jour des données (gouvernance)", level=2)
p = doc.add_paragraph()
run = p.add_run("Statut : PARTIEL")
run.bold = True
run.font.color.rgb = RGBColor(0xF3, 0x9C, 0x12)

doc.add_heading("Questionnaire annuel — FAIT", level=3)
doc.add_paragraph(
    "Le système de questionnaire annuel existe et fonctionne :"
)
doc.add_paragraph("Tables : QUESTIONNAIRE, QUESTION, REPONSE_QUESTIONNAIRE — migration 004_questionnaire_annuel.sql", style="List Bullet")
doc.add_paragraph("Création admin : AdminQuestionnaires.jsx + questionnaires.py", style="List Bullet")
doc.add_paragraph("Réponses alumni : AlumniSurvey.jsx", style="List Bullet")
doc.add_paragraph("KPI via tag sur QUESTION (migration 005_question_tag.sql) et conditionnee_statut_emploi (migration 006)", style="List Bullet")
doc.add_paragraph("Indicateurs calculés dans admin.py:328-387 (taux d'emploi, salaire moyen, taux 6 mois, taux adéquation)", style="List Bullet")

doc.add_heading("Relance proactive — MANQUANT", level=3)
p = doc.add_paragraph()
run = p.add_run(
    "Il n'existe AUCUN mécanisme de relance automatique. L'alumni doit se connecter "
    "de sa propre initiative. La seule utilisation de l'API Resend (otp.py:76-88) est "
    "pour l'envoi de codes OTP d'authentification. Il n'y a aucun email de relance, "
    "aucune notification push, aucun cron job de sollicitation."
)
run.italic = True

doc.add_paragraph("Ce qu'il faudrait ajouter :", style="List Bullet")
doc.add_paragraph("Un endpoint/scheduler (ex : cron hebdomadaire) identifiant les alumni sans réponse au questionnaire actif", style="List Bullet 2")
doc.add_paragraph("Des emails de relance automatisés via Resend (clé API déjà configurée dans .env et config.py:10-11)", style="List Bullet 2")
doc.add_paragraph("Idéalement 2-3 relances espacées, puis un flag \"injoignable\"", style="List Bullet 2")

# ── 1.4 Indicateurs d'insertion ──────────────────────────────────
doc.add_heading("1.4 Indicateurs d'insertion", level=2)
p = doc.add_paragraph()
run = p.add_run("Statut : FAIT")
run.bold = True
run.font.color.rgb = RGBColor(0x27, 0xAE, 0x60)

indicators = [
    ("Taux d'emploi global", "admin.py:164", "Hero card AdminDashboard.jsx:995"),
    ("Taux d'emploi à 6 mois", "admin.py (taux_6_mois)", "KPI card AdminDashboard.jsx"),
    ("Taux d'adéquation formation/emploi", "admin.py (taux_adquation)", "KPI card"),
    ("Salaire moyen", "admin.py:338-387", "Jauge demi-cercle dynamique AdminDashboard.jsx:1198-1215"),
    ("Taux de recommandation", "admin.py (taux_recommandation)", "KPI card"),
    ("Répartition sectorielle", "admin.py (repartition_secteur)", "Donut chart"),
    ("Évolution par promotion", "admin.py (evolution_promotions)", "Bar chart"),
    ("Taux de complétion profil", "admin.py (taux_completion)", "KPI card"),
    ("Types de contrat", "intégré", "Bar chart horizontal"),
    ("Maturité des cohortes", "admin.py (taux_6_mois par promo)", "Timeline"),
]
make_table(doc, ["Indicateur", "API (admin.py)", "Dashboard (AdminDashboard.jsx)"], indicators)

doc.add_paragraph("")
doc.add_paragraph(
    "Confirmé : Le \"taux d'emploi à 6 mois\" et le \"taux d'adéquation formation/emploi\" "
    "sont explicitement calculés et affichés, comme requis par le sujet de stage."
)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# 2. INFORMATIQUE
# ═══════════════════════════════════════════════════════════════════
doc.add_heading("2. INFORMATIQUE", level=1)

# ── 2.1 Modélisation BDD ─────────────────────────────────────────
doc.add_heading("2.1 Modélisation de la base de données", level=2)
p = doc.add_paragraph()
run = p.add_run("Statut : PARTIEL")
run.bold = True
run.font.color.rgb = RGBColor(0xF3, 0x9C, 0x12)

doc.add_heading("MCD/MLD existant", level=3)
mcd_files = [
    ("erd_alumni_crm.mmd", "148 lignes, 14 tables", "COMPLET et à jour (10/08/2026, vérifié 15/08/2026)", "FAIT"),
    ("erd_alumni_crm.docx", "40 Ko", "Version Word du précédent (15/08/2026)", "FAIT"),
    ("MCD_MLD V2.loo + MCD_MLD.loo + .lo1", "Binaires", "Phase initiale Looping (28/07/2026), supplanté par Mermaid", "Obsolète"),
    ("mcd_corrige.md", "102 lignes, 11 tables", "OBSOLÈTE — manque DEMANDE_RGPD, OTP_CODES, SCHEMA_MIGRATIONS", "À corriger"),
]
make_table(doc, ["Fichier", "Description", "Statut", "Verdict"], mcd_files)

doc.add_paragraph("")
doc.add_heading("Relation 1-N étudiant → expériences", level=3)
doc.add_paragraph(
    "CONFIRMÉE — erd_alumni_crm.mmd:18 : ETUDIANT ||--o{ EXPERIENCE_PRO (0,n expériences par étudiant). "
    "Historique de carrière multiple, pas un seul poste."
)

doc.add_heading("Ce qu'il faut corriger", level=3)
doc.add_paragraph(
    "Synchroniser ou supprimer mcd_corrige.md (alumni_crm_front/) pour qu'il reflète le schéma réel (14 tables)."
)

# ── 2.2 Interface admin ──────────────────────────────────────────
doc.add_heading("2.2 Interface admin", level=2)
p = doc.add_paragraph()
run = p.add_run("Statut : FAIT")
run.bold = True
run.font.color.rgb = RGBColor(0x27, 0xAE, 0x60)

doc.add_heading("Filtrage combiné promotion + secteur + entreprise", level=3)
doc.add_paragraph(
    "CONFIRMÉ — AlumniDirectory.jsx (719 lignes) : filtres AND-combinés dans un useMemo (l.72-114) :"
)
filter_items = [
    "Promotion : serveur (params.promotion, l.43)",
    "Secteur : client (a.sector, l.76-79), incluant \"Autre\"",
    "Entreprise : client (a.current_company, l.86-88)",
    "Disponibilité, compétence, contact autorisé, anonymisation : aussi disponibles",
    "Recherche texte sur nom/email/entreprise (l.103-111)",
]
for f in filter_items:
    doc.add_paragraph(f, style="List Bullet")

doc.add_heading("Dashboard avec indicateurs d'insertion", level=3)
doc.add_paragraph(
    "CONFIRMÉ — AdminDashboard.jsx (1266 lignes) : hero cards, jauge salaire dynamique, "
    "donuts, bar charts, timeline cohortes, KPI tags depuis questionnaires."
)

# ── 2.3 Interface alumni ─────────────────────────────────────────
doc.add_heading("2.3 Interface étudiant / alumni", level=2)
p = doc.add_paragraph()
run = p.add_run("Statut : FAIT")
run.bold = True
run.font.color.rgb = RGBColor(0x27, 0xAE, 0x60)

alumni_checks = [
    ("Formulaire d'inscription INITIAL distinct",
     "CONFIRMÉ — AlumniRegistration.jsx (632 lignes) : wizard multi-étapes (4 étapes), "
     "distinct de la mise à jour. Stocke alumni_id en localStorage après succès."),
    ("Mise à jour du profil professionnel",
     "CONFIRMÉE — AlumniProfileUpdate.jsx (425 lignes) : profil + carrière + certifications. "
     "AlumniCareer.jsx (674 lignes) : CRUD expériences avec modals de confirmation."),
    ("Suppression d'une entrée par erreur",
     "CONFIRMÉE — AlumniCareer.jsx:318-333 : bouton \"Supprimer\" + modal de confirmation. "
     "confirmRemove() (l.370) appelle careerAPI.delete() côté serveur. "
     "Bloqué sur comptes anonymisés (l.324-326)."),
]
for title, desc in alumni_checks:
    doc.add_paragraph(f"• {title} : {desc}", style="List Bullet")

# ── 2.4 Import / Export ──────────────────────────────────────────
doc.add_heading("2.4 Import / Export", level=2)
p = doc.add_paragraph()
run = p.add_run("Statut : FAIT")
run.bold = True
run.font.color.rgb = RGBColor(0x27, 0xAE, 0x60)

doc.add_paragraph("Import Excel — CONFIRMÉ :")
import_items = [
    "import_export.py:135-266 : POST /import/excel — accepte .xlsx, .xls, .csv",
    "21 colonnes supportées (l.27-51) : prénom, nom, email, téléphone, promotion, entreprise, poste, secteur, salaire, etc.",
    "Logique complète : création ETUDIANT + ENTREPRISE + EXPERIENCE_PRO, résolution de doublons email",
    "Template de téléchargement (GET /import/template)",
    "Frontend : ExcelImport.jsx (387 lignes) — drag & drop, preview 10 lignes, reconnaissance de colonnes",
    "Deuxième endpoint : automatisation.py:20-154 — POST /upload-etudiants/ via pandas + Pydantic",
]
for item in import_items:
    doc.add_paragraph(item, style="List Bullet")

doc.add_paragraph("")
doc.add_paragraph("Export — CONFIRMÉ :")
doc.add_paragraph("GET /import/export/alumni (import_export.py:304) — génère .xlsx", style="List Bullet")
doc.add_paragraph("Fallback client-side dans ExcelImport.jsx:119-156", style="List Bullet")

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# 3. LIVRABLES ATTENDUS
# ═══════════════════════════════════════════════════════════════════
doc.add_heading("3. LIVRABLES ATTENDUS", level=1)

# ── 3.1 Rapport de stage ─────────────────────────────────────────
doc.add_heading("3.1 Rapport de stage", level=2)
p = doc.add_paragraph()
run = p.add_run("Statut : MANQUANT")
run.bold = True
run.font.color.rgb = RGBColor(0xE7, 0x4C, 0x3C)

doc.add_paragraph(
    "Aucun brouillon de rapport de stage n'existe dans le projet."
)
rapport_items = [
    "generer_rapport.py (594 lignes) génère un document de préparation à l'oral (Preparation_Oral_Stage_CRM_Alumni.docx), PAS un rapport de stage",
    "Les 4 PDFs dans Rapport/ sont des livrables thématiques (cartographie, RGPD, stratégie, indicateurs), pas un rapport de stage structuré",
    "Aucun fichier contenant une introduction, conclusion, bibliographie, ou plan de rapport",
]
for item in rapport_items:
    doc.add_paragraph(item, style="List Bullet")

# ── 3.2 MCD/MLD ─────────────────────────────────────────────────
doc.add_heading("3.2 MCD / MLD", level=2)
p = doc.add_paragraph()
run = p.add_run("Statut : FAIT (avec réserve)")
run.bold = True
run.font.color.rgb = RGBColor(0x27, 0xAE, 0x60)

mcd_livrable = [
    ("Fichier principal", "alumni_crm_api/docs/erd_alumni_crm.mmd — 14 tables, à jour au 15/08/2026"),
    ("Version Word", "alumni_crm_api/docs/erd_alumni_crm.docx — 40 Ko, 15/08/2026"),
    ("Fichiers Looping", "MCD_MLD V2.loo (28/07/2026) — phase initiale, supplanté par Mermaid"),
    ("Note", "mcd_corrige.md dans alumni_crm_front/ est obsolète (manque 3 tables)"),
]
for title, desc in mcd_livrable:
    doc.add_paragraph(f"• {title} : {desc}", style="List Bullet")

# ── 3.3 Prototype fonctionnel ────────────────────────────────────
doc.add_heading("3.3 Prototype fonctionnel", level=2)
p = doc.add_paragraph()
run = p.add_run("Statut : FAIT")
run.bold = True
run.font.color.rgb = RGBColor(0x27, 0xAE, 0x60)

proto_items = [
    "Backend FastAPI opérationnel (14 routers, 50+ endpoints, Swagger à /docs)",
    "Frontend React/Vite complet (dist/ présent avec build production)",
    "Base PostgreSQL (14 tables, 12 migrations)",
    "Auth OTP + JWT (alumni), API Key + JWT (admin)",
    "Tests : 13 fichiers Vitest frontend, 66 assertions",
    "Import/Export Excel, RGPD bout en bout, questionnaire annuel",
]
for item in proto_items:
    doc.add_paragraph(item, style="List Bullet")

# ── 3.4 Guide animation réseau ───────────────────────────────────
doc.add_heading("3.4 Guide des processus d'animation du réseau", level=2)
p = doc.add_paragraph()
run = p.add_run("Statut : PARTIEL")
run.bold = True
run.font.color.rgb = RGBColor(0xF3, 0x9C, 0x12)

doc.add_paragraph("Pas de guide standalone dédié au service des relations entreprises.")
doc.add_paragraph(
    "Contenu partiel dans \"Stratégie de Mise à Jour des Données - Alumni CRM.pdf\" "
    "(Section 4, ~3 pages) couvrant :"
)
animation_items = [
    "Pilotage des campagnes de questionnaire",
    "Valorisation du réseau (filtrage dashboard, identification partenariats)",
    "Newsletter (levier d'animation, ciblage par consentement)",
]
for item in animation_items:
    doc.add_paragraph(item, style="List Bullet")
doc.add_paragraph(
    "Il manque un document dédié et complet avec : processus opérationnels, rôles, "
    "fréquence des actions, templates de communication."
)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# 4. TABLEAU RÉCAPITULATIF
# ═══════════════════════════════════════════════════════════════════
doc.add_heading("4. TABLEAU RÉCAPITULATIF", level=1)

recap = [
    ("1", "Cartographie des données", "FAIT", "AlumniRegistration.jsx, AlumniProfile.jsx, AlumniCareer.jsx, erd_alumni_crm.mmd"),
    ("2", "Charte RGPD / consentement", "FAIT", "rgpd.py, demandes_rgpd.py, purge.py, AlumniConsent.jsx, AdminRgpdDemandes.jsx, migrations 007-010"),
    ("3", "Stratégie de mise à jour", "PARTIEL", "questionnaires.py, AdminQuestionnaires.jsx, AlumniSurvey.jsx — MANQUANT : relance proactive"),
    ("4", "Indicateurs d'insertion", "FAIT", "admin.py:164,338-387, AdminDashboard.jsx:935-1263"),
    ("5", "Modélisation BDD", "PARTIEL", "erd_alumni_crm.mmd (OK), mcd_corrige.md (obsolète)"),
    ("6", "Interface admin", "FAIT", "AlumniDirectory.jsx:72-114, AdminDashboard.jsx, AdminPromotions.jsx"),
    ("7", "Interface alumni", "FAIT", "AlumniRegistration.jsx, AlumniProfileUpdate.jsx, AlumniCareer.jsx:318-370"),
    ("8", "Import / Export", "FAIT", "import_export.py:135-266, automatisation.py:20-154, ExcelImport.jsx"),
    ("9", "Rapport de stage", "MANQUANT", "Aucun fichier"),
    ("10", "MCD / MLD", "FAIT", "erd_alumni_crm.mmd, erd_alumni_crm.docx (réserve : mcd_corrige.md obsolète)"),
    ("11", "Prototype fonctionnel", "FAIT", "dist/, requirements.txt, 14 routers, 13 fichiers test"),
    ("12", "Guide animation réseau", "PARTIEL", "Section 4 du PDF Stratégie de Mise à Jour — pas de guide standalone"),
]
make_table(doc, ["#", "Point", "Statut", "Fichiers / Routes concernés"], recap)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# 5. PLAN D'ACTION
# ═══════════════════════════════════════════════════════════════════
doc.add_heading("5. PLAN D'ACTION PRIORITAIRE AVANT LA SOUTENANCE (19 septembre 2026)", level=1)

doc.add_heading("Urgence CRITIQUE — Manques documentaires (rédaction)", level=2)
critical = [
    ("1", "Rédiger le rapport de stage",
     "Aucun brouillon n'existe. C'est le livrable le plus important.",
     "2-3 semaines",
     "Introduction/contexte, missions, analyse conception (MCD/MLD, architecture), "
     "réalisation technique, résultats/indicateurs, conclusion/limites, bibliographie"),
    ("2", "Rédiger le guide d'animation du réseau",
     "Document dédié au service des relations entreprises.",
     "2-3 jours",
     "Processus opérationnels, rôles/responsabilités, fréquence des actions "
     "(campagnes questionnaire, relances, newsletter), templates de communication. "
     "Le contenu de la Section 4 du PDF Stratégie peut servir de base"),
]
make_table(doc, ["#", "Action", "Justification", "Estimation", "Détails"], critical)

doc.add_paragraph("")
doc.add_heading("Urgence MOYENNE — Manques techniques (code)", level=2)
medium = [
    ("3", "Implémenter la relance proactive",
     "Le questionnaire annuel fonctionne mais personne n'est sollicité.",
     "1-2 jours",
     "Endpoint/cron identifiant les alumni sans réponse + emails de relance via Resend "
     "(clé API déjà configurée dans .env) + 2-3 relances espacées"),
    ("4", "Synchroniser mcd_corrige.md",
     "Le fichier dans alumni_crm_front/ affiche 11 tables au lieu de 14.",
     "30 min",
     "Copier depuis erd_alumni_crm.mmd ou supprimer pour éviter la confusion"),
]
make_table(doc, ["#", "Action", "Justification", "Estimation", "Détails"], medium)

doc.add_paragraph("")
doc.add_heading("Attention — Non bloquant", level=2)
doc.add_paragraph("Migration 003 absente (numérotation sautée de 002 à 004) — cosmétique, ne bloque rien", style="List Bullet")
doc.add_paragraph("AlumniProfileUpdate.jsx:417 empêche la suppression de la dernière expérience — à documenter comme choix UX", style="List Bullet")
doc.add_paragraph("Les fichiers .loo/.lo1 de Looping (juillet 2026) sont obsolètes — à nettoyer ou archiver", style="List Bullet")

# ── Sauvegarde ────────────────────────────────────────────────────
output_path = r"C:\Users\PC\OneDrive\Desktop\stage\Audit_Final_Alumni_CRM.docx"
doc.save(output_path)
print(f"Document généré : {output_path}")
