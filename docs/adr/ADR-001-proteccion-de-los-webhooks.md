# ADR-001. Cómo se protegen los webhooks

**Fecha:** 31 ago 2026 · **Estado:** aceptado, con caducidad conocida · **Issue:** #1

---

## Contexto

El workflow de n8n expone cuatro webhooks. Tres de ellos ejecutan acciones con
**efectos externos irreversibles**, y uno envía correo a terceros. Los cuatro
aceptan peticiones sin ninguna credencial.

Tres se invocan por **GET desde un botón de Notion**. Eso es lo que condiciona todo
lo demás: un botón de Notion abre una URL y nada más. **No envía cabeceras.**

El 31 de agosto de 2026 se comprobó, midiendo contra la API de n8n, que los cuatro
nodos tienen `authentication: ninguna`, y que las rutas de tres de ellos llevaban
meses publicadas en este repositorio, que es público: en el README, en seis
documentos, en once copias de seguridad del workflow y dentro del código de los
nodos. Nadie lo vio porque nada lo miraba.

## Decisión

**Ruta impredecible, fuera del repositorio, y verificación automática de que no
vuelve a entrar.**

Los `path` viven en `workflows/PROD/secrets.local.json`, que está en `.gitignore`.
En todo lo versionado aparecen como `@@SECRET:<nodo>`. `check-secretos.mjs` corre
en el hook de pre-commit y en CI, y devuelve error si encuentra alguna.

## Por qué no autenticación por cabecera

Se intentó el 30 de agosto de 2026 en el webhook `buscar-para-user` y **se
descartó tras dos horas de diagnóstico**. Con Header Auth activo, el endpoint
devolvía 403 a todo, incluido el token correcto. Se descartaron una a una siete
variantes de configuración de la credencial.

Y hubo un efecto colateral que nadie habría relacionado: **activar Header Auth
pisó la credencial de Groq del mismo workflow**, que pasó a devolver 401. En n8n,
lo compartido se pisa en silencio.

Para los tres webhooks del botón de Notion el problema es anterior y más simple:
**aunque Header Auth funcionase, un botón no puede mandar la cabecera.**

## Por qué redactar el repositorio no es el arreglo

Una ruta publicada está quemada. Sacarla de los ficheros no la despublica: sigue
en el historial de commits, que ya está en GitHub.

Redactar sirve para **lo que venga después**, no para lo que ya salió. Lo único que
cierra una ruta publicada es **rotarla**, y entonces todas las apariciones antiguas
se convierten en cadenas muertas: no hay que perseguirlas ni reescribir el
historial.

De ahí el orden: primero se rota, luego se limpia, y publicar es lo último.

## Consecuencias

**Se acepta:**

- La protección depende de que la ruta no se filtre. Es más débil que una
  credencial, y se sabe.
- Rotar una ruta obliga a actualizar los botones de Notion en el mismo momento, o
  dejan de funcionar.
- Dos nodos de producción todavía construyen la URL con la ruta escrita a mano
  (`code-preparar-email-carta-cv.js`, `code-preparar-email-notificacion.js`). Al
  rotar hay que sustituirla por una expresión, o la ruta nueva vuelve al repo en
  el siguiente `wf-split`.

**Se gana:**

- Cerrado sin depender de Header Auth, que está medido y no funciona aquí.
- La verificación no depende de que nadie se acuerde. Es la misma idea que ya se
  aplicó a los prompts de `cv-server`: una prohibición escrita no es un control;
  un control es código que falla.

## Cuándo caduca esta decisión

**Cuando exista el frontend en Angular.**

Está decidido que este sistema tendrá una aplicación Angular con el ciclo completo
de una candidatura. Una aplicación en el navegador que llame a estos webhooks
**expone la ruta en la pestaña de red**. La ruta impredecible deja de proteger
nada en ese momento.

Es decir: esto es un puente, no un destino. El frontend obliga a autenticación de
verdad, con un backend que guarde el secreto y hable con n8n, o con tokens por
petición. Cuando se empiece el Angular, este ADR se sustituye.

---

**Relacionado:** issue #1 · `scripts/lib/secretos.mjs` · `tests/secretos.test.mjs`
· `scripts/check-secretos.mjs` · `workflows/PROD/README.md`
