# Sistema Automatizado de Búsqueda de Empleo — v3 (Ofertas Reales, Multi-usuario)

## Descripción

Sistema **multi-usuario** de búsqueda de empleo. Cada persona se registra en un formulario web; cada mañana el sistema busca **ofertas REALES** (Remotive + Adzuna + Tecnoempleo), las filtra por su perfil, y se las manda por email con botones. Al aprobar, genera **carta + CV adaptado al puesto** y permite enviarlo a la empresa.

**v3 vs v2:**
- v2 = ofertas **inventadas** por el LLM.
- v3 = ofertas **reales** scrapeadas de 3 fuentes + filtro por stack del usuario + anti-spam (no repite ofertas ya guardadas en Notion).
- v3 = envío a empresa **híbrido con edición previa** (revisás carta/CV en Notion/Drive antes de mandar).

---

## Arquitectura v3

```
USUARIO
  → cv-server-ggd8.onrender.com/   (formulario alta: nuevo / existente)
        │
        ▼
FLASK CV SERVER (Render Free)
  GET  /                → formulario alta + acciones
  POST /check-email     → ¿el email ya existe en Notion?
  POST /accion-existente→ "Buscar ahora" / "Programar 9am"
  POST /registro        → crea usuario en Notion Usuarios + dispara WF1
  POST /generar-cv      → genera CV adaptado al puesto y lo sube a Drive
                          (devuelve: link adaptado + cv_master_url)
  Capa LLM: CV y carta con Claude Sonnet 4.6 (Groq de fallback)
            Resto: Groq openai/gpt-oss-120b → Gemini 3.6 flash → Claude Haiku 4.5
        │
        ▼
n8n  ──  instancia: n8n-asistente-correo.onrender.com
  ┌───────────────────────────────────────────────────────────┐
  │ WF1 — BuscarTrabajo-Usuarios                              │
  │   Webhook /nuevo-usuario   → crea/normaliza → HTTP → WF2  │
  │   Webhook /buscar-ahora    → query Notion → HTTP → WF2    │
  ├───────────────────────────────────────────────────────────┤
  │ WF2 — WF2-integrado-v3 (multi-usuario)                    │
  │   Triggers:                                               │
  │     · Schedule 9am  → query usuarios activos → Loop       │
  │     · Webhook /buscar-para-user (interno desde WF1)       │
  │     · Webhooks /oferta-aprobar /-descartar /-mandar-empresa│
  │                                                           │
  │   Búsqueda (por usuario):                                 │
  │     Remotive + Adzuna + Tecnoempleo → Formatear           │
  │     (filtra por stack/rol del usuario + ANTI-SPAM contra  │
  │      ofertas ya en Notion) → cap 12 ofertas (Groq free)   │
  │     → Groq formatea → Notion crea Oferta → Brevo email    │
  │                                                           │
  │   Aprobar:                                                │
  │     Respond inmediato → Marcar Aprobado/En Proceso        │
  │     → Obtener Datos Oferta → Groq Carta                   │
  │     → CV Server /generar-cv (usa Email Enviado del user)  │
  │     → Brevo "revisar y enviar" + Notion guarda            │
  │       (Carta Enviada, CV usado=master, Link CV Drive=adaptado, Fecha envio)│
  │                                                           │
  │   Enviar a empresa (híbrido):                             │
  │     lee Carta Enviada YA EDITADA → si hay Email empresa:  │
  │       manda carta+CV a la empresa (replyTo = email user)  │
  │     si no: mail al user "aplicar a mano" con link oferta  │
  └───────────────────────────────────────────────────────────┘
```

---

## Servicios

| Servicio | URL | Propósito |
|----------|-----|-----------|
| CV Server | cv-server-ggd8.onrender.com | Formulario alta + generar CV adaptado |
| n8n | **n8n-asistente-correo.onrender.com** | Orquestador (WF1 + WF2) |
| Notion | api.notion.com | CRM Usuarios + Ofertas |
| Google Drive | drive.google.com | CVs adaptados |
| Brevo | api.brevo.com | Envío de emails |
| Groq | api.groq.com | LLM de ofertas y fallback de CV/carta (openai/gpt-oss-120b) |

> ⚠️ **Instancia n8n activa = `n8n-asistente-correo`.** Las viejas (`n8n-st1v`, `n8n-qwmu`) están deprecadas. n8n NO permite dos workflows con el mismo webhook path activos a la vez → tener UNA sola instancia activa con estos paths.

---

## Webhooks n8n

| Método | Path | Workflow |
|--------|------|----------|
| POST | `/webhook/nuevo-usuario` | WF1 |
| POST | `/webhook/buscar-ahora` | WF1 |
| POST | `/webhook/buscar-para-user` | Interno (WF1 → WF2) |
| GET | `/webhook/oferta-aprobar?id=` | WF2 |
| GET | `/webhook/oferta-descartar?id=` | WF2 |
| GET | `/webhook/oferta-mandar-empresa?id=` | WF2 |

---

## Base de Datos Notion

