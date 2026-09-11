# -*- coding: utf-8 -*-
"""Genere le poster A3 (29,7 x 42 cm) du livrable soutenance Pre-MSc 2026."""

import os
from fpdf import FPDF

FONT_REGULAR = r"C:\Windows\Fonts\segoeui.ttf"
FONT_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"
FONT_SEMI = r"C:\Windows\Fonts\seguisb.ttf"

NAVY = (21, 32, 66)
BLUE = (46, 111, 219)
GREEN = (46, 160, 110)
GOLD = (214, 158, 46)
LIGHT = (232, 239, 250)
LIGHT_GREEN = (228, 244, 236)
GRAY = (80, 90, 110)
WHITE = (255, 255, 255)

TITLE_BY_CARD = {
    "entreprise": (NAVY, LIGHT),
    "poste": (BLUE, LIGHT),
    "missions": (BLUE, LIGHT),
    "resultats": (GREEN, LIGHT_GREEN),
}


def add_semibold(pdf):
    try:
        pdf.add_font("SegoeUI", "S", FONT_SEMI)
    except Exception:
        pass
    return pdf


def card(pdf, x, y, w, h, title, color, bg):
    pdf.set_fill_color(*color)
    pdf.rect(x, y, w, h, style="F")
    pdf.set_fill_color(*bg)
    pdf.rect(x, y + 30, w, h - 30, style="F")
    pdf.set_font("SegoeUI", "S", 16)
    pdf.set_text_color(*WHITE)
    pdf.set_xy(x + 16, y + 6)
    pdf.cell(w - 32, 18, title.upper(), new_x="LMARGIN", new_y="NEXT")
    return y + 30


def body_lines(pdf, text, y, w, line_h, color=GRAY, size=12.5):
    pdf.set_font("SegoeUI", "", size)
    pdf.set_text_color(*color)
    pdf.set_xy(w[0], y)
    pdf.multi_cell(w[1], line_h, text, new_x="LMARGIN", new_y="NEXT")


def needed(pdf, text, w, line_h, size=12.5):
    pdf.set_font("SegoeUI", "", size)
    n = len(pdf.multi_cell(w, line_h, text, dry_run=True, output="LINES"))
    return n * line_h


