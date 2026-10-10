# Integración LinkedIn (Claude/Composio) + Auditoría multiusuario — 21 jul 2026

> Resumen de la sesión de hoy para no perder el contexto. Complementa `README.md`,
> `WORKFLOWS-N8N.md` y `AUDITORIA-2026-06-13.md`.

---

## 1. Qué se montó hoy: búsqueda de LinkedIn

LinkedIn no tiene API pública de ofertas (ni siquiera vía Composio — su conector solo
lee perfil y posts, no jobs). No se puede sumar como 4ª fuente igual que
Remotive/Adzuna/Tecnoempleo dentro de n8n.

**Solución:** una tarea programada de Claude (Cowork), separada de n8n, que:

- Corre **diariamente a las 9:10h** (`busqueda-empleos-mejor-pagados`, taskId en
  `/Users/vero/Claude/Scheduled/busqueda-empleos-mejor-pagados/SKILL.md`).
- Busca "AI Engineer" y "Frontend Lead" en LinkedIn (`COMPOSIO_SEARCH_WEB` sobre
  `site:linkedin.com/jobs`) + Indeed, remoto o híbrido Madrid.
- Verifica que la oferta siga abierta (descarta "No longer accepting applications").
- Comprueba anti-spam contra la columna **Link oferta** de la DB Notion "Ofertas de
  Trabajo" (`33d11515f4b281efa776d0ea698b748f`) antes de crear nada.
- Crea la página nueva en esa MISMA base (no un sistema paralelo), con:
  - `Puesto` = título **literal** de LinkedIn (sin reformular)
  - `Notas` = resumen destacado de qué pide la empresa en ESA oferta (para que
    `cv-server` lo use al adaptar CV/carta)
  - `Estado` = "Pendiente", `Usuario` = relación a la página de Verónica Serna Pérez
- **No manda ningún email.** El envío de la oferta lo gestiona Verónica manualmente
  desde Notion — decisión explícita para no duplicar el flujo de Brevo de n8n.

**Pendiente de verificar:** la primera ejecución en background (disparada por "Run
now") seguía corriendo (dos instancias en paralelo, una por el cron y otra manual) sin
haber llegado aún a escribir en Notion cuando se revisó. Revisar mañana si aparecieron
ofertas nuevas o si hubo que reintentar.

---

## 2. Auditoría de arquitectura multiusuario (a pedido de Vero)

Lectura completa de `cv_server_railway.py`, `README.md`, `WORKFLOWS-N8N.md`,
`05-COHERENCIA...md`, `AUDITORIA-2026-06-13.md`, y el export de producción real
descargado hoy (`BuscarTrabajo-PROD-modalidad-aprobar-dedup.json`, Downloads).

### Bien resuelto para multiusuario
- Notion como fuente de verdad de usuarios y ofertas: filtro por `Rol objetivo` /
  `Stack` / `Salario min` / `Modalidad` leído por usuario, nada hardcodeado (ya
  validado en el doc de coherencia de julio).
- `cv-server` lee todo por usuario (`buscar_usuario_por_email`), elige CV master
  ES/EN según idioma de la oferta, titular generado por oferta.
- El workflow de producción SÍ tiene loop real por usuario: nodo **"Loop Over
  Users"** sobre **"Notion — Query usuarios activos"** (confirmado en el JSON de
  producción de hoy, no en los exports viejos del repo que están desactualizados).

### Cuello de botella real: cuota de LLM compartida
Dentro del "Loop Over Users" hay un nodo **"Wait - Rate Limit Groq"** que pausa
**30 segundos por usuario** antes de llamar a Groq — parche manual para no reventar
el free tier compartido (100k tokens/día, ya documentado como límite en
`AUDITORIA-2026-06-13.md`, sección M4). Con 2 usuarios (los actuales, ambos Vero)
no se nota. Con 10 usuarios reales: ~5 min solo de esperas, y riesgo real de que el
segundo usuario del día se quede sin generar ofertas si el primero agotó la cuota.

**cv-server (CV + carta) ya usa Claude de pago** (`CV_MODEL=claude-haiku-4-5`,
`CARTA_MODEL=claude-sonnet-4-6`, ~$0,02-0,06 por CV) — ese coste ya escala bien
por usuario. El único punto sin resolver es el nodo de **ranking de ofertas**
("Groq - Generar Ofertas"), que sigue en el free tier compartido.

### Otros gaps de multiusuario (menor prioridad mientras sea solo Vero)
- **Google Drive**: un solo `GOOGLE_REFRESH_TOKEN` (cuenta personal de Vero) para
  TODOS los usuarios — todos los CVs se suben a su Drive, con su cuota e identidad.
  Punto único de fallo si se revoca el token.
- **Cero autenticación**: el formulario de registro/"buscar ahora" solo pide un
  email, sin verificar que quien lo escribe sea el dueño. Vale para conocidos de
  confianza, no para desconocidos.
- **Lógica de negocio en n8n sin versionar**: los exports de `workflows/` en el
  repo NO son la fuente de verdad (ya lo dice `WORKFLOWS-N8N.md`); dificulta testear
  cambios de reglas de filtrado.

### Decisión de Vero (hoy)
Por ahora el sistema queda para uso personal — no se toca nada. Cuando decida sumar
usuarios reales, evaluar entre: (a) pasar el nodo "Groq - Generar Ofertas" a un tier
de pago de Groq (barato, quita el rate limit compartido), o (b) mover ese nodo
también a Claude Haiku (volumen bajo — 5-12 ofertas rankeadas por usuario/día — coste
ínfimo, un solo proveedor de pago en vez de mezclar gratis+pago). No se decidió aún.

---

## 3. Sobre reemplazar n8n por automatizaciones de Claude

Evaluado y descartado como reemplazo completo. n8n aporta dos cosas que una tarea
programada de Claude no reproduce bien: webhooks síncronos instantáneos (el botón
"Aprobar" del email necesita respuesta en el momento) y ejecución 24/7 barata sin
depender de tokens de conversación por corrida.

**Lo que sí tiene sentido fuera de n8n:** búsqueda semántica donde no hay API limpia
(como LinkedIn, ya migrado hoy). El resto del pipeline (aprobar → generar → mandar)
se queda en n8n, o si genera fricción, se llevaría a rutas Flask nuevas dentro del
propio `cv-server` (ya es un servidor real) en vez de a un agente conversacional —
sería más barato y rápido que ambas alternativas.

---

**Generado:** 21 julio 2026, sesión Cowork/Claude.
