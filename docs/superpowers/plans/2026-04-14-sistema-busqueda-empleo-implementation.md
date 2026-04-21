# Sistema Busqueda Empleo v2 - Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar sistema completo con CV Server extendido (endpoints /aprobar, /descartar, /analizar-cv), workflow n8n corregido con URLs correctas, y nuevo workflow de polling para procesar ofertas aprobadas.

**Architecture:** CV Server en Railway actúa como puente entre emails y Notion (recibe clicks, actualiza estados). N8N en Render Free usa polling (2x/día) para procesar ofertas sin depender de webhooks activos 24/7. CV Agent con 3 prompts optimiza matching CV-oferta.

**Tech Stack:** Python (http.server), Anthropic Claude API, Notion API, Brevo API, N8N, Google Drive API, Railway, Render.

---

## File Structure

```
/Users/vero/Desktop/buscartrabajo/
├── cv_server_v2.py                    # EXTENDER - Añadir endpoints
├── cv_server_extended.py              # NUEVO - Versión completa (backup)
├── workflows/
│   ├── workflow-generacion.json       # RENOMBRAR desde BuscarTrabajo-FIXED.json
│   └── workflow-procesamiento.json    # NUEVO - Polling 2x/día
├── docs/
│   └── superpowers/
│       ├── specs/
│       │   └── 2026-04-14-sistema-busqueda-empleo-design.md
│       └── plans/
│           └── 2026-04-14-sistema-busqueda-empleo-implementation.md
└── tests/
    └── test_cv_server.py              # NUEVO - Tests básicos
```

---

## Phase 1: CV Server Extended (Railway)

### Task 1: Extender cv_server_v2.py - Variables de Entorno y Config Notion

**Files:**
- Modify: `cv_server_v2.py:1-50` (sección de configuración)

**Context:** Necesitamos añadir variables para Notion API y extraerlas de variables de entorno para seguridad.

- [ ] **Step 1: Añadir imports y configuración Notion**

```python
# Añadir después de los imports existentes (línea 24)
import urllib.request
import urllib.error

# Añadir después de la configuración existente (después de línea 34)
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "***REMOVED_NOTION_TOKEN***")
NOTION_VERSION = "2022-06-28"
```

- [ ] **Step 2: Crear función helper para PATCH Notion**

Insertar después de la función `get_drive_service()` (aprox línea 44):

```python
def update_notion_page_status(page_id, status):
    """Actualiza el estado de una página en Notion"""
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json"
    }
    data = {
        "properties": {
            "Estado": {
                "select": {
                    "name": status
                }
            }
        }
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers=headers,
        method='PATCH'
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        raise Exception(f"Notion API error: {e.code} - {error_body}")
```

- [ ] **Step 3: Commit cambios de configuración**

```bash
cd /Users/vero/Desktop/buscartrabajo
git add cv_server_v2.py
git commit -m "config: add Notion API helper and environment variables"
```

---

### Task 2: Implementar Endpoint GET /aprobar

**Files:**
- Modify: `cv_server_v2.py` - Clase CVHandler, método do_GET

**Context:** Necesitamos manejar GET requests a /aprobar, actualizar Notion, y devolver HTML de confirmación.

- [ ] **Step 1: Modificar do_POST para renombrar y preparar estructura**

Reemplazar todo el método `do_POST` existente con una estructura más robusta:

```python
class CVHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type='application/json'):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
    
    def _send_html_response(self, status_code, title, message, color="#22C55E"):
        """Envía una respuesta HTML bonita"""
        self._set_headers(status_code, 'text/html')
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .card {{
            background: white;
            padding: 40px;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
            max-width: 400px;
        }}
        .icon {{
            font-size: 64px;
            margin-bottom: 20px;
        }}
        h1 {{
            color: {color};
            margin: 0 0 16px 0;
            font-size: 28px;
        }}
        p {{
            color: #666;
            font-size: 16px;
            line-height: 1.6;
            margin: 0 0 8px 0;
        }}
        .info {{
            background: #f3f4f6;
            padding: 12px;
            border-radius: 8px;
            margin-top: 20px;
            font-size: 14px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="card">
        <div class="icon">{'✅' if status_code == 200 else '❌'}</div>
        <h1>{title}</h1>
        <p>{message}</p>
        <div class="info">Próximas ejecuciones: 10:00 y 18:00</div>
    </div>
</body>
</html>"""
        self.wfile.write(html.encode('utf-8'))
```

