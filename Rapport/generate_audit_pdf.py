# -*- coding: utf-8 -*-
"""Reconstruit AUDIT_COHERENCE.pdf depuis le .md source (UTF-8, monospace).

Le rendu est volontairement « brut » : les tableaux markdown sont conservés
tels quels (présentation monospace), on retire seulement la syntaxe légère
(headings, gras, backticks, blockquotes, fences de code).
"""
import os
import re
from fpdf import FPDF

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "AUDIT_COHERENCE.md")
OUT = os.path.join(HERE, "AUDIT_COHERENCE.pdf")
FONT = r"C:\Windows\Fonts\consola.ttf"


def clean(line: str) -> str:
    s = line.rstrip()
    s = s.replace("**", "").replace("*", "").replace("`", "")
    s = re.sub(r"^#{1,6}\s*", "", s)
    s = re.sub(r"^>\s?", "", s)
    return s


def chunk_by_width(pdf, text, max_w):
    lines = []
    current = ""
    for ch in text:
        if pdf.get_string_width(current + ch) * 0.352778 > max_w:
            lines.append(current)
            current = ch
        else:
            current += ch
    if current:
        lines.append(current)
    return lines


pdf = FPDF(format="A4")
pdf.set_margins(12, 10, 12)
pdf.set_auto_page_break(auto=True, margin=10)
pdf.add_font("Consolas", "", FONT)
pdf.set_font("Consolas", "", 8.5)
pdf.add_page()

max_w = pdf.w - pdf.l_margin - pdf.r_margin
in_fence = False
count = 0
for line in open(SRC, encoding="utf-8").read().splitlines():
    if line.strip().startswith("```"):
        in_fence = not in_fence
        continue
    content = clean(line)
    fragments = chunk_by_width(pdf, content, max_w) if content else [""]
    for frag in fragments:
        if pdf.get_y() + 4.4 > pdf.h - 10:
            pdf.add_page()
        pdf.cell(0, 4.4, frag, new_x="LMARGIN", new_y="NEXT")
    count += 1
    if not content:
        pdf.ln(1.0)

pdf.output(OUT)
print(f"AUDIT_COHERENCE.pdf genere ({count} lignes).")