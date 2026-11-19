import { test } from 'node:test';
import assert from 'node:assert/strict';
import { analizarWorkflow } from '../scripts/lib/wf-check.mjs';

const nodo = (params = {}) => ({
  name: params.name ?? 'Code - Demo',
  type: 'n8n-nodes-base.code',
  parameters: { jsCode: params.code ?? 'return items;', ...params.parametros },
});

test('workflow minimo con un nodo de codigo valido', () => {
  const wf = { nodes: [nodo({ name: 'Code - A', code: 'return items;' })] };
  const r = analizarWorkflow(wf);
  assert.equal(r.ok, true);
  assert.equal(r.nodes, 1);
  assert.equal(r.code_nodes, 1);
});

test('dos nodos de codigo con el mismo cuerpo y roles distintos fallan', () => {
  const wf = {
    nodes: [
      { name: 'Code - A', type: 'n8n-nodes-base.code', parameters: { jsCode: 'return items;' } },
      { name: 'Code - Z', type: 'n8n-nodes-base.code', parameters: { jsCode: 'return items;' } },
    ],
  };
  const r = analizarWorkflow(wf);
  assert.equal(r.ok, false);
  assert.ok(r.errors.some(e => e.includes('codigo IDENTICO')));
});

test('dos hermanos con el mismo cuerpo son un aviso, no fallo', () => {
  const wf = {
    nodes: [
      { name: 'Code - Error', type: 'n8n-nodes-base.code', parameters: { jsCode: 'return items;' } },
      { name: 'Code - Error1', type: 'n8n-nodes-base.code', parameters: { jsCode: 'return items;' } },
    ],
  };
  const r = analizarWorkflow(wf);
  assert.equal(r.ok, true);
  assert.ok(r.warnings.some(e => e.includes('hermanos')));
});

test('referencia colgante a un nodo inexistente falla', () => {
  const wf = { nodes: [{ name: 'Code - A', type: 'n8n-nodes-base.code', parameters: { jsCode: "return $('No existe').json;" } }] };
  const r = analizarWorkflow(wf);
  assert.equal(r.ok, false);
  assert.ok(r.errors.some(e => e.includes("referencia a $('No existe')")));
});

test('codigo invalido no compila y falla', () => {
  const wf = { nodes: [{ name: 'Code - Bad', type: 'n8n-nodes-base.code', parameters: { jsCode: 'return {' } }] };
  const r = analizarWorkflow(wf);
  assert.equal(r.ok, false);
  assert.ok(r.errors.some(e => e.includes('no compila')));
});

test('workflow partido se detecta', () => {
  const wf = { marker: '@@FILE:', nodes: [] };
  const r = analizarWorkflow(wf);
  assert.equal(r.ok, false);
  assert.ok(r.errors.length >= 1);
});

test('salida estable', () => {
  const wf = { nodes: [{ name: 'Code - A', type: 'n8n-nodes-base.code', parameters: { jsCode: 'return items;' } }] };
  const r = analizarWorkflow(wf);
  assert.ok(Array.isArray(r.warnings));
  assert.ok(Array.isArray(r.errors));
  assert.equal(typeof r.ok, 'boolean');
});