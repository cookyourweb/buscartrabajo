# Workflow Corregido - Instrucciones de Implementación

## 📁 Archivo Corregido

**Nombre:** `BUSCARTRABAJO-FINAL-FIXED.json`

## 🔧 Cambios Realizados

### 1. Estructura Secuencial Corregida

El flujo ahora sigue el orden correcto:

```
WebhookAprovado
    ↓
HTTP Request1 (PATCH Notion → "Aprobado")
    ↓
HTTP Request4 (GET Notion → Datos completos)
    ↓
HTTP Request3 (Claude API → Genera carta)  ← NUEVO: Ahora es secuencial
    ↓
Code - Preparar Email Carta  ← NUEVO: Nodo que faltaba
    ↓
HTTP Request6 - Email Carta  ← NUEVO: Envía email con carta
    ↓
CV Server - Generar CV  ← AHORA: Espera al email anterior
    ↓
Code - Preparar Email CV Final
    ↓
HTTP Request7 - Email CV Final
```

### 2. Nodos Agregados

| Nodo | Propósito |
|------|-----------|
| `Code - Preparar Email Carta` | Prepara el body del email con la carta de presentación |
| `HTTP Request6 - Email Carta` | Envía el email con la carta a Brevo |
| `HTTP Request7 - Email CV Final` | Envía el email final con carta + link al CV |

### 3. Nodos Renombrados para Claridad

| Antes | Después |
|-------|---------|
| `HTTP Request3` | `HTTP Request3 - Generar Carta` |
| `HTTP Request4` | `HTTP Request4 - Obtener Datos` |
| `HTTP Request5` | `HTTP Request5 - Email Notificacion` |
| `CV Server` | `CV Server - Generar CV` |

### 4. Flujo Paralelo Eliminado

**Antes (roto):**
```
HTTP Request4 ─┬─→ HTTP Request3 ──→ Preparar email CV
               └─→ CV Server ──────→ (en paralelo, sin esperar)
```

**Después (corregido):**
```
HTTP Request4 → HTTP Request3 → Preparar Email Carta → Email Carta → CV Server → ...
```

## 📥 Cómo Importar el Workflow

### Paso 1: Acceder a n8n
1. Ve a `https://n8n-qwmu.onrender.com`
2. Inicia sesión con tus credenciales

### Paso 2: Importar el Workflow
1. Ve a **Workflows**
2. Click en **"Import from File"**
3. Selecciona `BUSCARTRABAJO-FINAL-FIXED.json`
4. El workflow se llamará "BuscarTrabajo-FINAL-FIXED"

### Paso 3: Activar el Workflow
1. Abre el workflow importado
2. Click en el toggle **"Active"** (esquina superior derecha)
3. Debe ponerse VERDE
4. Guarda: `Ctrl+S` o `File → Save`

## 🧪 Pruebas Recomendadas

### Test 1: Flujo de Notificación (9:00 AM)
```bash
# Ejecutar manualmente desde el nodo "Schedule Trigger"
# Debería:
# ✅ Generar 5 ofertas con Claude
# ✅ Crear 5 páginas en Notion (estado: Enviado)
# ✅ Enviar 5 emails con botones Aprobar/Descartar
```

### Test 2: Flujo Aprobar (Webhooks)
```bash
# Obtener un page_id de Notion de una oferta en estado "Enviado"

# Probar webhook de aprobar:
curl "https://n8n-qwmu.onrender.com/webhook/approve?id=PAGE_ID_AQUI"

# Debería:
# ✅ Actualizar Notion a "Aprobado"
# ✅ Generar carta con Claude
# ✅ Enviar Email #2 (Carta de presentación) ← ESTE FALTABA
# ✅ Generar CV con CV Server
# ✅ Enviar Email #3 (Carta + Link CV)
```

### Test 3: Flujo Descartar
```bash
# Probar webhook de descartar:
curl "https://n8n-qwmu.onrender.com/webhook/reject?id=PAGE_ID_AQUI"

# Debería:
# ✅ Actualizar Notion a "Descartado"
```

## 📧 Flujo de Emails Completo

| # | Momento | Asunto | Contenido |
|---|---------|--------|-----------|
| **1** | 9:00 AM | `🤖 Nueva oferta: [Empresa] - [Puesto]` | Datos + botones Aprobar/Descartar |
| **2** | Tras aprobar | `📝 Carta de Presentación Generada - [Empresa]` | **NUEVO:** Solo la carta |
| **3** | Tras generar CV | `✅ Oferta lista: [Empresa] - [Puesto]` | Carta + Link al CV en Drive |

## ⚠️ Verificación de Credenciales

Antes de probar, verifica que estas credenciales estén configuradas en n8n:

### 1. Notion API
- **Token:** `REEMPLAZAR_POR_TU_NOTION_TOKEN`
- **Database ID:** `33d11515-f4b2-81ef-a776-d0ea698b748f`

### 2. Claude API (Anthropic)
- **API Key:** `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`

### 3. Brevo (Email)
- **API Key:** `REEMPLAZAR_POR_TU_BREVO_API_KEY`

### 4. CV Server
- **URL:** `https://cv-server-production.up.railway.app/generar-cv`

## 🔍 Debugging

Si algo falla, revisa en este orden:

1. **Revisa los logs de n8n:**
   - Ve a la pestaña "Executions"
   - Busca la ejecución fallida
   - Revisa nodo por nodo

2. **Verifica que el workflow esté activo:**
   - El toggle debe estar VERDE
   - Si está gris, actívalo y guarda

3. **Prueba los webhooks manualmente:**
   ```bash
   curl -v "https://n8n-qwmu.onrender.com/webhook/approve?id=test"
   # Debe devolver algo, no 404
   ```

4. **Verifica los servicios externos:**
   ```bash
   # CV Server
   curl -X POST https://cv-server-production.up.railway.app/generar-cv \
     -H "Content-Type: application/json" \
     -d '{"empresa":"Test","puesto":"Dev","descripcion":"test"}'
   ```

## 🎯 Estado del Fix

- [x] Nodo "Code - Preparar Email Carta" agregado
- [x] Nodo "HTTP Request6 - Email Carta" agregado
- [x] Flujo secuencial implementado (ya no es paralelo)
- [x] Conexiones corregidas
- [x] Nombres de nodos claros
- [ ] Testing en producción
- [ ] Verificación de emails

## 📞 Próximos Pasos

1. Importar el workflow corregido
2. Activarlo
3. Ejecutar prueba manual del flujo principal
4. Crear una oferta de prueba y hacer click en "Aprobar"
5. Verificar que lleguen los 3 emails:
   - Email de notificación inicial
   - Email con carta de presentación
   - Email con CV final

---

**Fecha de corrección:** 15 Abril 2026
**Archivo:** BUSCARTRABAJO-FINAL-FIXED.json
