# ESQUEMA WORKFLOW - BuscarTrabajo-2-Emails

## Flujo General

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    9:00 AM TODOS LOS DÍAS                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 1. CLAUDE API - Generar Ofertas                                         │
│    ├─ Prompt: "Genera 5 ofertas realistas para Frontend/IA en España"  │
│    └─ Devuelve: empresa, puesto, salario, modalidad, link, descripción  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 2. CODE - Normalizar Modalidad                                          │
│    ├─ Entrada: Array de 5 ofertas                                      │
│    ├─ Procesa: "remoto" → "Remoto", "híbrido" → "Hibrido"              │
│    └─ Salida: Array normalizado                                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 3. NOTION - Crear Oferta (x5 veces, una por oferta)                      │
│    ├─ Crea página en database                                           │
│    ├─ Guarda: Empresa, Puesto, Salario, Modalidad, Link, Notas        │
│    └─ Estado = "Pendiente"                                              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 4. SET - Preparar Variables Email                                       │
│    ├─ Extrae: empresa, puesto, modalidad, salario, pageId              │
│    ├─ Añade: sender_name, sender_email, to_email                       │
│    └─ Salida: Variables listas para Brevo                              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 5. BREVO - Email 1: Notificación                                        │
│    ├─ Para: hello.cookyourweb@gmail.com                                 │
│    ├─ Asunto: "Nueva oferta: [Empresa] - [Puesto]"                    │
│    ├─ Contenido: Tabla con datos de la oferta                           │
│    ├─ Botón VERDE: "Aprobar" → /webhook/aprobar?id=PAGE_ID           │
│    └─ Botón ROJO: "Descartar" → /webhook/descartar?id=PAGE_ID        │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Si haces click en "DESCARTAR"

```
┌─────────────────────────────────────────────────────────────────────────┐
│ CLICK EN BOTÓN ROJO DEL EMAIL                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 1. WEBHOOK Descartar                                                    │
│    └─ Recibe: pageId de la oferta                                      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 2. NOTION - Marcar Descartado                                           │
│    └─ Actualiza Estado → "Descartado"                                  │
│    └─ FIN DEL FLUJO (no hay más emails)                                │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Si haces click en "APROBAR"

```
┌─────────────────────────────────────────────────────────────────────────┐
│ CLICK EN BOTÓN VERDE DEL EMAIL                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 1. WEBHOOK Aprobar                                                      │
│    └─ Recibe: pageId de la oferta                                      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 2. NOTION - Marcar Aprobado                                             │
│    └─ Actualiza Estado → "Aprobado"                                    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 3. NOTION - Obtener Datos Completos                                   │
│    └─ Lee: empresa, puesto, descripción completa                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ├─────────────────────────────────────┐
                                    │                                     │
                                    ▼                                     ▼
┌─────────────────────────────────┐   ┌─────────────────────────────────┐
│ 4A. CLAUDE - Generar Carta      │   │ 4B. CV SERVER - Generar CV      │
│                                 │   │                                 │
│ ├─ Entrada: empresa, puesto,    │   │ ├─ Entrada: empresa, puesto,   │
│ │   descripción                 │   │ │   descripción                 │
│ ├─ Claude escribe carta       │   │ ├─ Lee CV Master de Drive     │
│ │   personalizada               │   │ ├─ Claude adapta el CV        │
│ └─ Salida: Texto de la carta    │   │ ├─ Genera .docx               │
│                                 │   │ ├─ Sube a Drive               │
│                                 │   │ └─ Salida: Link de Drive      │
└─────────────────────────────────┘   └─────────────────────────────────┘
                                    │                                     │
                                    └──────────────┬──────────────────────┘
                                                   │
                                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 5. CODE - Combinar Carta + CV                                            │
│    ├─ Entrada: Carta (de Claude) + Link CV (de CV Server)              │
│    ├─ Combina todo en un objeto                                        │
│    └─ Salida: Variables para email final                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 6. BREVO - Email 2: Carta + CV                                          │
│    ├─ Para: hello.cookyourweb@gmail.com                                 │
│    ├─ Asunto: "✅ Oferta Aprobada - [Empresa]"                        │
│    ├─ Sección 1: Carta de presentación completa                        │
│    ├─ Sección 2: Botón "📥 Descargar CV de Google Drive"              │
│    └─ Nota: "CV adaptado específicamente para esta oferta"           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Resumen de Emails

| # | Momento | Asunto | Contenido |
|---|---------|--------|-----------|
| **1** | 9:00 AM | `Nueva oferta: [Empresa] - [Puesto]` | Datos de la oferta + botones Aprobar/Descartar |
| **2** | Cuando apruebas | `✅ Oferta Aprobada - [Empresa]` | Carta de presentación + Link al CV en Drive |

---

## Estados en Notion

```
┌──────────┐     ┌──────────┐     ┌────────────┐
│ Pendiente│────▶│ Aprobado │     │ Descartado │
│  (nuevo) │     │          │     │            │
└──────────┘     └──────────┘     └────────────┘
     │                │                  │
     │                ▼                  │
     │           [Genera CV              │
     │           + Carta]                │
     │                │                  │
     │                ▼                  │
     │           [Email 2]                │
     │                                    │
     │                ┌───────────────────┘
     │                │
     ▼                ▼
   [Esperando]    [Archivado]
```

---

## URLs Importantes

- **N8N Dashboard:** `https://n8n-qwmu.onrender.com`
- **Webhook Aprobar:** `https://n8n-qwmu.onrender.com/webhook/aprobar?id=PAGE_ID`
- **Webhook Descartar:** `https://n8n-qwmu.onrender.com/webhook/descartar?id=PAGE_ID`
- **CV Server:** `https://cv-server-production.up.railway.app`

---

## Servicios Conectados

| Servicio | Uso |
|----------|-----|
| **Claude API** | Generar ofertas + Escribir cartas |
| **Notion** | Base de datos de ofertas (CRM) |
| **Brevo** | Enviar emails |
| **CV Server** | Generar y subir CVs adaptados |
| **Google Drive** | Almacenar CVs generados |
