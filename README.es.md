**Español** · [English](README.md)

# BuscarTrabajo

Un proyecto de CookYourWebAI.

[![tests](https://github.com/cookyourweb/buscartrabajo/actions/workflows/tests.yml/badge.svg)](https://github.com/cookyourweb/buscartrabajo/actions/workflows/tests.yml)

Sistema multiusuario que busca ofertas de empleo reales cada mañana, las filtra por
el perfil de cada persona y se las manda por correo. Al aprobar una, genera el CV y
la carta adaptados al puesto y permite enviarlos a la empresa.

En producción desde julio de 2026.

## Para quien busca empleo: lo que puedes hacer

Buscar trabajo es revisar los mismos portales cada día y reescribir el CV en cada
candidatura. Este sistema hace esa parte repetitiva por ti, y todas las decisiones
siguen siendo tuyas.

Hoy el circuito completo funciona para la búsqueda de empleo de la autora, y las
personas nuevas entran por invitación. La columna de estado dice qué funciona hoy y qué
está previsto, según el [plan de acción](#plan-de-acción).

| Qué hace por ti | Cómo | Estado |
|---|---|---|
| 1. Entras con la cuenta de Google que ya tienes | Solo por invitación, sin contraseña nueva | Desplegado el 7-oct-2026, pendiente de activar |
| 2. Configuras tu perfil una vez | Rol objetivo, stack, modalidad, ciudad y el enlace a tu CV maestro en Google Docs | Disponible hoy |
| 3. Dejas de revisar portales de empleo cada día | Cada mañana a las 9:00 busca en tres portales (Remotive, Adzuna, Tecnoempleo), filtra las ofertas por tu stack y tu rol, descarta las que ya tienes y te manda por correo hasta 12 | Disponible hoy |
| 4. Decides qué ofertas merecen tu tiempo | Apruebas o descartas cada una | Disponible hoy |
| 5. Dejas de reescribir el CV en cada candidatura | Por cada oferta que apruebas escribe un CV adaptado a ella (guardado en Google Drive) y una carta de presentación, y te avisa por correo para que los revises. Cuando confirmas, los manda a la empresa si la oferta tiene email, con las respuestas dirigidas a ti; si no, te avisa de que apliques a mano | Disponible hoy |
| 6. No pone en tu boca lo que no has hecho | El CV y la carta se contrastan con tu CV maestro: las tecnologías y cifras que no respalda se marcan para que las revises. Son avisos, no bloqueos, y nada sale sin tu aprobación | Disponible hoy |
| 7. Tus datos son solo tuyos | Cada dato con su dueña, en una base de datos de verdad | Previsto |
| 8. Un CV maestro más sólido | Un comprobador que dice qué le falta a tu CV maestro y un asistente que te ayuda a completarlo entrevistándote, sin inventar experiencia | Previsto |
| 9. El gasto de IA lo controlas tú | Traes tu propia clave de IA; ninguna petición cae a las claves de la dueña | Previsto |
| 10. Llegas a la entrevista preparada | Por oferta: qué piden y qué evidencia tienes, más un simulador para practicar | Previsto |

## Para desarrolladores: cómo está hecho y por qué

### Arquitectura

Tres repositorios, tres piezas. n8n busca y orquesta, `cv-server` escribe y valida, el
panel es la cara visible.

| Repositorio | Qué es | Dónde corre |
|---|---|---|
| `buscartrabajo` (este) | Workflows de n8n, scripts, ADR y runbooks | n8n en Render |
| [`cv-server`](https://github.com/cookyourweb/cv-server) | Servicio Python (Flask) que genera CV y carta con guardrails de veracidad | Render, plan gratuito |
| `panel-empleo` | Panel en Angular para ver y gestionar las ofertas. El acceso es por invitación, con cuenta de Google; la demo pública no muestra datos reales | En desarrollo |

```
  PANEL (Angular)                 acceso por invitación, cuenta de Google
      |
      | GET /yo, con ID token de Google
      v
  CV-SERVER (Flask, Render free)  <------------------------+
      |                                                     |
      | llama a n8n                              X-Clave-Maquina
      v                                                     |
  N8N (Render)  -------------------------------------------+
      |
      +-- Schedule 9:00, busca por usuario:
      |     Remotive + Adzuna + Tecnoempleo
      |     filtro por stack y rol + anti-spam contra ofertas ya en Notion
      |     tope de 12 ofertas, Groq formatea, Notion crea la oferta, Brevo avisa
      |
      +-- Aprobar:
      |     marca Aprobado, lee la oferta, genera la carta y el CV
      |     (cv-server), Brevo manda "revisar y enviar", Notion guarda el resultado
      |
      +-- Mandar a empresa:
            lee la carta ya editada; con email de empresa, envía carta y CV
            (replyTo = email del usuario); sin él, avisa al usuario de que aplique a mano
```

### Stack

| Pieza | Tecnología | Notas |
|---|---|---|
| Orquestación | n8n en Render | Workflow de búsqueda, aprobación y envío |
| Generación y validación | `cv-server`: Python, Flask (migrándose a FastAPI) | Plan gratuito de Render: duerme a los ~15 min y el arranque en frío tarda ~50 s. Página de invitación, API de usuarios y generación de CV y carta |
| Panel | Angular, entrada con Google | En desarrollo |
| Datos | Notion: CRM de usuarios y ofertas | Postgres en Neon, previsto |
| Ficheros y correo | Google Drive (CVs adaptados), Brevo (envío de correos) | |
| Modelos de lenguaje | CV y carta con `claude-sonnet-4-6` en producción (lo fija el entorno; `/health` lo muestra). Si Claude falla: Groq `openai/gpt-oss-120b`, después Gemini y después Claude Haiku 4.5 | Groq también formatea las ofertas en n8n |

### Por qué está hecho así

1. **Las ofertas vienen de portales reales, no de un modelo.**
   La versión anterior se las pedía a un modelo de lenguaje, que devolvía ofertas plausibles e inexistentes.
2. **El workflow de n8n vive en git, partido en piezas que se pueden diffear.**
   Un export de n8n es un JSON enorme con cada nodo de código dentro de un string escapado, así que un cambio de tres líneas es invisible en `git diff`. `wf-split` lo parte en piezas legibles, `wf-join` lo rehace, y `wf-check` tiene ocho reglas que salieron de averías reales. Ver [workflows/PROD](workflows/PROD/README.md).
3. **Las rutas de los webhooks no entran en el repositorio, y lo comprueba código.**
   Los webhooks ejecutan acciones con efectos externos, se midió que la autenticación por cabecera no funciona en ellos y las rutas llevaban meses publicadas; `check-secretos` falla en el hook de pre-commit y en CI, porque una regla escrita no es un control, un control es código que falla. Ver [ADR-001](docs/adr/ADR-001-proteccion-de-los-webhooks.md).
4. **Guardrails deterministas contrastan la salida con el CV maestro, en vez de más reglas en el prompt.**
   Un modelo no falla con una excepción: devuelve algo verosímil y peor, y añadir reglas a un prompt que ya lo satura lo empeora. Ver [`cv-server`](https://github.com/cookyourweb/cv-server).
5. **El CV lo escribe `claude-sonnet-4-6`, no Haiku.**
   Con unas 68 reglas en el prompt, Haiku se saltaba algunas de forma no determinista, y el sobrecoste medido es de 0,94 $ al mes para 40 CVs. Ver [ADR-002 de cv-server](https://github.com/cookyourweb/cv-server/blob/main/docs/ADR-002-modelo-del-cv.md).
6. **La cascada de modelos está escrita a mano, no con LiteLLM.**
   Se midió LiteLLM: +146 MB de disco, +5,96 s de arranque y 207 MB de RAM frente a 9 MB, demasiado para un servidor web pequeño. Ver [ADR-004 de cv-server](https://github.com/cookyourweb/cv-server/blob/main/docs/ADR-004-backend-llm.md).
7. **Dos puertas: entrada con Google y lista de invitadas para personas, clave de máquina (`X-Clave-Maquina`) para n8n.**
   Google no añade ningún servicio, ningún plan que caduque ni contraseñas que custodiar, mientras que el plan gratuito de Auth0 borra el tenant tras 150 días sin actividad; la clave de máquina separa las llamadas de las máquinas de la identidad de las personas. Ver [ADR-003](docs/adr/ADR-003-autenticacion.md).
8. **Notion hoy, Postgres en el plan gratuito de Neon después, y Notion congelado en solo lectura el día de la migración.**
   Desde el 2 oct 2026 el coste cero es el primer criterio, y Neon se despierta solo al llegar una consulta, mientras que la base gratuita de Render se borra y Supabase se pausa hasta que alguien la reactiva a mano; escribir en dos sitios es la forma más segura de desordenar los datos. Ver [ADR-002](docs/adr/ADR-002-donde-vive-postgres.md) y [ADR-005](docs/adr/ADR-005-notion-se-congela.md).

### Estructura del repositorio

| Pieza | Qué hace |
|---|---|
| `workflows/` | El workflow de n8n, partido en ficheros que git puede diffear |
| `scripts/wf-*.mjs` | Partir, rehacer, verificar y redactar el workflow |
| `scripts/*.py` | Utilidades sobre Notion y Drive |
| `docs/` | Decisiones, runbooks y reglas del sistema |
| `tests/` | Tests del núcleo de secretos y del formateo de ofertas |

### Arranque rápido

```bash
npm install          # sin dependencias: solo fija la version de node
npm test             # 25 tests con el runner de node, sin framework
npm run check:secretos
npm run hooks        # activa el hook de pre-commit
```

Requiere Node 20 o superior. Los scripts de Python necesitan `pip install -r requirements.txt`.

### Qué cubre ese verde

El badge y `npm test` ejecutan 25 tests: 22 sobre `scripts/lib/secretos.mjs` y 3 sobre
el formateo de ofertas. Se priorizó `secretos.mjs` porque es la única pieza cuyo fallo
no tiene vuelta atrás: si una ruta de webhook se escapa al repositorio, ya está publicada.

Lo que no cubre, dicho aquí para que nadie lo deduzca de un badge en verde:

| Pieza | Cobertura |
|---|---|
| `scripts/lib/secretos.mjs` | 22 tests |
| Formateo de ofertas (nodo del workflow) | 3 tests |
| `scripts/wf-*.mjs` | sin tests propios |
| `scripts/*.py` y `tools/*.py` | sin tests, y CI no los ejecuta |

CI corre sobre Node 20 y no instala Python. Es deuda declarada, no un descuido:
está anotada en [CONTRIBUTING](CONTRIBUTING.md).

---

## Operación del sistema

### Hacia dónde va

**La visión:** un acompañante para la búsqueda de empleo que trabaja con la
persona de principio a fin. Le ayuda a construir un CV maestro sólido, le
encuentra las ofertas que encajan, adapta cada candidatura sin inventar nada y la
prepara para la entrevista. La persona decide siempre; la IA propone, verifica y
avisa.

**Los principios, que ya se cumplen hoy:**

- **No inventar:** lo que escribe la IA se contrasta contra el CV maestro con detectores deterministas.
- **La persona decide:** ninguna candidatura sale sin aprobación humana.
- **Por invitación y con privacidad:** cada persona entra con su cuenta de Google y solo si está invitada.

#### Plan de acción

| Fase | Objetivo | Estado |
|---|---|---|
| 1. Acceso seguro | Entrada con Google por invitación en el panel; cerrar las rutas públicas que se fiaban de un email del cuerpo de la petición | Rutas cerradas en producción el 7-oct-2026; la entrada con Google, desplegada y pendiente de activar |
| 2. Identidad y datos por usuaria | Postgres en Neon con la identidad `(iss, sub)`, invitaciones de un solo uso y cada dato con su dueña | Siguiente |
| 3. Design system y landing | Componentes Angular sobre los tokens de marca ya probados, compartidos entre una landing pública prerenderizada y el panel | Siguiente |
| 4. CV maestro | Un comprobador que dice qué le falta al CV maestro antes de generar nada | Planificado |
| 5. Asistente del CV maestro | Ayuda a completar el CV entrevistando a la persona, sin inventar experiencia | Más adelante |
| 6. Claves de IA por usuaria | Cada persona trae su clave; ninguna petición cae a las claves de la dueña ([ADR-004](docs/adr/ADR-004-cada-usuaria-trae-su-clave-de-ia.md)) | Más adelante |
| 7. Preparación de entrevista | Por oferta: qué piden y qué evidencia tiene la persona; un simulador que no da respuestas para leer y no obedece instrucciones escondidas en una oferta | Más adelante |

Sin fechas a propósito: el plan dice el orden y el porqué, y el detalle de cada
fase se abre como issue.

### Qué falta

Lo que está por hacer se abre como
[issue](https://github.com/cookyourweb/buscartrabajo/issues), no se escribe aquí.
Una lista de próximos pasos escrita a mano envejece y acaba contradiciendo al código.
Las issues etiquetadas `seguridad` van primero.

Lo que sí queda escrito es lo que no es una tarea sino un estado del sistema, y
está en [CONTRIBUTING](CONTRIBUTING.md): las reglas de negocio del filtro viven
dentro de un prompt sin ningún test que las cubra, y las pruebas cubren solo
dos piezas. Eso no caduca porque describe cómo está hecho, no qué se piensa
hacer.

### Rutas de cv-server

| Ruta | Acceso | Para qué |
|---|---|---|
| `GET /` | Pública | Página de invitación |
| `GET /health` | Pública | Comprobar que el servicio está vivo |
| `GET /yo` | ID token de Google | Identifica a la persona que entra al panel |
| `POST /registro` | `X-Clave-Maquina` | Alta de usuario |
| `POST /generar-cv` | `X-Clave-Maquina` | CV adaptado al puesto, subido a Drive |
| `POST /generar-carta` | `X-Clave-Maquina` | Carta adaptada al puesto |
| `GET /usuarios` | `X-Clave-Maquina` | Lista de usuarios activos |
| `POST /crear-oferta` | `X-Clave-Maquina` | Crea una oferta en Notion |
| `POST /buscar-ofertas-reales` | `X-Clave-Maquina` | Búsqueda de ofertas desde cv-server |

El workflow de producción de n8n solo llama a `/health`, `/generar-cv` y
`/generar-carta`. El 7 de octubre de 2026 se eliminaron `/check-email`,
`/accion-existente` y el formulario de alta antiguo. La autenticación del panel se
explica en [ADR-003](docs/adr/ADR-003-autenticacion.md).

### Webhooks n8n

El workflow de producción expone webhooks para lanzar una búsqueda de un usuario y
para resolver una oferta (aprobar, descartar o mandarla a la empresa).

**Las rutas no se publican aquí.** Ejecutan acciones con efectos externos y hoy no
exigen credencial, así que la ruta es lo único que las protege (issue #1). Viven en
`workflows/PROD/secrets.local.json`, que está fuera de git, y en el workflow versionado
aparecen como `@@SECRET:<nodo>`.

Para recuperarlas en local: exportar el workflow desde n8n y pasarlo por
`node scripts/wf-split.mjs <export.json>`, que las separa a ese fichero.

**Una sola instancia de n8n activa.** n8n no permite dos workflows con el mismo path
de webhook activos a la vez, así que las instancias antiguas están deprecadas y no
deben reactivarse.

### Base de Datos Notion

#### DB Usuarios

| Columna | Tipo |
|---------|------|
| Name | Title |
| Email | Email (único) |
| Perfil | Rich text |
| Rol objetivo | Rich text |
| Stack | Multi-select |
| Salario min | Number |
| Modalidad | Multi-select |
| Ciudad | Rich text |
| LinkedIn | URL |
| CV Master URL | URL |
| cv_master_file_id | Rich text |
| Activo | Checkbox |

#### DB Ofertas

| Columna | Tipo | Qué guarda |
|---------|------|------------|
| Empresa | Title | nombre empresa |
| Puesto | Rich text | |
| Salario | Rich text | |
| Modalidad | Select | Remoto / Hibrido / Presencial |
| Link oferta | URL | url original (clave anti-spam) |
| Notas | Rich text | descripción corta |
| Estado | Select | Pendiente / Aprobado / Descartado / En proceso / Enviado a empresa |
| **Email Enviado** | Email | **email del usuario destinatario** |
| Usuario | Relation | relación a DB Usuarios |
| Nombre Contacto | Rich text | RRHH de la oferta |
| Email empresa | Email | contacto de la empresa (para envío auto) |
| Teléfono Contacto | Phone | |
| Fecha Publicacion | Date | |
| Fecha envio | Date | cuándo se generó carta+CV |
| Fecha Envio Empresa | Date | cuándo se mandó a la empresa |
| **Link CV Drive** | URL | **CV adaptado** a la oferta |
| **CV usado** | Rich text | **CV master** (referencia del que se partió) |
| **Carta Enviada** | Rich text | carta de presentación generada/editada |
| Seguimiento | Date | seguimiento manual |

**CV usado** es el CV master (la referencia de la que se partió). **Link CV Drive** es el CV adaptado (el resultado). Son dos CVs distintos.

### Debugging rápido

```bash
# 1. ¿CV Server vivo? Render Free duerme a los ~15 min y el arranque en frío tarda ~50 s
curl https://cv-server-ggd8.onrender.com/health

# 2. ¿El webhook de búsqueda responde?
#    La URL sale de workflows/PROD/secrets.local.json (fuera de git)
curl -X POST "$N8N_HOST/webhook/$RUTA_BUSCAR_AHORA" \
  -H "Content-Type: application/json" \
  -d '{"email":"tu@correo.com","nombre":"tu-nombre"}'
```

Si responden 200, el problema está en el flujo interno: revisa Executions en n8n.

### Gotchas y deuda conocida

- **Groq Free TPD = 200.000 tokens/día** (verificado el 2-oct-2026) es el cuello de botella real (no el RPM). Por eso el cap de **12 ofertas** en modo prueba. Agotarlo da 429 hasta el reset diario.
- **Variable de Render de cv-server** `WEBHOOK_BUSCAR_AHORA`: debe apuntar a la instancia de n8n activa. Si apunta a una instancia deprecada, la búsqueda se dispara en el vacío.
- **API keys**: tras rotarlas hay que actualizarlas en DOS sitios: credenciales n8n (Notion, Brevo) **y** env vars Render (Groq, Gemini, Notion, Google OAuth).
- **n8n**: al importar un workflow desde otra instancia, los IDs de credencial NO se mapean: reasigna la credencial nodo por nodo. Importar con *Import from File* SOBRE el workflow abierto (si no, se duplica).
- **Notion**: nombres de propiedad case-sensitive y con tildes (`Teléfono Contacto`, `Email empresa`). Mandar una propiedad con tipo equivocado da 400; mandar una que no existe en el payload no falla, pero escribir en un nombre inexistente sí rompe el PATCH.
- **Tipografía del CV/carta (cv-server)**: el `cv-server` sanea el texto antes de renderizar (`sanear_tipografia`): fuera guiones largos y flechas, que son rastro de IA y NO pueden salir a una empresa. Cuidado: el DOCX detecta la línea de empresa usando el guion largo como marcador, así que la detección sigue leyendo la línea cruda y solo se limpia el texto que se escribe. No metas un saneado global antes de parsear o pierdes las negritas.

---

El estado de este repositorio lo cuenta `git log`, no una línea escrita a mano al
final del README. El workflow que corre en producción está en [`workflows/PROD/`](workflows/PROD/README.md),
partido en piezas que git puede diffear.
