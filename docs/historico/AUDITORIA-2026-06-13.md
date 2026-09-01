#cuditoría del sistema buscarTrabajo — 13 jun 2026

> Informe de estado para decidir los próximos pasos. Sistema: búsqueda de empleo
> multi-usuario (n8n + cv-server) que busca ofertas reales, las propone por mail,
> y al aprobar genera carta + CV adaptado y los manda a la empresa.

---

## 1. Resumen ejecutivo

El sistema **ya funciona de punta a punta**: busca ofertas reales, las crea en Notion,
manda mail con botones, y al aprobar genera carta + CV y manda el 2º mail. En los últimos
dos días se arreglaron 4 bugs que lo tenían roto (tokens y parseo de CV).

**Pero NO está listo para mandar CVs a empresas todavía.** La calidad del CV y de la carta
no es suficiente, faltan campos y hay un riesgo de seguridad abierto. El motor que genera
los textos (Groq/llama gratis) se queda corto para algo que va a un empleador.

| Área | Estado |
|------|--------|
| Infraestructura (n8n, cv-server, Render, tokens) | 🟢 Funciona |
| Pipeline end-to-end (buscar → aprobar → carta+CV → mail) | 🟢 Funciona |
| Calidad del CV generado | 🟡 Mejoró (ya usa experiencia real) pero queda corto |
| Calidad de la carta | 🔴 Genérica, no usa la experiencia real |
| Datos capturados en Notion (contacto, email empresa) | 🟡 Incompleto |
| Edición de carta/CV antes de enviar | 🟡 Abren en solo-lectura |
| Seguridad | 🔴 Token de Google con caducidad + secreto filtrado |

---

## 2. Arquitectura del sistema

**Dos servicios separados en Render** (cajas distintas, env vars propias):

1. **`n8n-asistente-correo.onrender.com`** — instancia n8n (plan starter, no se duerme).
   Aloja el workflow **WF2 Integrado v3** (47 nodos).
2. **`cv-server-ggd8.onrender.com`** — servidor Python/Flask (plan free, se duerme;
   keep-warm cada 10 min). Genera el CV en DOCX y lo sube a Drive.

**Servicios externos:**
- **Notion** — 2 bases: Usuarios (`34811515…`) y Ofertas (`33d11515…`). Fuente de verdad
  de usuarios y ofertas. El cv-server las lee EN VIVO.
- **Google Drive** — guarda el CV master de cada usuario y los CVs generados.
- **Brevo** — envío de los mails (notificación + carta/CV).
- **Fuentes de ofertas** — Remotive, Adzuna, Tecnoempleo.
- **LLMs** — Groq (llama-3.3-70b, primario, gratis) → Gemini → Claude (fallbacks).

**Flujo WF2 (resumido):**
```
Schedule 9am / Manual → Query usuarios activos → Loop por usuario
  → Buscar ofertas (Remotive+Adzuna+Tecnoempleo) → Anti-spam (Notion ofertas existentes)
  → Groq formatea (cap 12) → Crear oferta en Notion → Mail con botones
Aprobar (webhook) → Notion "En proceso" → Groq genera CARTA + cv-server genera CV
  → 2º mail "revisar y enviar" → Guardar Link CV en Notion
Enviar a empresa (webhook) → marca enviado
```

---

## 3. Qué funciona (verificado esta semana)

- ✅ El cv-server reconoce los usuarios de Notion (`/usuarios` → 2 usuarios).
- ✅ `/generar-cv` responde 200 y sube el CV a Drive.
- ✅ El CV ahora **usa la experiencia real** del master (React, ALD→Ayvens, design system).
- ✅ El pipeline llega de Aprobar → carta + CV → 2º mail con botón Enviar.
- ✅ Guardrail nuevo: si el master es ilegible, el server **aborta con error claro** en
  vez de inventar un CV falso.

---

## 4. Hallazgos por severidad

### 🔴 CRÍTICOS

**C1 — Token de Google caduca cada 7 días.**
El cliente OAuth que usa Render (`36051363838…`) vive en un proyecto Google Cloud en modo
**Testing** → los refresh tokens mueren a los 7 días. El token actual caduca **~19 jun**.
*Fix:* publicar ese proyecto a "En producción", o migrar Render al cliente `179321830807`
(que ya está en producción).

**C2 — Client secret de Google filtrado.**
Durante el debug, el `client_secret` (`GOCSPX-…`) se pegó en el chat.
*Fix:* rotarlo en Google Cloud (hacerlo junto con C1, así se regenera el token una sola vez).

