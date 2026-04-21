# CLAUDE.md — Memoria del proyecto BuscarTrabajo

> **Para cualquier IA que trabaje en este proyecto en futuras sesiones:** lee esto primero.
> Te da contexto en 2 minutos sin que el usuario tenga que repetir la historia cada vez.

---

## ¿Qué es esto?

Sistema automatizado multi-usuario de búsqueda de empleo. Cualquiera se registra en un
formulario web y cada mañana recibe 5 ofertas personalizadas + CVs adaptados + cartas
listas para enviar. Construido por Verónica Serna (frontend dev senior, Madrid).

## Estado actual (Abril 2026 — v2)

✅ **Funcionando en producción:**
- Generación diaria de 5 ofertas con Claude (ahora **ficticias**, generadas por IA)
- Notion CRM con 2 databases (Usuarios + Ofertas)
- Formulario de registro multi-user (nuevo vs existente)
- **Arquitectura modular con 2 workflows n8n separados**
- CV Server multi-user (lee CV Master según email del user)
- Emails con botones aprobar/descartar/mandar
- Agente revisor de CV integrado en el prompt (no hay llamada extra)

⏳ **Pendiente:**
- Ofertas REALES con `web_search` tool (ahora las inventa)
- Follow-ups automáticos 7/14 días
- Monitor de email (polling Gmail)
- Agente preparador de entrevistas

## Arquitectura — 2 workflows n8n separados

**Workflow 1: BuscarTrabajo-Usuarios** (11 nodos) — el "portero"
- `POST /webhook/nuevo-usuario` → crea en Notion → dispara webhook interno
- `POST /webhook/buscar-ahora` → busca en Notion → dispara webhook interno

**Workflow 2: BuscarTrabajo-v2-Principal** (38 nodos) — el "motor"
- `Schedule 9am` → lee todos los users activos
- `POST /webhook/buscar-para-user` → recibe del Workflow 1
- Merge → Split → Claude → Notion → Brevo
- Webhooks `aprobar`, `descartar`, `mandar` (igual que antes)

**Comunicación entre workflows:** el Workflow 1 hace `POST /webhook/buscar-para-user`
al Workflow 2 al terminar su parte. Patrón estándar "workflows modulares" de n8n.

## Stack

| Componente | Plataforma | URL |
|------------|-----------|-----|
| Orquestador | n8n en Render | `https://n8n-qwmu.onrender.com` |
| CV Server | Flask en Render | `https://cv-server-ggd8.onrender.com` |
| DB | Notion (2 databases) | Usuarios + Ofertas |
| Email | Brevo | dominio `usecookyourwebai.es` |
| Storage CVs | Google Drive | service account |
| LLM | Claude API | modelo `claude-sonnet-4-6` |

## Reglas NO NEGOCIABLES

Si estás editando el sistema:

1. **Model string Claude: SIEMPRE alias `claude-sonnet-4-6`** — nunca snapshot con fecha
   (ya nos pasó de inventar fechas que no existen)

2. **URL CV Server: `cv-server-ggd8.onrender.com`** — NO `cv-server-production.up.railway.app`
   (Railway antiguo muerto)

3. **Multi-tenant real:** `/generar-cv` requiere `email` en body. Fallback legacy a
   `CV_Master_Veronica.txt` SOLO para `hello.cookyourweb@gmail.com`.

4. **Schema Notion sensible a acentos/mayúsculas:**
   - `Teléfono Contacto` (con tilde)
   - `Email empresa` (minúscula en "empresa", no "Contacto")

5. **Emails dinámicos:** nunca hardcodear `hello.cookyourweb@gmail.com` en nodos Brevo.
   Usar `$('Split in Batches').item.json.email`.

6. **2 workflows separados:** NO los fusiones en uno. Están separados a propósito por
   debug/deploy independientes. Comunicación vía `/webhook/buscar-para-user`.

7. **Orden de importación en n8n:** primero Workflow 2 (principal), luego Workflow 1
   (usuarios). Si lo haces al revés, el webhook interno no existe y falla.

## Bugs conocidos que se han resuelto (NO vuelvas a hacerlos)

| Bug | Causa | Fix |
|-----|-------|-----|
| "No JSON found" misterioso | Claude sin créditos → Code no podía parsear | Error handling explícito |
| "Empresa undefined" al crear en Notion | Title tenía `{{ .empresa }}` sin `$json.` | Usar `{{ $json.empresa }}` |
| Bad request al crear usuario en Notion | `bodyParameters` con `name: "="` no funciona | Usar `specifyBody: "json"` + `jsonBody` |
| Webhook buscar-ahora colgado | Faltaba conexión al Respond | Conectar explícitamente |
| Todos los emails a Verónica | `to: 'hello.cookyourweb@gmail.com'` hardcoded | Usar email del user |
| Model string inventado | Fecha `20260217` no existía | Usar alias sin fecha |

## Archivos clave

```
workflow-1-usuarios.json           ← Workflow usuarios (registro)
workflow-2-principal.json          ← Workflow principal (ofertas + CV + aprobar)
cv-server/cv_server_railway.py     ← Flask multi-user
DOCUMENTACION_TECNICA_v2.md        ← Arquitectura completa
sync_notion_usuarios.py            ← Añadir columnas DB Usuarios
ROADMAP.md                         ← Fases futuras
```

## Cómo debuggear si algo falla

En este orden:

```bash
# 1. ¿Servidor vivo?
curl https://cv-server-ggd8.onrender.com/health

# 2. Diagnóstico total
curl https://cv-server-ggd8.onrender.com/debug

# 3. ¿Los 5 webhooks responden?
curl -X POST https://n8n-qwmu.onrender.com/webhook/buscar-para-user \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","nombre":"Test","perfil":"test"}'

# 4. Ver nodos en rojo en n8n UI — click para ver Output del error
# Los Code — Normalizar hacen throw Error con mensaje claro

# 5. Test Notion directamente
curl -X POST https://api.notion.com/v1/databases/34811515f4b280f19a42f8da5e91a8fe/query \
  -H "Authorization: Bearer ntn_G464872773099dpLY7OzD7I4ZeZee38rKHsoVlmCV2z7A0" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{"page_size": 5}'
```

## Créditos Anthropic

**Si recibes "credit balance too low":**
- Ir a `console.anthropic.com/settings/billing`
- Añadir créditos (mínimo $5, recomendado $20)
- Re-ejecutar

## Datos personales de Verónica (para referencia)

Solo cambiar si ella pide explícitamente:
- Verónica Serna Pérez · Senior Frontend Developer
- Madrid · +34 655 13 38 39 · verserper@gmail.com
- linkedin.com/in/veronica4web
- Email remitente emails sistema: `veronica@usecookyourwebai.es`

## Contexto de negocio

- Verónica está buscando trabajo activamente
- Quiere convertir esto en producto multi-user (2-3 beta testers primero, luego quizá comercializar)
- Salario target: 60K+ sin techo
- Modalidad: remoto o híbrido Madrid
- El sistema es TANTO portfolio técnico COMO herramienta útil real para ella

---

**Si este documento está desactualizado:** la versión canónica está en el repo de GitHub.
