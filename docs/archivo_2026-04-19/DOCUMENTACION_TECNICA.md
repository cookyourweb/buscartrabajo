# Documentación Técnica — Sistema Automatizado de Búsqueda de Empleo

**Versión:** 1.0  
**Fecha:** 14 de Abril 2026  
**Estado:** En Producción (N8N + CV Server)  
**Autor:** CookYourWebAI

---

## 📋 Índice

1. [Resumen Ejecutivo](#1-resumen-ejecutivo)
2. [Arquitectura del Sistema](#2-arquitectura-del-sistema)
3. [Componentes](#3-componentes)
4. [Flujos de Trabajo](#4-flujos-de-trabajo)
5. [Configuración y Despliegue](#5-configuración-y-despliegue)
6. [Solución de Problemas](#6-solución-de-problemas)
7. [Próximos Desarrollos](#7-próximos-desarrollos)

---

## 1. Resumen Ejecutivo

Sistema automatizado que:
1. **Genera ofertas de trabajo** diariamente con Claude API
2. **Las guarda en Notion** como CRM
3. **Notifica por email** con botones Aprobar/Descartar
4. **Al aprobar:** Genera carta de presentación + CV adaptado y lo sube a Google Drive

### Stack Tecnológico

| Componente | Tecnología | Proveedor | Estado |
|------------|-----------|-----------|--------|
| Orquestador | N8N v2.15.1 | Render.com (Free) | ⚠️ Configuración pendiente |
| CV Server | Python + FastAPI | Railway.app | ✅ Producción |
| IA | Claude API (Anthropic) | Anthropic | ✅ Producción |
| CRM | Notion API | Notion | ✅ Producción |
| Email | Brevo API | Brevo | ✅ Producción |
| Almacenamiento | Google Drive API | Google | ✅ Producción |

---

## 2. Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ARQUITECTURA GENERAL                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │
│  │   N8N        │    │   CV Server  │    │   Notion     │              │
│  │  (Render)    │◄──►│  (Railway)   │◄──►│   Database   │              │
│  │              │    │              │    │              │              │
│  │  - Workflow  │    │  - Flask API │    │  - Ofertas   │              │
│  │  - Webhooks  │    │  - Claude    │    │  - Estados   │              │
│  │  - Schedule  │    │  - Drive     │    │  - Links CV  │              │
│  └──────┬───────┘    └──────┬───────┘    └──────────────┘              │
│         │                   │                                          │
│         │                   │                                          │
│         ▼                   ▼                                          │
│  ┌──────────────┐    ┌──────────────┐                                  │
│  │   Brevo      │    │   Google     │                                  │
│  │   (Email)    │    │   Drive      │                                  │
│  │              │    │              │                                  │
│  │  - Notifs    │    │  - CVs       │                                  │
│  │  - Cartas    │    │  - Carpetas  │                                  │
│  └──────────────┘    └──────────────┘                                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### URLs de Producción

| Servicio | URL | Propósito |
|----------|-----|-----------|
| **N8N** | `https://n8n-qwmu.onrender.com` | Orquestador principal |
| **CV Server** | `https://cv-server-production.up.railway.app` | Generación de CVs |
| **Webhook Aprobar** | `https://n8n-qwmu.onrender.com/webhook/aprobar` | Acción Aprobar |
| **Webhook Descartar** | `https://n8n-qwmu.onrender.com/webhook/descartar` | Acción Descartar |

---

## 3. Componentes

### 3.1 N8N Workflow (`BuscarTrabajo-FIXED.json`)

**Ubicación:** `/Users/vero/Desktop/buscartrabajo/BuscarTrabajo-FIXED.json`

#### Nodos del Workflow

| ID | Nombre | Tipo | Función |
|----|--------|------|---------|
| 1 | `Schedule Trigger` | Schedule | Ejecuta daily a las 9:00 |
| 2 | `HTTP Request` | HTTP | Claude API - Genera 5 ofertas |
| 3 | `Code in JavaScript` | Code | Normaliza modalidad |
| 4 | `Create a database page1` | Notion | Crea oferta en Notion |
| 5 | `HTTP Request5` | Code | Prepara email con botones |
| 6 | `Brevo Notificacion` | HTTP | Envía email notificación |
| 7 | `WebhookAprovado` | Webhook | GET `/aprobar` |
| 8 | `HTTP Request1` | HTTP | PATCH Notion (Estado: Enviado) |
| 9 | `HTTP Request4` | HTTP | GET Notion (datos completos) |
| 10 | `HTTP Request3` | HTTP | Claude API - Genera carta |
| 11 | `Code in JavaScript1` | Code | Prepara HTML carta |
| 12 | `HTTP Request7` | HTTP | Brevo - Envía carta |
| 13 | **`CV Server`** | **HTTP** | **POST `/generar-cv`** ⚠️ **PENDIENTE** |
| 14 | `WebhookDescartado` | Webhook | GET `/descartar` |
| 15 | `HTTP Request2` | HTTP | PATCH Notion (Estado: Descartado) |

#### Variables del Workflow

```json
{
  "notion_database_id": "33d11515-f4b2-81ef-a776-d0ea698b748f",
  "notion_token": "Bearer ntn_G464872773099dpLY7OzD7I4ZeZee38rKHsoVlmCV2z7A0",
  "claude_api_key": "sk-ant-api03-...",
  "brevo_api_key": "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",
  "webhook_base_url": "https://n8n-qwmu.onrender.com/webhook"
}
```

---

### 3.2 CV Server (`cv_server_v2.py`)

**Ubicación:** `/Users/vero/Desktop/buscartrabajo/cv_server_v2.py`  
**Deployment:** Railway.app

#### Endpoint

```
POST /generar-cv
Content-Type: application/json

Body:
{
  "empresa": "Nombre de la Empresa",
  "puesto": "Senior Frontend Developer",
  "descripcion": "Descripción de la oferta..."
}

Response:
{
  "success": true,
  "link": "https://drive.google.com/file/d/xxx/view",
  "carpeta": "2026-04-14_Empresa_Puesto",
  "archivo": "CV_Veronica_Empresa.docx"
}
```

#### Configuración Required

```env
# Variables de entorno en Railway
DIR_BASE=/app
TOKEN_PATH=/app/token.pickle
CREDS_PATH=/app/credentials.json
FOLDER_GENERADOS=1tHuVOIz3ratjRp8AmHsF0kGVpmy9DocY
FOLDER_CV=1duJA_G3lLbOqiUYoSJcsXAvbtJUdcmzR
CLAUDE_API_KEY=sk-ant-api03-...
```

---

### 3.3 CV Master (`CV_Master_Veronica.txt`)

**Ubicación:** `/Users/vero/Desktop/buscartrabajo/CV_Master_Veronica.txt`  
**Ubicación Drive:** `Drive/cv/CV_Master_Veronica.txt`

Contiene toda la información profesional:
- 15-20+ años de experiencia
- Skills: React, TypeScript, Vue.js, Next.js, Python, IA, N8N
- Experiencia: CookYourWebAI, Bitcode/Ayvens, Mutualidad
- Proyectos: tuvueltaalsol.es, wunjocreations.es

---

### 3.4 Notion Database

**Database ID:** `33d11515-f4b2-81ef-a776-d0ea698b748f`

#### Schema

| Columna | Tipo | Propósito |
|---------|------|-----------|
| `Empresa` | Title | Nombre de la empresa |
| `Puesto` | Rich Text | Título del puesto |
| `Estado` | Select | `Pendiente` → `Enviado` → `Descartado` |
| `Salario` | Rich Text | Rango salarial |
| `Modalidad` | Select | `Remoto` / `Hibrido` / `Presencial` |
| `Link oferta` | URL | Enlace a la oferta original |
| `Notas` | Rich Text | Descripción de la oferta |
| `Link CV Drive` | URL | **PENDIENTE** - Link al CV generado |

---

## 4. Flujos de Trabajo

### 4.1 Flujo Principal (Diario 9:00)

```
1. Schedule Trigger (9:00 AM Europe/Madrid)
   ↓
2. Claude API → Genera 5 ofertas en JSON
   ↓
3. Code Node → Normaliza modalidad (Remoto/Hibrido/Presencial)
   ↓
4. Notion → Crea página en database (Estado: Pendiente)
   ↓
5. Code Node → Prepara email con botones Aprobar/Descartar
   ↓
6. Brevo → Envía email a hello.cookyourweb@gmail.com
```

### 4.2 Flujo Aprobar

```
1. Usuario click en ✅ Aprobar del email
   ↓
2. Webhook GET /aprobar?id={notion_page_id}
   ↓
3. Notion PATCH → Estado: Enviado
   ↓
4. Notion GET → Obtiene datos completos de la oferta
   ↓
5. Claude API → Genera carta de presentación
   ↓
6. Code Node → Prepara HTML de la carta
   ↓
7. Brevo → Envía email con la carta
   ↓
8. [PENDIENTE] CV Server → Genera CV adaptado
   ↓
9. [PENDIENTE] Brevo → Envía email con link al CV
```

### 4.3 Flujo Descartar

```
1. Usuario click en ❌ Descartar del email
   ↓
2. Webhook GET /descartar?id={notion_page_id}
   ↓
3. Notion PATCH → Estado: Descartado
   ↓
4. FIN
```

---

## 5. Configuración y Despliegue

### 5.1 N8N en Render

#### Environment Variables (Render Dashboard → Environment)

**Grupo: Database** (ya configurado)
```
DB_TYPE = postgresdb
DB_POSTGRESDB_HOST = dpg-d7e7n9beo5us7383beo0-a
DB_POSTGRESDB_DATABASE = n8n_db_wz1y
DB_POSTGRESDB_USER = n8n_db_wz1y_user
DB_POSTGRESDB_PASSWORD = Nn2yTCNjpcBOhygNfNmsqok3B2h8KU2U
DB_POSTGRESDB_PORT = 5432
```

**Grupo: N8N Configuration** (AÑADIR)
```
N8N_BASIC_AUTH_ACTIVE = true
N8N_BASIC_AUTH_USER = admin
N8N_BASIC_AUTH_PASSWORD = <tu-contraseña>
N8N_HOST = n8n-qwmu.onrender.com
N8N_PROTOCOL = https
N8N_PORT = 5678
N8N_USER_FOLDER = /tmp/.n8n
GENERIC_TIMEZONE = Europe/Madrid
WEBHOOK_URL = https://n8n-qwmu.onrender.com/
```

**Variables a ELIMINAR:**
```
❌ RAILWAY_RUN_COMMAND
```

#### Cómo Hacer Redeploy en Render

1. **Ve al Dashboard:** https://dashboard.render.com
2. **Selecciona tu servicio:** `n8n-qwmu`
3. **Click en la pestaña "Manual"** (en el menú lateral)
4. **Click en "Deploy Latest Commit"**
5. **Espera 2-3 minutos** hasta que el estado sea "Live"

![Render Redeploy](https://docs.render.com/images/deploy-button.png)

#### Cómo Activar el Workflow

1. **Accede:** https://n8n-qwmu.onrender.com
2. **Login:** `admin` / `<tu-contraseña>`
3. **Workflows → "BuscarTrabajo-Completo"**
4. **Click en toggle "Active"** (esquina superior derecha)
5. **Debe verse VERDE**
6. **Guarda:** `Ctrl+S` o `File → Save`

---

### 5.2 CV Server en Railway

#### Environment Variables (Railway Dashboard)

```
DIR_BASE=/app
TOKEN_PATH=/app/token.pickle
CREDS_PATH=/app/credentials.json
FOLDER_GENERADOS=1tHuVOIz3ratjRp8AmHsF0kGVpmy9DocY
FOLDER_CV=1duJA_G3lLbOqiUYoSJcsXAvbtJUdcmzR
CLAUDE_API_KEY=sk-ant-api03-...
PORT=5000
```

#### Cómo Hacer Redeploy en Railway

1. **Ve al Dashboard:** https://railway.app
2. **Selecciona tu proyecto:** `cv-server`
3. **Click en "Deployments"** (menú lateral)
4. **Click en "Redeploy"** en el último deployment
5. **O: Push a GitHub** → Deploy automático

---

### 5.3 Credenciales Requeridas

| Servicio | Archivo | Ubicación | Estado |
|----------|---------|-----------|--------|
| Google OAuth | `credentials.json` | `/app/` en Railway | ✅ |
| Google Token | `token.pickle` | `/app/` en Railway | ✅ |
| Notion Token | `ntn_...` | N8N workflow | ✅ |
| Claude API | `sk-ant-...` | N8N workflow + CV Server | ✅ |
| Brevo API | `xkeysib-...` | N8N workflow | ✅ |

---

## 6. Solución de Problemas

### 6.1 Webhook Devuelve 404

**Síntoma:**
```json
{
  "code": 404,
  "message": "The requested webhook \"GET aprobar\" is not registered."
}
```

**Causas posibles:**

| Causa | Solución |
|-------|----------|
| Workflow no está Active | Activar toggle en N8N UI |
| N8N se reinició y perdió auth | Revisar variables de entorno en Render |
| URL incorrecta | Verificar WEBHOOK_URL en env vars |

**Debug:**
```bash
# Test directo al webhook
curl -v "https://n8n-qwmu.onrender.com/webhook/aprobar?id=test-123"

# Ver logs de N8N
# Render Dashboard → Logs
```

---

### 6.2 N8N Pide Login Cada Vez

**Causa:** Variables de autenticación no persisten o no están configuradas.

**Solución:**
1. Verificar que `N8N_BASIC_AUTH_*` existen en Render Environment
2. Verificar que los valores son fijos (no cambian entre deploys)
3. Redeploy después de añadir variables

---

### 6.3 CV Server No Responde

**Debug:**
```bash
# Test del endpoint
curl -X POST https://cv-server-production.up.railway.app/generar-cv \
  -H "Content-Type: application/json" \
  -d '{"empresa":"Test","puesto":"Test","descripcion":"Test"}'

# Ver logs en Railway
# Railway Dashboard → Project → Deployments → View Logs
```

---

### 6.4 Email No Llega

**Causas posibles:**
- Brevo API key inválida
- Dominio no verificado en Brevo
- Email en spam

**Debug:**
1. Verificar API key en workflow N8N
2. Verificar dominio autenticado en Brevo Dashboard
3. Revisar spam folder

---

## 7. Próximos Desarrollos

### 7.1 Añadir Nodo CV Server en N8N (PRIORIDAD ALTA)

**Descripción:** Completar el flujo de aprobación generando el CV adaptado.

**Nodos a añadir:**

```json
{
  "name": "CV Server - Generar CV",
  "parameters": {
    "method": "POST",
    "url": "https://cv-server-production.up.railway.app/generar-cv",
    "sendBody": true,
    "specifyBody": "json",
    "jsonBody": "={
      \"empresa\": \"{{ $('HTTP Request4').first().json.properties.Empresa.title[0].text.content }}\",
      \"puesto\": \"{{ $('HTTP Request4').first().json.properties.Puesto.rich_text[0].text.content }}\",
      \"descripcion\": \"{{ $('HTTP Request4').first().json.properties.Notas.rich_text[0].text.content }}\"
    }"
  },
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4.2
}
```

**Conexión:**
```
HTTP Request3 (Claude carta) → CV Server → Code Node (preparar email CV) → Brevo
```

---

### 7.2 Añadir Campo "Link CV Drive" en Notion

**Descripción:** Guardar el link del CV generado en la database.

**Schema update:**
```
Notion DB → Añadir columna: "Link CV Drive" (URL)
```

**Workflow update:**
```
CV Server → Notion PATCH → Añadir link_cv_drive
```

---

### 7.3 Migrar N8N a Railway (Recomendado)

**Motivo:** Render Free duerme tras 15 min, webhooks no fiables.

**Pasos:**
1. Crear nuevo servicio en Railway
2. Usar imagen: `n8nio/n8n:latest`
3. Conectar a PostgreSQL existente
4. Copiar variables de entorno
5. Importar workflow `BuscarTrabajo-FIXED.json`
6. Actualizar URLs en emails Brevo

---

### 7.4 Conectar Indeed API Real

**Motivo:** Ahora genera ofertas ficticias con Claude.

**Alternativas:**
- Indeed API (oficial)
- LinkedIn scraping (con precaución)
- InfoJobs API (España)

---

## 📎 Apéndices

### A. Comandos Útiles

```bash
# Test webhook aprobar
curl "https://n8n-qwmu.onrender.com/webhook/aprobar?id=test-123"

# Test CV Server
curl -X POST https://cv-server-production.up.railway.app/generar-cv \
  -H "Content-Type: application/json" \
  -d '{"empresa":"Google","puesto":"Senior Frontend","descripcion":"..."}'

# Ver logs N8N (local)
docker logs n8n-n8n-1

# Activar entorno Python
cd /Users/vero/Desktop/buscartrabajo
source venv/bin/activate
```

### B. Archivos Importantes

| Archivo | Propósito |
|---------|-----------|
| `BuscarTrabajo-FIXED.json` | Workflow N8N exportado |
| `cv_server_v2.py` | Servidor CV |
| `CV_Master_Veronica.txt` | CV base para adaptación |
| `credentials.json` | Google OAuth (en Railway) |
| `token.pickle` | Google auth token (en Railway) |

### C. Contactos y Recursos

| Recurso | URL |
|---------|-----|
| N8N Docs | https://docs.n8n.io |
| Render Docs | https://docs.render.com |
| Railway Docs | https://docs.railway.app |
| Brevo Docs | https://developers.brevo.com |
| Notion API | https://developers.notion.com |

---

**Última actualización:** 14 de Abril 2026  
**Mantenimiento:** CookYourWebAI
