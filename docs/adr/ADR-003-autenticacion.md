# ADR-003. Contra quién se autentica y qué valida el backend

**Fecha:** 2 oct 2026 · **Estado:** aceptado · **Cierra:** C4 de [decisiones de arquitectura](../diseno/2026-09-05-decisiones-arquitectura.md) · **Sustituirá:** [ADR-001](ADR-001-proteccion-de-los-webhooks.md), cuando `cv-server` sea el único que llama a n8n

---

## Estado a 7 de octubre de 2026

| Punto | Estado |
|---|---|
| 1. Token en memoria (Angular) | Implementado en `develop`, pendiente de despliegue |
| 2. Interceptor solo hacia `cv-server` | Implementado en `develop`, pendiente de despliegue |
| 3. Validación del token en `cv-server` | Implementado en `develop`, pendiente de despliegue |
| 4. `(iss, sub)` a identificador interno | Pendiente |
| 5. Capa de datos con dueño y 404 en recurso ajeno | Pendiente |
| 6. Invitación | Implementada con una lista `INVITADAS` por email. El vínculo con `(iss, sub)` queda pendiente hasta que exista Neon |
| 7. CORS sin comodín | Implementado en `develop`, pendiente de despliegue |

El guard de Angular protege solo las pantallas con datos reales. La demo pública
sigue abierta.

Las rutas del formulario público se eliminaron o se cerraron en `cv-server`
(`develop`) el 7 de octubre de 2026. La verificación en producción está pendiente
hasta que se despliegue.

---

## Contexto

`cv-server` todavía no identifica a las personas que lo llaman: hasta ahora solo
lo usaban procesos propios. El sistema se abre a otras personas, por invitación, y
eso exige saber quién pide cada cosa y que nadie vea lo de otra.

Como paso previo, el 2 de octubre de 2026 se cerraron las dos rutas que no podían
seguir abiertas: `/debug` se eliminó y `/usuarios` exige una clave de máquina.

El protocolo ya estaba decidido: OIDC con OAuth2, guard e interceptor en Angular.
Está descartado guardar contraseñas en `cv-server`. Faltaba el proveedor, y el
criterio es que sea **gratuito y no añada servicios** ([ADR-002](ADR-002-donde-vive-postgres.md)).

El 2 de octubre de 2026 se comprobó en las páginas oficiales:

- **Google** emite un ID token estándar, verificable por JWKS, con un `sub`
  estable. Pero **no ofrece a una aplicación de navegador el flujo de código con
  PKCE sin secreto**: el canje se hace en un backend, y el navegador no recibe
  token de renovación.
- **Auth0** sí ofrece ese flujo y 25.000 usuarios gratis. Pero **borra el tenant
  tras 150 días sin actividad**, sin posibilidad de recuperarlo.
- **Supabase Auth** emite tokens verificables por JWKS, pero vive dentro de un
  proyecto que se pausa a los 7 días.

## Decisión

**Google como proveedor OIDC directo. `cv-server` valida el token en cada petición.**

1. Angular obtiene el token de Google y lo guarda **en memoria**, nunca en
   `localStorage`.
2. Un interceptor lo añade solo a las peticiones dirigidas a `cv-server`. El token
   no entra nunca en un prompt ni viaja a un proveedor de modelos.
3. `cv-server` comprueba la firma por JWKS, que `iss` esté en la lista configurada
   (Google emite `accounts.google.com` y `https://accounts.google.com`), `aud`,
   `exp` y `email_verified`. El algoritmo es una constante en el código (RS256) y nunca
   se lee del token. Las claves del JWKS se guardan en caché 3600 s; un `kid`
   desconocido provoca una nueva descarga, como máximo cada 300 s.
4. `(iss, sub)` se traduce a un identificador interno. **El usuario sale del
   token y de ningún otro sitio**: lo que diga el cuerpo de la petición se ignora.
5. Toda consulta a datos con dueño pasa por una capa que exige ese identificador.
   Un recurso ajeno responde 404. Hay un test por ruta en el que una usuaria pide
   el recurso de otra y no lo obtiene.
6. **Invitación.** Se invita por email. En el primer acceso, con `email_verified`,
   ese email se vincula a `(iss, sub)`, y desde entonces solo cuenta `sub`. Un
   token válido de alguien no invitado recibe 403.
7. **CORS.** `cv-server` acepta solo los orígenes del panel y de desarrollo, sin
   comodín.

