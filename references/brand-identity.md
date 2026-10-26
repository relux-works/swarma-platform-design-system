# Brand identity: the Swarma mark slot and the Relux Works operator

A Swarma surface carries two identities. Swarma is the product and always leads. Relux Works is the
operator and appears with its approved artwork, smaller and later on the page. This reference
defines the slot for the Swarma mark, the interim text wordmark, and the operator rules inherited
from the Relux Works product web design system.

## Swarma mark: AWAITING OWNER ARTWORK

The owner draws the Swarma mark. Until the owner supplies approved artwork, this slot stays empty.
Nobody using this system draws, traces, generates or approximates a Swarma logo, symbol or mark,
including placeholder geometry, monograms, icons or favicon art.

### Slot definition

| Item | Requirement |
| --- | --- |
| Header position | Inline-start zone of the header, before navigation; links to the locale home |
| Footer position | First item of the footer, before the operator lockup |
| Variants to be supplied | Horizontal lockup and standalone symbol, each for light surfaces, dark surfaces and one colour; an opaque square avatar for platforms that crop |
| Artwork format | Path-only SVG with a fixed view box; no live text, raster images, strokes that change with scale, gradients, filters, masks, embedded fonts or accessibility metadata |
| Clear space | Defined by the owner with the artwork, as a multiple of a named feature of the mark; until then, at least the cap height of the wordmark on every side |
| Minimum size | Defined by the owner per variant; the standalone symbol must stay legible at 16 CSS px |
| Colour | Fixed by the owner with the artwork. The mark must not take the Relux red and must not be recoloured by theme tokens |
| Forced colours | The one-colour variant with a `CanvasText` path-fill override, in the same way as the operator artwork |
| Direction | LTR-isolated, never mirrored in RTL layouts |
| Accessible name | A linked mark has the accessible name `Swarma`; the nested SVG is hidden |

### Favicon and social images

| Asset | Requirement once the mark exists | Interim rule |
| --- | --- | --- |
| SVG favicon | Light and dark standalone symbols with media-qualified icon links | The site may use the operator symbol as described in "Operator favicon" below, or ship no favicon; the choice is recorded in the product's design contract |
| `.ico` 16, 32, 48 px and Apple touch icon 180 × 180 px | Generated from the approved Swarma avatar | Same as the SVG favicon |
| Social image (1200 × 630 px) | Approved Swarma artwork plus the page title in PT Sans, inside platform-safe margins | Page title and the text wordmark "Swarma" in PT Sans on a page-ground background, with the operator lockup sized as "Placement and hierarchy" requires; no generated imagery |
| Structured data | `Organization.logo` stays the operator's approved symbol; a `Brand` or product logo for Swarma is added only with the approved artwork | No Swarma logo is declared |

### Interim text wordmark

Until the mark exists, Swarma is identified by the text wordmark "Swarma":

- set in the display face, PT Sans Bold 700, `letter-spacing: 0`;
- always in Latin script, in every locale;
- in `--color-text` (`CanvasText` in forced colours), never in the accent or a role colour;
- live text, linked to the locale home, with the accessible name `Swarma`;
- no symbol, container, ligature, custom kerning, outline, gradient or animation.

The text wordmark is not a logo and must not be exported as artwork, used as a favicon or placed in
a social image as if it were a mark. When the owner supplies the mark, the mark replaces the
wordmark in the header and footer, and this section is updated.

## Relux Works as operator

Relux Works operates Swarma surfaces. The book's title page carries the brand line "Relux Works ·
Swarma" (book `book/ru/00-dlya-kogo.md`, front matter). The operator relationship is shown with the
approved Relux Works artwork contained in `assets/`, and only that artwork.

### Placement and hierarchy

Swarma leads and the operator follows. The rules below make that measurable; each is checked in
the release checks at the end of this reference.

| Rule | Measure |
| --- | --- |
| Header | No operator artwork in the header, and none above the page's `h1` |
| Footer only | On pages, the operator lockup appears only in the footer |
| Order | In the footer, the Swarma wordmark or mark precedes the operator lockup in DOM order and in reading order |
| Lockup size | The horizontal lockup renders between 160 and 176 CSS px wide (about 35.6 to 39.1 px tall from its `0 0 450 100` view box) at every viewport width. 160 px is the Relux minimum; 168 px is the default |
| Symbol size | The standalone operator symbol, where used (favicon excepted), renders between 16 and 24 CSS px |
| Social image | The operator lockup is 160 px wide (35.6 px tall) in a corner inside the safe margin; the rendered cap height of the wordmark "Swarma", or the height of the Swarma mark, is at least twice the lockup's height, so at least 71.2 px |
| Relationship line | One line next to the footer lockup names the relationship, in PT Sans at compact interface size |

Structured data names Relux Works as the `Organization` with the approved standalone symbol.

### Approved operator artwork

