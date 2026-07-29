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

import os
import json
import urllib.request
import urllib.error

DATABASE_ID = "33d11515-f4b2-81ef-a776-d0ea698b748f"

# Nombres de variable posibles para el token (el tuyo puede ser cualquiera de estos)
TOKEN_VARS = ["NOTION_TOKEN", "NOTION_API_KEY", "NOTION_KEY", "NOTION_SECRET"]

# .env donde puede estar el token (se prueban en orden)
ENV_PATHS = [
    os.path.join(os.path.dirname(__file__), "..", ".env"),
    os.path.join(os.path.dirname(__file__), "..", "..", "cv-server", ".env"),
    ".env",
]


def _leer_env_file(path):
    """Lee un .env sencillo y devuelve {VAR: valor} (sin dependencias externas)."""
    valores = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea or linea.startswith("#") or "=" not in linea:
                    continue
                clave, _, valor = linea.partition("=")
                valores[clave.strip()] = valor.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return valores


def obtener_token():
    """Busca el token en variables de entorno, luego en .env, y si no, lo pide."""
    for var in TOKEN_VARS:
        if os.environ.get(var):
            print(f"Token leído de la variable de entorno {var}.")
            return os.environ[var].strip()
    for path in ENV_PATHS:
        valores = _leer_env_file(path)
        for var in TOKEN_VARS:
            if valores.get(var):
                print(f"Token leído de {os.path.abspath(path)} ({var}).")
                return valores[var].strip()
    return input("No encontré el token en el entorno ni en .env. Pégalo aquí: ").strip()


NOTION_API_KEY = obtener_token()

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}


def _api(url, method="GET", body=None):
    """Llamada HTTP a la API de Notion usando solo la stdlib (sin requests)."""
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detalle = e.read().decode("utf-8", "replace")
        raise RuntimeError(f"HTTP {e.code}: {detalle}") from None


def listar_ofertas():
    """Devuelve [(page_id, empresa, puesto)] de todas las ofertas (paginado)."""
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    ofertas, cursor = [], None
    while True:
        payload = {"page_size": 100}
        if cursor:
            payload["start_cursor"] = cursor
        data = _api(url, method="POST", body=payload)
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
    _api(url, method="PATCH", body={"archived": True})


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
