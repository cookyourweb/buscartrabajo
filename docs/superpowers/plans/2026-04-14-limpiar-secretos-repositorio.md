# Limpiar Secretos del Repositorio - Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminar todos los secretos del repositorio, regenerar API keys, y crear una versión limpia del código usando variables de entorno.

**Architecture:** Refactorizar el servidor Python para usar `os.environ`, crear templates de workflows n8n con placeholders, y preparar documentación para configuración de variables en Railway/Render.

**Tech Stack:** Python, n8n Workflows JSON, Environment Variables, Railway/Render

---

## File Structure Changes

| File | Action | Purpose |
|------|--------|---------|
| `cv_server_v2.py` | Modify | Leer secretos desde variables de entorno |
| `generar_cv_master.py` | Modify | Leer secretos desde variables de entorno |
| `.env.example` | Create | Template de variables necesarias |
| `workflows/workflow_template.json` | Create | Template de workflow n8n sin secretos |
| `DEPLOYMENT.md` | Create | Guía de configuración en Railway/Render |
| `credentials.json` | Delete | Eliminar archivo con secretos Google |
| `token.pickle` | Delete | Eliminar token de Google |
| `ssh-key-2026-04-11.key` | Delete | Eliminar clave SSH privada |
| `ssh-key-2026-04-11.key.pub` | Delete | Eliminar clave SSH pública |
| `.git` | Delete | Eliminar historial de git con secretos |

---

## Task 1: Crear .env.example con Placeholders

**Files:**
- Create: `.env.example`

- [ ] **Step 1: Crear archivo .env.example**

```bash
cat > .env.example << 'EOF'
# ==========================================
# CONFIGURACIÓN DE API KEYS - BuscarTrabajo
# ==========================================
# Copiar este archivo a .env y rellenar con tus valores reales
# NUNCA subir .env a git (ya está en .gitignore)

# --- Anthropic Claude API ---
# Obtener en: https://console.anthropic.com/
CLAUDE_API_KEY=sk-ant-api03-TU_CLAVE_AQUI

# --- Notion API ---
# Obtener en: https://www.notion.so/my-integrations
NOTION_TOKEN=ntn_TU_TOKEN_AQUI
NOTION_DATABASE_ID=33d11515-f4b2-81ef-a776-d0ea698b748f

# --- Brevo API (Sendinblue) ---
# Obtener en: https://app.brevo.com/settings/keys/api
BREVO_API_KEY=xkeysib-TU_CLAVE_AQUI

# --- Google Drive API ---
# El token.pickle se genera automáticamente en el primer run
# Las credenciales se configuran en Railway como variables de entorno
GOOGLE_CLIENT_ID=TU_CLIENT_ID.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=TU_CLIENT_SECRET

# --- Configuración de Carpetas Drive ---
FOLDER_GENERADOS=1tHuVOIz3ratjRp8AmHsF0kGVpmy9DocY
FOLDER_CV=1duJA_G3lLbOqiUYoSJcsXAvbtJUdcmzR
FOLDER_EJEMPLOS=162O7HV2Y4tvNjuHOYiAOWVngCTLqj4yQ

# --- Configuración del Servidor ---
PORT=8080
DIR_BASE=/app

# --- Configuración de Email ---
EMAIL_FROM=veronica@usecookyourwebai.es
EMAIL_TO=hello.cookyourweb@gmail.com
EOF
```

- [ ] **Step 2: Verificar contenido**

Run: `cat .env.example | head -20`
Expected: Muestra el encabezado del archivo

- [ ] **Step 3: Commit**

```bash
git add .env.example
git commit -m "docs: add .env.example with required environment variables"
```

---

## Task 2: Refactorizar cv_server_v2.py para Variables de Entorno

**Files:**
- Modify: `cv_server_v2.py:35-48`

- [ ] **Step 1: Reemplazar configuración hardcodeada con os.environ**