El emisor, la dirección del JWKS y la audiencia son configuración. **El código no
nombra a Google**: cambiar de proveedor es cambiar la configuración y el adaptador
de entrada en Angular. El algoritmo (RS256) es la excepción: es una constante.

`GET /yo` devuelve la identidad de quien entra. Responde 401 si el token falta o no
es válido, 403 si es válido pero la persona no está invitada, y 503 si falla el
proveedor o falta configuración.

## Por qué no Auth0

Es el flujo de manual y lo más parecido a lo que usa una empresa grande. Pero
añade un servicio, y su plan gratuito borra el tenant a los 150 días de silencio,
que es lo que le pasa a un proyecto personal que pasa meses sin uso.

Vuelve a estar sobre la mesa si hace falta entrar sin cuenta de Google.

## Por qué no Supabase Auth

No incumple A6 en la letra: el navegador hablaría con un proveedor de identidad,
no con la base. Pero ata la identidad a un proyecto que se pausa.

## Consecuencias

**Se acepta:**

- Solo entra quien tenga cuenta de Google.
- Sin token de renovación en el navegador: la sesión se renueva pidiendo otro
  token a Google, en principio sin que la usuaria lo note. Hay que medirlo.
- El ID token se usa como credencial ante la API propia. No es lo canónico, y se
  sabe. Es defendible porque `aud` es el identificador de cliente de las
  aplicaciones de la marca, y el backend es suyo.
- Con el token en memoria, cada aplicación (empleo, formación) pide su propio
  token a Google. Entrar una vez y que sirva en todas llega con la evolución de
  abajo.

**Se gana:**

- Ningún servicio nuevo, ningún plan que caduque, ninguna contraseña que custodiar.
- Lo aprendido se traslada: guard, interceptor, token en memoria y validación por
  JWKS son iguales contra cualquier proveedor.

## Los enlaces del correo y las llamadas de n8n

Hoy los enlaces de aprobar y descartar son peticiones GET con efectos, a webhooks de
n8n protegidos solo por una ruta impredecible (ADR-001). Los filtros de correo
abren enlaces por su cuenta.

- Pasan a llevar un **token firmado por `cv-server`**, de un solo propósito y con
  caducidad. El enlace abre una página del panel que muestra la oferta y un botón;
  el botón hace POST a `cv-server`, que valida el token. **Repetir el POST no
  repite la acción.**
- Si esa página pide iniciar sesión o si el token basta como autorización está
  **pendiente de decidir**.
- `cv-server` pasa a ser **el único que llama a n8n**. Ese día ADR-001 queda
  sustituido entero.
- Las llamadas de n8n a `cv-server` llevan una **clave de máquina** en la cabecera
  `X-Clave-Maquina`, distinta de la identidad de las personas. ADR-001 midió que la
  autenticación por cabecera fallaba en los webhooks que **recibe** n8n. Aquí n8n
  **envía** la cabecera, que es otro caso, pero hay que medirlo y comprobar después
  que la credencial de Groq del workflow sigue viva.
- **Medido el 4 de octubre de 2026.** n8n envía `X-Clave-Maquina` con una credencial
  Header Auth propia ("cv-server clave de maquina") en los nodos de `/generar-cv` y
  `/generar-carta`; la credencial de Groq sigue en su nodo, sin tocar. `cv-server`
  exige la clave en `/registro`, `/usuarios`, `/generar-cv`, `/generar-carta`,
  `/crear-oferta` y `/buscar-ofertas-reales`: sin ella responde 401 y no llama al modelo. Importar un
  workflow encima de uno existente no conservó la credencial: se puso a mano.

## Cuándo se revisa

Al publicar el panel en su subdominio ([ADR-006](ADR-006-subdominios.md)). Panel y
API comparten dominio, y eso permite que el canje lo haga `cv-server` y la sesión
viaje en una cookie que ningún script puede leer. Si se da ese paso, cambia el
punto 3 (JWKS se valida solo al entrar) y aparece la protección contra CSRF: será
un ADR nuevo que sustituya a este.

---

**Fuentes, consultadas el 2 oct 2026:**
developers.google.com/identity/openid-connect/openid-connect ·
developers.google.com/identity/oauth2/web/guides/use-code-model ·
developers.google.com/identity/gsi/web/guides/verify-google-id-token ·
auth0.com/pricing · supabase.com/docs/guides/auth/jwts

**Relacionado:** [ADR-001](ADR-001-proteccion-de-los-webhooks.md) ·
[ADR-004](ADR-004-cada-usuaria-trae-su-clave-de-ia.md) ·
`cv-server/tests/test_rutas_cerradas.py`
