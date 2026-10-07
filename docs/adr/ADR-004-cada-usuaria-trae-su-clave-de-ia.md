# ADR-004. Cada usuaria trae su propia clave de IA

**Fecha:** 2 oct 2026 · **Estado:** aceptado el 3 oct 2026, sin implementar (ver «Lo que falta para que esto sea verdad»), al decidir cómo encaja la búsqueda de ofertas

---

## Contexto

Generar CV y cartas, y conversar con el asesor de entrevistas, llama a un modelo
de lenguaje. Es el único coste variable real del sistema (sección D del
[tablero](../diseno/2026-09-05-decisiones-arquitectura.md)): crece con cada usuaria
y con cada uso.

El sistema se abre a otras personas por invitación, y el criterio es que a la
dueña **no le cueste nada** ([ADR-002](ADR-002-donde-vive-postgres.md)). Quedaban
dos formas de que lo pague quien lo usa:

- **Cobrarle el coste.** Obliga a pasarela de pago, a emitir factura por cada
  cobro y a gestionar el IVA. Para unos céntimos de modelo, el trámite cuesta más
  que el servicio.
- **Que cada usuaria use su propia clave** del proveedor. Nadie cobra a nadie.

### Lo que cuesta, medido el 2 de octubre de 2026

Con el prompt y el modelo de producción (`claude-sonnet-4-6`, 3 USD por millón de
tokens de entrada y 15 de salida), sobre tres ofertas reales:

| | Tokens de entrada | Tokens de salida | Coste |
|---|---|---|---|
| CV | 9.600 a 10.100 | 1.400 a 1.600 | unos 0,05 USD |
| Carta | 3.450 a 3.850 | 115 a 140 | unos 0,013 USD |

Una oferta aprobada, con CV y carta, cuesta **unos 6 céntimos de dólar**.

### Lo que no existe: gratis y de calidad

Se midió el mismo prompt contra Groq en su plan gratuito (`gpt-oss-120b`). Su
límite es de 8.000 tokens por minuto y el prompt del CV ya ocupa unos 7.600: **no
generó ninguna de las tres ofertas reales**. Las rechazó por tamaño.

Las condiciones de la API de Gemini no permiten ofrecer su plan gratuito a usuarias
del Espacio Económico Europeo, y Anthropic no tiene plan gratuito de API.

## Decisión

**Cada usuaria conecta su propia clave de IA** (BYOK, *bring your own key*). Lo
que genera para ella se cobra en su cuenta del proveedor.

**Solo se admiten modelos de una lista de modelos soportados.** Un modelo entra en
la lista si genera de verdad los casos de `cv-server/evaluacion.py` y los pasa,
con los guardrails de veracidad (cifras, tecnologías, habilidades, experiencia (en la carta) y
titular) en verde. Esos guardrails contrastan la salida contra el CV Master y no
dependen del modelo: sirven igual para cualquiera. Hoy la lista es `claude-sonnet-4-6`.

**Lo que ve la usuaria:**

1. En el alta, un paso para conectar su IA, con una guía corta que recomienda una
   clave dedicada a este sistema y con tope de gasto.
2. Al pegar la clave, el sistema comprueba que existe y que da acceso al modelo
   soportado, **antes** de guardarla. El saldo no se puede saber de antemano: se
   descubre en la primera generación.
3. Después solo ve los últimos caracteres de la clave. Puede cambiarla o borrarla.
4. Las ofertas se ven y se ordenan sin clave: el orden se calcula con reglas, sin modelo de IA.
5. Cada documento muestra qué modelo lo escribió y cuántos tokens gastó.

**Cómo se trata la clave:**

- Se guarda **cifrada** (AES-256-GCM o Fernet), con el identificador de la usuaria
  y el proveedor como datos asociados, para que un cifrado no pueda moverse a la
  fila de otra. La llave maestra vive en el entorno de `cv-server`, nunca en la
  base ni en el repositorio, y nunca en las copias de la base.
- Cada clave guarda la versión de la llave con que se cifró. Rotar es descifrar con
  la vieja y cifrar con la nueva. Si la llave se pierde, las claves no se recuperan:
  cada usuaria la vuelve a pegar.
- Viaja desde el navegador una sola vez, al guardarla, y **nunca vuelve** al panel.
- Solo `cv-server` la descifra, **en cada llamada**: nunca por variable de entorno
  ni en un cliente compartido entre usuarias.
- **No aparece en los registros.** Va en cabecera, nunca en una URL, y los errores
  de los proveedores se registran por tipo y código, nunca con su mensaje. Lo
  vigila `cv-server/tests/test_claves_fuera_de_los_registros.py`.
