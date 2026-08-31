# 📘 DOCUMENTACIÓN TÉCNICA — BuscarTrabajo v2

**Versión:** 2.0 Multi-User (arquitectura modular)
**Fecha:** Abril 2026
**Stack:** Flask (Render) · n8n (Render) · Notion · Brevo · Claude API · Google Drive

---

## 🎯 ¿Qué es BuscarTrabajo v2?

Sistema automatizado multi-usuario de búsqueda de empleo. Cualquier persona se registra vía formulario web, el sistema le genera 5 ofertas personalizadas cada mañana usando Claude, le envía email con botones para aprobar/descartar, y al aprobar genera un CV adaptado + carta de presentación y lo envía listo para aplicar.

**Diferencias clave con v1:**
- v1 = solo para Verónica (todo hardcoded)
- v2 = multi-user con formulario de registro + CV dinámico por usuario
- v2 = arquitectura modular con **2 workflows separados** en n8n (no un monolito)

---

## 🏗️ Arquitectura general

```
┌──────────────────────────────────────────────────┐
│  USUARIO                                         │
│  Abre: cv-server-ggd8.onrender.com/registro      │
└──────────────┬───────────────────────────────────┘
               ↓
┌──────────────────────────────────────────────────┐
│  FLASK CV SERVER (Render)                        │
│  - Sirve formulario HTML                         │
│  - POST /registro (detecta nuevo vs existente)   │
│  - Dispara webhooks n8n                          │
│  - POST /generar-cv multi-user                   │
└──────────────┬───────────────────────────────────┘
               ↓
┌──────────────────────────────────────────────────┐
│  N8N — WORKFLOW 1: USUARIOS                      │
│  (el "portero")                                  │
│  - POST /webhook/<RUTA_OCULTA>                   │
│  - POST /webhook/<RUTA_OCULTA>                    │
│  - Crea/busca en Notion DB Usuarios              │
│  - Dispara HTTP interno al workflow 2            │
└──────────────┬───────────────────────────────────┘
               ↓ POST /webhook/buscar-para-user
┌──────────────────────────────────────────────────┐
│  N8N — WORKFLOW 2: PRINCIPAL                     │
│  (el "motor")                                    │
│  - Schedule 9am (lee todos los users activos)    │
│  - Webhook /buscar-para-user (individual)        │
│  - Merge + Split in Batches (1 user/vez)         │
│  - Claude genera ofertas con PROMPT DINÁMICO     │
│  - Notion crea oferta (con Email usuario)        │
│  - Brevo envía al email del user                 │
│  - Webhooks aprobar/descartar/mandar             │
└──────────────────────────────────────────────────┘
```

---

## 🧩 Por qué 2 workflows separados

**Razones técnicas:**
- **Debug independiente:** si falla el registro, el flujo de ofertas sigue funcionando
- **Historia de ejecuciones limpia:** cada workflow tiene sus propios logs en n8n
- **Deploy independiente:** puedo actualizar el flujo de usuarios sin parar el cron 9am
- **Onboarding más claro:** alguien mirando el workflow principal no ve ruido del "cómo se autenticó el user"

**Cómo se comunican:**
Workflow 1 termina con un nodo HTTP que hace `POST /webhook/buscar-para-user` al Workflow 2. Es el patrón estándar en n8n para workflows modulares (como Airbnb y Shopify usan internamente).

---

## 📋 Workflow 1 — BuscarTrabajo-Usuarios

**Archivo:** `workflow-1-usuarios.json`
**Total nodos:** 11

### Flujo "Nuevo usuario"

```
POST /webhook/<RUTA_OCULTA>
  body: { nombre, email, perfil, rol_objetivo, stack, modalidad, 
          salario_min, ciudad, linkedin, cv_master_url }
    ↓
Code — Extraer nuevo
  (normaliza campos y convierte stack/modalidad a arrays)
    ↓
Notion — Crear usuario
  POST api.notion.com/v1/pages con DB_USUARIOS
    ↓
  ├→ Respond — OK nuevo
  │   { estado: 'creado', mensaje: 'Mañana a las 9:00...' }
  │
  └→ HTTP — Disparar búsqueda (nuevo)
      POST /webhook/buscar-para-user → Workflow 2
      (source: '<RUTA_OCULTA>')
```