### DB Usuarios — `34811515f4b280f19a42f8da5e91a8fe`

| Columna | Tipo |
|---------|------|
| Name | Title |
| Email | Email (único) |
| Perfil | Rich text |
| Rol objetivo | Rich text |
| Stack | Multi-select |
| Salario min | Number |
| Modalidad | Multi-select |
| Ciudad | Rich text |
| LinkedIn | URL |
| CV Master URL | URL |
| cv_master_file_id | Rich text |
| Activo | Checkbox |

### DB Ofertas — `33d11515f4b281efa776d0ea698b748f`

| Columna | Tipo | Qué guarda |
|---------|------|------------|
| Empresa | Title | nombre empresa |
| Puesto | Rich text | |
| Salario | Rich text | |
| Modalidad | Select | Remoto / Hibrido / Presencial |
| Link oferta | URL | url original (clave anti-spam) |
| Notas | Rich text | descripción corta |
| Estado | Select | Pendiente / Aprobado / Descartado / En proceso / Enviado a empresa |
| **Email Enviado** | Email | **email del usuario destinatario** |
| Usuario | Relation | relación a DB Usuarios |
| Nombre Contacto | Rich text | RRHH de la oferta |
| Email empresa | Email | contacto de la empresa (para envío auto) |
| Teléfono Contacto | Phone | |
| Fecha Publicacion | Date | |
| Fecha envio | Date | cuándo se generó carta+CV |
| Fecha Envio Empresa | Date | cuándo se mandó a la empresa |
| **Link CV Drive** | URL | **CV adaptado** a la oferta |
| **CV usado** | Rich text | **CV master** (referencia del que se partió) |
| **Carta Enviada** | Rich text | carta de presentación generada/editada |
| Seguimiento | Date | seguimiento manual |

> 🔑 **CV usado = master (referencia)** · **Link CV Drive = CV adaptado (resultado)**. Son dos CVs distintos.

---

## Debugging rápido

```bash
# 1. ¿CV Server vivo? (Render Free duerme ~15min → cold start ~50s)
curl https://cv-server-ggd8.onrender.com/health

# 2. ¿LLM responde?
curl https://cv-server-ggd8.onrender.com/debug

# 3. ¿Webhook buscar-ahora funciona? (instancia NUEVA)
curl -X POST https://n8n-asistente-correo.onrender.com/webhook/buscar-ahora \
  -H "Content-Type: application/json" \
  -d '{"email":"hello.cookyourweb@gmail.com","nombre":"vero"}'
```

Si responden 200 → el problema está en el flujo interno (revisar Executions en n8n).

---

## Gotchas y deuda conocida

- **Groq Free TPD = 100.000 tokens/día** es el cuello de botella real (no el RPM). Por eso el cap de **12 ofertas** en modo prueba. Agotarlo da 429 hasta el reset diario.
- **Env vars Render del CV Server** (`WEBHOOK_NUEVO_USUARIO`, `WEBHOOK_BUSCAR_AHORA`) DEBEN apuntar a `n8n-asistente-correo`. Si quedaron en `n8n-st1v`, el alta de usuario nuevo dispara a la instancia muerta.
- **API keys**: tras rotarlas hay que actualizarlas en DOS sitios — credenciales n8n (Notion, Brevo) **y** env vars Render (Groq, Gemini, Notion, Google OAuth).
- **n8n**: al importar un workflow desde otra instancia, los IDs de credencial NO se mapean → reasignar credencial nodo por nodo. Importar con *Import from File* SOBRE el workflow abierto (si no, se duplica).
- **Notion**: nombres de propiedad case-sensitive y con tildes (`Teléfono Contacto`, `Email empresa`). Mandar una propiedad con tipo equivocado da 400; mandar una que no existe en el payload no falla, pero escribir en un nombre inexistente sí rompe el PATCH.
- **Tipografía del CV/carta (cv-server)**: el `cv-server` sanea el texto antes de renderizar (`sanear_tipografia`): fuera guiones largos y flechas, que son rastro de IA y NO pueden salir a una empresa. Cuidado: el DOCX detecta la línea de empresa usando el guion largo como marcador, así que la detección sigue leyendo la línea cruda y solo se limpia el texto que se escribe. No metas un saneado global antes de parsear o pierdes las negritas.
- **Credencial Groq del workflow Telegram**: caso real del gotcha de importar workflows. "Búsqueda Empleo Diaria" fallaba a diario porque su nodo Groq apuntaba a una credencial borrada (`2b1f3WOTcvKNLpgy`). Reapuntado a la credencial viva `Groq account 2` (`Ewz07GBHAM5voex1`, la misma que usan Digest y Outlook FIX) el 20-jul-2026.

---

**Última actualización:** 20 julio 2026
**Estado:** ✅ v3 multi-usuario con ofertas reales. Flujo de aprobación con carta y CV operativo. Fix de tipografía (sin guiones largos ni flechas) en cv-server y credencial Telegram reparada el 20-jul.
**Archivo canónico workflow:** `workflows/WF2-integrado-v3.json`
