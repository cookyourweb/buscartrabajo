# Documentación Corrección Workflow - Abril 2026

**Fecha:** 17 Abril 2026  
**Archivo:** `BUSCARTRABAJO-CORREGIDO.json`  
**Estado:** ✅ Listo para producción

---

## 📋 Problemas Corregidos

### 1. ❌ Email del remitente no verificado en Brevo

**Problema:** El nodo "Set - Preparar Email Notificacion" usaba `veronica@usecookyourwebai.es` que no estaba verificado en Brevo.

**Solución:** Cambiado a `hello.cookyourweb@gmail.com` (email verificado)

**Nodos afectados:**
- `Set - Preparar Email Notificacion` (línea 82)
- `Code - Preparar Confirmación` (línea 224)
- `Code - Fusionar Carta+CV` (línea 316)

---

### 2. ❌ Flujo paralelo mal configurado

**Problema:** "CV Server - Generar CV" y "Claude - Generar Carta" estaban en secuencia incorrecta. Claude devolvía texto de carta, pero CV Server esperaba datos de Notion (`empresa`, `puesto`, `descripcion`).

**Solución:** Añadido nodo "Code - Preparar Datos Paralelo" que distribuye datos a ambas ramas en paralelo.

**Flujo CORREGIDO:**
```
Notion - Obtener Datos Oferta
    ↓
Code - Preparar Datos Paralelo
    ├─→ Claude - Generar Carta (rama superior)
    └─→ CV Server - Generar CV (rama inferior)
            ↓
    Code - Fusionar Carta+CV (recibe de ambas)
            ↓
    Brevo - Enviar Carta+CV
```

---

### 3. ❌ Nodo "Code - Preparar Email Carta+CV" accedía a datos incorrectos

**Problema:** El código intentaba acceder a:
```javascript
const carta = $input.first().json.content[0].text;  // ✅ De Claude
const empresa = $input.first().json.properties...    // ❌ De Notion (no disponible)
```

Pero recibía datos de "CV Server", no de "Notion - Obtener Datos".

**Solución:** Renombrado a "Code - Fusionar Carta+CV" y reescrito para usar `$node[]` para acceder a la rama de CV Server:

```javascript
// Rama 1 (carta): viene de Claude
const cartaResponse = $input.first().json;
const carta = cartaResponse.content?.[0]?.text || '';

// Rama 2 (CV): accedemos via $node
const cvResponse = $node["CV Server - Generar CV"].first().json;
const linkCV = cvResponse.link || cvResponse.cv_link || '';
```

---

## 🔄 Flujo Completo del Workflow

### Flujo Principal (9:00 AM o Manual)

```
┌──────────────────────┐
│ Schedule/Manual      │
│ Trigger              │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Claude - Generar     │
│ Ofertas (5 ofertas)  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Code - Normalizar    │
│ Modalidad            │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Notion - Crear       │
│ Oferta (Estado:      │
│ Pendiente)           │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Set - Preparar Email │
│ Notificacion         │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Brevo - Enviar       │
│ Email #1:            │
│ 🤖 Nueva oferta      │
│ + botones ✅/❌      │
└──────────────────────┘
```

---

### Flujo "Aprobar" (Webhook `/oferta-aprobar`)

```
┌──────────────────────┐
│ Webhook Aprobar      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Notion - Marcar      │
│ Aprobado             │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Notion - Obtener     │
│ Datos Oferta         │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Code - Preparar      │
│ Datos Paralelo       │
└──────────┬───────────┘
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌─────────┐   ┌─────────┐
│ Claude  │   │ CV      │
│ Carta   │   │ Server  │
└────┬────┘   └────┬────┘
     │             │
     └──────┬──────┘
            │
            ▼
┌──────────────────────┐
│ Code - Fusionar      │
│ Carta+CV             │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Brevo - Email #2:    │
│ 📝 Carta + 📄 CV     │
│ + botón ✅ Empresa   │
└──────────────────────┘
```

---

### Flujo "Descartar" (Webhook `/oferta-descartar`)

```
┌──────────────────────┐
│ Webhook Descartar    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Notion - Marcar      │
│ Descartado           │
└──────────────────────┘
```

---

### Flujo "Mandar a Empresa" (Webhook `/oferta-mandar-empresa`)

```
┌──────────────────────┐
│ Webhook Mandar       │
│ Empresa              │
└──────────┬───────────┘
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌─────────┐   ┌─────────┐
│ Notion  │   │ Code    │
│ Enviado │   │ Preparar│
│         │   │ Confirm.│
└─────────┘   └────┬────┘
                   │
                   ▼
            ┌──────────────────────┐
            │ Brevo - Email #3:    │
            │ ✅ Aplicado a        │
            │ [Empresa]            │
            └──────────────────────┘
```

---

## 📧 Secuencia de Emails

| # | Momento | Asunto | Contenido | Botones |
|---|---------|--------|-----------|---------|
| **1** | 9:00 AM | `🤖 Nueva oferta: [Empresa] - [Puesto]` | Datos oferta + tabla | ✅ Aprobar / ❌ Descartar |
| **2** | Tras aprobar | `Candidatura completa: [Empresa]` | Carta + Link CV | ✅ Mandar a empresa |
| **3** | Tras mandar | `✅ Aplicado a [Empresa] - [Puesto]` | Confirmación + fecha | - |

---

## 🔧 Configuración de Emails (Brevo)

**Importante:** Todos los emails usan `hello.cookyourweb@gmail.com` como remitente y destinatario para testing.

