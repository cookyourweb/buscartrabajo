# Análisis Completo del Workflow N8N - BuscarTrabajo

## Fecha: 16 Abril 2026

---

## Resumen Ejecutivo

Después de revisar exhaustivamente toda la documentación y los archivos JSON del workflow, he identificado que **el workflow más reciente y completo es: `BUSCARTRABAJO-EMAILS-FIXED.json`** (última modificación: 16 Abril 2026, 13:37).

Este archivo ya contiene las correcciones necesarias para el flujo de emails, incluyendo el nodo **Set - Preparar Datos Email** que consolida los datos antes de generar la carta.

---

## Flujo Actual Corregido (BUSCARTRABAJO-EMAILS-FIXED.json)

### Flujo Principal (Generación de Ofertas)

```
Schedule Trigger (9:00 AM)
    ↓
HTTP Request - Claude API (Genera 5 ofertas)
    ↓
Code in JavaScript - Normalizar Modalidad
    ↓
Create a database page1 - Notion (Estado: Enviado)
    ↓
HTTP Request5 - Email Notificación
    [Email 1: Nueva oferta con botones Aprobar/Descartar]
```

### Flujo Aprobar (Webhooks) - CORREGIDO ✅

```
WebhookAprovado (/webhook/approve)
    ↓
HTTP Request1 - Notion PATCH (Estado → "Aprobado")
    ↓
HTTP Request4 - Notion GET (Obtiene datos completos)
    ↓
Set - Preparar Datos Email ← NUEVO: Extrae empresa, puesto, salario, etc.
    ↓
HTTP Request3 - Generar Carta v2 ← Usa datos del Set
    ↓
Code - Preparar Email Carta ← Prepara HTML con la carta
    ↓
HTTP Request6 - Email Carta ← ENVÍA EMAIL #2 (Carta) ✅
    ↓
CV Server - Generar CV
    ↓
Code - Preparar Email CV Final
    ↓
HTTP Request7 - Email CV Final ← ENVÍA EMAIL #3 (Carta + CV) ✅
```

### Flujo Descartar

```
WebhookDescartado (/webhook/reject)
    ↓
HTTP Request2 - Notion PATCH (Estado → "Descartado")
    ↓
FIN
```

---

## Cambios Clave en el Workflow Corregido

### 1. Nodo "Set - Preparar Datos Email" (NUEVO)

**Ubicación:** Entre HTTP Request4 y HTTP Request3

**Función:** Extrae y normaliza los datos de Notion ANTES de pasarlos a Claude:

```javascript
// Campos extraídos:
- empresa: {{ $json.properties.Empresa.title[0].text.content }}
- puesto: {{ $json.properties.Puesto.rich_text[0].text.content }}
- salario: {{ $json.properties.Salario?.rich_text[0]?.text?.content || 'No especificado' }}
- modalidad: {{ $json.properties.Modalidad?.select?.name || 'No especificado' }}
- descripcion: {{ $json.properties.Notas?.rich_text[0]?.text?.content || '' }}
```

**Por qué es necesario:**
- El nodo HTTP Request3 (Claude API) necesita datos planos, no la estructura anidada de Notion
- Sin este nodo, las referencias `$json.properties.Empresa...` fallaban

### 2. Nodo "HTTP Request3 - Generar Carta v2" (CORREGIDO)

**Cambio:** Ahora usa las variables del nodo Set anterior:

```javascript
// ANTES (no funcionaba):
"Empresa: {{ $json.properties.Empresa.title[0].text.content }}"

// DESPUÉS (funciona):
"Empresa: {{ $json.empresa }}"
```

### 3. Nodo "Code - Preparar Email Carta" (CORREGIDO)

**Función:** Prepara el body para Brevo con la carta generada

**Input:** Datos del nodo anterior + respuesta de Claude
**Output:** Objeto `brevoBody` listo para enviar

