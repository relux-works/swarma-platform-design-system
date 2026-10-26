# Layout and Components

## Contents

1. [Shared geometry](#shared-geometry)
2. [Identity in the page chrome](#identity-in-the-page-chrome)
3. [Header](#header)
4. [First viewport](#first-viewport)
5. [Sections and repeated rows](#sections-and-repeated-rows)
6. [Cards and surfaces](#cards-and-surfaces)
7. [Controls](#controls)
8. [Swarma components](#swarma-components)
9. [Product media and data](#product-media-and-data)
10. [Responsive behavior](#responsive-behavior)
11. [Footer](#footer)

Everything in this reference is inherited from the Relux Works product web design system unless it
is marked as a Swarma change.

## Shared geometry

Inherited without change:

```css
--layout-max: 73.75rem;      /* 1180px */
--layout-reading: 45rem;     /* 720px */
--layout-header-height: 4.25rem;
--layout-gutter: 1.5rem;
--layout-section: 6rem;
--layout-section-mobile: 4rem;
--radius-control: 0.25rem;
--radius-surface: 0.5rem;
```

- Centre the main container with equal logical inline gutters.
- Use the spacing scale rather than local arbitrary gaps.
- Set `min-width: 0` on grid and flex children that may contain text.
- Define grids with `minmax(0, 1fr)` so content cannot silently expand a track.
- Use `scrollbar-gutter: stable` where page width changes would move a centred header or dialog.
- Never use `overflow-x: hidden` to conceal a broken grid.

**Swarma change: no larger radii.** The book's diagrams round their boxes at 12 px and trust-boundary
containers at 16 px (`theme:25`, `:32`; notation as in [swarma-identity.md](swarma-identity.md)).
Those radii stay inside the figures. Interface elements keep the family limit of 8 px, including the
Swarma components below.

## Identity in the page chrome

**Swarma change.** Swarma owns the header; Relux Works appears in the footer as the operator. The
Swarma mark slot is empty until the owner supplies artwork, and the text wordmark "Swarma" stands in
for it. Placement, sizes and the operator artwork rules are in [brand-identity.md](brand-identity.md).

## Header

Inherited three-zone header: brand at the inline start, navigation on the page axis, locale and
primary action at the inline end.

```css
.site-header__inner {
  min-height: var(--layout-header-height);
  display: grid;
  grid-template-columns: minmax(0, 13.75rem) minmax(0, 1fr) minmax(0, 13.75rem);
  align-items: center;
  gap: 1rem;
}

.site-header__nav { justify-self: center; }
.site-header__actions { justify-self: end; }
```

- **Swarma change:** the brand zone holds the Swarma wordmark (later the approved mark), not the
  Relux lockup.
- Keep the header height stable across routes, locales and active states.
- Use a translucent material only when content scrolls under the header; otherwise a solid surface.
- At about 1100 px, or when translated labels no longer fit, replace desktop navigation with one
  menu control. Do not compress labels until they collide.
- The mobile panel opens from the logical inline end, which mirrors in RTL.
- Preserve focus, return focus to the trigger, close on `Escape` and outside press, and lock
  background scrolling while the modal drawer is open.
- Use `aria-current="page"` without changing the link's dimensions.

## First viewport

Inherited. Match composition to the archetype (see [foundations.md](foundations.md)): documentation
shows navigation, version context and content immediately; editorial pages show the reading path;
service pages show positioning and actions first. Do not force the first viewport to fill the
screen, and keep the next section visible.

## Sections and repeated rows

Inherited. Build sections as full-width bands with a constrained inner grid.

```css
.section-heading {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(16rem, 0.75fr);
  gap: 3rem;
  align-items: end;
}

.structured-row {
  display: grid;
  grid-template-columns: 3rem minmax(13rem, 0.8fr) minmax(0, 1.6fr) 15rem;
  gap: 2rem;
  align-items: start;
}
```

Stack the heading grid at the content breakpoint. Change the complete row grid at a breakpoint
rather than letting individual rows wrap differently.

## Cards and surfaces

Inherited:

- Use cards for repeated independent objects, framed tools, dialogs and media that needs a stable
  boundary. Do not wrap a whole section in a card, and never nest cards.
- Default surface radius is 8 px or less. Pills are for binary state, compact filters or genuinely
  circular identity.
- Prefer a border, surface step or whitespace over a large shadow.
- Keep padding consistent for cards of one type; state changes must not change outer dimensions.

## Controls

Inherited:

- Familiar icons for icon actions, segmented controls for modes, switches or checkboxes for binary
  settings, menus for bounded option sets.
- Text, or icon plus text, for clear commands.
- Touch targets at least 44 px in each dimension.
- An accessible name for every icon-only control and a tooltip for unfamiliar symbols.
- Visible focus independent of hover; never remove native outlines without a tested replacement.
- Confirmation dialogs only for destructive, irreversible actions; prefer undo for reversible ones.
- **Swarma addition:** a consequential action shows the exact content it will submit before the
  person confirms it (see [swarma-identity.md](swarma-identity.md), "Exact versions and exact
  content").
- Validate near the affected field and preserve the layout when feedback appears.

## Swarma components

Each component below exists because the book uses the same element with the same meaning. None of
them is decoration.

### Trust boundary

The visual sign of a trust boundary: a machine, an OS account, a process or an owner's domain
(`diagram-style:40`).

- A container with a dashed `var(--boundary-width)` border, `border-style: dashed`, in the
  `--color-role-<role>-stroke` of the role that controls the zone, and `--radius-surface` corners.
  Browsers do not take a custom dash pattern for CSS borders; where the exact `8 6` dash
  (`--boundary-dash`) matters, draw the frame as an SVG rectangle with `stroke-dasharray`.
- A label at the inline-start top in PT Sans compact interface size, sentence case,
  `letter-spacing: 0`, naming the zone in text.
- Content inside is the content that lives within the boundary; content that crosses it is shown
  crossing it.
- Never used as a card, a divider, a quotation, a callout or for visual grouping. At most two
  levels of nesting, as in the diagrams (`diagram-style:42`).
- Forced colours: the border becomes `CanvasText` and stays dashed.

### Role marker

A small marker that tells the reader an element plays a role from the diagrams: a 2 px frame in
`--color-role-<role>-stroke` on `--color-role-<role>-fill`, the element's name in
`--color-role-<role>-text`, `--radius-control` corners. The name is always in text. Used in legends,
in component lists next to a figure, and in tables that classify elements by role. Not used as a
button, tag filter or decoration.

### Status badge

The book's status badge (`book/style.css:257-270`): the status word in PT Sans 700 compact size on
`--color-status-<status>-bg` in `--color-status-<status>-text`, `--radius-control` corners, no wrap.
It renders only one of the five status words, only from status data, and never as the only signal.
A table cell whose status is not exactly one of the five words renders its text in neutral text
without a badge. A product that renders status without colour uses the same component in neutral
tokens.

### Layer order

Where the three layers appear together, list them in one fixed order with their number in PT Mono:
`2` Swarma Runtime, `1` Swarma Protocol, `0` Swarma Chain, as the book numbers them (ch. 02,
line 5). Use ordinary list or table semantics. No stacked-slab illustration, isometric block or icon
represents the layers.

### Book figure

A book diagram on its white ground with frame, caption and source line. The full rules are in
[diagrams.md](diagrams.md).

### Version context

A line in PT Mono that names the exact book or paper version and date a page relies on, close to the
page title. It follows the book's principle that a check refers to an exact version (ch. 03,
"Одобрение относится к точным версиям").

## Product media and data

Inherited:

- Show the real product, object, state or data; avoid generic stock imagery and mock interfaces.
- Declare `width`, `height` or `aspect-ratio` before media loads.
- Keep critical content inside a predictable safe region across crops.
- Keep native table semantics; on narrow screens use a compact representation or a labelled scroll
  region, not clipped columns.
- Charts need text labels and non-colour distinctions, with data date and source nearby.
- Code blocks expose a copy affordance without resizing when the label changes.

For Swarma the primary media are the book's figures (see [diagrams.md](diagrams.md)) and the book's
tables. Swarma has no approved photography or illustration.

## Responsive behavior

Inherited:

| Range | Expected behavior |
| --- | --- |
| Below 640px | Single-column content, mobile navigation, 1.5rem gutters |
| 640-1099px | Compact grids, reduced section spacing, mobile or compact navigation |
| 1100px and above | Three-zone header and full structured rows |

- Reflow instead of hiding essential information.
- Test long words, long localised labels, 200% browser zoom and default font-size changes.
- Use logical margins, padding, borders and inset properties.
- Do not size fonts by viewport width.
- Keep DOM order meaningful; CSS reordering must not change keyboard or screen-reader order.

## Footer

Inherited, with the Swarma operator rule:

- State the product name first, then its relationship to Relux Works with the approved operator
  lockup (see [brand-identity.md](brand-identity.md)).
- Link to documentation, status, privacy, terms, support and source only when they exist.
- Keep legal identity and dates accurate and localised.
- Use the same constrained grid and logical alignment as the page.
- Keep language labels in their native language and expose the current value programmatically.
