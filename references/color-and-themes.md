# Color and Themes

## Contents

1. [Semantic model](#semantic-model)
2. [Swarma palette](#swarma-palette)
3. [Role layer](#role-layer)
4. [Status layer](#status-layer)
5. [Operator identity colors](#operator-identity-colors)
6. [Theme requirements](#theme-requirements)
7. [Contrast targets and evidence](#contrast-targets-and-evidence)
8. [Dark mode](#dark-mode)
9. [Materials and gradients](#materials-and-gradients)
10. [Implementation rules](#implementation-rules)

Source notation (`diagram-style:17`, `theme:78`, `book.lua:12`) is defined in
[swarma-identity.md](swarma-identity.md).

## Semantic model

Components consume semantic roles, never palette names. The token contract in `assets/tokens.css`
keeps every role of the Relux Works system and adds two Swarma layers:

- Canvas and surfaces: `--color-bg`, `--color-surface`, `--color-surface-raised`,
  `--color-surface-subtle`, `--color-surface-hover`.
- Text: `--color-text`, `--color-text-muted`, `--color-text-faint`, `--color-text-inverse`.
- Structure: `--color-border`, `--color-border-strong`, `--color-divider`.
- Controls: `--color-control*`, `--color-strong-action*`, `--color-focus`.
- Accent and links: `--color-accent*`, `--color-on-accent`, `--color-link`, `--color-link-hover`.
- Feedback: `--color-success`, `--color-warning`, `--color-error`, `--color-info`.
- Overlays: selection, scrim, material and shadow.
- **Swarma role layer:** `--color-role-<role>-stroke`, `-fill` and `-text` for the eight diagram
  roles (human, agent, service, store, key, external, alert, neutral).
- **Swarma status layer:** `--color-status-<status>-bg` and `-text` for the book's five status
  words.
- **Figures:** `--color-figure-ground` (fixed white) and `--color-figure-frame`.
- Fixed operator identity: `--color-brand-red`, `--color-brand-ink`, `--color-brand-white`.

A semantic role keeps its meaning when its value changes. The role and status layers never replace
feedback roles: an `alert` element in a mechanism is not a form error, and a status badge is not a
success message.

## Swarma palette

The palette comes from the book (see [swarma-identity.md](swarma-identity.md), "Colour"): one deep
blue accent and cool blue-grey neutrals. Light values are the book's own where they meet the
contrast targets; dark and more-contrast values are derived from the same hues.

| Role | Light | Dark | Light, more contrast | Dark, more contrast | Light source |
| --- | --- | --- | --- | --- | --- |
| `--color-bg` | `#f5f7fa` | `#0f1318` | `#f5f7fa` | `#0b0e12` | book quotation ground |
| `--color-surface-subtle` | `#eef1f5` | `#151a20` | `#ebeef3` | `#12161b` | book table header |
| `--color-surface` | `#fafbfc` | `#1a2027` | `#fafbfc` | `#171c22` | derived, not pure white |
| `--color-text` | `#1d2126` | `#e5e8ec` | `#0f1216` | `#f2f4f6` | book ink |
| `--color-text-muted` | `#374151` | `#bcc3cc` | `#2a3038` | `#d3d8de` | book secondary text |
| `--color-text-faint` | `#5f6670` | `#9aa3ae` | `#3c434d` | `#bcc3cc` | diagram label grey |
| `--color-border` | `#d5d9df` | `#313943` | `#6f7884` | `#66707c` | book rule |
| `--color-accent` | `#23466e` | `#8db4e6` | `#1c3a5e` | `#b3cdf0` | book accent |
| `--color-link` | `#23466e` | `#a7c5ee` | `#1c3a5e` | `#c0d6f3` | book links |
| `--color-focus` | `#23466e` | `#a7c5ee` | `#1c3a5e` | `#c0d6f3` | book accent |
| `--color-error` | `#b0204f` | `#f59ab7` | `#8a1840` | `#f8b5ca` | diagram `alert` label |

`--color-success`, `--color-warning` and `--color-info` keep the inherited Relux values: they are
functional, and the book has no feedback colours of its own. The full set, including hover,
pressed, soft, control and overlay values, is in `assets/tokens.css`.

Control foregrounds are paired by state. Pressed controls use `--color-control-text-pressed`
on `--color-control-pressed`; default and hover keep `--color-control-text`.

| Pair | Light foreground / background | Dark foreground / background | Light, more contrast | Dark, more contrast | Forced colors |
| --- | --- | --- | --- | --- | --- |
| `--color-control-text` / `--color-control` | `#1d2126` / `#fafbfc` | `#e5e8ec` / `#1a2027` | `#0f1216` / `#fafbfc` | `#f2f4f6` / `#171c22` | `ButtonText` / `ButtonFace` |
| `--color-control-text` / `--color-control-hover` | `#1d2126` / `#eef1f5` | `#e5e8ec` / `#222931` | `#0f1216` / `#e3e8ee` | `#f2f4f6` / `#222931` | `ButtonText` / `ButtonFace` |
| `--color-control-text-pressed` / `--color-control-pressed` | `#1d2126` / `#e8ecf1` | `#e5e8ec` / `#151a20` | `#0f1216` / `#ebeef3` | `#f2f4f6` / `#12161b` | `HighlightText` / `Highlight` |

The pressed foreground reuses the existing text value in the four palettes. Its separate
semantic role preserves the system's selected-state pairing under forced colors.

Two recorded consequences:

- Links have less than 3:1 against body text in every appearance, so links in prose are always
  underlined; colour is an extra cue.
- The accent and `--color-info` are both blues and close in luminance (see the "info" lines in
  [contrast-report.md](contrast-report.md)). `--color-info` always carries a text label, so the two
  are never told apart by colour alone.

## Role layer

The eight roles carry the meanings the book's diagrams give them (`diagram-style:17-28`):

| Role | Meaning in the book | Light stroke | Light fill | Light text |
| --- | --- | --- | --- | --- |
| `human` | a person: operator, owner, donor | `#747c87` | `#f1f2f4` | `#5f6670` |
| `agent` | an agent or its key | `#7c4ddb` | `#f3effd` | `#6a3fc8` |
| `service` | a platform program | `#2f6fdb` | `#ebf2ff` | `#2a62c4` |
| `store` | a store, registry or journal | `#11826d` | `#e7f5f1` | `#0e6f5d` |
| `key` | a key, root of trust or key-holding program | `#a8740a` | `#fff8e1` | `#8f6208` |
| `external` | a system outside the owner's control | `#d0650e` | `#fff2e6` | `#a04c09` |
| `alert` | refusal, revocation, alarm, physical action on a device | `#c8285f` | `#fdeef3` | `#b0204f` |
| `neutral` | an auxiliary element without a role | `#747c87` | `#f6f7f9` | `#5f6670` |

Light values equal the diagram theme except four, changed for interface contrast: the human and
neutral strokes (`#8b929c` in the diagrams, below 3:1 against their fills), the external stroke
(`#d9690f` in the diagrams, 2.96:1 on the hover surface) and the external text (`#b9580b` in the
diagrams, 4.28:1 on its fill). Dark and more-contrast values are new. The contrast check measures
every role text and stroke against its fill and against every page surface, hover surfaces
included, so a role marker may appear on any surface of the system.

Rules:

- Use a role colour only on an element that has that role in the mechanism the page describes: a
  labelled box, a legend swatch, a marker beside a named component.
- Name the element in text; the colour repeats the role and never replaces it.
- Do not use role colours for actions, links, focus, navigation, feedback or decoration.
- `-text` is for the element's label, `-stroke` for its 2 px frame, `-fill` for its ground.
- Inside a book figure the figure's own colours apply; the role tokens are for interface elements
  next to it.

## Status layer

The book renders its five status words as coloured badges that always contain the word
(`book.lua:11-17`, `book/style.css:266-270`):

| Token | Status word | Light ground | Light text |
| --- | --- | --- | --- |
| `--color-status-now-*` | работает сегодня | `#dcefdd` | `#1f5a2b` |
| `--color-status-decided-*` | решено | `#dfe8f5` | `#1e3f6b` |
| `--color-status-proposed-*` | предложено | `#fbead0` | `#7a4a04` |
| `--color-status-spec-*` | спецификация | `#ebe3f5` | `#4b2a75` |
| `--color-status-open-*` | открыто | `#f5dddd` | `#7c1f1f` |

Rules:

- A status badge always shows the status word itself. Colour repeats the word and is never the only
  signal.
- Only these five words get a status colour, and only when a cell is exactly one of them. Any other
  status text renders in neutral text without a badge colour.
- A status appears only where its source states it; the badge never raises or summarises a status.
- A product may choose to render status without colour (for example, when its design contract says
  so). The tokens exist so that, where colour is used, it matches the book.

## Operator identity colors

```css
--color-brand-red: #F60D10;
--color-brand-ink: #181A18;
--color-brand-white: #FFFFFF;
```

These belong to the Relux Works operator artwork and change for no product. They are not Swarma
interface colours: Relux red has 3.93:1 on the Swarma light page ground. Under forced colours all
three map to `CanvasText`.

## Theme requirements

Inherited from Relux. Every Swarma surface supports:

1. Light appearance from `prefers-color-scheme: light`.
2. Dark appearance from `prefers-color-scheme: dark`.
3. Increased contrast in both appearances from `prefers-contrast: more`.
4. Reduced transparency from `prefers-reduced-transparency: reduce` where supported.
5. Forced colours with system colour keywords and visible native focus.

A user-controlled theme switch is optional. When present, `system` is the default and the explicit
choice is persisted without a flash of the wrong appearance.

## Contrast targets and evidence

Inherited targets:

- Body and compact text: at least 4.5:1 against its actual surface.
- Large text: at least 3:1; prefer 4.5:1.
- Focus indicators, input outlines, icons and meaningful component boundaries: at least 3:1.
- Increased-contrast text: 7:1.
- Disabled controls remain legible and are not distinguished by opacity alone.
- Charts and states use labels, patterns or shapes in addition to colour.

Evidence is recomputed from the token file, not copied by hand:

```sh
python3 scripts/check_contrast.py assets/tokens.css
python3 scripts/check_contrast.py assets/tokens.css --report references/contrast-report.md
python3 scripts/check_contrast.py assets/tokens.css --control
```

The first command measures every declared pair with Chromium in all four palettes, with and without
reduced transparency and forced colors, and exits 1 on any failure. The
second also writes [contrast-report.md](contrast-report.md). The third injects a known failing value
in memory and must exit 1; it proves that the check can fail. The script uses computed browser colors and WCAG 2.x relative
luminance and composites translucent tokens over `--color-bg`. It does not replace measuring the
rendered product in a browser, which the QA reference requires.

## Dark mode

Inherited rules apply: dark mode is separately tuned, not an inversion; no pure black or pure
white; the canvas is darker than surfaces; accents gain luminance; shadows soften; imagery, logos,
syntax colours, focus, selection and form controls are checked on their own; `color-scheme: light
dark`.

Swarma specifics:

- The dark neutrals keep the cool blue-grey tint of the light ones.
- Book figures do not take the dark theme. They keep their white ground (`--color-figure-ground`)
  inside a frame; see [diagrams.md](diagrams.md).
- Use the dark operator artwork on dark surfaces; Relux ink must not sit on a dark surface.

## Materials and gradients

Inherited from Relux. Translucency marks a floating layer only; never stack translucent surfaces;
provide an opaque fallback for reduced transparency. No gradient page backgrounds, colour orbs, bokeh,
glow fields or one-hue washes. The book's diagrams have no gradients at all (`diagram-style:9`), so
Swarma uses gradients only inside real data visualisations that encode information.

## Implementation rules

- Literal colours live only in the theme token layer, illustrations and data-series definitions.
- Keep operator tokens and `--color-figure-ground` outside product override boundaries.
- Change a palette only as a complete tested set and rerun `scripts/check_contrast.py`.
- Prefer borders over shadows for operational density, and spacing over either where structure
  suffices.
- Keep browser selection, focus, autofill, validation and visited-link behaviour in the colour
  review.
- Record contrast results with the foreground token, background token, appearance, ratio and tool;
  the generated report does this.
