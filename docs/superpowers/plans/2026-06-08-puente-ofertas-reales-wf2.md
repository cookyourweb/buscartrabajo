# Puente ofertas reales → pipeline Notion/aprobar — Plan de implementación

> **Medio:** edición de workflow n8n (JSON), no código con tests unitarios.
> Cada tarea termina con: importar en n8n → "Probar ahora" → mirar el output del
> nodo → re-exportar el JSON → commit. La "prueba" es observar el output real del nodo.

**Goal:** Conectar la búsqueda diaria de ofertas reales (3 fuentes ya validadas)
al pipeline existente de Notion + email con botones + aprobar (WF2 Mitad B), sin
tocar el flujo de aprobar que ya funciona.

**Arquitectura:** Extender el workflow "Búsqueda Empleo Diaria" (Opción A). Las
ofertas reales pasan por filtro → dedupe contra Notion → ranker → se crean en
Notion (Estado=Pendiente) → un email diario con botones Aprobar/Descartar/Mandar.
Los botones pegan a los webhooks ya existentes (`<RUTA_OCULTA>`, etc.).

**Datos reales (no cambiar a ciegas):**
- Notion DB id: `33d11515f4b281efa776d0ea698b748f`
- Campos Notion: Empresa (título), Puesto (rich_text), Salario (rich_text),
  Modalidad (select), Link oferta (url), Notas (rich_text), Estado (select="Pendiente")
- Webhooks WF2: `<RUTA_OCULTA>`, `<RUTA_OCULTA>`, `<RUTA_OCULTA>`
- Brevo: `POST https://api.brevo.com/v3/smtp/email`, header `api-key` (SECRETO → en n8n)
- Archivo base a editar: `~/Downloads/Busqueda Empleo Diaria - ADZUNA.json`
- Fuente de nodos a reusar: `buscartrabajo/workflows/WF2-BuscarTrabajo-v2-Groq.json`

---

## Tarea 1 — "Formatear ofertas" emite array estructurado (no texto)

**Archivo:** nodo `Formatear ofertas` en `Busqueda Empleo Diaria - ADZUNA.json`

Hoy junta las 3 fuentes en un string `ofertas`. Para dedupe + Notion necesitamos
**un objeto por oferta**, no un blob.

- [ ] **Paso 1:** Cambiar el `return` del nodo. En vez de `{ ofertas: lista, total }`,
  devolver un item por oferta con campos exactos que consume Notion:
  ```js
  // al final del nodo, en lugar de armar el string:
  return out.map(o => ({ json: {
    empresa: o.empresa,
    puesto: o.titulo,
    salario: o.salario || 's/i',
    modalidad: o.modalidad || (o.fuente === 'Remotive' ? 'Remoto' : ''),
    link: o.link,
    descripcion_corta: (o.desc || '').slice(0, 180),
    fuente: o.fuente
  }}));
  ```
  (Refactor: cambiar el `out.push('[Remotive] ...string...')` por
  `out.push({ titulo, empresa, salario, modalidad, link, desc, fuente })` en cada
  una de las 3 ramas — objetos, no strings.)
- [ ] **Paso 2:** Importar en n8n, "Probar ahora", abrir el nodo `Formatear ofertas`.
  **Esperado:** N items, cada uno con `empresa, puesto, link, descripcion_corta...`
  (no un solo item con un string gigante).
- [ ] **Paso 3:** Re-exportar el JSON a `buscartrabajo/workflows/` y commit:
  ```bash
  git add buscartrabajo/workflows/busqueda-empleo-diaria.json
  git commit -m "refactor(empleo): Formatear ofertas emite array estructurado por oferta"
  ```

---

## Tarea 2 — Nodo "Dedupe Notion" (descarta ofertas ya vistas)

**Archivo:** nuevo nodo entre `Formatear ofertas` y `Rankear ofertas`

- [ ] **Paso 1:** Añadir un nodo HTTP Request (o Notion "Get Many") que consulte la DB
  `33d11515f4b281efa776d0ea698b748f` y traiga los `Link oferta` ya guardados.
  HTTP: `POST https://api.notion.com/v1/databases/33d11515f4b281efa776d0ea698b748f/query`
  con header `Authorization: Bearer {{NOTION_TOKEN}}` (secreto, ya en n8n) y
  `Notion-Version: 2022-06-28`. Body: `{ "page_size": 100 }` (paginar si hace falta).
