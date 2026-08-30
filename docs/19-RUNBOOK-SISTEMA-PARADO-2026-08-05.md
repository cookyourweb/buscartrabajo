# 19. Runbook: "el sistema no me manda ofertas"

**Fecha:** 5 de agosto de 2026
**Estado:** causa raíz encontrada y arreglada
**Aplica a:** workflow `BuscarTrabajo - Ofertas Diarias (PROD, dedup ON)`, id `CsvmtPcLVmGIZg6C`

Este documento existe porque el mismo síntoma se ha diagnosticado **cinco veces** (24-jun, 8-jul, 13-jul, 30-jul, 5-ago) y cuatro de ellas se empezó desde cero. La quinta encontró la causa real. Aquí queda escrita para no volver a pagar ese peaje.

---

## 1. La causa raíz del 5 de agosto

El workflow tiene **cuatro triggers**, no uno:

| Trigger | Cron | Para qué |
|---|---|---|
| `Schedule Trigger (9am)` | `0 9 * * *` | la búsqueda diaria de ofertas |
| `Cron - Revisar Aprobadas` | `* * * * *` **(el culpable)** | revisar ofertas aprobadas en Notion |
| `Manual Trigger` | manual | pruebas |
| `Error Trigger` | evento | avisos de error |

`Cron - Revisar Aprobadas` disparaba **cada minuto**: 1.440 ejecuciones diarias de 400 a 650 ms, todas con estado `success` y sin producir nada. Sumadas al resto de workflows activos, la instancia acumuló **11.240 ejecuciones de producción**.

La cadena completa:

1. El cron del minuto satura la instancia de n8n en Render todo el día.
2. La instancia se queda sin memoria y se reinicia sola.
3. Cuando llega el disparo de las 9:00, no hay memoria disponible: `WorkflowCrashedError: Workflow did not finish, possible out-of-memory issue`, muriendo en el propio `Schedule Trigger (9am)`. Ocurrió el 29, 30 y 31 de julio.
4. Del 3 de agosto en adelante la instancia ni siquiera llegaba viva a las 9:00, así que no había ejecución **ni mail de error**. Silencio total, que es el síntoma más engañoso de todos.

### El arreglo aplicado

`Cron - Revisar Aprobadas` pasa de `* * * * *` a `*/15 * * * *`. De 1.440 ejecuciones diarias a 96.

Verificado releyendo el workflow del servidor y observando 6 minutos sin ningún disparo. Backup previo en `workflows/BACKUP-CsvmtPcLVmGIZg6C-2026-08-05-0832-antes-fix-cron.json`.

---

## 1 bis. Los otros dos fallos, que eran los que de verdad vaciaban Notion

Arreglar el cron dejó de tirar la instancia, pero **seguían sin llegar ofertas**. Había otros dos fallos encadenados, los dos medidos sobre el feed real, no supuestos.

### Fallo A: el filtro de modalidad asumía Presencial y tiraba el 39% de las ofertas

En `Code - Normalizar Modalidad`:

```js
let modalidad = 'Presencial';                  // valor por defecto
if (mod.includes('remoto'))  modalidad = 'Remoto';
else if (mod.includes('híbrido')) modalidad = 'Hibrido';
if (modalidad === 'Presencial') return null;   // descartada
```

Si la oferta no declaraba modalidad, el valor se quedaba en `Presencial` y la línea siguiente la descartaba. El workflow acababa en `success` con cero items y nadie se enteraba.

**Y contradecía al propio prompt de Groq**, que dice literalmente *"NUNCA asumas la modalidad: si la oferta no dice remoto/hibrido, deja el campo vacio"*. Groq obedecía y devolvía `"modalidad": ""`. El código de después asumía. Dos reglas contrarias en el mismo workflow.

**Medido sobre el RSS real (80 ofertas):**

| | ofertas |
|---|---|
| con modalidad en algún punto del texto | 49 |
| **sin modalidad en ninguna parte** | **31 (39%)** |
| con modalidad visible en los primeros 60 chars | 31 |
| con modalidad visible en los primeros 500 chars | 31 |

Dato útil: **Tecnoempleo mete la modalidad en el campo `Provincia`**. En 23 ofertas pone `hibrido` y en 3 `100% en remoto` en vez de una provincia. Por eso ya son visibles en los primeros 60 caracteres.

Hipótesis descartada por el camino: se pensó que el problema era que a Groq solo se le mandan 60 caracteres de descripción (`descFull.slice(0, 60)`). Subirlo a 500 gana **2 ofertas de 80**. No era eso, y medirlo antes de tocarlo ahorró un cambio inútil.

