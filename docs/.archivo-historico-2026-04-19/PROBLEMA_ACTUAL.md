# Documentación del Problema - Segundo Email No Se Dispara

## Fecha: 2026-04-14

---

## 🎯 Objetivo del Flujo

Cuando un usuario hace click en **"✅ Aprobar"** en el email de una oferta de trabajo:

1. ✅ Actualizar estado en Notion de "Enviado" → "Aprobado"
2. ✅ Obtener datos completos de la oferta desde Notion
3. ✅ Generar carta de presentación con Claude API
4. ✅ **Enviar segundo email con la carta** (HTTP Request6)
5. ✅ Llamar al CV Server para generar CV adaptado
6. ✅ **Enviar tercer email con el link al CV**

---

## ⚠️ Problema Actual

**El segundo email NO se dispara después de aprobar la oferta.**

### Síntomas:
- El webhook de aprobar SÍ se ejecuta (log: "Workflow was started")
- El estado en Notion SÍ se actualiza a "Aprobado" (después de correcciones)
- **PERO el flujo se para antes de enviar el segundo email**

---

## 🔍 Análisis del Workflow

### Flujo de Aprobación (WebhookAprovado):

```
WebhookAprovado (línea 292-305)
    ↓
HTTP Request1 (línea 187-220) - PATCH /v1/pages/{id} → Estado: "Aprobado"
    ↓
HTTP Request4 (línea 307-337) - GET /v1/pages/{id} → Obtiene datos completos
    ↓
HTTP Request3 (línea 257-290) - POST Claude API → Genera carta
    ↓
Code in JavaScript1 (línea 367-378) - Prepara email
    ↓
HTTP Request6 (línea 380-407) - POST Brevo → ENVÍA SEGUNDO EMAIL ⚠️ NO LLEGA AQUÍ
    ↓
CV Server (línea 409-435) - POST /generar-cv
    ↓
Preparar email CV (línea 437-448) - Prepara email CV
    ↓
Email CV Brevo (línea 450-477) - POST Brevo → ENVÍA TERCER EMAIL
```

---

## 🔧 Correcciones Aplicadas

### 1. Referencias de datos en webhooks (`.item` → `.first()`)

| Nodo | Línea | Antes | Después |
|------|-------|-------|---------|
| HTTP Request1 | 190 | `$json.query.id` | `$('WebhookAprovado').first().json.query.id` |
| HTTP Request2 | 225 | `$json.query.id` | `$('WebhookDescartado').first().json.query.id` |
| HTTP Request4 | 310 | `.item.json` | `.first().json` |

### 2. Estado inicial en Notion

| Nodo | Línea | Antes | Después |
|------|-------|-------|---------|
| Create a database page1 | 133 | `=Pendiente` | `=Enviado` |

### 3. Estado en PATCH de aprobar

| Nodo | Línea | Antes | Después |
|------|-------|-------|---------|
| HTTP Request1 | 210 | `Enviado` | `Aprobado` |

---

## 🧪 Pruebas Pendientes

### Lo que necesitamos verificar:

1. **HTTP Request4 (GET datos)** - ¿Está recibiendo el ID correcto de Notion?
   - URL: `https://api.notion.com/v1/pages/{{ $('WebhookAprovado').first().json.query.id }}`
   - Método: GET
   - Headers: Authorization, Notion-Version, Content-Type

2. **HTTP Request3 (Claude API)** - ¿Está recibiendo los datos de la oferta?
   - Usa `{{ $json.properties.Empresa.title[0].text.content }}`
   - Usa `{{ $json.properties.Puesto.rich_text[0].text.content }}`
   - Usa `{{ $json.properties.Notas.rich_text[0].text.content }}`

3. **Code in JavaScript1** - ¿Está recibiendo la carta de Claude?
   - Espera: `$input.first().json.content[0].text`

4. **HTTP Request6** - ¿Se está ejecutando?
   - Envía email con la carta a `hello.cookyourweb@gmail.com`

---

## 🔎 Posibles Causas del Fallo

### Causa 1: HTTP Request1 no devuelve datos útiles
- El PATCH de Notion devuelve solo metadata de la página
- HTTP Request4 necesita el ID, pero lo toma del webhook, no del output de HTTP Request1
- **Verificación**: Checkear logs de n8n para ver qué devuelve HTTP Request1

### Causa 2: HTTP Request4 falla al obtener datos
- El ID del webhook puede no ser válido
- Los permisos de Notion API pueden ser insuficientes
- **Verificación**: Probar GET manual con el mismo ID

