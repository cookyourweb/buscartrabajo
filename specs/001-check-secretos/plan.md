# Plan 001 — Mejorar `check-secretos`

## Objetivo
Añadir una salida JSON estable sin romper la salida humana actual.

## Alcance
- Parsear `--json` desde `process.argv`.
- Reutilizar las validaciones existentes.
- Construir un objeto `violations` ordenado por archivo.
- No modificar el formato humano actual.

## Archivos
- `scripts/check-secretos.mjs`
- `tests/secretos.test.mjs`

## Reglas
- JSON puro, sin texto mêzclado.
- Si no hay violaciones, `violations` vacío.
- `reviewed_files` cuenta todos los ficheros revisados por forma.
- `secrets_file_present` indica si existe `secrets.local.json`.

## Criterios
- tests existentes siguen verdes
- nuevas pruebas cubren `--json`
- salida ordenada y estable