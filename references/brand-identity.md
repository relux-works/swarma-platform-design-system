# Brand identity: the Swarma mark and the Relux Works operator

A Swarma surface carries two identities. Swarma is the product and always leads. Relux Works is the
operator and appears with its approved artwork, smaller and later on the page. This reference
names the source of the Swarma mark, restates the rules this system needs from its usage guide, and
keeps the operator rules inherited from the Relux Works product web design system.

## Swarma mark: Quorum

The owner approved the Swarma **Quorum** identity: three separate modules around an open triangular
centre, with the upper module in Relux red. The source of truth for the artwork, its exports, its
usage rules and its provenance is the repository
[`relux-works/swarma-brand-assets`](https://github.com/relux-works/swarma-brand-assets/tree/e750345410ccee402acc159e8e1edb8f0687a83d) at commit
`e750345410ccee402acc159e8e1edb8f0687a83d` ("Add approved Swarma Quorum identity and reproducible asset package").
Read its [README](https://github.com/relux-works/swarma-brand-assets/blob/e750345410ccee402acc159e8e1edb8f0687a83d/README.md), [usage guide](https://github.com/relux-works/swarma-brand-assets/blob/e750345410ccee402acc159e8e1edb8f0687a83d/docs/USAGE.md),
[provenance](https://github.com/relux-works/swarma-brand-assets/blob/e750345410ccee402acc159e8e1edb8f0687a83d/docs/PROVENANCE.md) and [validation record](https://github.com/relux-works/swarma-brand-assets/blob/e750345410ccee402acc159e8e1edb8f0687a83d/docs/VALIDATION.md).

This system does not copy the artwork. A product copies the exact files it uses from that commit
into its own public assets and checks them against the checksums in the repository's
[asset manifest](https://github.com/relux-works/swarma-brand-assets/blob/e750345410ccee402acc159e8e1edb8f0687a83d/assets/manifest.json). A new artwork revision is adopted by moving the
pinned commit here, never by editing a copied file. Nobody using this system draws, traces,
regenerates, recolours or approximates the mark.

### Variants

All paths are in the brand-assets repository at the pinned commit. Every SVG is path-only artwork
with outlined lettering, so no font is needed to display it.

| Use | File |
| --- | --- |
| Header and footer, light appearance | `assets/svg/swarma-lockup-horizontal.svg` (red and ink, transparent) |
| Header and footer, dark appearance | `assets/svg/swarma-lockup-horizontal-dark.svg` (red and white, transparent, no plate) |
| Forced colours and other one-colour use | `assets/svg/swarma-lockup-horizontal-mono.svg` (all ink) on a light ground, `assets/svg/swarma-lockup-horizontal-white.svg` (all white) on a dark ground |
| Compact symbol, where space is limited and the name is already clear | `assets/svg/swarma-symbol.svg` and its `-dark`, `-mono` and `-white` variants |
| Centred composition | `assets/svg/swarma-lockup-stacked.svg` and its variants |
| Name without the symbol | `assets/svg/swarma-wordmark.svg`, `assets/svg/swarma-wordmark-white.svg` (outlined, not live text) |
| Platforms that control the background | `assets/png/swarma-avatar-light-*.png`, `assets/png/swarma-avatar-dark-*.png` (plated) |
| Favicons and app icons | `assets/icons/` (see "Favicon, app icons and social images") |

### Rules from the usage guide

These rules restate the [usage guide](https://github.com/relux-works/swarma-brand-assets/blob/e750345410ccee402acc159e8e1edb8f0687a83d/docs/USAGE.md); where they differ, the guide wins.

- **Composition.** The horizontal lockup is the default logo. Use the symbol where space is limited
  and the product name is already clear, the stacked lockup for centred placements, and a plated
  avatar where a platform controls the surrounding background.
- **Integrity.** Keep the three separate modules and the triangular aperture, the upper module red,
  the lower modules and their spacing, and the orientation. Do not crop the aperture, close the
  gaps, rotate a module, stretch a lockup, change letter spacing, recreate the wordmark with live
  text, or add gradients, shadows, strokes, textures or animation.
- **Colours.** Relux red `#F60D10` (upper module), Relux ink `#181A18` (lower modules and wordmark
  on light surfaces), white `#FFFFFF` (lower modules and wordmark on dark surfaces). They are
  identity colours and prescribe no interface text or button colours.
- **Variants, not filters.** Use a supplied variant. Never apply a CSS filter, a fill replacement or
  a theme token to the mark. This also holds in forced colours: the `CanvasText` override that this
  system sanctions for the operator artwork does not apply to the Swarma mark.
- **Plates.** The avatars and the PNG and ICO icons carry their own white or ink plate. Do not add
  another plate or a border.
- **Clear space.** The symbol master has a `120 × 120` view box with visible bounds `10…110`
  horizontally and `14…94` vertically. Keep the canvas and its padding, and reserve at least 12
  more master units around it next to other logos, text or controls: 12 px at a 120 px symbol
  width, scaled proportionally. Lockups use the same 12-unit measure from their 120-unit symbol
  height.
- **Minimum sizes.** Symbol 24 CSS px wide in ordinary interface use (the supplied favicon covers
  16 px); horizontal lockup 160 CSS px; stacked lockup 140 CSS px; wordmark alone 100 CSS px.
- **Direction.** Never mirror the mark in right-to-left interfaces.
- **Relux Works.** Swarma has its own product mark. Keep the approved Relux Works logo separate and
  unchanged when showing operator ownership, and never combine parts of the two marks into a hybrid.

### Slot definition

| Item | Requirement |
| --- | --- |
| Header position | Inline-start zone of the header, before navigation: the horizontal lockup, linked to the locale home |
| Header size | At least 160 CSS px wide. The horizontal lockup has a `0 0 344 120` view box, so at 160 px it is about 55.8 px tall and its 12-unit clear space is about 5.6 px; together about 67 px, inside the 68 px (`--layout-header-height: 4.25rem`) header |
| Footer position | First item of the footer, before the operator lockup: the horizontal lockup at the same minimum |
| Appearance | Light: the default lockup. Dark: the `-dark` lockup. A page that follows the system theme selects with `prefers-color-scheme`; a page with its own theme switch selects from the active site theme |
| Forced colours | The `-mono` lockup when the forced palette has a light ground, the `-white` lockup when it has a dark ground, selected with `(forced-colors: active)` sources ordered before the theme sources. No fill override. Check both a light and a dark forced palette, since the image itself is not recoloured |
| Dimensions | Declare `width` and `height` from the view box so the header does not shift while the file loads |
| Direction | LTR-isolated, never mirrored in RTL layouts |
| Accessible name | The link has the accessible name `Swarma`; name either the link or the image, not both |

### Favicon, app icons and social images

| Asset | Requirement |
| --- | --- |
| SVG favicon | `assets/icons/favicon.svg` for light and `assets/icons/favicon-dark.svg` for dark, with media-qualified icon links |
| `.ico` and Apple touch icon | `assets/icons/favicon.ico` (16, 32 and 48 px frames) and `assets/icons/apple-touch-icon.png` (180 × 180 px) |
| App manifest | `assets/icons/icon-192.png` and `assets/icons/icon-512.png` with `purpose: "any"`, `assets/icons/icon-maskable-512.png` with `purpose: "maskable"`; they carry a white plate |
| Social image (1200 × 630 px) | The approved Swarma lockup plus the page title in PT Sans, inside platform-safe margins, with the operator lockup sized as "Placement and hierarchy" requires; no generated imagery |
| Structured data | `Organization.logo` stays the operator's approved symbol. Where a format declares a product logo for Swarma, it is the Swarma symbol from the pinned commit |

The PNG favicons, the ICO and the app icons are generated in the brand-assets repository; a
product does not regenerate or resize them.

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
| Order | In the footer, the Swarma lockup precedes the operator lockup in DOM order and in reading order |
| Lockup size | The horizontal lockup renders between 160 and 176 CSS px wide (about 35.6 to 39.1 px tall from its `0 0 450 100` view box) at every viewport width. 160 px is the Relux minimum; 168 px is the default |
| Symbol size | The standalone operator symbol, where used (favicon excepted), renders between 16 and 24 CSS px |
| Social image | The operator lockup is 160 px wide (35.6 px tall) in a corner inside the safe margin; the Swarma lockup is at least twice the operator lockup's height, so at least 71.2 px tall |
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
live type. Inter appears on a Swarma surface only inside outlined artwork: the operator's wordmark
and the Swarma wordmark, which the brand-assets provenance record also sets in outlined Inter Bold
700. Live text stays in the PT family.

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

## Release checks

- Every Swarma mark instance is an unchanged file from the pinned brand-assets commit, matching
  its manifest checksum, in the variant for its appearance (light, dark, forced colours in a light
  and a dark palette). No other mark, symbol, placeholder, filter, fill override or live-text
  wordmark appears anywhere.
- The Swarma horizontal lockup is at least 160 CSS px wide with its clear space at 390, 768, 1440
  and 1920 px, and the header height does not change.
- Favicon, Apple touch icon and app icons are the files from `assets/icons/` at the pinned commit.
- Compare every operator artwork instance with the supplied SVG at 100% and at small sizes; confirm
  the horizontal wordmark contains paths and no live `<text>`.
- Confirm SVGs contain no raster images, strokes, gradients, filters, masks, clipping debris,
  embedded accessibility metadata or duplicate IDs.
- Check full-colour light and dark contexts, one-colour and forced-colours variants.
- Check operator symbol rendering at 16, 24 and 32 CSS px.
- Check the measures in "Placement and hierarchy": no operator artwork in the header or above the
  `h1`; footer order Swarma first; operator lockup width 160 to 176 CSS px at 390, 768, 1440 and
  1920 px; social image Swarma lockup at least twice the operator lockup height.
- Check left-to-right and right-to-left pages without mirroring either identity.