| Use | Light surface | Dark surface |
| --- | --- | --- |
| Horizontal footer lockup | `assets/relux-lockup-horizontal.svg` | `assets/relux-lockup-horizontal-dark.svg` |
| Standalone symbol | `assets/relux-symbol.svg` | `assets/relux-symbol-dark.svg` |
| Square avatar or plated fallback | `assets/relux-avatar-light.svg` | `assets/relux-avatar-dark.svg` |

Use `assets/relux-symbol-one-color.svg` and `assets/relux-lockup-horizontal-one-color.svg` for
one-colour and forced-colours contexts. The system does not bundle stacked or white-knockout
masters; obtain those from the approved Relux Works master-logo package when a delivery requires
them, and do not derive a new variant.

`assets/relux-linkedin-company-cover.jpg` and its SVG source are the Relux Works company page cover.
They are operator assets inherited with the fork and are not used on Swarma surfaces.

Keep each SVG source intact. Do not trace, simplify, redraw, retype or pass the mark through image
generation. The symbol uses a `0 0 100 100` view box and the horizontal lockup a `0 0 450 100` view
box; both use filled paths only. The horizontal wordmark is outlined Inter Bold 700 artwork, not
live type; it is the one place where Inter appears on a Swarma surface, as part of the operator's
artwork.

### Fixed operator values

- Relux red: `#F60D10`
- Relux ink: `#181A18`
- Knockout white: `#FFFFFF`
- Symbol clear space: at least one red-arm thickness, `T`, on every side
- Symbol minimum: 16 CSS px on screen or 10 mm in print
- Horizontal lockup minimum: 160 CSS px on screen or 30 mm in print
- Stacked lockup minimum, when supplied by the production library: 120 CSS px on screen or 25 mm
  in print

In the normalised symbol, `T = 10√2`, about `14.14` view-box units, measured perpendicular to either
45-degree red arm. For the symbol and horizontal lockup, reserve at least `14.14%` of the rendered
100-unit SVG viewport height outside the artwork on every side, measured from the visible artwork
bounds.

These values belong to the operator artwork. Swarma tokens never recolour `--color-brand-*` or an
approved SVG, and Relux red is not a Swarma interface colour. It has 3.93:1 contrast on the
Swarma light page ground and fails 4.5:1 for text.

### Do not

- stretch, crop, rotate, skew, mirror, rearrange or re-space the artwork;
- round its corners or add a container unless using the supplied avatar;
- add gradients, shadows, glows, outlines, textures, depth or motion;
- move, resize or recolour one arrow independently;
- let the Swarma mark replace, merge with or sit inside the Relux Works lockup;
- rebuild the Relux wordmark as HTML text or an SVG `<text>` element.

### Light, dark and constrained colour

On light neutral surfaces use the full-colour asset with red chevron and ink arrow or wordmark. On
dark neutral surfaces use the dark asset with red chevron and white arrow or wordmark. Do not use the
ink artwork on a dark surface.

For forced colours, inline the bundled one-colour asset and apply the only sanctioned runtime fill
override:

```css
@media (forced-colors: active) {
  .relux-logo path { fill: CanvasText; }
}
```

Keep the source SVG unchanged and keep the inline copy hidden when its containing link supplies the
accessible name.

### Accessibility and direction

Give a linked operator logo the accessible name `Relux Works` and hide its nested SVG with
`aria-hidden="true"`. For an `<img>`, set `alt="Relux Works"`. Keep the artwork in left-to-right
drawing order in every locale:

```css
.relux-logo {
  direction: ltr;
  unicode-bidi: isolate;
}
```

### Operator favicon

When a Swarma surface uses the operator symbol as its interim favicon, use the light and dark
standalone symbols as theme-aware SVG favicons, and generate the `.ico` at 16, 32 and 48 px and the
Apple touch icon at 180 × 180 px from `assets/relux-avatar-light.svg`. Record this choice in the
product's design contract; it ends when the Swarma mark exists.

## Release checks

- The Swarma mark slot holds approved owner artwork or the text wordmark; no other mark, symbol or
  placeholder appears anywhere.
- Compare every operator artwork instance with the supplied SVG at 100% and at small sizes; confirm
  the horizontal wordmark contains paths and no live `<text>`.
- Confirm SVGs contain no raster images, strokes, gradients, filters, masks, clipping debris,
  embedded accessibility metadata or duplicate IDs.
- Check full-colour light and dark contexts, one-colour and forced-colours variants.
- Check operator symbol rendering at 16, 24 and 32 CSS px.
- Check the measures in "Placement and hierarchy": no operator artwork in the header or above the
  `h1`; footer order Swarma first; lockup width 160 to 176 CSS px at 390, 768, 1440 and 1920 px;
  social image wordmark at least twice the lockup height.
- Check left-to-right and right-to-left pages without mirroring either identity.