### Flujo "Buscar ahora"

```
POST /webhook/<RUTA_OCULTA>
  body: { email, nombre }
    ↓
Code — Extraer email
    ↓
Notion — Buscar usuario
  Query DB Usuarios: filter Email+Activo=true, limit 1
    ↓
Code — Normalizar perfil
  (throw Error si no encuentra)
    ↓
  ├→ Respond — OK buscar
  │   { estado: 'buscando', mensaje: 'Recibirás en minutos...' }
  │
  └→ HTTP — Disparar búsqueda (ahora)
      POST /webhook/buscar-para-user → Workflow 2
      (source: '<RUTA_OCULTA>')
```

---

## ⚙️ Workflow 2 — BuscarTrabajo-v2-Principal

**Archivo:** `workflow-2-principal.json`
**Total nodos:** 38

### Entry points

```
Schedule Trigger (9am)                    Webhook /buscar-para-user
    ↓                                            ↓
Notion — Query usuarios activos         Code — Normalizar (interno)
    ↓                                            ↓
Code — Normalizar users (schedule)          (ya está plano)
    ↓                                            ↓
    └──────────────→ Merge (2 inputs) ←─────────┘
                         ↓
                  Split in Batches (1 user/vez)
                         ↓
             Claude — Generar Ofertas
             (prompt dinámico con user.perfil)
                         ↓
             Code — Normalizar modalidad
                         ↓
             Notion — Crear Oferta
             (con Email usuario = user.email)
                         ↓
             Brevo — Enviar notificación
             (to: user.email, no hardcoded)
```

### Flujo aprobar oferta

```
GET /webhook/<RUTA_OCULTA>?id=PAGE_ID
    ↓
Code — Extraer ID
    ↓
Respond to Webhook Aprobar
    ↓
Notion — Marcar Aprobado → En proceso
    ↓
Notion — Obtener Datos Oferta
  (incluye Email usuario)
    ↓
Claude — Generar Carta
    ↓
CV Server — Generar CV
  POST cv-server-ggd8.onrender.com/generar-cv
  body: { email, empresa, puesto, descripcion }
    ↓
Code — Preparar Email Carta+CV
    ↓
Brevo — Enviar Carta+CV
  (to: email usuario de la oferta)
    ↓
Notion — Guardar Link CV + Email Enviado + contactos
```

### Flujo descartar

```
GET /webhook/<RUTA_OCULTA>?id=PAGE_ID
    ↓
Notion — Marcar Descartado
    ↓
Respond OK
```

### Flujo mandar a empresa

```
GET /webhook/<RUTA_OCULTA>?id=PAGE_ID
    ↓
Code — Extraer ID Mandar
    ├→ Respond (rápido)
    ↓
Notion — Marcar Enviado a empresa + Fecha Envio
    ↓
Notion — Obtener Datos Mandar
    ↓
Code — Preparar Confirmación
    ↓
Brevo — Email Confirmación
```

---

## 🗄️ Modelo de datos Notion

### DB Usuarios — `34811515f4b280f19a42f8da5e91a8fe`

| Columna | Tipo | Obligatorio | Descripción |
|---------|------|:-:|-------------|
| Name | Title | ✅ | Nombre completo |
| Email | Email | ✅ | Único — clave para identificar al user |
| Perfil | Rich Text | ✅ | Descripción libre de lo que busca |
| Activo | Checkbox | ✅ | `true` = recibe búsquedas, `false` = pausado |
| Rol objetivo | Rich Text | - | Ej: "Senior Frontend Dev / Tech Lead" |
| Stack | Multi-select | - | React, TypeScript, Vue.js, AI/ML, etc. |
| Salario min | Number (€) | - | Mínimo aceptable |
| Modalidad | Multi-select | - | Remoto, Híbrido Madrid, Híbrido BCN, Presencial |
| Ciudad | Rich Text | - | Para filtros de híbrido |
| LinkedIn | URL | - | Perfil |
| CV Master URL | URL | - | Link Drive al CV base |

