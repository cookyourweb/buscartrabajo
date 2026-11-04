"""Query the users through Notion's data source, not the database (API 2025-09-03).

    python3 scripts/patch_usuarias_data_source_2026_11_04.py <in.json> <out.json>

Why (4 Nov 2026): the Users database now holds TWO data sources (Users, plus a linked
"All Users" view of Ofertas de Trabajo). The old endpoint POST /v1/databases/{id}/query
with Notion-Version 2022-06-28 cannot tell which one to query and returns no users, so
the daily search finds nobody. Querying the data source itself
(POST /v1/data_sources/{id}/query, Notion-Version 2025-09-03) works however many views
or sources are added later. The filter and the result format are the same.
"""
import json
import sys

NODO = "Notion — Query usuarios activos"
DB_USUARIOS = "34811515f4b280f19a42f8da5e91a8fe"
DS_USUARIOS = "34811515-f4b2-80d6-875a-000b7b858306"

src, dst = sys.argv[1], sys.argv[2]
wf = json.load(open(src))
nodo = next(n for n in wf["nodes"] if n["name"] == NODO)
p = nodo["parameters"]
assert p["url"] == f"https://api.notion.com/v1/databases/{DB_USUARIOS}/query", "already patched or changed"

p["url"] = f"https://api.notion.com/v1/data_sources/{DS_USUARIOS}/query"
cabeceras = p["headerParameters"]["parameters"]
version = next(h for h in cabeceras if h["name"] == "Notion-Version")
version["value"] = "2025-09-03"

json.dump(wf, open(dst, "w"), ensure_ascii=False, indent=2)
print(f"{NODO}: now queries data source {DS_USUARIOS} with Notion-Version 2025-09-03")
