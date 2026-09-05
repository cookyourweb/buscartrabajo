# Documentación

Esta carpeta está partida por **lo que se puede hacer con cada cosa**, no por tema.
La distinción importa: aquí conviven documentos que describen el sistema de hoy con
otros que son el registro de por qué llegó a ser así, y mezclarlos hace que no te
puedas fiar de ninguno.

| Carpeta | Qué es | ¿Vigente? |
|---|---|---|
| [`adr/`](adr/) | Decisiones de arquitectura: qué se decidió, qué se descartó y por qué | Sí. Una ADR solo se sustituye por otra ADR |
| [`runbooks/`](runbooks/) | Qué hacer cuando pasa algo. Se leen con el sistema roto | Sí |
| [`referencia/`](referencia/) | Cómo funciona el sistema hoy y qué reglas se aplican | Sí |
| [`diseno/`](diseno/) | Lo que se va a construir y todavía no existe: diseños, tokens y decisiones abiertas | Sí, hasta que se construye. Entonces pasa a `referencia/` |
| [`historico/`](historico/) | Registro fechado: propuestas, auditorías y arreglos ya aplicados | **No.** Se conserva por el porqué, no por el qué |

## Cómo leerla

**Si vienes a entender el sistema**, empieza por el [README](../README.md), sigue por
[cómo entra una oferta](referencia/10-COMO-ENTRA-UNA-OFERTA-2026-07-23.md) y termina en
[ADR-001](adr/ADR-001-proteccion-de-los-webhooks.md), que es la decisión que más
condiciona el resto.

**Si algo está roto**, ve directo a `runbooks/`.

**Si te preguntas por qué algo es como es**, `historico/`. Está fechado a propósito: un
documento de julio describe julio, y eso es exactamente lo que se le pide.

## Las reglas no están aquí

Las reglas del proyecto viven en [`CONTRIBUTING.md`](../CONTRIBUTING.md), en la raíz.
Lo que está en `docs/` hay que ir a buscarlo, y por eso se olvida.
