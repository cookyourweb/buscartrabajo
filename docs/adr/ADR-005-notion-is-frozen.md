# ADR-005. Notion se congela el día de la migración

**Fecha:** 2 oct 2026 · **Estado:** aceptado

---

## Contexto

Hoy las ofertas y las candidaturas viven en una base de Notion, que escriben el bot
de n8n, `cv-server` y la dueña a mano. El destino es Postgres
([ADR-002](ADR-002-donde-vive-postgres.md)), con el panel en Angular como sitio de
trabajo.

Dos sitios donde se escribe lo mismo es la forma más segura de que los datos se
desordenen: algo se actualiza en uno y no en el otro, y deja de saberse cuál es el
bueno. Ya pasó con dos registros de la misma persona: salió un CV con la cabecera
equivocada ([modelo de datos](../diseno/2026-09-07-modelo-de-datos.md)).

Había tres opciones: congelar Notion, mantenerlo como copia sincronizada, o
eliminarlo.

## Decisión

**El día de la migración, Notion pasa a ser de solo consulta.** Todo lo nuevo se
escribe en Postgres y se trabaja desde el panel. Notion queda como archivo de lo
anterior.

- **Antes de migrar** se hace una copia completa de la base y se comprueba que el
  número de fichas copiadas coincide con el de Notion.
- **"Solo consulta" es un control, no una promesa.** La integración de Notion pasa
  a tener solo permiso de lectura, y se retira la credencial de escritura de n8n y
  de `cv-server`.
- **Desde ese día, n8n escribe en Postgres a través de `cv-server`,** con la clave
  de máquina ([ADR-003](ADR-003-autenticacion.md)). Nunca directamente en la base.

## Hasta la migración

Notion es la verdad. Si el panel ofrece "Eliminar" antes de migrar, la ficha va a
la papelera de Notion y antes se guarda su huella (enlace, y empresa con puesto)
fuera de Notion, para que el bot no vuelva a traer esa oferta.

## Consecuencias

**Se acepta:**

- Lo que haya en Notion después de la migración no se ve en el panel.

**Se gana:**

- Un solo sitio donde está la verdad.
- El bot deja de escribir en Notion, y con él desaparece como problema el límite
  de bloques del plan gratuito para espacios con varios miembros.

## Cuándo se revisa

Solo si hiciera falta volver a escribir fuera del panel. La respuesta por defecto
es exportar desde Postgres, no volver a escribir en dos sitios.

---

**Fuentes, consultadas el 2 oct 2026:** developers.notion.com/reference/capabilities ·
notion.com/pricing

**Relacionado:** [ADR-002](ADR-002-donde-vive-postgres.md) ·
[ADR-003](ADR-003-autenticacion.md) · [modelo de datos](../diseno/2026-09-07-modelo-de-datos.md)
