"""Adds Google Jobs (SerpApi) as a per-user source, between Tecnoempleo and Formatear ofertas.

    python3 scripts/patch_google_jobs_2026_11_01.py <in.json> <out.json>

The SerpApi key is NOT in the workflow: the node uses an n8n "Query Auth" credential
(name `api_key`) that the owner creates in the n8n UI and selects on the node.
Budget: one search per active user per day (free plan: 250 searches a month).
"""
import copy
import json
import sys

src, dst = sys.argv[1], sys.argv[2]
wf = json.load(open(src))
nodes = {n["name"]: n for n in wf["nodes"]}
assert "Buscar en Google Jobs" not in nodes, "already patched"

tecno = nodes["Buscar en Tecnoempleo"]
gj = copy.deepcopy(nodes["Buscar en Adzuna"])
gj.pop("id", None)
gj.pop("credentials", None)
gj["name"] = "Buscar en Google Jobs"
gj["position"] = [tecno["position"][0] + 224, tecno["position"][1] + 200]
# Per-user query: the user's first target role + "remote Europe", searched from the UK.
# Google Jobs returns nothing for Spain or other EU countries (tested 1 Nov 2026: Madrid,
# Berlin, Amsterdam, Lisbon all 0), but a UK search for remote-Europe roles returns jobs
# open to people in Spain. Spain itself is covered by Tecnoempleo and LinkedIn.
gj["parameters"] = {
    "url": (
        "=https://serpapi.com/search.json?engine=google_jobs&hl=en&gl=uk"
        "&location=London%2CEngland%2CUnited%20Kingdom"
        "&q={{ encodeURIComponent(($('Loop Over Users').item.json.rol || 'Software Engineer').split('·')[0].trim() + ' remote Europe') }}"
    ),
    "authentication": "genericCredentialType",
    "genericAuthType": "httpQueryAuth",
    "options": {"timeout": 60000},
}
gj["onError"] = "continueRegularOutput"
wf["nodes"].append(gj)

# Rewire: Tecnoempleo -> Google Jobs -> Formatear ofertas.
conns = wf["connections"]
assert conns["Buscar en Tecnoempleo"]["main"] == [[{"node": "Formatear ofertas", "type": "main", "index": 0}]]
conns["Buscar en Tecnoempleo"]["main"] = [[{"node": "Buscar en Google Jobs", "type": "main", "index": 0}]]
conns["Buscar en Google Jobs"] = {"main": [[{"node": "Formatear ofertas", "type": "main", "index": 0}]]}

# Parse Google Jobs results in Formatear ofertas, with the same filters as the other sources.
fmt = nodes["Formatear ofertas"]["parameters"]
anchor = "// CAP modo prueba"
assert anchor in fmt["jsCode"]
block = r"""// Google Jobs via SerpApi (1 Nov 2026). Per-user query built in the node.
// apply_options[0] is usually the employer's or a portal's page; share_link is the fallback.
try {
  const g = $('Buscar en Google Jobs').first().json || {};
  for (const j of (g.jobs_results || []).slice(0, 10)) {
    const link = ((j.apply_options || [])[0] || {}).link || j.share_link || '';
    const descReal = limpiar(j.description);
    if (!link || !matchea(j.title, descReal)) continue;
    if (!esNueva(link)) continue;
    if (!esNuevaKey(j.company_name, j.title)) continue;
    const ext = j.detected_extensions || {};
    const ubic = ext.work_from_home ? 'Remoto' : (j.location || '');
    idiomaPorLink[String(link).trim()] = detIdioma(j.title + ' ' + descReal);
    descripcionPorLink[String(link).trim()] = String(descReal || '').slice(0, 1800);
    ubicacionPorLink[String(link).trim()] = ubic;
    out.push('[Google Jobs via ' + (j.via || '?') + '] ' + j.title + ' | ' + (j.company_name || '') + ' | ' + ubic + ' | ' + (ext.salary || 's/i') + ' | ' + link + ' | ' + descReal.slice(0, 600));
  }
} catch (e) {}

"""
fmt["jsCode"] = fmt["jsCode"].replace(anchor, block + anchor, 1)

json.dump(wf, open(dst, "w"), ensure_ascii=False, indent=2)
print("ok:", dst)
