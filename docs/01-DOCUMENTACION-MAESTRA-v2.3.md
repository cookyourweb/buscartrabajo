# 📋 BuscarTrabajo v2.3 — Documentación maestra

> ⚠️ **DOC PARCIALMENTE SUPERADA (jun 2026).** El sistema ya está en **v3 (ofertas reales, multi-usuario)**.
> La **fuente de verdad operativa** (arquitectura, instancia n8n, schema Notion, webhooks, flujos) es **[`../README.md`](../README.md)**.
> Lo que cambió respecto a este documento:
> - Instancia n8n viva: **`n8n-asistente-correo.onrender.com`** (NO `n8n-st1v` / `n8n-qwmu`).
> - Workflow vigente: **`WF2-integrado-v3`** (NO `WF2-BuscarTrabajo-v2-Groq`).
> - Ofertas **reales** (Remotive + Adzuna + Tecnoempleo) con anti-spam, NO inventadas.
> - LLM de ofertas/cartas: **Groq** (`llama-3.3-70b-versatile`), NO Claude.
> - Schema Ofertas: la carta va en **`Carta Enviada`** (no "Carta generada"); el email del user en **`Email Enviado`** (no "Email usuario"); campos nuevos `CV usado` (=CV master), `Link CV Drive` (=CV adaptado), `Fecha envio`, `Fecha Envio Empresa`, `Seguimiento`, `Usuario` (relation).
> - Envío a empresa **híbrido con edición previa** (revisar carta/CV antes de mandar).
>
> Las secciones de **lecciones aprendidas, modelo de costes y gotchas** de abajo siguen siendo válidas.

**Última actualización (doc original):** 28 abril 2026
**Estado real:** ✅ v3 multi-usuario con ofertas reales (ver README)

---

## 🎯 Resumen ejecutivo

Sistema multi-usuario de búsqueda de empleo que:

1. Registra usuarios vía formulario web (`/`)
2. Detecta si el email ya existe (no duplica)
3. Si es nuevo: pide datos completos
4. Si existe: ofrece "Buscar ahora" o "Programar 9am"
5. Genera 1-5 ofertas (actualmente inventadas por Groq)
6. Las envía por email con botones Aprobar / Descartar
7. Si Aprobar → genera carta + CV adaptado al puesto → email al usuario
8. Si Mandar a empresa → envía candidatura

**Coste actual:** ~$0.02/usuario/mes (prácticamente gratis con Groq Free)

---

## 🏗️ Arquitectura actual

```
┌──────────────────────────────────────────────────────────┐
│ USUARIO                                                  │
│ → cv-server-ggd8.onrender.com/                           │
└──────────────┬───────────────────────────────────────────┘
               ↓
┌──────────────────────────────────────────────────────────┐
│ FLASK CV SERVER (Render Free)                            │
│                                                          │
│ Endpoints:                                               │
│  GET  /              → Formulario 5 pantallas            │
│  GET  /health        → Status del servidor               │
│  GET  /debug         → Test del LLM activo               │
│  GET  /usuarios      → Lista usuarios Notion             │
│  POST /check-email   → ¿Existe el email?                 │
│  POST /accion-existente → Buscar ahora / Mañana 9am      │
│  POST /registro      → Crea usuario nuevo + dispara WF1  │
│  POST /generar-cv    → Genera CV adaptado y sube a Drive │
│                                                          │
│ Capa LLM (orden de fallback):                            │
│  1. Groq (llama-3.3-70b-versatile)  ← primario           │
│  2. Gemini 1.5 flash                                     │
│  3. Claude 3 haiku                                       │
└──────────────┬───────────────────────────────────────────┘
               ↓
┌──────────────────────────────────────────────────────────┐
│ N8N-ST1V (Render Free) — workflows orquestadores         │
│                                                          │
│ WF1 BuscarTrabajo-Usuarios (10 nodos):                   │
│  Webhook /nuevo-usuario  → Code → Respond + HTTP→WF2     │
│  Webhook /buscar-ahora   → Notion query → Code → HTTP→WF2│
│                                                          │
│ WF2 BuscarTrabajo-v2-Groq (39 nodos):                    │
│  Trigger:                                                │
│   - Schedule (9am UTC)                                   │
│   - Webhook /buscar-para-user (interno desde WF1)        │
│   - Webhooks /oferta-aprobar /oferta-descartar           │
│              /oferta-mandar-empresa (botones email)      │
│                                                          │
│  Flujo búsqueda:                                         │
│   → Wait 30s → Groq genera 1 oferta                      │
│   → Code Normalizar Modalidad                            │
│   → Notion crear Oferta                                  │
│   → Brevo email con botones                              │
│                                                          │
│  Flujo aprobar:                                          │
│   → Notion Marcar Aprobado → En Proceso                  │
│   → Notion Obtener Datos                                 │
│   → Groq Generar Carta                                   │
│   → Wait 30s → CV Server /generar-cv                     │
│   → Brevo Enviar Carta+CV                                │
│   → Notion Guardar Link CV                               │
└──────────────────────────────────────────────────────────┘
```