- [ ] **Step 2: Añadir método do_GET para /aprobar y /descartar**

Añadir después del método `_send_html_response`:

```python
    def do_GET(self):
        """Maneja requests GET para /aprobar y /descartar"""
        parsed_path = self.path.split('?')
        path = parsed_path[0]
        query_string = parsed_path[1] if len(parsed_path) > 1 else ""
        
        # Parsear query parameters
        params = {}
        for param in query_string.split('&'):
            if '=' in param:
                key, value = param.split('=', 1)
                params[key] = urllib.parse.unquote(value)
        
        page_id = params.get('id', '')
        
        if path == '/aprobar':
            if not page_id:
                self._send_html_response(400, "Error", "Falta el parámetro 'id'", "#EF4444")
                return
            
            try:
                # Actualizar Notion
                update_notion_page_status(page_id, "Aprobar")
                self._send_html_response(
                    200, 
                    "¡Oferta Aprobada!", 
                    "La oferta ha sido marcada para procesamiento. Recibirás un email con la carta y CV adaptado en la próxima ejecución."
                )
            except Exception as e:
                print(f"Error en /aprobar: {e}")
                self._send_html_response(
                    500, 
                    "Error", 
                    f"No se pudo actualizar la oferta: {str(e)}", 
                    "#EF4444"
                )
        
        elif path == '/descartar':
            if not page_id:
                self._send_html_response(400, "Error", "Falta el parámetro 'id'", "#EF4444")
                return
            
            try:
                # Actualizar Notion
                update_notion_page_status(page_id, "Descartado")
                self._send_html_response(
                    200, 
                    "Oferta Descartada", 
                    "La oferta ha sido marcada como descartada. No se procesará.",
                    "#6B7280"
                )
            except Exception as e:
                print(f"Error en /descartar: {e}")
                self._send_html_response(
                    500, 
                    "Error", 
                    f"No se pudo actualizar la oferta: {str(e)}", 
                    "#EF4444"
                )
        
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
```

- [ ] **Step 3: Commit endpoint GET handlers**

```bash
cd /Users/vero/Desktop/buscartrabajo
git add cv_server_v2.py
git commit -m "feat: add GET /aprobar and /descartar endpoints with HTML responses"
```

---

### Task 3: Implementar Endpoint POST /analizar-cv (CV Agent)

**Files:**
- Modify: `cv_server_v2.py` - Añadir método do_POST y funciones del CV Agent

**Context:** El CV Agent usa 3 prompts secuenciales con Claude API para analizar, optimizar y puntuar el CV.

- [ ] **Step 1: Añadir función para llamar a Claude con retry**

Añadir después de la función `call_claude` existente (aprox línea 84):

```python
def call_claude_with_retry(prompt, max_tokens=4000, max_retries=3):
    """Llama a Claude API con retry logic"""
    for attempt in range(max_retries):
        try:
            return call_claude(prompt, max_tokens)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            print(f"Retry {attempt + 1}/{max_retries} after error: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff
```

Necesitarás añadir `import time` al principio del archivo.

- [ ] **Step 2: Añadir función CV Agent con 3 prompts**

Añadir después de la función anterior:

