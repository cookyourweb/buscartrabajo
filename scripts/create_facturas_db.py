#!/usr/bin/env python3
"""
Crea la base de Notion "Facturas pendientes" para el ASISTENTE DE CORREO.

Es una BANDEJA DE PENDIENTES (checklist), NO la contabilidad.
Cuando llega una factura/gasto por Outlook, n8n crea aquí una fila en estado
"Por descargar". La fila sigue en el radar hasta que Verónica la marca
"Registrada" (tras descargarla y volcarla a su Excel/carpetas del proyecto fiscal).

Esquema:
- Concepto   (title)     -> asunto del correo
- Proveedor  (rich_text) -> quién la envía
- Importe    (rich_text) -> € si está en el correo (si no, vacío)
- Fecha      (date)      -> cuándo llegó
- Estado     (select)    -> Por descargar / Descargada / Registrada
- NIF OK     (select)    -> Sí / No / Por revisar  (sin NIF = no deducible)
- Fuera UE   (select)    -> Sí / No / Por revisar  (inversión sujeto pasivo)
- Resumen    (rich_text) -> vista previa del correo

Lee NOTION_TOKEN del .env (raíz del proyecto). Page ID hardcodeado (no es secreto).
La integración n8n-asistente-correo ya tiene acceso a la página padre.
"""

import os
import sys
import requests

ENV_PATH = os.path.join(os.path.dirname(__file__), "..", ".env")


def load_env(path=ENV_PATH):
    if not os.path.exists(path):
        sys.exit(f"❌ No encuentro {path}. Crea el archivo con NOTION_TOKEN.")
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env()

NOTION_API_KEY = os.environ.get("NOTION_TOKEN", "").strip()
# Página padre "Asistente correo" (la integración ya tiene acceso).
PARENT_PAGE_ID = "37411515-f4b2-8092-8aa2-d885009ca473"

if not NOTION_API_KEY:
    sys.exit("❌ Falta NOTION_TOKEN en el .env.")

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

DB_TITLE = "Facturas pendientes"

PROPERTIES = {
    "Concepto": {"title": {}},
    "Proveedor": {"rich_text": {}},
    "Importe": {"rich_text": {}},
    "Fecha": {"date": {}},
    "Estado": {
        "select": {
            "options": [
                {"name": "Por descargar", "color": "red"},
                {"name": "Descargada", "color": "yellow"},
                {"name": "Registrada", "color": "green"},
            ]
        }
    },
    "NIF OK": {
        "select": {
            "options": [
                {"name": "Sí", "color": "green"},
                {"name": "No", "color": "red"},
                {"name": "Por revisar", "color": "gray"},
            ]
        }
    },
    "Fuera UE": {
        "select": {
            "options": [
                {"name": "Sí", "color": "orange"},
                {"name": "No", "color": "gray"},
                {"name": "Por revisar", "color": "gray"},
            ]
        }
    },
    "Resumen": {"rich_text": {}},
}


def create_database():
    url = "https://api.notion.com/v1/databases"
    payload = {
        "parent": {"type": "page_id", "page_id": PARENT_PAGE_ID},
        "title": [{"type": "text", "text": {"content": DB_TITLE}}],
        "properties": PROPERTIES,
    }
    print(f"\nCreando base «{DB_TITLE}» dentro de la página {PARENT_PAGE_ID}...")
    response = requests.post(url, headers=HEADERS, json=payload)

    if response.status_code == 200:
        data = response.json()
        print("\n✅ ¡Base creada!")
        print(f"\n🔑 DATABASE ID (para el nodo de n8n):\n   {data.get('id')}")
        print("\nColumnas:")
        for name, prop in data.get("properties", {}).items():
            print(f"  - {name}: {prop.get('type')}")
        return True
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(f"Detalle: {response.text}")
        if response.status_code == 404:
            print("\n💡 404 = la integración no tiene acceso a la página padre.")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Notion - Crear base «Facturas pendientes»")
    print("=" * 60)
    if create_database():
        print("\n✅ Listo. Usa este DATABASE ID en el nodo Notion de la rama Factura.")
    else:
        sys.exit(1)
