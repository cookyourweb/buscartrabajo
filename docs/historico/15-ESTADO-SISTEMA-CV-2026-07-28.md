# Estado del sistema de CVs

**28 jul 2026** · Resumen de la sesión del 27-28. Ocho commits, todo en `main` y desplegado.

---

## ⏭️ LO ÚNICO PENDIENTE

**Regenerar PANEL Sistemas Informáticos.**

En Notion, `Ofertas de Trabajo` → PANEL → Estado a `Pendiente` y luego otra vez a
`Aprobado`. La oferta ya apunta al usuario correcto, así que el CV saldrá con la
identidad buena.

Revisarlo con:

```bash
python3 buscartrabajo/scripts/revisar_cv_generado.py <file_id_de_drive>
```

Comparar contra el de la mañana del 28 (`1bh2R0AXk00XoVPZsgyeXCV19wuqJpqu2`), que
salió con la identidad equivocada. **Si sale limpio → lanzar Revolut y Malwarebytes**
(esas dos ya apuntaban al registro bueno; no hizo falta tocarlas).

---

## Antes → después

| | Antes | Ahora |
|---|---|---|
| Modelo del CV | Haiku 4.5 (4/5 checks fallando) | **Sonnet 4.6 (1/5)** |
| Usuarios en Notion | 2 registros derivados de la misma persona | **1 usuario, 2 cuentas** |
| Ofertas mal asignadas | 5 | **0** |
| `/health` | Mentía: `llm_provider: groq` | Declara los 3 modelos reales |
| Fallback de Claude | Modelo retirado → 404 | `claude-haiku-4-5` |
| Guardrails | 3, todos de salida | **4** (el nuevo mira la entrada) |
| Tests | 87 | **125** |

---

## Los cinco hallazgos

### 1. El CV lo escribía Haiku y la carta Sonnet

Estaba invertido: el documento crítico con el modelo pequeño. El prompt tiene **68
directivas simultáneas** y Haiku cumplía la mayoría, saltándose unas cuantas de forma
no determinista.

**La prueba:** con el mismo commit en producción, el titular salía perfecto para el
puesto `Applied AI Engineer` y roto para `Senior Product Engineer (Fullstack)`. Un bug
de código falla **siempre igual**; esto fallaba **distinto cada vez**.

**Corolario:** añadir más reglas al prompt lo empeora. Es pedirle a un modelo saturado
que sostenga 75 restricciones en vez de 68. → `cv-server/docs/ADR-002`

### 2. El coste medido resultó ser la mitad de lo estimado

Con `count_tokens` sobre el prompt real:

| Modelo | Tokens in | $/CV | 40 CVs/mes |
|---|---|---|---|
| Haiku 4.5 | 3.532 | $0,0117 | $0,47 |
| **Sonnet 4.6** | 3.532 | $0,0352 | **$1,41** |
| Sonnet 5 | **5.313** | $0,0353 | $1,41 |

**Diferencia real: $0,94/mes.** La estimación previa (~1,50 €) estaba inflada un 70%.

**Sonnet 5 cuenta un 50% más de tokens para el mismo texto** (tokenizador nuevo), así
que su precio introductorio más bajo se lo come entero: sale igual que Sonnet 4.6 y
además arriesga truncado por adaptive thinking. Por eso no se subió.

### 3. `CV_MODEL` no existía, y el fallback llevaba 3 meses muerto

`CV_MODEL` se lee en el código (línea 56) pero **nunca se declaró** en ningún `.env`:
siempre corrió con el valor por defecto. Y `CLAUDE_MODEL` apuntaba a
`claude-3-haiku-20240307`, **retirado el 19 de abril**: si Groq fallaba, la cadena
devolvía 404.

### 4. Dos registros de usuario derivaron

Las ofertas llegan a dos buzones y se habían creado dos registros. El segundo quedó con
el Master a medias (4.689 chars **sin `PERFIL BASE`**, frente a 8.702 del bueno), sin
`Email CV` y con la ciudad en minúsculas.

