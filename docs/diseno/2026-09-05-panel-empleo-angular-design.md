# Panel de empleo en Angular: diseño

Fecha: 2026-09-05
Estado: propuesta, pendiente de aprobación
Autora de las decisiones: Verónica Serna

## 1. Qué es esto

La cara de un sistema que ya funciona.

Hoy el sistema existe y está en producción, pero repartido: un workflow de n8n capta
ofertas, `cv-server` genera el CV adaptado, diecinueve scripts de Python hacen el
resto y Notion sirve a la vez de almacén y de interfaz. Se maneja por línea de
comandos.

Este proyecto construye la interfaz web de ese sistema. No inventa producto nuevo:
unifica el que ya hay.

## 2. Alcance: multiusuario desde el diseño, una usuaria hoy

El sistema **es multiusuario desde el primer día**. Lo que ocurre hoy es que solo hay
una fila en la tabla de usuarios.

Esto no es un matiz de redacción. Significa que no existe un «cuando abramos el
multiusuario»: no hay dos modos, no hay migración pendiente y no hay condicionales
repartidos por el código. Hay un sistema multiusuario con un usuario.

Entra en el diseño desde ahora:

| Entra desde el día uno | Por qué |
|---|---|
| `user_id` en todas las tablas | Añadirlo después obliga a migrar datos y a tocar todas las consultas |
| Toda consulta filtra por usuario | El aislamiento no se retro-encaja. Se olvida una consulta y se filtran datos ajenos |
| Autenticación real, con la identidad saliendo de un token | Es el agujero que ya existe en `cv-server` y en `tu-vuelta-al-sol`. Nace bien o nace mal |
| Control de gasto por usuario | Las llamadas al modelo son el único coste variable. Sin límite por usuario no se puede abrir a nadie |
| La capa de datos detrás de una interfaz | Permite la demo pública y permite testear sin red |

Queda fuera solo lo que es producto y se añade sin tocar la arquitectura: pantallas
de alta e invitaciones, roles y permisos finos, panel de administración y facturación.

## 3. Objetivos

- Sustituir la línea de comandos y Notion como interfaz de trabajo diaria.
- Ser código público defendible: un tech lead abre el repo y ve criterio.
- Convertir Angular y Figma, hoy huecos declarados, en experiencia real bajo la regla
  del CV: una tecnología entra solo si se tiene de verdad.

## 4. Dos despliegues

| | Datos | Dónde | Para quién |
|---|---|---|---|
| **Real** | Los de Verónica | Local o privado | Ella, a diario |
| **Demo** | De ejemplo, incluidos en el propio front | Público, estático | Quien abra el enlace |

La demo no toca backend ni base de datos. No es un parche a ningún plan gratuito: un
escaparate debe cargar al instante y no puede depender de que un servicio esté vivo.

Esto no se resuelve con un `if`. La aplicación depende de una interfaz de datos y se
inyecta una implementación u otra.

## 5. Decisiones tomadas

| Decisión | Elección | Motivo |
|---|---|---|
| Framework | Angular última versión, standalone y signals | Hueco a cubrir; decisión del 22-jul-2026 |
| Base de datos | Postgres | Los datos son relacionales y hacen falta constraints |
| Quién habla con la base | Solo el backend | El navegador nunca toca la base ni ve un token de terceros |
| Backend | `cv-server`, que ya existe | Ya funciona, con guardrails y tests. No se añaden servicios |
| Autenticación | OIDC, con `cv-server` validando el token en cada petición | Lo transferible es el protocolo, no el proveedor |
| Captación | n8n, sin cambios | Está en producción |
| Notion | Solo como entrada de n8n | Deja de ser almacén y deja de ser interfaz |
| Diseño | Figma con Variables, antes del código | Es evidencia pública, igual que Angular |

### Por qué Notion deja de ser la base de datos

Notion es una herramienta de trabajo humano con una API encima. No tiene constraints,
ni integridad referencial, ni transacciones, y su API va a unas tres peticiones por
segundo.

Ya falló por esto, y está documentado en el propio repositorio. De la cabecera de
`cv-server/tests/test_usuario_multicuenta.py`: al no poder declarar que un usuario es
único, hubo que crear dos registros para la misma persona, los dos derivaron y el CV
salió con la cabecera equivocada. Un `UNIQUE` lo habría impedido.

## 6. Arquitectura

```
Angular (navegador)
  |
  '-- cv-server (FastAPI)
        |
        |-- Postgres
        '-- Drive, modelos de lenguaje, plantillas

n8n, fuera de la aplicación: capta ofertas.
  En la rebanada 1 sigue escribiendo en Notion y una sincronización las lleva
  a la base. Que escriba directo en Postgres es trabajo aparte.
```

Reglas que sostienen esto:

- El navegador no ve nunca un token de Notion, de Drive ni de un modelo.
- La aplicación no habla con Notion. Nunca.
- `cv-server` deja de fiarse del email que llegue en el cuerpo de la petición.

## 7. Modelo de datos

Cinco tablas. Todas con `user_id`, aunque hoy solo haya un valor.

- `profiles`: una fila por persona.
- `profile_emails`: los buzones de una persona. Resuelve el caso de los dos correos
  sin duplicar la persona. `UNIQUE(email)`.
- `offers`: ofertas captadas. Empresa, puesto, descripción, origen, fecha.
- `applications`: relación entre persona y oferta. Estado, fecha de envío, vía. Aquí
  vive el seguimiento.
- `documents`: CVs y cartas generados. Apuntan a una `application` y guardan el
  enlace de Drive y los avisos de los guardrails.

## 8. Generación de documentos: en segundo plano

Generar un CV llama a un modelo de lenguaje y puede tardar bastantes segundos. Una
petición síncrona deja el navegador esperando y cualquier proxy puede cortarla.