```python
# ── CONFIGURACIÓN ─────────────────────────────────────────────────────────────
# Leer desde variables de entorno (Railway/Render) o usar defaults para local
DIR_BASE          = os.environ.get("DIR_BASE", "/Users/vero/Desktop/buscartrabajo")
TOKEN_PATH        = os.environ.get("TOKEN_PATH", os.path.join(DIR_BASE, "token.pickle"))
CREDS_PATH        = os.environ.get("CREDS_PATH", os.path.join(DIR_BASE, "credentials.json"))
FOLDER_GENERADOS  = os.environ.get("FOLDER_GENERADOS", "1tHuVOIz3ratjRp8AmHsF0kGVpmy9DocY")
FOLDER_CV         = os.environ.get("FOLDER_CV", "1duJA_G3lLbOqiUYoSJcsXAvbtJUdcmzR")
CLAUDE_API_KEY    = os.environ.get("CLAUDE_API_KEY", "")
MIME_DOCX         = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

# ── CONFIGURACIÓN NOTION ─────────────────────────────────────────────────────
NOTION_TOKEN      = os.environ.get("NOTION_TOKEN", "")
NOTION_DB_ID      = os.environ.get("NOTION_DATABASE_ID", "33d11515-f4b2-81ef-a776-d0ea698b748f")
NOTION_API_URL    = "https://api.notion.com/v1/pages"

# Validación de variables requeridas
if not CLAUDE_API_KEY:
    print("⚠️  ADVERTENCIA: CLAUDE_API_KEY no está configurada")
if not NOTION_TOKEN:
    print("⚠️  ADVERTENCIA: NOTION_TOKEN no está configurado")
# ──────────────────────────────────────────────────────────────────────────────
```

- [ ] **Step 2: Verificar sintaxis Python**

Run: `python3 -m py_compile cv_server_v2.py`
Expected: Sin errores (no output)

- [ ] **Step 3: Commit**

```bash
git add cv_server_v2.py
git commit -m "refactor: read API keys from environment variables instead of hardcoded"
```

---

## Task 3: Refactorizar generar_cv_master.py para Variables de Entorno

**Files:**
- Modify: `generar_cv_master.py:23-28`

- [ ] **Step 1: Reemplazar configuración hardcodeada**

```python
# ─── CONFIGURACIÓN ───────────────────────────────────────────────────────────
FOLDER_EJEMPLOS = os.environ.get("FOLDER_EJEMPLOS", "162O7HV2Y4tvNjuHOYiAOWVngCTLqj4yQ")
FOLDER_CV       = os.environ.get("FOLDER_CV", "1duJA_G3lLbOqiUYoSJcsXAvbtJUdcmzR")
CLAUDE_API_KEY  = os.environ.get("CLAUDE_API_KEY", "")
TOKEN_PATH      = Path(os.environ.get("TOKEN_PATH", str(Path.home() / "Desktop" / "buscartrabajo" / "token.pickle")))
OUTPUT_PATH     = Path(os.environ.get("OUTPUT_PATH", str(Path.home() / "Desktop" / "buscartrabajo" / "CV_Master_Veronica.txt")))

# Validación
if not CLAUDE_API_KEY:
    raise ValueError("CLAUDE_API_KEY no está configurada. Define la variable de entorno.")
```

- [ ] **Step 2: Añadir import os al principio si no existe**

Verificar que línea 7 (import os) existe, si no:
```python
import os
```

- [ ] **Step 3: Verificar sintaxis**

Run: `python3 -m py_compile generar_cv_master.py`
Expected: Sin errores

- [ ] **Step 4: Commit**

```bash
git add generar_cv_master.py
git commit -m "refactor: read CLAUDE_API_KEY from environment variable"
```

---

## Task 4: Crear Template de Workflow n8n sin Secretos

**Files:**
- Create: `workflows/workflow_template.json`

- [ ] **Step 1: Crear directorio workflows si no existe**

```bash
mkdir -p workflows
```

- [ ] **Step 2: Crear template de workflow con placeholders**