```javascript
return [{
  json: {
    brevoBody: brevoBody,  // ← Importante: formato que espera HTTP Request6
    cartaTexto: cartaTexto,
    empresa: empresa,
    puesto: puesto
  }
}];
```

### 4. Nodo "HTTP Request6 - Email Carta" (CORREGIDO)

**Cambio:** Usa `contentType: "raw"` en lugar de `specifyBody: "json"`

```javascript
// Configuración:
{
  "contentType": "raw",
  "rawContentType": "application/json",
  "body": "={{ JSON.stringify($json.brevoBody) }}"
}
```

**Por qué:** Evita problemas de escape de caracteres en el JSON

---

## URLs de Webhooks Corregidas

| Acción | URL | Método |
|--------|-----|--------|
| **Aprobar** | `https://n8n-qwmu.onrender.com/webhook/approve` | GET |
| **Descartar** | `https://n8n-qwmu.onrender.com/webhook/reject` | GET |

**Parámetro:** `?id={NOTION_PAGE_ID}`

---

## Secuencia de Emails

| # | Momento | Asunto | Contenido |
|---|---------|--------|-----------|
| **1** | 9:00 AM (Schedule) | `🤖 Nueva oferta: [Empresa] - [Puesto]` | Datos de la oferta + botones Aprobar/Descartar |
| **2** | Después de aprobar | `📝 Carta de Presentación Generada - [Empresa]` | Carta de presentación completa |
| **3** | Después de generar CV | `✅ Oferta lista: [Empresa] - [Puesto]` | Carta + Link al CV en Google Drive |

---

## Estados en Notion

```
┌──────────┐     ┌──────────┐     ┌────────────┐
│ Enviado  │────▶│ Aprobado │     │ Descartado │
│ (nuevo)  │     │          │     │            │
└──────────┘     └──────────┘     └────────────┘
     │                │                  │
     │                ▼                  │
     │           [Genera Carta           │
     │            + CV]                  │
     │                │                  │
     │                ▼                  │
     │           [Emails 2 y 3]          │
     │                                    │
     └────────────────────────────────────┘
```

---

## Instrucciones para Publicar en N8N

### Paso 1: Acceder a N8N

1. Ve a: `https://n8n-qwmu.onrender.com`
2. Inicia sesión con tus credenciales

### Paso 2: Importar el Workflow

1. Ve a **Workflows** (menú lateral)
2. Click en **"Import from File"** (botón arriba a la derecha)
3. Selecciona: `BUSCARTRABAJO-EMAILS-FIXED.json`
4. El workflow se importará como: "BuscarTrabajo-EMAILS-FIXED"

### Paso 3: Verificar Credenciales

**Importante:** Las API keys están embebidas en el JSON. Verifica que estén activas:

1. **Claude API (Anthropic):** Verificar que `sk-ant-api03-...` siga siendo válida
2. **Notion:** Token `ntn_G464872773099dpLY7OzD7I4ZeZee38rKHsoVlmCV2z7A0`
3. **Brevo:** API Key `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`
4. **CV Server:** URL `https://cv-server-production.up.railway.app/generar-cv`

### Paso 4: Activar el Workflow

1. Abre el workflow importado
2. Busca el toggle **"Active"** en la esquina superior derecha
3. Actívalo (debe ponerse **VERDE**)
4. Guarda: `Ctrl+S` o `File → Save`

### Paso 5: Verificar Webhooks

Los webhooks se activan automáticamente cuando el workflow está activo. URLs:

```
Aprobar:   https://n8n-qwmu.onrender.com/webhook/approve?id=PAGE_ID
Descartar: https://n8n-qwmu.onrender.com/webhook/reject?id=PAGE_ID
```

---

## Testing del Workflow

### Test 1: Flujo Principal (Generación)

```bash
# En n8n, ejecuta manualmente desde el nodo "Schedule Trigger"
# O espera a las 9:00 AM

# Deberías recibir:
# ✅ 5 emails de notificación con ofertas
# ✅ 5 páginas creadas en Notion (estado: Enviado)
```

