# -*- coding: utf-8 -*-
"""Génère le support PowerPoint de soutenance (refait sur les docs du dossier Rapport)."""

import os
import struct
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

NAVY = RGBColor(0x15, 0x20, 0x42)
BLUE = RGBColor(0x2E, 0x6F, 0xDB)
GREEN = RGBColor(0x2E, 0xA0, 0x6E)
GRAY = RGBColor(0x60, 0x6A, 0x7E)
LIGHT = RGBColor(0xEA, 0xF0, 0xFB)
LIGHTGREEN = RGBColor(0xE7, 0xF3, 0xEB)
RED = RGBColor(0xC0, 0x39, 0x2B)
REDBG = RGBColor(0xFB, 0xEC, 0xF0)
AMBER = RGBColor(0xE0, 0x8A, 0x1E)
AMBERBG = RGBColor(0xFC, 0xF1, 0xDF)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

SW, SH = 13.333, 7.5
prs = Presentation()
prs.slide_width = Inches(SW)
prs.slide_height = Inches(SH)
BLANK = prs.slide_layouts[6]

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "image")


def png_dims(path):
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.size
    except Exception:
        with open(path, "rb") as f:
            data = f.read(33)
        w = struct.unpack(">I", data[16:20])[0]
        h = struct.unpack(">I", data[20:24])[0]
        return w, h


def box(title, left, top, width, height, text, size=18, color=NAVY, bold=False,
        align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, line_spacing=1.05):
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    lines = text if isinstance(text, list) else [text]
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        r = p.add_run()
        r.text = ln
        r.font.name = "Calibri"
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.color.rgb = color
    return tb


def bullets(title, items, left=0.7, top=1.5, width=12.0, height=5.3, size=17):
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    for i, (txt, lvl) in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.line_spacing = 1.12
        p.space_after = Pt(10)
        if lvl:
            p.level = lvl
        if txt.startswith("> "):
            p.level = 1
            txt = txt[2:]
        r = p.add_run()
        r.text = txt
        r.font.name = "Calibri"
        r.font.size = Pt(size - (1 if (lvl or txt.startswith("")) and lvl else 0) * 2)
        r.font.color.rgb = NAVY if (lvl == 0 and not txt.startswith(">")) else GRAY


def notes(text):
    ns = slide.notes_slide
    ns.notes_text_frame.text = text


def header(title, duration, subtitle=None):
    box("h", 0.0, 0.0, 13.333, 1.15, title, size=27, bold=True)
    box("u", 0.55, 1.02, 2.6, 0.09, "", size=2)
    ln = slide.shapes[-1]
    ln.fill.solid()
    ln.fill.fore_color.rgb = GREEN
    if subtitle:
        box("s", 0.0, 1.18, 13.333, 0.4, subtitle, size=15, color=GRAY)
    box("d", 12.15, 0.22, 0.95, 0.4, duration, size=12, color=GRAY, align=PP_ALIGN.RIGHT)
    box("p", 0.0, 7.05, 13.333, 0.35, "", size=2)
    ln2 = slide.shapes[-1]
    ln2.fill.solid()
    ln2.fill.fore_color.rgb = NAVY


def rect(x, y, w, h, color):
    shp = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    shp.line.fill.background()
    return shp


def picture_fit(path, x, y, max_w, max_h):
    w, h = png_dims(path)
    k = min(max_w / w, max_h / h)
    nw, nh = w * k, h * k
    slide.shapes.add_picture(path, Inches(x + (max_w - nw) / 2), Inches(y + (max_h - nh) / 2),
                             Inches(nw), Inches(nh))
    return nw, nh


