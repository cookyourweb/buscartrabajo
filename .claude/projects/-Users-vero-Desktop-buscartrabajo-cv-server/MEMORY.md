# Memoria del Proyecto - BuscarTrabajo

## Estado Actual (20 Abril 2026)

### Workflow Activo
- **Archivo:** `BuscarTrabajo-cvservrok.json`
- **Estado:** ✅ En producción
- **Ubicación:** `/Users/vero/Desktop/buscartrabajo/BuscarTrabajo-cvservrok.json`

### CV Server
- **Archivo:** `cv-server/cv_server_railway.py`
- **URL Producción:** `https://cv-server-production.up.railway.app`
- **Mejoras aplicadas:**
  - Prompt Claude mejorado: sin cabecera, formato plano
  - DOCX profesional con cabecera fija
  - Formato limpio: Calibri, líneas azules, bullets •

### URLs Importantes
| Servicio | URL |
|----------|-----|
| N8N | `https://n8n-qwmu.onrender.com` |
| CV Server | `https://cv-server-production.up.railway.app` |
| Webhook Aprobar | `/webhook/oferta-aprobar?id=PAGE_ID` |
| Webhook Descartar | `/webhook/oferta-descartar?id=PAGE_ID` |
| Webhook Mandar | `/webhook/oferta-mandar-empresa?id=PAGE_ID` |

### Base de Datos Notion
- **Database ID:** `33d11515-f4b2-81ef-a776-d0ea698b748f`
- **Estados:** Pendiente → Aprobado → En proceso → Enviado a empresa / Descartado

### Emails
1. 🤖 Nueva oferta (9:00 AM) - con botones ✅/❌
2. 📝 Carta + CV - con botón Mandar
3. ✅ Aplicado a empresa - confirmación

### Pendientes
- [ ] Verificar emails llegan correctamente
- [ ] Test completo del flujo aprobar
