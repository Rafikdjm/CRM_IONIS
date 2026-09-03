# -*- coding: utf-8 -*-
"""Génération du support PowerPoint de soutenance (15 min) — Alumni CRM.
Approche « documentation comme du code » : le deck est décrit en Python
et régénérable à tout moment.
"""
import os

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(OUTPUT_DIR, "..", "image")

# Palette (cohérente avec le rapport et le thème clair de l'application)
BLUE = RGBColor(30, 64, 175)        # indigo
DARK = RGBColor(17, 24, 39)         # presque noir
GRAY = RGBColor(107, 114, 128)      # gris
LIGHT = RGBColor(239, 246, 255)     # bleu très clair
WHITE = RGBColor(255, 255, 255)
ACCENT = RGBColor(16, 185, 129)     # vert

SW, SH = Inches(13.333), Inches(7.5)


def _blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def _set_bg(slide, color):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color


def _top_bar(slide, title, subtitle=None):
    """Bandeau bleu en haut avec le titre."""
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SW, Inches(1.1))
    bar.fill.solid()
    bar.fill.fore_color.rgb = BLUE
    bar.line.fill.background()
    tf = bar.text_frame
    tf.margin_left = Inches(0.5)
    tf.margin_top = Inches(0.15)
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = WHITE
    if subtitle:
        p2 = tf.add_paragraph()
        p2.text = subtitle
        p2.font.size = Pt(14)
        p2.font.color.rgb = LIGHT
    strip = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(1.1), SW, Inches(0.06))
    strip.fill.solid()
    strip.fill.fore_color.rgb = ACCENT
    strip.line.fill.background()


def _box(slide, x, y, w, h, color=WHITE, line=None):
    bx = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    bx.fill.solid()
    bx.fill.fore_color.rgb = color
    if line:
        bx.line.color.rgb = line
        bx.line.width = Pt(1)
    else:
        bx.line.fill.background()
    bx.shadow.inherit = False
    return bx


def _text(slide, x, y, w, h, text, size=18, bold=False, color=DARK, align=PP_ALIGN.LEFT):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.05)
    tf.margin_right = Inches(0.05)
    tf.margin_top = Inches(0.03)
    tf.margin_bottom = Inches(0.03)
    lines = text.split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.level = 0
        p.font.size = Pt(size)
        p.font.bold = bold
        p.font.color.rgb = color
        p.alignment = align
        p.space_after = Pt(2)
    return tb


def _bullets(slide, x, y, w, h, items, size=18, gap=8):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.05)
    tf.margin_top = Inches(0.03)
    first = True
    for it in items:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.text = ("• " if not it.startswith("•") else "") + it
        p.font.size = Pt(size)
        p.font.color.rgb = DARK
        p.space_after = Pt(gap)
    return tb


def _add_image(slide, path, x, y, w, h=None):
    if not os.path.exists(path):
        return False
    pic = slide.shapes.add_picture(path, x, y, width=w)
    if h:
        pic.height = h
    return True