---

## 🔌 Configuración

### Variables de entorno Render (cv-server)

| Variable | Valor / Descripción |
|----------|--------------------|
| `GROQ_API_KEY` | Key Groq (obligatoria) |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` |
| `GEMINI_API_KEY` | Fallback opcional |
| `GEMINI_MODEL` | `gemini-1.5-flash` |
| `CLAUDE_API_KEY` | Fallback opcional |
| `CLAUDE_MODEL` | `claude-3-haiku-20240307` |
| `GOOGLE_CLIENT_ID` | OAuth Drive |
| `GOOGLE_CLIENT_SECRET` | OAuth Drive |
| `GOOGLE_REFRESH_TOKEN` | OAuth Drive |
| `FOLDER_CV_MASTERS` | `1duJA_G3lLbOqiUYoSJcsXAvbtJUdcmzR` |
| `NOTION_TOKEN` | Token integración Notion |
| `NOTION_DB_USUARIOS` | `34811515f4b280f19a42f8da5e91a8fe` |
| `WEBHOOK_NUEVO_USUARIO` | `https://n8n-st1v.onrender.com/webhook/nuevo-usuario` |
| `WEBHOOK_BUSCAR_AHORA` | `https://n8n-st1v.onrender.com/webhook/buscar-ahora` |

### Notion DBs

**DB Usuarios** (`34811515f4b280f19a42f8da5e91a8fe`)

| Propiedad | Tipo |
|-----------|------|
| Name | Title |
| Email | Email |
| Perfil | Rich text |
| Rol objetivo | Rich text |
| Stack | Multi-select |
| Salario min | Number |
| Modalidad | Multi-select |
| Ciudad | Rich text |
| LinkedIn | URL |
| CV Master URL | URL |
| Activo | Checkbox |

**DB Ofertas** (`33d11515f4b281efa776d0ea698b748f`)

| Propiedad | Tipo | Notas |
|-----------|------|-------|
| Empresa | Title | |
| Puesto | Rich text | |
| Salario | Rich text | |
| Modalidad | Select | |
| Link oferta | URL | |
| Notas | Rich text | descripción corta |
| Estado | Select | Pendiente / Aprobado / Descartado / En proceso / Enviado |
| Email usuario | Email | usuario destinatario |
| Nombre Contacto | Rich text | RRHH oferta |
| Email empresa | Email | (minúscula) |
| Teléfono Contacto | Rich text | (con tilde) |
| Fecha Publicacion | Date | |
| **Email Enviado** | Rich text | tracking — usar valor "pendiente" inicial |
| Link CV Drive | URL | rellenado tras Aprobar |
| Carta generada | Rich text | rellenado tras Aprobar |

### Credenciales n8n (en n8n-st1v)

- `Notion account` — token integración Notion
- `Brevo` (o `Sendinblue`) — API key activa `n8napikey`

⚠️ **OJO al importar workflows:** los IDs de credencial NO se transfieren entre instancias. Hay que reasignar credencial nodo por nodo tras cada import.

---

## 🚨 Lecciones aprendidas (sesiones 22-28 abril)