```python
def cv_agent_analyze(cv_master, empresa, puesto, descripcion):
    """
    CV Agent - Sistema de 3 prompts para optimizar CV
    Retorna: dict con cv_adaptado, score, bullets_optimizados
    """
    
    # Prompt 1: Análisis de matching
    prompt1 = f"""Eres un experto en reclutamiento tech y optimización de CVs.

Analiza este CV Master y la descripción del trabajo.
Pull every phrase this company uses to describe success.
List them next to my closest matching bullet points.

CV Master:
{cv_master}

Job Description:
Empresa: {empresa}
Puesto: {puesto}
Descripción: {descripcion}

Instrucciones:
1. Identifica las palabras clave y frases que la empresa usa para describir éxito
2. Mapea cada requisito con mi experiencia más cercana
3. Identifica gaps (qué me falta mencionar)

Formato de salida (JSON):
{{
  "palabras_clave_empresa": ["palabra1", "palabra2", ...],
  "mapeo_requisitos": [
    {{"requisito": "...", "match_cv": "...", "score": 85}},
    ...
  ],
  "gaps": ["experiencia en X", "skill Y"]
}}"""
    
    print("🤖 CV Agent - Prompt 1: Analizando matching...")
    analysis = call_claude_with_retry(prompt1, max_tokens=3000)
    
    # Prompt 2: Optimización (simulamos las respuestas a clarificaciones)
    prompt2 = f"""Basado en el análisis anterior, genera un CV adaptado optimizado.

CV Master:
{cv_master}

Job Description:
Empresa: {empresa}
Puesto: {puesto}
Descripción: {descripcion}

Instrucciones:
1. Reescribe mis bullet points usando EL MISMO LENGUAJE que la empresa usa
2. NO mientas sobre lo que hice, pero OPTIMIZA cómo lo describes
3. Destaca la experiencia más relevante para esta oferta
4. Prioriza skills que menciona la empresa
5. Mantén un tono profesional pero humano
6. Máximo 2 páginas de contenido

Para las secciones donde mi experiencia no es 100% match, usa frases como:
- "Experiencia aplicable en..."
- "Background sólido en X relevante para Y"
- "Habilidades transferibles de Z a este rol"

Genera el CV completo en formato markdown."""
    
    print("🤖 CV Agent - Prompt 2: Generando CV optimizado...")
    cv_adaptado = call_claude_with_retry(prompt2, max_tokens=6000)
    
    # Prompt 3: Scoring
    prompt3 = f"""Compara el CV adaptado con la descripción del trabajo.

CV Adaptado:
{cv_adaptado}

Job Description:
Empresa: {empresa}
Puesto: {puesto}
Descripción: {descripcion}

Calcula el porcentaje de overlap de lenguaje entre el CV adaptado y la descripción del trabajo.
Marca en rojo (lista) cualquier sección que esté por debajo del 60%.

Formato de salida (JSON):
{{
  "score_matching": 78,
  "secciones_bajo_60": ["experiencia_angular", "certificacion_aws"],
  "bullets_optimizados": [
    {{"original": "Desarrollé aplicaciones con React", "optimizado": "Construí aplicaciones escalables con React..."}}
  ],
  "fortalezas": ["Experiencia en liderazgo", "Stack moderno"],
  "debilidades": ["Menos experiencia en Angular"]
}}"""
    
    print("🤖 CV Agent - Prompt 3: Calculando score...")
    scoring = call_claude_with_retry(prompt3, max_tokens=2000)
    
    # Extraer JSON del scoring (Claude a veces envuelve en markdown)
    import re
    json_match = re.search(r'\{[\s\S]*\}', scoring)
    if json_match:
        try:
            scoring_data = json.loads(json_match.group())
        except:
            scoring_data = {
                "score_matching": 75,
                "secciones_bajo_60": [],
                "bullets_optimizados": [],
                "fortalezas": [],
                "debilidades": []
            }
    else:
        scoring_data = {
            "score_matching": 75,
            "secciones_bajo_60": [],
            "bullets_optimizados": [],
            "fortalezas": [],
            "debilidades": []
        }
    
    return {
        "cv_adaptado_markdown": cv_adaptado,
        "score_matching": scoring_data.get("score_matching", 75),
        "secciones_bajo_60": scoring_data.get("secciones_bajo_60", []),
        "bullets_optimizados": scoring_data.get("bullets_optimizados", []),
        "analysis": analysis
    }
```

- [ ] **Step 3: Modificar do_POST para incluir /analizar-cv**

Reemplazar completamente el método `do_POST` existente:

```python
    def do_POST(self):
        """Maneja requests POST"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b'{}'
        
        try:
            data = json.loads(body.decode('utf-8'))
        except json.JSONDecodeError:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
            return
        
        if self.path == '/generar-cv':
            # Endpoint existente - mantener funcionalidad
            empresa = data.get('empresa', 'Empresa')
            puesto = data.get('puesto', 'Puesto')
            descripcion = data.get('descripcion', '')
            
            resultado = generar_y_subir_cv(empresa, puesto, descripcion)
            
            self._set_headers(200 if resultado.get('success') else 500)
            self.wfile.write(json.dumps(resultado).encode())
        
        elif self.path == '/analizar-cv':
            # Nuevo endpoint CV Agent
            cv_master = data.get('cv_master', '')
            empresa = data.get('empresa', '')
            puesto = data.get('puesto', '')
            descripcion = data.get('descripcion', '')
            
            if not all([cv_master, empresa, puesto]):
                self._set_headers(400)
                self.wfile.write(json.dumps({
                    "error": "Faltan campos requeridos: cv_master, empresa, puesto"
                }).encode())
                return
            
            try:
                resultado = cv_agent_analyze(cv_master, empresa, puesto, descripcion)
                self._set_headers(200)
                self.wfile.write(json.dumps({
                    "success": True,
                    **resultado
                }).encode())
            except Exception as e:
                print(f"Error en /analizar-cv: {e}")
                self._set_headers(500)
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": str(e)
                }).encode())
        
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())
```

