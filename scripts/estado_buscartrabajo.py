#!/usr/bin/env python3
"""Estado del sistema BuscarTrabajo en un vistazo.

    python3 scripts/estado_buscartrabajo.py

Responde a las tres preguntas que importan:
  1. Se ejecutó el disparo de las 9:00 y cómo acabó
  2. Entraron ofertas nuevas en Notion
  3. Los crons siguen donde deben (nadie los ha vuelto a poner a cada minuto)

Lee las credenciales del .env y NUNCA las imprime.
Documentado en docs/runbooks/19-RUNBOOK-SISTEMA-PARADO-2026-08-05.md
"""
import json
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

HOST = "https://n8n-asistente-correo.onrender.com"
WF_ID = "CsvmtPcLVmGIZg6C"          # BuscarTrabajo - Ofertas Diarias (PROD, dedup ON)
DB_OFERTAS = "33d11515f4b281efa776d0ea698b748f"
RAIZ = Path(__file__).resolve().parent.parent

VERDE, ROJO, AMBAR, FIN = "\033[32m", "\033[31m", "\033[33m", "\033[0m"


def env():
    valores = {}
    ruta = RAIZ / ".env"
    if not ruta.exists():
        sys.exit(f"No existe {ruta}")
    for linea in ruta.read_text(encoding="utf-8", errors="replace").splitlines():
        linea = linea.strip()
        if linea and not linea.startswith("#") and "=" in linea:
            clave, _, valor = linea.partition("=")
            valores[clave.strip()] = valor.strip().strip("'\"")
    return valores


E = env()
# La key es un JWT. Si trae basura pegada al final, el servidor devuelve 401 y
# parece revocada cuando no lo está. Ya pasó el 5-ago con un '<' de más.
bruto = E.get("N8N_API_KEY", "")
jwt = re.match(r"[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+", bruto)
if not jwt:
    sys.exit("N8N_API_KEY ausente o con formato raro en el .env")
if jwt.group(0) != bruto:
    print(f"{AMBAR}AVISO: la N8N_API_KEY del .env tiene "
          f"{len(bruto) - len(jwt.group(0))} caracteres de basura al final. "
          f"Se ignoran, pero conviene limpiarlos.{FIN}")
N8N_KEY = jwt.group(0)
NOTION = E.get("NOTION_TOKEN", "")


def pedir(url, cabeceras, cuerpo=None, metodo="GET", intentos=3):
    """Devuelve (ok, codigo, datos). ok=False significa NO SE PUDO PREGUNTAR."""
    ultimo = None
    for i in range(intentos):
        datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
        req = urllib.request.Request(url, data=datos, headers=cabeceras, method=metodo)
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return True, r.status, json.loads(r.read() or b"{}")
        except urllib.error.HTTPError as e:
            return True, e.code, {}
        except Exception as e:
            ultimo = f"{type(e).__name__}"
            if i < intentos - 1:
                time.sleep(4)
    return False, ultimo, {}


def n8n(ruta):
    return pedir(HOST + ruta, {"X-N8N-API-KEY": N8N_KEY})


def notion(cuerpo):
    return pedir(
        f"https://api.notion.com/v1/databases/{DB_OFERTAS}/query",
        {"Authorization": f"Bearer {NOTION}", "Notion-Version": "2022-06-28",
         "Content-Type": "application/json"},
        cuerpo, "POST",
    )


ahora = datetime.now(timezone.utc)
print(f"\n{'=' * 66}\n  ESTADO BUSCARTRABAJO   {ahora:%Y-%m-%d %H:%M} UTC "
      f"({datetime.now():%H:%M} local)\n{'=' * 66}")

# --- 1. La instancia esta viva? Sondeo, no una sola llamada ---
codigos = []
for _ in range(3):
    ok, cod, _ = pedir(HOST + "/healthz", {}, intentos=1)
    codigos.append(cod if ok else "sin red")
    time.sleep(2)
viva = all(c == 200 for c in codigos)
color = VERDE if viva else ROJO
print(f"\n[1] Instancia n8n : {color}{codigos}{FIN}")
if not viva:
    print(f"    {ROJO}Va y viene. Si aparecen 502 se esta reiniciando.{FIN}")

# --- 2. Los crons donde deben estar ---
ok, cod, wf = n8n(f"/api/v1/workflows/{WF_ID}")
print(f"\n[2] Configuracion del workflow (http={cod})")
if not ok or cod != 200:
    print(f"    {ROJO}No se pudo leer. 401 = revisa la N8N_API_KEY del .env{FIN}")
