# Runbook: oferta que llega por contacto directo

> Escrito el 23-jul-2026 después de tardar más de una hora en sacar el CV de Tenth
> Revolution. El objetivo de este documento es que la próxima vez sean quince minutos.

## Cuándo aplica

Un recruiter escribe por LinkedIn, por email o llama. La oferta NO viene del workflow n8n
ni de la tarea programada, así que no está en Notion y el sistema no sabe que existe.

---

## Los cinco pasos

### 1. Meter la oferta en Notion

**Cómo:** contándosela a Claude en la conversación y pegando el mensaje del recruiter.
Claude crea la página. No hay formulario ni endpoint que usar.

La página va en la data source `collection://33d11515-f4b2-8176-947b-000bbafd1ca7`
con estos campos como mínimo: `Empresa`, `Puesto`, `Descripción`, `Salario`, `Modalidad`,
`Ubicación`, `Estado`, `Idioma`, `Usuario`.

- `Estado`: **`Aprobado`**. Una oferta de contacto directo entra por el final del
  recorrido, no por el principio: la decisión de que interesa ya está tomada cuando el
  recruiter escribe, y `Aprobado` es lo que dispara la generación de CV y carta. No hace
  falta un estado nuevo del tipo "Me han contactado". El porqué está en
  `10-COMO-ENTRA-UNA-OFERTA-2026-07-23.md`.
- Las nueve opciones válidas y quién pone cada una están en
  `10-COMO-ENTRA-UNA-OFERTA-2026-07-23.md`.
- **Siempre en `Ofertas de Trabajo`, nunca en `Candidaturas`**: esta última no tiene
  `Descripción` ni `Idioma`, y sin ellos no se puede generar un CV adaptado.
- `Usuario`: `["https://app.notion.com/p/34b11515f4b2817980ecc0b6d2093abb"]`
- `Notas`: aquí van el estado de la conversación, lo que ha pedido el recruiter y **los
  gaps conocidos**. Es lo que evita repetir el análisis dentro de dos semanas.
- El cuerpo de la página: pegar el mensaje original completo y el histórico de respuestas.

**Ojo:** el multi_select `Tags` no tiene opciones definidas. Mandar cualquier valor da
`validation_error`. O se dejan vacías o se añaden antes las opciones al schema.

**No usar `POST /crear-oferta`**: devuelve 404 (usa el id del data source donde Notion
espera el id de la database). Ver el bug en la memoria del proyecto.

### 2. Generar el CV

> **El CV lo escribe el prompt. Nunca Claude a mano en el chat.**
>
> El 23 de julio se sacó el CV de Tenth Revolution corrigiendo a mano cada fallo según
> aparecía. Salió un buen CV y el sistema quedó igual de roto: el prompt no aprendió nada.
> Cuando el CV generado falla, se arregla **el prompt del cv-server**, no el CV. Corregir
> el resultado esconde el problema y garantiza repetirlo en la siguiente oferta.

```bash
curl -s -X POST https://cv-server-ggd8.onrender.com/generar-cv \
  -H 'Content-Type: application/json' \
  -d '{"email":"hello.cookyourweb@gmail.com","empresa":"...","puesto":"...","idioma":"es","descripcion":"..."}'
```

Notion NO hace falta para esto: el endpoint acepta empresa, puesto y descripción sueltos.
Notion es para el seguimiento.

En la `descripcion` va el anuncio **más lo que haya pedido el recruiter en la llamada**.
Eso último es oro y no está en ningún anuncio.

### 3. LEER el CV generado. Siempre.

El endpoint devuelve un link de Drive. Hay que abrirlo y leerlo. No vale con que la
respuesta diga `ok: true`.

Lista de comprobación, que son los fallos reales que se han dado. **Cada casilla que salga
marcada es un arreglo en el prompt, no una corrección a mano del documento:**

- [ ] ¿Hay alguna **tecnología que la oferta pide y Vero no tiene**? (coló PHP/Symfony
      con la fórmula ambigua "contexto de integración con arquitecturas PHP/Symfony")
- [ ] ¿Aparece lo que el recruiter pidió expresamente?
- [ ] ¿El titular es una **identidad real** (`Frontend Tech Lead` / `Full-Stack Developer`
      / `UX Engineer`) y no el título de la vacante?
- [ ] ¿Hay **verbos de liderazgo** en el cuerpo si el puesto no pide lead/manager?
      (`rg -i 'lider|responsable|coordinando|a cargo|dirig'`)
- [ ] ¿Alguna frase se puede rastrear **casi literal hasta el anuncio**? Eso se borra.
- [ ] ¿Alguna cifra que no esté en el Master? (el guardrail lo comprueba y devuelve
      `cifras_no_respaldadas`, pero conviene mirarlo)

Nota sobre Drive: `read_file_content` puede devolver vacío en la primera llamada sobre un
`.docx`. Reintentar antes de dar por hecho que no se puede leer.

### 4. Pasarlo a PDF

El cv-server entrega `.docx`. A las empresas se manda PDF.

```bash
python3 -m venv venv-pdf && ./venv-pdf/bin/pip install reportlab
./venv-pdf/bin/python buscartrabajo/tools/cv_md_a_pdf.py CV.md CV.pdf
```

En macOS hace falta el venv: PEP 668 bloquea `pip install` sobre el Python del sistema.

Nombre del archivo con el puesto dentro, que en la bandeja de un recruiter un archivo que
solo lleve el nombre se pierde: `CV-Veronica-Serna-Perez-Frontend-Tech-Lead.pdf`.

### 5. Cerrar el círculo en Notion

Rellenar `Link CV Drive` y `CV usado`, y dejar el `Estado` que corresponda.

---

## Por qué la vez anterior tardó más de una hora

No fue el CV. Fueron las correcciones que se podían haber evitado:

1. `/crear-oferta` devolvió 404 y hubo que diagnosticarlo en caliente.
2. El CV generado incumplió DOS reglas que ya estaban escritas en el prompt (nivel del
   puesto y regla de evidencia sobre tecnologías), y hubo que arreglarlo a mano.
3. El perfil hacía eco del anuncio y hubo que limpiarlo.
4. Varias vueltas de redacción del párrafo de IA por no tener escrito cómo se quiere
   contar esto.

Las cuatro se arreglan en el origen, no repitiendo el trabajo manual cada vez.

## Pendiente para que este runbook sobre

- [x] ~~Guardrail de tecnologías en el prompt del cv-server (regla de evidencia: la
      tecnología entra solo si el Master la respalda)~~ **HECHO 23-jul**, commit `b3c98d2`
      en `cv-server`. `/generar-cv` devuelve `tecnologias_no_respaldadas`. Falta desplegar
      a PROD.
- [ ] Que la regla de NIVEL DEL PUESTO se cumpla de verdad (existe en
      `cv_server_railway.py:1381-1385` y no se aplicó)
- [ ] Regla anti-eco en el prompt (ya documentada en
      `cv-server/docs/PROMPT-ADAPTACION-CV.md`, falta llevarla al prompt)
- [ ] Export a PDF dentro del propio cv-server, para no hacerlo a mano
- [ ] Arreglar el 404 de `/crear-oferta` (id database contra id data source)

---

**Generado:** 23 julio 2026, tras el proceso de Tenth Revolution Group.
