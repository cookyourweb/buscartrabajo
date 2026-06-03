# 🚀 INSTRUCCIONES PARA PROBAR EL WORKFLOW

## Configuración Actual: MODO TEST

El workflow está configurado para ejecutarse **CADA MINUTO** para facilitar las pruebas.

---

## 📋 Checklist antes de probar

- [ ] Importar workflow en N8N
- [ ] Configurar credencial de Notion
- [ ] Verificar que CV Server está funcionando
- [ ] Verificar API keys de Claude y Brevo
- [ ] Cambiar email destinatario si es necesario

---

## 🔧 Paso 1: Importar en N8N

1. Ve a: `https://n8n-qwmu.onrender.com`
2. Login con tus credenciales
3. Click en **"Add Workflow"** (o "Import from File")
4. Selecciona: `BUSCARTRABAJO-2-EMAILS.json`

---

## 🔧 Paso 2: Configurar Credenciales

### Notion API:
1. Ve a Settings (rueda dentada) → Credentials
2. Click "Add Credential"
3. Selecciona "Notion API"
4. Introduce tu token: `REEMPLAZAR_POR_TU_NOTION_TOKEN`

### Brevo API:
El workflow ya tiene la API key incluida:
`REEMPLAZAR_POR_TU_BREVO_API_KEY`

### Claude API:
La API key ya está incluida en los nodos HTTP Request

---

## 🧪 Paso 3: Probar el Flujo

### Opción A: Ejecución Manual (Recomendado para primera prueba)

1. En el workflow, haz click en **"Execute Workflow"** (botón naranja arriba a la derecha)
2. Espera 10-20 segundos
3. Revisa tu email: deberías recibir el **Email 1** con la oferta

### Opción B: Esperar al Schedule (Automático)

El workflow se ejecutará **cada minuto** automáticamente.

---

## 📧 Paso 4: Probar el Botón Aprobar

1. Recibe el Email 1 en tu bandeja
2. Haz click en el botón **VERDE "Aprobar"**
3. Espera 30-60 segundos
4. Revisa tu email: deberías recibir el **Email 2** con:
   - Carta de presentación completa
   - Botón para descargar CV de Google Drive

---

## 📧 Paso 5: Probar el Botón Descartar

1. Espera al siguiente email de oferta (o ejecuta manualmente)
2. Haz click en el botón **ROJO "Descartar"**
3. Verifica en Notion que el estado cambió a "Descartado"
4. No deberías recibir más emails sobre esa oferta

---

## 🔄 Cambiar a Modo Producción (2 veces al día)

Cuando todo funcione, cambia el schedule:

1. Ve al nodo: **"Schedule Trigger (cada minuto - TEST)"**
2. Click en el nodo → "Edit"
3. Cambia la configuración:
   ```
   Mode: Trigger at specific time
   Trigger at Hour: 9
   ```
4. Para 2 veces al día, duplica el nodo y pon uno a las 9 y otro a las 18

---

## 🐛 Solución de Problemas

### No llega el email 1:
- Verifica spam/promociones
- Revisa logs del workflow en N8N
- Verifica que la API key de Brevo es correcta

### No llega el email 2 al aprobar:
- Verifica que el webhook está activo
- Prueba la URL directamente: `https://n8n-qwmu.onrender.com/webhook/aprobar?id=test`
- Revisa logs de ejecución del webhook

### El CV no se genera:
- Verifica que CV Server está funcionando:
  ```bash
  curl https://cv-server-production.up.railway.app/generar-cv \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"empresa":"Test","puesto":"Test","descripcion":"Test"}'
  ```

### Error en Notion:
- Verifica que el Database ID es correcto: `33d11515-f4b2-81ef-a776-d0ea698b748f`
- Verifica que el token de Notion tiene permisos sobre esa database

---

## 📊 Qué verificar en cada prueba

| Paso | Verificación | Dónde |
|------|--------------|-------|
| 1 | Ofertas generadas | Email 1 recibido |
| 2 | Datos en Notion | Notion → Database "Ofertas" |
| 3 | Webhook funciona | Al hacer click en Aprobar |
| 4 | Carta generada | Email 2 → Contenido de la carta |
| 5 | CV generado | Email 2 → Link funciona |
| 6 | Estado actualizado | Notion → Estado = "Aprobado" |

---

## ✅ Sign-off Checklist

Cuando todo funcione, marca:

- [ ] Email 1 llega correctamente
- [ ] Botones Aprobar/Descartar funcionan
- [ ] Email 2 llega con carta y CV
- [ ] Link del CV funciona y descarga el archivo
- [ ] Estados en Notion se actualizan correctamente
- [ ] Flujo Descartar funciona (sin emails adicionales)

---

**¿Todo funciona?** Cambia el schedule a producción (9am y 6pm) y desactiva el manual trigger.