**Auto-sync:** `sync_notion_usuarios.py` añade columnas faltantes sin tocar las existentes.

### DB Ofertas — `33d11515-f4b2-81ef-a776-d0ea698b748f`

| Columna | Tipo | Descripción |
|---------|------|-------------|
| Empresa | Title | Nombre empresa |
| Puesto | Rich Text | Título del puesto |
| Estado | Select | Pendiente → Aprobado → En proceso → Enviado → Descartado → Rechazado |
| Salario | Rich Text | Rango |
| Modalidad | Select | Remoto / Hibrido / Presencial |
| Link oferta | URL | Enlace original |
| Notas | Rich Text | Descripción completa |
| Link CV Drive | URL | Link al CV generado |
| **Email usuario** | Email | 🔑 Asocia oferta con usuario |
| Nombre Contacto | Rich Text | Contacto RRHH |
| Email empresa | Email | sic (minúscula en "empresa") |
| Teléfono Contacto | Phone | con tilde |
| Fecha Publicacion | Date | |
| Fecha Envio Empresa | Date | Cuando se marca "Mandar" |
| Email Enviado | Rich Text | Copia del email enviado |

---

## 🔌 Endpoints del servidor Flask

**URL base:** `https://cv-server-ggd8.onrender.com`

| Método | Ruta | Función |
|:-:|------|---------|
| GET | `/health` | Estado + variables de entorno |
| GET | `/debug` | Diagnóstico: Claude + Drive + Notion DB Usuarios |
| GET | `/test-claude` | Prueba rápida Claude API |
| GET | `/registro` | Sirve HTML del formulario |
| POST | `/registro` | Procesa registro (nuevo vs existente) |
| POST | `/generar-cv` | Genera CV adaptado (requiere `email` en body) |

### POST /registro — registro inicial

```json
{
  "nombre": "Verónica Serna",
  "email": "veronica@example.com",
  "perfil": "Busco rol de Tech Lead...",
  "rol_objetivo": "Senior Frontend / Tech Lead",
  "ciudad": "Madrid",
  "modalidad": ["Remoto", "Híbrido Madrid"],
  "stack": ["React", "TypeScript", "AI/ML"],
  "salario_min": 65000,
  "linkedin": "https://linkedin.com/in/...",
  "cv_master_url": "https://drive.google.com/file/d/..."
}
```

Respuestas:
- `{"estado": "existente", "nombre": "..."}` → el front muestra pantalla 2
- `{"estado": "creado", "email": "..."}` → el front muestra pantalla 3

### POST /registro — acción user existente

```json
{"email": "...", "nombre": "...", "accion": "ahora"}  // o "manana"
```

### POST /generar-cv

```json
{
  "email": "veronica@example.com",
  "empresa": "ACME",
  "puesto": "Tech Lead",
  "descripcion": "React + TypeScript + IA..."
}
```

Respuesta:
```json
{
  "success": true,
  "link": "https://drive.google.com/...",
  "archivo": "CV_Veronica_ACME.docx",
  "usuario": "Verónica Serna",
  "email": "veronica@example.com",
  "carpeta_usuario": "veronica-example-com"
}
```

---

## 🌐 Webhooks n8n

**Base:** `https://n8n-qwmu.onrender.com`

### Externos (llamados por Flask o email)

| Método | Path | Workflow | Disparado por |
|:-:|------|----------|---------------|
| POST | `/webhook/<RUTA_OCULTA>` | Workflow 1 | Flask al detectar email nuevo |
| POST | `/webhook/<RUTA_OCULTA>` | Workflow 1 | Flask al pulsar "Buscar ahora" |
| GET | `/webhook/<RUTA_OCULTA>?id=` | Workflow 2 | Click ✅ en email |
| GET | `/webhook/<RUTA_OCULTA>?id=` | Workflow 2 | Click ❌ en email |
| GET | `/webhook/<RUTA_OCULTA>?id=` | Workflow 2 | Click "Mandar" |

