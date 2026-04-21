# Workflow Corregido - BuscarTrabajo-EMAILS-FIXED

## Cambios Realizados

### Problema Principal: El segundo email no se enviaba

**Causa raíz**: El nodo "Code - Preparar Email Carta" intentaba acceder a datos de Notion usando `$('HTTP Request4...')`, pero esta referencia no siempre funciona correctamente en tiempo de ejecución porque:
1. El nodo anterior es "HTTP Request3 - Generar Carta" (Claude API)
2. `$input.first()` devuelve la respuesta de Claude, no de Notion
3. `$('HTTP Request4...')` es una referencia global que puede fallar

### Solución Implementada

#### 1. Nuevo Nodo: "Set - Preparar Datos Email"

**Antes del nodo de código**, añadimos un nodo **Set** que extrae y combina los datos necesarios:

- Datos de Notion (de HTTP Request4): empresa, puesto, salario, modalidad
- Respuesta de Claude (de HTTP Request3): la carta generada
- Output: un objeto JSON consolidado con todos los datos para el email

#### 2. Nodo "Code - Preparar Email Carta" Corregido

```javascript
// Ahora recibe datos consolidados del nodo Set anterior
const inputData = $input.first().json;

// Extraer carta de la respuesta de Claude (validando estructura)
const cartaResponse = inputData.carta_response;
let cartaTexto = '';

if (cartaResponse && cartaResponse.content && cartaResponse.content[0] && cartaResponse.content[0].text) {
  cartaTexto = cartaResponse.content[0].text;
} else if (cartaResponse && cartaResponse.content) {
  // Fallback: buscar texto en cualquier posición
  const textItem = cartaResponse.content.find(item => item.text);
  if (textItem) cartaTexto = textItem.text;
}

// Extraer datos de Notion (ya disponibles en input)
const empresa = inputData.empresa || 'Empresa';
const puesto = inputData.puesto || 'Puesto';

// Preparar body para Brevo
const brevoBody = {
  sender: {name: 'Verónica Serna', email: 'veronica@usecookyourwebai.es'},
  to: [{email: 'hello.cookyourweb@gmail.com'}],
  subject: '📝 Carta de Presentación Generada - ' + empresa,
  htmlContent: `<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
    <h1 style="color: #1F5C8B;">Carta de Presentación Generada</h1>
    <p><strong>Empresa:</strong> ${empresa}</p>
    <p><strong>Puesto:</strong> ${puesto}</p>
    <hr style="margin: 20px 0;">
    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; line-height: 1.6;">
      ${cartaTexto.replace(/\\n/g, '<br>')}
    </div>
    <hr style="margin: 20px 0;">
    <p style="color: #666; font-size: 12px;">Generado automáticamente por CookYourWebAI</p>
  </div>`
};

return [{
  json: {
    brevoBody: brevoBody,
    cartaTexto: cartaTexto,
    empresa: empresa,
    puesto: puesto
  }
}];
```

#### 3. HTTP Request6 - Email Carta (Formato Raw)

Cambiado de `specifyBody: "json"` a `contentType: "raw"` para evitar problemas de escape:

```json
{
  "parameters": {
    "method": "POST",
    "url": "https://api.brevo.com/v3/smtp/email",
    "sendHeaders": true,
    "headerParameters": {
      "parameters": [
        {"name": "api-key", "value": "xkeysib-..."},
        {"name": "Content-Type", "value": "application/json"}
      ]
    },
    "sendBody": true,
    "contentType": "raw",
    "rawContentType": "application/json",
    "body": "={{ JSON.stringify($json.brevoBody) }}"
  }
}
```

### Flujo Corregido

```
WebhookAprovado
    ↓
HTTP Request1 - PATCH Notion → "Aprobado"
    ↓
HTTP Request4 - GET Notion → Obtiene datos completos
    ↓
HTTP Request3 - Claude API → Genera carta
    ↓
[NEW] Set - Preparar Datos Email → Combina datos de Notion + Carta
    ↓
Code - Preparar Email Carta → Prepara body para Brevo
    ↓
HTTP Request6 - Email Carta → ENVÍA SEGUNDO EMAIL ✅
    ↓
CV Server - Generar CV
    ↓
Code - Preparar Email CV Final
    ↓
HTTP Request7 - Email CV Final → ENVÍA TERCER EMAIL
```

---

## Nodo Set - Configuración

```json
{
  "parameters": {
    "mode": "manual",
    "fields": {
      "values": [
        {
          "name": "empresa",
          "value": "={{ $json.properties.Empresa.title[0].text.content }}"
        },
        {
          "name": "puesto", 
          "value": "={{ $json.properties.Puesto.rich_text[0].text.content }}"
        },
        {
          "name": "salario",
          "value": "={{ $json.properties.Salario?.rich_text[0]?.text?.content || 'No especificado' }}"
        },
        {
          "name": "modalidad",
          "value": "={{ $json.properties.Modalidad?.select?.name || 'No especificado' }}"
        },
        {
          "name": "descripcion",
          "value": "={{ $json.properties.Notas?.rich_text[0]?.text?.content || '' }}"
        }
      ]
    }
  }
}
```

---

## Archivo Corregido

El archivo `BUSCARTRABAJO-EMAILS-FIXED.json` contiene:

1. ✅ Nuevo nodo "Set - Preparar Datos Email" entre HTTP Request3 y Code
2. ✅ Nodo Code corregido con validación de respuesta Claude
3. ✅ HTTP Request6 cambiado a formato raw
4. ✅ Conexiones actualizadas para el flujo secuencial

---

## Instrucciones de Importación

1. Ve a n8n: `https://n8n-qwmu.onrender.com`
2. Workflows → Import from File
3. Selecciona `BUSCARTRABAJO-EMAILS-FIXED.json`
4. Activa el workflow (toggle verde)
5. Guarda: Ctrl+S

---

## Prueba Recomendada

1. Crea una oferta de prueba manualmente en Notion (estado: "Enviado")
2. Obtén el page_id
3. Ejecuta: `curl "https://n8n-qwmu.onrender.com/webhook/approve?id=PAGE_ID"`
4. Verifica en n8n: Execution log debería mostrar todos los nodos verdes
5. Revisa bandeja de entrada: deberías recibir 2 emails seguidos:
   - Email 2: Carta de presentación
   - Email 3: Carta + Link CV

---

## Si Aún Falla

Si el email 2 sigue sin enviarse:

1. **Revisa el nodo Set**: Asegúrate que los campos `empresa` y `puesto` se estén extrayendo correctamente de HTTP Request4
2. **Revisa logs de ejecución**: Ve a Executions → la ejecución fallida → expande cada nodo para ver qué data recibe
3. **Verifica formato de Claude**: La respuesta de Claude debería tener `content[0].text` - si es diferente, ajusta el código
4. **Prueba HTTP Request6 manual**: Copia el body generado por el nodo Code y pruébalo directamente en Brevo API
