# Plan 009 — Ofertas por usuaria

## Enfoque
Migrar la búsqueda diaria a `cv-server` una usuaria por llamada, reutilizando el change `ofertas-por-usuaria`. n8n queda como planificador/notificador.

## Decisiones
- Reutilizar endpoints existentes de cv-server (`/buscar-ofertas-reales`, `/crear-oferta`, `/puntuar-ofertas`, `/usuarios`).
- Añadir `POST /buscar-para-usuaria` que orquesta por usuaria.
- Portar filtros de n8n (prompt Groq + Normalizar Modalidad) a Python.
- Añadir campos al perfil: `regiones_remoto`, `ciudades_hibrido`, `tarifa_dia_min`, `evitar`.
- Respetar cuota Neon (8 unidades/mes, spend cap).
- gunicorn timeout 120s por usuaria.

## Riesgos
- gunicorn timeout por usuaria con muchas fuentes.
- Mezcla de datos entre usuarias si no se aísla por `usuario_id`.
- Cuota Neon agotada a mitad de mes.
- Adzuna 503 persistente.

## Orden de implementación
1. Extender perfil (migración + modelo).
2. Implementar `/buscar-para-usuaria`.
3. Portar filtros.
4. Actualizar n8n para llamar al endpoint.
5. Tests.
6. Retirar Phase 1.