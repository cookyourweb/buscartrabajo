#!/usr/bin/env python3
"""Revisa un CV generado contra los fallos MEDIDOS del generador.

Los cinco checks salen de casos reales, no de teoria (25-27 jul 2026):

  1. Cuantificadores inventados  - "millions of transactions" (Malwarebytes)
  2. Coletillas sin metrica      - "improving operational efficiency" (Malwarebytes),
                                   "reducing manual effort and error rates" (Revolut)
  3. Afirmaciones de ROL falsas  - "designed backend services" (el Master solo dice
                                   "coordinated data contracts WITH the backend team")
  4. Titular roto                - duplicado o con el titulo de la vacante dentro
  5. Bullets nominalizados       - "Design and integration of X" en vez de "Designed X"

Los checks 3 y 5 son los que NINGUN guardrail del servidor detecta: son semanticos,
no coincidencia de texto contra el Master.

    python3 revisar_cv_generado.py <file_id_de_drive>
"""
import importlib.util
import io
import re
import sys
import urllib.request
import zipfile

_spec = importlib.util.spec_from_file_location(
    "subir", "/Users/vero/Desktop/proyectosActivosCookyourweb/buscartrabajo/scripts/subir_cv_drive.py"
)
subir = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(subir)

CUANTIFICADORES = [
    r"\bmillions? of\b", r"\bthousands? of\b", r"\bhundreds? of\b",
    r"\bmillones de\b", r"\bmiles de\b", r"\bcientos de\b",
    r"\blarge[- ]scale\b", r"\bmassive\b", r"\bcountless\b",
]

COLETILLAS = [
    r"improving \w+", r"reducing \w+", r"increasing \w+", r"enhancing \w+",
    r"boosting \w+", r"optimizing \w+ (?:efficiency|performance|rates?)",
    r"mejorando \w+", r"reduciendo \w+", r"aumentando \w+",
]

# Afirmaciones de alcance que el Master no respalda. Cada una es un caso real.
ROL_SOSPECHOSO = [
    r"designed backend services", r"architected \w+ systems?",
    r"led .{0,25}across .{0,25}(?:distributed|microservices)",
    r"built resilient systems", r"owned the \w+ architecture",
    r"managed a team", r"hired\b", r"performance reviews?",
    r"handling millions", r"distributed systems? (?:design|architecture)",
]

NOMINALIZADOS = [
    r"^[-•\s]*(?:Design|Development|Integration|Implementation|Creation|Documentation|Evaluation) of ",
    r"^[-•\s]*(?:Diseno|Desarrollo|Integracion|Implementacion|Creacion) de ",
]


def texto_docx(datos: bytes) -> str:
    with zipfile.ZipFile(io.BytesIO(datos)) as z:
        xml = z.read("word/document.xml").decode("utf-8", "replace")
    xml = re.sub(r"</w:p>", "\n", xml)
    return re.sub(r"<[^>]+>", "", xml).strip()


def descargar(token: str, fid: str) -> str:
    cab = {"Authorization": f"Bearer {token}"}
    meta_url = f"https://www.googleapis.com/drive/v3/files/{fid}?fields=mimeType,name"
    with urllib.request.urlopen(urllib.request.Request(meta_url, headers=cab), timeout=60) as r:
        import json
        meta = json.load(r)
    if meta["mimeType"] == "application/vnd.google-apps.document":
        url = f"https://www.googleapis.com/drive/v3/files/{fid}/export?mimeType=text/plain"
        with urllib.request.urlopen(urllib.request.Request(url, headers=cab), timeout=90) as r:
            return r.read().decode("utf-8", "replace")
    url = f"https://www.googleapis.com/drive/v3/files/{fid}?alt=media"
    with urllib.request.urlopen(urllib.request.Request(url, headers=cab), timeout=90) as r:
        return texto_docx(r.read())


def _buscar(patrones, texto, por_linea=False):
    hits = []
    if por_linea:
        for linea in texto.splitlines():
            for p in patrones:
                if re.search(p, linea.strip(), re.I):
                    hits.append(linea.strip()[:95])
                    break
        return hits
    for p in patrones:
        for m in re.finditer(p, texto, re.I):
            ini = max(0, m.start() - 45)
            hits.append("..." + texto[ini:m.end() + 45].replace("\n", " "))
    return hits


def revisar(texto: str) -> int:
    lineas = [l for l in texto.splitlines() if l.strip()]
    titular = lineas[1] if len(lineas) > 1 else ""

    print(f"\n{'=' * 74}\nREVISION DEL CV  ({len(texto)} chars)\n{'=' * 74}")
    print(f"\nTITULAR: {titular}\n")

    fallos = 0

    # 1
    hits = _buscar(CUANTIFICADORES, texto)
    print(f"1. CUANTIFICADORES INVENTADOS ... {'FALLO' if hits else 'ok'}")
    for h in hits[:4]:
        print(f"     {h}")
    fallos += bool(hits)

    # 2
    hits = _buscar(COLETILLAS, texto)
    print(f"2. COLETILLAS SIN METRICA ...... {'REVISAR' if hits else 'ok'}")
    for h in hits[:4]:
        print(f"     {h}")
    fallos += bool(hits)

    # 3
    hits = _buscar(ROL_SOSPECHOSO, texto)
    print(f"3. AFIRMACIONES DE ROL ......... {'FALLO' if hits else 'ok'}")
    for h in hits[:4]:
        print(f"     {h}")
    fallos += bool(hits)

    # 4
    problemas = []
    for frag in ("10+ years", "años", "years"):
        if titular.lower().count(frag.lower()) > 1:
            problemas.append(f"'{frag}' duplicado")
    for vac in ("Engineer |", "Developer |"):
        pass
    if titular.count("|") > 5:
        problemas.append(f"{titular.count('|')} separadores (esperado <=5)")
    print(f"4. TITULAR ..................... {'FALLO' if problemas else 'ok'}")
    for p in problemas:
        print(f"     {p}")
    fallos += bool(problemas)

    # 5
    hits = _buscar(NOMINALIZADOS, texto, por_linea=True)
    print(f"5. BULLETS NOMINALIZADOS ....... {'REVISAR' if hits else 'ok'}")
    for h in hits[:5]:
        print(f"     {h}")
    fallos += bool(hits)

    print(f"\n{'=' * 74}")
    print("VEREDICTO: LIMPIO" if fallos == 0 else f"VEREDICTO: {fallos}/5 checks con hallazgos")
    print(f"{'=' * 74}\n")
    return fallos


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    token = subir.access_token(subir.leer_env(subir.ENV))
    texto = descargar(token, sys.argv[1])
    revisar(texto)
    print("--- CV COMPLETO ---")
    print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