```bash
cat > workflows/workflow_template.json << 'EOF'
{
  "name": "BuscarTrabajo-Template",
  "nodes": [
    {
      "parameters": {},
      "type": "n8n-nodes-base.manualTrigger",
      "typeVersion": 1,
      "position": [0, 0],
      "id": "manual-trigger",
      "name": "When clicking 'Execute workflow'"
    },
    {
      "parameters": {
        "rule": {"interval": [{"triggerAtHour": 9}]}
      },
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1.2,
      "position": [200, 200],
      "id": "schedule-trigger",
      "name": "Schedule Trigger"
    },
    {
      "parameters": {
        "method": "POST",
        "url": "https://api.anthropic.com/v1/messages",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {"name": "x-api-key", "value": "={{ $env.CLAUDE_API_KEY }}"},
            {"name": "anthropic-version", "value": "2023-06-01"},
            {"name": "Content-Type", "value": "application/json"}
          ]
        },
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={\n  \"model\": \"claude-sonnet-4-6\",\n  \"max_tokens\": 2000,\n  \"messages\": [{\n    \"role\": \"user\",\n    \"content\": \"Genera una lista de 5 ofertas de trabajo ficticias pero realistas para una Senior Frontend Developer / Tech Lead con React, TypeScript, Vue.js y experiencia en IA en España. Modalidad remoto o híbrido. Responde SOLO con un array JSON válido, sin texto adicional, con estos campos por oferta: empresa, puesto, salario, modalidad, link, descripcion_corta\"\n  }]\n}"
      },
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [400, 200],
      "id": "claude-request",
      "name": "Claude API Request"
    },
    {
      "parameters": {
        "resource": "databasePage",
        "databaseId": {
          "__rl": true,
          "mode": "id",
          "value": "={{ $env.NOTION_DATABASE_ID }}"
        },
        "title": "={{ $json.empresa }}",
        "propertiesUi": {
          "propertyValues": [
            {"key": "Puesto|rich_text", "textContent": "={{ $json.puesto }}"},
            {"key": "Salario|rich_text", "textContent": "={{ $json.salario }}"},
            {"key": "Modalidad|select", "selectValue": "={{ $json.modalidad }}"},
            {"key": "Empresa|title", "title": "={{ $json.empresa }}"},
            {"key": "Link oferta|url", "urlValue": "={{ $json.link }}"},
            {"key": "Notas|rich_text", "textContent": "={{ $json.descripcion_corta }}"},
            {"key": "Estado|select", "selectValue": "=Pendiente"}
          ]
        }
      },
      "type": "n8n-nodes-base.notion",
      "typeVersion": 2.2,
      "position": [600, 200],
      "id": "notion-create",
      "name": "Create Notion Entry",
      "credentials": {"notionApi": {"id": "notion-credential", "name": "Notion Account"}}
    },
    {
      "parameters": {
        "method": "POST",
        "url": "https://api.brevo.com/v3/smtp/email",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {"name": "api-key", "value": "={{ $env.BREVO_API_KEY }}"},
            {"name": "Content-Type", "value": "application/json"}
          ]
        },
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={\n  \"sender\": {\n    \"name\": \"{{ $env.EMAIL_FROM_NAME }}\",\n    \"email\": \"{{ $env.EMAIL_FROM }}\"\n  },\n  \"to\": [{\n    \"email\": \"{{ $env.EMAIL_TO }}\"\n  }],\n  \"subject\": \"Nueva oferta: {{ $json.empresa }} - {{ $json.puesto }}\",\n  \"htmlContent\": \"<div>Ver template completo en documentación</div>\"\n}"
      },
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [800, 200],
      "id": "brevo-email",
      "name": "Send Brevo Email"
    },
    {
      "parameters": {
        "path": "aprobar",
        "options": {"httpMethod": "GET"}
      },
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 2.1,
      "position": [200, 400],
      "id": "webhook-aprobar",
      "name": "Webhook Aprobar",
      "webhookId": "aprobar-webhook-id"
    },
    {
      "parameters": {
        "path": "descartar",
        "options": {"httpMethod": "GET"}
      },
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 2.1,
      "position": [200, 600],
      "id": "webhook-descartar",
      "name": "Webhook Descartar",
      "webhookId": "descartar-webhook-id"
    },
    {
      "parameters": {
        "method": "PATCH",
        "url": "=https://api.notion.com/v1/pages/{{ $json.query.id }}",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {"name": "Authorization", "value": "=Bearer {{ $env.NOTION_TOKEN }}"},
            {"name": "Notion-Version", "value": "2022-06-28"},
            {"name": "Content-Type", "value": "application/json"}
          ]
        },
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={\n  \"properties\": {\n    \"Estado\": {\"select\": {\"name\": \"Enviado\"}}\n  }\n}"
      },
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [400, 400],
      "id": "notion-aprobar",
      "name": "Update Notion Estado"
    },
    {
      "parameters": {
        "method": "PATCH",
        "url": "=https://api.notion.com/v1/pages/{{ $json.query.id }}",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {"name": "Authorization", "value": "=Bearer {{ $env.NOTION_TOKEN }}"},
            {"name": "Notion-Version", "value": "2022-06-28"},
            {"name": "Content-Type", "value": "application/json"}
          ]
        },
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={\n  \"properties\": {\n    \"Estado\": {\"select\": {\"name\": \"Descartado\"}}\n  }\n}"
      },
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [400, 600],
      "id": "notion-descartar",
      "name": "Update Notion Descartado"
    },
    {
      "parameters": {
        "method": "POST",
        "url": "={{ $env.CV_SERVER_URL }}/generar-cv",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {"name": "Content-Type", "value": "application/json"}
          ]
        },
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={\n  \"empresa\": \"{{ $json.properties.Empresa.title[0].text.content }}\",\n  \"puesto\": \"{{ $json.properties.Puesto.rich_text[0].text.content }}\",\n  \"descripcion\": \"{{ $json.properties.Notas.rich_text[0].text.content }}\"\n}"
      },
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [800, 400],
      "id": "cv-server",
      "name": "CV Server - Generar CV"
    }
  ],
  "connections": {
    "Schedule Trigger": {
      "main": [[{"node": "Claude API Request", "type": "main", "index": 0}]]
    },
    "Claude API Request": {
      "main": [[{"node": "Create Notion Entry", "type": "main", "index": 0}]]
    },
    "Create Notion Entry": {
      "main": [[{"node": "Send Brevo Email", "type": "main", "index": 0}]]
    },
    "Webhook Aprobar": {
      "main": [[{"node": "Update Notion Estado", "type": "main", "index": 0}]]
    },
    "Update Notion Estado": {
      "main": [[{"node": "CV Server - Generar CV", "type": "main", "index": 0}]]
    },
    "Webhook Descartar": {
      "main": [[{"node": "Update Notion Descartado", "type": "main", "index": 0}]]
    }
  },
  "active": false,
  "settings": {"executionOrder": "v1"},
  "tags": []
}
EOF
```

