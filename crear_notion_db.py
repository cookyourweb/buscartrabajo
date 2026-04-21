"""
Crea la base de datos "Ofertas de Trabajo" en Notion.
Ejecútalo UNA sola vez.

Instalación:
  pip install requests

Uso:
  python3 crear_notion_db.py
"""

import requests
import json

# ── CONFIGURACIÓN ─────────────────────────
NOTION_TOKEN = "ntn_G464872773099dpLY7OzD7I4ZeZee38rKHsoVlmCV2z7A0"   # Regenera el token en notion.so/my-integrations
PAGE_ID = "33d11515f4b28093bd74e75da412b9dc"
# ──────────────────────────────────────────

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

database = {
    "parent": { "type": "page_id", "page_id": PAGE_ID },
    "title": [{ "type": "text", "text": { "content": "Ofertas de Trabajo" } }],
    "properties": {
        "Empresa":        { "title": {} },
        "Puesto":         { "rich_text": {} },
        "Estado": {
            "select": {
                "options": [
                    { "name": "Pendiente",       "color": "yellow" },
                    { "name": "Enviado",         "color": "blue"   },
                    { "name": "En proceso",      "color": "purple" },
                    { "name": "Entrevista",      "color": "orange" },
                    { "name": "Oferta recibida", "color": "green"  },
                    { "name": "Descartado",      "color": "red"    },
                    { "name": "Rechazado",       "color": "gray"   }
                ]
            }
        },
        "Fecha envio":    { "date": {} },
        "Email empresa":  { "email": {} },
        "Link oferta":    { "url": {} },
        "CV usado":       { "rich_text": {} },
        "Link CV Drive":  { "url": {} },
        "Salario":        { "rich_text": {} },
        "Modalidad": {
            "select": {
                "options": [
                    { "name": "Remoto",      "color": "green" },
                    { "name": "Hibrido",     "color": "blue"  },
                    { "name": "Presencial",  "color": "red"   }
                ]
            }
        },
        "Notas":          { "rich_text": {} },
        "Seguimiento":    { "date": {} }
    }
}

res = requests.post(
    "https://api.notion.com/v1/databases",
    headers=headers,
    json=database
)

if res.status_code == 200:
    data = res.json()
    print("✅ Base de datos creada correctamente.")
    print(f"   ID: {data['id']}")
    print(f"   URL: {data['url']}")
    print("\n⚠️  Guarda el ID, lo necesitarás para configurar N8N:")
    print(f"   {data['id']}")
else:
    print(f"❌ Error {res.status_code}:")
    print(res.text)