### 1. Render Free duerme
- Servidores web, n8n y CV Server tardan 30-60s en despertar
- Webhook con timeout 5s falla la primera vez
- Soluciones:
  - Aumentar timeout del cliente a 30s
  - Reintento automático
  - O pasar a Render Pro ($7/mes)

### 2. Rate limits LLM
- **Gemini Free:** 10 req/min, 1500/día → ajustado pero suficiente
- **Groq Free:** 30 req/min, 14400/día → mucho mejor para producción
- **Claude:** ~$15/usuario/mes → caro para validar

### 3. Importar workflows rompe credenciales
- Al importar JSON desde otra instancia, los IDs de credencial NO se mapean
- Hay que entrar a CADA nodo y reasignar credencial manualmente
- Síntoma típico: `Credential with ID "xxx" does not exist`

### 4. Brevo Free
- 300 emails/día gratis
- Free no permite enviar a emails arbitrarios sin verificación
- Plan Lite ($9/mes) = 20.000/mes y permite cualquier destinatario
- Sender debe estar validado en Brevo Senders & IPs

### 5. n8n peculiaridades
- `Respond to Webhook` debe estar al FINAL del flujo, no en medio
- `responseMode: "responseNode"` en el Webhook trigger
- Si hay 2 workflows con mismo path → uno se desactiva al activar el otro
- Webhooks producción se ven SOLO en Executions, no en canvas

### 6. Notion gotchas
- Schemas son sensibles: `Teléfono Contacto` (con tilde), `Email empresa` (minúscula)
- Si una propiedad existe en DB y NO se manda en payload → no falla
- Si una propiedad se manda con tipo equivocado → 400 "expected to be X"
- Property names en n8n son case-sensitive

### 7. 2 instancias n8n duplicadas
- Sesión empezó con `n8n-qwmu` (vieja, vacía)
- Trabajo se hizo en `n8n-st1v` (nueva, activa)
- Env vars del CV Server apuntaban a la vieja → ningún workflow se disparaba
- Lección: documentar QUÉ instancia usar y mantener UNA sola activa

---

## 📊 Modelo de costes actual

Con Groq Free + Render Free:

| Escenario | Coste/mes |
|-----------|----------:|
| 1 usuario, 1 oferta/día | **$0.00** |
| 10 beta testers | **$0.00** |
| 100 usuarios activos | **$0.00** (cabe en Groq Free) |
| 500+ usuarios | $7-15 (Render Pro + plan Brevo Lite) |

---

## 🔐 Pendientes de seguridad

1. **Rotar API keys expuestas en chats:**
   - Notion token (`ntn_G46487...`)
   - Brevo (`xkeysib-2e087...`)
   - Groq (`gsk_Nr7Pm...`)
   - Gemini (`AIzaSyDrSFZqms...`)
2. **Repo `cv-server` → privado** en GitHub
3. **Suspender `n8n-qwmu`** si no se usa
4. **Limpiar usuarios y ofertas de prueba** en Notion

---

## 🛠️ Debugging rápido

```bash
# 1. ¿CV Server vivo y bien configurado?
curl https://cv-server-ggd8.onrender.com/health

# 2. ¿LLM responde?
curl https://cv-server-ggd8.onrender.com/debug

# 3. ¿Webhook nuevo-usuario funciona?
curl -X POST https://n8n-st1v.onrender.com/webhook/nuevo-usuario \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Test","email":"test@test.com"}'

# 4. ¿Webhook buscar-ahora funciona?
curl -X POST https://n8n-st1v.onrender.com/webhook/buscar-ahora \
  -H "Content-Type: application/json" \
  -d '{"email":"hello.cookyourweb@gmail.com","nombre":"vero"}'

# 5. ¿Webhook interno buscar-para-user funciona?
curl -X POST https://n8n-st1v.onrender.com/webhook/buscar-para-user \
  -H "Content-Type: application/json" \
  -d '{"nombre":"vero","email":"...","perfil":"...","rol":"...","stack":["React"],"salario":50000,"modalidad":["Remoto"],"ciudad":"Madrid","source":"test"}'
```

Si todos responden 200/OK → problema está en flujo interno (revisar Executions en n8n).
