# Book diagrams on Swarma surfaces

Book figures are artifacts with their own fixed visual language: a white ground, eight role colours,
2 px role frames with pale fills, a dashed container for a trust boundary, PT Sans and PT Mono
(`diagram-style:9`, `:17-28`, `:32`, `:40`; source notation as in
[swarma-identity.md](swarma-identity.md)). The diagram guide states that every figure keeps its white
ground on a dark page and that the diagrams have no dark theme (`diagram-style:11`). This reference
says how such a figure sits on a page in every theme.

Whether a product may publish book figures at all is a product decision recorded in its design
contract. These rules apply wherever figures are shown.

## Rules

1. **Unchanged artwork.** Embed the book's SVG as published, as an `<img>` (not inline SVG): no
   recolouring, filtering, inverting, cropping, redrawing or CSS overrides of its fills and strokes.
   A figure that does not read well is reported to the book, not adjusted on the page.
2. **White ground in every theme.** The figure sits on `--color-figure-ground` (`#FFFFFF`) in light,
   dark and more-contrast appearances. This is the one pure-white surface in the system, and it is
   allowed because it is part of the artifact, like the operator's knockout white.
3. **Frame and padding.** Place the figure in a block with `--space-4` padding on the white ground,
   a 1 px `--color-figure-frame` border and `--radius-surface` corners. In dark appearances the
   frame separates the white block from the page; the block takes no shadow and no glow.
4. **Stable size.** Declare `width` and `height` (or `aspect-ratio`) from the SVG view box before it
   loads; scale with `max-width: 100%` and `height: auto`. On narrow screens a wide figure scales
   down; when its smallest text would fall below the book's own minimum of 7 pt (about 9.3 CSS px;
   `diagram-style:85`), put it in a labelled horizontal scroll region rather than shrinking it
   further.
5. **Caption.** Every figure has a `figcaption` outside the white block, on the page ground, in PT
   Sans compact interface size, `--color-text-muted`. It carries the book's caption for the figure
   verbatim and the source line the product defines (book, version, chapter, figure).
6. **Text alternative.** The image has `alt` equal to the book's caption; in the book the figure's
   description equals its caption (`diagram-style:108`), and the SVG carries it in its `<title>`.
   The section text around the figure describes what the figure shows, so the page is complete
   without it. For a complex figure, add a short description list or table next to it rather than a
   long `alt`.
7. **Not interactive.** Figures are not links, buttons or zoom widgets by default. If a product adds
   "open full size", it is a native link to the SVG with a visible label.
8. **Forced colours.** In forced-colours mode the white ground maps to `Canvas` and the frame to
   `CanvasText`; the SVG keeps its colours because browsers do not apply forced colours to images.
   Check that the figure remains legible and that the caption carries its meaning.
9. **Print.** On print the figure prints as in the book; the frame may drop.

## Interface elements next to a figure

When a page marks an element of a figure in text (for example, "the keyholder" beside a figure in
which the keyholder is a `key` box), it may use the role layer from
[color-and-themes.md](color-and-themes.md) with the same role. A legend outside the figure uses the
role tokens; the figure's own colours stay as drawn.

## Checks

- The SVG served equals the book's SVG byte for byte.
- The white block, frame and caption render in light, dark, light more contrast, dark more contrast
  and forced colours.
- No layout shift on load at 390, 768, 1440 and 1920 px.
- The caption text equals the book caption; the image `alt` equals the caption.
- The surrounding section is complete with the figure removed.
