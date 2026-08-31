// El path de un webhook de n8n es un SECRETO, y este repositorio es PUBLICO.
//
// Desde el 30-ago-2026 el webhook de busqueda se protege por path impredecible:
// quien conoce el path, dispara el webhook. Y hay tres webhooks mas -aprobar,
// descartar y mandar-empresa- que no piden NINGUNA credencial (issue #1), asi que
// para esos el path es lo unico que los separa de cualquiera que sepa leer.
//
// `wf-split` ya los saca a secrets.local.json al partir el workflow. Estos tests
// fijan ese comportamiento y, sobre todo, cubren el caso que wf-split NO cubria:
// los backups crudos exportados de n8n ANTES de que wf-split existiera, que
// llevan los paths en claro y estaban a un `git push` de publicarse.
import { test } from 'node:test';
import assert from 'node:assert/strict';

import { redactarPaths, pathsSinRedactar, fusionarSecretos, PREFIJO_SECRETO } from '../scripts/lib/secretos.mjs';

/** Un export de n8n reducido a lo que importa aqui. */
const workflowDePrueba = () => ({
  name: 'PROD',
  nodes: [
    {
      name: 'Webhook Aprobar',
      type: 'n8n-nodes-base.webhook',
      parameters: { path: 'ruta-real-que-no-debe-publicarse', httpMethod: 'GET' },
    },
    {
      name: 'Code - Normalizar Modalidad',
      type: 'n8n-nodes-base.code',
      parameters: { jsCode: 'return items;' },
    },
    {
      name: 'Webhook sin path',
      type: 'n8n-nodes-base.webhook',
      parameters: { httpMethod: 'POST' },
    },
  ],
});

test('el path de un webhook sale del workflow y queda en secretos', () => {
  const { workflow, secretos } = redactarPaths(workflowDePrueba());

  const webhook = workflow.nodes.find((n) => n.name === 'Webhook Aprobar');
  assert.equal(webhook.parameters.path, `${PREFIJO_SECRETO}Webhook Aprobar`);
  assert.equal(secretos['Webhook Aprobar'], 'ruta-real-que-no-debe-publicarse');
});

test('el path real no sobrevive en NINGUNA parte del workflow redactado', () => {
  const { workflow } = redactarPaths(workflowDePrueba());

  assert.ok(
    !JSON.stringify(workflow).includes('ruta-real-que-no-debe-publicarse'),
    'el secreto sigue en el JSON: publicarlo filtraria el webhook',
  );
});

test('lo que no es un webhook no se toca', () => {
  const { workflow } = redactarPaths(workflowDePrueba());

  const code = workflow.nodes.find((n) => n.name === 'Code - Normalizar Modalidad');
  assert.equal(code.parameters.jsCode, 'return items;');
});

test('un webhook sin path no revienta ni inventa un secreto', () => {
  const { secretos } = redactarPaths(workflowDePrueba());

  assert.equal(secretos['Webhook sin path'], undefined);
});

test('redactar dos veces deja el mismo resultado', () => {
  const primera = redactarPaths(workflowDePrueba());
  const segunda = redactarPaths(primera.workflow);

  assert.equal(
    segunda.workflow.nodes.find((n) => n.name === 'Webhook Aprobar').parameters.path,
    `${PREFIJO_SECRETO}Webhook Aprobar`,
  );
  assert.equal(
    Object.keys(segunda.secretos).length,
    0,
    'un marcador no es un secreto: redactar lo ya redactado no debe recogerlo',
  );
});

test('no modifica el objeto que recibe', () => {
  const original = workflowDePrueba();
  redactarPaths(original);

  assert.equal(
    original.nodes[0].parameters.path,
    'ruta-real-que-no-debe-publicarse',
    'redactarPaths no puede mutar su entrada: quien la llame puede seguir necesitandola',
  );
});

