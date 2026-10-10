# ADR-002. Dónde vive Postgres

**Fecha:** 2 oct 2026 · **Estado:** aceptado, a falta de confirmar la región al crear el proyecto · **Cierra:** C2 de [decisiones de arquitectura](../diseno/2026-09-05-decisiones-arquitectura.md)

---

## Contexto

A2 fija Postgres como modelo de datos y A6 fija que solo `cv-server` lo toca. Con
eso el proveedor es sustituible, pero el plan gratuito no es indiferente: un
proyecto personal pasa semanas sin uso, y la base no puede desaparecer ni quedarse
dormida sin que nadie la despierte.

**Cambio de criterio.** Desde el 2 de octubre de 2026 el coste cero pasa a ser el
primer criterio, por delante de "el destino manda" del tablero: todo en plan
gratuito mientras no haya una razón para pagar. Que la elección no obligue a
reescribir sigue siendo la condición para elegir entre opciones gratuitas.

El 2 de octubre de 2026 se comprobó en las páginas oficiales qué hace cada plan
gratuito tras la inactividad:

| | Render | Supabase | Neon |
|---|---|---|---|
| Tras inactividad | La base caduca a los 30 días de crearse, con 14 de gracia, y después **se borra con todos sus datos** | El proyecto **se pausa** tras 7 días de baja actividad | El cómputo se suspende a los 5 minutos sin uso |
| Cómo vuelve | No vuelve | **A mano**, entrando al panel | **Sola**, al llegar una consulta, en cientos de milisegundos |
| Copias | Ninguna | No verificado | Restauración a un punto de las últimas 6 horas |
| Plan gratuito | Caduca | No caduca, se pausa | Permanente, sin tarjeta |

## Decisión

**Neon, plan gratuito, en la Unión Europea, en la misma región que `cv-server`.**

- `cv-server` se conecta por cadena de conexión estándar y las migraciones son de
  Alembic. El código no usa ninguna función propia de Neon.
- Base y servidor en la misma región. Si no, cada consulta cruza un océano.
- Una rama de Neon aparte para desarrollo y pruebas. Nada se prueba contra los
  datos reales.

## Por qué no Render

Es el único que no añadiría proveedor, porque `cv-server` ya vive ahí. Pero una
base que se borra a los 44 días no sirve para datos reales, y pagar desde el primer
día va contra el criterio de coste.

## Por qué no Supabase

Falla justo en el riesgo que señalaba el tablero. Que la base se pause no es el
problema. El problema es que **no vuelve sola**: si nadie entra al panel de
Supabase, el sistema no arranca, y nadie se entera hasta que alguien intenta usarlo.

Mantenerlo despierto con una consulta programada es un apaño que añade otra pieza
que se puede caer.

## Consecuencias

**Se acepta:**

- Un proveedor nuevo. Es el único que añade esta decisión, y A2 ya lo exigía.
- 100 horas de cómputo al mes. Si se agotan, la base se suspende hasta el mes
  siguiente sin perder datos. Por eso ningún proceso puede consultar la base en
  bucle, ni `cv-server` ni n8n a través de él.
- Restauración de solo 6 horas atrás. Hace falta una copia propia periódica, fuera
  del proveedor. Se decide en un ADR aparte.
- 1 GB de almacenamiento.

**Se gana:**

- La base nunca necesita que nadie la despierte a mano.
- Pasar a pago no es una migración: es el mismo proyecto, facturado por uso y sin
  mínimo mensual.
- El proveedor sigue siendo un detalle. Cambiarlo es volcar, restaurar y cambiar
  una variable de entorno.

## Cuándo se revisa

Si Neon cambia las condiciones del plan gratuito, si se superan las horas de
cómputo dos meses seguidos, o si `cv-server` pasa a un plan de pago y compensa
tener la base a su lado.

**Pendiente al crear el proyecto:** Neon ofrece regiones en Frankfurt y Londres,
pero su página no aclara si están en el plan gratuito. Si no lo están, esta
decisión se revisa antes de guardar ningún dato personal.

---

**Fuentes, consultadas el 2 oct 2026:** neon.com/pricing ·
neon.com/docs/introduction/plans · neon.com/docs/introduction/scale-to-zero ·
neon.com/docs/introduction/regions · render.com/docs/free · supabase.com/pricing ·
supabase.com/docs/guides/platform/free-project-pausing

**Relacionado:** [ADR-003](ADR-003-autenticacion.md) ·
[ADR-005](ADR-005-notion-se-congela.md) · [modelo de datos](../diseno/2026-09-07-modelo-de-datos.md)
