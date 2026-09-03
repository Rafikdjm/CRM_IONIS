# -*- coding: utf-8 -*-
"""Génération du support PowerPoint de soutenance (15 min) — Alumni CRM.
Approche « documentation comme du code » : le deck est décrit en Python
et régénérable à tout moment.
"""
import os

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
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
    """Bandeau bleu en haut avec le titre, utilisé sur les slides de contenu."""
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
    # bande accent sous le bandeau
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
        if line.startswith("•"):
            p.text = line
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


def build():
    prs = Presentation()
    prs.slide_width = SW
    prs.slide_height = SH

    # ---------- 1. Titre ----------
    s = _blank(prs)
    _set_bg(s, WHITE)
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(2.2), SW, Inches(0.14))
    bar.fill.solid(); bar.fill.fore_color.rgb = BLUE; bar.line.fill.background()
    # petit bloc accent haut
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
        ("1", "Contexte, objectifs et problématique"),
        ("2", "Méthodologie et choix technologiques"),
        ("3", "Développement technique (architecture, données, sécurité)"),
        ("4", "Démonstration — espaces Admin et Alumni"),
        ("5", "Indicateurs d'insertion et conformité RGPD"),
        ("6", "Difficultés, bilan et perspectives"),
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

    # ---------- 3. Contexte ----------
    s = _blank(prs); _set_bg(s, WHITE)
    _top_bar(s, "Contexte et enjeux")
    _bullets(s, Inches(0.9), Inches(1.5), Inches(11.6), Inches(4.6), [
        "IONIS Education Group : premier groupe d'enseignement supérieur privé en France, multi-écoles (EPITECH, ESGI, IIM, ESM, ISA…).",
        "Le suivi de l'insertion des diplômés est un enjeu stratégique : pilotage de la formation, animation du réseau, obligations réglementaires.",
        "Sans système centralisé, les données d'insertion périment vite et la collecte est manuelle.",
        "Un chantier prioritaire : disposer d'un dispositif de suivi alumni scalable et conforme au RGPD.",
    ], size=19)
    box = _box(s, Inches(0.9), Inches(5.6), Inches(11.6), Inches(1.1), color=LIGHT)
    _text(s, Inches(1.2), Inches(5.75), Inches(11.0), Inches(0.8),
          "Problématique : comment structurer la donnée alumni, piloter l'insertion par des indicateurs fiables, "
          "et animer le réseau dans le respect du RGPD ?", size=17, bold=True, color=BLUE)
    _footer(s, 3)

    # ---------- 4. Objectifs ----------
    s = _blank(prs); _set_bg(s, WHITE)
    _top_bar(s, "Objectifs du stage")
    goals = [
        ("O1", "Créer un CRM alumni complet (espace admin + espace alumni)"),
        ("O2", "Modéliser et implémenter une base relationnelle SQL (14 tables)"),
        ("O3", "Développer un tableau de bord admin avec indicateurs d'insertion"),
        ("O4", "Implémenter la conformité RGPD (consentement, export, suppression, audit)"),
        ("O5", "Automatiser l'import/export des données (Excel / CSV)"),
        ("O6", "Documenter les processus managériaux (gouvernance, newsletter, questionnaire)"),
    ]
    y = Inches(1.45)
    for code, txt in goals:
        box = _box(s, Inches(0.9), y, Inches(1.0), Inches(0.85), color=ACCENT)
        tf = box.text_frame; tf.word_wrap = True
        p = tf.paragraphs[0]; p.text = code
        p.font.size = Pt(20); p.font.bold = True; p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER
        _text(s, Inches(2.15), y + Inches(0.15), Inches(10.3), Inches(0.6), txt, size=18)
        y += Inches(0.93)
    _footer(s, 4)

    # ---------- 5. Méthodologie ----------
    s = _blank(prs); _set_bg(s, WHITE)
    _top_bar(s, "Méthodologie et déroulement")
    _bullets(s, Inches(0.9), Inches(1.5), Inches(11.6), Inches(3.0), [
        "Phase d'analyse : cahier des charges, étude des solutions existantes, choix de la stack.",
        "Phase de conception : MCD/MLD, règle d'intégrité, schéma d'API.",
        "Phase de développement : backend FastAPI, frontend React, conformité RGPD.",
        "Phase de consolidation : revue de conformité, documentation des livrables, préparation du guide des processus.",
    ], size=19)
    _bullets(s, Inches(0.9), Inches(4.6), Inches(11.6), Inches(2.0), [
        "Démarche itérative en solo : audit de cohérence par introspection SQL, rejeu des migrations, tests manuels des parcours.",
        "Documentation « comme du code » : tous les livrables générés par script (PDF, DOCX, PPTX).",
    ], size=18)
    _footer(s, 5)

    # ---------- 6. Choix technologiques ----------
    s = _blank(prs); _set_bg(s, WHITE)
    _top_bar(s, "Choix technologiques et arbitrages")
    techs = [
        ("Backend", "FastAPI (Python) + Pydantic : validation, docs Swagger automatiques", "82 endpoints REST"),
        ("Frontend", "React + Vite : SPA fluide, composants partagés, garde de routes par rôle", "14 pages"),
        ("Base de données", "PostgreSQL + driver pg8000 : relationnel, JSONB, intégrité", "14 tables, 16 migrations"),
        ("Sécurité", "OTP email, JWT, clé API admin, garde anti-IDOR, sanitisation des erreurs", "Conforme RGPD"),
    ]
    y = Inches(1.5)
    for nom, desc, badge in techs:
        _box(s, Inches(0.9), y, Inches(11.6), Inches(1.2), color=LIGHT)
        _text(s, Inches(1.2), y + Inches(0.1), Inches(3.2), Inches(0.5), nom, size=20, bold=True, color=BLUE)
        _text(s, Inches(1.2), y + Inches(0.55), Inches(8.2), Inches(0.7), desc, size=16)
        _text(s, Inches(9.6), y + Inches(0.5), Inches(2.6), Inches(0.5), badge, size=14, bold=True, color=ACCENT, align=PP_ALIGN.RIGHT)
        y += Inches(1.35)
    _footer(s, 6)

    # ---------- 7. Modèle de données ----------
    s = _blank(prs); _set_bg(s, WHITE)
    _top_bar(s, "Modèle de données (MCD/MLD)")
    _bullets(s, Inches(0.9), Inches(1.5), Inches(5.8), Inches(5.2), [
        "5 domaines, 14 tables.",
        "Données étudiantes : ETUDIANT, PROMOTION (N:1).",
        "Parcours pro : ENTREPRISE, EXPERIENCE_PRO, CERTIFICATION, OBTIENT (N:M).",
        "RGPD : CONSENTEMENT_RGPD, DEMANDE_RGPD, AUDIT_LOG.",
        "Questionnaires : QUESTIONNAIRE, QUESTION, REPONSE_QUESTIONNAIRE (JSON).",
        "Infrastructure : otp_codes, schema_migrations.",
        "Règles de cascade et contraintes d'unicité garantissant la cohérence.",
    ], size=17)
    # schéma simplifié (boîtes)
    code = {
        "ETUDIANT": 0.4, "PROMOTION": 0.4, "EXPERIENCE_PRO": 0.6, "ENTREPRISE": 0.4,
        "CERTIFICATION": 0.4, "CONSENTEMENT_RGPD": 0.8, "DEMANDE_RGPD": 0.8,
    }
    _text(s, Inches(7.0), Inches(1.5), Inches(5.2), Inches(0.4), "Cartographie simplifiée des entités", size=16, bold=True, color=BLUE)
    _box(s, Inches(7.0), Inches(2.0), Inches(2.6), Inches(4.9), color=LIGHT)
    _box(s, Inches(9.8), Inches(2.0), Inches(2.6), Inches(4.9), color=LIGHT)
    _text(s, Inches(7.2), Inches(2.1), Inches(2.2), Inches(0.4), "Toutes les données", size=14, bold=True)
    _text(s, Inches(10.0), Inches(2.1), Inches(2.2), Inches(0.4), "RGPD & pilotage", size=14, bold=True)
    _footer(s, 7)

    # ---------- 8. Architecture ----------
    s = _blank(prs); _set_bg(s, WHITE)
    _top_bar(s, "Architecture 3-tiers")
    # 3 boîtes verticales
    layers = [
        ("FRONTEND", "React + Vite (SPA)\nEspace Admin / Espace Alumni\nproxy /api → port 8000", BLUE),
        ("BACKEND", "FastAPI — 82 endpoints, 16 routeurs\nauth OTP + JWT, clé API, RGPD", ACCENT),
        ("BASE DE DONNÉES", "PostgreSQL\n14 tables, 16 migrations, JSONB", DARK),
    ]
    x = Inches(0.9)
    for nom, desc, col in layers:
        box = _box(s, x, Inches(1.7), Inches(3.6), Inches(4.4), color=col)
        tf = box.text_frame; tf.word_wrap = True
        p = tf.paragraphs[0]; p.text = nom
        p.font.size = Pt(20); p.font.bold = True; p.font.color.rgb = WHITE
        p2 = tf.add_paragraph(); p2.text = desc
        p2.font.size = Pt(15); p2.font.color.rgb = WHITE
        # flèche entre colonnes
        if x < Inches(8.6):
            arr = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, x + Inches(3.55), Inches(3.7), Inches(0.28), Inches(0.4))
            arr.fill.solid(); arr.fill.fore_color.rgb = GRAY; arr.line.fill.background()
        x += Inches(3.95)
    _text(s, Inches(0.9), Inches(6.3), Inches(11.6), Inches(0.6),
          "Côté applicatif : authentification OTP (alumni) / clé API + hash (admin) ; sessions JWT.", size=17, bold=True, color=BLUE)
    _footer(s, 8)

    # ---------- 9. Démo Admin (capture dashboard) ----------
    s = _blank(prs); _set_bg(s, WHITE)
    _top_bar(s, "Démonstration — Espace Administration", "Tableau de bord, annuaire, RGPD")
    _add_image(s, os.path.join(FIG_DIR, "anB_dashboard.png"), Inches(0.9), Inches(1.4), Inches(11.6))
    _footer(s, 9)

    # ---------- 10. Démo Alumni (capture profil) ----------
    s = _blank(prs); _set_bg(s, WHITE)
    _top_bar(s, "Démonstration — Espace Alumni", "Profil, parcours, consentement, questionnaire")
    _add_image(s, os.path.join(FIG_DIR, "anC_parcours.png"), Inches(0.9), Inches(1.4), Inches(11.6))
    _footer(s, 10)

    # ---------- 11. RGPD ----------
    s = _blank(prs); _set_bg(s, WHITE)
    _top_bar(s, "Conformité RGPD")
    _bullets(s, Inches(0.9), Inches(1.5), Inches(11.6), Inches(1.6), [
        "Consentement explicite : 4 types (contact, partenaires, enquêtes, newsletter), horodaté et réellement consommé.",
        "Droits des personnes : export en auto-service (JSON/Excel/CSV), demande de suppression avec workflow verrouillé.",
        "Anonymisation vs suppression ; traçabilité via journal d'audit ; purge différée des comptes anonymisés.",
    ], size=18)
    img = _add_image(s, os.path.join(FIG_DIR, "anC_consentement.png"), Inches(0.9), Inches(3.2), Inches(5.8))
    img = _add_image(s, os.path.join(FIG_DIR, "anB_demandes_rgpd.png"), Inches(7.0), Inches(3.2), Inches(5.8))
    _footer(s, 11)

    # ---------- 12. Indicateurs ----------
    s = _blank(prs); _set_bg(s, WHITE)
    _top_bar(s, "Indicateurs d'insertion professionnelle")
    _bullets(s, Inches(0.9), Inches(1.5), Inches(5.8), Inches(5.4), [
        "8 indicateurs reproductibles, avec formule et source de données explicites.",
        "Taux d'emploi à 6 mois : expériences actives à la date de référence.",
        "Adéquation formation/emploi via les tags KPI du questionnaire.",
        "Salaire moyen / min / max sur le champ salaire annuel.",
        "Répartition par promotion et par secteur, taux de complétion.",
        "Refus d'afficher un chiffre trompeur (cohortes immatures → non disponible).",
    ], size=17)
    _add_image(s, os.path.join(FIG_DIR, "anB_dashboard.png"), Inches(7.0), Inches(1.9), Inches(5.6))
    _footer(s, 12)

    # ---------- 13. Difficultés ----------
    s = _blank(prs); _set_bg(s, WHITE)
    _top_bar(s, "Difficultés rencontrées et solutions")
    _bullets(s, Inches(0.9), Inches(1.5), Inches(11.6), Inches(5.2), [
        "Auth croisée admin/alumni (403) → clés distinctes, vérification du rôle, purge des sessions orphelines.",
        "Dérive modèle/base → migrations correctives + rejeu complet sur base vide.",
        "Indicateur d'insertion trompeur → filtrage des expériences actives, exclusion des cohortes immatures.",
        "Incident OneDrive → dépôt Git + .gitignore consolidé (versionner avant la première ligne de code).",
        "Failles sécurité (IDOR, upload, secrets) → correctifs documentés, sanitisation des erreurs.",
        "Limites exposées de façon transparente (tests, newsletter, mise à jour d'expérience).",
    ], size=18)
    _footer(s, 13)

    # ---------- 14. Bilan ----------
    s = _blank(prs); _set_bg(s, WHITE)
    _top_bar(s, "Bilan et perspectives")
    _bullets(s, Inches(0.9), Inches(1.5), Inches(11.6), Inches(3.4), [
        "Prototype complet et opérationnel : 82 endpoints, 14 pages, 14 tables, conformité RGPD.",
        "Compétences : full-stack, sécurité applicative, migrations versionnées, RGPD, méthodologie.",
        "Documentation « comme du code » : rapports, cartographies, guide des processus, ce support.",
    ], size=18)
    _bullets(s, Inches(0.9), Inches(4.9), Inches(11.6), Inches(2.0), [
        "Court terme : suite de tests automatisés, automatisation du questionnaire, frontend newsletter.",
        "Moyen terme : module de mentorat, chiffrement applicatif, route de mise à jour d'une expérience.",
        "Long terme : application mobile, PWA, notification de violation (art. 33 RGPD).",
    ], size=17, gap=4)
    _footer(s, 14)

    # ---------- 15. Conclusion / fin ----------
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
    print("Soutenance PPTX genere.")
    return out


if __name__ == "__main__":
    build()