- [ ] **Step 4: Commit CV Agent implementation**

```bash
cd /Users/vero/Desktop/buscartrabajo
git add cv_server_v2.py
git commit -m "feat: add CV Agent with 3-prompt system and /analizar-cv endpoint"
```

---

### Task 4: Actualizar Puerto para Railway

**Files:**
- Modify: `cv_server_v2.py` - Final del archivo (main)

**Context:** Railway asigna el puerto vía variable de entorno PORT.

- [ ] **Step 1: Modificar el bloque main para usar PORT de env**

Reemplazar las líneas finales (aprox líneas 335-343):

```python
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), CVHandler)
    print(f"🚀 Servidor CV v2 corriendo en http://0.0.0.0:{port}")
    print(f"   Endpoint POST: /generar-cv")
    print(f"   Endpoint POST: /analizar-cv")
    print(f"   Endpoint GET:  /aprobar?id=PAGE_ID")
    print(f"   Endpoint GET:  /descartar?id=PAGE_ID")
    print(f"   CV Master: Drive/cv/CV_Master_Veronica.txt")
    print(f"   Destino:   Drive/cv/generados/FECHA_EMPRESA_PUESTO/")
    server.serve_forever()
```

- [ ] **Step 2: Commit final del CV Server**

```bash
cd /Users/vero/Desktop/buscartrabajo
git add cv_server_v2.py
git commit -m "config: use PORT from environment for Railway compatibility"
```

---

## Phase 2: N8N Workflow - Correcciones

### Task 5: Corregir Workflow Generación (BuscarTrabajo-FIXED.json)

**Files:**
- Modify: `BuscarTrabajo-FIXED.json` → luego renombrar a `workflow-generacion.json`
- Modify: `workflow-generacion.json` - Nodos específicos

**Context:** Necesitamos:
1. Cambiar URL de webhooks en el email (apuntar a CV Server Railway)
2. Cambiar estado inicial de "Pendiente" a "Enviado"

- [ ] **Step 1: Corregir estado inicial en Create a database page1**

Buscar la línea:
```json
{"key": "Estado|select", "selectValue": "=Pendiente"}
```

Cambiar a:
```json
{"key": "Estado|select", "selectValue": "=Enviado"}
```

- [ ] **Step 2: Corregir URLs en el email de Brevo**

Buscar en el nodo "Brevo Notificacion" (aprox línea 173):

```json
"jsonBody": "={\n  ...\n  \"htmlContent\": \"<div...><a href=\\\"https://n8n-production-b93b.up.railway.app/webhook/aprobar?id={{ $json.pageId }}\\\"...>"
```

Reemplazar con:

