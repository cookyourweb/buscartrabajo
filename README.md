# BuscarTrabajo

[![tests](https://github.com/cookyourweb/buscartrabajo/actions/workflows/tests.yml/badge.svg)](https://github.com/cookyourweb/buscartrabajo/actions/workflows/tests.yml)

Sistema multiusuario que busca ofertas de empleo reales cada mañana, las filtra por
el perfil de cada persona y se las manda por correo. Al aprobar una, genera el CV y
la carta adaptados al puesto y permite enviarlos a la empresa.

En producción desde julio de 2026.

## Los tres repositorios

| Repositorio | Qué es | Dónde corre |
|---|---|---|
| `buscartrabajo` (este) | Workflows de n8n, scripts, ADR y runbooks | n8n en Render |
| [`cv-server`](https://github.com/cookyourweb/cv-server) | Servicio Python (Flask) que genera CV y carta con guardrails de veracidad | Render, plan gratuito |
| `panel-empleo` | Panel en Angular para ver y gestionar las ofertas. El acceso es por invitación, con cuenta de Google; la demo pública no muestra datos reales | En desarrollo |

n8n busca y orquesta, `cv-server` escribe y valida, el panel es la cara visible.

## Qué tiene de interesante

**Las ofertas son reales.** La versión anterior se las pedía a un modelo de lenguaje,
que devolvía ofertas plausibles e inexistentes. Ahora vienen de tres fuentes
(Remotive, Adzuna, Tecnoempleo), se filtran por el stack del usuario y se descartan
las que ya están guardadas.

**El texto lo escribe un modelo, la verdad no.** La generación de CV y carta vive en
[`cv-server`](https://github.com/cookyourweb/cv-server), un servicio aparte con
guardrails de veracidad y casos de evaluación construidos sobre fallos reales de
producción. Un modelo no falla con una excepción: devuelve algo verosímil y peor.

**Los secretos no dependen de que nadie se acuerde.** Los webhooks de n8n ejecutan
acciones con efectos externos, así que sus rutas no pueden entrar en un repositorio
público. `check-secretos` lo comprueba en el hook de pre-commit y en CI, y falla si
encuentra una. Se escribió después de descubrir que llevaban meses publicadas: una
regla escrita no es un control, un control es código que falla.
Ver [ADR-001](docs/adr/ADR-001-proteccion-de-los-webhooks.md).

**El workflow de n8n se puede diffear.** Un export de n8n es un JSON de 91k con cada
nodo de código dentro de un string escapado: un cambio de tres líneas es invisible en
`git diff`. `wf-split` lo parte en piezas legibles, `wf-join` lo rehace, y `wf-check`
tiene ocho reglas que salieron de averías reales. Ver [workflows/PROD](workflows/PROD/README.md).

## Arranque rápido

```bash
npm install          # sin dependencias: solo fija la version de node
npm test             # 25 tests con el runner de node, sin framework
npm run check:secretos
npm run hooks        # activa el hook de pre-commit
```

Requiere Node 20 o superior. Los scripts de Python necesitan `pip install -r requirements.txt`.

## Qué cubre ese verde

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

## Qué falta

Lo que está por hacer se abre como
[issue](https://github.com/cookyourweb/buscartrabajo/issues), no se escribe aquí.
Una lista de próximos pasos escrita a mano envejece y acaba contradiciendo al código.
Las issues etiquetadas `seguridad` van primero.

Lo que sí queda escrito es lo que no es una tarea sino un estado del sistema, y
está en [CONTRIBUTING](CONTRIBUTING.md): las reglas de negocio del filtro viven
dentro de un prompt sin ningún test que las cubra, y las pruebas cubren solo
dos piezas. Eso no caduca porque describe cómo está hecho, no qué se piensa
hacer.

## Piezas

| Pieza | Qué hace |
|---|---|
| `workflows/` | El workflow de n8n, partido en ficheros que git puede diffear |
| `scripts/wf-*.mjs` | Partir, rehacer, verificar y redactar el workflow |
| `scripts/*.py` | Utilidades sobre Notion y Drive |
| `docs/` | Decisiones, runbooks y reglas del sistema |
| `tests/` | Tests del núcleo de secretos |

---

## Arquitectura

Tres piezas. n8n orquesta, `cv-server` genera y valida, el panel muestra.

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

Modelos de lenguaje en `cv-server`: CV con Claude Haiku 4.5 y carta con Claude Sonnet
4.6 (Groq de fallback). Resto de usos: Groq `openai/gpt-oss-120b`, Gemini 3.6 Flash y
Claude Haiku 4.5, en ese orden.

---

## Servicios

| Servicio | Propósito |
|----------|-----------|
| cv-server (Render free) | Página de invitación, API de usuarios y generación de CV y carta |
| n8n (Render) | Orquestador del workflow de búsqueda y aprobación |
| Notion | CRM de usuarios y ofertas |
| Google Drive | CVs adaptados |
| Brevo | Envío de correos |
| Groq | LLM de ofertas y fallback de CV y carta (`openai/gpt-oss-120b`) |

**Una sola instancia de n8n activa.** n8n no permite dos workflows con el mismo path
de webhook activos a la vez, así que las instancias antiguas están deprecadas y no
deben reactivarse.

---

## Webhooks n8n

El workflow de producción expone webhooks para lanzar una búsqueda de un usuario y
para resolver una oferta (aprobar, descartar o mandarla a la empresa).

**Las rutas no se publican aquí.** Ejecutan acciones con efectos externos y hoy no
exigen credencial, así que la ruta es lo único que las protege (issue #1). Viven en
`workflows/PROD/secrets.local.json`, que está fuera de git, y en el workflow versionado
aparecen como `@@SECRET:<nodo>`.

Para recuperarlas en local: exportar el workflow desde n8n y pasarlo por
`node scripts/wf-split.mjs <export.json>`, que las separa a ese fichero.

---

## Base de Datos Notion

### DB Usuarios

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

### DB Ofertas

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

---

## Debugging rápido

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

---

## Gotchas y deuda conocida

- **Groq Free TPD = 100.000 tokens/día** es el cuello de botella real (no el RPM). Por eso el cap de **12 ofertas** en modo prueba. Agotarlo da 429 hasta el reset diario.
- **Variable de Render de cv-server** `WEBHOOK_BUSCAR_AHORA`: debe apuntar a la instancia de n8n activa. Si apunta a una instancia deprecada, la búsqueda se dispara en el vacío.
- **API keys**: tras rotarlas hay que actualizarlas en DOS sitios: credenciales n8n (Notion, Brevo) **y** env vars Render (Groq, Gemini, Notion, Google OAuth).
- **n8n**: al importar un workflow desde otra instancia, los IDs de credencial NO se mapean: reasigna la credencial nodo por nodo. Importar con *Import from File* SOBRE el workflow abierto (si no, se duplica).
- **Notion**: nombres de propiedad case-sensitive y con tildes (`Teléfono Contacto`, `Email empresa`). Mandar una propiedad con tipo equivocado da 400; mandar una que no existe en el payload no falla, pero escribir en un nombre inexistente sí rompe el PATCH.
- **Tipografía del CV/carta (cv-server)**: el `cv-server` sanea el texto antes de renderizar (`sanear_tipografia`): fuera guiones largos y flechas, que son rastro de IA y NO pueden salir a una empresa. Cuidado: el DOCX detecta la línea de empresa usando el guion largo como marcador, así que la detección sigue leyendo la línea cruda y solo se limpia el texto que se escribe. No metas un saneado global antes de parsear o pierdes las negritas.

---

El estado de este repositorio lo cuenta `git log`, no una línea escrita a mano al
final del README. El workflow que corre en producción está en [`workflows/PROD/`](workflows/PROD/README.md),
partido en piezas que git puede diffear.
