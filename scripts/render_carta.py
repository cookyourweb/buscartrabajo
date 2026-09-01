"""Renderiza una carta de presentacion (.txt) a PDF con la cabecera de Veronica.

Replica el formato de las cartas del 29-ago (que se hicieron a mano por Google
Docs): nombre centrado en negrita, linea de contacto centrada en gris, y el
cuerpo justificado. Los acentos entran tal cual porque las fuentes Type1 de
reportlab llevan Latin-1.

Uso: python render_carta.py entrada.txt salida.pdf
"""
import os
import sys

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

# Los datos de contacto de una persona NO viven en el codigo. Este repositorio
# es publico: escribir aqui el telefono o el correo es publicarlos. Salen del
# .env de la raiz, que esta en .gitignore, igual que el resto de secretos.
ENV_PATH = os.path.join(os.path.dirname(__file__), "..", ".env")


def cargar_env(path=ENV_PATH):
    """Lee el .env a mano (sin dependencias extra) y lo vuelca a os.environ."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            clave, _, valor = linea.partition("=")
            os.environ.setdefault(clave.strip(), valor.strip().strip('"').strip("'"))


def dato(var: str) -> str:
    valor = os.environ.get(var, "").strip()
    if not valor:
        raise SystemExit(
            f"ABORTADO: falta {var}.\n"
            f"Los datos de contacto no se escriben en el codigo. Anade a .env:\n"
            f'  CARTA_NOMBRE="Nombre Apellidos"\n'
            f'  CARTA_CONTACTO="Ciudad · +34 000 000 000 · correo@ejemplo.com"'
        )
    return valor


cargar_env()
NOMBRE = dato("CARTA_NOMBRE")
CONTACTO = dato("CARTA_CONTACTO")

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