- Al darse de baja se borra la clave cifrada. Las copias de la base caducan por su
  cuenta, y se recomienda a la usuaria revocar la clave en su proveedor, porque solo
  ella puede hacerlo.

**Cuando la clave falla:**

- **Nunca se cae a una clave de la dueña.** Ni pagaría ella, ni el CV acabaría en
  un proveedor que la usuaria no eligió.
- Límite de tasa o proveedor caído: se reintenta con espera, con la misma clave.
- Clave inválida, revocada o caducada, sin saldo, o tope de gasto alcanzado: no se
  reintenta. La clave se marca como "necesita atención" y el panel lo explica en
  lenguaje claro.

**La búsqueda de ofertas (decidido el 3 de octubre de 2026).** El bot busca una
sola vez al día y guarda una **bolsa común** de ofertas para todas las usuarias. El
orden de esa bolsa para cada usuaria se calcula **con reglas, sin modelo de IA**, a
partir de los campos de su perfil (rol, tecnologías, modalidad, ubicación y salario).
Así nadie paga por ordenar ofertas, ningún perfil de una usuaria pasa por la cuenta
de IA de otra persona, y el bot escala igual con una usuaria que con cincuenta. Por
eso el alta tiene que recoger el perfil en campos estructurados, no en texto libre.

El modelo de IA solo se usa en lo que lo necesita de verdad: el CV, la carta y el
asesor, siempre con la clave de la usuaria.

**Procesos programados.** Si en el futuro algún proceso programado usa el modelo en
nombre de una usuaria, necesita su consentimiento explícito y separado, un tope
diario propio del sistema y una pausa automática tras varios fallos seguidos.

**Límites.** No hace falta una cuota **económica**: el dinero es de cada usuaria.
Sí se mantiene no repetir una generación ya hecha y un límite de uso por usuaria,
para que un error del sistema no gaste en la cuenta de nadie.

## Lo que falta para que esto sea verdad

Hoy `cv-server` habla con tres proveedores, pero con las claves de la dueña, leídas
del entorno y con un cliente compartido, y con una cascada que cae de uno a otro.
BYOK obliga a cambiarlo antes de abrir el sistema a nadie.

Y el bot de n8n llama hoy al modelo por su cuenta, con la clave de la dueña, para
filtrar y elegir ofertas (nodo `Groq - Generar Ofertas`); el CV y la carta ya los
redacta `cv-server`. Con la bolsa común deja de hacerlo: n8n busca y guarda la oferta
a través de `cv-server`, con la clave de máquina, y el orden lo calcula `cv-server`
con reglas. La base está en `real_jobs._ranking_fallback`, que hoy solo puntúa por
tecnologías: hay que añadirle rol, modalidad, ubicación y salario.

## Consecuencias

**Se acepta:**

- Con reglas, la selección de ofertas pierde los filtros que hoy aplica el modelo
  leyendo la descripción: que el frontend o la IA sean el trabajo principal y la
  seniority real del puesto. Se compensa con un perfil más rico en el alta.
- Con una bolsa común, el estado de una oferta (aprobada, descartada) deja de vivir
  en la oferta y pasa a ser de cada usuaria: ofertas compartidas y candidaturas por
  usuaria, como prevé el modelo de datos.

- Conectar una clave le cuesta a quien no es técnica. La guía del alta tiene que
  resolverlo.
- Custodiar claves de terceros es un dato delicado más.
- Hoy no hay opción gratuita que cumpla la calidad.

**Se gana:**

- Coste cero para la dueña, sin pasarela, sin facturas y sin IVA.
- Cada usuaria controla su gasto con el tope de su proveedor, si este lo permite.
- Ningún modelo entra por intuición: entra si pasa los tests de calidad.

## Cuándo se revisa

- Si hay personas dispuestas a pagar por el servicio: entonces se diseña un plan de
  pago de verdad, no un cobro por coste.
- Si el prompt del CV se reduce lo bastante para que un modelo gratuito quepa y
  pase la evaluación.

---

**Fuentes, consultadas el 2 oct 2026:** platform.claude.com/docs/en/about-claude/pricing ·
ai.google.dev/gemini-api/terms · console.groq.com/docs/rate-limits ·
ai.google.dev/gemini-api/docs/api-key

**Relacionado:** [ADR-003](ADR-003-autenticacion.md) · `cv-server/evaluacion.py` ·
`cv-server/guardrails.py` · [modelo de datos](../diseno/2026-09-07-modelo-de-datos.md)
