#!/usr/bin/env python3
"""
Archiva (envía a papelera de Notion) TODAS las ofertas de la database
"Ofertas de Trabajo", para empezar de cero antes de un barrido nuevo.

- Lista todas las ofertas (paginado, sin límite de plan).
- Te las muestra y pide confirmación EXPLÍCITA antes de tocar nada.
- Archiva con PATCH /v1/pages/{id} {"archived": true} → van a papelera
  (recuperables ~30 días desde Notion). NO es borrado permanente.

Uso:
    python3 scripts/archivar_ofertas.py
"""

import requests

NOTION_API_KEY = input("Introduce tu NOTION_API_KEY: ").strip()
DATABASE_ID = "33d11515-f4b2-81ef-a776-d0ea698b748f"

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}


def listar_ofertas():
    """Devuelve [(page_id, empresa, puesto)] de todas las ofertas (paginado)."""
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    ofertas, cursor = [], None
    while True:
        payload = {"page_size": 100}
        if cursor:
            payload["start_cursor"] = cursor
        r = requests.post(url, headers=HEADERS, json=payload)
        r.raise_for_status()
        data = r.json()
        for pg in data.get("results", []):
            props = pg.get("properties", {})
            empresa = _texto(props.get("Empresa"))
            puesto = _texto(props.get("Puesto"))
            ofertas.append((pg["id"], empresa, puesto))
        if data.get("has_more"):
            cursor = data.get("next_cursor")
        else:
            break
    return ofertas


def _texto(prop):
    """Extrae texto de una propiedad title o rich_text de Notion."""
    if not prop:
        return ""
    partes = prop.get("title") or prop.get("rich_text") or []
    return "".join(p.get("plain_text", "") for p in partes).strip()


def archivar(page_id):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    r = requests.patch(url, headers=HEADERS, json={"archived": True})
    r.raise_for_status()


def main():
    print("\nBuscando ofertas en la database...")
    ofertas = listar_ofertas()
    if not ofertas:
        print("No hay ofertas. Nada que hacer.")
        return

    print(f"\nSe encontraron {len(ofertas)} ofertas:")
    for i, (_, empresa, puesto) in enumerate(ofertas, 1):
        print(f"  {i:2d}. {empresa or '(sin empresa)'} — {puesto or '(sin puesto)'}")

    resp = input(
        f"\n¿Archivar las {len(ofertas)} ofertas (van a papelera, recuperables)? "
        "Escribe SI para confirmar: "
    ).strip()
    if resp != "SI":
        print("Cancelado. No se tocó nada.")
        return

    ok, fallos = 0, []
    for page_id, empresa, _ in ofertas:
        try:
            archivar(page_id)
            ok += 1
        except Exception as e:
            fallos.append((empresa, str(e)))

    print(f"\nArchivadas: {ok}/{len(ofertas)}")
    if fallos:
        print("Fallos:")
        for empresa, err in fallos:
            print(f"  - {empresa}: {err}")
    else:
        print("Todo limpio. Listo para el barrido de cero.")


if __name__ == "__main__":
    main()
