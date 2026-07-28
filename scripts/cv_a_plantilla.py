#!/usr/bin/env python3
"""Convierte un CV en texto plano al HTML con la plantilla de Vero, y saca el PDF.

Nace el 28jul2026: los CVs de Revolut y Malwarebytes se iban a enviar como export
plano de Google Docs (Arial 11pt, todo negro, sin jerarquia) mientras que los de
`~/Desktop/cv/ACTIVOS/` llevan la identidad visual de Vero. En la bandeja de un
recruiter esa diferencia se nota en los primeros diez segundos.

El diseno sale de `~/Desktop/cv/_fuentes/cv-4-edreams-frontend-lead.html`: azul
#14487f, secciones en versalitas con filete, competencias a dos columnas, 8,6pt para
que entre en dos paginas.

    # desde un Google Doc de Drive
    python3 cv_a_plantilla.py --doc <file_id> --salida CV-Empresa-Puesto.pdf

    # desde un fichero de texto
    python3 cv_a_plantilla.py --texto cv.txt --salida CV-Empresa-Puesto.pdf

Estructura que espera el texto (la que produce el cv-server):

    NOMBRE APELLIDOS
    <titular con | separadores>
    <contacto con · separadores>
    SECCION EN MAYUSCULAS
    ...
"""
import argparse
import html
import os
import re
import subprocess
import sys
import tempfile
import urllib.request

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Secciones que se maquetan como tabla clave/valor en vez de parrafos.
_SECCIONES_TABLA = {
    "technical skills", "habilidades tecnicas", "habilidades técnicas",
    "competencias", "skills", "education", "formacion", "formación",
}
# Encabezados de seccion: linea corta, en mayusculas, sin bullet.
_SEP_CONTACTO = "·"


def _es_seccion(linea: str) -> bool:
    t = linea.strip()
    if not t or t.startswith(("•", "-", "·")):
        return False
    letras = [c for c in t if c.isalpha()]
    return bool(letras) and all(c.isupper() for c in letras) and len(t) < 60


def _es_fecha(linea: str) -> bool:
    return bool(re.match(r"^\s*(19|20)\d{2}\s*(-|–|to)?\s*((19|20)\d{2}|Present|Actualidad)?\s*$",
                         linea.strip(), re.I))


def parsear(texto: str) -> dict:
    lineas = [l.strip().lstrip("﻿") for l in texto.splitlines() if l.strip()]
    cv = {"nombre": lineas[0], "titular": lineas[1], "contacto": lineas[2], "secciones": []}
    actual = None
    for l in lineas[3:]:
        if _es_seccion(l):
            actual = {"titulo": l, "bloques": []}
            cv["secciones"].append(actual)
        elif actual is not None:
            actual["bloques"].append(l)
    return cv


def _render_experiencia(bloques: list) -> str:
    """Puesto / fechas / bullets. El puesto es la linea previa a una de fecha."""
    out, i = [], 0
    while i < len(bloques):
        l = bloques[i]
        if i + 1 < len(bloques) and _es_fecha(bloques[i + 1]):
            puesto, fechas = l, bloques[i + 1]
            i += 2
            bullets = []
            while i < len(bloques) and bloques[i].startswith("•"):
                bullets.append(bloques[i].lstrip("• ").strip()); i += 1
            out.append(
                '<div class="job avoid-break"><div class="jobhead">'
                f'<span class="role">{html.escape(puesto)}</span>'
                f'<span class="dates">{html.escape(fechas)}</span></div><ul>'
                + "".join(f"<li>{html.escape(b)}</li>" for b in bullets)
                + "</ul></div>"
            )
        elif l.startswith("•"):
            out.append(f'<ul><li>{html.escape(l.lstrip("• ").strip())}</li></ul>'); i += 1
        else:
            out.append(f"<p>{html.escape(l)}</p>"); i += 1
    return "".join(out)


def _render_tabla(bloques: list) -> str:
    filas = []
    for l in bloques:
        if ":" in l:
            k, _, v = l.partition(":")
            filas.append(f'<tr><td class="k">{html.escape(k.strip())}</td>'
                         f'<td>{html.escape(v.strip())}</td></tr>')
        elif " - " in l:  # formacion: "Titulo - Centro (anios)"
            k, _, v = l.partition(" - ")
            filas.append(f'<tr><td class="k">{html.escape(k.strip())}</td>'
                         f'<td>{html.escape(v.strip())}</td></tr>')
        else:
            filas.append(f'<tr><td colspan="2">{html.escape(l)}</td></tr>')
    return f'<table class="skills">{"".join(filas)}</table>'


