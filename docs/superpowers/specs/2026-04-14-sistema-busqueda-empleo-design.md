# Especificación Técnica — Sistema Automatizado de Búsqueda de Empleo v2

**Fecha:** 14 de Abril 2026  
**Versión:** 2.0  
**Estado:** Diseño Aprobado  
**Autor:** CookYourWebAI + Usuario

---

## 1. Resumen Ejecutivo

Sistema automatizado para búsqueda de empleo que combina:
- **Generación diaria de ofertas** (Claude API + Notion)
- **Aprobación manual** vía botones en email (apuntan a CV Server en Railway)
- **Procesamiento batch** 2 veces al día (genera carta + CV adaptado)
- **CV Agent** con sistema de 3 prompts para optimizar el matching

---

## 2. Arquitectura del Sistema

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           ARQUITECTURA GENERAL                                │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                 │
│  │    N8N       │◄────┤   CV Server  │◄────┤   Notion     │                 │
│  │  (Render)    │     │  (Railway)   │     │   Database   │                 │
│  │              │     │              │     │              │                 │
│  │  • Schedule  │     │  • /aprobar  │     │  • Ofertas   │                 │
│  │  • Polling   │     │  • /descartar│     │  • Estados   │                 │
│  │  • Workflow  │     │  • /generar-cv     │  • Links     │                 │
│  │  • Batch     │     │  • /analizar-cv    │              │                 │
│  └──────┬───────┘     └──────┬───────┘     └──────────────┘                 │
│         │                    │                                               │
│         │                    │                                               │
│         ▼                    ▼                                               │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                   │
│  │   Claude API │     │   Google     │     │   Brevo      │                   │
│  │   (Anthropic)│     │   Drive      │     │   (Email)    │                   │
│  │              │     │              │     │              │                   │
│  │  • Ofertas   │     │  • CVs       │     │  • Notifs    │                   │
│  │  • Cartas    │     │  • Master    │     │  • Cartas    │                   │
│  │  • CV Agent  │     │              │     │  • CVs       │                   │
│  └──────────────┘     └──────────────┘     └──────────────┘                   │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Flujos de Trabajo

### 3.1 Flujo de Generación (Diario 9:00)

```
Schedule Trigger (9:00 AM Europe/Madrid)
    ↓
HTTP Request: Claude API → Genera 5 ofertas ficticias
    ↓
Code Node: Parsea JSON y normaliza modalidad
    ↓
Notion: Create Database Page (Estado: "Enviado")
    ↓
Set Node: Prepara variables email
    ↓
Brevo: Envía email con botones Aprobar/Descartar
        (links apuntan a CV Server /aprobar y /descartar)
```

### 3.2 Flujo de Aprobación (Instantáneo vía CV Server)

```
Usuario click en "✅ Aprobar" en email
    ↓
GET https://cv-server.up.railway.app/aprobar?id=PAGE_ID
    ↓
CV Server: PATCH Notion (Estado → "Aprobar")
    ↓
CV Server: HTTP 302 Redirect → Página de confirmación HTML
```

### 3.3 Flujo de Procesamiento (2 veces al día: 10:00, 18:00)

```
Schedule Trigger (10:00, 18:00)
    ↓
Notion: Query Database (Filter: Estado = "Aprobar")
    ↓
Split In Batches (procesa cada oferta)
    ↓
Para cada oferta:
    ├→ HTTP Request: Claude API → Genera carta de presentación
    ├→ HTTP Request: CV Server /analizar-cv → Optimiza CV con 3 prompts
    ├→ HTTP Request: CV Server /generar-cv → Genera CV DOCX
    ├→ Set Node: Prepara email con carta + link CV
    ├→ HTTP Request: Brevo → Envía email final
    └→ Notion: PATCH (Estado → "Procesado")
```

---

## 4. Estados en Notion Database

| Estado | Significado | Transición |
|--------|-------------|------------|
| `Enviado` | Oferta nueva, email notificación enviado | Auto |
| `Aprobar` | Usuario aprobó vía botón email | CV Server PATCH |
| `Descartado` | Usuario rechazó vía botón email | CV Server PATCH |
| `Procesado` | Carta y CV generados, email enviado | N8N Workflow |

---

## 5. CV Agent — Sistema de 3 Prompts

### Endpoint: `POST /analizar-cv`

**Request:**
```json
{
  "cv_master": "...contenido CV Master...",
  "oferta_empresa": "Google",
  "oferta_puesto": "Senior Frontend Developer",
  "oferta_descripcion": "...descripción de la oferta..."
}
```

**Flujo interno del CV Agent:**

```
Prompt 1: Análisis de Matching
─────────────────────────────
"Analiza este CV Master y la descripción del trabajo.
Pull every phrase this company uses to describe success.
List them next to my closest matching bullet points.

CV Master:
{cv_master}

Job Description:
{oferta_descripcion}"

→ Output: Mapeo de bullets CV ↔ requisitos empresa

Prompt 2: Optimización con Clarificaciones
──────────────────────────────────────────
"Basado en el análisis anterior, hazme preguntas clarificadoras
para ayudarme a reescribir mis bullet points usando exactamente
el lenguaje de la empresa. No mientas sobre lo que hice,
optimiza cómo lo describo.

Pregúntame hasta 5 cosas específicas para poder reescribir
los bullets más importantes."

→ Output: 5 preguntas al usuario (en este caso, usamos defaults)

Prompt 3: Scoring y Validación
───────────────────────────────
"Genera un CV adaptado usando el lenguaje optimizado.
Luego calcula el porcentaje de overlap de lenguaje entre
el CV adaptado y la descripción del trabajo.
Marca en rojo cualquier sección que esté por debajo del 60%.

Formato de salida:
{
  "cv_adaptado_markdown": "...",
  "score_matching": 78,
  "secciones_bajo_60": ["experiencia_angular"],
  "bullets_optimizados": [...]
}"
```

