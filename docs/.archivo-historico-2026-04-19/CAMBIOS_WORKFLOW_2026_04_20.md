# Cambios en Workflow BuscarTrabajo - 2026-04-20

## Resumen

Se corrigió el workflow `BuscarTrabajo-cvservrok.json` para guardar correctamente los datos de contacto de reclutadores en Notion y mostrarlos en los emails.

---

## Problema Original

El workflow fallaba al crear ofertas en Notion con el error:

```
body failed validation. Fix one: 
body.properties.Email Contacto Empresa.title should be defined...
body.properties.Email Contacto Empresa.email should be populated or null, instead was ""
```

**Causa raíz:** Los nombres de campos en el workflow no coincidían con el schema real de la database de Notion.

---

## Schema Real de Notion (verificado vía API)

| Campo | Tipo | Estado |
|-------|------|--------|
| `Empresa` | title | ✅ Existía |
| `Puesto` | rich_text | ✅ Existía |
| `Salario` | rich_text | ✅ Existía |
| `Modalidad` | select | ✅ Existía |
| `Link oferta` | url | ✅ Existía |
| `Notas` | rich_text | ✅ Existía |
| `Estado` | select | ✅ Existía |
| `Email empresa` | email | ✅ Existía |
| `Link CV Drive` | url | ✅ Existía |
| `CV usado` | rich_text | ✅ Existía |
| `Fecha envio` | date | ✅ Existía |
| `Seguimiento` | date | ✅ Existía |
| `Nombre Contacto` | rich_text | ❌ **No existía** |
| `Teléfono Contacto` | phone_number | ❌ **No existía** |

---

## Cambios Realizados

### 1. Campos añadidos a Notion

Se ejecutó script `add_notion_fields.py` para añadir:
- `Nombre Contacto` (rich_text)
- `Teléfono Contacto` (phone_number)

### 2. Nodos del workflow corregidos

#### Nodo: `Notion - Crear Oferta` (línea ~82-143)
**Antes:**
```javascript
{
  "key": "Email Contacto Empresa|email",
  "textContent": "={{ $json.email_contacto }}"
}
```

**Después:**
```javascript
{
  "key": "Nombre Contacto|rich_text",
  "textContent": "={{ $json.nombre_contacto || '' }}"
},
{
  "key": "Teléfono Contacto|phone_number",
  "phoneNumber": "={{ $json.telefono_contacto || '' }}"
},
{
  "key": "Email empresa|email",
  "emailValue": "={{ $json.email_contacto || null }}"
}
```

#### Nodo: `Claude - Generar Ofertas` (línea ~55)
**Antes:**
```javascript
"model": "claude-sonnet-4-6"  // ❌ Sin fecha → error 400/404
```

**Después:**
```javascript
"model": "claude-sonnet-4-6-20260217"  // ✅ Con fecha
```

**Prompt actualizado:**
```
"Genera una lista de 5 ofertas... inventa un contacto de RRHH o hiring manager 
realista con nombre completo, email corporativo y teléfono español (+34). 
...con estos campos por oferta: empresa, puesto, salario, modalidad, link, 
descripcion_corta, nombre_contacto, email_contacto, telefono_contacto"
```

#### Nodo: `Code - Normalizar Modalidad` (línea ~70)
**Antes:** Solo pasaba `nombre_contacto` y `email_contacto`

**Después:** También pasa `telefono_contacto`

#### Nodo: `Code - Preparar Email Notificacion` (línea ~179)
**Antes:** Solo leía campos básicos de Notion

**Después:** También lee:
```javascript
nombreContacto: d.properties?.['Nombre Contacto']?.rich_text?.[0]?.text?.content || '',
emailContacto: d.properties?.['Email empresa']?.email || '',
telefonoContacto: d.properties?.['Teléfono Contacto']?.phone_number || ''
```

#### Nodo: `Brevo - Enviar Notificacion` (línea ~210)
**Antes:** Email sin datos de contacto

**Después:** Incluye sección de contacto:
```html
<div style="background:#f9f9f9;padding:16px;border-radius:6px;margin:16px 0">
  <h3 style="color:#1F5C8B;margin-top:0">📧 Contacto en la empresa</h3>
  <p><strong>Nombre:</strong> {{nombreContacto}}</p>
  <p><strong>Email:</strong> {{emailContacto}}</p>
  <p><strong>Teléfono:</strong> {{telefonoContacto}}</p>
</div>
```