**C3 — La carta es genérica y no usa la experiencia real.**
El nodo `Groq - Generar Carta` escribe sin ver el CV master → cartas vacías de contenido,
con frases que deberían estar prohibidas ("proactiva y apasionada", "soluciones innovadoras
y escalables", "emocionada de la oportunidad"). **Esto va a una empresa.**

### 🟡 IMPORTANTES (calidad / datos)

**I1 — El CV se queda corto.**
Mejoró mucho (ya usa experiencia real) pero el output salió en ~1.669 chars vs 4.943 del
master: se comió Mutualidad, Aditel, ElMundo y parte de las skills. Causa probable: el motor
(llama-3.3-70b) recorta y no sigue bien un prompt elaborado. (Ver sección 5.)

**I2 — Faltan campos en Notion.**
No se captura email de la empresa, nombre de contacto ni teléfono de la oferta. Sin esos
datos no se puede enviar a la empresa de forma automática.

**I3 — Links de edición abren en modo lectura.**
"Editar carta en Notion" y "Editar CV en Drive" abren en solo-lectura → no se puede ajustar
antes de enviar.

**I4 — El CV no va adjunto en el 2º mail.**
Solo va el link a Drive. Para una empresa, conviene el DOCX adjunto.

### 🔵 MENORES / técnicos

- **M1 — Typo en la cabecera del CV:** "Develper" (viene del campo `rol` en Notion).
- **M2 — Auto-Deploy de Render estaba apagado** → los pushes no se aplicaban. Ya activado.
- **M3 — Fragilidad de expresiones largas en n8n:** los nodos con JS multi-línea se rompen
  al editar. Convención adoptada: dejarlas en UNA línea.
- **M4 — Budget de Groq free:** 100k tokens/día. Las pruebas consumen; no spamear.

---

## 5. La decisión central: motor del CV (Groq vs Claude)

El prompt nuevo que escribiste ("CV ADAPTER") está **diseñado para Claude** (lo dice literal).
El cv-server hoy usa **Groq/llama-3.3-70b gratis**, y por eso el CV sale corto y no respeta
bien reglas finas (language mirroring, anti-IA, orden de skills por tipo de oferta).

**3 cosas a entender antes de integrarlo:**

1. **El LLM solo escribe TEXTO; el `.docx` lo arma el código Python.** Todo el diseño visual
   de tu prompt (Navy #0D2137, Arial, tamaños, texto invisible ATS, footer) va programado en
   la función `generar_docx_con_cabecera`, NO en el prompt.
2. **El CV base conviene embeberlo** (como en tu prompt) en vez de leer el `.docx` de Drive
   — es más fiable y ya está curado por vos.
3. **El motor define la calidad.** Para algo que va a empresas, vale la pena Claude.

**Costo por CV (precios oficiales, ~4k tokens entrada + ~3k salida):**

| Motor | Precio (in/out por 1M) | Costo por CV | Calidad para este prompt |
|-------|------------------------|--------------|--------------------------|
| Groq llama-3.3-70b | gratis | $0 | Baja: recorta, no sigue reglas finas |
| Claude Haiku 4.5 | $1 / $5 | **~$0,02** | Buena, muy barata |
| Claude Sonnet 4.6 | $3 / $15 | **~$0,06** | Muy buena, equilibrio ideal |
| Claude Opus 4.8 | $5 / $25 | ~$0,10 | Máxima, probablemente innecesaria |

**Recomendación:** usar **Claude (Sonnet 4.6 o Haiku 4.5) solo para el CV y la carta** —
lo que va a empresas — y dejar Groq gratis para la búsqueda de ofertas. A ~2-6 céntimos por
CV, el costo es trivial frente al valor de conseguir entrevistas. El cv-server ya tiene
soporte de Claude como fallback; habría que promoverlo a primario para esos dos nodos.

---

## 6. Roadmap recomendado (orden de prioridad)

**Antes de mandar UN CV a una empresa:**
1. [C3 + I1] Migrar generación de CV y carta a Claude + integrar el prompt "CV ADAPTER"
   (contenido al prompt, diseño visual al código).
2. [I2] Agregar campos en Notion (email empresa, contacto, teléfono) y capturarlos del scraping.
3. [I3] Permisos de edición en los links de carta/CV.
4. [M1] Corregir "Develper" → "Developer" en Notion.

**Esta semana (antes del 19 jun):**
5. [C1 + C2] Publicar el proyecto OAuth a producción + rotar el client_secret.

**Cuando el flujo esté pulido:**
6. [I4] Adjuntar el DOCX en el 2º mail.
7. Botones de envío: "Enviar ahora" vs "Voy a modificar" (tomar la última versión guardada).
8. 4ª etapa: preparación de entrevista (modelada en osapiens-prep).

---

## 7. Decisiones abiertas (para vos)

1. **Motor del CV/carta:** ¿Claude Sonnet 4.6 (mejor), Haiku 4.5 (más barato), o mixto?
2. **CV base:** ¿lo embebemos en el código (curado, fiable) o seguimos leyendo el `.docx` de Drive?
3. **Durabilidad del token Google:** ¿publicar el proyecto actual a producción, o migrar al
   cliente `179321830807` que ya está en producción?
4. **Adjunto vs link** para el CV en el mail a la empresa.

---

*Generado durante la sesión de auditoría del 13/06/2026. Pricing verificado contra la
referencia oficial de la API de Claude.*