def stats(pdf, x, y, w, h, entries):
    n = len(entries)
    slot = w / n
    for i, (num, label) in enumerate(entries):
        cx = x + i * slot
        pdf.set_fill_color(*NAVY)
        pdf.rect(cx + 10, y, slot - 20, h, style="F")
        pdf.set_font("SegoeUI", "B", 28)
        pdf.set_text_color(*WHITE)
        pdf.set_xy(cx + 10, y + 8)
        pdf.cell(slot - 20, 32, num, align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("SegoeUI", "", 10.5)
        pdf.set_text_color(*GOLD)
        pdf.set_xy(cx + 10, y + 46)
        pdf.cell(slot - 20, 14, label.upper(), align="C", new_x="LMARGIN", new_y="NEXT")


def main():
    pdf = FPDF(format=(842, 1191), unit="pt")
    pdf.set_auto_page_break(auto=False)
    pdf.add_font("SegoeUI", "", FONT_REGULAR)
    pdf.add_font("SegoeUI", "B", FONT_BOLD)
    add_semibold(pdf)
    pdf.add_page()

    M = 45
    W = 842 - 2 * M          # 752
    LH = 16

    # ---- Header (bandeau navy) ----
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, 842, 200, style="F")
    pdf.image(r"C:\Users\PC\OneDrive\Desktop\stage\ionis-stm-logo.png", x=707, y=30, w=92)
    pdf.set_xy(M, 30)
    pdf.set_font("SegoeUI", "B", 40)
    pdf.set_text_color(*WHITE)
    pdf.cell(W - 150, 42, "ALUMNI CRM", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("SegoeUI", "S", 16)
    pdf.set_text_color(190, 205, 240)
    pdf.set_xy(M, 80)
    pdf.multi_cell(W - 150, 20,
                   "Suivi du parcours étudiant et valorisation du réseau des anciens",
                   new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("SegoeUI", "", 13)
    pdf.set_text_color(*GOLD)
    pdf.set_xy(M, 124)
    pdf.cell(W - 150, 18, "Rafik Djemadi - Stage Pré-MSc 2026 - IONIS-STM",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("SegoeUI", "", 13.5)
    pdf.set_text_color(*WHITE)
    pdf.set_xy(M, 152)
    pdf.multi_cell(W - 150, 19,
                   "Une plateforme unique pour suivre les diplômés après leur sortie "
                   "et animer le réseau des anciens, du premier emploi jusqu'à leur "
                   "carrière.", new_x="LMARGIN", new_y="NEXT")

    # ---- Zone cartes ----
    y0 = 236
    colw = 370
    hgap = 14
    xL = M
    xR = M + colw + hgap
    pw_band = colw * 2 + hgap - 32

    # --- Textes (constants) ----
    t_ent = [
        ("L'ENTREPRISE", "entreprise"),
        [
            "J'ai fait mon stage à IONIS-STM, une école du groupe Ionis Education "
            "Group qui forme au management et aux nouvelles technologies.",
            "À l'origine du projet : l'école perdait la trace de ses diplômés une "
            "fois partis, et rien ne permettait de mesurer leur insertion.",
            "C'est pourtant un vrai atout — surtout comme vivier de futurs "
            "terrains de stage pour les promotions suivantes.",
        ],
    ]
    t_poste = [
        ("LE POSTE", "poste"),
        [
            "Un stage Pré-MSc 2026 en tant que développeur informatique.",
            "Ma mission : concevoir et développer un CRM qui suit chaque étudiant "
            "de l'inscription jusqu'à sa carrière après le diplôme.",
            "J'ai touché à toute la chaîne : base de données, API, interface web "
            "et gestion des données (RGPD, mise à jour de l'annuaire).",
        ],
    ]
    missions = [
        "Créer la base de données relationnelle : relier chaque étudiant à ses "
        "années d'études, ses certifications et ses expériences.",
        "Développer l'application web : un espace admin pour l'école (tableau de "
        "bord, annuaire filtrable) et un espace alumni pour les anciens "
        "(inscription, mise à jour du profil).",
        "Automatiser ce qui va de soi : importer la liste des admis depuis Excel, "
        "exporter les données.",
        "Soigner la partie données : cartographie, conformité RGPD et une "
        "stratégie pour garder l'annuaire à jour (questionnaire annuel).",
    ]
    resultats = [
        "Une application 3-tiers livrée : FastAPI côté serveur, React côté "
        "interface, PostgreSQL pour la base.",
        "Une API REST complète et documentée avec 84 endpoints ; chaque évolution "
        "de la base est versionnée (17 migrations).",
        "Le RGPD a été intégré dès le départ : 4 consentements traçables, "
        "export/suppression, anonymisation et journal d'audit.",
        "Import des admis en un clic depuis Excel et export complet des données "
        "du CRM.",
        "Les indicateurs d'insertion (emploi à 6 mois, adéquation "
        "formation/emploi) se remplissent tout seuls dès qu'une question est "
        "taggée, sans toucher au backend.",
    ]
    persp_lines = [
        "Lancer pour de bon le questionnaire annuel et la newsletter, pour que les anciens continuent à mettre à jour leurs infos.",
        "Enrichir le CRM : compétences, recommandations, et pourquoi pas un système de mentorat entre anciens et étudiants.",
        "Partager le tableau de bord avec les entreprises partenaires, un bon moyen de décrocher de futurs terrains de stage.",
        "Mettre en place une vraie suite de tests (pytest côté backend, Vitest côté frontend) avant toute mise en production.",
    ]

    # --- Hauteurs fixes, calculees avec la police de rendu reelle ----
    def h_for(items, min_h=160):
        tot = 0
        for it in items:
            tot += needed(pdf, it, colw - 32, LH) + 4
        return max(min_h, 30 + tot + 8)

    h_ent = h_for(t_ent[1])
    h_poste = h_for(t_poste[1])
    h_mis = h_for(missions)
    h_res = h_for(resultats)

    pdf.set_font("SegoeUI", "", 13)
    persp_tot = 0
    for line in persp_lines:
        n = len(pdf.multi_cell(pw_band - 14, LH, line, dry_run=True, output="LINES"))
        persp_tot += n * LH + 2
    persp_h = max(150, 56 + persp_tot + 24)
    persp_bullets_bottom = 56 + persp_tot

    pdf.set_font("SegoeUI", "", 12.5)
    rep_line1 = (
        "API REST FastAPI  ·  Frontend React (Vite)  ·  Base PostgreSQL (17 migrations versionnées)  ·  "
        "Emails via Resend (OTP, relances, newsletter)"
    )
    rep_line2 = "Soutenance : 18 septembre 2026  ·  Tuteur pédagogique : Joly Donfack"
    n1 = len(pdf.multi_cell(pw_band, 17, rep_line1, dry_run=True, output="LINES"))
    n2 = len(pdf.multi_cell(pw_band, 17, rep_line2, dry_run=True, output="LINES"))
    rep_h = max(96, 42 + n1 * 17 + 8 + n2 * 17 + 18)

    stats_h = 76

    # --- Espacement vertical reparti pour remplir la page, sans debordement ----
    blocks_total = max(h_ent, h_poste) + max(h_mis, h_res) + persp_h + stats_h + rep_h
    target_bottom = 1146
    vg = max(14, (target_bottom - y0 - blocks_total) // 4)

    print("h_ent", h_ent, "h_poste", h_poste, "h_mis", h_mis, "h_res", h_res)
    print("persp_h", persp_h, "stats_h", stats_h, "rep_h", rep_h, "vg", vg)

    # ---- Dessin des cartes ----
    y = y0

    def draw_pair(title_a, ckey_a, body_a, h_a, title_b, ckey_b, body_b, h_b):
        cy = y
        colA, bgA = TITLE_BY_CARD[ckey_a]
        colB, bgB = TITLE_BY_CARD[ckey_b]
        top = card(pdf, xL, cy, colw, h_a, title_a, colA, bgA)
        for item in body_a:
            body_lines(pdf, item, top, (xL + 16, colw - 32), LH)
            top += needed(pdf, item, colw - 32, LH) + 4
        topB = card(pdf, xR, cy, colw, h_b, title_b, colB, bgB)
        for item in body_b:
            body_lines(pdf, item, topB, (xR + 16, colw - 32), LH)
            topB += needed(pdf, item, colw - 32, LH) + 4
        return cy + max(h_a, h_b) + vg

    y = draw_pair(*t_ent[0], t_ent[1], h_ent, *t_poste[0], t_poste[1], h_poste)
    y = draw_pair("LES MISSIONS", "missions", missions, h_mis,
                  "RESULTATS & SOLUTIONS", "resultats", resultats, h_res)

    # ---- Perspectives (bandeau plein, hauteur fixe) ----
    pdf.set_fill_color(*NAVY)
    pdf.rect(xL, y, colw * 2 + hgap, persp_h, style="F")
    pdf.set_font("SegoeUI", "S", 17)
    pdf.set_text_color(*GOLD)
    pdf.set_xy(xL + 16, y + 14)
    pdf.cell(pw_band, 20, "PERSPECTIVES D'ÉVOLUTION", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("SegoeUI", "", 13)
    pdf.set_text_color(*WHITE)
    py = y + 56
    for line in persp_lines:
        pdf.set_xy(xL + 16, py)
        pdf.cell(11, LH, "\u2022", new_x="RIGHT")
        lines = pdf.multi_cell(pw_band - 14, LH, line, dry_run=True, output="LINES")
        for ln in lines:
            pdf.set_xy(xL + 30, py)
            pdf.multi_cell(pw_band - 14, LH, " " + ln, new_x="LMARGIN", new_y="NEXT")
            py += LH
        py += 2
    y = y + persp_h + vg

    # ---- Stats (hauteur fixe) ----
    entries = [
        ("84", "endpoints API REST"),
        ("17", "migrations versionnees"),
        ("14", "tables PostgreSQL"),
        ("4", "types de consentement RGPD"),
    ]
    stats(pdf, xL, y, colw * 2 + hgap, stats_h, entries)
    y = y + stats_h + vg

    # ---- Repères techniques (hauteur fixe, ligne 2 decalee apres la ligne 1) ----
    pdf.set_fill_color(*BLUE)
    pdf.rect(xL, y, colw * 2 + hgap, rep_h, style="F")
    pdf.set_font("SegoeUI", "S", 16)
    pdf.set_text_color(*GOLD)
    pdf.set_xy(xL + 16, y + 12)
    pdf.cell(pw_band, 20, "REPÈRES TECHNIQUES", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("SegoeUI", "", 12.5)
    pdf.set_text_color(*WHITE)
    pdf.set_xy(xL + 16, y + 42)
    pdf.multi_cell(pw_band, 17, rep_line1, new_x="LMARGIN", new_y="NEXT")
    pdf.set_xy(xL + 16, y + 42 + n1 * 17 + 8)
    pdf.multi_cell(pw_band, 17, rep_line2, new_x="LMARGIN", new_y="NEXT")

    # ---- Pied de page ----
    footer_y = 1191 - 34
    pdf.set_font("SegoeUI", "", 9.5)
    pdf.set_text_color(*GRAY)
    pdf.set_xy(0, footer_y)
    pdf.cell(842, 12, "Rafik Djemadi - Stage Pre-MSc 2026 - IONIS-STM - "
                       "Poster A3 (29,7 x 42 cm)", align="C", new_x="LMARGIN", new_y="NEXT")

    out = r"C:\Users\PC\OneDrive\Desktop\stage\Livrables\5_Poster_A3\Poster_A3_Alumni_CRM.pdf"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pdf.output(out)
    print("Poster genere :", out)


if __name__ == "__main__":
    main()