#### Nodo: `Code - Preparar Email Carta+CV` (línea ~575)
**Antes:** Solo usaba `emailContacto`

**Después:** Usa `nombreContacto`, `emailContacto`, `telefonoContacto`

#### Nodo: `Notion - Guardar Link CV` (línea ~643)
**Antes:** Guardaba solo `Email empresa` y `CV usado`

**Después:** También guarda:
```javascript
"Nombre Contacto": { rich_text: [{ text: { content: $json.nombreContacto || '' } }] },
"Teléfono Contacto": { phone_number: $json.telefonoContacto || null },
```

#### Nodo: `Code - Preparar Confirmación` (línea ~368)
**Antes:** Solo leía `emailContacto`

**Después:** Lee los 3 campos de contacto

#### Nodo: `Brevo - Email Confirmación` (línea ~675)
**Antes:** Solo mostraba email de contacto

**Después:** Muestra nombre, email y teléfono (si existen)

---

## Flujo Actualizado

### Flujo 1: Generación Diaria (9am)

```
Schedule Trigger → Claude (5 ofertas con nombre/email/teléfono) 
  → Code normalizar → Notion crear (guarda contacto completo) 
  → Notion obtener → Code preparar email → Brevo enviar (muestra contacto)
```

### Flujo 2: Aprobar Oferta

```
Webhook Aprobar → Notion (Aprobado → En proceso) 
  → Notion obtener datos → Claude (carta) → CV Server (CV) 
  → Code preparar email (lee contacto completo de Notion) 
  → Brevo enviar (muestra contacto) → Notion guardar (actualiza contacto)
```

### Flujo 3: Mandar a Empresa

```
Webhook Mandar → Notion (Enviado a empresa) 
  → Notion obtener → Code preparar (lee contacto completo) 
  → Brevo confirmar (muestra contacto completo)
```

---

## Archivos Modificados

| Archivo | Cambios |
|---------|---------|
| `BuscarTrabajo-cvservrok.json` | 10 nodos corregidos |
| `add_notion_fields.py` | Nuevo script para añadir campos |

---

## Testing Pendiente

1. **Ejecutar workflow manualmente** desde n8n UI
2. **Verificar que se crean ofertas** en Notion con datos de contacto
3. **Verificar emails** que llegan con datos de contacto completos
4. **Probar flujo aprobar** → genera carta + CV + guarda contacto
5. **Probar flujo mandar empresa** → email confirmación con contacto

---

## Notas Importantes

1. **Modelo de Claude:** Siempre usar formato con fecha (`claude-sonnet-4-6-20260217`)
2. **Campos de Notion:** Usar nombres exactos (`Email empresa`, no `Email Contacto Empresa`)
3. **Webhook data:** En nodos Code, acceder vía `$json.body` si viene de webhook
4. **Continue on fail:** Nodos críticos mantienen esta opción para no bloquear flujo
5. **Referencias entre nodos:** Usar `$('Nombre Nodo').first().json` para leer datos de nodos anteriores

## Bug Fix Adicional (2026-04-20)

**Problema:** Nodo `Claude - Generar Carta` fallaba al leer datos de Notion.

**Causa:** El nodo intentaba leer `$json.properties.Empresa.title[0].text.content` pero los datos venían del nodo anterior (`Notion - Marcar En Proceso`) que no devuelve la estructura completa de Notion.

**Solución:** Cambiar la expresión para leer directamente del nodo que obtiene los datos:

```javascript
// Antes (incorrecto):
$json.properties.Empresa.title[0].text.content

// Después (correcto):
$('Notion - Obtener Datos Oferta').first().json.properties.Empresa.title[0].text.content
```

---

## Próximo Paso

Importar el workflow actualizado en n8n:

1. Ir a `https://n8n-qwmu.onrender.com`
2. Workflows → Import from File
3. Seleccionar `BuscarTrabajo-cvservrok.json`
4. Activar toggle (debe estar VERDE)
5. Ejecutar manualmente para testear
