# Guía de Configuración - BuscarTrabajo-FINAL-LIMPIO

## Cambios Realizados

### 1. Webhooks Actualizados (Evita Conflictos)
- `aprobar` → `aprobar-v2`
- `descartar` → `descartar-v2`

### 2. Código Python en Nodos Code
- Nodo "Normalizar Modalidad" ahora usa Python (importa `json` y `re`)
- Nodo "Combinar Carta y CV" ahora usa Python
- Ambos usan sintaxis `_input`, `_node` de n8n Python Beta

### 3. URLs de Webhooks Actualizadas
- Email ahora apunta a `/webhook/aprobar-v2` y `/webhook/descartar-v2`

### 4. Schedule Corregido
- Antes: cada minuto (`*/1 * * * *`)
- Ahora: todos los días a las 9:00 AM (`0 9 * * *`)

---

## Instrucciones de Importación

### Paso 1: Importar el Workflow
1. Abre n8n: `https://n8n-qwmu.onrender.com`
2. Ve a **Workflows** → **Import from File**
3. Selecciona `BUSCARTRABAJO-FINAL-LIMPIO.json`
4. El workflow se llamará "BuscarTrabajo-FINAL-LIMPIO"

### Paso 2: Configurar Credenciales (IMPORTANTE)

⚠️ **Las API keys están en el JSON - muevelas a credentials de n8n:**

#### Anthropic API (Claude)
1. Ve a **Settings** → **Credentials**
2. Crea nueva credencial tipo **HTTP Header Auth**
3. Guarda la API key allí y referenciala en el nodo

#### Notion
1. Crea credencial tipo **Notion API**
2. Usa el token existente: `REEMPLAZAR_POR_TU_NOTION_TOKEN`

#### Brevo
1. Crea credencial tipo **HTTP Header Auth**
2. Guarda el API key de Brevo

### Paso 3: Verificar Base de Datos Notion

La base de datos debe tener estas columnas:
- **Empresa** (Title)
- **Puesto** (Text/Rich Text)
- **Salario** (Text/Rich Text)
- **Modalidad** (Select: Remoto/Hibrido/Presencial)
- **Link oferta** (URL)
- **Notas** (Text/Rich Text)
- **Estado** (Select: Pendiente/Aprobado/Descartado)

ID de base de datos en el workflow: `33d11515-f4b2-81ef-a776-d0ea698b748f`

### Paso 4: Verificar CV Server

El CV Server está en: `https://cv-server-production.up.railway.app/generar-cv`

Asegúrate de que esté funcionando:
```bash
curl https://cv-server-production.up.railway.app/generar-cv \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"empresa":"Test","puesto":"Dev","descripcion":"test"}'
```

### Paso 5: Probar el Workflow

#### Test 1: Flujo Principal (Generar Ofertas)
1. Click en "Execute Workflow"
2. Debería:
   - Llamar a Claude API
   - Crear 5 páginas en Notion (estado "Pendiente")
   - Enviar 5 emails con botones Aprobar/Descartar

#### Test 2: Flujo Aprobar
1. En tu email, click en **Aprobar** (botón verde)
2. Debería:
   - Actualizar Notion a "Aprobado"
   - Generar carta con Claude
   - Generar CV via CV Server
   - Enviar email 2 con carta + link CV

#### Test 3: Flujo Descartar
1. En tu email, click en **Descartar** (botón rojo)
2. Debería actualizar Notion a "Descartado"

---

## URLs de Webhooks (para testing manual)

```
# Aprobar
https://n8n-qwmu.onrender.com/webhook/aprobar-v2?id=PAGE_ID_DE_NOTION

# Descartar
https://n8n-qwmu.onrender.com/webhook/descartar-v2?id=PAGE_ID_DE_NOTION
```

Reemplaza `PAGE_ID_DE_NOTION` con el ID de una página de Notion.

---

## Solución de Problemas

### Error: "Cannot read property 'json' of undefined"
- Verifica que el nodo anterior haya ejecutado correctamente
- Revisa la pestaña **Executions** para ver errores detallados

### Error: "No JSON found in response"
- Claude API puede devolver texto mal formateado
- El código Python intenta extraer JSON con regex
- Si falla, retorna error descriptivo

### Error: "ModuleNotFoundError" en Code node
- Solo librería estándar de Python disponible
- Los nodos actuales usan: `json`, `re` (permitidos)

### Emails no llegan
- Verifica que Brevo API key esté activa
- Revisa spam/correo no deseado
- Verifica que el remitente esté verificado en Brevo

### Webhook no responde
- Asegúrate de que el workflow esté **activo** (toggle verde)
- Verifica que no haya conflictos con otros workflows usando webhooks
- Prueba las URLs manualmente en el navegador

---

## Estructura del Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                      FLUJO PRINCIPAL                             │
├─────────────────────────────────────────────────────────────────┤
│ Schedule 9AM → Claude API → Code Python → Notion → Email        │
└─────────────────────────────────────────────────────────────────┘
                                    ↓
                           Email con botones
                                    ↓
┌─────────────────────────────────────────────────────────────────┐
│                      FLUJO APROBAR (webhook)                     │
├─────────────────────────────────────────────────────────────────┤
│ Webhook → Notion (Aprobado) → Notion (Lee datos)              │
│    → Claude (Carta) + CV Server (CV) → Code Python → Email      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      FLUJO DESCARTAR (webhook)                  │
├─────────────────────────────────────────────────────────────────┤
│ Webhook → Notion (Descartado) → Fin                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Código Python en Nodos Code

### Nodo: Normalizar Modalidad
```python
import json
import re

response = _input.first()["json"]
text = response["content"][0]["text"]

json_match = re.search(r'\[\s\S]*\]', text)
if not json_match:
    return [{"json": {"error": "No se encontró JSON"}}]

ofertas = json.loads(json_match.group(0))

result = []
for oferta in ofertas:
    mod = "Presencial"
    m = oferta.get("modalidad", "").lower()
    if "remoto" in m:
        mod = "Remoto"
    elif "hibrido" in m or "híbrido" in m:
        mod = "Hibrido"
    oferta["modalidad"] = mod
    result.append({"json": oferta})

return result
```

### Nodo: Combinar Carta y CV
```python
carta_response = _node["Generar Carta"]["json"]
cv_response = _node["Generar CV"]["json"]
notion_data = _node["Obtener Datos Oferta"]["json"]

empresa = notion_data.get("properties", {}).get("Empresa", {}).get("title", [{}])[0].get("text", {}).get("content", "Empresa Desconocida")
puesto = notion_data.get("properties", {}).get("Puesto", {}).get("rich_text", [{}])[0].get("text", {}).get("content", "Puesto Desconocido")
carta = carta_response.get("content", [{}])[0].get("text", "")
link_cv = cv_response.get("link", "")

return [{"json": {"empresa": empresa, "puesto": puesto, "carta": carta, "linkCV": link_cv}}]
```

---

## Contacto y Soporte

Si tienes problemas:
1. Revisa los logs de ejecución en n8n (pestaña "Executions")
2. Verifica que todos los servicios externos estén funcionando
3. Comprueba que las API keys no hayan expirado
