# Spec 009 — Ofertas por usuaria (búsqueda multiusuaria en cv-server)

Estado: borrador

## Contexto y objetivo
Mover la búsqueda diaria de ofertas de n8n a `cv-server`, una usuaria por llamada, leyendo el perfil desde Postgres/Neon. n8n queda solo como planificador y notificador. Reutiliza el change `ofertas-por-usuaria` (explore + proposal, 21-oct) en vez de crear uno paralelo.

Phase 1 (filtro por usuaria en n8n) es un stop-gap y se retira cuando esta spec se implemente.

## Usuarios / actores
- Usuaria registrada con perfil activo (`busqueda_activa`).
- n8n (disparador a las 9:00, un webhook por usuaria).
- cv-server (ejecuta búsqueda, filtrado, puntuación y creación de oferta).
- Panel de empleo (lectura de ofertas/candidaturas por usuaria).

## Historias de usuario
- HU-1: Como usuaria, quiero que la búsqueda diaria use MI perfil (ciudad, salario, stack, modalidad, evitar), no el de otra persona.
- HU-2: Como usuaria, quiero recibir solo ofertas que encajan con mis criterios.
- HU-3: Como operador, quiero que una usuaria que falla no rompa la búsqueda de las demás.
- HU-4: Como operador, quiero trazabilidad por usuaria, oferta y fecha.

## Alcance V1
- Endpoint `POST /buscar-para-usuaria` en cv-server que procesa una sola usuaria.
- Lectura de perfil desde Postgres (`perfil`) + campos nuevos (`regiones_remoto`, `ciudades_hibrido`, `tarifa_dia_min`, `evitar`).
- Fuentes: Remotive + Tecnoempleo + Google Jobs (SerpApi) + Adzuna (si disponible).
- Filtrado per-usuaria portado desde n8n (prompt Groq + Normalizar Modalidad).
- Creación de oferta en Notion y puntuación por usuaria.
- Cuota Neon (8 unidades/mes, spend cap) respetada.
- n8n: bucle por usuaria con continue-on-error, scoring una vez.

## Requisitos funcionales
- RF-1: `POST /buscar-para-usuaria` acepta `usuario_id` y devuelve resumen (ofertas encontradas, creadas, descartadas, error).
- RF-2: El perfil se lee de Postgres; si falta un campo, se usa default seguro y se registra aviso.
- RF-3: Ningún dato de una usuaria se mezcla con el de otra (aislamiento por `usuario_id`).
- RF-4: Una usuaria con `busqueda_activa=false` se salta sin error.
- RF-5: Un fallo en una usuaria no detiene el bucle de n8n (continue on error).
- RF-6: La puntuación se ejecuta una sola vez al final del bucle.
- RF-7: Se respeta la cuota Neon (gasto acumulado por mes).
- RF-8: Trazabilidad: log por usuaria, oferta y fecha (sin datos personales sensibles).

## Contrato de salida `/buscar-para-usuaria`
- `usuario_id: int`
- `ofertas_encontradas: int`
- `ofertas_creadas: int`
- `ofertas_descartadas: int`
- `errores: string[]`
- `duracion_ms: int`

## Casos límite
- Usuaria sin perfil completo.
- Fuente caída (Adzuna 503, Tecnoempleo vacío).
- Groq devuelve plantilla vacía.
- Oferta duplicada por enlace / empresa+puesto.
- Cuota Neon agotada.
- Timeout de gunicorn (120s) por usuaria.

## Fuera de alcance
- Migración completa de Notion a Neon (ADR-005, otra spec).
- Pagos / billing por usuaria.
- Frontend de configuración avanzada (Phase 1 ya cubre perfil básico).

## Criterios de finalización
- Endpoint implementado y probado con usuaria de prueba.
- Tests unitarios de filtrado y aislamiento.
- n8n actualizado para llamar al endpoint (sin lógica de filtrado en nodos).
- Phase 1 retirado o marcado deprecated.
- Verificación con Chrome DevTools en móvil.