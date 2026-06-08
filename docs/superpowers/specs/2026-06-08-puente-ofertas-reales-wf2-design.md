# Diseño — Puente: ofertas reales → pipeline Notion + aprobar (WF2)

**Fecha:** 2026-06-08
**Proyecto:** buscartrabajo
**Autora:** Verónica + Claude

## Problema

La búsqueda diaria de empleo (Fase 1) ya trae ofertas **reales** de 3 fuentes
(Remotive, Adzuna, Tecnoempleo), filtradas por perfil y rankeadas. Pero solo las
manda a **Telegram**, donde mueren: no quedan registradas ni se puede accionar.

Por otro lado, el WF2 ya tiene **toda la Fase 2 construida y activa**: botón
Aprobar → genera carta + CV adaptado → email de revisión. Pero corre sobre
ofertas **inventadas** por Groq.

Las dos mitades no están conectadas. Este diseño construye el **puente**.

## Alcance

- **Human-in-the-loop SIEMPRE.** El sistema prepara CV + carta y se los manda a
  Verónica para revisar. Ella decide y envía a la empresa **a mano**.
- Dejar **preparado** para un futuro auto-envío, sin construirlo ahora (YAGNI).
- No se reconstruye nada de la Fase 2: ya existe y funciona.

## Arquitectura

Pensar el WF2 en dos mitades:

- **Mitad A** — generaba ofertas inventadas → Notion → email con botones. *(se retira)*
- **Mitad B** — webhooks Aprobar / Descartar / Mandar a empresa. *(intacta, origen-agnóstica)*

El puente reemplaza la Mitad A: alimenta el pipeline con ofertas **reales** desde
la búsqueda diaria, reutilizando los nodos de creación en Notion + email con botones.

### Flujo de datos (workflow "Búsqueda Empleo Diaria", extendido)

```
[Remotive] [Adzuna] [Tecnoempleo]
        ↓
[Formatear ofertas]  ← filtro determinista por perfil (EXCLUIR por título, KEYWORDS por todo)
        ↓
[Dedupe]             ← descarta ofertas cuya URL ya existe en Notion (ANTES del LLM: no gastar ranking en ya vistas)
        ↓
[Rankear ofertas]    ← LLM Groq: devuelve LISTA ESTRUCTURADA ordenada (mejor primero), tope 10
        ↓
[Separar 1 ítem por oferta]
        ↓
[Notion: Crear Oferta]  (Estado = "Nueva")  ← reusa nodo de WF2 Mitad A
        ↓
[Armar fila de email]   (botones Aprobar/Descartar/Mandar con el id de página)
        ↓
[Brevo: 1 email diario de revisión]  con todas las ofertas nuevas del día
        ↓
[Telegram]              ← sigue como vistazo rápido (sin cambios)
```

La **Mitad B** del WF2 no se toca: los botones del email pegan a los webhooks ya
existentes (`oferta-aprobar`, `oferta-descartar`, `oferta-mandar-empresa`), que
disparan carta + CV + email de revisión.

## Componentes y cambios

### 1. Nodo "Rankear ofertas" — salida estructurada (CAMBIO)
- **Antes:** un bloque de texto formateado para Telegram.
- **Ahora:** una lista JSON de ofertas, ordenada de mejor a peor, con campos:
  `titulo, empresa, ubicacion, salario, url, descripcion, fuente, motivo`.
- **Tope:** 10 ofertas (parámetro ajustable). Evita un email gigante el primer día.
- El mensaje de Telegram se deriva de esta misma lista (formateo aparte), para no
  duplicar la llamada al LLM.

### 2. Nodo "Dedupe" (NUEVO) — corre ANTES del ranker
- Consulta la base de datos de Notion por las URLs de las ofertas candidatas.
- Descarta las que ya existen. Solo continúan las **nuevas** al ranker.
- Clave de deduplicación: **URL de la oferta** (única y estable por oferta).
- Va antes del LLM para no gastar ranking en ofertas ya vistas.

### 3. Nodos "Crear en Notion" + "Email con botones" (REUSAR de WF2 Mitad A)
- Por cada oferta nueva: crear página en Notion con `Estado = Pendiente` y los campos
  (título, empresa, ubicación, salario, url, descripción, fuente).
- Recoger el `id` de la página creada para construir los links de los botones.
- Agrupar todas las ofertas del día en **un solo email** Brevo, cada una con sus
  tres botones (Aprobar / Descartar / Mandar a empresa).

### 4. WF2 Mitad A — retirar (CAMBIO)
- Desactivar el generador de ofertas inventadas (su Schedule Trigger) para que no
  siga creando ofertas falsas. La Mitad B (webhooks) queda activa.

## Datos: base de datos de Notion

Campos mínimos por oferta (verificar contra la DB existente al implementar):
`Título`, `Empresa`, `Ubicación`, `Salario`, `URL`, `Descripción`, `Fuente`,
`Estado` (Pendiente → Aprobada → En proceso → En revisión → Enviada / Descartada).
DB id real: `33d11515f4b281efa776d0ea698b748f`.

## Manejo de errores

- **Fuente caída** (una API falla): el workflow continúa con las otras dos
  (ya hay `try/catch` por fuente en "Formatear ofertas").
- **Sin ofertas nuevas hoy:** no se manda email de revisión (o se manda un aviso
  corto "0 ofertas nuevas"). No crear páginas vacías en Notion.
- **CV Server caído** (Render, 502 ocasional): el webhook Aprobar debe responder
  con un error claro y dejar la oferta en estado recuperable (reintentar al
  re-aprobar), no perder la oferta.
- **Dedupe:** si la consulta a Notion falla, NO crear duplicados a ciegas →
  abortar la creación de esa tanda y avisar, mejor 0 que repetidas.

## Qué NO entra (YAGNI)

- Auto-envío a la empresa (se deja la puerta abierta, no se construye).
- Multi-usuario (el cv-server ya lee por email; no se generaliza ahora).
- Scraping de LinkedIn (descartado: sin API, frágil, baneable).

## Criterios de éxito

1. Una oferta real que pasa el filtro aparece en Notion con `Estado = Pendiente`.
2. Llega **un** email diario con las ofertas nuevas y sus botones.
3. Al tocar **Aprobar**, llega a los pocos minutos el email con CV adaptado + carta.
4. Ofertas ya vistas **no** se repiten al día siguiente (dedupe funciona).
5. El flujo de aprobar (Mitad B) sigue funcionando sin cambios.
