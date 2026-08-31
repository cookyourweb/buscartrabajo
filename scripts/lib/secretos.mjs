// Los `path` de los webhook de n8n son SECRETOS, y este repositorio es PUBLICO.
//
// Quien conoce el path, dispara el webhook. El de busqueda se protegio el
// 30-ago-2026 justamente por ahi (path impredecible), y los de aprobar,
// descartar y mandar-empresa NO piden ninguna credencial (issue #1): para esos,
// el path es lo unico que los separa de cualquiera que sepa leer el repo.
//
// Esta funcion vivia dentro de `wf-split.mjs` y solo corria al partir el
// workflow. Sale aqui porque hace falta en dos sitios: al partir, y al limpiar
// los backups crudos que se exportaron ANTES de que wf-split existiera.
// Extraida el 31-ago-2026, con tests en tests/secretos.test.mjs.

/** Marcador que sustituye al path en el JSON publicable. */
export const PREFIJO_SECRETO = '@@SECRET:';

const esWebhook = (nodo) => typeof nodo?.type === 'string' && nodo.type.endsWith('webhook');

/**
 * Saca los paths de webhook de un workflow de n8n.
 *
 * No muta la entrada: devuelve una copia redactada y los secretos aparte, para
 * que quien la llame pueda seguir usando el original.
 *
 * Es idempotente: un workflow ya redactado se queda igual y no aporta secretos,
 * porque un marcador no es un secreto. Asi se puede pasar dos veces sin miedo.
 *
 * @param {object} workflowOriginal export de n8n
 * @returns {{workflow: object, secretos: Record<string,string>}}
 */
export function redactarPaths(workflowOriginal) {
  const workflow = structuredClone(workflowOriginal);
  const secretos = {};

  for (const nodo of workflow.nodes ?? []) {
    const p = nodo.parameters;
    if (!esWebhook(nodo) || typeof p?.path !== 'string') continue;
    if (p.path.startsWith(PREFIJO_SECRETO)) continue;   // ya redactado

    secretos[nodo.name] = p.path;
    p.path = `${PREFIJO_SECRETO}${nodo.name}`;
  }

  // Las rutas no viven solo en el campo `path`. Los nodos de codigo que arman
  // los enlaces de los correos las llevan ESCRITAS DENTRO del jsCode:
  //   '<a href="https://host/webhook/' + RUTA + '?id=' + pageId + '">'
  // Redactar solo el campo `path` las dejaba ahi, y bastaba con rotar y volver a
  // partir el workflow para publicarlas otra vez. Segunda pasada por texto.
  for (const [nombre, path] of Object.entries(secretos)) {
    for (const nodo of workflow.nodes ?? []) {
      const p = nodo.parameters;
      if (!p) continue;
      for (const campo of ['jsCode', 'jsonBody', 'text', 'html']) {
        if (typeof p[campo] === 'string' && p[campo].includes(path)) {
          p[campo] = p[campo].split(path).join(`${PREFIJO_SECRETO}${nombre}`);
        }
      }
    }
  }

  return { workflow, secretos };
}

/**
 * Busca paths de webhook sin redactar. Devuelve los nombres de los nodos que
 * los llevan, o lista vacia si el workflow es publicable.
 *
 * Es la comprobacion que faltaba: `redactarPaths` limpia, y esta AVISA. Se usa
 * en wf-check y en el hook de pre-commit, donde no se quiere modificar nada,
 * solo impedir que un secreto salga hacia un repo publico.
 */
export function pathsSinRedactar(workflow) {
  return (workflow?.nodes ?? [])
    .filter((n) => esWebhook(n)
      && typeof n.parameters?.path === 'string'
      && !n.parameters.path.startsWith(PREFIJO_SECRETO))
    .map((n) => n.name);
}

/**
 * Une los secretos encontrados en un fichero con los que ya estaban guardados,
 * SIN pisar ninguno.
 *
 * 31-ago-2026: redactando los backups historicos, el path VIEJO de un webhook ya
 * rotado piso al vivo en secrets.local.json porque se hacia `Object.assign`.
 * Nadie lo habria visto hasta intentar rehacer el workflow con un path muerto.
 *
 * `secrets.local.json` guarda los paths VIVOS. Un fichero historico solo puede
 * APORTAR un nombre que falte, nunca cambiar uno que ya esta: si algo esta ahi,
 * es porque es lo que hay en produccion.
 *
 * @param {Record<string,string>} existentes lo ya guardado (manda)
 * @param {Record<string,string>} nuevos     lo encontrado ahora
 */
export function fusionarSecretos(existentes, nuevos) {
  const fusion = { ...existentes };
  for (const [nombre, path] of Object.entries(nuevos)) {
    if (!(nombre in fusion)) fusion[nombre] = path;
  }
  return fusion;
}
