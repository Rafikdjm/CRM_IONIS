"""Génère le canva de soutenance Word rédigé comme une préparation d'étudiant (ton naturel), aligné sur le PPTX 20 slides."""

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import datetime

NAVY = "1B3A5C"

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
    hs.font.name = "Calibri"


def set_cell_shading(cell, color_hex):
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), color_hex)
    shading.set(qn("w:val"), "clear")
    cell._tc.get_or_add_tcPr().append(shading)


def cell_text(cell, text, bold=False, white=False, size=10, center=False):
    cell.text = ""
    p = cell.paragraphs[0]
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(str(text))
    run.bold = bold
    run.font.size = Pt(size)
    if white:
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)


def add_table(headers, rows, col_widths=None):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        set_cell_shading(table.rows[0].cells[i], NAVY)
        cell_text(table.rows[0].cells[i], h, bold=True, white=True, size=10, center=True)
    for r, row_data in enumerate(rows):
        for c, val in enumerate(row_data):
            cell_text(table.rows[r + 1].cells[c], val, size=10)
    if col_widths:
        for i, w in enumerate(col_widths):
            for row in table.rows:
                row.cells[i].width = Cm(w)
    doc.add_paragraph()
    return table


def note(text):
    p = doc.add_paragraph()
    run = p.add_run("Note pour moi : " + text)
    run.italic = True
    run.font.color.rgb = RGBColor.from_string("777777")


def visual(text):
    p = doc.add_paragraph()
    run = p.add_run("Visuel à poser : " + text)
    run.bold = True
    run.font.color.rgb = RGBColor(0x1B, 0x3A, 0x5C)


def slide_header(num, title, duration):
    h = doc.add_heading(f"Slide {num} — {title}", level=1)
    r = h.add_run(f"   ({duration})")
    r.font.color.rgb = RGBColor.from_string("AAAAAA")
    r.font.size = Pt(11)