**Arreglo aplicado:** la modalidad ya no se asume. Si no se puede determinar, queda `Sin confirmar` (opción nueva añadida al select de Notion) y la oferta **entra igual**, con `[VERIFICAR MODALIDAD]` al principio de las Notas. Se descarta solo con dato explícito: Presencial, o Híbrido fuera de Madrid. La modalidad se busca además en la descripción de 1800 caracteres que el nodo ya tenía guardada al lado, sin tocar el prompt ni el nodo de formateo.

### Fallo B: solo se leían las 30 primeras ofertas del RSS, de 80

En `Formatear ofertas`:

```js
for (let k = 1; k < parts.length && k <= 30; k++) {   // el feed trae 80
```

**Medido sobre el feed del 5 de agosto:**

| | ofertas del perfil de Vero |
|---|---|
| en las 30 primeras | **0** |
| en las 80 totales | **5** |

Las cinco que encajaban estaban por debajo de la posición 30. El tope las tiraba todas sin mirarlas. El feed de Tecnoempleo **no viene ordenado por relevancia**: las 30 primeras de ese día eran Técnico Automatista, Operario Electrónico, SAP MDG, ABAP y Consultor ERP.

Esto explica el goteo de "una oferta en doce días" mejor que ninguna otra cosa.

**Arreglo aplicado:** tope subido de 30 a 100.

### Fallo C: el `Wait` de 30 segundos perdía la ejecución entera

`Wait - Rate Limit Groq` estaba en 30 segundos. La ejecución de las 9:00 del 5 de agosto (id 34056) murió exactamente ahí: recorrió los tres portales sin un solo fallo, formateó las ofertas, llegó al `Wait` y quedó huérfana con `WorkflowCrashedError`.

En n8n **una espera corta vive en la memoria del proceso, no en base de datos**. Si el proceso se reinicia durante esos 30 segundos, la ejecución se pierde y el mensaje que sale es el genérico de *"possible out-of-memory"*, que manda el diagnóstico en la dirección equivocada. No era memoria: era una espera que nadie reanudó.

Con **un solo usuario** se hace una única llamada a Groq, así que no hay rate limit del que protegerse. **Arreglo aplicado:** bajado a 2 segundos. El flujo completo pasó de 38 a **6,7 segundos**, con lo que la ventana en la que un reinicio puede matar la ejecución es quince veces más pequeña.

### Verificación end-to-end

Disparando el flujo real por `POST /webhook/buscar-para-user` con el perfil de Notion:

```
webhook -> 200 (38,1s)
respuesta: {"messageId": "<...@smtp-relay.mailin.fr>"}

OFERTAS NUEVAS EN NOTION: 2
  zooplus SE | Senior AI Engineer         | Sin confirmar
  Swiss Re   | Senior Full Stack Engineer | Sin confirmar
```

Las dos son exactamente las que Groq había seleccionado el 4 de agosto y el filtro descartaba.

**Cómo relanzar el flujo sin esperar a las 9:00:** `POST https://n8n-asistente-correo.onrender.com/webhook/buscar-para-user` con el body que espera `Code — Normalizar (interno)`: `nombre`, `email`, `perfil`, `rol`, `stack[]`, `salario`, `modalidad[]`, `ciudad`, `user_id`. El `user_id` es el id de la página de Vero en la base Users. Script listo en el scratchpad de la sesión (`probar_flujo_real.py`).

---

## 2. Los cuatro engaños que cuestan horas

Cada uno de estos hizo perder tiempo en algún diagnóstico anterior. Leerlos antes de investigar.

### Engaño 1: "no me llegan los mails"

Los mails **sí llegan**. Están sin abrir en `hello.cookyourweb@gmail.com`, remitente `veronica@cookyourwebai.es` (Brevo). El 5 de agosto había sin leer la oferta de Arelance del 2-ago y los tres avisos de error del 29, 30 y 31 de julio.

El mail se manda **una vez por cada oferta nueva creada en Notion**. Sin oferta nueva no hay mail. Así que "no llegan mails" casi siempre significa "no se están creando ofertas", que es un problema distinto y aguas arriba.

### Engaño 2: "me llegan avisos a Telegram, luego el sistema va"

Falso. Son **workflows distintos**:

- Telegram: `Búsqueda Empleo Diaria`, id `LODaOAsNrmU7NnJ4`, 9 nodos.
- Notion y mail: `BuscarTrabajo - Ofertas Diarias (PROD, dedup ON)`, id `CsvmtPcLVmGIZg6C`, 50 nodos.

Que uno funcione no dice nada del otro.

