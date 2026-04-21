# Sistema Automatizado de Búsqueda de Empleo v2

## Descripción

Sistema **multi-usuario** automatizado de búsqueda de empleo. Cualquier persona se registra vía formulario web y cada mañana recibe 5 ofertas personalizadas + CVs adaptados + cartas listas para enviar.

**v2 vs v1:**
- v1 = solo para Verónica (todo hardcoded)
- v2 = multi-user con formulario de registro + CV dinámico por usuario
- v2 = arquitectura modular con **2 workflows separados** en n8n

## Arquitectura v2 — 2 Workflows Separados

```
┌──────────────────────────────────────────────────┐
│  USUARIO                                         │
│  Abre: cv-server-ggd8.onrender.com/registro      │
└──────────────┬───────────────────────────────────┘
               ↓
┌──────────────────────────────────────────────────┐
│  FLASK CV SERVER (Render)                        │
│  - Sirve formulario HTML                         │
│  - POST /registro (nuevo vs existente)           │
│  - POST /generar-cv multi-user                   │
└──────────────┬───────────────────────────────────┘
               ↓
┌──────────────────────────────────────────────────┐
│  N8N — WORKFLOW 1: USUARIOS (11 nodos)           │
│  - POST /webhook/nuevo-usuario                   │
│  - POST /webhook/buscar-ahora                    │
│  - Crea/busca en Notion DB Usuarios              │
│  - Dispara HTTP interno al workflow 2            │
└──────────────┬───────────────────────────────────┘
               ↓ POST /webhook/buscar-para-user
┌──────────────────────────────────────────────────┐
│  N8N — WORKFLOW 2: PRINCIPAL (38 nodos)          │
│  - Schedule 9am (lee todos los users activos)    │
│  - Webhook /buscar-para-user (individual)        │
│  - Claude genera ofertas con PROMPT DINÁMICO     │
│  - Notion crea oferta + Brevo envía email        │
│  - Webhooks aprobar/descartar/mandar             │
└──────────────────────────────────────────────────┘
```

## Servicios Conectados

| Servicio | Estado | URL | Propósito |
|----------|--------|-----|-----------|
| Claude API | ✅ | api.anthropic.com | Generar ofertas, cartas, CV |
| Notion | ✅ | api.notion.com | CRM Usuarios + Ofertas |
| Google Drive | ✅ | drive.google.com | Almacenar CVs |
| Brevo | ✅ | api.brevo.com | Enviar emails |
| CV Server | ✅ | cv-server-ggd8.onrender.com | Generar CVs multi-user |
| N8N | ⚠️ | n8n-qwmu.onrender.com | Orquestador (Render Free) |

## Endpoints CV Server

| Método | Ruta | Función |
|--------|------|---------|
| GET | `/health` | Estado + variables de entorno |
| GET | `/debug` | Diagnóstico: Claude + Drive + Notion |
| GET | `/registro` | Formulario de registro |
| POST | `/registro` | Procesa registro (nuevo/existente) |
| POST | `/generar-cv` | Genera CV adaptado (requiere `email`) |

## Webhooks n8n

| Método | Path | Workflow |
|--------|------|----------|
| POST | `/webhook/nuevo-usuario` | Workflow 1 |
| POST | `/webhook/buscar-ahora` | Workflow 1 |
| POST | `/webhook/buscar-para-user` | Interno (1 → 2) |
| GET | `/webhook/oferta-aprobar?id=` | Workflow 2 |
| GET | `/webhook/oferta-descartar?id=` | Workflow 2 |
| GET | `/webhook/oferta-mandar-empresa?id=` | Workflow 2 |

## Base de Datos Notion

### DB Usuarios — `34811515f4b280f19a42f8da5e91a8fe`

| Columna | Tipo |
|---------|------|
| Name | Title |
| Email | Email (único) |
| Perfil | Rich Text |
| Activo | Checkbox |
| Rol objetivo | Rich Text |
| Stack | Multi-select |
| Salario min | Number |
| Modalidad | Multi-select |
| Ciudad | Rich Text |
| LinkedIn | URL |
| CV Master URL | URL |

### DB Ofertas — `33d11515-f4b2-81ef-a776-d0ea698b748f`

| Columna | Tipo |
|---------|------|
| Empresa | Title |
| Puesto | Rich Text |
| Estado | Select |
| Email usuario | Email (asocia al user) |
| Link CV Drive | URL |

## Debugging

```bash
# 1. ¿Servidor vivo?
curl https://cv-server-ggd8.onrender.com/health

# 2. Diagnóstico total
curl https://cv-server-ggd8.onrender.com/debug

# 3. ¿Webhook interno responde?
curl -X POST https://n8n-qwmu.onrender.com/webhook/buscar-para-user \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","nombre":"Test","perfil":"test"}'
```

## Documentación

- [`DOCUMENTACION_TECNICA_v2.md`](DOCUMENTACION_TECNICA_v2.md) - Arquitectura completa
- [`CLAUDE.md`](CLAUDE.md) - Memoria del proyecto para IAs

---

**Última actualización:** 21 Abril 2026  
**Estado:** ✅ v2 Multi-User en producción