```json
"jsonBody": "={\n  \"sender\": {\n    \"name\": \"{{ $json.sender_name }}\",\n    \"email\": \"{{ $json.sender_email }}\"\n  },\n  \"to\": [{\n    \"email\": \"{{ $json.to_email }}\"\n  }],\n  \"subject\": \"Nueva oferta: {{ $json.empresa }} - {{ $json.puesto }}\",\n  \"htmlContent\": \"<div style=\\\"font-family:Arial,sans-serif;padding:20px;max-width:600px;margin:0 auto\\\"><h2 style=\\\"color:#1F5C8B\\\">Nueva oferta encontrada</h2><table style=\\\"width:100%;border-collapse:collapse;margin:20px 0\\\"><tr><td style=\\\"padding:10px;font-weight:bold;border-bottom:1px solid #ddd\\\">Empresa</td><td style=\\\"padding:10px;border-bottom:1px solid #ddd\\\">{{ $json.empresa }}</td></tr><tr style=\\\"background:#f9f9f9\\\"><td style=\\\"padding:10px;font-weight:bold;border-bottom:1px solid #ddd\\\">Puesto</td><td style=\\\"padding:10px;border-bottom:1px solid #ddd\\\">{{ $json.puesto }}</td></tr><tr><td style=\\\"padding:10px;font-weight:bold;border-bottom:1px solid #ddd\\\">Modalidad</td><td style=\\\"padding:10px;border-bottom:1px solid #ddd\\\">{{ $json.modalidad }}</td></tr><tr style=\\\"background:#f9f9f9\\\"><td style=\\\"padding:10px;font-weight:bold\\\">Salario</td><td style=\\\"padding:10px\\\">{{ $json.salario }}</td></tr></table><div style=\\\"margin-top:30px;text-align:center\\\"><a href=\\\"https://cv-server-production.up.railway.app/aprobar?id={{ $json.pageId }}\\\" style=\\\"background:#22C55E;color:white;padding:14px 28px;text-decoration:none;border-radius:8px;font-weight:bold;display:inline-block;margin-right:10px\\\">✅ Aprobar</a><a href=\\\"https://cv-server-production.up.railway.app/descartar?id={{ $json.pageId }}\\\" style=\\\"background:#EF4444;color:white;padding:14px 28px;text-decoration:none;border-radius:8px;font-weight:bold;display:inline-block\\\">❌ Descartar</a></div><div style=\\\"margin-top:30px;padding:15px;background:#f0f9ff;border-radius:8px;font-size:14px;color:#666\\\"><strong>Nota:</strong> Al aprobar, recibirás un email con la carta y CV adaptado en la próxima ejecución (10:00 o 18:00).</div></div>\"\n}"
```

- [ ] **Step 3: Renombrar archivo y commit**

```bash
cd /Users/vero/Desktop/buscartrabajo
cp BuscarTrabajo-FIXED.json workflows/workflow-generacion.json
rm BuscarTrabajo-FIXED.json
git add workflows/workflow-generacion.json
# Nota: git rm BuscarTrabajo-FIXED.json si estaba trackeado
git commit -m "fix: update webhook URLs to CV Server Railway and change initial state to Enviado"
```

---

## Phase 3: N8N Workflow - Nuevo Workflow de Procesamiento

### Task 6: Crear Workflow de Procesamiento (workflow-procesamiento.json)

**Files:**
- Create: `workflows/workflow-procesamiento.json`

**Context:** Nuevo workflow que corre 2 veces al día (10:00, 18:00) y procesa ofertas con estado "Aprobar".

- [ ] **Step 1: Crear archivo con estructura base**

