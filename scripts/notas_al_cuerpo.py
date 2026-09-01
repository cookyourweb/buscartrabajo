#!/usr/bin/env python3
"""Mueve el historial de cada oferta de la propiedad `Notas` al cuerpo de la página.

    python3 scripts/notas_al_cuerpo.py --backup          solo vuelca, no toca nada
    python3 scripts/notas_al_cuerpo.py --migrar          mueve las que estén al límite
    python3 scripts/notas_al_cuerpo.py --migrar --todas  mueve todas las que tengan notas

POR QUÉ EXISTE. La propiedad `Notas` de Notion admite 2.000 caracteres. La ficha de
Alan llegó a 1.990 y su final ya estaba cortado a media frase: cada vez que se
añadía algo nuevo delante, el historial más viejo se caía por el otro extremo y se
perdía sin avisar. El cuerpo de la página no tiene ese límite.

Qué hace: copia el texto largo al cuerpo, troceado en bloques, y deja en la
propiedad solo lo más reciente más un aviso de dónde está el resto.
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

DB = "33d11515f4b281efa776d0ea698b748f"
ENV = Path("/Users/vero/Desktop/proyectosActivosCookyourweb/buscartrabajo/.env")
BACKUPS = Path("/Users/vero/Desktop/proyectosActivosCookyourweb/buscartrabajo/backups-master")

LIMITE_PROPIEDAD = 2000      # el que impone Notion
LIMITE_BLOQUE = 1900         # por bloque de texto, con margen
UMBRAL = 1200                # a partir de aquí se considera en riesgo
RESUMEN = 400                # lo que se queda en la propiedad

env = {}
for linea in ENV.read_text(encoding="utf-8").splitlines():
    linea = linea.strip()
    if linea and not linea.startswith("#") and "=" in linea:
        c, _, v = linea.partition("=")
        env[c.strip()] = v.strip().strip("'\"")
CAB = {"Authorization": f"Bearer {env['NOTION_TOKEN']}",
       "Notion-Version": "2022-06-28", "Content-Type": "application/json"}


def pedir(url, cuerpo=None, metodo="GET", intentos=3):
    for i in range(intentos):
        datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
        req = urllib.request.Request(url, data=datos, headers=CAB, method=metodo)
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.status, json.loads(r.read() or b"{}")
        except urllib.error.HTTPError as e:
            return e.code, {"_error": e.read()[:300].decode("utf-8", "replace")}
        except Exception as e:
            if i == intentos - 1:
                return type(e).__name__, {}
            time.sleep(4)


def texto(props, nombre, tipo="rich_text"):
    """Concatena TODOS los fragmentos, no solo el primero.

    Notion parte el valor en varios rich_text cuando se edita desde su interfaz.
    Leer solo v[0] perdía 1.047 caracteres en la ficha de Builder.io, que tiene
    el historial repartido en tres trozos. Comprobado el 10-ago-2026.
    """
    v = props.get(nombre, {}).get(tipo, [])
    if not isinstance(v, list):
        return ""
    return "".join(i.get("plain_text", "") for i in v)


def todas_las_ofertas():
    ofertas, cursor = [], None
    while True:
        cuerpo = {"page_size": 100}
        if cursor:
            cuerpo["start_cursor"] = cursor
        codigo, r = pedir(f"https://api.notion.com/v1/databases/{DB}/query", cuerpo, "POST")
        if codigo != 200:
            sys.exit(f"No se pudo leer la base: {r}")
        ofertas.extend(r.get("results", []))
        if not r.get("has_more"):
            return ofertas
        cursor = r["next_cursor"]


def trocear(t, tam):
    """Corta por saltos de línea o espacios, nunca a mitad de palabra."""
    partes = []
    while t:
        if len(t) <= tam:
            partes.append(t)
            break
        corte = t.rfind("\n", 0, tam)
        if corte < tam // 2:
            corte = t.rfind(" ", 0, tam)
        if corte < tam // 2:
            corte = tam
        partes.append(t[:corte])
        t = t[corte:].lstrip()
    return partes


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--backup", action="store_true", help="solo volcar, sin tocar nada")
    ap.add_argument("--migrar", action="store_true", help="mover al cuerpo de la página")
    ap.add_argument("--todas", action="store_true", help="no solo las que están al límite")
    args = ap.parse_args()
    if not (args.backup or args.migrar):
        ap.error("elegí --backup o --migrar")

    ofertas = todas_las_ofertas()
    print(f"Ofertas en la base: {len(ofertas)}")

    # ---- backup siempre, pase lo que pase ----
    volcado = []
    for p in ofertas:
        pr = p["properties"]
        volcado.append({
            "id": p["id"],
            "empresa": texto(pr, "Empresa", "title"),
            "puesto": texto(pr, "Puesto"),
            "notas": texto(pr, "Notas"),
            "descripcion": texto(pr, "Descripción"),
        })
    sello = date.today().isoformat()
    destino = BACKUPS / f"NOTION-notas-backup-{sello}.json"
    destino.write_text(json.dumps(volcado, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Backup: {destino}")

    con_notas = [v for v in volcado if v["notas"]]
    en_riesgo = [v for v in con_notas if len(v["notas"]) >= UMBRAL]
    print(f"  con notas: {len(con_notas)}   ·   en riesgo (>= {UMBRAL} chars): {len(en_riesgo)}")
    for v in sorted(con_notas, key=lambda x: -len(x["notas"]))[:12]:
        alarma = "  <-- AL LIMITE" if len(v["notas"]) >= LIMITE_PROPIEDAD - 60 else (
                 "  <-- en riesgo" if len(v["notas"]) >= UMBRAL else "")
        print(f"    {len(v['notas']):5d}  {v['empresa'][:34]}{alarma}")

    if args.backup:
        print("\nSolo backup. No se ha tocado nada.")
        return

    # ---- migración ----
    objetivo = con_notas if args.todas else en_riesgo
    print(f"\nMigrando {len(objetivo)} fichas al cuerpo de la página...\n")
    ok = fallos = 0
    for v in objetivo:
        completo = v["notas"]
        bloques = [{"object": "block", "type": "heading_3",
                    "heading_3": {"rich_text": [{"type": "text", "text": {
                        "content": f"Historial de la candidatura (movido el {sello})"}}]}}]
        for trozo in trocear(completo, LIMITE_BLOQUE):
            bloques.append({"object": "block", "type": "paragraph",
                            "paragraph": {"rich_text": [{"type": "text",
                                                         "text": {"content": trozo}}]}})
        codigo, r = pedir(f"https://api.notion.com/v1/blocks/{v['id']}/children",
                          {"children": bloques}, "PATCH")
        if codigo != 200:
            print(f"  FALLO al escribir el cuerpo de {v['empresa'][:30]}: {r}")
            fallos += 1
            continue

        corto = completo[:RESUMEN].rstrip()
        aviso = " […] HISTORIAL COMPLETO EN EL CUERPO DE ESTA PAGINA (bajar y leer)."
        codigo, r = pedir(f"https://api.notion.com/v1/pages/{v['id']}",
                          {"properties": {"Notas": {"rich_text": [
                              {"text": {"content": (corto + aviso)[:LIMITE_PROPIEDAD]}}]}}},
                          "PATCH")
        if codigo != 200:
            print(f"  OJO: cuerpo escrito pero no se pudo acortar la propiedad "
                  f"de {v['empresa'][:30]}: {r}")
            fallos += 1
            continue
        print(f"  {v['empresa'][:34]:34s} {len(completo):5d} chars -> cuerpo "
              f"({len(bloques)-1} bloques)")
        ok += 1
        time.sleep(0.4)

    print(f"\nMigradas: {ok}   ·   fallos: {fallos}")
    print("A partir de ahora el historial largo va al cuerpo, no a la propiedad.")


if __name__ == "__main__":
    main()
