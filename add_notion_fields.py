#!/usr/bin/env python3
"""
Script para añadir campos de contacto de reclutador a la database de Notion.
Campos que se añadirán:
- Nombre Contacto (Rich text)
- Teléfono Contacto (Phone number)
"""

import requests
import json

# Configuración
NOTION_API_KEY = "***REMOVED_NOTION_TOKEN***"
DATABASE_ID = "33d11515-f4b2-81ef-a776-d0ea698b748f"

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# Campos a añadir
NEW_PROPERTIES = {
    "Nombre Contacto": {
        "rich_text": {}
    },
    "Teléfono Contacto": {
        "phone_number": {}
    }
}

def add_properties_to_database():
    """Añade nuevas propiedades a la database de Notion."""

    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}"

    # Notion API usa PATCH para actualizar el schema
    payload = {
        "properties": NEW_PROPERTIES
    }

    print(f"Añadiendo campos a la database {DATABASE_ID}...")
    print(f"Campos: {list(NEW_PROPERTIES.keys())}")

    response = requests.patch(url, headers=HEADERS, json=payload)

    if response.status_code == 200:
        print("\n✅ Campos añadidos correctamente!")

        # Mostrar schema actualizado
        data = response.json()
        print("\nSchema actualizado:")
        for prop_name, prop_data in data.get("properties", {}).items():
            print(f"  - {prop_name}: {prop_data.get('type')}")

        return True
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(f"Detalle: {response.text}")
        return False

def verify_database():
    """Verifica que la database es accesible y muestra el schema actual."""

    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}"

    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        print(f"\nDatabase: {data.get('title', [{}])[0].get('text', 'N/A')}")
        print(f"Propiedades actuales:")

        for prop_name, prop_data in data.get("properties", {}).items():
            print(f"  - {prop_name}: {prop_data.get('type')}")

        return True
    else:
        print(f"Error: {response.status_code}")
        print(f"Detalle: {response.text}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Notion Database - Añadir Campos de Contacto")
    print("=" * 60)

    # Paso 1: Verificar database
    print("\n1. Verificando acceso a la database...")
    if not verify_database():
        print("\n❌ No se pudo acceder a la database. Verifica el API key.")
        exit(1)

    # Paso 2: Añadir campos
    print("\n2. Añadiendo nuevos campos...")
    if add_properties_to_database():
        print("\n✅ Proceso completado!")
        print("\nAhora puedes usar estos campos en el workflow n8n:")
        print("  - Nombre Contacto")
        print("  - Teléfono Contacto")
        print("  - Email empresa (ya existía)")
    else:
        print("\n❌ Error al añadir los campos.")
        exit(1)
