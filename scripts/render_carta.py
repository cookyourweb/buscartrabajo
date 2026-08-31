"""Renderiza una carta de presentacion (.txt) a PDF con la cabecera de Veronica.

Replica el formato de las cartas del 29-ago (que se hicieron a mano por Google
Docs): nombre centrado en negrita, linea de contacto centrada en gris, y el
cuerpo justificado. Los acentos entran tal cual porque las fuentes Type1 de
reportlab llevan Latin-1.

Uso: python render_carta.py entrada.txt salida.pdf
"""
import sys

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

NOMBRE = "Verónica Serna Pérez"
CONTACTO = ("Valdemorillo, Madrid · +34 655 133 839 · verserper@gmail.com · "
            "linkedin.com/in/veronica4web")

DARK = HexColor("#1A1A1A")
GREY = HexColor("#666666")

# Guiones largos y flechas: regla NO NEGOCIABLE, jamas salen hacia una empresa.
PROHIBIDOS = "—–―‒→←⟶⟹➜➔➡⇒"


def construir(texto: str, destino: str) -> None:
    malos = sorted({c for c in texto if c in PROHIBIDOS})
    if malos:
        raise SystemExit(f"ABORTADO: el texto trae caracteres prohibidos {malos}")

    doc = SimpleDocTemplate(
        destino, pagesize=letter,
        topMargin=2 * cm, bottomMargin=2 * cm,
        leftMargin=2.2 * cm, rightMargin=2.2 * cm,
        title="Cover Letter", author=NOMBRE,
    )

    s_nombre = ParagraphStyle("nombre", fontName="Helvetica-Bold", fontSize=15,
                              leading=19, alignment=TA_CENTER, textColor=DARK)
    s_contacto = ParagraphStyle("contacto", fontName="Helvetica", fontSize=8.5,
                                leading=12, alignment=TA_CENTER, textColor=GREY)
    s_cuerpo = ParagraphStyle("cuerpo", fontName="Helvetica", fontSize=10.5,
                              leading=16, alignment=TA_JUSTIFY, textColor=DARK)

    historia = [
        Paragraph(NOMBRE, s_nombre),
        Spacer(1, 4),
        Paragraph(CONTACTO, s_contacto),
        Spacer(1, 30),
    ]

    # Un parrafo por bloque separado por linea en blanco. Los .txt se escriben SIN
    # cortes de ancho, asi que cada salto de linea de dentro es intencionado (la
    # despedida y la firma) y se respeta con <br/>.
    for bloque in [b.strip() for b in texto.split("\n\n") if b.strip()]:
        lineas = [" ".join(l.split()) for l in bloque.split("\n") if l.strip()]
        historia.append(Paragraph("<br/>".join(lineas), s_cuerpo))
        historia.append(Spacer(1, 11))

    doc.build(historia)


if __name__ == "__main__":
    entrada, salida = sys.argv[1], sys.argv[2]
    with open(entrada, encoding="utf-8") as f:
        construir(f.read(), salida)
    print(f"OK  {salida}")