def sub(text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = True
    run.font.color.rgb = RGBColor(0x27, 0xAE, 0x60)


def bullets(items):
    for it in items:
        doc.add_paragraph(it, style="List Bullet")


# ═══════════════════════════════════════════════════════════════════
# PAGE DE GARDE
# ═══════════════════════════════════════════════════════════════════
for _ in range(5):
    doc.add_paragraph("")

t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = t.add_run("Canva de soutenance")
run.font.size = Pt(26)
run.bold = True
run.font.color.rgb = RGBColor.from_string(NAVY)

st = doc.add_paragraph()
st.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = st.add_run("Alumni CRM — suivi du parcours étudiant et valorisation du réseau des anciens diplômés")
run.font.size = Pt(13)
run.font.color.rgb = RGBColor.from_string("555555")

doc.add_paragraph()

info = doc.add_paragraph()
info.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = info.add_run("Mon support de préparation pour la soutenance (Pré-MSc, IONIS-STM)\n15 minutes de présentation, puis 10 minutes de questions et 15 minutes de débriefing\nRafik Djemadi — tuteur : Joly Donfack — soutenance le 18 septembre 2026")
run.font.size = Pt(11)
run.font.color.rgb = RGBColor.from_string("777777")

doc.add_page_break()

# ── MODE D'EMPLOI ─────────────────────────────────────────────────
doc.add_heading("Comment je me sers de ce document", level=1)
intro = doc.add_paragraph()
intro.add_run("Ce canva, c'est ma trame de préparation. Pour chaque slide je note trois choses : ")
run = intro.add_run("ce que je raconte, ce que j'affiche, et ce que je dois avoir en tête")
run.bold = True
intro.add_run(" pour ne pas me perdre. Le ton est volontairement à la première personne : c'est comme ça que je vais parler le jour J.")

bullets(
    [
        "Le temps est serré (15 min max), donc chaque slide a une durée butoir. Je me suis chronométré en répétant, tout passe de justesse et il me reste un peu de marge.",
        "Ce qui est en italique gris, ce sont mes petites notes perso : les pièges à éviter et les questions que je m'attends à avoir.",
        "Je me suis basé sur la consigne de soutenance 2026 : 15 min de présentation + 10 min de questions + 15 min de débriefing, jury en huis clos (responsable de filière, un intervenant externe et mon tuteur).",
        "Tout ce que je cite (chiffres, fonctionnalités) doit coller au rapport de stage. Si l'écart est trop gros, le jury le remarque.",
        "Les slides 6 à 10 (les étapes) sont volontairement courtes : 30 secondes chacune, juste de quoi raconter la démarche sans entrer dans le détail technique trop tôt.",
    ]
)

doc.add_paragraph()
doc.add_heading("Répartition du temps", level=1)
overview = [
    ("1", "Carte d'identité + plan", "0:30"),
    ("2", "L'établissement d'accueil : IONIS-STM", "0:45"),
    ("3", "Contexte et pourquoi ce sujet", "0:45"),
    ("4", "Problématique et objectifs", "1:15"),
    ("5", "Méthodologie, dans quel ordre j'ai travaillé", "0:45"),
    ("6", "Étape 1 — Cadrage", "0:30"),
    ("7", "Étape 2 — Modélisation", "0:30"),
    ("8", "Étape 3 — Backend", "0:30"),
    ("9", "Étape 4 — Frontend", "0:30"),
    ("10", "Étape 5 — Tests + audits", "0:30"),
    ("11", "Architecture de l'application", "1:00"),
    ("12", "Modèle de données et parcours étudiant", "0:45"),
    ("13", "Le RGPD, dès le départ", "1:00"),
    ("14", "Audit de sécurité : les failles corrigées", "0:45"),
    ("15", "Démo 1 : l'espace alumni", "1:30"),
    ("16", "Démo 2 : l'espace admin et les indicateurs", "1:15"),
    ("17", "Difficultés rencontrées et leçons", "0:45"),
    ("18", "Les 5 livrables Management", "0:30"),
    ("19", "Bilan, limites et pistes", "0:45"),
    ("20", "Conclusion", "0:15"),
    ("", "Total", "15:00"),
]
add_table(["#", "Slide", "Durée"], overview, [1.0, 13.0, 2.0])

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# SLIDE 1
# ═══════════════════════════════════════════════════════════════════
slide_header(1, "Carte d'identité + plan", "0:30")
sub("Ce que je raconte")
doc.add_paragraph(
    "\u00ab Bonjour, je m'appelle Rafik Djemadi, je suis en Pré-MSc à IONIS-STM. "
    "Pendant ce stage, j'ai conçu et développé Alumni CRM : une application pour suivre le parcours des étudiants "
    "et valoriser le réseau des anciens diplômés. Je vais vous parler du contexte, de ce que j'ai construit, "
    "je vous ferai une courte démo, et je terminerai par le bilan. \u00bb"
)
visual("Slide de garde avec le titre du projet et le logo, puis le plan en 4 points sur la droite.")
note("Je ne lis jamais la slide. Si je la lis, j'ai déjà perdu l'attention du jury.")
doc.add_paragraph()

# ── SLIDE 2 ───────────────────────────────────────────────────────
slide_header(2, "L'établissement d'accueil : IONIS-STM", "0:45")
sub("Ce que je raconte")
doc.add_paragraph(
    "L'école où j'ai réalisé ce stage, c'est IONIS-STM. C'est une école privée du Groupe IONIS, le premier groupe "
    "d'enseignement supérieur privé en France. IONIS-STM, c'est la double compétence tech et management : créée en "
    "2002 sous le nom « Masters Epita », devenue IONIS-STM en 2009. On y forme des profils hybrides en Pré-MSc, "
    "MSc1 et MSc2 — reconversion ou poursuite d'études — dans le développement, la cybersécurité, la data, le "
    "management et le marketing digital. Plusieurs centaines de diplômés sortent chaque année."
)
visual("Le logo IONIS-STM + 2-3 chiffres clés (création, double compétence, filières).")
note("Je reste bref : juste de quoi situer l'établissement avant de parler du besoin métier.")
doc.add_paragraph()

# ── SLIDE 3 ───────────────────────────────────────────────────────
slide_header(3, "Contexte et pourquoi ce sujet", "0:45")
sub("Ce que je raconte")
doc.add_paragraph(
    "Le point de départ, c'est un constat simple : l'établissement ne suivait quasi pas le parcours de ses étudiants "
    "une fois diplômés. Les données d'insertion étaient dispersées (emails, formulaires papier, appels), les "
    "indicateurs se calculaient à la main, le réseau alumni était inactif et rien n'était formalisé côté RGPD. "
    "Or le réseau des anciens, c'est un vrai atout pour l'école (parrainage, alternance, visibilité), et pouvoir "
    "montrer le taux d'insertion des promotions, c'est un argument fort pour attirer de futurs étudiants."
)
visual("4 faits courts identifiés (dispersé, à la main, inactif, non formalisé) + le logo de l'école.")
note("Quarante-cinq secondes, pas une de plus. Les détails techniques viendront après.")
doc.add_paragraph()

# ── SLIDE 4 ───────────────────────────────────────────────────────
slide_header(4, "Problématique et objectifs", "1:15")
sub("Ce que je raconte")
doc.add_paragraph(
    "La question que je me suis posée en arrivant, c'est : comment suivre le parcours complet de l'étudiant, de "
    "l'inscription jusqu'au réseau des anciens, tout en restant conforme au RGPD ? J'ai ensuite décliné ça en "
    "quatre objectifs : centraliser les données sur un cycle de vie unique, fiabiliser les indicateurs d'insertion, "
    "animer le réseau alumni, et intégrer la conformité dès la conception."
)
visual("Problématique encadrée au centre, les 4 objectifs en colonnes autour.")
note("C'est le moment de montrer que je comprends le besoin métier, avant même de parler technique.")
doc.add_paragraph()

# ── SLIDE 5 ───────────────────────────────────────────────────────
slide_header(5, "Méthodologie, dans quel ordre j'ai travaillé", "0:45")
sub("Ce que je raconte")
doc.add_paragraph(
    "Je n'ai pas attaqué le code tout de suite. D'abord le cadrage et la modélisation avec Looping (MCD puis MLD), "
    "ensuite le backend, puis le frontend, et j'ai terminé par des audits : cohérence entre la base et l'API, puis "
    "sécurité, avant la rédaction des livrables Management. C'est un stage de substitution mené en solo : chaque "
    "fonctionnalité était développée, testée manuellement et consolidée avant la suivante."
)
visual("Frise horizontale à 5 étapes : cadrage → modélisation → backend → frontend → audits & livrables.")
note("Je peux glisser une phrase sur les livrables demandés (cartographie des données, charte RGPD) : ça rassure le jury sur le sérieux.")
doc.add_paragraph()

# ── SLIDE 6 ───────────────────────────────────────────────────────
slide_header(6, "Étape 1 — Cadrage", "0:30")
sub("Ce que je raconte")
doc.add_paragraph(
    "J'ai surtout écouté avant de coder : entretiens avec l'équipe de l'école pour comprendre le besoin réel, "
    "état des lieux du suivi Excel, et validation des 4 objectifs. J'ai cadré deux espaces dès le départ : "
    "l'école (admin) et les anciens étudiants (alumni)."
)
visual("La capture de la page de connexion avec ses deux espaces + les 4 objectifs en rappel.")
note("Slide courte, volontairement. Juste situer le besoin avant de plonger dans le technique.")
doc.add_paragraph()

# ── SLIDE 7 ───────────────────────────────────────────────────────
slide_header(7, "Étape 2 — Modélisation", "0:30")
sub("Ce que je raconte")
doc.add_paragraph(
    "Avant d'écrire le moindre code, j'ai modélisé : le MCD avec Looping pour poser les entités métier, puis le "
    "MLD avec 14 tables réparties en 5 domaines (données étudiantes, parcours professionnel, RGPD, questionnaires, "
    "infrastructure). Ces 14 tables ont été reprises en 17 migrations versionnées, et j'ai cartographié les données "
    "personnelles — une exigence RGPD."
)
visual("Le MCD en haut, le MLD en dessous, et une phrase qui dit « 14 tables → 17 migrations ».")
note("Je montre le diagramme sans le lire dans le détail : quelques entités suffisent.")
doc.add_paragraph()

# ── SLIDE 8 ───────────────────────────────────────────────────────
slide_header(8, "Étape 3 — Backend", "0:30")
sub("Ce que je raconte")
doc.add_paragraph(
    "Côté backend, j'ai pris FastAPI, surtout pour la documentation automatique : les 84 endpoints se retrouvent "
    "dans Swagger sans rien écrire à la main. Les 17 migrations sont versionnées, donc chaque évolution du schéma "
    "est tracée et rejouable. Et la sécurité dès le début : clé API admin, sessions JWT par rôle, code OTP à 6 "
    "chiffres validé 10 minutes, emails via Resend."
)
visual("Un extrait de Swagger avec quelques routes documentées, et la DSL auth en rappel.")
note("Je cite Swagger parce que ça montre une vraie discipline : documenter l'API, c'est gagner du temps pour le front.")
doc.add_paragraph()

# ── SLIDE 9 ───────────────────────────────────────────────────────
slide_header(9, "Étape 4 — Frontend", "0:30")
sub("Ce que je raconte")
doc.add_paragraph(
    "Pour l'interface, React avec Vite, en SPA, avec un thème clair et sombre. Le frontend compte 14 routes, réparties "
    "en deux espaces bien séparés : l'espace alumni (inscription guidée, profil, parcours, questionnaire, consentements) "
    "et l'espace admin (tableau de bord KPI, annuaire filtrable, import / export Excel). Chaque écran consomme "
    "l'API, et les routes sont protégées par rôle dans le navigateur."
)
visual("Une capture de l'espace alumni + une de l'espace admin, côte à côte.")
note("Je n'entre pas dans chaque écran, ce sera le rôle de la démo.")
doc.add_paragraph()

# ── SLIDE 10 ──────────────────────────────────────────────────────
slide_header(10, "Étape 5 — Tests + audits", "0:30")
sub("Ce que je raconte")
doc.add_paragraph(
    "Pour la validation : les parcours clés (inscription, profil, questionnaire, admin) testés manuellement, plus le "
    "build de production et le lint comme filet de contrôle. Ensuite deux audits : un audit de cohérence pour que "
    "chaque objet de l'API existe vraiment en base, et un audit de sécurité dont je reparle à la slide 14. Je le "
    "dis clairement : il n'y a pas encore de vraie suite de tests automatisés, c'est le chantier n°1 avant la "
    "production. Le rapport le mentionne, je préfère l'assumer."
)
visual("Un dashboard cohérent + la mention des deux audits (cohérence, sécurité).")
note("C'est une limite assumée, pas une excuse. Le jury apprécie qu'on connaisse ses propres lacunes.")
doc.add_paragraph()

# ── SLIDE 11 ──────────────────────────────────────────────────────
slide_header(11, "Architecture de l'application", "1:00")
sub("Ce que je raconte")
doc.add_paragraph(
    "C'est une architecture en trois couches. À gauche, l'interface React : espace alumni, espace admin, 14 routes, "
    "thème clair / sombre. Au milieu, l'API FastAPI : 84 endpoints REST documentés dans Swagger, avec la sécurité "
    "(OTP à 6 chiffres, sessions JWT par rôle, clé API admin) et les emails via Resend. Enfin PostgreSQL : "
    "14 tables, 17 migrations versionnées, contraintes CHECK et unicité pour le RGPD. Le fil rouge : rien ne se fait "
    "hors de cette chaîne — chaque écran appelle l'API, chaque objet de l'API existe en base, aucun secret dans le dépôt."
)
visual("Schéma 3-tiers avec des flèches : React → FastAPI → PostgreSQL, et la sécurité transversale en bas.")
note("J'explique avec le geste, toujours dans le même sens. Je ne cite que 2-3 endpoints en exemple, pas les 84.")
doc.add_paragraph()

# ── SLIDE 12 ──────────────────────────────────────────────────────
slide_header(12, "Modèle de données et parcours étudiant", "0:45")
sub("Ce que je raconte")
doc.add_paragraph(
    "Le modèle de données couvre tout le cycle de vie : le dossier de l'étudiant, ses expériences et certifications, "
    "mais aussi ses consentements. Concrètement, un ancien étudiant s'inscrit en plusieurs étapes avec un code de "
    "vérification, puis il complète son profil, renseigne son parcours professionnel et répond chaque année à un "
    "questionnaire d'insertion."
)
visual("Un extrait du MLD (le schéma des tables), pas la base entière.")
note("Pas besoin de tout montrer : quelques tables et les flèches entre elles suffisent à faire comprendre.")
doc.add_paragraph()

# ── SLIDE 13 ──────────────────────────────────────────────────────
slide_header(13, "Le RGPD, dès le départ", "1:00")
sub("Ce que je raconte")
doc.add_paragraph(
    "Le RGPD, je l'ai intégré dès la conception, pas après coup. Concrètement : quatre types de consentement traçables "
    "et réellement consommés (un refus d'enquête bloque le questionnaire, un refus de contact déclenche "
    "l'anonymisation), un workflow d'export et de suppression avec un verrou anti-double-traitement, le choix entre "
    "anonymiser et supprimer définitivement, une purge différée de 6 mois, la durée de conservation affichée et un "
    "contact DPO. À côté, j'ai rédigé la cartographie des données et une charte RGPD."
)
visual("Les 4 consentements affichés, plus un petit schéma du workflow export/suppression + durée + DPO.")
note("Question très probable ici : la différence entre anonymisation et suppression. Je réfléchis déjà à ma réponse.")
doc.add_paragraph()

# ── SLIDE 14 ──────────────────────────────────────────────────────
slide_header(14, "Audit de sécurité : les failles corrigées", "0:45")
sub("Ce que je raconte")
doc.add_paragraph(
    "L'audit de sécurité a mis en évidence plusieurs failles réelles, toutes corrigées et versionnées : des routes "
    "d'écriture non protégées (clé API admin ajoutée), une route d'upload morte et ouverte (supprimée), un IDOR où "
    "un alumni pouvait lire et modifier les réponses d'un autre (vérification de propriétaire ajoutée), des comptes "
    "anonymisés redevenus modifiables (garde centralisée sur 12 points d'écriture), et la suppression d'une promotion "
    "avec des étudiants rattachés (409 sauf force explicite)."
)
visual("3-4 fautes → correctifs affichés comme avant / après, plus un écran du workflow RGPD.")
note("Je parle vite mais je reste précis : dire « IDOR » et l'expliquer en une phrase, c'est un point crédible auprès du jury.")
doc.add_paragraph()

# ── SLIDE 15 ──────────────────────────────────────────────────────
slide_header(15, "Démo 1 : l'espace alumni", "1:30")
sub("Ce que je raconte")
doc.add_paragraph(
    "Je vais vous montrer le parcours d'un ancien étudiant qui s'inscrit : il reçoit un code à 6 chiffres, complète "
    "son profil, ajoute une expérience, et donne ses consentements. Tout se passe en plusieurs étapes guidées, donc "
    "l'utilisateur ne se perd pas."
)
visual("4 captures maximum, enchaînées : inscription → code → profil → expérience → consentement.")
note("Démo chronométrée vraiment. Si ça dépasse, je saute l'import Excel sans faire de commentaire. Base allumée et compte démo prêts avant de commencer.")
doc.add_paragraph()

# ── SLIDE 16 ──────────────────────────────────────────────────────
slide_header(16, "Démo 2 : l'espace admin et les indicateurs", "1:15")
sub("Ce que je raconte")
doc.add_paragraph(
    "Côté administrateur, le tableau de bord affiche les huit indicateurs de base : total alumni, actifs, complétion, "
    "emploi à 6 mois, emploi global, salaires, secteur, type de contrat — plus un indicateur dérivé par question "
    "taguée KPI, sans toucher au backend. L'annuaire se filtre par promotion, secteur, entreprise ou compétence, et "
    "il y a l'import / export à partir d'un template Excel, validé ligne par ligne."
)
visual("Le tableau de bord avec ses graphiques, puis l'annuaire filtrable.")
note("Je définis clairement le taux d'emploi : expériences actives à la date de référence ; cohorte jeune = « en cours », jamais un faux chiffre.")
doc.add_paragraph()

# ── SLIDE 17 ──────────────────────────────────────────────────────
slide_header(17, "Difficultés rencontrées et leçons", "0:45")
sub("Ce que je raconte")
doc.add_paragraph(
    "J'assume ce qui a coincé. Un incident de synchronisation OneDrive a fait perdre des fichiers frontend : leçon, "
    "versionner avant de coder, dépôt Git initié en cours de stage. La modification d'une expérience n'était pas "
    "atomique : une route PUT en une seule transaction règle ça. Deux administrateurs pouvaient traiter la même "
    "demande RGPD : un statut intermédiaire et un verrou l'empêchent. Et j'ai corrigé un taux d'emploi qui comptait "
    "des expériences terminées : seules les expériences actives comptent, sinon la cohorte est marquée « en cours ». "
    "Chaque incident a produit une leçon écrite dans le rapport, section 3.2."
)
visual("5 paires « difficulté → leçon » précédées d'une flèche, ton sobre.")
note("Ne pas minimiser : le jury sait que ça arrive, il veut voir comment je réagis et ce que j'en retiens.")
doc.add_paragraph()

# ── SLIDE 18 ──────────────────────────────────────────────────────
slide_header(18, "Les 5 livrables Management", "0:30")
sub("Ce que je raconte")
doc.add_paragraph(
    "Le sujet avait aussi un volet Management, et il est couvert par cinq documents : la cartographie des données, "
    "la charte de conformité RGPD, l'analyse des indicateurs d'insertion (les 8 indicateurs avec leurs formules), "
    "la stratégie de mise à jour des données, et le guide des processus d'animation du réseau (7 processus). Tous "
    "sont générés par des scripts, donc régénérables et toujours synchronisés avec le rapport — annexes E à I."
)
visual("Les 5 titres en liste, chacun à côté d'un petit rendu de sa page de couverture.")
note("Une phrase par document, pas un résumé de chacun : c'est un aperçu du sérieux, pas un cours.")
doc.add_paragraph()

# ── SLIDE 19 ──────────────────────────────────────────────────────
slide_header(19, "Bilan, limites et pistes", "0:45")
sub("Ce que je raconte")
doc.add_paragraph(
    "Ce que je retiens : j'ai touché à toutes les couches, du modèle de données au front, avec un vrai travail "
    "RGPD et des audits qui ont fiabilisé l'application. Les limites, assumées : la suite de tests automatisés "
    "à construire (prérequis avant la production), pas de chiffrement applicatif, et un déploiement côté école "
    "qui demande de l'infrastructure. Comme pistes : à court terme les tests et les relances newsletter, à moyen "
    "terme le mentorat et le chiffrement, à long terme une PWA et la notification de violation (article 33 RGPD)."
)
visual("Trois colonnes simples : bilan / limites / pistes.")
note("Ne pas dire que tout est parfait. Une limite assumée, c'est plus crédible et ça lance souvent une bonne discussion.")
doc.add_paragraph()

# ── SLIDE 20 ──────────────────────────────────────────────────────
slide_header(20, "Conclusion", "0:15")
sub("Ce que je raconte")
doc.add_paragraph(
    "En une phrase : Alumni CRM est un prototype opérationnel, documenté, avec son volet Management couvert, et "
    "conforme au RGPD, avec deux espaces pensés chacun pour son utilisateur. Je vous remercie et je suis prêt à "
    "répondre à vos questions."
)
visual("Un simple \u00ab Merci \u00bb, sobre.")
note("Pendant les 10 minutes de questions : je note, je réponds court, et je ne coupe pas la parole. Le débriefing de 15 minutes me concerne moins, je laisse faire.")
doc.add_paragraph()

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# CHECKLIST + DÉROULÉ JOUR J
# ═══════════════════════════════════════════════════════════════════
doc.add_heading("Checklist avant le jour J", level=1)
checklist = [
    "Je me suis passé ma présentation deux fois au chronomètre : sous les 15 min, avec un peu de marge.",
    "La démo tourne sur le poste qui sera branché au vidéoprojecteur : base démarrée, compte démo prêt, navigateur ouvert sur la bonne page.",
    "Tous mes rendus sont sur une clé USB (rapport PDF, support, sources) : la consigne le conseille et ça couvre les pépins.",
    "Plan B si la démo plante : support en PDF et captures d'écran de secours sur le même poste.",
    "Questions que je m'attends à avoir et que j'ai préparées : calcul du taux d'emploi, anonymisation vs suppression, failles de sécurité corrigées (IDOR, clé API), pourquoi FastAPI/PostgreSQL.",
    "Mes chiffres sont cohérents avec le rapport : 84 endpoints, 14 tables, 17 migrations versionnées, 14 routes frontend, 8 indicateurs de base, 5 livrables Management.",
    "Tenue et posture : je parle au jury, je ne lis pas mes slides, je marque des pauses.",
    "Le jour J : 15 min de présentation, 10 min de questions, 15 min de débriefing. Jury en huis clos : responsable de filière, un intervenant externe et mon tuteur (en visio Teams s'il ne peut pas venir).",
]
bullets(checklist)

section = doc.sections[0]
footer_p = section.footer.paragraphs[0]
footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = footer_p.add_run(f"Canva de soutenance — Alumni CRM — préparé le {datetime.date.today().strftime('%d/%m/%Y')}")
run.font.size = Pt(8)
run.font.color.rgb = RGBColor.from_string("888888")

OUT = "Canva Soutenance - Alumni CRM v2.docx"
doc.save(OUT)
print(f"OK : {OUT}")