def a_html(cv: dict) -> str:
    partes = []
    for s in cv["secciones"]:
        titulo = s["titulo"]
        bloques = s["bloques"]
        if titulo.strip().lower() in _SECCIONES_TABLA:
            cuerpo = _render_tabla(bloques)
        elif any(_es_fecha(b) for b in bloques):
            cuerpo = _render_experiencia(bloques)
        else:
            cuerpo = "".join(f"<p>{html.escape(b)}</p>" for b in bloques)
        # `page-break-inside: avoid` en una seccion LARGA la empuja entera a la
        # pagina siguiente y deja media pagina en blanco. Solo se aplica a las
        # cortas; en experiencia va en cada puesto (.job), no en la seccion.
        clase = ' class="avoid-break"' if len(bloques) <= 8 else ""
        partes.append(f'<section{clase}><h2>{html.escape(titulo)}</h2>{cuerpo}</section>')

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>{html.escape(cv['nombre'])}</title><style>
  @page {{ size: A4; margin: 13mm 14mm; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; font-size: 8.6pt;
         line-height: 1.42; color: #2b2b2b; }}
  a {{ color: inherit; text-decoration: none; }}
  strong {{ color: #14487f; font-weight: 600; }}
  header {{ border-bottom: 2.5px solid #14487f; padding-bottom: 7px; margin-bottom: 12px; }}
  h1 {{ font-size: 20pt; color: #14487f; letter-spacing: -0.3px; margin-bottom: 3px; }}
  .headline {{ font-size: 9.6pt; color: #2e75b6; font-weight: 600; margin-bottom: 5px; }}
  .contact {{ font-size: 7.9pt; color: #6b6b6b; }}
  h2 {{ font-size: 9pt; color: #14487f; letter-spacing: 1.6px; text-transform: uppercase;
       border-bottom: 1px solid #d6dee7; padding-bottom: 3px; margin: 13px 0 8px; }}
  section:first-of-type h2 {{ margin-top: 0; }}
  section p {{ margin-bottom: 5px; text-align: justify; }}
  table.skills {{ width: 100%; border-collapse: collapse; }}
  table.skills td {{ padding: 2.5px 0; vertical-align: top; }}
  table.skills td.k {{ width: 26%; color: #14487f; font-weight: 600; padding-right: 10px; }}
  .job {{ margin-bottom: 9px; }}
  .job:last-child {{ margin-bottom: 0; }}
  .jobhead {{ display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 3px; }}
  .role {{ font-weight: 700; color: #1a1a1a; font-size: 9.1pt; }}
  .dates {{ font-size: 7.9pt; color: #8a8a8a; white-space: nowrap; padding-left: 12px; }}
  ul {{ list-style: none; }}
  li {{ position: relative; padding-left: 11px; margin-bottom: 2.5px; }}
  li::before {{ content: "\\2022"; position: absolute; left: 0; color: #2e75b6; }}
  .avoid-break {{ page-break-inside: avoid; }}
</style></head><body>
<header>
  <h1>{html.escape(cv['nombre'])}</h1>
  <div class="headline">{html.escape(cv['titular'])}</div>
  <div class="contact">{html.escape(cv['contacto'])}</div>
</header>
{''.join(partes)}
</body></html>"""


def texto_de_doc(file_id: str) -> str:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "subir", os.path.join(os.path.dirname(os.path.abspath(__file__)), "subir_cv_drive.py"))
    subir = importlib.util.module_from_spec(spec); spec.loader.exec_module(subir)
    tok = subir.access_token(subir.leer_env(subir.ENV))
    req = urllib.request.Request(
        f"https://www.googleapis.com/drive/v3/files/{file_id}/export?mimeType=text/plain")
    req.add_header("Authorization", f"Bearer {tok}")
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read().decode("utf-8", "replace")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--doc", help="file_id de un Google Doc")
    g.add_argument("--texto", help="fichero .txt con el CV")
    ap.add_argument("--salida", required=True, help="ruta del PDF a generar")
    ap.add_argument("--guardar-html", help="guardar tambien el HTML intermedio")
    a = ap.parse_args()

    texto = texto_de_doc(a.doc) if a.doc else open(a.texto, encoding="utf-8").read()
    cv = parsear(texto)
    htm = a_html(cv)

    ruta_html = a.guardar_html if a.guardar_html else tempfile.mktemp(suffix=".html")
    open(ruta_html, "w", encoding="utf-8").write(htm)

    salida = os.path.abspath(a.salida)
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={salida}", f"file://{ruta_html}"],
                   check=True, capture_output=True)
    print(f"OK  {salida}")
    print(f"    {cv['nombre']} | {len(cv['secciones'])} secciones: "
          f"{', '.join(s['titulo'] for s in cv['secciones'])}")
    if a.guardar_html:
        print(f"    HTML: {ruta_html}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
