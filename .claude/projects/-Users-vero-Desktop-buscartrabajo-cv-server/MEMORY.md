# Memoria del Proyecto - BuscarTrabajo v2

## Estado Actual (21 Abril 2026)

### Arquitectura v2 - Multi-User
- **2 Workflows separados en n8n:**
  - Workflow 1: `workflow-1-usuarios.json` (11 nodos) - Registro de usuarios
  - Workflow 2: `workflow-2-principal.json` (38 nodos) - Búsqueda diaria + CV + Emails

### CV Server
- **Archivo:** `cv-server/cv_server_railway.py`
- **URL Producción:** `https://cv-server-ggd8.onrender.com`
- **Multi-user:** Lee CV Master según email del usuario desde Notion DB Usuarios

### URLs Importantes
| Servicio | URL |
|----------|-----|
| N8N | `https://n8n-qwmu.onrender.com` |
| CV Server | `https://cv-server-ggd8.onrender.com` |
| Registro | `https://cv-server-ggd8.onrender.com/registro` |
| Health | `https://cv-server-ggd8.onrender.com/health` |
| Debug | `https://cv-server-ggd8.onrender.com/debug` |

### Webhooks n8n
| Webhook | URL |
|---------|-----|
| Nuevo Usuario | `/webhook/nuevo-usuario` |
| Buscar Ahora | `/webhook/buscar-ahora` |
| Buscar Para User (interno) | `/webhook/buscar-para-user` |
| Aprobar | `/webhook/oferta-aprobar?id=PAGE_ID` |
| Descartar | `/webhook/oferta-descartar?id=PAGE_ID` |
| Mandar Empresa | `/webhook/oferta-mandar-empresa?id=PAGE_ID` |

### Bases de Datos Notion
- **DB Usuarios:** `34811515f4b280f19a42f8da5e91a8fe`
- **DB Ofertas:** `33d11515-f4b2-81ef-a776-d0ea698b748f`

### Emails del Sistema
1. 🤖 Nueva oferta (9:00 AM) - 5 ofertas personalizadas con botones ✅/❌
2. 📝 Carta + CV - Al aprobar oferta
3. ✅ Confirmación - Al mandar a empresa

### Stack
- **Orquestador:** n8n en Render
- **CV Server:** Flask en Render
- **DB:** Notion (2 databases)
- **Email:** Brevo (`usecookyourwebai.es`)
- **Storage:** Google Drive
- **LLM:** Claude API (`claude-sonnet-4-6`)

### Documentación
- `CLAUDE.md` - Memoria completa del proyecto
- `DOCUMENTACION_TECNICA_v2.md` - Arquitectura detallada
- `README.md` - Vista general

---

## 🚀 INICIO DE SESIÓN — Checklist para Agentes

### 1. Leer siempre al empezar:
```bash
# 1. Memoria del proyecto (este archivo)
cat .claude/projects/-Users-vero-Desktop-buscartrabajo-cv-server/MEMORY.md

# 2. Documentación completa
cat CLAUDE.md

# 3. Estado git
git status
git log --oneline -5
```

### 2. Verificar servicios antes de tocar código:
```bash
# CV Server vivo
curl https://cv-server-ggd8.onrender.com/health

# Diagnóstico completo
curl https://cv-server-ggd8.onrender.com/debug

# n8n vivo (webhook interno)
curl -X POST https://n8n-qwmu.onrender.com/webhook/buscar-para-user \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","nombre":"Test","perfil":"test"}'
```

### 3. Reglas NO NEGOCIABLES (nunca violar):
1. **Modelo Claude:** SIEMPRE `claude-sonnet-4-6` (nunca con fecha/snapshot)
2. **URL CV Server:** SIEMPRE `cv-server-ggd8.onrender.com` (Railway muerto)
3. **Multi-tenant:** `/generar-cv` requiere `email` en body
4. **Schema Notion:** Respeta acentos/mayúsculas (`Teléfono Contacto`, `Email empresa`)
5. **Emails dinámicos:** Nunca hardcodear `hello.cookyourweb@gmail.com` en nodos Brevo
6. **2 workflows separados:** NO fusionar — comunicación vía `/webhook/buscar-para-user`
7. **Orden importación n8n:** Primero Workflow 2 (principal), luego Workflow 1 (usuarios)