- [ ] **Paso 2:** Nodo Code "Filtrar nuevas": construir un Set de URLs existentes y
  filtrar los items de `Formatear ofertas` cuya `link` ya esté:
  ```js
  const existentes = new Set();
  for (const p of ($('Dedupe Notion').first().json.results || [])) {
    const u = p.properties?.['Link oferta']?.url;
    if (u) existentes.add(u.trim());
  }
  return $('Formatear ofertas').all()
    .filter(it => !existentes.has((it.json.link || '').trim()));
  ```
- [ ] **Paso 3:** "Probar ahora", abrir "Filtrar nuevas". **Esperado:** solo ofertas
  cuya URL NO está en Notion. Correr dos veces seguidas: la 2ª vez deben quedar 0
  (todas creadas en la 1ª). *(Si la consulta a Notion falla → el nodo debe cortar,
  NO crear duplicados: ver manejo de errores del diseño.)*
- [ ] **Paso 4:** Re-exportar y commit:
  ```bash
  git add buscartrabajo/workflows/busqueda-empleo-diaria.json
  git commit -m "feat(empleo): dedupe por Link oferta contra Notion antes del ranker"
  ```

---

## Tarea 3 — "Rankear ofertas" ordena y recorta (salida estructurada)

**Archivo:** nodo `Rankear ofertas` (LLM Groq) en el workflow

- [ ] **Paso 1:** Cambiar el prompt para que reciba la lista deduplicada y devuelva
  **JSON**: un array ordenado (mejor primero), máximo 10, de `{ link, motivo }`.
  Pasar las ofertas como JSON al prompt (`{{ JSON.stringify($json) }}` por item o
  un Aggregate previo). Pedir explícito: *"Devolvé SOLO un array JSON válido, sin
  texto alrededor, con los objetos {link, motivo} de las mejores 10 para Verónica,
  ordenadas de mejor a peor. Si hay menos de 10 buenas, devolvé menos."*
- [ ] **Paso 2:** Nodo Code "Unir motivo": parsear el JSON del LLM y volver a unir el
  `motivo` con el objeto de oferta completo por `link`, conservando el orden del LLM:
  ```js
  let ranked = [];
  try { ranked = JSON.parse(($json.text || '[]').trim()); } catch(e) { ranked = []; }
  const byLink = {};
  for (const it of $('Filtrar nuevas').all()) byLink[it.json.link] = it.json;
  return ranked.filter(r => byLink[r.link])
    .slice(0, 10)
    .map(r => ({ json: { ...byLink[r.link], motivo: r.motivo } }));
  ```
- [ ] **Paso 3:** "Probar ahora", abrir "Unir motivo". **Esperado:** ≤10 items,
  ordenados, cada uno con todos los campos + `motivo`. *(Si el LLM devuelve texto
  no-JSON, el `try/catch` deja `ranked=[]` → 0 items: revisar el prompt, no romper.)*
- [ ] **Paso 4:** Re-exportar y commit:
  ```bash
  git commit -am "feat(empleo): ranker devuelve top-10 estructurado y ordenado"
  ```

---

## Tarea 4 — Crear cada oferta en Notion (reusar nodo de WF2)

**Archivo:** copiar nodo `Notion - Crear Oferta` desde
`WF2-BuscarTrabajo-v2-Groq.json` al workflow, después de "Unir motivo"

- [ ] **Paso 1:** Copiar el nodo `Notion - Crear Oferta` tal cual (ya mapea
  empresa→título, puesto, salario, modalidad, link→"Link oferta",
  descripcion_corta→Notas, Estado="Pendiente"). Verificar que los campos del item
  de "Unir motivo" coinciden con los `$json.empresa`, `$json.puesto`, etc. que el
  nodo espera. Conectarlo para que reciba **un item por oferta** (se ejecuta N veces).
- [ ] **Paso 2:** "Probar ahora", abrir el nodo Notion y la DB en el navegador.
  **Esperado:** una página nueva por oferta, Estado=Pendiente, Link oferta poblado.
- [ ] **Paso 3:** Commit:
  ```bash
  git commit -am "feat(empleo): crear cada oferta real en Notion (Estado=Pendiente)"
  ```

---

## Tarea 5 — Un email diario con botones (adaptar de WF2)

**Archivo:** adaptar `Code - Preparar Email Notificacion` + `Brevo - Enviar
Notificacion` desde WF2; agrupar las N ofertas en UN email