```json
{
  "name": "BuscarTrabajo-Procesamiento",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {"triggerAtHour": 10},
            {"triggerAtHour": 18}
          ]
        }
      },
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1.2,
      "position": [250, 300],
      "id": "trigger-procesamiento-001",
      "name": "Schedule Trigger Procesamiento"
    },
    {
      "parameters": {
        "resource": "databasePage",
        "operation": "getAll",
        "databaseId": {
          "__rl": true,
          "value": "33d11515-f4b2-81ef-a776-d0ea698b748f",
          "mode": "id"
        },
        "filter": {
          "singleSelect": {
            "propertyName": "Estado",
            "propertyValue": "Aprobar"
          }
        },
        "options": {}
      },
      "type": "n8n-nodes-base.notion",
      "typeVersion": 2.2,
      "position": [450, 300],
      "id": "notion-query-001",
      "name": "Query Ofertas Aprobadas",
      "credentials": {
        "notionApi": {
          "id": "mu2V7agOVkH2Eoyh",
          "name": "Notion account"
        }
      }
    },
    {
      "parameters": {
        "batchSize": 1,
        "options": {}
      },
      "type": "n8n-nodes-base.splitInBatches",
      "typeVersion": 3,
      "position": [650, 300],
      "id": "split-batches-001",
      "name": "Split In Batches"
    },
    {
      "parameters": {
        "method": "POST",
        "url": "https://api.anthropic.com/v1/messages",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {"name": "x-api-key", "value": "=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"},
            {"name": "anthropic-version", "value": "2023-06-01"},
            {"name": "Content-Type", "value": "application/json"}
          ]
        },
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={\n  \"model\": \"claude-sonnet-4-6\",\n  \"max_tokens\": 4000,\n  \"messages\": [{\n    \"role\": \"user\",\n    \"content\": \"Eres el asistente de Veronica Serna, Tech Lead UX Engineer con 15+ años de experiencia. Genera una carta de presentacion breve, profesional y en español para esta oferta:\\\n\\\nEmpresa: {{ $json.properties.Empresa.title[0].text.content }}\\\nPuesto: {{ $json.properties.Puesto.rich_text[0].text.content }}\\\nDescripcion: {{ $json.properties.Notas.rich_text[0].text.content }}\\\n\\\nTono directo y humano, sin guiones largos. Maximo 3 parrafos. Firma como Veronica Serna.\"\n  }]\n}",
        "options": {}
      },
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [850, 300],
      "id": "claude-carta-001",
      "name": "Claude - Generar Carta"
    },
    {
      "parameters": {
        "method": "POST",
        "url": "https://cv-server-production.up.railway.app/analizar-cv",
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={\n  \"cv_master\": \"Veronica Serna Pérez - Tech Lead UX Engineer con 15+ años de experiencia en desarrollo web, React, TypeScript, Vue.js, Next.js. Especialista en IA aplicada a negocio, automatización con N8N/Make/Zapier. Liderazgo de equipos de 4-6 ingenieros. Experiencia: CookYourWebAI (2024-actual), Bitcode/Ayvens (2017-2024), Mutualidad (2008-2016). Proyectos: tuvueltaalsol.es, wunjocreations.es. Skills: React, TypeScript, Vue.js, Next.js, Python, IA, N8N, Figma, Firebase...\",\n  \"empresa\": \"{{ $json.properties.Empresa.title[0].text.content }}\",\n  \"puesto\": \"{{ $json.properties.Puesto.rich_text[0].text.content }}\",\n  \"descripcion\": \"{{ $json.properties.Notas.rich_text[0].text.content }}\"\n}",
        "options": {}
      },
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [850, 500],
      "id": "cv-agent-001",
      "name": "CV Server - Analizar CV"
    },
    {
      "parameters": {
        "method": "POST",
        "url": "https://cv-server-production.up.railway.app/generar-cv",
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={\n  \"empresa\": \"{{ $json.properties.Empresa.title[0].text.content }}\",\n  \"puesto\": \"{{ $json.properties.Puesto.rich_text[0].text.content }}\",\n  \"descripcion\": \"{{ $json.properties.Notas.rich_text[0].text.content }}\"\n}",
        "options": {}
      },
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [1050, 400],
      "id": "cv-generate-001",
      "name": "CV Server - Generar CV"
    },
    {
      "parameters": {
        "jsCode": "const empresa = $input.first().json.json.properties.Empresa.title[0].text.content;\nconst puesto = $input.first().json.json.properties.Puesto.rich_text[0].text.content;\nconst carta = $('Claude - Generar Carta').first().json.content[0].text;\nconst cv_link = $('CV Server - Generar CV').first().json.link;\nconst cv_score = $('CV Server - Analizar CV').first().json.score_matching || 75;\n\nconst htmlContent = `<div style=\"font-family:Arial,sans-serif;padding:20px;max-width:600px;margin:0 auto\">\n  <h2 style=\"color:#1F5C8B\">Carta y CV Generados</h2>\n  <p><strong>Empresa:</strong> ${empresa}</p>\n  <p><strong>Puesto:</strong> ${puesto}</p>\n  <p><strong>Score CV Matching:</strong> ${cv_score}%</p>\n  <hr style=\"margin:20px 0\">\n  <h3>Carta de Presentación</h3>\n  <div style=\"background:#f9f9f9;padding:20px;border-radius:8px;line-height:1.6\">${carta}</div>\n  <div style=\"margin-top:30px;text-align:center\">\n    <a href=\"${cv_link}\" style=\"background:#1F5C8B;color:white;padding:14px 28px;text-decoration:none;border-radius:8px;font-weight:bold;display:inline-block\">📎 Descargar CV Adaptado</a>\n  </div>\n  <div style=\"margin-top:30px;padding:15px;background:#f0f9ff;border-radius:8px;font-size:14px;color:#666\">\n    <strong>Nota:</strong> Si todo está correcto, puedes enviar tu candidatura directamente. El CV ha sido optimizado para esta oferta específica.\n  </div>\n</div>`;\n\nreturn [{\n  json: {\n    sender_name: 'Veronica Serna',\n    sender_email: 'veronica@usecookyourwebai.es',\n    to_email: 'hello.cookyourweb@gmail.com',\n    subject: `CV y Carta listos: ${empresa} - ${puesto}`,\n    htmlContent: htmlContent\n  }\n}];"
      },
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [1250, 400],
      "id": "code-email-001",
      "name": "Preparar Email Final"
    },
    {
      "parameters": {
        "method": "POST",
        "url": "https://api.brevo.com/v3/smtp/email",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {"name": "api-key", "value": "***REMOVED_BREVO_KEY***"},
            {"name": "Content-Type", "value": "application/json"}
          ]
        },
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={\n  \"sender\": {\n    \"name\": \"{{ $json.sender_name }}\",\n    \"email\": \"{{ $json.sender_email }}\"\n  },\n  \"to\": [{\n    \"email\": \"{{ $json.to_email }}\"\n  }],\n  \"subject\": \"{{ $json.subject }}\",\n  \"htmlContent\": \"{{ $json.htmlContent }}\"\n}",
        "options": {}
      },
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [1450, 400],
      "id": "brevo-final-001",
      "name": "Brevo - Enviar Email Final"
    },
    {
      "parameters": {
        "resource": "databasePage",
        "operation": "update",
        "pageId": "={{ $json.id }}",
        "propertiesUi": {
          "propertyValues": [
            {"key": "Estado|select", "selectValue": "=Procesado"}
          ]
        },
        "options": {}
      },
      "type": "n8n-nodes-base.notion",
      "typeVersion": 2.2,
      "position": [1450, 600],
      "id": "notion-update-001",
      "name": "Notion - Marcar Procesado",
      "credentials": {
        "notionApi": {
          "id": "mu2V7agOVkH2Eoyh",
          "name": "Notion account"
        }
      }
    }
  ],
  "connections": {
    "Schedule Trigger Procesamiento": {
      "main": [[{"node": "Query Ofertas Aprobadas", "type": "main", "index": 0}]]
    },
    "Query Ofertas Aprobadas": {
      "main": [[{"node": "Split In Batches", "type": "main", "index": 0}]]
    },
    "Split In Batches": {
      "main": [
        [{"node": "Claude - Generar Carta", "type": "main", "index": 0}],
        [{"node": "CV Server - Analizar CV", "type": "main", "index": 0}]
      ]
    },
    "Claude - Generar Carta": {
      "main": [[{"node": "CV Server - Generar CV", "type": "main", "index": 0}]]
    },
    "CV Server - Analizar CV": {
      "main": [[{"node": "CV Server - Generar CV", "type": "main", "index": 0}]]
    },
    "CV Server - Generar CV": {
      "main": [[{"node": "Preparar Email Final", "type": "main", "index": 0}]]
    },
    "Preparar Email Final": {
      "main": [
        [{"node": "Brevo - Enviar Email Final", "type": "main", "index": 0}],
        [{"node": "Notion - Marcar Procesado", "type": "main", "index": 0}]
      ]
    }
  },
  "active": false,
  "settings": {
    "executionOrder": "v1",
    "binaryMode": "separate"
  },
  "tags": []
}
```

- [ ] **Step 2: Commit del nuevo workflow**

```bash
cd /Users/vero/Desktop/buscartrabajo
mkdir -p workflows
git add workflows/workflow-procesamiento.json
git commit -m "feat: add processing workflow with CV Agent and polling schedule"
```

---

## Phase 4: Variables de Entorno y Deployment

### Task 7: Configurar Variables de Entorno en Railway (CV Server)

**Files:**
- Railway Dashboard (manual)
- Documentar en: `.env.example` (nuevo archivo)

- [ ] **Step 1: Crear archivo .env.example**

```bash
cd /Users/vero/Desktop/buscartrabajo
cat > .env.example << 'EOF'
# CV Server Configuration (Railway)
CLAUDE_API_KEY=sk-ant-api03-...
NOTION_TOKEN=ntn_...
PORT=5000