def arch_card(x, y, w, h, title, items, bar_color):
    rect(x, y, w, h, LIGHT)
    rect(x, y, w, 0.62, bar_color)
    box("", x + 0.15, y, w - 0.3, 0.62, title, size=15, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    body = []
    for it in items:
        if it.startswith("> "):
            body.append("   " + it[2:])
        else:
            body.append("• " + it)
    box("", x + 0.2, y + 0.8, w - 0.4, h - 1.0, body, size=11.5, color=NAVY, line_spacing=1.12)


def connector(x, y):
    shp = slide.shapes.add_shape(6, Inches(x), Inches(y), Inches(0.26), Inches(0.4))
    shp.fill.solid()
    shp.fill.fore_color.rgb = BLUE
    shp.line.fill.background()


def kpi_card(x, y, w, name, formule, exemple):
    h = 1.15
    rect(x, y, w, h, LIGHT)
    rect(x, y, w, 0.09, BLUE)
    box("", x + 0.15, y + 0.2, w - 0.3, 0.32, name, size=12.5, bold=True)
    box("", x + 0.15, y + 0.56, w - 0.3, 0.3, formule, size=10, color=GRAY)
    box("", x + 0.15, y + 0.86, w - 0.3, 0.3, "ex. " + exemple, size=10, color=GREEN, bold=True)


def pb_sol(x, y, w, title, desc):
    rect(x, y, w, 1.18, REDBG)
    rect(x, y, 0.1, 1.18, RED)
    box("", x + 0.25, y + 0.1, w - 0.45, 0.4, title, size=13, bold=True, color=RED)
    box("", x + 0.25, y + 0.55, w - 0.45, 0.55, desc, size=10.5, color=NAVY)


def sol_box(x, y, w, title, desc):
    rect(x, y, w, 1.18, LIGHTGREEN)
    rect(x, y, 0.1, 1.18, GREEN)
    box("", x + 0.25, y + 0.1, w - 0.45, 0.4, title, size=13, bold=True, color=GREEN)
    box("", x + 0.25, y + 0.55, w - 0.45, 0.55, desc, size=10.5, color=NAVY)


# ════════════════════════ SLIDE 1 — GARDE ════════════════════════
slide = prs.slides.add_slide(BLANK)
rect(0, 0, SW, 7.5, NAVY)
rect(0, 6.62, SW, 0.88, BLUE)
box("t", 0.9, 1.9, 11.5, 1.6, "Alumni CRM", size=48, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
box("st", 1.3, 2.9, 10.7, 1.0,
    "Suivre le parcours des étudiants, valoriser le réseau des anciens diplômés",
    size=20, color=RGBColor(0xC7, 0xD4, 0xEE), align=PP_ALIGN.CENTER)
box("id", 1.0, 4.3, 11.3, 2.0, [
    "Rafik Djemadi — Pré-MSc, IONIS-STM",
    "Stage : conception et développement full-stack d'une application de gestion des alumni",
    "Tuteur pédagogique : Joly Donfack",
    "Soutenance : 18 septembre 2026",
    "",
    "Plan : l'école → le besoin → la conception → la démo → le bilan",
], size=15, color=WHITE, align=PP_ALIGN.CENTER)
notes("Bonjour, je m'appelle Rafik Djemadi, je suis en Pré-MSc Informatique & Management à IONIS-STM. "
      "Pendant ce stage de substitution, j'ai conçu et développé Alumni CRM : une application pour suivre le "
      "parcours des étudiants et valoriser le réseau des anciens diplômés. Mon tuteur pédagogique est Joly "
      "Donfack, et la soutenance a lieu le 18 septembre 2026. Je vais vous parler du contexte, de ce que j'ai "
      "construit, une courte démo, puis je terminerai sur le bilan.")

# ════════════════════════ SLIDE 2 — ÉCOLE D'ACCUEIL ════════════════════════
slide = prs.slides.add_slide(BLANK)
header("L'établissement d'accueil : IONIS-STM", "0:30")
logo = os.path.join(HERE, "ionis-stm-logo.png")
if os.path.exists(logo):
    pic_w, pic_h = png_dims(logo)
    k = min(3.0 / pic_w, 1.6 / pic_h)
    slide.shapes.add_picture(logo, Inches(0.9), Inches(2.0), Inches(pic_w * k), Inches(pic_h * k))
bullets("id", [
    ("Une école du Groupe IONIS, premier groupe d'enseignement supérieur privé en France", 0),
    ("Créée en 2002 sous le nom « Masters Epita », devenue IONIS-STM en 2009", 0),
    ("La première école dédiée à la double compétence Tech & Management", 0),
    ("Pré-MSc, MSc1 et MSc2 — reconversion et poursuite d'études après un premier diplôme", 0),
    ("Filières : développement, cybersécurité, data, management, marketing digital", 0),
    ("Plusieurs centaines de diplômés formés chaque année", 0),
], left=4.4, top=1.6, size=15)
notes("L'école où j'ai réalisé ce stage, c'est IONIS-STM : une école privée du Groupe IONIS, le premier groupe "
      "d'enseignement supérieur privé en France. Créée en 2002 sous le nom 'Masters Epita', elle est devenue "
      "IONIS-STM en 2009. C'est la première école française dédiée à la double compétence tech & management. "
      "On y forme des profils de niveau Pré-MSc, MSc1 et MSc2, en reconversion ou en poursuite d'études, dans "
      "plusieurs filières, et plusieurs centaines de diplômés sortent chaque année. C'est mon école de stage : "
      "Pré-MSc Informatique & Management.")

# ════════════════════════ SLIDE 3 — CONTEXTE ════════════════════════
slide = prs.slides.add_slide(BLANK)
header("Pourquoi ce projet", "0:45")
bullets("b", [
    ("Aucun outil pour suivre un étudiant de l'inscription jusqu'à sa vie professionnelle.", 0),
    ("Données dispersées : emails, formulaires papier, appels — rien de structuré.", 0),
    ("Indicateurs calculés à la main, croisements longs et source d'erreurs.", 0),
    ("Réseau alumni inanimé : aucun canal pour rester en contact.", 0),
    ("RGPD : aucun workflow traçable sur les données personnelles.", 0),
    ("Prouver l'insertion = un argument fort pour recruter de futurs étudiants.", 0),
], size=18)
notes("Le point de départ, c'est un constat simple, confirmé dès le cadrage : l'école n'avait aucun outil pour "
      "suivre un étudiant de son inscription jusqu'à son évolution professionnelle. Les données d'insertion "
      "traînaient un peu partout, les indicateurs se calculaient à la main, le réseau alumni était inactif et "
      "rien n'était formalisé côté RGPD. Or montrer le taux d'insertion, c'est un argument fort pour recruter "
      "de futurs étudiants. Quatre défis sont ressortis de ce constat, je les détaille à la slide suivante.")

# ════════════════════════ SLIDE 4 — PROBLÉMATIQUE ════════════════════════
slide = prs.slides.add_slide(BLANK)
header("Problématique et objectifs", "1:00")
rect(0.7, 1.5, 11.9, 1.35, LIGHT)
box("p1", 0.95, 1.68, 11.4, 1.0,
    "Comment suivre le parcours complet de l'étudiant, de l'inscription jusqu'au réseau des anciens, "
    "tout en restant conforme au RGPD ?", size=19, bold=True)
bullets("o", [
    ("1. Centraliser les données : un cycle de vie unique, de l'inscription au parcours professionnel", 0),
    ("2. Fiabiliser les indicateurs d'insertion : taux d'emploi, salaires, adéquation", 0),
    ("3. Animer le réseau alumni : questionnaire annuel, newsletter", 0),
    ("4. Intégrer le RGPD dès la conception : consentements, export, suppression", 0),
], left=0.95, top=3.15, size=18)
notes("La question que je me suis posée en arrivant : comment suivre le parcours complet de l'étudiant, de "
      "l'inscription jusqu'au réseau des anciens, tout en restant conforme au RGPD ? J'ai décliné ça en quatre "
      "objectifs repris du sujet de stage : centraliser les données, fiabiliser les indicateurs d'insertion, "
      "animer le réseau et intégrer la conformité dès le départ. C'est le moment de montrer que j'ai compris "
      "le besoin métier avant de parler technique.")


# ════════════════════════ SLIDE 5 — MÉTHODOLOGIE ════════════════════════
slide = prs.slides.add_slide(BLANK)
header("Comment j'ai travaillé", "0:45")
steps = [
    ("1. Cadrage", "recueil du besoin, 4 objectifs validés"),
    ("2. Modélisation", "MCD / MLD avec Looping, cartographie des données"),
    ("3. Backend", "FastAPI, 84 endpoints, 17 migrations versionnées"),
    ("4. Frontend", "React + Vite, deux espaces (admin / alumni), 14 routes"),
    ("5. Audits & livrables", "cohérence base / API, sécurité, 5 documents"),
]
x = 0.55
lane_y, lane_h = 3.9, 2.5
for i, (t, d) in enumerate(steps):
    rect(x, lane_y, 2.32, lane_h, LIGHT if i % 2 == 0 else LIGHTGREEN)
    tbx = box("", x + 0.12, lane_y + 0.15, 2.08, 0.6, t, size=16, bold=True, align=PP_ALIGN.CENTER)
    box("", x + 0.12, lane_y + 0.9, 2.08, 1.4, d, size=11.5, color=GRAY, align=PP_ALIGN.CENTER)
    if i < len(steps) - 1:
        connector(x + 2.32, lane_y + 0.95)
    x += 2.42
box("", 0.7, 1.9, 11.9, 0.6,
    "Démarche itérative : une fonctionnalité développée et consolidée avant la suivante.", size=17, bold=True)
box("", 0.7, 2.5, 11.9, 1.0,
    "Stage de substitution proposé par IONIS-STM, mené en solo avec une autonomie totale sur les choix "
    "techniques.", size=15, color=GRAY)
notes("Je n'ai pas attaqué le code tout de suite. J'ai suivi une démarche itérative : cadrage, modélisation, "
      "backend, frontend, puis des audits — cohérence entre la base et l'API, et sécurité — avant la rédaction "
      "des livrables Management. C'est un stage de substitution proposé par l'école, mené en solo, donc avec "
      "une autonomie totale sur les choix techniques : chaque fonctionnalité était développée, testée "
      "manuellement puis consolidée avant de passer à la suivante.")

# ══════════════════ SLIDE 6 — ÉTAPE 1 : CADRAGE ══════════════════
slide = prs.slides.add_slide(BLANK)
header("Étape 1 — Cadrage", "0:30", "recueil du besoin et du contexte métier")
bullets("c1", [
    ("Entretiens avec l'équipe de l'école pour comprendre le besoin réel", 0),
    ("État des lieux : le suivi se fait dans des fichiers Excel, sans vue d'ensemble", 0),
    ("4 objectifs validés : cycle de vie étudiant, insertion, réseau alumni, RGPD", 0),
    ("Cadrage des deux espaces : école (admin) et anciens étudiants (alumni)", 0),
], left=0.7, top=1.75, width=6.2, height=5.0, size=16)
picture_fit(os.path.join(IMG, "login_light.png"), 7.25, 1.75, 5.4, 4.6)
box("cap_cadrage", 7.25, 6.4, 5.4, 0.4, "la porte d'entrée : deux espaces dès le départ", size=13, color=GRAY, align=PP_ALIGN.CENTER)
notes("Pour commencer, j'ai surtout écouté. Le vrai besoin, c'était de suivre les étudiants une fois sortis de "
      "l'école, jusqu'à leur vie pro. Jusque-là, tout partait dans des fichiers Excel un peu n'importe comment. "
      "J'ai posé quatre objectifs avec l'équipe, le RGPD dès le départ, et j'ai vu qu'il fallait vraiment deux "
      "espaces : un pour l'école, un pour les anciens.")

# ══════════════════ SLIDE 7 — ÉTAPE 2 : MODÉLISATION ══════════════════
slide = prs.slides.add_slide(BLANK)
header("Étape 2 — Modélisation", "0:30", "MCD / MLD avec Looping, cartographie des données")
bullets("c2", [
    ("MCD : les entités du métier (étudiant, expérience, certification, consentement…)", 0),
    ("Modélisation avec Looping, des documents clairs et réutilisables", 0),
    ("14 tables normalisées en 5 domaines, reprises en 17 migrations versionnées", 0),
    ("Cartographie des données personnelles, exigée par le RGPD", 0),
], left=0.7, top=1.75, width=6.2, height=5.0, size=16)
picture_fit(os.path.join(IMG, "MCD.png"), 7.25, 1.75, 5.4, 2.35)
box("cap_mcd", 7.25, 4.15, 5.4, 0.35, "MCD — entités métier", size=13, color=GRAY, align=PP_ALIGN.CENTER)
picture_fit(os.path.join(IMG, "MLD.png"), 7.25, 4.55, 5.4, 2.35)
box("cap_mld", 7.25, 6.95, 5.4, 0.35, "MLD — 14 tables", size=13, color=GRAY, align=PP_ALIGN.CENTER)
notes("Avant d'écrire le moindre code, j'ai modélisé. Le MCD avec Looping a permis de poser toutes les entités "
      "du métier, puis je suis passé au MLD : 14 tables réparties en 5 domaines — données étudiantes, parcours "
      "professionnel, RGPD, questionnaires, infrastructure. J'en ai profité pour cartographier les données "
      "personnelles, question RGPD. Les 14 tables ont été versionnées en 17 migrations. Le diagramme, je ne le "
      "lis pas, je le montre juste.")

# ══════════════════ SLIDE 8 — ÉTAPE 3 : BACKEND ══════════════════
slide = prs.slides.add_slide(BLANK)
header("Étape 3 — Backend", "0:30", "FastAPI, 84 endpoints, 17 migrations versionnées")
bullets("c3", [
    ("FastAPI : une API REST documentée automatiquement dans Swagger", 0),
    ("84 endpoints répartis par domaine (dossiers, expériences, entreprises, RGPD…)", 0),
    ("17 migrations versionnées : chaque évolution du schéma est tracée et rejouable", 0),
    ("Sécurité : clé API admin, sessions JWT par rôle, code OTP à 6 chiffres (TTL 10 min)", 0),
    ("Emails OTP et relances via Resend (console en développement)", 0),
    ("Fin de stage : newsletter ciblée, relance questionnaire, indicateurs partenaires anonymisés, export groupé RGPD, PUT expérience atomique", 0),
], left=0.7, top=1.75, width=6.2, height=5.0, size=15)
picture_fit(os.path.join(IMG, "swagger_light.png"), 7.25, 1.75, 5.4, 4.9)
notes("Côté backend, j'ai pris FastAPI, surtout pour la documentation automatique : les 84 endpoints se "
      "retrouvent dans Swagger sans rien écrire à la main. Les 17 migrations sont versionnées, donc chaque "
      "modification du schéma est tracée et rejouable. J'ai mis la sécurité dès le début : clé API admin, "
      "sessions JWT avec des rôles strictement séparés, code OTP à 6 chiffres avec 10 minutes de validité. "
      "Les emails partent via Resend, en console pendant le développement. En fin de stage j'ai ajouté cinq "
      "endpoints demandés par le rapport : newsletter ciblée, relance du questionnaire annuel, indicateurs "
      "partenaires agrégés et anonymisés, export groupé des demandes RGPD, et la mise à jour atomique d'une "
      "expérience.")

# ══════════════════ SLIDE 9 — ÉTAPE 4 : FRONTEND ══════════════════
slide = prs.slides.add_slide(BLANK)
header("Étape 4 — Frontend", "0:30", "React + Vite, deux espaces (admin / alumni), 14 routes")
bullets("c4", [
    ("React + Vite : composants réutilisables, thème clair / sombre", 0),
    ("14 routes frontend, protection par rôle dans le navigateur", 0),
    ("Espace alumni : inscription guidée, profil, parcours, questionnaire, consentements", 0),
    ("Espace admin : tableau de bord KPI, annuaire filtrable, import / export Excel", 0),
    ("Chaque écran consomme les endpoints de l'API", 0),
], left=0.7, top=1.75, width=6.2, height=5.0, size=16)
picture_fit(os.path.join(IMG, "anC_profil_light_1.png"), 7.25, 1.75, 5.4, 2.35)
box("cap_alumni", 7.25, 4.15, 5.4, 0.35, "espace alumni", size=13, color=GRAY, align=PP_ALIGN.CENTER)
picture_fit(os.path.join(IMG, "anB_promotions_light.png"), 7.25, 4.55, 5.4, 2.35)
box("cap_admin", 7.25, 6.95, 5.4, 0.35, "espace admin", size=13, color=GRAY, align=PP_ALIGN.CENTER)
notes("Pour l'interface, React avec Vite, en SPA. Deux espaces vraiment séparés : les anciens s'inscrivent en "
      "étapes, complètent leur profil et répondent au questionnaire ; l'école, elle, a le tableau de bord, "
      "l'annuaire filtrable et l'import / export Excel. Le frontend compte 14 routes, avec une protection par "
      "rôle : un token admin n'accède pas aux routes alumni, et inversement. Thème clair ou sombre, au cas où.")

# ══════════════════ SLIDE 10 — ÉTAPE 5 : TESTS + AUDITS ══════════════════
slide = prs.slides.add_slide(BLANK)
header("Étape 5 — Tests + audits", "0:30", "validation manuelle, cohérence base / API, sécurité")
bullets("c5", [
    ("Parcours clés testés manuellement : inscription, profil, questionnaire, admin", 0),
    ("Build de production (vite build) + lint (oxlint) comme filet de contrôle", 0),
    ("Audit de cohérence : chaque objet de l'API vérifié contre les 14 tables", 0),
    ("Audit de sécurité : failles corrigées — détail slide 14", 0),
    ("Chantier restant avant production : une vraie suite de tests automatisés", 0),
], left=0.7, top=1.75, width=6.2, height=5.0, size=16)
picture_fit(os.path.join(IMG, "anB_dashboard_light_3.png"), 7.25, 1.75, 5.4, 4.9)
box("cap_audit", 7.25, 6.6, 5.4, 0.4, "un tableau de bord cohérent avec les données", size=13, color=GRAY, align=PP_ALIGN.CENTER)
notes("Pour la validation, je me suis appuyé sur les parcours clés testés manuellement, le build de production "
      "et le lint. Deux audits ensuite : un audit de cohérence entre la base et l'API — chaque objet renvoyé "
      "doit exister en base — et un audit de sécurité dont je reparle à la slide 14. Je le dis clairement : il "
      "n'y a pas encore de vraie suite de tests automatisés dans le dépôt, c'est le chantier n°1 avant une mise "
      "en production. Le rapport le mentionne, et je préfère l'assumer que le cacher.")

# ══════════════════ SLIDE 11 — ARCHITECTURE DE L'APPLICATION ══════════════════
slide = prs.slides.add_slide(BLANK)
header("Architecture de l'application", "1:00", "une architecture trois tiers : React → FastAPI → PostgreSQL")
arch_card(0.55, 1.75, 3.85, 3.9, "Front — React + Vite", [
    "espace alumni & espace admin",
    "14 routes, thème clair / sombre",
    "inscription guidée + questionnaire",
    "dashboard KPI, annuaire, import / export",
    "protection des routes par rôle",
], BLUE)
connector(4.5, 3.35)
arch_card(4.85, 1.75, 3.85, 3.9, "API — FastAPI", [
    "84 endpoints REST",
    "doc Swagger générée automatiquement",
    "auth OTP / JWT par rôle / clé API admin",
    "import & export Excel / CSV",
    "emails : Resend (console en dev)",
], NAVY)
connector(8.8, 3.35)
arch_card(9.15, 1.75, 3.85, 3.9, "Base — PostgreSQL", [
    "14 tables, 5 domaines",
    "17 migrations versionnées",
    "contraintes CHECK + unicité (RGPD)",
    "rejeu complet validé sur base vide",
    "purge différée des comptes anonymisés",
], GREEN)
box("", 0.55, 5.9, 12.4, 0.7,
    "Chaque écran consomme l'API ; chaque objet de l'API existe dans la base. Une sécurité sur toutes les "
    "couches : clé API admin, JWT par rôle, code OTP, aucun secret dans le dépôt (.env).", size=14, bold=True)
notes("L'architecture est en trois tiers, comme le décrit le rapport. À gauche, le frontend React avec ses deux "
      "espaces et ses 14 routes. Au milieu, l'API FastAPI avec ses 84 endpoints et la sécurité : clé API admin, "
      "JWT par rôle, OTP. Enfin PostgreSQL, 14 tables, 17 migrations versionnées. J'insiste sur le point qui me "
      "semble important : rien ne se fait hors de cette chaîne — chaque écran appelle l'API, chaque objet de "
      "l'API existe en base, et aucun secret ne traîne dans le dépôt.")

# ════════════════════════ SLIDE 12 — MODÈLE DE DONNÉES ════════════════════════
slide = prs.slides.add_slide(BLANK)
header("Le modèle de données et le parcours étudiant", "0:45")
box("", 0.7, 1.3, 6.0, 5.4, [
    "Tout le cycle de vie est couvert :",
    "  • dossier étudiant / alumni",
    "  • expériences et certifications",
    "  • consentements RGPD",
    "",
    "Parcours de l'alumni :",
    "  • inscription en étapes avec code OTP",
    "  • profil + parcours professionnel",
    "  • questionnaire annuel d'insertion",
], size=16)
picture_fit(os.path.join(IMG, "MLD.png"), 7.0, 1.35, 5.6, 5.0)
notes("Le modèle de données couvre tout le cycle de vie : le dossier de l'étudiant, ses expériences et "
      "certifications, mais aussi ses consentements. Concrètement, un ancien étudiant s'inscrit en plusieurs "
      "étapes avec un code de vérification, puis il complète son profil, renseigne son parcours professionnel "
      "et répond chaque année à un questionnaire. Je montre quelques tables et les flèches entre elles, pas la "
      "base entière.")

# ════════════════════════ SLIDE 13 — RGPD ════════════════════════
slide = prs.slides.add_slide(BLANK)
header("Le RGPD, pris dès le départ", "0:45")
bullets("rgpd", [
    ("4 types de consentement, tracés et réellement consommés (contact, partage, enquêtes, newsletter)", 0),
    ("Demandes d'export et de suppression via un workflow avec verrou anti-double-traitement", 0),
    ("Choix entre anonymiser et supprimer définitivement (suppression réservée aux doublons)", 0),
    ("Purge différée paramétrable : 6 mois par défaut (purge.py --dry-run)", 0),
    ("Durée de conservation affichée à l'alumni + contact DPO", 0),
    ("Livrables d'accompagnement : cartographie des données + charte RGPD", 0),
], size=16)
notes("Le RGPD, je l'ai intégré dès la conception, pas après coup : quatre types de consentement traçables et "
      "réellement consommés — un refus d'enquêtes bloque le questionnaire, un refus de contact déclenche "
      "l'anonymisation. Des demandes d'export et de suppression avec un verrou qui empêche deux administrateurs "
      "de traiter la même demande. Une distinction claire entre anonymiser et supprimer définitivement. Une "
      "purge différée de 6 mois. Et la durée de conservation est affichée à l'alumni, avec un contact DPO. "
      "Question très probable : la différence entre anonymisation et suppression.")

# ══════════════════ SLIDE 14 — AUDIT DE SÉCURITÉ ══════════════════
slide = prs.slides.add_slide(BLANK)
header("Audit de sécurité : les failles corrigées", "0:45", "un passage au crible, des correctifs versionnés")
bullets("sec", [
    ("Routes POST/DELETE (promotions, entreprises) non protégées", 0),
    ("> clé API admin obligatoire sur les écritures sensibles", 1),
    ("Route d'upload morte et ouverte", 0),
    ("> router supprimé, import via la route protégée uniquement", 1),
    ("IDOR : un alumni pouvait lire et modifier les réponses d'un autre", 0),
    ("> require_owner_or_admin sur les ressources personnelles", 1),
    ("Comptes anonymisés redevenus modifiables", 0),
    ("> garde « refuser_compte_anonymise » sur 12 points d'écriture", 1),
    ("Suppression d'une promotion avec étudiants rattachés", 0),
    ("> 409 sauf ?force=true", 1),
], left=0.7, top=1.6, width=6.4, height=5.3, size=14)
picture_fit(os.path.join(IMG, "anB_demandes_rgpd_light.png"), 7.6, 1.7, 5.0, 4.8)
box("cap_sec", 7.6, 6.55, 5.0, 0.4, "le workflow RGPD, rendu robuste par l'audit", size=13, color=GRAY, align=PP_ALIGN.CENTER)
notes("L'audit de sécurité a permis de corriger plusieurs failles réelles, toutes versionnées. Des routes "
      "d'écriture n'étaient pas protégées — clé API admin ajoutée. Une route d'upload était morte et ouverte — "
      "elle a été supprimée. Un alumni pouvait lire ou modifier les réponses d'un autre — c'est le classique "
      "IDOR, corrigé par une vérification de propriétaire. Les comptes anonymisés pouvaient être modifiés — "
      "garde centralisée sur douze points d'écriture. Et la suppression d'une promotion avec des étudiants "
      "renvoie désormais 409 sauf force explicite. J'ai aussi remplacé les vérifs environ par la gestion des "
      "IntegrityError pour éliminer les courses TOCTOU.")

# ════════════════════════ SLIDE 15 — DÉMO ALUMNI ════════════════════════
slide = prs.slides.add_slide(BLANK)
header("Démo — l'espace alumni", "1:15")
shots = [
    ("anC_inscription_light_1.png", "Inscription en étapes"),
    ("anC_inscription_light_2.png", "Vérification par code OTP"),
    ("anC_profil_light_1.png", "Profil et expériences"),
    ("anC_consentement_light_1.png", "Consentements RGPD"),
]
xy = [(0.55, 1.35), (6.9, 1.35), (0.55, 4.45), (6.9, 4.45)]
for (img, cap), (x, y) in zip(shots, xy):
    picture_fit(os.path.join(IMG, img), x, y, 5.9, 2.8)
    box("", x, y + 2.82, 5.9, 0.4, cap, size=14, color=GRAY, align=PP_ALIGN.CENTER)
notes("Parcours d'un ancien étudiant qui s'inscrit : il reçoit un code à 6 chiffres, complète son profil, "
      "ajoute une expérience et donne ses consentements. Tout se passe en étapes guidées. Démo chronométrée : "
      "si ça dépasse, je saute l'import Excel sans commentaire. Base allumée et compte démo prêts avant de "
      "commencer.")

# ════════════════════════ SLIDE 16 — DÉMO ADMIN + KPI ════════════════════════
slide = prs.slides.add_slide(BLANK)
header("Démo — l'espace admin et les indicateurs", "1:15")
picture_fit(os.path.join(IMG, "anB_dashboard_light_1.png"), 0.6, 1.4, 7.3, 3.1)
picture_fit(os.path.join(IMG, "anB_annuaire_light.png"), 0.6, 4.6, 7.3, 2.1)
box("kpi", 8.2, 1.5, 4.6, 5.2, [
    "8 indicateurs de base : total alumni, actifs, complétion, emploi 6 mois, emploi global, salaire, secteur, type de contrat",
    "Taux d'emploi à 6 mois : expériences actives à la date de référence ; cohortes jeunes = « en cours », jamais un faux chiffre",
    "Indicateurs dérivés par question taguée KPI : ajouter un tag enrichit le tableau de bord sans toucher au backend",
    "Annuaire filtrable : promotion, secteur, entreprise, disponibilité, compétence",
    "Import / export via template Excel, validation ligne par ligne",
], size=14.5)
notes("Côté administrateur, le tableau de bord affiche les huit indicateurs de base définis dans le rapport, "
      "plus un indicateur dérivé par question taguée KPI. Le point le plus travaillé, c'est le taux d'emploi à "
      "6 mois : seules les expériences actives à la date de référence comptent, et une cohorte trop jeune "
      "renvoie « en cours » au lieu d'un faux chiffre. L'annuaire se filtre par promotion, secteur, entreprise "
      "ou compétence, avec import / export Excel. J'insiste : les tags KPI permettent d'enrichir les indicateurs "
      "sans modifier le backend.")

# ══════════════════ SLIDE 17 — LES 8 INDICATEURS (FORMULES + EXEMPLES) ══════════════════
slide = prs.slides.add_slide(BLANK)
header("Les 8 indicateurs : formules et exemples", "0:45",
       "la table des indicateurs d'insertion du rapport")
kpis = [
    ("Taux d'emploi à 6 mois", "expériences actives à la date de référence ÷ effectif", "Promo 2025 : 9/12 en poste = 75 %"),
    ("Taux d'emploi global (brut)", "(alumni avec expérience ÷ effectif) × 100", "30 en poste / 40 = 75 %"),
    ("Type de contrat", "comptage des expériences en cours", "CDI 8 · CDD 3 · Freelance 2"),
    ("Salaire moyen", "moyenne de salary_annuel (NUMERIC)", "(38 000 + 42 000 + 50 000) / 3 = 43 333 €"),
    ("Alumni actifs", "alumni avec ≥ 1 expérience enregistrée", "45 actifs sur 60"),
    ("Taux de complétion", "≥ 1 expérience dans EXPERIENCE_PRO", "45 / 60 = 75 %"),
    ("Alumni par promotion", "comptage par id_promotion", "Promo 2025 : 12"),
    ("Répartition par secteur", "agrégation de secteur_activite", "Info 3 · Finance 2 · Santé 1"),
]
for j, (name, formule, exemple) in enumerate(kpis):
    i = j % 4
    k = j // 4
    kpi_card(0.55 + k * 6.75, 1.6 + i * 1.32, 6.0, name, formule, exemple)
box("", 0.7, 6.95, 11.9, 0.4,
    "8 indicateurs de base + un indicateur dérivé par question taguée KPI des questionnaires actifs (variable).",
    size=13, color=GRAY, align=PP_ALIGN.CENTER)
notes("Ce sont les huit indicateurs de base du rapport, avec leur formule et un exemple réel, repris de la "
      "table des indicateurs (rapport, section 2.2). Le point d'attention : le taux d'emploi à 6 mois ne "
      "compte que les expériences actives à la date de référence — pour la promo 2025 : 9 sur 12 en poste, "
      "soit 75 % — et une cohorte trop récente renvoie « en cours » au lieu d'un faux chiffre. Le salaire "
      "moyen s'appuie sur le champ numérique salary_annuel, avec repli sur le champ texte historique. Un "
      "indicateur dérivé variable s'ajoute pour chaque question taguée KPI des questionnaires actifs.")

# ══════════════════ SLIDE 18 — RÉPONSE À LA PROBLÉMATIQUE ══════════════════
slide = prs.slides.add_slide(BLANK)
header("Réponse à la problématique (4 problèmes → 4 solutions)", "0:30",
       "la table « problèmes identifiés / solutions apportées » du rapport")
pbs = [
    ("Données dispersées", "emails, formulaires papier, appels, Excel", "Base centralisée : 14 tables + import Excel / CSV"),
    ("Indicateurs non fiables", "croisements manuels, source d'erreurs", "8 indicateurs automatisés + dérivés par tags KPI"),
    ("Réseau inanimé", "aucun canal pour rester en contact", "Espace alumni : profil, parcours, questionnaire, newsletter"),
    ("RGPD non formalisé", "aucun workflow traçable", "Consentements tracés, workflow de demandes, journal d'audit, DPO"),
]
py = 1.55
for p, detail, s in pbs:
    pb_sol(0.55, py, 5.55, p, detail)
    connector(6.3, py + 0.39)
    sol_box(6.85, py, 5.95, "Solution", s)
    py += 1.36
box("", 0.7, 6.95, 11.9, 0.4,
    "Chaque problème identifié au départ est couvert par le système — détail dans le rapport, table 2.",
    size=13, color=GRAY, align=PP_ALIGN.CENTER)
notes("Le rapport répond aux quatre problèmes initiaux dans une table que j'ai reprise ici. À gauche ce qui "
      "existait avant : données dispersées, indicateurs calculés à la main, réseau inanimé, RGPD non "
      "formalisé. À droite les solutions : base centralisée avec import Excel, huit indicateurs automatisés "
      "et fiabilisés plus les dérivés par tags KPI, espace alumni vivant avec questionnaire annuel, et un "
      "volet RGPD complet (consentements, workflow de demandes, journal d'audit, durée de conservation, "
      "contact DPO).")

# ══════════════════ SLIDE 19 — DIFFICULTÉS ET LEÇONS ══════════════════
slide = prs.slides.add_slide(BLANK)
header("Difficultés rencontrées et leçons", "0:45",
       "5 incidents réels du rapport (§ 3.2)")
diffs = [
    ("Workflow RGPD : deux admins pouvaient traiter la même demande",
     "leçon : statut « en cours de traitement » + verrou prise_en_charge_par"),
    ("Pas de versionning Git : incident de synchronisation OneDrive",
     "leçon : dépôt Git + .gitignore consolidé — versionner avant de coder"),
    ("Identifiants PostgreSQL en dur dans le code",
     "leçon : variables d'environnement (.env), aucun secret versionné"),
    ("Données temporaires sans purge : OTP expirés et journal d'audit s'accumulent",
     "leçon : prévoir la rétention dès la conception"),
    ("Spécificités du driver pg8000 : JSONB non uniforme, pas d'ID auto, pas de pool",
     "leçon : helpers centralisés (rows_to_dicts, IntegrityError, ::jsonb)"),
]
dy = 1.5
for title, lesson in diffs:
    rect(0.7, dy, 6.35, 1.0, LIGHT)
    box("", 0.85, dy + 0.08, 6.0, 0.42, title, size=13.5, bold=True)
    box("", 0.85, dy + 0.52, 6.05, 0.42, lesson, size=11, color=GRAY)
    dy += 1.09
picture_fit(os.path.join(IMG, "otp_error_light.png"), 7.4, 1.8, 5.2, 3.9)
box("cap_diff19", 7.4, 5.75, 5.2, 0.4, "le flux OTP — codes expirés et journal s'accumulaient sans purge", size=13, color=GRAY, align=PP_ALIGN.CENTER)
notes("J'assume ce qui a coincé, et je reprends les difficultés documentées à la section 3.2 du rapport, "
      "classées par difficulté de correction. Simple : deux administrateurs pouvaient traiter la même demande "
      "RGPD, corrigé par un statut intermédiaire et un verrou ; l'absence de versionning Git, révélée par "
      "l'incident de synchronisation OneDrive, corrigée par un dépôt Git ; et des identifiants PostgreSQL en "
      "dur dans le code, déplacés dans des variables d'environnement. Moyen : des données temporaires qui "
      "s'accumulent sans purge — codes OTP expirés et journal d'audit —, avec une rétention consignée en "
      "piste d'amélioration ; et les spécificités du driver pg8000 — sérialisation JSONB non uniforme, pas "
      "d'ID généré automatiquement, pas de pool de connexions —, traitées par des helpers centralisés. "
      "Chaque incident a produit une leçon écrite dans le rapport.")

# ══════════════════ SLIDE 20 — LIVRABLES MANAGEMENT ══════════════════
slide = prs.slides.add_slide(BLANK)
header("Les 5 livrables Management", "0:30", "le volet Management du sujet couvert par 5 documents")
items = [
    ("1. Cartographie des données", "inventaire des données personnelles par phase de vie — socle RGPD", LIGHT, BLUE),
    ("2. Charte de conformité RGPD", "droits, 4 consentements, durées de conservation, contact DPO", LIGHTGREEN, GREEN),
    ("3. Analyse des indicateurs d'insertion", "les 8 indicateurs : formules, sources, cas limites", LIGHT, BLUE),
    ("4. Stratégie de mise à jour des données", "gouvernance contre l'obsolescence de l'annuaire alumni", LIGHTGREEN, GREEN),
    ("5. Guide des processus d'animation du réseau", "7 processus opérationnels pour le service Relations Entreprises", LIGHT, BLUE),
]
y = 1.55
for t, d, bg, bar in items:
    rect(0.7, y, 11.9, 0.95, bg)
    rect(0.7, y, 0.14, 0.95, bar)
    box("", 1.05, y + 0.08, 11.3, 0.4, t, size=15, bold=True)
    box("", 1.05, y + 0.5, 11.3, 0.4, d, size=13, color=GRAY)
    y += 1.06
box("", 0.7, 6.8, 11.9, 0.4,
    "Tous générés par scripts (fpdf2, python-docx) : régénérables, donc toujours synchronisés avec le rapport.",
    size=13, color=GRAY, align=PP_ALIGN.CENTER)
notes("Le sujet avait aussi un volet Management, et il est couvert par cinq documents livrés en PDF : la "
      "cartographie des données, la charte de conformité RGPD, l'analyse des indicateurs d'insertion, la "
      "stratégie de mise à jour des données et le guide des processus d'animation du réseau. Tous sont générés "
      "par des scripts, donc régénérables et toujours synchronisés avec le rapport. Une phrase pour dire que "
      "chacun de ces documents est cité dans le rapport, annexes E à I.")

# ════════════════════════ SLIDE 21 — BILAN ════════════════════════
slide = prs.slides.add_slide(BLANK)
header("Bilan, limites, pistes", "0:45")
cols = [
    ("Bilan", LIGHT, BLUE, [
        "full-stack complet : données, API FastAPI, front React",
        "sécurité appliquée : IDOR, TOCTOU, messages sanitaires",
        "rigueur : migrations versionnées, documents traités comme du code",
    ]),
    ("Limites", REDBG, RED, [
        "pas de tests automatisés — prérequis avant la production",
        "pas de chiffrement des données sensibles",
        "déploiement côté école : une infrastructure à prévoir",
    ]),
    ("Pistes", LIGHTGREEN, GREEN, [
        "court terme : tests automatisés, newsletter, relances",
        "moyen terme : mentorat, chiffrement, édition en ligne",
        "long terme : PWA, tests E2E, notification de violation (art. 33)",
    ]),
]
x = 0.55
for t, bg, c, items in cols:
    rect(x, 1.5, 4.0, 4.9, bg)
    rect(x, 1.5, 4.0, 0.7, c)
    box("", x + 0.15, 1.58, 3.7, 0.5, t, size=17, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    box("", x + 0.2, 2.5, 3.6, 3.7, items, size=13.5, color=NAVY)
    x += 4.12
box("", 0.7, 6.55, 11.9, 0.4,
    "Bilan : les 4 objectifs du départ sont couverts par un prototype opérationnel, conforme au RGPD.",
    size=14, color=GRAY)
notes("Ce que je retiens : j'ai touché à toutes les couches du full-stack, mis la sécurité en pratique "
      "et le RGPD n'a pas été un ajout après coup. Les limites, assumées : pas de suite de tests "
      "automatisés — c'est le prérequis avant la production —, pas de chiffrement applicatif, et un "
      "déploiement qui demandera de l'infrastructure côté école. Les pistes ensuite, classées par "
      "horizon : court terme, les tests et la newsletter ; moyen terme, le mentorat et le chiffrement ; "
      "long terme, une PWA et la notification de violation, article 33 du RGPD. Je ne dis pas que tout "
      "est parfait : une limite assumée, c'est plus crédible.")

# ════════════════════════ SLIDE 22 — MERCI ════════════════════════
slide = prs.slides.add_slide(BLANK)
rect(0, 0, SW, 7.5, NAVY)
rect(0, 6.62, SW, 0.88, GREEN)
box("t", 0.9, 2.7, 11.5, 1.4, "Merci, je suis prêt pour vos questions", size=40, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
box("st", 1.3, 4.2, 10.7, 0.8, "Alumni CRM — 14 tables · 84 endpoints · 14 routes · 8 indicateurs · conforme RGPD",
    size=16, color=RGBColor(0xC7, 0xD4, 0xEE), align=PP_ALIGN.CENTER)
notes("En une phrase : Alumni CRM est un prototype opérationnel, documenté, avec son volet Management, et "
      "conforme au RGPD, avec deux espaces pensés chacun pour son utilisateur. Je vous remercie. Pendant les "
      "10 minutes de questions je note, je réponds court et ne coupe pas la parole. Le débriefing de 15 "
      "minutes me concerne moins, je laisse faire.")

OUT = os.path.join(HERE, "Soutenance - Alumni CRM v2.pptx")
prs.save(OUT)
print("OK :", OUT)