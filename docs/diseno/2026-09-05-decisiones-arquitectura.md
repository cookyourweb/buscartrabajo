# Decisiones de arquitectura: tablero inicial

Fecha: 2026-09-05
Estado: listado para decidir, no decidido

Criterios que mandan, en este orden:

1. **El destino manda, no el plan gratuito de hoy.** Se diseña el sistema al que se
   quiere llegar y se elige hoy lo que no obligue a reescribir para llegar. Lo que sí
   sea de usar y tirar, se marca como tal.
2. **Coste cercano a cero mientras haya una sola usuaria.**
3. **Carga rápida.** Quien abra el enlace lo juzga en tres segundos.
4. **Que lo aprendido sea transferible** a una empresa con equipo grande.

Alcance: **el sistema se diseña multiusuario desde el primer día**, aunque hoy lo use
una sola persona. No hay un «cuando abramos el multiusuario»: hay un sistema
multiusuario con un usuario.

Los tres grupos de abajo separan lo que ya está cerrado, lo que se decide por
defecto sin discusión, y lo que hay que hablar de verdad.

---

## A. Ya cerrado

| # | Decisión | Elección |
|---|---|---|
| A1 | Framework de front | Angular última versión, standalone |
| A2 | Modelo de datos | Relacional, Postgres |
| A3 | Generación de CV y carta | `cv-server`, que ya existe |
| A4 | Captación de ofertas | n8n, sin cambios |
| A5 | Diseño previo | Figma con Variables, y design system propio |
| A6 | El navegador no habla con la base | Angular llama a `cv-server`; solo el backend toca Postgres |

A6 es el cambio de hoy. Elimina el patrón Backend-as-a-Service, que no se usa en
equipos grandes, y convierte al proveedor de base de datos en un detalle sustituible.

---

## B. Se deciden por defecto

Sin debate salvo que alguien objete. Todas van en la misma dirección: menos
JavaScript, menos servidores, menos factura.

| # | Decisión | Elección | Motivo |
|---|---|---|---|
| B1 | Renderizado | SPA cliente, sin SSR | El panel vive detrás de login. SSR no aporta y obliga a pagar un servidor Node |
| B2 | Alojamiento del front | Estático en CDN | Coste cero y primera carga desde el borde. Un front estático no tiene servidor que mantener |
| B3 | Estado | Signals nativos | NgRx sobra para este tamaño y añade peso y ceremonia |
| B4 | Detección de cambios | Sin zone.js | Menos JavaScript de arranque y menos trabajo por interacción |
| B5 | Carga de código | Lazy loading por ruta y bloques diferidos | Solo se descarga lo que se ve |
| B6 | Librería de componentes | Ninguna. Componentes propios sobre los tokens | Una librería pesa y además impone su estética, que es justo lo que queremos demostrar que sabemos construir |
| B7 | Estilos | CSS con custom properties | Los tokens son el contrato. Sin dependencia de build |
| B8 | Contrato de API | REST | GraphQL añade servidor, caché y complejidad que aquí no se pagan solos |
| B9 | Formularios | Reactive forms tipados | |
| B10 | Migraciones de base de datos | Alembic | El backend ya es Python |
| B11 | Fuentes | Alojadas con la app | Evita una conexión extra a un tercero y el salto de texto al cargar |
| B12 | Tests | Unitarios en el front, Playwright en el flujo principal | |

---

## C. Hay que hablarlo

Estas cuatro cambian el resultado. El resto son detalles.

### C1. Disponibilidad del backend (decidido)

En la arquitectura objetivo el backend está siempre disponible. Es un requisito y no
se negocia con el plan de alojamiento.

**Decidido, por sus propios méritos**: la demo pública no depende del backend. Un
escaparate debe cargar al instante y no puede caerse porque un servicio no responda.

Que hoy `cv-server` corra en un plan gratuito que se duerme es un asunto operativo
del momento, no una restricción de diseño. Se resuelve cambiando de plan el día que
haga falta.

### C2. Dónde vive Postgres

Con A6, el proveedor es sustituible. Pero el plan gratuito importa: algunos pausan
los proyectos que pasan días sin actividad, y un escaparate pasa semanas sin visitas.

Hay que comprobar, plan por plan y no de memoria, qué hace cada uno tras la
inactividad y cuánto tarda en volver. Candidatos: Supabase, Neon, Render.

Si la demo pública no toca la base (ver C1), este riesgo baja mucho.

### C3. La generación del CV tarda, porque llama a un modelo (decidido)

Una llamada a un LLM puede tardar bastantes segundos. Si la petición es síncrona, el
navegador se queda esperando y cualquier proxy puede cortarla.

**Decidido**: trabajo en segundo plano que el front consulta hasta que termina. Es lo
que aguanta cuando haya más de una usuaria, y cambiarlo después obliga a rehacer la
pantalla entera.

### C4. Autenticación: qué proveedor y qué protocolo

El protocolo es lo transferible: OIDC con OAuth2, guard e interceptor en Angular.
Eso funciona igual contra cualquier proveedor de identidad, incluido el de una
empresa grande.

Lo que falta decidir es contra quién se autentica y, sobre todo, que `cv-server`
valide el token en cada petición y deje de fiarse del email que llegue en el cuerpo.

---

## D. Coste, que es el criterio uno

| Partida | Cómo queda en cero |
|---|---|
| Front | Estático en CDN |
| Backend | Un solo servicio, el que ya existe. No se añaden más |
| Base de datos | Plan gratuito, pendiente de C2 |
| Llamadas al modelo | Es el único coste variable real. Hay que limitar cuántas puede lanzar un usuario y no repetir una generación ya hecha |
| Demo pública | Sin backend y sin base, si se resuelve C1 así |

La regla: **cada servicio nuevo que se añade hay que justificarlo.** Un servicio de
más es una factura de más y una cosa más que se puede caer durante una entrevista.