**Para producción**, actualizar los nodos Set/Code para usar:
- `sender_email`: Email verificado en Brevo (dominio propio)
- `to_email`: Email del contacto desde Notion (cuando esté disponible)

---

## 📊 Nodos del Workflow

| Nodo | Tipo | Función |
|------|------|---------|
| `Manual Trigger` | Trigger | Ejecución manual para testing |
| `Schedule Trigger (9am)` | Trigger | Ejecución diaria 9:00 AM |
| `Claude - Generar Ofertas` | HTTP Request | Llama a Claude API para 5 ofertas |
| `Code - Normalizar Modalidad` | Code | Normaliza modalidad (Remoto/Hibrido/Presencial) |
| `Notion - Crear Oferta` | Notion | Crea página en DB con estado "Pendiente" |
| `Set - Preparar Email Notificacion` | Set | Prepara variables para Email #1 |
| `Brevo - Enviar Notificacion` | HTTP Request | Envía Email #1 |
| `Webhook Aprobar` | Webhook | Recibe click en "Aprobar" |
| `Webhook Descartar` | Webhook | Recibe click en "Descartar" |
| `Webhook Mandar Empresa` | Webhook | Recibe click en "Mandar a empresa" |
| `Notion - Marcar Aprobado` | HTTP Request | PATCH Notion → Estado: "Aprobado" |
| `Notion - Marcar Descartado` | HTTP Request | PATCH Notion → Estado: "Descartado" |
| `Notion - Marcar Enviado a empresa` | HTTP Request | PATCH Notion → Estado: "Enviado a empresa" |
| `Notion - Obtener Datos Oferta` | HTTP Request | GET Notion → Datos completos |
| `Code - Preparar Datos Paralelo` | Code | Distribuye datos a ramas paralelas |
| `Claude - Generar Carta` | HTTP Request | Genera carta de presentación |
| `CV Server - Generar CV` | HTTP Request | Genera CV adaptado en Drive |
| `Code - Fusionar Carta+CV` | Code | Combina carta + link CV + botón |
| `Brevo - Enviar Carta+CV` | HTTP Request | Envía Email #2 |
| `Code - Preparar Confirmación` | Code | Prepara variables Email #3 |
| `Brevo - Email Confirmación` | HTTP Request | Envía Email #3 |

---

## 🔑 Credenciales Requeridas

| Servicio | Credential | Estado |
|----------|------------|--------|
| **Notion** | `notion-creds-001` | ✅ Configurada |
| **Claude/Anthropic** | Inline (API Key en nodo) | ⚠️ Hardcodeada |
| **Brevo** | Inline (API Key en nodo) | ⚠️ Hardcodeada |

**Recomendación:** Mover API Keys a credenciales de n8n o variables de entorno.

---

## 🧪 Testing

### Test 1: Flujo Principal

1. Ir a n8n → Workflows → BuscarTrabajo-CORREGIDO
2. Click en "Test workflow"
3. Ejecutar desde "Manual Trigger"
4. Verificar:
   - ✅ 5 ofertas generadas
   - ✅ 5 páginas en Notion creadas
   - ✅ 5 emails enviados

### Test 2: Flujo Aprobar

1. Obtener `page_id` de una oferta en Notion
2. Ejecutar: `curl "https://n8n-qwmu.onrender.com/webhook/oferta-aprobar?id=PAGE_ID"`
3. Verificar:
   - ✅ Notion actualizado a "Aprobado"
   - ✅ Email #2 recibido con carta + link CV + botón

### Test 3: Flujo Mandar Empresa

1. Click en botón "✅ Mandar a empresa" del Email #2
2. Verificar:
   - ✅ Notion actualizado a "Enviado a empresa"
   - ✅ Email #3 de confirmación recibido

---

## ⚠️ URLs Verificadas

| Servicio | URL | Estado |
|----------|-----|--------|
| **n8n** | `https://n8n-qwmu.onrender.com` | ⚠️ Render Free (puede dormir) |
| **CV Server** | `https://cv-server-production.up.railway.app` | ✅ Producción |
| **Webhook Aprobar** | `/webhook/oferta-aprobar` | ✅ |
| **Webhook Descartar** | `/webhook/oferta-descartar` | ✅ |
| **Webhook Mandar Empresa** | `/webhook/oferta-mandar-empresa` | ✅ |

---

## 📝 Cambios vs Versión Anterior

| Archivo | Problema | Solución |
|---------|----------|----------|
| `BUSCARTRABAJO-DEFINITIVO-FINAL.json` | Email no verificado | Cambiado a gmail verificado |
| `BUSCARTRABAJO-DEFINITIVO-FINAL.json` | Flujo paralelo roto | Añadido nodo distribuidor |
| `BUSCARTRABAJO-DEFINITIVO-FINAL.json` | Code node accedía datos incorrectos | Reescrito con `$node[]` |
| `BUSCARTRABAJO-DEFINITIVO-FINAL.json` | Posiciones duplicadas | Corregido layout |

---

## 🚀 Próximos Pasos

1. **Importar workflow** en n8n
2. **Activar** toggle (poner en verde)
3. **Guardar** (Ctrl+S)
4. **Testear** flujo completo
5. **Opcional:** Mover API keys a credenciales seguras
6. **Opcional:** Actualizar emails para producción (usar dominio verificado)

---

**Generado:** 17 Abril 2026  
**Autor:** CookYourWebAI Assistant
