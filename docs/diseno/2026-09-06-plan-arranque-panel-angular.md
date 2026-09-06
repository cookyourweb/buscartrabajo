# Panel de empleo en Angular: plan de arranque

Fecha: 2026-09-06
Estado: preparado, sin arrancar
Continúa a: `2026-09-05-panel-empleo-angular-design.md`

## El mapa: qué hay y cómo convive

Son cuatro piezas que ya existen y una que se añade. Ninguna se reescribe.

| Pieza | Repositorio | Qué es | Papel |
|---|---|---|---|
| Captación | `buscartrabajo` (`workflows/`) | Workflows de n8n | Capta ofertas y las escribe en Notion |
| Sistema | `buscartrabajo` | Python y scripts | Filtros, reglas y documentación de decisiones |
| Motor | `cv-server` | FastAPI en Render | Genera el CV y la carta adaptados |
| Marca | `cookyourwebai` | React, sitio de la agencia | Cantera del design system |
| **Cara** | **`panel-empleo`** | **Angular 22** | **Lo que se añade** |

Los tres papeles que no hay que confundir:

- **`cv-server` es el motor.** El panel le habla a él. No se reescribe ni se duplica.
- **`cookyourwebai` es la cantera del diseño.** De ahí salen las rampas y los tokens
  medidos. El panel los hereda; la web de la agencia no depende del panel.
- **Angular es lo que se viene a practicar.** Es el hueco declarado del currículum, y
  por eso el panel va en repositorio propio: para que se vea.

En una frase: el panel es la cara en Angular de un motor que ya funciona, vestido con
la marca de CookYourWeb.

### Cómo conviven

```
n8n  ->  Notion
                \
                 '->  cv-server (FastAPI)  <-  panel-empleo (Angular)
                          |
                          '->  Postgres, Drive, modelos

cookyourwebai: no participa en tiempo de ejecución.
               Aporta los tokens, que se copian.
```

Reglas de convivencia:

- **El panel solo habla con `cv-server`.** Nunca con Notion, ni con Drive, ni con un
  modelo de lenguaje. El navegador no ve jamás un token de terceros.
- **`buscartrabajo` no depende del panel.** Sigue funcionando por línea de comandos
  aunque el panel no exista. El panel sustituye la interfaz, no el sistema.
- **`cookyourwebai` y el panel comparten tokens, no código.** Se copian, con sus tests.
  Si un día duele mantenerlos en dos sitios, se extraen a un paquete.
- **En cada momento se escribe en un solo sitio.** La regla del diseño del 5 de
  septiembre sigue vigente: en la rebanada 1 Notion es la verdad y el panel solo lee.

## Qué cambió desde el diseño del 5 de septiembre

El diseño mandaba llevar los colores a Figma, medir contrastes y después bajarlos al
código. **Los dos primeros pasos ya están hechos, y en código.**

El 6 de septiembre se implantó el design system en `cookyourwebai`: las cuatro rampas
completas, los tokens semánticos apuntando a ellas y veinticuatro tests que calculan
el contraste con la fórmula de WCAG y fallan si un par baja del mínimo. Está en
producción.

Los tokens dejaron de ser una propuesta. Meterlos ahora en Figma para volver a bajarlos
crearía una segunda fuente de verdad, que es justamente lo que ese trabajo corrigió.

**Figma entra después, para las pantallas**: layout, componentes y variantes. Ahí sí
aporta. Para los colores ya no.

## Decisiones tomadas

| Decisión | Elección | Motivo |
|---|---|---|
| Dónde vive | Repositorio propio, `panel-empleo` | Ver más abajo |
| Framework | Angular 22, standalone y signals | Hueco declarado en el CV |
| Runner de tests | Vitest | Soportado oficialmente por Angular 22; Karma está en las últimas |
| Tokens | Se copian de `cookyourwebai` con sus tests | Ya están medidos y protegidos |
| Figma | Después, y solo para pantallas | Los colores ya están decididos |

### Por qué repositorio aparte

Medido el 6 de septiembre: GitHub etiqueta `buscartrabajo` como **Python** (79.130
bytes de Python contra 72.143 de JavaScript). De los veinte repositorios de la cuenta,
**ninguno es Angular**: los que aparecen como TypeScript son React.

Un panel Angular enterrado en una subcarpeta de un repositorio que GitHub muestra como
Python deja la única evidencia de Angular donde nadie la mira. Quien revisa un perfil
abre y mira; no bucea.

Con repositorio propio hay README propio, TypeScript como lenguaje dominante,
integración continua con una sola suite y despliegue independiente. Y desaparece el
`package.json` anidado, que obligaría a ejecutar dos suites distintas en el mismo
flujo.

No va dentro de `cookyourwebai`: ese es el sitio de la agencia y el panel es otro
producto.

### Qué pasa con el design system compartido

Los tokens se copian al panel. Si algún día duele mantenerlos en dos sitios, se
extraen a un paquete.

Copiar dos veces está bien. Abstraer antes de la tercera es prematuro, y crea una
dependencia que hay que versionar y publicar para dos consumidores.

## Bloqueante antes de empezar

**Angular 22 no arranca con el Node instalado.**

- Exige `^22.22.3 || ^24.15.0 || >=26.0.0`
- Instalado hoy: `v20.19.3`, y es la única versión en `nvm`

Se resuelve con `nvm install 22`. No afecta al Node global: `nvm` cambia la versión por
terminal, así que el resto de proyectos siguen igual.

## Pasos, en orden

1. **Node 22.** `nvm install 22`. Sin esto no hay nada.
2. **Crear el repositorio** `panel-empleo`, público, y el andamiaje con `ng new`:
   standalone, signals, sin renderizado en servidor, Vitest como runner.
3. **Portar el design system.** Las cuatro rampas y los tokens semánticos como custom
   properties, y con ellos `contrast.ts`, `tokens.ts` y sus veinticuatro tests. La
   primera suite queda en verde el primer día y el sistema nace protegido.
4. **Integración continua desde el primer commit.** El mismo flujo que ya funciona en
   `buscartrabajo` y en `cookyourwebai`: instalar con `npm ci`, ejecutar los tests y
   compilar, en cada push y en cada pull request.
5. **Rebanada 1, con test primero.** Empezando por la interfaz de datos, que es lo que
   permite que la demo pública no dependa de ningún backend vivo.

## Cómo se trabaja

- Un test que falla, la pieza mínima que lo pone en verde, y commit. Sin excepciones.
- Commits pequeños, cada uno con una decisión explicada. Nada de un commit gigante.
- Una pull request por rebanada, no una al final. Con la suite en verde y el preview
  desplegado antes de mezclar.
- Arquitectura, nombres de dominio y prioridades se preguntan. El detalle de
  implementación se resuelve y se cuenta.

## Qué no entra en el arranque

- Tocar `cv-server`. Su falta de autenticación es trabajo aparte y está documentada.
- Migrar nada de Notion. En la rebanada 1 Notion sigue siendo la verdad.
- Figma.
- Postular automáticamente, que ya quedó fuera en el diseño.

## Pendiente de decidir al arrancar

Si el trabajo pasa antes por el flujo de desarrollo dirigido por especificación
(propuesta, especificaciones, diseño y tareas escritas antes del código) o se va
directo a las rebanadas con test primero.

Lo primero es más lento al principio y deja un rastro de decisiones en el repositorio.
Lo segundo es más rápido y ya demostró funcionar el 6 de septiembre.