### 4. Variables de entorno requeridas (CV Server):
```bash
# En Render
CLAUDE_API_KEY=sk-ant-api03-...
GOOGLE_CREDENTIALS=<base64 service account>
NOTION_TOKEN=ntn_...
NOTION_DB_USUARIOS=34811515f4b280f19a42f8da5e91a8fe
FOLDER_GENERADOS=1tHuVOIz3ratjRp8AmHsF0kGVpmy9DocY
FOLDER_CV_MASTERS=1duJA_G3lLbOqiUYoSJcsXAvbtJUdcmzR
N8N_WEBHOOK_NUEVO=https://n8n-qwmu.onrender.com/webhook/nuevo-usuario
N8N_WEBHOOK_BUSCAR=https://n8n-qwmu.onrender.com/webhook/buscar-ahora
```

### 5. Scripts locales (usan env vars o piden keys):
```bash
# sync_notion_schema.py — usa NOTION_TOKEN de env var o pide
python3 sync_notion_schema.py

# add_notion_fields.py — pide API key
python3 add_notion_fields.py
```

### 6. Repositorios GitHub:
- **Principal:** https://github.com/cookyourweb/buscartrabajo
- **CV Server:** https://github.com/cookyourweb/cv-server (subir solo cambios críticos)

### 7. Debugging rápido:
```bash
# Ver logs CV Server (Render)
https://dashboard.render.com → cv-server → Logs

# Ver ejecuciones n8n
https://n8n-qwmu.onrender.com → Executions

# Ver DB Usuarios Notion
curl -X POST https://api.notion.com/v1/databases/34811515f4b280f19a42f8da5e91a8fe/query \
  -H "Authorization: Bearer $NOTION_TOKEN" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{"page_size": 5}'
```

### 8. Créditos Anthropic:
Si ves `"credit balance too low"`:
- Ir a `console.anthropic.com/settings/billing`
- Añadir créditos (mínimo $5, recomendado $20)

---

## 📁 Estructura del Proyecto

```
buscartrabajo/
├── CLAUDE.md                        ← Memoria completa (leer primero)
├── README.md                        ← Vista general
├── DOCUMENTACION_TECNICA_v2.md      ← Arquitectura detallada
├── DOCUMENTACION_WORKFLOW.md        ← Docs del workflow n8n
├── .claude/
│   └── projects/
│       └── -Users-vero-Desktop-buscartrabajo-cv-server/
│           └── MEMORY.md            ← Este archivo (inicio de sesión)
├── docs/
│   ├── .archivo-historico-2026-04-19/  ← Docs antiguas v1 (NO USAR)
│   ├── CAMBIOS_WORKFLOW_2026_04_20.md
│   └── WORKFLOW_CAMBIOS_RECIENTES.md
├── cv-server/                       ← Repo separado
│   ├── cv_server_railway.py         ← Flask multi-user
│   ├── get_token.py                 ← Local (NO subir)
│   ├── requirements.txt
│   └── Procfile
├── add_notion_fields.py             ← Script añadir campos Notion
├── sync_notion_schema.py            ← Sync schema Notion
└── workflows/                       ← JSONs exportados de n8n
```

---

## ⚠️ Bugs Conocidos (NO repetir)

| Bug | Causa | Prevención |
|-----|-------|------------|
| "No JSON found" | Claude sin créditos | Error handling explícito |
| "Empresa undefined" | `{{ .empresa }}` sin `$json.` | Usar `{{ $json.empresa }}` |
| Bad request Notion | `bodyParameters` con `name: "="` | Usar `specifyBody: "json"` |
| Webhook colgado | Faltaba conexión al Respond | Conectar explícitamente |
| Emails a Verónica | `hello.cookyourweb@gmail.com` hardcoded | Usar `user.email` |
| Model string inventado | Fecha `20260217` no existía | Usar alias sin fecha |

---

## 📞 Datos de Verónica (referencia)

- **Nombre:** Verónica Serna Pérez
- **Rol:** Senior Frontend Developer
- **Ubicación:** Madrid
- **Email:** verserper@gmail.com
- **LinkedIn:** linkedin.com/in/veronica4web
- **Email remitente sistema:** veronica@usecookyourwebai.es

---

**Última actualización:** 21 Abril 2026  
**Estado:** ✅ v2 Multi-User en producción
