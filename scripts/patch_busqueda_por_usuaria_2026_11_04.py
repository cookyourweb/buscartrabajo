"""One n8n execution per user for the daily search, instead of all users in one.

    python3 scripts/patch_busqueda_por_usuaria_2026_11_04.py <in.json> <out.json>

Why (4 Nov 2026): the Render instance has 512 MB and n8n idles at ~75-80%. Since 1 Nov
the 9:00 search dies with "JavaScript heap out of memory" (exit 134) on most days,
because every user's sources, Groq calls and Notion writes live in ONE execution that
keeps every node's output. One more user would make it fail every day.

What changes:
- The 9:00 path (and the manual trigger) no longer runs the loop itself. A new HTTP node
  calls the workflow's own "Webhook — Buscar para user" once per user, one at a time
  (batch size 1, 10 s apart). That webhook answers when its run ends ("lastNode"), so the
  runs never overlap and each one frees its memory when it finishes.
- A user whose run fails does not stop the others (continueRegularOutput).
- Scoring (cv-server /puntuar-ofertas) runs ONCE, after all the users, instead of at the
  end of every per-user run. The loop's "done" branch no longer triggers it.

The webhook path is never written here: the URL reads it from the webhook node at run
time, so the public repo does not get the secret (see workflows/PROD/README.md).
"""
import copy
import json
import sys

WEBHOOK = "Webhook — Buscar para user"
NORMALIZAR_SCHEDULE = "Code — Normalizar users (schedule)"
LOOP = "Loop Over Users"
DESPERTAR_PUNTUAR = "Despertar CV Server (puntuar)"
LANZAR = "Lanzar búsqueda por usuaria"
N8N_HOST = "https://n8n-asistente-correo.onrender.com"

src, dst = sys.argv[1], sys.argv[2]
wf = json.load(open(src))
nodes = {n["name"]: n for n in wf["nodes"]}
assert LANZAR not in nodes, "already patched"
for nombre in (WEBHOOK, NORMALIZAR_SCHEDULE, LOOP, DESPERTAR_PUNTUAR):
    assert nombre in nodes, f"missing node: {nombre}"
assert nodes[WEBHOOK]["parameters"].get("responseMode") == "lastNode", \
    "the webhook must answer at the end of the run, or the per-user runs would overlap"

conns = wf["connections"]
assert [c["node"] for c in conns[NORMALIZAR_SCHEDULE]["main"][0]] == [LOOP]
assert [c["node"] for c in conns[LOOP]["main"][0]] == [DESPERTAR_PUNTUAR], \
    "expected the loop's done branch to start scoring"

base = nodes[NORMALIZAR_SCHEDULE]["position"]
lanzar = {
    "parameters": {
        "method": "POST",
        "url": f'={N8N_HOST}/webhook/{{{{ $node["{WEBHOOK}"].parameter["path"] }}}}',
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify($json) }}",
        "options": {
            "batching": {"batch": {"batchSize": 1, "batchInterval": 10000}},
            "timeout": 900000,
        },
    },
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [base[0] + 224, base[1] - 160],
    "name": LANZAR,
    "onError": "continueRegularOutput",
}
wf["nodes"].append(lanzar)

# 9:00 / manual path: users -> one call per user -> scoring once.
conns[NORMALIZAR_SCHEDULE]["main"][0] = [{"node": LANZAR, "type": "main", "index": 0}]
conns[LANZAR] = {"main": [[{"node": DESPERTAR_PUNTUAR, "type": "main", "index": 0}]]}
nodes[DESPERTAR_PUNTUAR]["executeOnce"] = True

# Per-user run: the loop ends there; scoring is the 9:00 path's job.
conns[LOOP]["main"][0] = []

json.dump(wf, open(dst, "w"), ensure_ascii=False, indent=2)
print(f"{src} -> {dst}: '{LANZAR}' added, scoring runs once after all users")