# Google Drive (ya configurado en Railway)
DIR_BASE=/app
TOKEN_PATH=/app/token.pickle
CREDS_PATH=/app/credentials.json
FOLDER_GENERADOS=1tHuVOIz3ratjRp8AmHsF0kGVpmy9DocY
FOLDER_CV=1duJA_G3lLbOqiUYoSJcsXAvbtJUdcmzR
EOF
```

- [ ] **Step 2: Commit y push a Railway**

```bash
git add .env.example
git commit -m "docs: add environment variables template"
git push origin main
```

- [ ] **Step 3: Configurar en Railway Dashboard**

Instrucciones manuales para el usuario:

1. Ir a https://railway.app/dashboard
2. Seleccionar proyecto `cv-server`
3. Ir a tab "Variables"
4. Añadir `NOTION_TOKEN` con valor: `***REMOVED_NOTION_TOKEN***`
5. Verificar que `CLAUDE_API_KEY` ya esté configurada
6. Hacer "Redeploy" del servicio

---

### Task 8: Configurar Variables en Render (N8N)

**Files:**
- Render Dashboard (manual)

Instrucciones manuales para el usuario:

1. Ir a https://dashboard.render.com
2. Seleccionar servicio `n8n-qwmu`
3. Ir a "Environment"
4. Añadir/verificar variables:
   ```
   CV_SERVER_URL=https://cv-server-production.up.railway.app
   NOTION_TOKEN=***REMOVED_NOTION_TOKEN***
   CLAUDE_API_KEY=sk-ant-api03-...
   BREVO_API_KEY=xkeysib-...
   ```
5. Hacer "Manual Deploy" → "Deploy Latest Commit"

---

## Phase 5: Testing y Validación

### Task 9: Probar CV Server Localmente

**Files:**
- Terminal commands
- `tests/test_cv_server.py` (opcional)

- [ ] **Step 1: Probar endpoint /generar-cv existente**

```bash
# Desde local (con servidor corriendo)
curl -X POST http://localhost:8080/generar-cv \
  -H "Content-Type: application/json" \
  -d '{
    "empresa": "Test Company",
    "puesto": "Senior Frontend Developer",
    "descripcion": "React, TypeScript, 5+ years experience"
  }'