def _footer(slide, num):
    tb = slide.shapes.add_textbox(Inches(0.4), Inches(7.05), Inches(12.5), Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = False
    p = tf.paragraphs[0]
    p.text = "Alumni CRM — Stage PreMSc 2026 — IONIS-STM        %d" % num
    p.font.size = Pt(11)
    p.font.color.rgb = GRAY


def _screenshot(slide, path, left=Inches(1.9), top=Inches(1.35), ratio=1.6):
    """Capture 16:10 calée verticalement dans la zone utile (max hauteur ~5.55in)."""
    h = Inches(5.55)
    w = int(h * ratio)
    _add_image(slide, path, left, top, w, h)


def _numbered_rows(slide, y0, pairs, box_color, step=Inches(0.72), title=True):
    """Suite de lignes numérotées (boîte code + texte)."""
    y = y0
    for code, txt in pairs:
        box = _box(slide, Inches(0.9), y, Inches(0.9), Inches(0.6), color=box_color)
        tf = box.text_frame; tf.word_wrap = True
        p = tf.paragraphs[0]; p.text = code
        p.font.size = Pt(17); p.font.bold = True; p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER
        _text(slide, Inches(2.0), y + Inches(0.03), Inches(10.4), Inches(0.55),
              txt, size=17, bold=(title and code.startswith("O")))
        y += step
    return y


def build():
    prs = Presentation()
    prs.slide_width = SW
    prs.slide_height = SH

    # ---------- 1. Titre ----------
    s = _blank(prs); _set_bg(s, WHITE)
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(2.2), SW, Inches(0.14))
    bar.fill.solid(); bar.fill.fore_color.rgb = BLUE; bar.line.fill.background()
    top = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SW, Inches(0.18))
    top.fill.solid(); top.fill.fore_color.rgb = BLUE; top.line.fill.background()
    _text(s, Inches(1.2), Inches(0.9), Inches(10.9), Inches(0.5),
          "CONCEPTION ET DÉVELOPPEMENT D'UN ALUMNI CRM", size=34, bold=True, color=BLUE,
          align=PP_ALIGN.CENTER)
    _text(s, Inches(1.2), Inches(1.55), Inches(10.9), Inches(0.5),
          "Système de suivi du parcours étudiant et de valorisation du réseau des anciens",
          size=18, color=GRAY, align=PP_ALIGN.CENTER)
    _text(s, Inches(1.2), Inches(2.6), Inches(10.9), Inches(0.9),
          "Rafik DJEMADI", size=30, bold=True, color=DARK, align=PP_ALIGN.CENTER)
    _text(s, Inches(1.2), Inches(3.4), Inches(10.9), Inches(0.6),
          "Stage de substitution — Programme Pré-MSc 2026", size=17, color=GRAY,
          align=PP_ALIGN.CENTER)
    _text(s, Inches(1.2), Inches(4.0), Inches(10.9), Inches(0.5),
          "IONIS-STM — Ionis Education Group", size=17, color=BLUE, align=PP_ALIGN.CENTER)
    _text(s, Inches(1.2), Inches(6.3), Inches(10.9), Inches(0.5),
          "Soutenance — 19 septembre 2026", size=15, color=GRAY, align=PP_ALIGN.CENTER)

    # ---------- 2. Plan ----------
    s = _blank(prs); _set_bg(s, WHITE)
    _top_bar(s, "Plan de la présentation")
    outline = [
        ("1", "Contexte, objectifs"),
        ("2", "Méthodologie et architecture"),
        ("3", "Modèle de données et RGPD"),
        ("4", "Démonstration — espaces Admin et Alumni"),
        ("5", "Indicateurs d'insertion"),
        ("6", "Bilan et perspectives"),
    ]
    y = Inches(1.5)
    for num, txt in outline:
        box = _box(s, Inches(0.9), y, Inches(1.0), Inches(0.8), color=BLUE)
        tf = box.text_frame; tf.word_wrap = True
        p = tf.paragraphs[0]; p.text = num
        p.font.size = Pt(26); p.font.bold = True; p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER
        _text(s, Inches(2.15), y + Inches(0.15), Inches(10.3), Inches(0.6), txt, size=20)
        y += Inches(0.92)
    _footer(s, 2)

    # ---------- 3. Contexte & Objectifs ----------
    s = _blank(prs); _set_bg(s, WHITE)
    _top_bar(s, "Contexte, enjeux et objectifs")
    _bullets(s, Inches(0.9), Inches(1.25), Inches(11.6), Inches(1.4), [
        "Le suivi de l'insertion des diplômés est stratégique : pilotage de la formation, animation du réseau, obligations réglementaires (RGPD).",
        "Sans système centralisé, les données périment vite et la collecte est manuelle.",
    ], size=15, gap=6)
    box = _box(s, Inches(0.9), Inches(2.8), Inches(11.6), Inches(0.8), color=LIGHT)
    _text(s, Inches(1.2), Inches(2.88), Inches(11.0), Inches(0.65),
          "Problématique : structurer la donnée alumni, piloter l'insertion par des indicateurs fiables, "
          "et animer le réseau dans le respect du RGPD.", size=15, bold=True, color=BLUE)
    goals = [
        ("O1", "Un CRM complet : espace admin + espace alumni"),
        ("O2", "Une base relationnelle SQL modélisée (MCD/MLD)"),
        ("O3", "Un tableau de bord avec indicateurs d'insertion"),
        ("O4", "Une conformité RGPD réelle (consentement, export, suppression, audit)"),
        ("O5", "L'import/export automatisé (Excel / CSV)"),
    ]
    _numbered_rows(s, Inches(3.75), goals, ACCENT, step=Inches(0.62))
    _footer(s, 3)

    # ---------- 4. Méthodologie & architecture ----------
    s = _blank(prs); _set_bg(s, WHITE)
    _top_bar(s, "Méthodologie et architecture 3-tiers")
    _bullets(s, Inches(0.9), Inches(1.35), Inches(5.9), Inches(4.8), [
        "Phases : analyse → conception (MCD/MLD) → développement → consolidation.",
        "Démarche itérative en solo : audit SQL, rejeu des migrations, tests manuels.",
        "Failles sécurité identifiées (IDOR, upload, secrets) → correctifs documentés.",
        "Documentation « comme du code » : tous les livrables générés par script.",
    ], size=17, gap=10)
    layers = [
        ("FRONTEND", "React + Vite (SPA)\nAdmin / Alumni\nproxy /api → 8000", BLUE),
        ("BACKEND", "FastAPI\n82 endpoints, 16 routeurs\nauth OTP + JWT, clé API, RGPD", ACCENT),
        ("BASE DE DONNÉES", "PostgreSQL\n14 tables, 16 migrations, JSONB", DARK),
    ]
    x = Inches(7.0)
    for nom, desc, col in layers:
        box = _box(s, x, Inches(1.6), Inches(2.0), Inches(4.9), color=col)
        tf = box.text_frame; tf.word_wrap = True
        p = tf.paragraphs[0]; p.text = nom
        p.font.size = Pt(17); p.font.bold = True; p.font.color.rgb = WHITE
        p2 = tf.add_paragraph(); p2.text = desc
        p2.font.size = Pt(13); p2.font.color.rgb = WHITE
        if x < Inches(11.0):
            arr = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, x + Inches(1.97), Inches(3.8), Inches(0.24), Inches(0.4))
            arr.fill.solid(); arr.fill.fore_color.rgb = GRAY; arr.line.fill.background()
        x += Inches(2.28)
    _footer(s, 4)

    # ---------- 5. Modèle de données ----------
    s = _blank(prs); _set_bg(s, WHITE)
    _top_bar(s, "Modèle de données (MCD/MLD)")
    _bullets(s, Inches(0.9), Inches(1.5), Inches(11.6), Inches(5.2), [
        "5 domaines, 14 tables.",
        "Étudiants : ETUDIANT, PROMOTION (N:1).",
        "Parcours pro : ENTREPRISE, EXPERIENCE_PRO, CERTIFICATION, OBTIENT (N:M).",
        "RGPD : CONSENTEMENT_RGPD, DEMANDE_RGPD, AUDIT_LOG.",
        "Questionnaires : QUESTIONNAIRE, QUESTION, REPONSE_QUESTIONNAIRE (JSON).",
        "Cascade et contraintes d'unicité garantissent la cohérence.",
    ], size=18, gap=12)
    _footer(s, 5)

    # ---------- 6. RGPD ----------
    s = _blank(prs); _set_bg(s, WHITE)
    _top_bar(s, "Conformité RGPD")
    _bullets(s, Inches(0.9), Inches(1.35), Inches(5.9), Inches(2.5), [
        "Consentement explicite : 4 types, horodaté et réellement consommé.",
        "Droits : export en auto-service (JSON/Excel/CSV), suppression avec workflow verrouillé.",
        "Anonymisation vs suppression ; journal d'audit ; purge différée.",
    ], size=15, gap=6)
    _add_image(s, os.path.join(FIG_DIR, "anC_consentement_light.png"), Inches(0.9), Inches(4.0), Inches(4.7))
    _add_image(s, os.path.join(FIG_DIR, "anB_demandes_rgpd_light.png"), Inches(7.0), Inches(1.35), Inches(5.9))
    _footer(s, 6)

    # ---------- 7. Démo Admin ----------
    s = _blank(prs); _set_bg(s, WHITE)
    _top_bar(s, "Démonstration — Espace Administration", "Tableau de bord, annuaire, RGPD")
    _screenshot(s, os.path.join(FIG_DIR, "anB_dashboard_light.png"))
    _footer(s, 7)

    # ---------- 8. Démo Alumni ----------
    s = _blank(prs); _set_bg(s, WHITE)
    _top_bar(s, "Démonstration — Espace Alumni", "Profil, parcours, consentement, questionnaire")
    _screenshot(s, os.path.join(FIG_DIR, "anC_parcours_light.png"))
    _footer(s, 8)

    # ---------- 9. Indicateurs ----------
    s = _blank(prs); _set_bg(s, WHITE)
    _top_bar(s, "Indicateurs d'insertion professionnelle")
    _bullets(s, Inches(0.9), Inches(1.5), Inches(5.9), Inches(5.4), [
        "8 indicateurs reproductibles, formule et source explicites.",
        "Taux d'emploi à 6 mois (expériences actives).",
        "Adéquation formation/emploi via les tags KPI.",
        "Salaire moyen / min / max (champ annuel).",
        "Répartition par promotion et secteur, taux de complétion.",
        "Pas de chiffre trompeur : cohortes immatures → « non disponible ».",
    ], size=17)
    _add_image(s, os.path.join(FIG_DIR, "anB_dashboard_light.png"), Inches(7.0), Inches(1.9), Inches(5.6))
    _footer(s, 9)

    # ---------- 10. Bilan & perspectives ----------
    s = _blank(prs); _set_bg(s, WHITE)
    _top_bar(s, "Bilan, difficultés et perspectives")
    _bullets(s, Inches(0.9), Inches(1.4), Inches(11.6), Inches(2.2), [
        "Prototype complet et opérationnel, documenté « comme du code ».",
        "Compétences : full-stack, sécurité applicative, migrations versionnées, RGPD.",
    ], size=17)
    _bullets(s, Inches(0.9), Inches(3.5), Inches(11.6), Inches(1.7), [
        "Limites assumées : tests automatisés non conservés, newsletter et mise à jour d'expérience à faire.",
    ], size=16)
    _bullets(s, Inches(0.9), Inches(4.9), Inches(11.6), Inches(2.0), [
        "Court terme : suite de tests, automatisation du questionnaire, frontend newsletter.",
        "Moyen/long terme : mentorat, chiffrement applicatif, application mobile / PWA.",
    ], size=16, gap=6)
    _footer(s, 10)

    # ---------- 11. Conclusion / fin ----------
    s = _blank(prs); _set_bg(s, WHITE)
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SW, Inches(0.18))
    bar.fill.solid(); bar.fill.fore_color.rgb = BLUE; bar.line.fill.background()
    _text(s, Inches(1.2), Inches(2.0), Inches(10.9), Inches(0.6),
          "Merci pour votre attention", size=40, bold=True, color=BLUE, align=PP_ALIGN.CENTER)
    _text(s, Inches(1.2), Inches(3.1), Inches(10.9), Inches(0.5),
          "Questions / échanges", size=22, color=GRAY, align=PP_ALIGN.CENTER)
    _text(s, Inches(1.2), Inches(5.2), Inches(10.9), Inches(0.9),
          "Rafik DJEMADI\nAlumni CRM — Stage PreMSc 2026 — IONIS-STM", size=16, color=DARK,
          align=PP_ALIGN.CENTER)

    out = os.path.join(OUTPUT_DIR, "Soutenance - Alumni CRM - PreMSc 2026.pptx")
    prs.save(out)
    print("Soutenance PPTX genere (%d slides)." % len(prs.slides._sldIdLst))
    return out


if __name__ == "__main__":
    build()
