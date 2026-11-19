# Plan 008 — Workflow diff guard

## Cambios
- Extraer `analizarWorkflow` en `scripts/lib/wf-check.mjs`.
- Refactorizar `scripts/wf-check.mjs` para usar la biblioteca.
- Añadir salida `--json`.
- Añadir tests unitarios en `tests/wf-check.test.mjs`.

## Criterios
- 8 reglas conservadas.
- salida estable.
- npm test verde.
- workflow real validado.