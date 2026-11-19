# MEMORY.md

## Proyecto
- Sistema integrado de búsqueda de trabajo.
- `buscartrabajo/` es el orquestador principal.
- Subsistemas: `panel-empleo`, `cv-server`.

## Decisiones técnicas
- Memoria compartida vía Engram (proyecto `buscartrabajo`).
- SDD activo a partir de la constitución.
- Agentes coordinados: `bt-coordinator`, `bt-planner`, `bt-implementer`, `bt-reviewer`.

## Backlog de validación
- Probar flujo SDD completo con una spec pequeña.
- Verificar Chrome DevTools + móvil.
- Comparar memoria Claude/OpenCode.