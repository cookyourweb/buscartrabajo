#!/usr/bin/env python3
"""Renderiza el CV en markdown plano a un PDF limpio de una/dos paginas."""
import re
import sys

from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate,
                                Paragraph, Spacer, HRFlowable, KeepTogether)

SRC = sys.argv[1]
OUT = sys.argv[2]

TINTA = colors.HexColor("#1a1a1a")
GRIS = colors.HexColor("#555555")
ACENTO = colors.HexColor("#1f4e79")

S = {
    "nombre": ParagraphStyle("nombre", fontName="Helvetica-Bold", fontSize=19,
                             leading=22, textColor=TINTA, spaceAfter=3),
    "titular": ParagraphStyle("titular", fontName="Helvetica", fontSize=9.6,
                              leading=13, textColor=ACENTO, spaceAfter=3),
    "contacto": ParagraphStyle("contacto", fontName="Helvetica", fontSize=8.6,
                               leading=12, textColor=GRIS, spaceAfter=2),
    "seccion": ParagraphStyle("seccion", fontName="Helvetica-Bold", fontSize=10,
                              leading=12, textColor=ACENTO, spaceBefore=9,
                              spaceAfter=3),
    "empresa": ParagraphStyle("empresa", fontName="Helvetica-Bold", fontSize=9.8,
                              leading=12, textColor=TINTA, spaceBefore=5),
    "cargo": ParagraphStyle("cargo", fontName="Helvetica-Oblique", fontSize=9.2,
                            leading=11.5, textColor=GRIS),
    "cuerpo": ParagraphStyle("cuerpo", fontName="Helvetica", fontSize=9,
                             leading=12.6, textColor=TINTA, alignment=TA_JUSTIFY,
                             spaceAfter=4),
    "bullet": ParagraphStyle("bullet", fontName="Helvetica", fontSize=8.8,
                             leading=12, textColor=TINTA, alignment=TA_JUSTIFY,
                             leftIndent=9, bulletIndent=1, spaceAfter=2.2),
    "skill": ParagraphStyle("skill", fontName="Helvetica", fontSize=8.6,
                            leading=11.6, textColor=TINTA, leftIndent=0,
                            spaceAfter=2.6),
    "linea": ParagraphStyle("linea", fontName="Helvetica", fontSize=8.8,
                            leading=12.4, textColor=TINTA, spaceAfter=1.5),
}

SECCIONES = {"PERFIL PROFESIONAL", "EXPERIENCIA PROFESIONAL", "HABILIDADES TÉCNICAS",
             "FORMACIÓN", "IDIOMAS"}


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def negritas(t):
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", esc(t))


lineas = [l.rstrip() for l in open(SRC, encoding="utf-8").read().split("\n")]
story = []
i = 0
n = len(lineas)
seccion_actual = None

while i < n:
    l = lineas[i].strip()
    if not l:
        i += 1
        continue

    if i == 0:
        story.append(Paragraph(esc(l), S["nombre"]))
        i += 1
        continue

    if l in SECCIONES:
        seccion_actual = l
        story.append(Spacer(1, 3))
        story.append(Paragraph(esc(l), S["seccion"]))
        story.append(HRFlowable(width="100%", thickness=0.7, color=ACENTO,
                                spaceBefore=0, spaceAfter=5))
        i += 1
        continue

    if l.startswith("•"):
        story.append(Paragraph(negritas(l[1:].strip()), S["bullet"], bulletText="•"))
        i += 1
        continue

    # Cabecera: titular y linea de contacto
    if seccion_actual is None:
        estilo = S["titular"] if "|" in l else S["contacto"]
        story.append(Paragraph(esc(l), estilo))
        if estilo is S["contacto"]:
            story.append(HRFlowable(width="100%", thickness=0.7, color=ACENTO,
                                    spaceBefore=6, spaceAfter=0))
        i += 1
        continue

    if seccion_actual == "EXPERIENCIA PROFESIONAL":
        # Bloque empresa / cargo / fechas seguido de bullets
        bloque = [Paragraph(esc(l), S["empresa"])]
        j = i + 1
        sub = []
        while j < n and lineas[j].strip() and not lineas[j].strip().startswith("•"):
            sub.append(lineas[j].strip())
            j += 1
        if sub:
            bloque.append(Paragraph(esc(" · ".join(sub)), S["cargo"]))
        # Arrastra los dos primeros bullets con la cabecera para que un puesto
        # no se parta dejando una linea huerfana al final de la pagina.
        while j < n and not lineas[j].strip():
            j += 1
        arrastrados = 0
        while j < n and arrastrados < 2 and lineas[j].strip().startswith("•"):
            bloque.append(Paragraph(negritas(lineas[j].strip()[1:].strip()),
                                    S["bullet"], bulletText="•"))
            j += 1
            arrastrados += 1
        story.append(KeepTogether(bloque))
        i = j
        continue

    if seccion_actual == "HABILIDADES TÉCNICAS" and ":" in l:
        etiqueta, resto = l.split(":", 1)
        story.append(Paragraph(f"<b>{esc(etiqueta)}:</b> {esc(resto.strip())}", S["skill"]))
        i += 1
        continue

    if seccion_actual in ("FORMACIÓN", "IDIOMAS"):
        story.append(Paragraph(negritas(l), S["linea"]))
        i += 1
        continue

    story.append(Paragraph(negritas(l), S["cuerpo"]))
    i += 1


def pie(canv, doc):
    canv.saveState()
    canv.setFont("Helvetica", 7.2)
    canv.setFillColor(GRIS)
    canv.drawRightString(A4[0] - 16 * mm, 10 * mm, f"Verónica Serna Pérez · {doc.page}")
    canv.restoreState()


doc = BaseDocTemplate(OUT, pagesize=A4,
                      leftMargin=16 * mm, rightMargin=16 * mm,
                      topMargin=14 * mm, bottomMargin=15 * mm,
                      title="CV Verónica Serna Pérez - Senior Frontend Developer",
                      author="Verónica Serna Pérez",
                      subject="Senior Frontend Developer | Desarrollo AI-First")
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="cuerpo")
doc.addPageTemplates([PageTemplate(id="cv", frames=[frame], onPage=pie)])
doc.build(story)
print("PDF generado:", OUT)
