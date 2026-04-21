# Estado Real del Workflow - Análisis Completo

**Fecha:** 17 Abril 2026  
**Autor:** CookYourWebAI

---

## 🎯 Resumen Ejecutivo

Después de analizar **12 archivos JSON de workflows** y toda la documentación, este es el estado REAL del sistema:

### Workflow Recomendado: `BUSCARTRABAJO-DEFINITIVO-FINAL.json`

| Característica | Estado |
|----------------|--------|
| URL CV Server | ✅ Correcta (`railway.app`) |
| Flujo secuencial | ✅ Correcto (no paralelo) |
| Emails enviados | ✅ 3 emails (Notificación, Carta, CV) |
| Estado inicial | ✅ "Pendiente" |
| Webhooks | ✅ `/approve` y `/reject` |
| Botón "Mandar a empresa" | ❌ FALTA |
| Webhook `/mandar-empresa` | ❌ FALTA |
| Guardar seguimiento en Notion | ❌ FALTA |
| Email confirmación "Aplicado" | ❌ FALTA |

---

## 📊 Comparativa de Workflows

| Archivo | Activo | Emails | CV Server URL | Estado | Recomendado |
|---------|--------|--------|---------------|--------|-------------|
| `BUSCARTRABAJO-DEFINITIVO-FINAL.json` | ❌ No | 3 | ✅ railway.app | Completo | ✅ **SÍ** |
| `BUSCARTRABAJO-EMAILS-FIXED.json` | ✅ Sí | 2 | ✅ railway.app | Activo pero incompleto | ⚠️ Parcial |
| `BUSCARTRABAJO-FINAL-FIXED.json` | ❌ No | 3 | ✅ railway.app | Bueno | ✅ Sí |
| `workflow_final_v3.json` | ✅ Sí | 3 | ❌ render.gg | **URL ROTA** | ❌ NO |
| `workflow-DEFINITIVO.json` | ❌ No | 2 | ❌ no tiene | Incompleto | ❌ NO |

---

## 🔄 Flujo ACTUAL (lo que funciona)

### Flujo Principal (9:00 AM)
```
Schedule Trigger
    ↓
Claude API → Genera 5 ofertas
    ↓
Code → Normaliza modalidad (Remoto/Hibrido/Presencial)
    ↓
Notion → Crea página (Estado: Pendiente)
    ↓
Brevo → Email #1: Notificación con botones ✅/❌
```

### Flujo Aprobar (Webhook `/approve`)
```
Webhook Aprobar
    ↓
Notion PATCH → Estado: "Aprobado"
    ↓
Notion GET → Obtiene datos completos
    ↓
Set → Normaliza datos (empresa, puesto, descripción)
    ↓
Claude API → Genera carta de presentación
    ↓
Code → Prepara HTML carta
    ↓
Brevo → Email #2: Carta de presentación
    ↓
CV Server → Genera CV adaptado → Sube a Drive
    ↓
Code → Prepara HTML con link CV
    ↓
Brevo → Email #3: CV adaptado con link a Drive
```

### Flujo Descartar (Webhook `/reject`)
```
Webhook Descartar
    ↓
Notion PATCH → Estado: "Descartado"
    ↓
FIN
```

---

## ❌ LO QUE FALTA (Requisitos del Usuario)

### 1. Botón "Mandar a empresa" en Email #2

**Email #2 actual:** Solo muestra carta de presentación + link CV  
**Email #2 necesario:** Debe tener botón para siguiente paso

```html
<!-- AÑADIR al final del Email #2 -->
<a href="https://n8n-qwmu.onrender.com/webhook/mandar-empresa?id=PAGE_ID" 
   style="background:#1F5C8B;color:white;padding:12px 24px;text-decoration:none;border-radius:6px">
   ✅ Mandar a empresa
</a>
```

### 2. Nuevo Webhook `/mandar-empresa`

```
Webhook Mandar Empresa (NUEVO)
    ↓
Notion PATCH → Estado: "Enviado a empresa"
    ↓
Notion PATCH → Añadir campos:
    - Fecha envío: hoy
    - Link CV enviado: el de Drive
    - Contacto: (si existe en la oferta)
    ↓
Brevo → Email #4: Confirmación "✅ Aplicado a [Empresa]"
```

