#!/usr/bin/env python3
"""
Sync Notion Database Schema — añade las columnas que falten a la DB del workflow BuscarTrabajo.

Uso:
    python3 sync_notion_schema.py

Qué hace:
1. Lee el schema actual de la database de Notion
2. Compara con el schema esperado
3. Añade (PATCH) las columnas que faltan
4. NO toca las columnas existentes (aunque sean de tipo distinto — lo avisa)

Requisitos:
    pip install requests
"""

import requests
import sys

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
NOTION_TOKEN = "ntn_G464872773099dpLY7OzD7I4ZeZee38rKHsoVlmCV2z7A0"
DATABASE_ID = "33d11515-f4b2-81ef-a776-d0ea698b748f"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# Schema esperado — name → Notion property definition
SCHEMA_ESPERADO = {
    # Ya existentes probablemente, los listamos para referencia
    "Empresa":            {"title": {}},
    "Puesto":             {"rich_text": {}},
    "Estado":             {"select": {"options": [
        {"name": "Pendiente",        "color": "gray"},
        {"name": "Aprobado",         "color": "blue"},
        {"name": "En proceso",       "color": "yellow"},
        {"name": "Enviado a empresa","color": "green"},
        {"name": "Descartado",       "color": "red"}
    ]}},
    "Salario":            {"rich_text": {}},
    "Modalidad":          {"select": {"options": [
        {"name": "Remoto",     "color": "green"},
        {"name": "Hibrido",    "color": "yellow"},
        {"name": "Presencial", "color": "orange"}
    ]}},
    "Link oferta":        {"url": {}},
    "Notas":              {"rich_text": {}},
    "Link CV Drive":      {"url": {}},

    # Nuevos (20 Abril 2026)
    "Nombre Contacto":    {"rich_text": {}},
    "Email empresa":      {"email": {}},
    "Teléfono Contacto":  {"phone_number": {}},
    "Fecha Publicacion":  {"date": {}},
    "Fecha Envio Empresa":{"date": {}},
    "Email Enviado":      {"rich_text": {}},
    "Carta Enviada":      {"rich_text": {}},
}


def get_database():
    """Lee el schema actual de la database."""
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        print(f"❌ Error leyendo database: {r.status_code}")
        print(r.text)
        sys.exit(1)
    return r.json()


def type_of_prop(prop_def):
    """Devuelve el tipo de una propiedad (title, rich_text, select, etc.)."""
    for t in ("title", "rich_text", "number", "select", "multi_select",
              "date", "people", "files", "checkbox", "url", "email",
              "phone_number", "formula", "relation", "rollup",
              "created_time", "created_by", "last_edited_time",
              "last_edited_by", "status"):
        if t in prop_def:
            return t
    return "unknown"


def sync_schema():
    print("🔍 Leyendo schema actual de Notion...")
    db = get_database()
    current_props = db.get("properties", {})

    print(f"\n📊 Columnas actuales ({len(current_props)}):")
    for name, prop in current_props.items():
        t = type_of_prop(prop)
        print(f"   • {name:25} → {t}")

    print(f"\n🎯 Schema esperado ({len(SCHEMA_ESPERADO)} columnas)")

    # Calcular diferencias
    faltantes = {}
    conflictos = []
    for name, expected_def in SCHEMA_ESPERADO.items():
        if name not in current_props:
            faltantes[name] = expected_def
        else:
            # Comparar tipos
            expected_type = list(expected_def.keys())[0]
            current_type = type_of_prop(current_props[name])
            if current_type != expected_type:
                conflictos.append((name, current_type, expected_type))

    if not faltantes and not conflictos:
        print("\n✅ Todas las columnas existen y tienen el tipo correcto. Nada que hacer.")
        return

    if conflictos:
        print(f"\n⚠️  Columnas con TIPO INCORRECTO ({len(conflictos)}):")
        for name, current, expected in conflictos:
            print(f"   ⚠️  {name}: tienes {current}, el workflow espera {expected}")
        print("   → Para estas columnas, debes eliminarlas en Notion manualmente y volver a ejecutar este script.")

    if faltantes:
        print(f"\n➕ Columnas FALTANTES ({len(faltantes)}):")
        for name in faltantes:
            expected_type = list(faltantes[name].keys())[0]
            print(f"   + {name:25} ({expected_type})")

        confirmar = input("\n¿Añadir las columnas faltantes? [S/n]: ").strip().lower()
        if confirmar and confirmar != "s":
            print("Cancelado.")
            return

        # PATCH para añadir las propiedades
        url = f"https://api.notion.com/v1/databases/{DATABASE_ID}"
        body = {"properties": faltantes}
        r = requests.patch(url, headers=HEADERS, json=body)

        if r.status_code == 200:
            print(f"\n✅ {len(faltantes)} columnas añadidas correctamente.")
            # Listar
            for name in faltantes:
                print(f"   ✅ {name}")
        else:
            print(f"\n❌ Error añadiendo columnas: {r.status_code}")
            print(r.text)
            sys.exit(1)


if __name__ == "__main__":
    sync_schema()
