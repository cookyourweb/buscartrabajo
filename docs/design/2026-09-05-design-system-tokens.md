# Design system tokens: a measured starting point

Date: 2026-09-05
Origin: `~/cookyourweb/cookyourwebai`
Status: proposal ready to take to Figma as Variables

Note on names: the color keys in `tokens-color.json` and in the code keep their
Spanish identifiers (`cian`, `magenta`, `violeta`, `verde`). In this document they
are called cyan, magenta, violet and green.

## Where each thing comes from

**Taken** from the current website: the four brand colors, the typeface pairing and
the names of the semantic tokens, which are well chosen.

**Not taken**: the template's factory gray values, the hexadecimal values repeated by
hand and `#BB60D1`, which is not declared in any palette.

## The finding: it is a dark-background brand

Measured contrast of the colors as they are today. The WCAG AA minimum for normal text
is 4.5:1, and 3:1 for large text.

| Color | Hex | On white | On `#0a0a0a` |
|---|---|---|---|
| cyan | `#32e2ec` | **1.59:1**, not usable for text | 12.47:1 |
| green | `#3fec71` | **1.56:1**, not usable for text | 12.68:1 |
| magenta | `#ec32c7` | 3.59:1, large text only | 5.51:1 |
| violet | `#8f32ec` | 5.48:1 | 3.62:1, large text only |

Three of the four colors are unusable for text on white, and the same three give more
than 5:1 on black. Cyan and green reach 12.5:1, which is excellent.

**Decision that follows: the dark theme is the primary one.** It is not an aesthetic
preference. It is where the brand is already designed for and where it works.

The light theme exists all the same, and uses the deep steps of each ramp.

## Scales

Generated in OKLCh, which is perceptually uniform: the steps look regular, which does
not happen when interpolating in HSL. Chroma is reduced automatically when a step
falls outside the representable color space.

The values are also in `tokens-color.json`, ready to import.

### cyan (`cian`)
```
50 #dafdff   100 #a2f9ff   200 #45eef8   300 #0ad3dd   400 #06b7c0
500 #039ca4  600 #018188   700 #01656a   800 #00494d   900 #002d30
```

### magenta
```
50 #fff0fa   100 #ffdcf3   200 #ffbceb   300 #ff8ce0   400 #ff48d8
500 #e224be  600 #c001a1   700 #97007e   800 #70015c   900 #47003a
```

### violet (`violeta`)
```
50 #f7f3ff   100 #ece2ff   200 #dccaff   300 #c8a7ff   400 #b583ff
500 #a457ff  600 #8e30eb   700 #7301c7   800 #540194   900 #34005f
```

### green (`verde`)
```
50 #dfffe3   100 #adffb9   200 #51f97e   300 #28de64   400 #01c251
500 #00a544  600 #038937   700 #006b29   800 #004e1c   900 #00300f
```

In all four ramps, **steps 600 to 900 pass AA on white**. Steps 50 to 500 are for dark
backgrounds, for soft backgrounds or for elements that are not text.

The original neons do not disappear: they live around step 200 and are the ones that
glow on dark. And the orphan `#BB60D1` is covered by the violet ramp, so it stops
being a color with no origin.

## Usage rule

| Use | Dark theme | Light theme |
|---|---|---|
| Brand text | 200 to 300 | 700 to 800 |
| Accent background | 800 to 900 | 50 to 100 |
| Borders | 600 | 600 |
| Focus and states | 300 | 600 |

No component picks a color. It picks a semantic token, and the theme decides the
value.

### Correction of 6 September: borders

The borders row used to say "700 in dark, 200 in light". **That was wrong**, and it
was not noticed until a test was written that calculated the contrast of the tokens
already in place.

WCAG 1.4.11 requires 3:1 for elements that are not text but are needed to identify a
control: a field's border, the focus ring. A border that cannot be told apart from the
background leaves keyboard navigation blind.

Actual contrast of the cyan ramp against the two backgrounds:

| step | on `#0a0a0a` | on white |
|---|---|---|
| 200 `#45eef8` | 13.99:1 | **1.42:1** |
| 300 `#0ad3dd` | 10.72:1 | **1.85:1** |
| 400 `#06b7c0` | 8.05:1 | **2.46:1** |
| 500 `#039ca4` | 5.94:1 | 3.34:1 |
| **600 `#018188`** | **4.24:1** | **4.67:1** |
| 700 `#01656a` | **2.90:1** | 6.84:1 |

Both values proposed by the original rule fail: 700 gives 2.90:1 on dark and 200 gives
1.42:1 on white. **Step 600 is the only one that works for both themes**, and it is
also the one `primary` already uses in light, so the border and the main color share a
value instead of contradicting each other.

That a token document with measured data had a wrong row is exactly the argument for
having the test: the eye would never have caught it.

## Typography

From the current website:

- **Playfair Display**, a high-contrast serif, for headings. Today only at weight 700.
- **Inter**, a neutral sans, for body and interface. Today only at weights 400 and 700.

Two things to resolve:

1. **Intermediate weights are missing.** A panel needs 500 or 600 for buttons, labels
   and table headers. With only 400 and 700 the hierarchy breaks.
2. **The fonts are loaded from a third party.** They have to be hosted with the
   application: it avoids an external connection and the text jump on load.

There is no size scale declared anywhere. One has to be defined, and it goes to Figma
as Text Styles.

## Spacing, radii and shadows

What exists today: `--radius: 0.5rem`, a container with 2rem of padding and a larger
breakpoint at 1400px. The spacing scale is the one Tailwind brings by default, that is,
it is not a decision of our own.

A spacing scale, a radius scale and a shadow scale need to be declared. Shadows deserve
attention: today the brand effect is a colored glow, not a gray shadow, and that is
identity and should be kept as a token.

## How it enters Figma

1. A Variables collection with the four complete ramps, as `color/cian/500` and so on
   for all of them.
2. A second collection of semantic tokens with **two modes**, dark and light, that
   point to the first. Components use only this one.
3. The semantic names are kept from the current website: `primary`, `secondary`,
   `muted`, `accent`, `destructive`, `border`, `input`, `ring`, with their content
   pairs.
4. Text Styles built from the typographic scale.

## How it comes down to Angular

Custom properties only. No preprocessor variables: they are resolved at compile time,
do not exist in the browser and would leave theme switching out of reach.

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

One place per token, and the theme changes live.