### 3. Nuevos campos en Notion

| Columna | Tipo | Propósito |
|---------|------|-----------|
| `Fecha envío` | Date | Cuándo se aplicó a la oferta |
| `Contacto` | Text | Persona de contacto en la empresa |
| `Link CV enviado` | URL | Link al CV en Drive que se envió |
| `Seguimiento` | Date | Recordatorio para follow-up |

### 4. Email #4 de confirmación

| # | Momento | Asunto | Contenido |
|---|---------|--------|-----------|
| **4** | Tras click "Mandar a empresa" | `✅ Aplicado a [Empresa] - [Puesto]` | Confirmación + datos de seguimiento |

---

## 🔧 URLs Correctas (Verificadas)

| Servicio | URL | Estado |
|----------|-----|--------|
| **N8N** | `https://n8n-qwmu.onrender.com` | ⚠️ Render Free (puede dormir) |
| **CV Server** | `https://cv-server-production.up.railway.app` | ✅ Producción |
| **Webhook Aprobar** | `https://n8n-qwmu.onrender.com/webhook/approve` | ✅ |
| **Webhook Descartar** | `https://n8n-qwmu.onrender.com/webhook/reject` | ✅ |
| **Webhook Mandar Empresa** | `https://n8n-qwmu.onrender.com/webhook/mandar-empresa` | ❌ **CREAR** |

---

## 🧪 Testing Manual (SIN esperar a las 9:00)

### Opción 1: Desde n8n UI (Recomendado)

```
1. Ir a: https://n8n-qwmu.onrender.com
2. Workflows → BuscarTrabajo-DEFINITIVO-FINAL
3. Click en "Test workflow" (esquina superior derecha)
4. Click en "Execute workflow" en el nodo "Manual Trigger"
5. Ver ejecución en tiempo real
```

### Opción 2: Nodo Manual Trigger

El workflow incluye **dos triggers**:

| Trigger | Tipo | Uso |
|---------|------|-----|
| `Schedule Trigger (9am)` | Schedule | Producción (diario 9:00) |
| `Manual Trigger` | Manual | Testing (ejecución inmediata) |

**Importante:** Ambos triggers están conectados al mismo flujo, puedes usar cualquiera.

### Opción 3: Webhook de test

```bash
# Ejecutar workflow completo via webhook (si está configurado)
curl "https://n8n-qwmu.onrender.com/webhook/test-trigger"
```

---

## 📧 Secuencia de Emails (ACTUAL vs NECESARIO)

### Actual (3 emails)

| # | Momento | Asunto | Contenido |
|---|---------|--------|-----------|
| 1 | 9:00 AM o Manual | `🤖 Nueva oferta: [Empresa] - [Puesto]` | Datos + botones Aprobar/Descartar |
| 2 | Tras aprobar | `📝 Carta de Presentación Generada - [Empresa]` | Solo carta |
| 3 | Tras generar CV | `✅ Oferta lista: [Empresa] - [Puesto]` | Carta + Link CV |

### Necesario (4 emails + botón)

| # | Momento | Asunto | Contenido | Botón |
|---|---------|--------|-----------|-------|
| 1 | 9:00 AM | `🤖 Nueva oferta: [Empresa] - [Puesto]` | Datos + botones | ✅ Aprobar / ❌ Descartar |
| 2 | Tras aprobar | `📝 Carta + CV Generados - [Empresa]` | Carta + Link CV | ✅ Mandar a empresa |
| 3 | (Opcional) | `📄 CV Adaptado - [Empresa]` | Solo link CV | - |
| 4 | Tras mandar | `✅ Aplicado a [Empresa] - Seguimiento` | Confirmación + datos | - |

---

## 🛠️ Pasos para Completar el Workflow

### Paso 1: Importar workflow recomendado
```
1. n8n → Workflows → Import from File
2. Seleccionar: BUSCARTRABAJO-DEFINITIVO-FINAL.json
3. Activar toggle (verde)
4. Guardar (Ctrl+S)
```