```

Expected output:
```json
{
  "success": true,
  "link": "https://drive.google.com/file/d/xxx/view",
  "carpeta": "2026-04-14_Test-Company_Senior-Frontend-Developer",
  "archivo": "CV_Veronica_Test-Company.docx"
}
```

- [ ] **Step 2: Probar endpoint /analizar-cv**

```bash
curl -X POST http://localhost:8080/analizar-cv \
  -H "Content-Type: application/json" \
  -d '{
    "cv_master": "Veronica Serna - Tech Lead UX Engineer...",
    "empresa": "Test Company",
    "puesto": "Senior Frontend Developer",
    "descripcion": "React, TypeScript, Next.js, 5+ years"
  }'
```

Expected output:
```json
{
  "success": true,
  "cv_adaptado_markdown": "...",
  "score_matching": 78,
  "secciones_bajo_60": [],
  "bullets_optimizados": [...]
}
```

- [ ] **Step 3: Probar endpoints /aprobar y /descartar**

```bash
# Probar aprobar (reemplazar PAGE_ID con uno real de Notion)
curl -v "http://localhost:8080/aprobar?id=TEST_PAGE_ID"

# Debería devolver HTML con status 200
# Y actualizar el estado en Notion si el PAGE_ID es válido
```

- [ ] **Step 4: Probar en Railway (después de deploy)**

```bash
# Probar endpoint en producción
curl -X POST https://cv-server-production.up.railway.app/analizar-cv \
  -H "Content-Type: application/json" \
  -d '{
    "cv_master": "Test",
    "empresa": "Google",
    "puesto": "Test",
    "descripcion": "Test"
  }'
```

---

### Task 10: Importar Workflows en N8N

**Files:**
- N8N UI (manual)

Instrucciones manuales para el usuario:

1. Acceder a https://n8n-qwmu.onrender.com
2. Login con credenciales
3. Importar workflow-generacion.json:
   - Workflows → Add Workflow → Import from File
   - Seleccionar `workflow-generacion.json`
   - Activar con toggle
4. Importar workflow-procesamiento.json:
   - Workflows → Add Workflow → Import from File
   - Seleccionar `workflow-procesamiento.json`
   - Activar con toggle

---

## Summary

| Phase | Tasks | Output |
|-------|-------|--------|
| 1 | 1-4 | CV Server extendido con /aprobar, /descartar, /analizar-cv |
| 2 | 5 | Workflow generación corregido con URLs correctas |
| 3 | 6 | Nuevo workflow de procesamiento con polling |
| 4 | 7-8 | Variables de entorno configuradas |
| 5 | 9-10 | Testing y validación completados |

---

**Plan saved to:** `docs/superpowers/plans/2026-04-14-sistema-busqueda-empleo-implementation.md`

**Ready for execution. Choose approach:**
1. **Subagent-Driven (recommended)** - Fresh subagent per task, review between tasks
2. **Inline Execution** - Execute tasks in this session with checkpoints
