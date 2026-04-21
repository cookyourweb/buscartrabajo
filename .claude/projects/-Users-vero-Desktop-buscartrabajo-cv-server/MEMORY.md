# Memoria del Proyecto - BuscarTrabajo v2

## Estado Actual (21 Abril 2026)

### Arquitectura v2 - Multi-User
- **2 Workflows separados en n8n:**
  - Workflow 1: `workflow-1-usuarios.json` (11 nodos) - Registro de usuarios
  - Workflow 2: `workflow-2-principal.json` (38 nodos) - Búsqueda diaria + CV + Emails

### CV Server
- **Archivo:** `cv-server/cv_server_railway.py`
- **URL Producción:** `https://cv-server-ggd8.onrender.com`
- **Multi-user:** Lee CV Master según email del usuario desde Notion DB Usuarios

### URLs Importantes
| Servicio | URL |
|----------|-----|
| N8N | `https://n8n-qwmu.onrender.com` |
| CV Server | `https://cv-server-ggd8.onrender.com` |
| Registro | `https://cv-server-ggd8.onrender.com/registro` |
| Health | `https://cv-server-ggd8.onrender.com/health` |
| Debug | `https://cv-server-ggd8.onrender.com/debug` |

### Webhooks n8n
| Webhook | URL |
|---------|-----|
| Nuevo Usuario | `/webhook/nuevo-usuario` |
| Buscar Ahora | `/webhook/buscar-ahora` |
| Buscar Para User (interno) | `/webhook/buscar-para-user` |
| Aprobar | `/webhook/oferta-aprobar?id=PAGE_ID` |
| Descartar | `/webhook/oferta-descartar?id=PAGE_ID` |
| Mandar Empresa | `/webhook/oferta-mandar-empresa?id=PAGE_ID` |

### Bases de Datos Notion
- **DB Usuarios:** `34811515f4b280f19a42f8da5e91a8fe`
- **DB Ofertas:** `33d11515-f4b2-81ef-a776-d0ea698b748f`

### Emails del Sistema
1. 🤖 Nueva oferta (9:00 AM) - 5 ofertas personalizadas con botones ✅/❌
2. 📝 Carta + CV - Al aprobar oferta
3. ✅ Confirmación - Al mandar a empresa

### Stack
- **Orquestador:** n8n en Render
- **CV Server:** Flask en Render
- **DB:** Notion (2 databases)
- **Email:** Brevo (`usecookyourwebai.es`)
- **Storage:** Google Drive
- **LLM:** Claude API (`claude-sonnet-4-6`)

### Documentación
- `CLAUDE.md` - Memoria completa del proyecto
- `DOCUMENTACION_TECNICA_v2.md` - Arquitectura detallada
- `README.md` - Vista general