El CV de PANEL salió con cabecera `<correo antiguo>`, titular haciendo **eco
literal de la vacante** (`Tech Lead Full Stack | Java · Angular · Microservicios`) y
tecnologías ajenas (Maven, Oracle).

**El guardrail del titular no saltó**, y no por un bug: ese Master no tiene `PERFIL
BASE`, así que no había contrato contra el que validar. Un guardrail que depende de un
dato solo protege cuando el dato existe. → `cv-server/docs/ADR-003`

### 5. El nombre del campo fallaba en silencio

El código exigía `Emails alias`; el campo se creó como `Email alias`. El campo existe,
el código no lo ve, y **no hay error**. Un fallo así vive meses. Ahora se aceptan
variantes.

---

## Qué se construyó

**`cv-server`**

- `evaluar_descripcion_oferta()` — guardrail de **entrada**. Las ofertas de LinkedIn e
  Indeed llegan con 172-245 caracteres (el titular reformulado, a veces con el
  metacomentario del scraper); las de Tecnoempleo y Remotive, con 991-1800. Umbral 400
  (`DESCRIPCION_MINIMA`). **Avisa, no rechaza**, para no romper n8n.

  Es el único fallo que los otros tres no ven: miran la salida, y un CV genérico no
  inventa nada — simplemente no dice nada.

- `emails_de_usuario()` / `usuario_tiene_email()` — un usuario, N cuentas.
  `buscar_usuario_por_email` hace dos pasadas y **verifica exacto en Python**, porque el
  `contains` de Notion es de subcadena: `ana@ejemplo.com` casa con `mariana@ejemplo.com`.

- **Bug latente arreglado en `api.py`** — `GenerarCVResponse` no declaraba ningún
  guardrail. `response_model` filtra lo no declarado, así que al desplegar FastAPI los
  avisos de tecnologías inventadas habrían dejado de llegar **sin error ni rastro**.

- `/health` v2.4 declara `modelos: {cv, carta, fallback}`.
- `.env.example` documenta las variables que faltaban.

**`buscartrabajo`**

- `scripts/revisar_cv_generado.py` — los cinco fallos **medidos**, no teóricos.
  Validado contra el crudo de Malwarebytes, donde caza 4/5.
- `scripts/subir_cv_drive.py` — sube a `FOLDER_CV_GENERADOS` solo con stdlib.

---

## Migración de Notion (ya ejecutada por API)

1. `Email alias = <correo antiguo>` en el registro bueno
2. Cinco ofertas reapuntadas: Grupo NS, PANEL, Clipster, A.Team, EXDESIS
3. Registro `veronica serna` **desactivado, no borrado** (si algo lo referencia, la
   relación sobrevive)
4. Verificado: **0** ofertas apuntando al duplicado

---

## Agujeros conocidos (abiertos)

- **Los guardrails no detectan afirmaciones de rol.** Comparan texto contra el Master,
  así que cazan `FastAPI` y cazan `166.000`, pero no *"designed backend services"* ni
  *"built resilient systems"*, que son semánticas. Cuatro casos reales confirmados.
- **Nada avisa de un Master sin bloque `PERFIL BASE`.** Es lo que dejó pasar el titular
  con eco en PANEL.
- **De 15 ofertas pendientes, 9 no tienen descripción utilizable** (LinkedIn e Indeed).
  Para probar solo sirven las de Tecnoempleo y Remotive: PANEL, Grupo NS, A.Team ×2,
  Lemon.io, Clipster.

---

**Relacionado:** `cv-server/docs/ADR-002-modelo-del-cv.md`,
`cv-server/docs/ADR-003-usuario-multicuenta.md`,
`docs/09-RUNBOOK-OFERTA-CONTACTO-DIRECTO`, `docs/14-ESTRATEGIA-BUSQUEDA-PAN-VS-TECHO`