La generación se encola y el front consulta el estado hasta que termina. Se construye
así desde el principio: es lo que aguanta cuando haya más de una usuaria, y cambiarlo
después obliga a rehacer la pantalla entera.

## 9. Design system

Nace de la marca de CookYourWeb, que existe pero está desconectada del código.

Punto de partida verificado en `cookyourwebai`: cuatro colores de marca en
`tailwind.config.ts` (`#32e2ec`, `#ec32c7`, `#8f32ec`, `#3fec71`), mientras los tokens
semánticos de `index.css` siguen con los grises del template. Los neones se repiten a
mano hasta ocho veces y hay un `#BB60D1` que no está declarado en ninguna paleta.

El camino, en orden:

1. Los cuatro colores entran en Figma como Variables, con escala completa. Un color de
   marca es una rampa, no un valor.
2. Se miden los contrastes. Los neones están pensados para fondo oscuro; el cian y el
   verde no alcanzan 4.5:1 sobre blanco. Cada token declara sobre qué fondo vive.
3. Las Variables se conectan a los tokens semánticos conservando los nombres que ya
   existen: `primary`, `muted`, `destructive`, `border`, `ring`. No se inventan nombres.
4. Los tokens bajan a Angular como CSS custom properties. Ese es el puente. No se
   exporta código desde Figma.
5. Cada componente de Figma, con sus variantes, se corresponde con un componente
   standalone de Angular donde cada variante es un `input` tipado.

El design system se construye para el panel. `cookyourweb.es` se migra después, y por
eso se conservan los nombres de token.

## 10. Qué pasa con Notion

Notion se usa hoy como CRM visual y contiene tres dominios distintos: **ofertas de
empleo**, **leads de CookYourWeb** y **facturas**. Solo migra el primero.

Los otros dos pertenecen a otra actividad y se quedan donde están. No se mezclan dos
negocios en una base de datos porque casualmente compartan herramienta.

Y se quedan porque ahí Notion es la herramienta correcta: pocos registros, edición
humana, sin concurrencia y sin integridad crítica. El problema nunca fue Notion, fue
pedirle que hiciera de base de datos de un sistema automatizado.

Notion no desaparece. Deja de ser el CRM de ofertas.

### La regla que no se rompe

**En cada momento se escribe en un solo sitio.** Nunca en dos. El día que n8n escriba
en Notion y el panel escriba en Postgres, los datos derivan.

No es una precaución teórica: ya ocurrió. Dos registros para la misma persona
acabaron distintos y el CV salió con la cabecera equivocada.

### Transición en dos fases

**Fase 1, mientras se construye la rebanada 1.**
Notion sigue siendo la verdad. n8n escribe ahí. Una sincronización en una sola
dirección vuelca a Postgres y el panel solo lee. Si el panel falla, no se pierde nada
y no hay que dejar de trabajar.

**Fase 2, con las pantallas de estado de la rebanada 2.**
Se invierte. n8n pasa a escribir contra la API, Postgres es la verdad y la base de
ofertas de Notion se congela en solo lectura. Pasa a ser histórico, no herramienta.

### Migración del histórico

Se migra entero: ofertas y candidaturas, con fechas, estados y enlaces a los
documentos generados. Es el registro real de la búsqueda y no se tira.

La migración es además el momento de corregir lo que ya se sabe sucio, como las
ofertas descartadas cuyo estado nunca llegó a actualizarse.

### Dónde vive el design system

Ni en Notion ni en el CRM. Cada pieza en el sitio que le corresponde:

| Pieza | Dónde | Por qué |
|---|---|---|
| Los tokens | Figma, como Variables | Tienen tipos, escalas y modos, y se pueden extraer por API |
| El porqué de cada decisión | El repositorio | Las reglas del proyecto no viven en una herramienta de proveedor, y un repositorio público sí se abre |
| Los valores que consume la aplicación | El código, como custom properties | |

Si los tokens viven en un documento, alguien los copia a mano y vuelve a aparecer un
color que nadie sabe de dónde salió. Que es el problema que este trabajo corrige.

## 11. Entrega por rebanadas

Rebanadas verticales completas, no capas.

**Rebanada 1.** Ver mis ofertas, abrir una, generar CV y carta, descargar. Toca la
capa de datos, el design system y `cv-server`. Es el escaparate.

**Rebanada 2.** Marcar como aplicada, estados y seguimiento. Sustituye a Notion como
interfaz.

**Rebanada 3.** Preparación de entrevista. Es lo único sin nada construido detrás.

## 12. Qué no entra

- **Postular automáticamente.** Cada portal es distinto, LinkedIn no ofrece API para
  ello y automatizarlo lleva a scraping frágil que arriesga la cuenta. El panel abre
  la oferta y la persona registra que aplicó en un clic.
- Pantallas de alta e invitaciones, roles finos, panel de administración y
  facturación. Es producto, y se añade sin tocar la arquitectura.
- Migrar `cookyourweb.es` al design system nuevo.
- Sustituir n8n.
- Microservicios, contenedores orquestados y multi-región. Un monolito bien separado
  por dentro aguanta mucho más de lo que se cree.

## 13. Riesgos

| Riesgo | Mitigación |
|---|---|
| El alcance completo son seis subsistemas | Se entrega por rebanadas; la 1 vale por sí sola |
| Migrar de Notion a Postgres puede desalinear a n8n | n8n sigue escribiendo en Notion en la rebanada 1 |
| Los neones no pasan contraste | Se mide antes de diseñar y se documenta |
| Aprender Angular y Figma a la vez retrasa la búsqueda de empleo | La rebanada 1 es pequeña y publicable |
| «Ya lo cambiaremos» sobre el esquema | Por eso `user_id` y el filtrado por usuario van desde el día uno |
