# Spec 008 — Workflow diff guard

Estado: implementada

## Contexto y objetivo
`wf-check.mjs` ya contiene 8 reglas graves, pero no es testable ni estable para CI. Se busca convertir esas reglas en una biblioteca reutilizable, con salida JSON, sin cambiar el comportamiento de seguridad existente.

## Usuarios / actores
- Desarrollador que reconstruye el workflow.
- CI / scripts locales.
- Revisor de PR.

## Historias de usuario
- HU-1: Como desarrollador, quiero saber exactamente por qué no se puede importar un export.
- HU-2: Como CI, quiero una salida JSON estable.
- HU-3: Como mantenedor, quiero probar cada regla de forma aislada.

## Alcance V1
- Conservar las 8 reglas actuales.
- Añadir `--json`.
- Extraer la lógica a `scripts/lib/wf-check.mjs`.
- Añadir pruebas unitarias para cada regla principal.
- No modificar ni generar workflow.
- No rotar secrets.

## Requisitos funcionales
- RF-1: Si el workflow está partido (`@@FILE:`), el check falla de forma explicable.
- RF-2: Detecta nodos de código con cuerpos idénticos y roles distintos.
- RF-3: Compila cada nodo de código.
- RF-4: Detecta referencias colgantes a `$('X')`.
- RF-5: Valida Groq (`max_tokens`, `reasoning_effort`).
- RF-6: Valida Adzuna.
- RF-7: Verifica que lo calculado se devuelve.
- RF-8: Impide credenciales compartidas entre webhook y nodo externo.
- RF-9: Avisa de webhooks con path secreto sin redactar.
- RF-10: Con `--json`, emite JSON válido y estable.
- RF-11: Si no hay fallos, código de salida 0.
- RF-12: Si hay fallos, código de salida 1.

## Contrato de salida `--json`
- `ok: boolean`
- `nodes: number`
- `code_nodes: number`
- `warnings: string[]`
- `errors: string[]`
- `reviewed: boolean`

## Casos límite
- export con cero nodos de código
- nodo de código vacío
- dos hermanos con el mismo cuerpo
- referencia colgante
- Groq ausente
- Adzuna con `where=`
- credencial compartida
- warnings sin errores
- errors sin warnings

## Fuera de alcance
- auto-corrección del workflow
- cambios de n8n
- rotación de rutas
- nuevas reglas basadas en nuevas averías

## Criterios de finalización
- tests de reglas unitarias en verde
- salida `--json` validable
- comportamiento anterior preservado
- demo con un workflow inválido y uno válido