- [ ] **Paso 1:** Tras "Notion - Crear Oferta", añadir un nodo que recoja **todas**
  las páginas creadas (Aggregate o `$input.all()`). Por cada oferta, construir un
  bloque HTML con sus 3 botones, usando el `id` de la página de Notion en los links:
  ```js
  const base = 'https://TU-N8N.onrender.com/webhook';
  const bloques = $input.all().map(it => {
    const id = it.json.id;                 // id de la página Notion creada
    const d  = it.json;
    const empresa = d.properties?.Empresa?.title?.[0]?.plain_text || 'Oferta';
    const link = d.properties?.['Link oferta']?.url || '#';
    return `<div style="margin:16px 0;padding:12px;border:1px solid #eee">
      <b>${empresa}</b><br><a href="${link}">Ver oferta</a><br>
      <a href="${base}/<RUTA_OCULTA>?id=${id}">✅ Aprobar</a> &nbsp;
      <a href="${base}/<RUTA_OCULTA>?id=${id}">❌ Descartar</a> &nbsp;
      <a href="${base}/<RUTA_OCULTA>?id=${id}">📤 Mandar</a>
    </div>`;
  }).join('');
  const brevoBody = JSON.stringify({
    sender: { name: 'Búsqueda Empleo', email: 'hello.cookyourweb@gmail.com' },
    to: [{ email: 'hello.cookyourweb@gmail.com' }],
    subject: `☀️ ${$input.all().length} ofertas nuevas hoy`,
    htmlContent: `<h2>Ofertas de hoy</h2>${bloques}`
  });
  return [{ json: { brevoBody, total: $input.all().length } }];
  ```
  *(Confirmar la URL base de n8n y el email destino reales antes de probar.)*
- [ ] **Paso 2:** Copiar el nodo `Brevo - Enviar Notificacion` de WF2 (usa
  `{{ $json.brevoBody }}`). La api-key va en el header como secreto en n8n.
- [ ] **Paso 3:** Añadir guarda "0 ofertas": si `total === 0`, NO mandar email (rama
  con IF). Evita un email vacío los días sin novedades.
- [ ] **Paso 4:** "Probar ahora". **Esperado:** llega UN email con las ofertas del día,
  cada una con sus 3 botones. Tocar **Aprobar** en una → a los minutos llega el email
  con CV adaptado + carta (eso lo hace la Mitad B, sin cambios).
- [ ] **Paso 5:** Commit:
  ```bash
  git commit -am "feat(empleo): email diario unico con botones aprobar/descartar/mandar"
  ```

---

## Tarea 6 — Telegram desde la lista estructurada + retirar generador falso

- [ ] **Paso 1:** El nodo Telegram ahora cuelga de "Unir motivo": un Code arma el
  texto top-5 a partir de los objetos (mismo formato lindo de antes) y lo manda al
  grupo Empleo `-5232143614`. Telegram = vistazo; email = accionable.
- [ ] **Paso 2:** En `WF2-BuscarTrabajo-v2-Groq.json`, **desactivar** el Schedule
  Trigger de la Mitad A (generador de ofertas inventadas) para que no cree falsas.
  Dejar la Mitad B (webhooks) ACTIVA. *(Solo desactivar el trigger; no borrar nodos.)*
- [ ] **Paso 3:** "Probar ahora" en la diaria + verificar que WF2 ya no genera falsas.
  **Esperado:** las ofertas en Notion son todas reales.
- [ ] **Paso 4:** Activar el workflow diario (toggle Active) y commit final:
  ```bash
  git commit -am "feat(empleo): telegram desde lista estructurada; retira generador falso WF2"
  ```

---

## Verificación de cobertura (self-review)

- ✅ Ofertas reales en Notion con Estado=Pendiente → Tarea 4
- ✅ Un email diario con botones → Tarea 5
- ✅ Aprobar dispara CV+carta → Mitad B existente (no se toca)
- ✅ Dedupe por URL → Tarea 2
- ✅ Mitad B intacta → Tareas 4-6 no tocan webhooks
- ✅ 0 ofertas → guarda en Tarea 5 paso 3
- ✅ Fuente caída → try/catch ya existente en Formatear ofertas

## Pendiente de confirmar al ejecutar (datos que solo Vero tiene)
- URL base real de la instancia n8n (para los links de botones).
- Email destino de revisión (¿hello.cookyourweb@gmail.com u otro?).
- Que los nombres de campos en la DB de Notion coinciden exactamente
  (Empresa/Puesto/Salario/Modalidad/Link oferta/Notas/Estado).
