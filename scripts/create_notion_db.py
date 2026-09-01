#!/usr/bin/env python3
"""
Crea la base de datos de Notion para el ASISTENTE DE CORREO (Outlook → n8n).

La base guarda los correos clasificados como "trabajo/colaboración".
Esquema:
- Asunto         (title)        -> el asunto del correo
- Remitente      (rich_text)    -> quién lo envía
- Fecha          (date)         -> cuándo llegó
- Resumen        (rich_text)    -> resumen que escribe Groq
- Estado         (select)       -> Nuevo / Respondido / Archivado
- Link al correo (url)          -> enlace al mensaje en Outlook

Requisitos ANTES de ejecutar:
1. Tener una página en Notion donde vivirá esta base (ej. "Asistente Correo").
2. Compartir esa página con la integración "n8n-asistente-correo"
   (en la página: ••• -> Connections -> n8n-asistente-correo).
3. Tener a mano el ID de esa página (sale de la URL de la página).

El token NO se guarda en este archivo: se lee del .env (gitignored).
El .env debe tener:
    NOTION_TOKEN=secret_xxx          (token de la integración n8n-asistente-correo)
    NOTION_PARENT_PAGE_ID=xxxxxxxx   (ID de la página padre en Notion)
"""

import os
import sys
import requests


# .env vive en la raíz del proyecto (carpeta padre de scripts/), no en el cwd.
ENV_PATH = os.path.join(os.path.dirname(__file__), "..", ".env")


def load_env(path=ENV_PATH):
    """Lee el .env a mano (sin dependencias extra) y lo vuelca a os.environ."""
    if not os.path.exists(path):
        sys.exit(f"❌ No encuentro {path}. Crea el archivo con NOTION_TOKEN y NOTION_PARENT_PAGE_ID.")
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env()

NOTION_API_KEY = os.environ.get("NOTION_TOKEN", "").strip()
# ID de la página "Asistente correo" (de la URL; NO es secreto, por eso va aquí).
PARENT_PAGE_ID = "37411515-f4b2-8092-8aa2-d885009ca473"

if not NOTION_API_KEY:
    sys.exit("❌ Falta NOTION_TOKEN en el .env.")

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

# --- Esquema de la base de datos ---
DB_TITLE = "Correos – Trabajo/Colaboración"

PROPERTIES = {
    # En Notion, exactamente UNA propiedad debe ser de tipo "title".
    "Asunto": {"title": {}},
    "Remitente": {"rich_text": {}},
    "Fecha": {"date": {}},
    "Resumen": {"rich_text": {}},
    "Estado": {
        "select": {
            "options": [
                {"name": "Nuevo", "color": "blue"},
                {"name": "Respondido", "color": "green"},
                {"name": "Archivado", "color": "gray"},
            ]
        }
    },
    "Link al correo": {"url": {}},
}


def create_database():
    """Crea la base de datos como hija de la página padre indicada."""
    url = "https://api.notion.com/v1/databases"

    payload = {
        "parent": {"type": "page_id", "page_id": PARENT_PAGE_ID},
        "title": [{"type": "text", "text": {"content": DB_TITLE}}],
        "properties": PROPERTIES,
    }

    print(f"\nCreando base de datos «{DB_TITLE}» dentro de la página {PARENT_PAGE_ID}...")
    response = requests.post(url, headers=HEADERS, json=payload)

    if response.status_code == 200:
        data = response.json()
        db_id = data.get("id")
        print("\n✅ ¡Base de datos creada!")
        print(f"\n🔑 DATABASE ID (cópialo para el nodo de n8n):\n   {db_id}")
        print("\nColumnas creadas:")
        for prop_name, prop_data in data.get("properties", {}).items():
            print(f"  - {prop_name}: {prop_data.get('type')}")
        return True
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(f"Detalle: {response.text}")
        if response.status_code == 404:
            print(
                "\n💡 404 casi siempre significa que la integración NO tiene acceso "
                "a la página padre. Ve a la página en Notion -> ••• -> Connections "
                "-> añade «n8n-asistente-correo», y vuelve a ejecutar."
            )
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Notion - Crear base de datos del Asistente de Correo")
    print("=" * 60)

    if create_database():
        print("\n✅ Proceso completado.")
        print("Próximo paso: usar este DATABASE ID en el nodo Notion de n8n.")
    else:
        print("\n❌ No se pudo crear la base de datos. Revisa el detalle de arriba.")
        exit(1)
