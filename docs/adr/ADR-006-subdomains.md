# ADR-006. El producto vive en subdominios de cookyourwebai.es

**Fecha:** 2 oct 2026 · **Estado:** aceptado. Nombre del panel decidido el 7 oct 2026

---

## Contexto

El sistema deja de ser una herramienta personal y pasa a ser un producto de la
marca Cook Your Web, abierto por invitación. Tiene dos líneas:

- **Empleo:** encontrar ofertas, aprobarlas o descartarlas, y preparar la
  entrevista.
- **Formación:** los cursos. Su relación con el panel de empleo se decidirá aparte.

La web de la marca existe y está hecha en React. El panel está en Angular.

## Decisión

**Un dominio, cookyourwebai.es, con un subdominio por línea y otro para la API.**

- Panel de empleo: `empleo.cookyourwebai.es` (decidido el 7 oct 2026 frente a
  `carrera`, que es ambiguo: también es una carrera universitaria o deportiva).
  Se publica en Vercel, donde ya vive la web; el DNS del dominio está en IONOS.
- API: `api.cookyourwebai.es`.
- Formación: su propio subdominio, por ejemplo `formacion.cookyourwebai.es`.

**La web en React no se reescribe en Angular.** La web, el panel y la formación se
unen por tres cosas, no por el framework:

1. **Enlaces.** La web es la puerta de entrada y lleva a cada línea.
2. **Un mismo sistema de diseño.** Los mismos tokens, copiados de `cookyourwebai`
   con sus tests de contraste, como dice el
   [plan del panel](../diseno/2026-09-06-plan-arranque-panel-angular.md). Si
   mantenerlos en dos sitios duele, se extraen a un paquete.
3. **Una misma cuenta.** Todas las líneas usan Google y el mismo identificador
   interno ([ADR-003](ADR-003-autenticacion.md)). Compartir la sesión entre
   subdominios llegará con la cookie de sesión que ADR-003 deja como evolución.

## Por qué subdominios del mismo dominio

Para que el panel y la API sean del mismo sitio. Hoy la sesión va por token en
memoria (ADR-003), y el dominio común deja abierta la evolución a una cookie que
ningún script puede leer, sin cambiar de dominio. Con dominios distintos esa
cookie sería de terceros, y Safari y Firefox la bloquean por defecto: no es fiable.

Además los subdominios no cuestan nada: vienen con el dominio que ya se paga.

## Sobre el SEO

El nombre del subdominio pesa poco en el posicionamiento: Google posiciona por el
contenido. Y el panel vive detrás del inicio de sesión, así que Google no lo ve.

Lo que posiciona son las **páginas públicas** que explican cada línea. Esas páginas
se generan como HTML en el momento de publicar (`@angular/ssr` con
`outputMode: "static"`), sin servidor y sin coste. Esto modifica B1 del
[tablero](../diseno/2026-09-05-decisiones-arquitectura.md) solo para las páginas
públicas: el panel sigue siendo una aplicación de navegador.

**Pendiente:** si esas páginas públicas viven en el panel en Angular o en la web en
React.

## Consecuencias

**Se acepta:**

- Hay que configurar el DNS del dominio y publicar cada pieza en su subdominio.
- La web, el panel y la formación tienen que respetar el mismo sistema de diseño
  para sentirse un solo producto.

**Se gana:**

- Un producto con una sola marca y una sola cuenta.
- Ninguna reescritura: cada pieza sigue en la tecnología en la que está.

## Cuándo se revisa

Cuando se decida si la web integra el panel o solo lo enlaza. Hoy solo lo enlaza.

---

**Fuentes, consultadas el 2 oct 2026:** angular.dev/guide/ssr ·
developer.mozilla.org/en-US/docs/Web/Privacy/Guides/Third-party_cookies

**Relacionado:** [ADR-003](ADR-003-autenticacion.md) ·
[plan del panel](../diseno/2026-09-06-plan-arranque-panel-angular.md)
