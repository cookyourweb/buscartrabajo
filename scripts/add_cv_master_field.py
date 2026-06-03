#!/usr/bin/env python3
"""
add_cv_master_field.py
Añade el campo `cv_master_file_id` (Text) a la DB de Usuarios en Notion
y opcionalmente actualiza el valor para un usuario concreto.

Uso:
    python add_cv_master_field.py                    # Solo crea el campo
    python add_cv_master_field.py --update-vero      # Crea el campo Y rellena el de Verónica
    python add_cv_master_field.py --update-user EMAIL FILE_ID

Requisitos:
    pip install requests python-dotenv

Variables de entorno necesarias (en .env o exportadas):
    NOTION_TOKEN         - Token de integración Notion
    NOTION_DB_USUARIOS   - ID de la DB de Usuarios (default: 34811515f4b280f19a42f8da5e91a8fe)
"""

import os
import sys
import argparse
import requests
from typing import Optional

try:
    from dotenv import load_dotenv
    from pathlib import Path
    # Los scripts en buscartrabajo/scripts/ leen el .env del cv-server
    # (única fuente de verdad para variables de entorno)
    project_root = Path(__file__).resolve().parent.parent  # buscartrabajo/
    env_paths_to_try = [
        project_root / 'cv-server' / '.env',  # cv-server/.env (preferido)
        project_root / '.env',                 # raíz/.env (fallback)
    ]
    loaded = False
    for env_path in env_paths_to_try:
        if env_path.exists():
            load_dotenv(env_path)
            loaded = True
            break
    if not loaded:
        load_dotenv()  # último recurso: directorio actual
except ImportError:
    pass  # Si no está python-dotenv, usa env vars del sistema

# ─── Configuración ──────────────────────────────────────────────
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DB_USUARIOS = os.getenv(
    "NOTION_DB_USUARIOS",
    "34811515f4b280f19a42f8da5e91a8fe"  # default
)
NOTION_VERSION = "2022-06-28"

# Nombre del campo nuevo a crear
NEW_FIELD_NAME = "cv_master_file_id"

# Valor por defecto para Verónica (file_id del CV master)
VERONICA_EMAIL = "hello.cookyourweb@gmail.com"
VERONICA_CV_MASTER_FILE_ID = "1jJqjZ7p4vB99atBIBAPL-gYbXZKiixMD"


# ─── Helpers ────────────────────────────────────────────────────
def headers() -> dict:
    if not NOTION_TOKEN:
        sys.exit("❌ Error: NOTION_TOKEN no está definido. Crea un .env o exporta la variable.")
    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json"
    }


def get_database() -> dict:
    """Obtiene los detalles de la DB para verificar las propiedades existentes."""
    url = f"https://api.notion.com/v1/databases/{NOTION_DB_USUARIOS}"
    r = requests.get(url, headers=headers(), timeout=30)
    if r.status_code != 200:
        sys.exit(f"❌ Error obteniendo DB: {r.status_code} {r.text[:200]}")
    return r.json()


def field_exists(db: dict, field_name: str) -> bool:
    """Verifica si una propiedad ya existe en la DB."""
    return field_name in db.get("properties", {})


def add_text_field(field_name: str) -> bool:
    """Añade un campo de tipo rich_text a la DB."""
    url = f"https://api.notion.com/v1/databases/{NOTION_DB_USUARIOS}"
    payload = {
        "properties": {
            field_name: {
                "rich_text": {}  # tipo "text" en Notion
            }
        }
    }
    r = requests.patch(url, headers=headers(), json=payload, timeout=30)
    if r.status_code == 200:
        print(f"✅ Campo '{field_name}' creado correctamente en la DB")
        return True
    else:
        print(f"❌ Error creando el campo: {r.status_code} {r.text[:300]}")
        return False


def find_user_page_by_email(email: str) -> Optional[str]:
    """Busca la página del usuario por email y devuelve el page_id."""
    url = f"https://api.notion.com/v1/databases/{NOTION_DB_USUARIOS}/query"
    payload = {
        "filter": {
            "property": "Email",  # Asume que el campo email se llama 'Email'
            "email": {"equals": email}
        }
    }
    r = requests.post(url, headers=headers(), json=payload, timeout=30)
    if r.status_code != 200:
        print(f"⚠️  Error buscando usuario: {r.status_code} {r.text[:200]}")
        return None
    
    results = r.json().get("results", [])
    if not results:
        print(f"⚠️  No se encontró usuario con email: {email}")
        return None
    return results[0]["id"]


def update_user_field(page_id: str, field_name: str, value: str) -> bool:
    """Actualiza un campo de texto en una página de usuario."""
    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {
        "properties": {
            field_name: {
                "rich_text": [
                    {"text": {"content": value}}
                ]
            }
        }
    }
    r = requests.patch(url, headers=headers(), json=payload, timeout=30)
    if r.status_code == 200:
        print(f"✅ Campo '{field_name}' actualizado a '{value}' en la página")
        return True
    else:
        print(f"❌ Error actualizando: {r.status_code} {r.text[:300]}")
        return False


# ─── Programa principal ─────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Añade el campo cv_master_file_id a la DB de Usuarios en Notion"
    )
    parser.add_argument(
        "--update-vero",
        action="store_true",
        help="Tras crear el campo, actualiza también el valor para Verónica (hello.cookyourweb@gmail.com)"
    )
    parser.add_argument(
        "--update-user",
        nargs=2,
        metavar=("EMAIL", "FILE_ID"),
        help="Actualiza el cv_master_file_id de un usuario específico"
    )
    args = parser.parse_args()

    print("=" * 60)
    print(f"🚀 Añadir campo '{NEW_FIELD_NAME}' a Notion DB Usuarios")
    print(f"   DB: {NOTION_DB_USUARIOS}")
    print("=" * 60)

    # 1. Obtener la DB y verificar si el campo ya existe
    print("\n📋 Paso 1: Verificando estado actual de la DB...")
    db = get_database()
    existing_props = list(db.get("properties", {}).keys())
    print(f"   Propiedades actuales ({len(existing_props)}): {', '.join(existing_props[:5])}{'...' if len(existing_props) > 5 else ''}")

    if field_exists(db, NEW_FIELD_NAME):
        print(f"\n✅ El campo '{NEW_FIELD_NAME}' YA existe. No se vuelve a crear.")
    else:
        # 2. Crear el campo
        print(f"\n🔧 Paso 2: Creando el campo '{NEW_FIELD_NAME}'...")
        if not add_text_field(NEW_FIELD_NAME):
            sys.exit(1)

    # 3. Actualizar usuario(s) si se pidió
    if args.update_vero:
        print(f"\n👤 Paso 3: Actualizando el campo para Verónica ({VERONICA_EMAIL})...")
        page_id = find_user_page_by_email(VERONICA_EMAIL)
        if page_id:
            update_user_field(page_id, NEW_FIELD_NAME, VERONICA_CV_MASTER_FILE_ID)

    if args.update_user:
        email, file_id = args.update_user
        print(f"\n👤 Paso 3: Actualizando el campo para {email}...")
        page_id = find_user_page_by_email(email)
        if page_id:
            update_user_field(page_id, NEW_FIELD_NAME, file_id)

    print("\n" + "=" * 60)
    print("✅ Proceso completado")
    print("=" * 60)


if __name__ == "__main__":
    main()
