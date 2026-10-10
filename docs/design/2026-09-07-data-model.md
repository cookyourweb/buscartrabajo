# Modelo de datos del panel

Fecha: 2026-09-07
Continúa a: `2026-09-05-panel-empleo-angular-design.md`, que preveía tres tablas
Verificado contra tres fuentes: el esquema de Notion por API, un export completo de la
base, y el workflow de n8n en producción

## Qué cambia respecto al diseño del 5 de septiembre

Aquel documento preveía `offers`, `applications` y `documents`. Al mirar los datos reales
aparecen **dos entidades más**, y las dos estaban escondidas en el mismo sitio: el cuerpo
de la página de Notion, escritas en prosa.

## Las cinco entidades

### `offers`, la oferta

Lo que describe el puesto y no depende de quién lo mire. Trece campos: empresa, puesto,
descripción, enlace, ubicación, modalidad, salario, tipo de contrato, modo de
contratación, idioma, palabras clave, fecha de publicación y si está verificada.

### `applications`, la candidatura

La relación entre una persona y una oferta. Catorce campos: usuario, estado, fase, vía de
envío, cuatro fechas, formato técnico, los tres campos de contacto, el correo enviado y
las notas.

### `documents`, lo generado

Cinco campos: currículum usado, enlace de Drive, carta enviada, enlace de preparación y
el aviso de autónoma en la carta.

### `events`, el historial

**No existe hoy como dato.** Vive en prosa, dentro del cuerpo de la página:

```
15 de julio: responde interesada e indica su referencia salarial.
21 de julio: el recruiter vuelve de vacaciones y propone llamada.
22 de julio: llamada mantenida. Encaje bueno.
```

Eso es un registro de eventos fechados. En prosa no se puede ordenar, ni consultar, ni
sacar en una pantalla. Y es justo lo que hace falta para saber a quién insistir: no el
estado, sino qué pasó y cuándo.

### `encaje`, lo que sobra y lo que falta

Tampoco existe hoy como dato. También en prosa:

```
Fuerte:      React, Vue, TypeScript, Core Web Vitals, FastAPI
Gap:         PHP/Symfony. No está en su experiencia y no se inventa en el CV.
A negociar:  el rango de la oferta queda por debajo de la referencia
```

Es la regla de no mentir, aplicada oferta por oferta. Y es el dato que alimenta la
promesa de ayudar a aprender lo que falta, en lugar de inflar el currículum.

`Tags` no migra: cero valores en toda la base.

## La dimensión que faltaba: quién rellena cada campo, y cuándo

Los campos no se distinguen solo por a qué entidad pertenecen. También por su origen.

| | Quién lo pone | Cuándo |
|---|---|---|
| ① | El sistema | Al captar la oferta |
| ② | El sistema | Al generar el currículum o la carta |
| ③ | La persona | Al avanzar, tras cada contacto |

Y el relleno medido lo confirma:

| Origen | Relleno |
|---|---|
| ① captación | por encima del ochenta por ciento de las filas |
| ③ a mano | por debajo del quince por ciento |

Los peores son precisamente los que más dicen de un proceso: la fase en la que está, el
formato de la prueba técnica, la fecha de la entrevista y el nombre de la persona con la
que se habla.

**No están vacíos porque no importen. Están vacíos porque rellenarlos obliga a volver a
Notion y editar una fila a mano.** Esos números son la medida del problema, no un
descuido.

Consecuencias para la pantalla:

- Los campos de ① se muestran, no se editan. Si están mal, lo que falló es la extracción.
- Los de ② los escribe el sistema.
- Los de ③ son los que tienen que costar un clic. **Ahí es donde el panel gana o pierde.**

### Por qué esto obliga a dar forma a lo que hoy es prosa

Está previsto que más adelante se pueda dictar lo que ha pasado y que un agente rellene
los campos. Eso no se construye ahora, pero condiciona el modelo de hoy: un agente
rellena sin equivocarse un campo con valores cerrados, y no rellena bien un cajón de
texto libre.

Hoy `Notas` está relleno en casi todas las filas y contiene de todo: pruebas técnicas,
avisos de los guardrails y trozos de historial. Ese cajón es donde la información deja de
ser consultable.

## Lo que ya estaba decidido y aquí se respeta

Del documento de julio sobre cómo entra una oferta:

- **El origen no es un estado.** El estado cambia constantemente; el origen no cambia
  nunca. Si el origen vive dentro del estado, se pierde en cuanto la candidatura avanza.
- **`Aprobado` no es un estado: es una orden.** Ponerlo dispara la generación del
  currículum y la carta, venga del botón del correo o de la mano de la persona. Por eso
  no tiene filas: es una cola, no un sitio donde se está.
- **`Estado` mezcla dos ciclos de vida** en una sola propiedad, el del automatismo y el de
  la candidatura real. La separación en `applications` y `events` es lo que los desmezcla.

## Lo que los datos dejan a la vista

**Ofertas duplicadas.** Misma empresa, mismo puesto y el mismo enlace. Es la misma
oferta capturada dos veces. Un `UNIQUE` sobre el enlace lo impediría, y es el mismo fallo
que ya ocurrió con las personas: dos registros para la misma acabaron distintos y salió un
currículum con la cabecera equivocada.

**Una oferta sin usuario.** Con `user_id` obligatorio no podría existir.

**El salario es texto libre.** Una cadena que mezcla el rango que ofrece la empresa con la
referencia de quien busca lleva tres datos dentro: mínimo, máximo y expectativa. El
sistema promete buscar por sueldo, y eso exige que el sueldo sea un número.

**Hay una segunda base de candidaturas, abandonada.** Unas pocas filas, todas de tres días
de julio, con un vocabulario de estados que no coincide. Y parte de lo que hay ahí no
existe en la base principal. La pregunta no es si alinear los dos vocabularios: es
rescatar lo que solo vive ahí, congelar esa base y no volver a escribir en dos sitios.

## Lo que el panel resuelve de verdad

Hoy una candidatura vive repartida en cuatro sitios sin ningún enlace entre ellos: la
oferta y su estado en Notion, el currículum en Drive, la preparación de la entrevista en
una carpeta dentro de git, y el seguimiento en la cabeza de quien busca.

**No existe un sitio común.** El panel es ese sitio.