### Paso 2: Añadir botón "Mandar a empresa" en Email #2

**Nodo a editar:** `Code - Preparar Email CV` (línea ~280)

**Añadir al HTML:**
```html
<a href="https://n8n-qwmu.onrender.com/webhook/mandar-empresa?id={{ $json.notion_page_id }}" 
   style="background:#1F5C8B;color:white;padding:12px 24px;text-decoration:none;border-radius:6px;display:inline-block;margin-top:20px">
   ✅ Mandar a empresa
</a>
```

### Paso 3: Crear webhook `/mandar-empresa`

```json
{
  "parameters": {
    "path": "mandar-empresa",
    "options": {"httpMethod": "GET"}
  },
  "type": "n8n-nodes-base.webhook",
  "name": "Webhook Mandar Empresa"
}
```

### Paso 4: Añadir nodos de seguimiento en Notion

```
Webhook Mandar Empresa
    ↓
Set → Preparar datos seguimiento
    ↓
Notion PATCH → Estado: "Enviado a empresa"
    ↓
Notion PATCH → Añadir:
    - Fecha envío: {{ new Date().toISOString() }}
    - Link CV enviado: {{ $json.cv_link }}
    - Contacto: {{ $json.contacto || '' }}
    ↓
Brevo → Email confirmación
```

### Paso 5: Actualizar schema de Notion

**Database ID:** `33d11515-f4b2-81ef-a776-d0ea698b748f`

**Columnas a añadir:**
- `Fecha envío` (Date)
- `Contacto` (Text)
- `Link CV enviado` (URL)
- `Seguimiento` (Date)

---

## 🧪 Testing Rápido

### Test 1: Flujo principal
```bash
# En n8n, ejecutar desde Schedule Trigger
# Debe:
# ✅ Generar 5 ofertas
# ✅ Crear 5 páginas en Notion
# ✅ Enviar 5 emails con botones
```

### Test 2: Flujo aprobar
```bash
# Obtener page_id de Notion
curl "https://n8n-qwmu.onrender.com/webhook/approve?id=PAGE_ID"

# Debe:
# ✅ Actualizar Notion a "Aprobado"
# ✅ Enviar Email #2 (Carta)
# ✅ Generar CV
# ✅ Enviar Email #3 (CV)
# ✅ Mostrar botón "Mandar a empresa"
```

### Test 3: Flujo mandar empresa (NUEVO)
```bash
# Después de crear el webhook
curl "https://n8n-qwmu.onrender.com/webhook/mandar-empresa?id=PAGE_ID"

# Debe:
# ✅ Actualizar Notion a "Enviado a empresa"
# ✅ Guardar fecha, link CV, contacto
# ✅ Enviar Email #4 (Confirmación)
```

---

## 📝 Archivos de Workflow - Cuál Usar

| Para qué | Archivo | Acción |
|----------|---------|--------|
| **Usar en producción** | `BUSCARTRABAJO-DEFINITIVO-FINAL.json` | Importar y completar |
| **Referencia** | `BUSCARTRABAJO-EMAILS-FIXED.json` | El que está activo ahora |
| **Descartar** | `workflow_final_v3.json` | URL CV Server rota |
| **Descartar** | `workflow-DEFINITIVO.json` | Incompleto |

---

## ✅ Checklist Final

- [ ] Importar `BUSCARTRABAJO-DEFINITIVO-FINAL.json`
- [ ] Activar workflow en n8n
- [ ] Añadir botón "Mandar a empresa" en Email #2
- [ ] Crear webhook `/mandar-empresa`
- [ ] Añadir nodos de seguimiento en Notion
- [ ] Crear columnas en Notion DB (Fecha envío, Contacto, Link CV, Seguimiento)
- [ ] Añadir Email #4 de confirmación
- [ ] Test completo del flujo
- [ ] Verificar que llegan todos los emails

---

**Próximo paso:** Crear el workflow completo con todas las funcionalidades y actualizar la documentación oficial.
