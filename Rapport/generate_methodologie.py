import os
import docx
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def set_cell_bg(cell, color_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), color_hex)
    tcPr.append(shd)


def titre(doc, text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(18)
    run.font.color.rgb = RGBColor(0x1E, 0x40, 0xAF)
    return p


def sous_titre(doc, text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0x6B, 0x72, 0x80)
    return p


def chapitre(doc, num, text):
    p = doc.add_paragraph()
    run = p.add_run(f"{num}. {text}")
    run.bold = True
    run.font.size = Pt(13)
    run.font.color.rgb = RGBColor(0x1E, 0x40, 0xAF)
    return p


def section(doc, text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(11)
    return p


def body(doc, text):
    p = doc.add_paragraph(text)
    p.paragraph_format.space_after = Pt(4)
    return p


def bullet(doc, text):
    p = doc.add_paragraph(text, style='List Bullet')
    p.paragraph_format.space_after = Pt(2)
    return p


def indicateur_table(doc, rows):
    table = doc.add_table(rows=1, cols=2)
    table.style = 'Light Grid Accent 1'
    hdr = table.rows[0].cells
    hdr[0].text = 'Champ'
    hdr[1].text = 'Valeur'
    set_cell_bg(hdr[0], 'DBEAFE')
    set_cell_bg(hdr[1], 'DBEAFE')
    for champ, valeur in rows:
        r = table.add_row().cells
        r[0].text = champ
        r[1].text = valeur
        r[0].paragraphs[0].runs[0].font.bold = True
    doc.add_paragraph()
    return table


def generate():
    doc = Document()
    titre(doc, "Methodologie des indicateurs d'insertion")
    sous_titre(doc, "CRM Alumni (IONIS STM) - Fiche de reference complete et fidele au code")
    body(doc, "Chaque indicateur est documente avec sa formule exacte, ses tables/colonnes, ses exclusions et un exemple chiffre calcule comme le font les requetes SQL reelles du backend (routers/admin.py).")

    # 1. Principes
    chapitre(doc, 1, "Principes generaux")
    bullet(doc, "Comptes anonymises (ETUDIANT.date_anonymisation IS NOT NULL) exclus de tous les indicateurs.")
    bullet(doc, "Source de verite de l'emploi : EXPERIENCE_PRO (poste_actuel / experience en cours), pas availability_status.")
    bullet(doc, "Salaire : salary_annuel prioritaire si renseigne, sinon repli sur le champ texte salaire.")
    bullet(doc, "Une date de fin deja passee exclut toujours l'experience, meme si poste_actuel = TRUE.")

    # 2. Indicateurs
    chapitre(doc, 2, "Les 10 indicateurs avec exemples chiffres")

    section(doc, "2.1 Total Alumni actifs")
    indicateur_table(doc, [
        ("Formule", "COUNT(*) FROM ETUDIANT WHERE date_anonymisation IS NULL"),
        ("Tables / colonnes", "ETUDIANT.date_anonymisation"),
        ("Exclusions / limites", "Comptes anonymises exclus."),
        ("Exemple chiffre", "3 alumni (Rafik, Alice, Anonyme) -> 2 (Anonyme exclu)"),
    ])

    section(doc, "2.2 Alumni actifs (>= 1 experience)")
    indicateur_table(doc, [
        ("Formule", "COUNT(DISTINCT id_etudiant) FROM EXPERIENCE_PRO JOIN ETUDIANT non anonymises"),
        ("Tables / colonnes", "EXPERIENCE_PRO.id_etudiant, ETUDIANT.date_anonymisation"),
        ("Exclusions / limites", "Doublons exclus (DISTINCT). Aucune condition de date."),
        ("Exemple chiffre", "Rafik (2 exp), Alice (1 exp), Anonyme exclu -> 2"),
    ])

    section(doc, "2.3 Taux de completion / couverture")
    indicateur_table(doc, [
        ("Formule", "(alumni avec >= 1 experience / total alumni) x 100"),
        ("Tables / colonnes", "EXPERIENCE_PRO.id_etudiant, ETUDIANT.date_anonymisation"),
        ("Exclusions / limites", "Profil sans experience = incomplet."),
        ("Exemple chiffre", "2 non anonymises, 1 avec exp -> (1/2)x100 = 50 %"),
    ])

    section(doc, "2.4 Taux d'emploi a 6 mois")
    indicateur_table(doc, [
        ("Formule", "date_reference = annee_diplome || '-12-01' (diplomation juin + 6 mois). Exp. active si date_debut <= reference AND (date_fin IS NULL OR date_fin >= reference). Taux = SUM(emplois_6_mois)/SUM(total_diplomes) x 100 (promotions matures)."),
        ("Tables / colonnes", "PROMOTION.annee_diplome, ETUDIANT.id_promotion, EXPERIENCE_PRO.date_debut/fin"),
        ("Exclusions / limites", "Promotions non matures exclues du global -> statut en_attente, taux null."),
        ("Exemple chiffre", "2024 : 7/10 ; 2025 : 9/12 ; 2026 en_attente -> (16/22) = 72,7 %"),
    ])

    section(doc, "2.5 Taux d'emploi global (brut)")
    indicateur_table(doc, [
        ("Formule", "(etudiants en poste / total etudiants) x 100, par promotion puis somme"),
        ("Tables / colonnes", "EXPERIENCE_PRO.poste_actuel, ETUDIANT.id_promotion"),
        ("Exclusions / limites", "Un seul comptage par etudiant (DISTINCT). availability_status non utilise."),
        ("Exemple chiffre", "Promo 2024 : 8 en poste / 10 -> 80 %"),
    ])

    section(doc, "2.6 Adequation formation/emploi")
    indicateur_table(doc, [
        ("Formule", "(reponses 'Oui' / reponses exploitables) x 100. Question retenue : tag = 'adequation_formation' + questionnaire actif le plus recent."),
        ("Tables / colonnes", "QUESTION.tag, QUESTIONNAIRE.actif, REPONSE_QUESTIONNAIRE.reponses (JSON)"),
        ("Exclusions / limites", "Reponses 'non applicable' exclues du denominateur. Si aucune question taguee -> etat vide."),
        ("Exemple chiffre", "5 reponses dont 1 'Non applicable' (Oui,Oui,Oui,Non) -> 3/4 exploitables = 75 %"),
    ])

    section(doc, "2.7 Repartition par secteur")
    indicateur_table(doc, [
        ("Formule", "Par secteur : COUNT(DISTINCT id_etudiant) ayant poste_actuel = TRUE. % = count / total alumni actifs x 100."),
        ("Tables / colonnes", "ENTREPRISE.secteur_activite, EXPERIENCE_PRO.poste_actuel"),
        ("Exclusions / limites", "Secteur vide exclu. Un alumni multi-postes peut apparaitre dans plusieurs secteurs."),
        ("Exemple chiffre", "Info 3 (50%), Finance 2 (33%), Sante 1 (17%) -> donut"),
    ])

    section(doc, "2.8 Alumni par promotion")
    indicateur_table(doc, [
        ("Formule", "Par promotion : effectif, % en poste, couverture experience, salaire moyen. Promotions sans alumni exclues (HAVING COUNT > 0)."),
        ("Tables / colonnes", "PROMOTION, ETUDIANT.id_promotion, EXPERIENCE_PRO.poste_actuel/salaire"),
        ("Exclusions / limites", "Salaire moyen sur postes actuels uniquement."),
        ("Exemple chiffre", "2024 : 10, 80% ; 2025 : 12, 75% ; 2026 : 15, 73%"),
    ])

    section(doc, "2.9 Salaire moyen")
    indicateur_table(doc, [
        ("Formule", "AVG(CASE WHEN salary_annuel > 0 THEN salary_annuel ELSE salaire END). Filtres : poste_actuel = TRUE, salaire > 0, non anonymises. Fourchette jauge : si >= 5 salaires -> [min x 0.9, max x 1.1] ; sinon [val x 0.7, val x 1.3] + mention 'indicatif'."),
        ("Tables / colonnes", "EXPERIENCE_PRO.salary_annuel, salaire, poste_actuel"),
        ("Exclusions / limites", "Salaires nuls exclus. Echantillon < 5 : fourchette elargie, mention affichee."),
        ("Exemple chiffre", "38000, 42000, 50000 -> moyenne 43333 ; n=3 < 5 -> fourchette [30333, 56333] indicatif"),
    ])

    section(doc, "2.10 Repartition par type de contrat")
    indicateur_table(doc, [
        ("Formule", "Par type : COUNT(*) des experiences en cours (poste_actuel = TRUE ou dates en cours)"),
        ("Tables / colonnes", "EXPERIENCE_PRO.type_contrat, poste_actuel, date_debut/fin"),
        ("Exclusions / limites", "On compte des experiences (pas des alumni). Valeurs vides -> 'Non renseigne'."),
        ("Exemple chiffre", "CDI 6, CDD 3, Stage 1, vide -> 'Non renseigne' 1"),
    ])

    # 3. Endpoints
    chapitre(doc, 3, "Endpoints API")
    endpoints = [
        ("GET /admin/indicateurs", "Indicateurs principaux (taux emploi 6 mois/global, taux_reponse, alumni_actifs, salaire_moyen/min/max, coherence, hypothese, source_de_verite)"),
        ("GET /admin/indicateurs/secteurs", "Repartition par secteur {secteur, count} + total_alumni"),
        ("GET /admin/indicateurs/types-contrat", "Repartition par type de contrat (vides -> Non renseigne)"),
        ("GET /admin/indicateurs/kpi-tag?tag=X", "Valeur d'un KPI specifique (valeur, unite, distribution, detail)"),
        ("GET /admin/indicateurs/kpi-tags", "Tous les tags KPI des questionnaires actifs, calcules automatiquement"),
        ("GET /admin/indicateurs/kpi-tags-actifs", "Tags DISTINCT des questionnaires actifs"),
        ("GET /admin/indicateurs/partenaires", "Indicateurs anonymises restreints aux alumni 'partage_donnees' actif"),
    ]
    table = doc.add_table(rows=1, cols=2)
    table.style = 'Light Grid Accent 1'
    hdr = table.rows[0].cells
    hdr[0].text = 'Endpoint'
    hdr[1].text = 'Description'
    set_cell_bg(hdr[0], 'DBEAFE')
    set_cell_bg(hdr[1], 'DBEAFE')
    for e, d in endpoints:
        r = table.add_row().cells
        r[0].text = e
        r[1].text = d

    # 4. Cas limites
    chapitre(doc, 4, "Cas limites & alertes")
    bullet(doc, "Promotion sans fenetre 6 mois ecoulee : taux null, statut en_attente, jamais comptee dans le global.")
    bullet(doc, "Ecart statut declaratif / poste reel mesure et expose (coherence_availability_poste_actuel).")
    bullet(doc, "Adequation sans reponse : etat vide avec instructions pour taguer une question KPI.")
    bullet(doc, "Echantillon salaire < 5 : fourchette elargie + mention 'echantillon limite'.")
    bullet(doc, "RGPD : comptes anonymises exclus ; salaire des anciens postes neutralise (salaire = 0).")

    out = os.path.join(OUTPUT_DIR, "methodologie_indicateurs_insertion.docx")
    doc.save(out)
    print("DOCX genere :", out)


if __name__ == "__main__":
    generate()