### Interno (workflow-to-workflow)

| Método | Path | De | A |
|:-:|------|-----|-----|
| POST | `/webhook/buscar-para-user` | Workflow 1 | Workflow 2 |

Body del webhook interno:
```json
{
  "nombre": "...",
  "email": "...",
  "perfil": "...",
  "rol": "...",
  "stack": ["..."],
  "salario": 65000,
  "modalidad": ["..."],
  "ciudad": "...",
  "linkedin": "...",
  "cv_master_url": "...",
  "source": "<RUTA_OCULTA>" | "<RUTA_OCULTA>"
}
```

---

## 🤖 Agentes de IA

### Agente revisor de CV (integrado, NO separado)

**Ubicación:** DENTRO del prompt de `generar_cv_adaptado()` en Flask.

**Por qué integrado:** ahorra una llamada extra a Claude. El análisis se hace internamente ("silent") y el output ya es el CV mejorado.

```
STEP 1 — ANÁLISIS (silencioso, no se output):
  - Skills relevantes del CV
  - Keywords del offer a usar
  - Gaps detectados (no inventar lo que no existe)
  - Match score 1-10

STEP 2 — OUTPUT: genera el CV adaptado usando el análisis
```

**Beneficio:** Una llamada en vez de dos. 50% del coste.

### Agente preparador de entrevistas (pendiente)

Se activará cuando se detecte respuesta positiva de la empresa (monitor de email, fase futura).
Ver `ROADMAP.md` para detalle.

---

## 🔧 Variables de entorno

### CV Server (Flask en Render)

| Variable | Valor |
|----------|-------|
| `CLAUDE_API_KEY` | `sk-ant-api03-...` (tu clave) |
| `GOOGLE_CREDENTIALS` | Base64 del service-account JSON |
| `NOTION_TOKEN` | `ntn_...` (tu clave) |
| `NOTION_DB_USUARIOS` | `34811515f4b280f19a42f8da5e91a8fe` |
| `FOLDER_GENERADOS` | ID Drive carpeta output CVs |
| `FOLDER_CV_MASTERS` | ID Drive carpeta CV masters |
| `N8N_WEBHOOK_NUEVO` | `https://n8n-qwmu.onrender.com/webhook/<RUTA_OCULTA>` |
| `N8N_WEBHOOK_BUSCAR` | `https://n8n-qwmu.onrender.com/webhook/<RUTA_OCULTA>` |

---

## 📦 Archivos del proyecto

```
buscartrabajo/
├── README.md
├── DOCUMENTACION_TECNICA_v2.md          ← este archivo
├── CHANGELOG.md
├── DEBUGGING.md
├── CLAUDE.md                            ← contexto para IAs (memoria)
├── ROADMAP.md                           ← fases futuras
├── workflow-1-usuarios.json             ← workflow de registro (11 nodos)
├── workflow-2-principal.json            ← workflow principal (38 nodos)
├── cv-server/
│   ├── cv_server_railway.py             ← Flask multi-user
│   ├── requirements.txt
│   └── Procfile
├── scripts/
│   ├── sync_notion_schema.py            ← DB Ofertas
│   └── sync_notion_usuarios.py          ← DB Usuarios
└── skills/
    └── n8n-buscartrabajo.skill
```

---

## 🚀 Checklist de deployment v2

### 1. Notion
- [ ] DB Usuarios existe con ID `34811515f4b280f19a42f8da5e91a8fe`
- [ ] `python3 sync_notion_usuarios.py` para añadir columnas estructuradas
- [ ] DB Ofertas tiene columna `Email usuario` (Email)
- [ ] Al menos un usuario con `Activo=true`