- [ ] **Step 3: Verificar JSON válido**

Run: `python3 -c "import json; json.load(open('workflows/workflow_template.json'))" && echo "JSON válido"`
Expected: "JSON válido"

- [ ] **Step 4: Commit**

```bash
git add workflows/
git commit -m "feat: add workflow template with environment variable placeholders"
```

---

## Task 5: Crear Guía de Deployment

**Files:**
- Create: `DEPLOYMENT.md`

- [ ] **Step 1: Crear archivo DEPLOYMENT.md**

```bash
cat > DEPLOYMENT.md << 'EOF'
# Guía de Despliegue - BuscarTrabajo

## Configuración de Variables de Entorno

Este proyecto usa variables de entorno para todas las API keys y secretos. Nunca hardcodees secretos en el código.

### Variables Requeridas

| Variable | Descripción | Dónde Obtenerla |
|----------|-------------|-----------------|
| `CLAUDE_API_KEY` | API Key de Anthropic Claude | https://console.anthropic.com/ |
| `NOTION_TOKEN` | Token de integración Notion | https://www.notion.so/my-integrations |
| `NOTION_DATABASE_ID` | ID de la base de datos Notion | URL de la database |
| `BREVO_API_KEY` | API Key de Brevo (email) | https://app.brevo.com/settings/keys/api |
| `CV_SERVER_URL` | URL del servidor CV | Railway Dashboard |

### Configuración en Railway (CV Server)

1. Ve a https://railway.app y selecciona tu proyecto
2. Ve a la pestaña **Variables**
3. Añade cada variable:

```
CLAUDE_API_KEY=sk-ant-api03-TU_CLAVE_AQUI
NOTION_TOKEN=ntn_TU_TOKEN_AQUI
NOTION_DATABASE_ID=33d11515-f4b2-81ef-a776-d0ea698b748f
BREVO_API_KEY=xkeysib-TU_CLAVE_AQUI
FOLDER_GENERADOS=1tHuVOIz3ratjRp8AmHsF0kGVpmy9DocY
FOLDER_CV=1duJA_G3lLbOqiUYoSJcsXAvbtJUdcmzR
PORT=8080
DIR_BASE=/app
```

4. Haz clic en **Deploy** para aplicar los cambios

### Configuración en Render (N8N)

1. Ve a https://dashboard.render.com
2. Selecciona tu servicio n8n
3. Ve a **Environment**
4. Añade las variables:

```
CLAUDE_API_KEY=sk-ant-api03-TU_CLAVE_AQUI
NOTION_TOKEN=ntn_TU_TOKEN_AQUI
NOTION_DATABASE_ID=33d11515-f4b2-81ef-a776-d0ea698b748f
BREVO_API_KEY=xkeysib-TU_CLAVE_AQUI
CV_SERVER_URL=https://cv-server-production.up.railway.app
EMAIL_FROM=veronica@usecookyourwebai.es
EMAIL_TO=hello.cookyourweb@gmail.com
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=TU_PASSWORD_SEGURA
```

5. Guarda y haz **Manual Deploy**

### Configuración Local (Desarrollo)

1. Copia `.env.example` a `.env`:

```bash
cp .env.example .env
```

2. Edita `.env` con tus valores reales

3. Carga las variables:

```bash
# En macOS/Linux
export $(cat .env | grep -v '#' | xargs)