### Causa 3: HTTP Request3 (Claude) falla
- La API key puede estar expirada
- El payload puede tener sintaxis incorrecta
- **Verificación**: Checkear respuesta de Claude API

### Causa 4: Code in JavaScript1 falla
- La estructura de datos de entrada no es la esperada
- **Verificación**: Añadir console.log para debug

---

## 📋 Checklist de Debugging

- [ ] Ejecutar workflow manualmente desde n8n
- [ ] Ver logs de ejecución de cada nodo
- [ ] Verificar que HTTP Request1 devuelve 200 OK
- [ ] Verificar que HTTP Request4 devuelve 200 OK con datos
- [ ] Verificar que HTTP Request3 devuelve 200 OK con carta generada
- [ ] Verificar que Code in JavaScript1 produce output válido
- [ ] Verificar que HTTP Request6 se ejecuta y devuelve 200 OK
- [ ] Checkear bandeja de entrada de emails (spam?)

---

## 📝 URLs de Webhooks

- **Aprobar**: `https://n8n-qwmu.onrender.com/webhook/aprobar?id={ID_OFERTA}`
- **Descartar**: `https://n8n-qwmu.onrender.com/webhook/descartar?id={ID_OFERTA}`

---

## 📊 Estados en Notion

| Estado | Descripción |
|--------|-------------|
| `Enviado` | Oferta creada, email enviado, esperando respuesta |
| `Aprobado` | Usuario aprobó, proceso de carta/CV en curso o completado |
| `Descartado` | Usuario rechazó la oferta |
| `Pendiente` | (Antiguo estado inicial - ya no se usa) |

---

## 🔄 Flujo Completo del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                    GENERACIÓN DE OFERTAS                        │
├─────────────────────────────────────────────────────────────────┤
│ Schedule Trigger (9am)                                          │
│     ↓                                                           │
│ HTTP Request (Claude API) - Genera 5 ofertas ficticias          │
│     ↓                                                           │
│ Code in JavaScript - Parsea y normaliza modalidad               │
│     ↓                                                           │
│ Create a database page1 - Crea en Notion (Estado: Enviado)      │
│     ↓                                                           │
│ HTTP Request5 - Envía email con botones Aprobar/Descartar       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    FLUJO DE APROBACIÓN                          │
├─────────────────────────────────────────────────────────────────┤
│ WebhookAprovado (click en email)                                │
│     ↓                                                           │
│ HTTP Request1 - PATCH Notion: Estado → "Aprobado"               │
│     ↓                                                           │
│ HTTP Request4 - GET Notion: Obtiene datos completos             │
│     ↓                                                           │
│ HTTP Request3 - Claude: Genera carta de presentación            │
│     ↓                                                           │
│ Code in JavaScript1 - Prepara email con carta                   │
│     ↓                                                           │
│ HTTP Request6 - Brevo: ENVÍA SEGUNDO EMAIL ⚠️                   │
│     ↓                                                           │
│ CV Server - POST /generar-cv                                    │
│     ↓                                                           │
│ Preparar email CV - Prepara email con link                      │
│     ↓                                                           │
│ Email CV Brevo - Brevo: ENVÍA TERCER EMAIL                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    FLUJO DE DESCARTAR                           │
├─────────────────────────────────────────────────────────────────┤
│ WebhookDescartado (click en email)                              │
│     ↓                                                           │
│ HTTP Request2 - PATCH Notion: Estado → "Descartado"             │
│     ↓                                                           │
│ (Fin del flujo)                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Archivos Relacionados

| Archivo | Descripción |
|---------|-------------|
| `workflow_final_v3.json` | Workflow principal de n8n |
| `cv_server_v2.py` | Servidor Flask para generar CVs |
| `generar_cv_master.py` | Script maestro para generación de CV |
| `CV_Master_Veronica.txt` | Plantilla base del CV |
| `requirements.txt` | Dependencias Python |

---

## 📞 Siguientes Pasos

1. **Probar el webhook de aprobar** en n8n y revisar logs nodo por nodo
2. **Identificar en qué nodo se para** el flujo
3. **Corregir el error específico** (si es HTTP Request4, verificar ID; si es HTTP Request3, verificar API key; etc.)
4. **Una vez funcione**, generar documentación completa del sistema

---

*Documento creado durante sesión de debugging del 2026-04-14*
