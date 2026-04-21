# Actualizar Documentación v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Actualizar README.md y CLAUDE.md con la arquitectura v2 multi-user y 2 workflows separados desde la carpeta `actualizarconesto`.

**Architecture:** Reemplazar documentación desactualizada (v1 monolito, Railway muerto) con v2 modular (Render, 2 workflows, multi-user).

**Tech Stack:** Flask (Render), n8n (Render), Notion, Brevo, Claude API, Google Drive

---

### Task 1: Actualizar README.md con arquitectura v2

**Files:**
- Modify: `/Users/vero/Desktop/buscartrabajo/README.md`

- [ ] **Step 1: Reemplazar contenido README.md**

El README actual está desactualizado (menciona Railway muerto, arquitectura monolito). Reemplazar con:

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: actualizar README con arquitectura v2 multi-user"
```

---

### Task 2: Verificar si DOCUMENTACION_TECNICA_v2.md existe en raíz

**Files:**
- Check: `/Users/vero/Desktop/buscartrabajo/DOCUMENTACION_TECNICA_v2.md`
- Create: `/Users/vero/Desktop/buscartrabajo/DOCUMENTACION_TECNICA_v2.md` (si no existe)

- [ ] **Step 1: Comprobar existencia**

El archivo `DOCUMENTACION_TECNICA_v2.md` existe en `actualizarconesto/` pero hay que verificar si ya existe en la raíz del proyecto.

- [ ] **Step 2: Copiar si no existe**

Si no existe en raíz, copiar desde `actualizarconesto/DOCUMENTACION_TECNICA_v2.md`.

- [ ] **Step 3: Commit**

```bash
git add DOCUMENTACION_TECNICA_v2.md
git commit -m "docs: añadir DOCUMENTACION_TECNICA_v2.md con arquitectura completa"
```

---

### Task 3: Actualizar CLAUDE.md si hay cambios

**Files:**
- Modify: `/Users/vero/Desktop/buscartrabajo/CLAUDE.md`

- [ ] **Step 1: Comparar CLAUDE.md actual con actualizarconesto/CLAUDE.md**

Verificar diferencias entre ambos archivos.

- [ ] **Step 2: Aplicar cambios si los hay**

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: actualizar CLAUDE.md con información v2"
```

---

### Task 4: Limpieza opcional de carpeta actualizarconesto

**Files:**
- Directory: `/Users/vero/Desktop/buscartrabajo/actualizarconesto`

- [ ] **Step 1: Preguntar al usuario**

Una vez completados los tasks 1-3, preguntar si quiere:
- Eliminar carpeta `actualizarconesto` (ya está todo copiado)
- Mantener como backup temporal

---

## Self-Review Checklist

- [ ] README.md actualizado con URLs correctas (Render, no Railway)
- [ ] README.md muestra arquitectura v2 con 2 workflows
- [ ] DOCUMENTACION_TECNICA_v2.md en raíz del proyecto
- [ ] CLAUDE.md verificado/actualizado
- [ ] Commits atómicos por cambio
- [ ] No quedan referencias a `cv-server-production.up.railway.app`
