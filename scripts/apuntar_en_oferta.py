#!/usr/bin/env python3
"""Apunta una entrada fechada en el historial de una candidatura.

    python3 scripts/apuntar_en_oferta.py "Alan" "Respondida por correo..."
    python3 scripts/apuntar_en_oferta.py "Alan" "..." --estado Entrevista
    python3 scripts/apuntar_en_oferta.py "Alan" "..." --seguimiento 2026-08-20

Escribe en el CUERPO de la página, no en la propiedad `Notas`. La propiedad
admite 2.000 caracteres y las fichas activas ya los rozaban: cada añadido
nuevo empujaba el historial viejo fuera y se perdía sin avisar. El cuerpo no
tiene ese límite.

La propiedad se deja con un resumen de la última entrada, para que se vea algo
en la vista de tabla sin abrir la ficha.
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
LIMITE_BLOQUE = 1900
RESUMEN_PROPIEDAD = 400

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
        except Exception:
            if i == intentos - 1:
                return "sin_red", {}
            time.sleep(4)


def texto(props, nombre, tipo="rich_text"):
    v = props.get(nombre, {}).get(tipo, [])
    # Notion parte el valor en varios fragmentos: hay que unirlos todos
    return "".join(i.get("plain_text", "") for i in v) if isinstance(v, list) else ""


def buscar(empresa):
    codigo, r = pedir(f"https://api.notion.com/v1/databases/{DB}/query",
                      {"page_size": 100}, "POST")
    if codigo != 200:
        sys.exit(f"No se pudo leer la base: {r}")
    hallados = [p for p in r["results"]
                if empresa.lower() in texto(p["properties"], "Empresa", "title").lower()
                and not texto(p["properties"], "Empresa", "title").startswith("ZZZ")]
    if not hallados:
        sys.exit(f"No hay ninguna oferta que contenga «{empresa}»")
    if len(hallados) > 1:
        print("Hay varias coincidencias, elegí una y afiná el nombre:")
        for p in hallados:
            pr = p["properties"]
            print(f"   {texto(pr,'Empresa','title')}  ·  {texto(pr,'Puesto')[:50]}")
        sys.exit(1)
    return hallados[0]


def trocear(t, tam):
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
    ap.add_argument("empresa")
    ap.add_argument("entrada")
    ap.add_argument("--estado", help="Pendiente, En proceso, Entrevista, Rechazado…")
    ap.add_argument("--fase", help="1 · RRHH / Headhunter, 3 · Entrevista técnica…")
    ap.add_argument("--seguimiento", help="AAAA-MM-DD")
    args = ap.parse_args()

    pagina = buscar(args.empresa)
    pid = pagina["id"]
    nombre = texto(pagina["properties"], "Empresa", "title")
    hoy = date.today().isoformat()

    bloques = [{"object": "block", "type": "paragraph",
                "paragraph": {"rich_text": [
                    {"type": "text", "text": {"content": f"{hoy} · "},
                     "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": trocear(args.entrada, LIMITE_BLOQUE)[0]}},
                ]}}]
    for extra in trocear(args.entrada, LIMITE_BLOQUE)[1:]:
        bloques.append({"object": "block", "type": "paragraph",
                        "paragraph": {"rich_text": [{"type": "text",
                                                     "text": {"content": extra}}]}})

    codigo, r = pedir(f"https://api.notion.com/v1/blocks/{pid}/children",
                      {"children": bloques}, "PATCH")
    if codigo != 200:
        sys.exit(f"No se pudo escribir en el cuerpo: {r}")

    props = {"Notas": {"rich_text": [{"text": {"content":
             f"{hoy} · {args.entrada[:RESUMEN_PROPIEDAD]}"
             " […] historial completo en el cuerpo de esta página."}}]}}
    if args.estado:
        props["Estado"] = {"select": {"name": args.estado}}
    if args.fase:
        props["Fase"] = {"select": {"name": args.fase}}
    if args.seguimiento:
        props["Seguimiento"] = {"date": {"start": args.seguimiento}}

    codigo, r = pedir(f"https://api.notion.com/v1/pages/{pid}", {"properties": props}, "PATCH")
    if codigo != 200:
        sys.exit(f"Cuerpo escrito, pero fallaron las propiedades: {r}")

    print(f"Apuntado en «{nombre}» ({hoy})")
    codigo, v = pedir(f"https://api.notion.com/v1/pages/{pid}")
    pr = v["properties"]
    print(f"  Estado      : {(pr.get('Estado',{}).get('select') or {}).get('name')}")
    print(f"  Fase        : {(pr.get('Fase',{}).get('select') or {}).get('name')}")
    print(f"  Seguimiento : {(pr.get('Seguimiento',{}).get('date') or {}).get('start')}")


if __name__ == "__main__":
    main()