# O usa python-dotenv
python3 -c "from dotenv import load_dotenv; load_dotenv()"
```

## Importar Workflow en N8N

1. Accede a tu instancia N8N
2. Ve a **Workflows** → **Import**
3. Selecciona `workflows/workflow_template.json`
4. Configura las credenciales de Notion
5. Activa el workflow

## Verificación Post-Despliegue

### Test del CV Server

```bash
curl -X POST https://cv-server-production.up.railway.app/generar-cv \
  -H "Content-Type: application/json" \
  -d '{"empresa":"Test","puesto":"Test","descripcion":"Test"}'
```

### Test de Webhooks N8N

```bash
# Aprobar
curl "https://n8n-qwmu.onrender.com/webhook/aprobar?id=test-123"

# Descartar
curl "https://n8n-qwmu.onrender.com/webhook/descartar?id=test-123"
```

## Troubleshooting

### "CLAUDE_API_KEY not configured"
Verifica que la variable está definida en Railway/Render.

### "Invalid API key" en Claude
Regenera la API key en https://console.anthropic.com/

### Webhook devuelve 404
Asegúrate de que el workflow está **activado** (toggle verde).

### Email no llega
Verifica que el dominio está verificado en Brevo.
EOF
```

- [ ] **Step 2: Verificar archivo**

Run: `head -20 DEPLOYMENT.md`
Expected: Muestra el encabezado

- [ ] **Step 3: Commit**

```bash
git add DEPLOYMENT.md
git commit -m "docs: add deployment guide with environment variable setup"
```

---

## Task 6: Eliminar Archivos con Secretos

**Files:**
- Delete: `credentials.json`
- Delete: `token.pickle`
- Delete: `ssh-key-2026-04-11.key`
- Delete: `ssh-key-2026-04-11.key.pub`

- [ ] **Step 1: Eliminar archivos con secretos**

```bash
rm -f credentials.json
rm -f token.pickle
rm -f ssh-key-2026-04-11.key
rm -f ssh-key-2026-04-11.key.pub
```

- [ ] **Step 2: Verificar eliminación**

Run: `ls -la credentials.json token.pickle ssh-key-*.key* 2>&1 | head -5`
Expected: "No such file or directory" para todos

- [ ] **Step 3: Commit**

```bash
git add -u
git commit -m "security: remove files containing secrets"
```

---

## Task 7: Eliminar Historial Git Contaminado

**Files:**
- Delete: `.git/`

**IMPORTANTE:** Este paso elimina TODO el historial de git. Asegúrate de haber hecho commit de todos los cambios anteriores.

- [ ] **Step 1: Verificar que todo está commiteado**

Run: `git status`
Expected: "nothing to commit, working tree clean" o solo archivos untracked de venv/

- [ ] **Step 2: Eliminar directorio .git**

```bash
rm -rf .git
```

- [ ] **Step 3: Inicializar nuevo repositorio limpio**

```bash
git init
git add .
git commit -m "initial commit: clean repository without secrets"
```

- [ ] **Step 4: Verificar nuevo repositorio**

Run: `git log --oneline`
Expected: Muestra solo "initial commit: clean repository without secrets"

---

## Task 8: Actualizar DOCUMENTACION_TECNICA.md (Remover Secretos)

**Files:**
- Modify: `DOCUMENTACION_TECNICA.md:110-120`

- [ ] **Step 1: Reemplazar sección de variables sensibles**

