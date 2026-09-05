# Tokens del design system: punto de partida medido

Fecha: 2026-09-05
Origen: `~/cookyourweb/cookyourwebai`
Estado: propuesta lista para llevar a Figma como Variables

## De dónde sale cada cosa

**Se toma** de la web actual: los cuatro colores de marca, la pareja tipográfica y los
nombres de los tokens semánticos, que están bien elegidos.

**No se toma**: los valores grises de fábrica de la plantilla, los hexadecimales
repetidos a mano ni el `#BB60D1`, que no está declarado en ninguna paleta.

## El hallazgo: es una marca de fondo oscuro

Contraste medido de los colores tal como están hoy. El mínimo de WCAG AA para texto
normal es 4.5:1, y 3:1 para texto grande.

| Color | Hex | Sobre blanco | Sobre `#0a0a0a` |
|---|---|---|---|
| cian | `#32e2ec` | **1.59:1**, no vale para texto | 12.47:1 |
| verde | `#3fec71` | **1.56:1**, no vale para texto | 12.68:1 |
| magenta | `#ec32c7` | 3.59:1, solo texto grande | 5.51:1 |
| violeta | `#8f32ec` | 5.48:1 | 3.62:1, solo texto grande |

Tres de los cuatro colores son inservibles para texto sobre blanco, y los mismos tres
dan más de 5:1 sobre negro. El cian y el verde llegan a 12,5:1, que es excelente.

**Decisión que se deriva: el tema oscuro es el principal.** No es una preferencia
estética. Es donde la marca ya está pensada y donde funciona.

El tema claro existe igualmente, y usa los pasos profundos de cada rampa.

## Escalas

Generadas en OKLCh, que es perceptualmente uniforme: los saltos se ven regulares, cosa
que no ocurre interpolando en HSL. El croma se reduce automáticamente cuando un paso se
sale del espacio de color representable.

Los valores están también en `tokens-color.json`, listos para importar.

### cian
```
50 #dafdff   100 #a2f9ff   200 #45eef8   300 #0ad3dd   400 #06b7c0
500 #039ca4  600 #018188   700 #01656a   800 #00494d   900 #002d30
```

### magenta
```
50 #fff0fa   100 #ffdcf3   200 #ffbceb   300 #ff8ce0   400 #ff48d8
500 #e224be  600 #c001a1   700 #97007e   800 #70015c   900 #47003a
```

### violeta
```
50 #f7f3ff   100 #ece2ff   200 #dccaff   300 #c8a7ff   400 #b583ff
500 #a457ff  600 #8e30eb   700 #7301c7   800 #540194   900 #34005f
```

### verde
```
50 #dfffe3   100 #adffb9   200 #51f97e   300 #28de64   400 #01c251
500 #00a544  600 #038937   700 #006b29   800 #004e1c   900 #00300f
```

En las cuatro rampas, **los pasos 600 a 900 pasan AA sobre blanco**. Del 50 al 500 son
para fondo oscuro, para fondos suaves o para elementos que no son texto.

Los neones originales no desaparecen: viven alrededor del paso 200 y son los que
brillan sobre oscuro. Y el `#BB60D1` huérfano queda cubierto por la rampa violeta, así
que deja de ser un color sin origen.

## Regla de uso

| Uso | Tema oscuro | Tema claro |
|---|---|---|
| Texto de marca | 200 a 300 | 700 a 800 |
| Fondo de acento | 800 a 900 | 50 a 100 |
| Bordes | 700 | 200 |
| Foco y estados | 300 | 600 |

Ningún componente elige un color. Elige un token semántico, y el tema decide el valor.

## Tipografía

De la web actual:

- **Playfair Display**, serif de alto contraste, para títulos. Hoy solo con peso 700.
- **Inter**, sans neutra, para cuerpo e interfaz. Hoy solo con pesos 400 y 700.

Dos cosas a resolver:

1. **Faltan pesos intermedios.** Un panel necesita 500 o 600 para botones, etiquetas y
   encabezados de tabla. Con solo 400 y 700 la jerarquía se rompe.
2. **Las fuentes se cargan desde un tercero.** Hay que alojarlas con la aplicación:
   evita una conexión externa y el salto de texto al cargar.

No hay escala de tamaños declarada en ningún sitio. Hay que definirla, y va a Figma
como Text Styles.

## Espaciado, radios y sombras

Lo que existe hoy: `--radius: 0.5rem`, un contenedor con 2rem de relleno y un punto de
ruptura mayor en 1400px. La escala de espaciado es la que trae Tailwind por defecto, es
decir, no es una decisión propia.

Hace falta declarar escala de espaciado, de radios y de sombras. Las sombras merecen
atención: hoy el efecto de marca es un resplandor de color, no una sombra gris, y eso
sí es identidad y conviene conservarlo como token.

## Cómo entra en Figma

1. Una colección de Variables con las cuatro rampas completas, en `color/cian/500` y
   así con todas.
2. Una segunda colección de tokens semánticos con **dos modos**, oscuro y claro, que
   apuntan a la primera. Los componentes solo usan esta.
3. Los nombres semánticos se conservan de la web actual: `primary`, `secondary`,
   `muted`, `accent`, `destructive`, `border`, `input`, `ring`, con sus pares de
   contenido.
4. Text Styles a partir de la escala tipográfica.

## Cómo baja a Angular

Solo custom properties. Sin variables de preprocesador: se resuelven al compilar, no
existen en el navegador y dejarían el cambio de tema fuera de alcance.

```css
:root {
  --color-primary: #018188;
  --color-primary-contenido: #ffffff;
  --radius-md: 0.75rem;
}

[data-theme="dark"] {
  --color-primary: #45eef8;
  --color-primary-contenido: #002d30;
}
```

Un solo sitio por token, y el tema cambia en caliente.