### 2. Drive
- [ ] Carpeta CV_MASTERS existe
- [ ] `CV_Master_{email_slug}.txt` existe dentro
- [ ] Service account con acceso a ambas carpetas

### 3. Flask CV Server (Render)
- [ ] Variables de entorno configuradas
- [ ] Deploy `cv_server_railway.py` v2
- [ ] `curl /health` → todas las vars en verde
- [ ] `curl /debug` → muestra usuarios correctamente
- [ ] `/registro` (GET) muestra formulario
- [ ] `/registro` (POST) con email existente → `estado: existente`

### 4. n8n
- [ ] Importar **primero** `workflow-2-principal.json` y activar
- [ ] Verificar webhook interno:
  ```bash
  curl -X POST https://n8n-qwmu.onrender.com/webhook/buscar-para-user \
    -H "Content-Type: application/json" \
    -d '{"email":"test@test.com","nombre":"Test","perfil":"test"}'
  ```
- [ ] Importar `workflow-1-usuarios.json` y activar
- [ ] Los 5 webhooks externos respondiendo (<RUTA_OCULTA>, <RUTA_OCULTA>, aprobar, descartar, mandar)

### 5. Tests end-to-end
- [ ] Registro con email nuevo → email mañana a las 9
- [ ] Usuario existente + "Buscar ahora" → email en minutos
- [ ] Aprobar oferta → CV y carta con datos del usuario correcto
- [ ] Mandar a empresa → confirmación al usuario correcto

---

## 🐛 Troubleshooting v2

### El email llega a la cuenta equivocada
**Causa:** algún nodo Brevo sigue con `hello.cookyourweb@gmail.com` hardcoded.
**Fix:** buscar `hello.cookyourweb` en el JSON del workflow, cambiar a `$('Split in Batches').item.json.email`.

### CV generado tiene datos de Verónica (no del user)
**Causa:** el body de `/generar-cv` no incluye `email`.
**Fix:** en el nodo `CV Server - Generar CV`, el body JSON debe leer el email del `Notion - Obtener Datos Oferta`.

### "Usuario no encontrado en Notion DB Usuarios"
- El email no existe en DB Usuarios, o
- El user tiene `Activo=false`

Comprobar con `curl /debug` — lista todos los usuarios visibles.

### "No se encontró CV Master"
El Flask busca en este orden:
1. URL directo del campo `CV Master URL` en Notion
2. `CV_Master_{email_slug}.txt` en Drive
3. `{email_slug}.txt` en Drive
4. `CV_Master_{Nombre_con_guiones}.txt` en Drive
5. Fallback legacy: `CV_Master_Veronica.txt` (solo si email = `hello.cookyourweb@gmail.com`)

### Webhook interno /buscar-para-user da 404
**Causa:** el Workflow 2 no está activo, o se importó después del Workflow 1.
**Fix:** importar y activar primero el Workflow 2, luego el Workflow 1.

### "Claude API error 400 - Your credit balance is too low"
Recargar en `console.anthropic.com/settings/billing`.

### n8n duerme (Render Free)
Tras 15 min sin actividad, la primera request del día tarda 30-60s (cold start). Aceptable para búsquedas diarias. Upgrade a Starter ($7/mes) si se necesita respuesta inmediata siempre.

---

## 💡 Próximas fases (ver ROADMAP.md)

En orden de prioridad:

1. **Ofertas REALES con web_search** — hoy Claude las inventa. Añadir `tools: [{"type": "web_search_20250305"}]` al nodo Claude del Workflow 2
2. **Follow-ups automáticos** — tras 7/14 días sin respuesta, sugerir mensaje
3. **Monitor de email** — polling Gmail para detectar respuestas de empresas
4. **Agente preparador de entrevistas** — research + preguntas + simulación
5. **Dashboard web** opcional (Notion visible ya cumple para beta)

---

**Autoría:** Verónica Serna / CookYourWebAI
**Mantenimiento:** Verónica + Claude (sesiones iterativas)