### Test 2: Flujo Aprobar

```bash
# Obtén un page_id de Notion de una oferta en estado "Enviado"

# Prueba el webhook de aprobar:
curl "https://n8n-qwmu.onrender.com/webhook/approve?id=PAGE_ID_AQUI"

# Deberías recibir:
# ✅ Email #2: "📝 Carta de Presentación Generada..."
# ✅ Email #3: "✅ Oferta lista..." (con link al CV)
```

### Test 3: Flujo Descartar

```bash
# Prueba el webhook de descartar:
curl "https://n8n-qwmu.onrender.com/webhook/reject?id=PAGE_ID_AQUI"

# Verifica en Notion que el estado cambie a "Descartado"
```

---

## Debugging - Si Algo Falla

### Problema: Email #2 no llega

**Pasos para diagnosticar:**

1. **Revisa ejecuciones en n8n:**
   - Ve a la pestaña **"Executions"**
   - Busca la ejecución del webhook
   - Expande cada nodo para ver qué datos recibe

2. **Verifica el nodo "Set - Preparar Datos Email":**
   - ¿Está extrayendo empresa y puesto correctamente?
   - Los campos deberían tener valores, no estar vacíos

3. **Verifica el nodo "HTTP Request3 - Generar Carta v2":**
   - ¿Recibió respuesta de Claude (200 OK)?
   - ¿La respuesta tiene `content[0].text`?

4. **Verifica el nodo "Code - Preparar Email Carta":**
   - ¿Generó el objeto `brevoBody` correctamente?
   - ¿El campo `htmlContent` tiene la carta?

5. **Verifica el nodo "HTTP Request6 - Email Carta":**
   - ¿Devolvió 200 OK?
   - ¿Hay errores en la respuesta de Brevo?

### Comandos útiles para testing:

```bash
# Test CV Server
curl -X POST https://cv-server-production.up.railway.app/generar-cv \
  -H "Content-Type: application/json" \
  -d '{"empresa":"Test","puesto":"Dev","descripcion":"test"}'

# Test webhook aprobar (reemplazar PAGE_ID)
curl -v "https://n8n-qwmu.onrender.com/webhook/approve?id=PAGE_ID"

# Test webhook descartar
curl -v "https://n8n-qwmu.onrender.com/webhook/reject?id=PAGE_ID"
```

---

## Servicios Externos - Verificación

| Servicio | URL | Estado |
|----------|-----|--------|
| **N8N** | https://n8n-qwmu.onrender.com | ⚠️ Verificar activo |
| **CV Server** | https://cv-server-production.up.railway.app | ✅ Producción |
| **Notion DB** | 33d11515-f4b2-81ef-a776-d0ea698b748f | ✅ Configurado |

---

## Próximos Pasos Recomendados

1. ✅ **Importar** `BUSCARTRABAJO-EMAILS-FIXED.json` en n8n
2. ✅ **Activar** el workflow (toggle verde)
3. ✅ **Probar** el flujo de generación manualmente
4. ✅ **Crear** una oferta de prueba y hacer click en "Aprobar"
5. ✅ **Verificar** que lleguen los 3 emails
6. 🔄 **Si falla:** Revisar logs en n8n → Executions

---

## Notas Importantes

1. **Render Free Tier:** El servicio "duerme" tras 15 min de inactividad. El primer webhook puede tardar 30-60 segundos en responder mientras se "despierta".

2. **CV Server:** Ya está funcionando en producción en Railway. No necesita cambios.

3. **Notion:** El estado inicial de las ofertas es "Enviado" (no "Pendiente").

4. **Emails:** Pueden llegar a Spam. Verifica la carpeta de spam si no los ves en la bandeja de entrada.

---

**Documento creado:** 16 Abril 2026  
**Workflow recomendado:** `BUSCARTRABAJO-EMAILS-FIXED.json`  
**Estado:** Listo para importar y probar
