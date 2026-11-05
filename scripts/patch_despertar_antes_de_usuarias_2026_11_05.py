"""Wake cv-server before asking it for the active users.

    python3 scripts/patch_despertar_antes_de_usuarias_2026_11_05.py <in.json> <out.json>

Why (5 Nov 2026): the users node now calls cv-server (GET /usuarios?formato=notion).
On Render's free plan cv-server sleeps when idle and answers "Application loading"
(503) for about a minute while it wakes up. The node's 4 retries of 5 s are not
enough, so the first manual run failed after 22 s, and the 9:00 run would too.

Same pattern the workflow already uses before scoring ("Despertar CV Server
(puntuar)" + "Esperar arranque (puntuar)"): GET /health with retries and a long
timeout, then wait 60 s, then ask for the users.
"""
import copy
import json
import sys

USUARIAS = "Notion — Query usuarios activos"
DESPERTAR_REF = "Despertar CV Server (puntuar)"
ESPERAR_REF = "Esperar arranque (puntuar)"
DESPERTAR = "Despertar CV Server (usuarias)"
ESPERAR = "Esperar arranque (usuarias)"
DISPARADORES = ("Schedule Trigger (9am)", "Manual Trigger")

src, dst = sys.argv[1], sys.argv[2]
wf = json.load(open(src))
nodos = {n["name"]: n for n in wf["nodes"]}
assert DESPERTAR not in nodos, "already patched"
conns = wf["connections"]
for d in DISPARADORES:
    assert [c["node"] for c in conns[d]["main"][0]] == [USUARIAS], f"{d} must point to {USUARIAS}"

x, y = nodos[USUARIAS]["position"]
despertar = copy.deepcopy(nodos[DESPERTAR_REF])
esperar = copy.deepcopy(nodos[ESPERAR_REF])
for n in (despertar, esperar):
    n.pop("id", None)
    n.pop("webhookId", None)
despertar.update(name=DESPERTAR, position=[x - 40, y - 140])
esperar.update(name=ESPERAR, position=[x + 60, y - 140])
wf["nodes"] += [despertar, esperar]

for d in DISPARADORES:
    conns[d]["main"][0] = [{"node": DESPERTAR, "type": "main", "index": 0}]
conns[DESPERTAR] = {"main": [[{"node": ESPERAR, "type": "main", "index": 0}]]}
conns[ESPERAR] = {"main": [[{"node": USUARIAS, "type": "main", "index": 0}]]}

json.dump(wf, open(dst, "w"), ensure_ascii=False, indent=2)
print(f"triggers -> {DESPERTAR} -> {ESPERAR} (60 s) -> {USUARIAS}")