else:
    esperado = {"Schedule Trigger (9am)": "0 9 * * *",
                "Cron - Revisar Aprobadas": "*/15 * * * *"}
    for n in wf.get("nodes", []):
        nombre = n.get("name")
        if nombre in esperado:
            expr = ((n.get("parameters", {}).get("rule", {}).get("interval") or [{}])[0]
                    .get("expression", "?"))
            bien = expr == esperado[nombre]
            c = VERDE if bien else ROJO
            aviso = "" if bien else f"  <== deberia ser {esperado[nombre]}"
            print(f"    {nombre:26s} {c}{expr}{FIN}{aviso}")
        if nombre == "Wait - Rate Limit Groq":
            seg = n.get("parameters", {}).get("amount")
            c = VERDE if (seg or 99) <= 5 else ROJO
            print(f"    {nombre:26s} {c}{seg}s{FIN}"
                  + ("" if (seg or 99) <= 5 else "  <== una espera larga pierde la ejecucion"))
        if nombre == "Formatear ofertas":
            js = n.get("parameters", {}).get("jsCode", "")
            tope = re.search(r"k <= (\d+); k\+\+", js)
            valor = int(tope.group(1)) if tope else 0
            c = VERDE if valor >= 80 else ROJO
            print(f"    {'tope ofertas del RSS':26s} {c}{valor}{FIN}"
                  + ("" if valor >= 80 else "  <== el feed trae 80, se pierden ofertas"))
        if nombre == "Code - Normalizar Modalidad":
            js = n.get("parameters", {}).get("jsCode", "")
            asume = "let modalidad = 'Presencial'" in js
            c = ROJO if asume else VERDE
            print(f"    {'filtro modalidad':26s} "
                  f"{c}{'ASUME Presencial y descarta' if asume else 'no asume, marca Sin confirmar'}{FIN}")

# --- 3. Ejecuciones recientes ---
ok, cod, ex = n8n(f"/api/v1/executions?limit=100&workflowId={WF_ID}&includeData=false")
print(f"\n[3] Ejecuciones (http={cod})")
if not ok or cod != 200:
    print(f"    {ROJO}No se pudo consultar. Esto NO significa que no haya disparado.{FIN}")
else:
    filas = ex.get("data", [])
    estados = Counter(e.get("status") for e in filas)
    print(f"    ultimas {len(filas)}: {dict(estados)}")

    # Ritmo: cuantas en la ultima hora. Con el cron a 15 min deberian ser ~4
    hace_una_hora = ahora - timedelta(hours=1)
    recientes = 0
    for e in filas:
        try:
            t = datetime.strptime(e["startedAt"][:19], "%Y-%m-%dT%H:%M:%S").replace(
                tzinfo=timezone.utc)
            if t > hace_una_hora:
                recientes += 1
        except Exception:
            pass
    c = VERDE if recientes <= 8 else ROJO
    print(f"    en la ultima hora: {c}{recientes}{FIN}"
          + ("" if recientes <= 8 else "  <== demasiadas, algun cron esta disparado"))

    # El disparo diario de las 07:00 UTC
    print("\n    disparo diario de las 07:00 UTC (09:00 CEST):")
    por_dia = {}
    for e in filas:
        s = e.get("startedAt", "")
        if "T07:0" in s:
            por_dia.setdefault(s[:10], []).append((e.get("id"), e.get("status")))
    if not por_dia:
        print(f"      {AMBAR}ninguno en las ultimas {len(filas)} ejecuciones{FIN}")
    for dia in sorted(por_dia, reverse=True)[:5]:
        detalle = ", ".join(f"{i}={st}" for i, st in sorted(por_dia[dia]))
        malo = "crashed" in detalle
        print(f"      {ROJO if malo else VERDE}{dia}: {detalle}{FIN}")

# --- 4. Ofertas en Notion ---
ok, cod, res = notion({"page_size": 12, "sorts": [{"timestamp": "created_time",
                                                   "direction": "descending"}]})
print(f"\n[4] Ofertas en Notion (http={cod})")
if not ok or cod != 200:
    print(f"    {ROJO}No se pudo consultar Notion.{FIN}")
else:
    def texto(props, nombre, tipo):
        v = props.get(nombre, {}).get(tipo, [])
        return v[0].get("plain_text", "") if isinstance(v, list) and v else ""

    hoy = ahora.strftime("%Y-%m-%d")
    ayer = (ahora - timedelta(days=1)).strftime("%Y-%m-%d")
    n_hoy = 0
    for p in res.get("results", []):
        creado = p.get("created_time", "")
        pr = p["properties"]
        mod = (pr.get("Modalidad", {}).get("select") or {}).get("name", "-")
        marca = ""
        if creado.startswith(hoy):
            n_hoy += 1
            marca = f"  {VERDE}<== HOY{FIN}"
        elif creado.startswith(ayer):
            marca = "  <== ayer"
        print(f"    {creado[:16]} | {texto(pr,'Empresa','title')[:26]:26s} | "
              f"{texto(pr,'Puesto','rich_text')[:32]:32s} | {mod}{marca}")
    c = VERDE if n_hoy else AMBAR
    print(f"\n    creadas hoy: {c}{n_hoy}{FIN}")
    if not n_hoy:
        print("    (0 puede ser normal: el dedup no repite ofertas ya guardadas)")

print(f"\n{'=' * 66}\n")
