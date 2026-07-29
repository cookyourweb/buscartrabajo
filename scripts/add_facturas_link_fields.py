#!/usr/bin/env python3
"""
Añade a la base de Notion «Facturas pendientes» las columnas que el workflow
n8n «Captura Gmail — v4 (PDF a Drive)» necesita para guardar los enlaces:

- Link (url) -> enlace al correo original en Gmail
- PDF  (url) -> enlace de descarga del adjunto ya subido a Google Drive

Es IDEMPOTENTE: comprueba el esquema real y solo crea lo que falte. Si la
columna ya existe, no la toca. Si existe con otro tipo, avisa y NO la pisa.

Requisitos:
1. La base debe estar compartida con la integración del NOTION_TOKEN del .env:
   en Notion -> abrir la base -> ••• -> Connections -> añadir la integración.
2. NOTION_TOKEN en buscartrabajo/.env (no se imprime nunca).

Uso:
    buscartrabajo/venv/bin/python3 scripts/add_facturas_link_fields.py
"""

import os
import sys
import requests

ENV_PATH = os.path.join(os.path.dirname(__file__), "..", ".env")

# DB «Facturas pendientes» (id sacado del nodo "Registrar Factura" del workflow).
DB_ID = "37511515-f4b2-81a7-b863-fadf4c353b21"

# Columnas que el nodo de n8n escribe como url y que la DB no tenía al crearse.
CAMPOS_NUEVOS = {
    "Link": {"url": {}},
    "PDF": {"url": {}},
}


def load_env(path=ENV_PATH):
    if not os.path.exists(path):
        sys.exit(f"❌ No encuentro {path}.")
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env()

TOKEN = os.environ.get("NOTION_TOKEN", "").strip()
if not TOKEN:
    sys.exit("❌ Falta NOTION_TOKEN en el .env.")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}


def leer_esquema():
    r = requests.get(f"https://api.notion.com/v1/databases/{DB_ID}", headers=HEADERS)
    if r.status_code == 404:
        sys.exit(
            "❌ 404: la integración de este token NO tiene acceso a «Facturas pendientes».\n"
            "   Arréglalo en Notion: abre la base -> ••• -> Connections -> añade la integración.\n"
            "   Después vuelve a ejecutar este script."
        )
    if r.status_code != 200:
        sys.exit(f"❌ Error {r.status_code}: {r.text[:300]}")
    return r.json()


def main():
    data = leer_esquema()
    titulo = "".join(t.get("plain_text", "") for t in data.get("title", []))
    props = data.get("properties", {})

    print(f"Base: «{titulo}»")
    print(f"Columnas actuales: {', '.join(sorted(props))}\n")

    a_crear = {}
    for nombre, definicion in CAMPOS_NUEVOS.items():
        tipo = next(iter(definicion))
        if nombre not in props:
            a_crear[nombre] = definicion
            print(f"  + se creará «{nombre}» ({tipo})")
        elif props[nombre].get("type") != tipo:
            print(f"  ⚠️  «{nombre}» ya existe pero es {props[nombre]['type']}, "
                  f"no {tipo}. NO se toca: revísalo a mano.")
        else:
            print(f"  = «{nombre}» ({tipo}) ya existe, nada que hacer")

    if not a_crear:
        print("\n✅ No falta ninguna columna. La base ya está lista para el workflow.")
        return

    r = requests.patch(
        f"https://api.notion.com/v1/databases/{DB_ID}",
        headers=HEADERS,
        json={"properties": a_crear},
    )
    if r.status_code != 200:
        sys.exit(f"\n❌ Error al crear columnas: {r.status_code}\n{r.text[:400]}")

    finales = r.json().get("properties", {})
    print("\n✅ Columnas creadas. Esquema final:")
    for nombre, p in sorted(finales.items()):
        print(f"  - {nombre:14} [{p.get('type')}]")
    print("\nSiguiente paso: en n8n, «Probar ahora» el workflow v4 y comprobar que "
          "el nodo «Registrar Factura» ya no falla y que la fila trae Link y PDF.")


if __name__ == "__main__":
    main()