// ── El caso REAL, y el que motivo todo esto ──────────────────────────────────
// 31-ago-2026: nueve ficheros `BACKUP-CsvmtPcLVmGIZg6C-*.json` pendientes de
// subir llevaban EN CLARO el path de tres webhooks que no piden credencial.
// Son exports crudos, anteriores a wf-split, con la forma de abajo.
test('regresion: un backup crudo de n8n queda limpio tras redactar', () => {
  const backupCrudo = {
    name: 'BuscarTrabajo PROD',
    nodes: [
      { name: 'Webhook Aprobar', type: 'n8n-nodes-base.webhook', parameters: { path: 'aprobar-xyz' } },
      { name: 'Webhook Descartar', type: 'n8n-nodes-base.webhook', parameters: { path: 'descartar-xyz' } },
      { name: 'Webhook Mandar Empresa', type: 'n8n-nodes-base.webhook', parameters: { path: 'mandar-xyz' } },
    ],
    connections: {},
  };

  const { workflow, secretos } = redactarPaths(backupCrudo);
  const texto = JSON.stringify(workflow);

  for (const path of ['aprobar-xyz', 'descartar-xyz', 'mandar-xyz']) {
    assert.ok(!texto.includes(path), `el backup redactado todavia contiene "${path}"`);
  }
  assert.equal(Object.keys(secretos).length, 3);
});

// ── pathsSinRedactar: la comprobacion que no modifica nada ───────────────────
// `redactarPaths` limpia; esta AVISA. Es la que puede correr en un hook de
// pre-commit o en CI, donde no se quiere tocar el fichero, solo impedir que un
// secreto salga hacia un repo publico.

test('pathsSinRedactar delata los webhook que llevan el path en claro', () => {
  const nombres = pathsSinRedactar(workflowDePrueba());

  assert.deepEqual(nombres, ['Webhook Aprobar']);
});

test('pathsSinRedactar no encuentra nada en un workflow ya redactado', () => {
  const { workflow } = redactarPaths(workflowDePrueba());

  assert.deepEqual(pathsSinRedactar(workflow), []);
});

test('pathsSinRedactar aguanta un workflow sin nodos', () => {
  assert.deepEqual(pathsSinRedactar({}), []);
  assert.deepEqual(pathsSinRedactar(null), []);
});

// ── fusionarSecretos ─────────────────────────────────────────────────────────
// 31-ago-2026, fallo real cometido al redactar los once backups: los ficheros
// historicos traian el path VIEJO de un webhook que ya se habia rotado, y el
// script hacia Object.assign, asi que el path muerto PISO al vivo en
// secrets.local.json. Nadie habria visto nada hasta intentar rehacer el workflow.
//
// Es el mismo bicho que el del 30-ago en n8n: lo compartido se pisa en silencio.
//
// Regla: secrets.local.json guarda los paths VIVOS. Un backup solo puede APORTAR
// nombres que falten, nunca cambiar uno que ya esta.

test('fusionar no deja que un backup viejo pise un secreto vivo', () => {
  const vivos = { 'Webhook Buscar': 'path-nuevo-rotado-y-vivo' };
  const delBackup = { 'Webhook Buscar': 'path-viejo-y-muerto' };

  assert.equal(
    fusionarSecretos(vivos, delBackup)['Webhook Buscar'],
    'path-nuevo-rotado-y-vivo',
  );
});

test('fusionar SI incorpora un nombre que no estaba', () => {
  const vivos = { 'Webhook Buscar': 'path-vivo' };
  const delBackup = { 'Webhook Aprobar': 'path-de-aprobar' };

  assert.deepEqual(fusionarSecretos(vivos, delBackup), {
    'Webhook Buscar': 'path-vivo',
    'Webhook Aprobar': 'path-de-aprobar',
  });
});

test('fusionar no muta lo que ya habia', () => {
  const vivos = { 'Webhook Buscar': 'path-vivo' };
  fusionarSecretos(vivos, { 'Webhook Buscar': 'otro', 'Nuevo': 'x' });

  assert.deepEqual(vivos, { 'Webhook Buscar': 'path-vivo' });
});