**Response:**
```json
{
  "success": true,
  "cv_adaptado_markdown": "...",
  "score_matching": 78,
  "secciones_bajo_60": [],
  "bullets_optimizados": [
    {
      "original": "Desarrollé aplicaciones con React",
      "optimizado": "Construí aplicaciones escalables con React siguiendo principios de Google..."
    }
  ]
}
```

---

## 6. Endpoints del CV Server

### 6.1 `GET /aprobar?id=PAGE_ID`

**Función:** Recibe click de email, actualiza Notion a "Aprobar", redirige a confirmación.

**Response:**
```html
HTTP/1.1 302 Found
Location: /confirmacion?mensaje=Oferta+aprobada&estado=success

O HTML directo:
<div style="font-family:Arial;text-align:center;padding:50px">
  <h1 style="color:#22C55E">✅ Oferta Aprobada</h1>
  <p>La oferta ha sido marcada para procesamiento.</p>
  <p>Recibirás un email con la carta y CV adaptado en la próxima ejecución.</p>
  <p><small>Próximas ejecuciones: 10:00 y 18:00</small></p>
</div>
```

### 6.2 `GET /descartar?id=PAGE_ID`

Similar a /aprobar pero cambia estado a "Descartado".

### 6.3 `POST /generar-cv` (existente)

Mantiene funcionalidad actual.

### 6.4 `POST /analizar-cv` (nuevo)

Implementa el CV Agent con sistema de 3 prompts.

---

## 7. Configuración de Schedules en N8N

### Schedule 1: Generación (Diario)
```
Cron: 0 9 * * *
Timezone: Europe/Madrid
Workflow: BuscarTrabajo-Generacion
```

### Schedule 2: Procesamiento (2 veces al día)
```
Cron: 0 10,18 * * *
Timezone: Europe/Madrid
Workflow: BuscarTrabajo-Procesamiento
```

---

## 8. Seguridad y Variables de Entorno

### CV Server (Railway)
```env
CLAUDE_API_KEY=sk-ant-...
NOTION_TOKEN=ntn_...
GOOGLE_CREDENTIALS_JSON=...
PORT=5000
```

### N8N (Render)
```env
NOTION_TOKEN=ntn_...
CLAUDE_API_KEY=sk-ant-...
BREVO_API_KEY=xkeysib-...
CV_SERVER_URL=https://cv-server-production.up.railway.app
```

---

## 9. Consideraciones de Implementación

### 9.1 Rate Limits

| Servicio | Límite | Estrategia |
|----------|--------|------------|
| Claude API | Tier dependiente | Implementar retry con backoff |
| Notion API | 3 req/s | Batch processing, no paralelo |
| Brevo API | 300 req/hour | Suficiente para uso personal |

### 9.2 Manejo de Errores

- **Claude API falla:** Guardar estado "Error-Claude", reintentar en próxima ejecución
- **CV Server no responde:** Timeout 30s, reintentar con backoff exponencial
- **Notion API error:** Log error, continuar con siguiente oferta

### 9.3 Render Free Tier

- **Problema:** Instancia duerme tras 15 min inactiva
- **Solución:** Polling en lugar de webhooks
- **Impacto:** Delay máximo 5-7 horas (entre aprobación y procesamiento)
- **Mitigación:** 2 ejecuciones diarias en horarios convenientes

---

## 10. Archivos a Modificar/Crear

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `cv_server_v2.py` | Modificar | Añadir `/aprobar`, `/descartar`, `/analizar-cv` |
| `BuscarTrabajo-FIXED.json` | Renombrar | `workflow-generacion.json` |
| `workflow-procesamiento.json` | Crear | Nuevo workflow para polling de aprobadas |
| `CV_Master_Veronica.txt` | Referenciar | Base de conocimiento para CV Agent |

---

## 11. Futuras Mejoras (Backlog)

### Fase 2 (Post-MVP)
- [ ] Conectar Indeed API para ofertas reales
- [ ] Job Search Agent para filtrar por salario/ubicación
- [ ] Auto-envío de candidaturas
- [ ] Tracking de respuestas

### Fase 3
- [ ] Migrar N8N a Railway para respuesta inmediata
- [ ] Dashboard web para gestión manual
- [ ] Métricas: tasa de respuesta, salarios, etc.

---

## 12. Métricas de Éxito

| Métrica | Objetivo | Cómo medir |
|---------|----------|------------|
| Uptime sistema | >95% | Logs Railway/Render |
| Ofertas generadas/día | 5 | Conteo Notion |
| Tiempo aprobación → procesamiento | <6 horas | Timestamps Notion |
| Score matching CV | >60% | Output CV Agent |
| Emails enviados correctamente | 100% | Logs Brevo |

---

**Documento aprobado por:** Verónica Serna  
**Fecha de aprobación:** 14 de Abril 2026  
**Próximo paso:** Crear plan de implementación con writing-plans skill
