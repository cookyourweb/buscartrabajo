# Cambios Recientes en Workflow n8n - BUSCARTRABAJO-DEFINITIVO-FINAL.json

> **Fecha:** 2026-04-17  
> **Propósito:** Documentar reestructuración del flujo "Mandar a Empresa" para próxima sesión

---

## Resumen del Cambio

Se reestructuró el flujo del webhook `/mandar-empresa` para ejecutar en paralelo la actualización de Notion y el envío del email de confirmación.

---

## Flujo ANTES (Problemático)

```
Webhook Mandar Empresa
       │
       ▼
Notion - Marcar Enviado a empresa
       │
       ▼
Code - Preparar Confirmación
       │
       ▼
Brevo - Email Confirmación
```

**Problema:** El nodo "Notion - Marcar Enviado a empresa" hacía un PATCH a Notion y su salida reemplazaba los datos originales del webhook. El nodo "Code - Preparar Confirmación" no recibía los datos correctos (`properties`, `id`, etc.).

---

## Flujo DESPUÉS (Corregido)

```
Webhook Mandar Empresa
       │
       ├─────────────────────────────┐
       │                             │
       ▼ (index 0)                   ▼ (index 1)
Notion - Marcar Enviado a empresa   Code - Preparar Confirmación
       │                             │
       │ (terminal)                  ▼
       │                      Brevo - Email Confirmación
```

**Ventaja:** Ambos nodos reciben los datos originales del webhook directamente.

---

## Cambios Específicos Realizados

### 1. Conexiones del Webhook (línea ~354)

**ANTES:**
```json
"Webhook Mandar Empresa": {"main": [[{"node": "Notion - Marcar Enviado a empresa", "type": "main", "index": 0}]]}
```

**DESPUÉS:**
```json
"Webhook Mandar Empresa": {"main": [[{"node": "Notion - Marcar Enviado a empresa", "type": "main", "index": 0}, {"node": "Code - Preparar Confirmación", "type": "main", "index": 1}]]}
```

### 2. Conexión de "Notion - Marcar Enviado a empresa" (línea ~360)

**ANTES:**
```json
"Notion - Marcar Enviado a empresa": {"main": [[{"node": "Code - Preparar Confirmación", "type": "main", "index": 0}]]}
```

**DESPUÉS:**
```json
"Notion - Marcar Enviado a empresa": {"main": [[]]}
```

### 3. Código del nodo "Code - Preparar Confirmación" (líneas ~223)

**ANTES:**
```javascript
const pageId = $input.first().json.query.id;
const empresa = $input.first().json.properties?.Empresa?.title?.[0]?.text?.content || '';
const puesto = $input.first().json.properties?.Puesto?.rich_text?.[0]?.text?.content || '';
```

**DESPUÉS:**
```javascript
const webhookData = $input.first().json;
const pageId = webhookData.query?.id || webhookData.id || '';
const empresa = webhookData.properties?.Empresa?.title?.[0]?.text?.content || '';
const puesto = webhookData.properties?.Puesto?.rich_text?.[0]?.text?.content || '';
```

**Cambio clave:** Se añade fallback `webhookData.id` por si el ID viene en la raíz en lugar de `query.id`.

---

## Nodos Involucrados

| Nodo | ID | Tipo | Función |
|------|-----|------|---------|
| Webhook Mandar Empresa | `webhook-mandar-empresa-001` | `n8n-nodes-base.webhook` | Recibe POST `/mandar-empresa?id=<pageId>` |
| Notion - Marcar Enviado a empresa | `notion-mandar-empresa-001` | `n8n-nodes-base.httpRequest` | PATCH a Notion para cambiar Estado |
| Code - Preparar Confirmación | `code-prepara-confirmacion-001` | `n8n-nodes-base.code` | Extrae empresa, puesto, pageId |
| Brevo - Email Confirmación | `brevo-confirmacion-001` | `n8n-nodes-base.httpRequest` | POST a API Brevo para enviar email |

---

## Testing Pendiente

Para la próxima sesión, verificar:

1. **Activar el workflow** en n8n UI (cambiado a `active: false`)
2. **Testear webhook** con POST a `/mandar-empresa?id=<pageId>`
3. **Verificar en Notion** que el Estado cambia a "Enviado a empresa"
4. **Verificar email** de confirmación llega a `hello.cookyourweb@gmail.com`
5. **Chequear logs** de n8n para errores en paralelo

---

## Próximos Pasos

1. ✅ ~~Documentar cambios~~ (este archivo)
2. ⏳ Revisar errores pendientes del workflow
3. ⏳ Activar workflow en n8n
4. ⏳ Ejecutar test end-to-end
5. ⏳ Monitorear primeras ejecuciones

---

## Errores Conocidos a Revisar

- Verificar que el webhook está recibiendo datos correctamente
- Confirmar que las credenciales de Brevo y Notion están vigentes
- Validar que el paralelo de conexiones no causa race conditions

---

## Referencias

- Archivo workflow: `BUSCARTRABAJO-DEFINITIVO-FINAL.json`
- Skill usada: `n8n-workflow-patterns`, `n8n-code-javascript`
- Patrón aplicado: Webhook Processing con ejecución paralela
