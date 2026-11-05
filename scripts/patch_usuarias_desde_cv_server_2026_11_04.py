"""Get the active users from cv-server instead of querying Notion from n8n.

    python3 scripts/patch_usuarias_desde_cv_server_2026_11_04.py <in.json> <out.json>

Why (4 Nov 2026): the Users database now holds TWO data sources (a linked view of
Ofertas de Trabajo was added to it). POST /v1/databases/{id}/query with
Notion-Version 2022-06-28 then returns no users, and the daily search finds nobody.
The fix is to query the Users data source (API 2025-09-03), but n8n's Notion
credential forces an old Notion-Version header, so Notion answers "Invalid request URL".

cv-server already reads the users with its own token and, since the hotfix
"read users through the Users data source", GET /usuarios?formato=notion returns the
raw Notion pages under `results`. The next node ("Code — Normalizar users (schedule)")
reads `$input.first().json.results`, so nothing else changes.

The node keeps its name, so every reference to it still works. It uses the existing
"cv-server clave de maquina" credential, a long timeout for Render's cold start, and
keeps its retries.

Deploy order: the cv-server hotfix must be live BEFORE this workflow is published.
"""
import json
import sys

NODO = "Notion — Query usuarios activos"
REFERENCIA = "CV Server - Puntuar Ofertas"   # copy its machine-key credential
URL = "https://cv-server-ggd8.onrender.com/usuarios?formato=notion"

src, dst = sys.argv[1], sys.argv[2]
wf = json.load(open(src))
nodos = {n["name"]: n for n in wf["nodes"]}
nodo, ref = nodos[NODO], nodos[REFERENCIA]
assert "api.notion.com" in nodo["parameters"]["url"], "already patched or changed"

nodo["parameters"] = {
    "method": "GET",
    "url": URL,
    "authentication": "genericCredentialType",
    "genericAuthType": "httpHeaderAuth",
    "options": {"timeout": 120000},
}
nodo["credentials"] = json.loads(json.dumps(ref["credentials"]))
nodo["retryOnFail"] = True
nodo["maxTries"] = 4
nodo["waitBetweenTries"] = 5000

json.dump(wf, open(dst, "w"), ensure_ascii=False, indent=2)
print(f"{NODO}: now GET {URL} with the machine-key credential")