Buscar y reemplazar la sección de "Variables del Workflow" (líneas 110-120 aprox) con:

```markdown
#### Variables del Workflow

Las variables se configuran como **Variables de Entorno** en Render/Railway:

```json
{
  "notion_database_id": "{{ $env.NOTION_DATABASE_ID }}",
  "claude_api_key": "{{ $env.CLAUDE_API_KEY }}",
  "brevo_api_key": "{{ $env.BREVO_API_KEY }}",
  "webhook_base_url": "{{ $env.WEBHOOK_URL }}"
}
```

Ver [DEPLOYMENT.md](DEPLOYMENT.md) para instrucciones completas.
```

- [ ] **Step 2: Buscar y eliminar cualquier secreto restante**

Run: `grep -n "sk-ant\|ntn_\|xkeysib" DOCUMENTACION_TECNICA.md || echo "No se encontraron secretos"`
Expected: "No se encontraron secretos"

- [ ] **Step 3: Commit**

```bash
git add DOCUMENTACION_TECNICA.md
git commit -m "docs: remove hardcoded secrets from documentation"
```

---

## Task 9: Verificación Final

- [ ] **Step 1: Buscar secretos en todo el repositorio**

```bash
# Buscar patrones de API keys
grep -r "sk-ant-api03" . --include="*.py" --include="*.json" --include="*.md" 2>/dev/null || echo "✓ No Anthropic keys found"
grep -r "ntn_" . --include="*.py" --include="*.json" --include="*.md" 2>/dev/null | grep -v "node_modules\|venv" || echo "✓ No Notion tokens found"
grep -r "xkeysib" . --include="*.py" --include="*.json" --include="*.md" 2>/dev/null || echo "✓ No Brevo keys found"
```

Expected: Todos los grep deben mostrar "No ... found"

- [ ] **Step 2: Verificar estructura del proyecto**

```bash
ls -la
```

Expected: Ver archivos:
- `.env.example` (template, no tiene secretos reales)
- `cv_server_v2.py` (modificado, usa os.environ)
- `generar_cv_master.py` (modificado, usa os.environ)
- `workflows/workflow_template.json` (creado, con placeholders)
- `DEPLOYMENT.md` (creado, guía de config)
- No existen: `credentials.json`, `token.pickle`, archivos `.key`

- [ ] **Step 3: Verificar .gitignore**

Run: `cat .gitignore | grep -E "credentials|token|\.env|\.key"`

Expected: Muestra líneas que ignoran:
- `credentials.json`
- `token.pickle`
- `.env`
- `*.key`
- `*.key.pub`

- [ ] **Step 4: Commit final de verificación**

```bash
git add -A
git commit -m "chore: final verification - repository is clean of secrets"
```

---

## Post-Implementación: Acciones Requeridas del Usuario

Una vez completado este plan, el usuario DEBE:

1. **Regenerar API keys:**
   - Anthropic Claude: https://console.anthropic.com/
   - Notion: https://www.notion.so/my-integrations
   - Brevo: https://app.brevo.com/settings/keys/api

2. **Configurar variables en Railway:**
   - Subir `credentials.json` (nuevo) a Railway como archivo
   - O configurar `GOOGLE_CLIENT_ID` y `GOOGLE_CLIENT_SECRET`

3. **Configurar variables en Render (N8N):**
   - Añadir todas las variables del `.env.example`

4. **Crear nuevo repositorio en GitHub:**
   - Crear repo nuevo (no reutilizar el antiguo)
   - Push: `git remote add origin <url>` y `git push -u origin main`

5. **Verificar:**
   - Testear endpoints del CV Server
   - Importar workflow template en N8N
   - Ejecutar workflow de prueba

---

## Resumen de Cambios

| Aspecto | Antes | Después |
|---------|-------|---------|
| API Keys | Hardcodeadas en Python y JSON | Variables de entorno (`os.environ`) |
| Workflows | JSON con secretos incrustados | Templates con `{{ $env.VAR }}` |
| Documentación | Secretos expuestos | Placeholders + guía de config |
| Git History | Contiene secretos | Limpio, solo commits sin secretos |
| Archivos Sensibles | En repo | Eliminados + ignorados |

---

**Nota para implementador:** Este plan asume que los archivos existen en las rutas indicadas. Si alguna ruta es diferente, ajustar antes de ejecutar.