### Engaño 3: "healthz responde 200, la instancia está bien"

Una sola llamada no vale. El 5 de agosto `/healthz` respondió 200 en 0,24s, y diez minutos después estuvo **seis sondeos seguidos en 502** antes de volver. Una instancia que se reinicia en bucle responde 200 la mitad del tiempo.

**Hay que sondear varias veces espaciadas**, nunca una sola.

### Engaño 4: "el ID del workflow es el que pone la documentación"

El ID cambia cada vez que se importa un export. Histórico conocido: `3zFJWSkPPHDi4yMp`, `5pTwriXcc6aYHO1Y`, `OVoFiXTQwXmiyMfW` y ahora `CsvmtPcLVmGIZg6C`. Los cuatro siguen existiendo en la instancia, tres apagados.

**Nunca confiar en un ID escrito en un documento.** Listar los workflows y quedarse con el que esté `active`.

---

## 3. Orden de diagnóstico (seguir tal cual)

Cuando Vero diga "no me llega nada", hacer esto **en este orden**. Los tres primeros pasos cuestan un minuto y suelen bastar.

### Paso 1: ¿cuándo entró la última oferta de verdad?

Consultar Notion, data source `collection://33d11515-f4b2-8176-947b-000bbafd1ca7`:

```sql
SELECT createdTime, "Empresa", "Puesto", "Estado"
FROM "collection://33d11515-f4b2-8176-947b-000bbafd1ca7"
ORDER BY datetime(createdTime) DESC LIMIT 20
```

La columna es `createdTime`, **no** `"Created time"`. Fijarse en la **hora**: las creadas hacia las 07:00 UTC son del cron; las de media tarde son cargas manuales y no prueban que el sistema funcione.

### Paso 2: ¿qué dicen los mails de error?

Buscar en Gmail `hello.cookyourweb@gmail.com`:

```
newer_than:14d subject:"❌ ERROR"
```

Abrir el **cuerpo** del mail, no solo el asunto. El asunto siempre dice `Nodo: Unknown` y no sirve. El cuerpo trae el JSON con `error.message`, `lastNodeExecuted` y el id de ejecución.

Contar cuántos hay: dos errores en dos días seguidos no es un incidente puntual, es un fallo diario. Y **la ausencia de mails de error no es buena señal**: puede significar que la instancia ni arranca.

### Paso 3: ¿cada cuánto se está ejecutando?

En la UI de n8n, pestaña **Executions**, mirar la columna `Started`. Si hay una fila por minuto, ya está el problema encontrado.

Por API, restar dos ids de ejecución separados por 24 horas exactas: el 30 de julio dieron 1.625 ejecuciones al día. Lo normal debería ser menos de 300.

### Paso 4: ¿la instancia aguanta viva?

Sondear `https://n8n-asistente-correo.onrender.com/healthz` **diez veces con 20 segundos entre medias**. Si aparecen 502, la instancia se está reiniciando y ese es el problema real.

### Paso 5: revisar los triggers de todos los workflows activos

Listar por API y mirar cron a cron. El 5 de agosto había 6 workflows activos, y entre todos generaban unas 2.300 ejecuciones diarias:

| Workflow | Trigger | Frecuencia |
|---|---|---|
| `BuscarTrabajo - Ofertas Diarias` | Cron - Revisar Aprobadas | cada minuto (arreglado a 15 min) |
| `Captura Gmail - v4.1` | 7 triggers de Gmail | cada 15 min **cada uno** |
| `Asistente Correo Outlook` | Outlook Trigger | cada 15 min |
| `Keep-Warm CV Server` | Cada 10 minutos | cada 10 min |
| `Digest Diario Correo` | Schedule | diario 8:00 |
| `Búsqueda Empleo Diaria` | Cada día 9:00 | diario |

Los 7 triggers de Gmail del workflow de captura son el siguiente candidato si el problema vuelve.

---

## 4. La API de n8n

**Host real:** `https://n8n-asistente-correo.onrender.com` (no `n8n-qwmu`, que sale en documentación vieja).

**Key:** en `buscartrabajo/.env`, variable `N8N_API_KEY`. Cabecera `X-N8N-API-KEY`.

**Se genera en:** `https://n8n-asistente-correo.onrender.com/settings/api`

### Gotcha que costó media sesión

La key del `.env` devolvía **401** y parecía revocada. No lo estaba: tenía **un carácter `<` pegado al final**, que rompía la firma del JWT. La key son 267 caracteres y en el fichero había 268.

Antes de dar una key por muerta, comprobar que es un JWT limpio:

```python
re.match(r"[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+", valor)
```

