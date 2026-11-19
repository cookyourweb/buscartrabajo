# Spec 001 — Mejorar reporte de `check-secretos`

Estado: implementada

## Contexto y objetivo
Hoy `check-secretos` detecta bien las rutas prohibidas, pero su salida humana no es estable. Se busca hacer el fallo más directo y añadir salida JSON pura para CI, manteniendo separadas las dos vistas.

## Usuarios / actores
- Desarrollador que modifica workflows.
- CI / hook de pre-commit.
- Revisor de PR.

## Historias de usuario
- HU-1: Como desarrollador, quiero saber exactamente qué ruta prohibida falló y en qué archivo.
- HU-2: Como CI, quiero salida estable con `--json`.
- HU-3: Como revisor, quiero un mensaje claro de cómo corregir.

## Alcance
- Reporte humano siempre.
- Reporte JSON con `--json`, puro y separado.
- Sin auto-corrección.
- Sin escaneo de históricos.

## Requisitos funcionales
- RF-1: Cuando detecta una violación por forma, reporta archivo y causa exacta.
- RF-2: Cuando detecta una violación por valor, reporta archivo y nodos encontrados.
- RF-3: Cuando detecta literales, reporta archivo y literal (con límite si procede).
- RF-4: Con `--json`, emite JSON válido.
- RF-5: Sin violaciones: exit 0.
- RF-6: Con violaciones: exit 1.
- RF-7: JSON inválido se omite en forma, sin abortar toda la ejecución.
- RF-8: No modifica archivos.

## Contrato de salida `--json`
- `ok: boolean`
- `violations: Array<{file: string, type: string, detail: string}>`
- `reviewed_files: number`
- `secrets_file_present: boolean`

## Casos límite
- más de una violación por archivo
- archivo con JSON inválido
- ruta literal en tests/docs
- ruta viva rotada pero con literal muerto
- sin `secrets.local.json`
- fallo mixto de forma + valor + literal

## Fuera de alcance
- auto-redacción
- escaneo histórico
- rotación automática de rutas en n8n

## Criterios de finalización
- tests existentes verdes
- nuevo test para salida JSON
- salida estable y ordenada
- demo de fallo/sin fallo