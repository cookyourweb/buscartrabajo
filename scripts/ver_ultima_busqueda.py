#!/usr/bin/env python3
"""Shows what the last search runs did, node by node, without opening n8n.

    python3 scripts/ver_ultima_busqueda.py            # last 6 runs
    python3 scripts/ver_ultima_busqueda.py 10         # last 10 runs

For each run of the daily-search workflow: mode (manual, webhook = one per user,
trigger), status, and how many items came out of every search node. That tells apart
"the sources brought nothing", "the filter dropped everything", "everything was already
in Notion" and "a run failed".

Reads N8N_HOST and N8N_API_KEY from .env and never prints them.
"""
import json
import sys
import urllib.request
from pathlib import Path

WF_ID = "IGVSEBCp1sFMXYYB"
NODOS = [
    "Despertar CV Server (usuarias)", "Notion — Query usuarios activos",
    "Code — Normalizar users (schedule)", "Lanzar búsqueda por usuaria",
    "Code — Normalizar (interno)", "Notion - Ofertas existentes",
    "Buscar en Remotive", "Buscar en Adzuna", "Buscar en Tecnoempleo", "Buscar en Google Jobs",
    "Formatear ofertas", "Groq - Generar Ofertas", "Code - Normalizar Modalidad",
    "Notion - Crear Oferta", "Brevo - Enviar Notificacion", "CV Server - Puntuar Ofertas",
]


def env(nombre: str) -> str:
    for linea in (Path(__file__).resolve().parent.parent / ".env").read_text().splitlines():
        if linea.startswith(nombre + "="):
            return linea.split("=", 1)[1].strip().strip('"')
    sys.exit(f"{nombre} no está en .env")


def get(ruta: str) -> dict:
    req = urllib.request.Request(env("N8N_HOST").rstrip("/") + ruta,
                                 headers={"X-N8N-API-KEY": env("N8N_API_KEY")})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def items(run: dict) -> int:
    salida = (run.get("data") or {}).get("main") or []
    return sum(len(rama or []) for rama in salida)


def main() -> None:
    limite = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    ejecuciones = get(f"/api/v1/executions?workflowId={WF_ID}&limit={limite * 4}&includeData=true")["data"]
    mostradas = 0
    for e in ejecuciones:
        run_data = (((e.get("data") or {}).get("resultData") or {}).get("runData")) or {}
        if not any(n in run_data for n in NODOS):
            continue  # the 15-minute "Revisar Aprobadas" checks: not a search
        mostradas += 1
        print(f"\n#{e['id']}  {e.get('mode')}  {e.get('status')}  "
              f"{(e.get('startedAt') or '')[:19]} → {(e.get('stoppedAt') or '…')[:19]}")
        error = ((e.get("data") or {}).get("resultData") or {}).get("error")
        if error:
            print(f"   ERROR: {error.get('message', '')[:200]}")
        for nodo in NODOS:
            if nodo in run_data:
                ultimo = run_data[nodo][-1]
                fallo = ultimo.get("error")
                detalle = f"ERROR {fallo.get('message', '')[:120]}" if fallo else f"{items(ultimo)} items"
                print(f"   {nodo:<38} {detalle}")
        if mostradas >= limite:
            break
    if not mostradas:
        print("No hay ejecuciones de búsqueda recientes (solo las comprobaciones de cada 15 minutos).")


if __name__ == "__main__":
    main()