Si el match no cubre la cadena entera, sobra basura al final.

Ese mismo `<` es el que rompe la shell. **Nunca hacer `source .env` ni `. .env`**: zsh intenta interpretarlo, falla, y en el mensaje de error **imprime el valor de la línea anterior**. Así se quemó el `NOTION_TOKEN` el 5 de agosto. Para leer un valor del `.env`, parsearlo con Python línea a línea y no imprimirlo nunca.

### Gotcha del PUT

`PUT /api/v1/workflows/{id}` solo acepta `name`, `nodes`, `connections` y `settings`. Cualquier otro campo devuelve 400. Y dentro de `settings` solo admite esta lista:

```
saveExecutionProgress, saveManualExecutions, saveDataErrorExecution,
saveDataSuccessExecution, executionTimeout, errorWorkflow, timezone, executionOrder
```

`binaryMode` hay que quitarlo del body. No se pierde: n8n lo conserva en el servidor.

---

## 4 bis. Adzuna lleva días caída, y falla en silencio

Encontrado el 6 de agosto, con el sistema ya arreglado y funcionando. El nodo `Buscar en Adzuna` **no hace la llamada HTTP**. Devuelve:

```json
{"error": "access to env vars denied"}
```

La URL del nodo usa `{{ $env.ADZUNA_APP_KEY }}` y la instancia tiene bloqueado leer variables de entorno desde expresiones. El nodo devuelve el error como si fuera un resultado, el workflow continúa y acaba en `success`.

**Verificado el mismo error en tres ejecuciones de días distintos:** 4 de agosto (id 32459), 5 de agosto (id 34085) y 6 de agosto (id 34340). No se puede mirar más atrás porque n8n ya no conserva esas ejecuciones.

**De las tres fuentes solo funcionan dos.** Y Adzuna es la única que trae salario estructurado (`salary_min`, `salary_max`), así que además se pierde esa señal.

### La pista que lo delata: la duración

```
Buscar en Remotive     698 ms
Buscar en Tecnoempleo  414 ms
Buscar en Adzuna         3 ms     <- no ha llamado a nadie
```

**Cualquier nodo de red que tarde menos de 10 ms no ha hecho ninguna petición.** El estado dice `success` y la duración dice la verdad. Mirar la columna de duración antes que la de estado.

### Arreglos posibles

1. **El recomendado.** En Render, servicio n8n, añadir la variable de entorno `N8N_BLOCK_ENV_ACCESS_IN_NODE=false` y reiniciar. Desbloquea `$env` en las expresiones sin exponer la clave en el workflow, y de paso arregla cualquier otro nodo que la use.
2. Poner la clave literal en la URL del nodo. Funciona de inmediato, pero queda escrita en el JSON del workflow y en todos los backups.
3. Crear una credencial de n8n de tipo Query Auth y referenciarla. Más limpio que la 2 y más trabajo.

El `app_id` ya va en claro en la URL. Lo único que falta es `ADZUNA_APP_KEY`.

---

## 5. Lo que sigue pendiente

1. **Purgar el histórico de ejecuciones.** Hay 11.240 registros ocupando disco y memoria. En Render, variables de entorno del servicio n8n: `EXECUTIONS_DATA_PRUNE=true` y `EXECUTIONS_DATA_MAX_AGE=168` (7 días).

2. **Publicar la pantalla de consentimiento OAuth a Production.** El proyecto de Google `n8n-asistente-correo` está en modo **Testing**, y Google mata los refresh tokens **cada 7 días**. Es la causa de los `invalid_grant` del 21 de julio y del token de Drive caducado el 31 de julio. Mientras siga en Testing, va a volver a pasar cada semana.

3. **Rotar el `NOTION_TOKEN`**, expuesto el 5 de agosto por el `source .env`.

4. **Revisar los 7 triggers de Gmail** del workflow de captura. Siete pollings de 15 minutos sobre siete buzones es mucho para una instancia gratuita.

5. **La rama de LinkedIn lleva muerta desde el 23 de julio.** Necesita Claude in Chrome con sesión iniciada, y eso no existe en las rutinas de la nube. Ver documento 07.

---

## 6. Resumen en cinco líneas

- El síntoma "no llegan mails" casi nunca es de correo. Es de ofertas que no se crean.
- Telegram y Notion son workflows distintos: uno no informa del otro.
- Un `healthz` que responde 200 una vez no prueba nada. Sondear diez veces.
- Los IDs de workflow cambian con cada import. Listar y filtrar por `active`.
- Antes de tocar nada: mirar cada cuánto se ejecuta. Un cron cada minuto tira la instancia entera.
