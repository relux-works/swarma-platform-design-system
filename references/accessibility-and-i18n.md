# Accessibility and Internationalization

## Conformance target

Every user-facing product surface targets WCAG 2.2 Level AA. The target covers public
pages, authenticated workflows, errors, empty and loading states, overlays, required
third-party steps, and every supported language. Apply
[wcag-2.2-aa.md](wcag-2.2-aa.md) in addition to this component-level guidance.

Do not state that a product conforms based only on design review, `axe-core`, or a
Lighthouse score. A conformance claim requires the automated and manual release gates
in [quality-assurance.md](quality-assurance.md), with known limitations disclosed.

## Semantic structure

- Use one `main` landmark, a visible or programmatic page heading, and headings that
  follow a meaningful hierarchy.
- Use native links for navigation and native buttons for actions.
- Associate every form control with a persistent label. Placeholder text is not a
  label.
- Use lists, tables, figures, navigation, and dialogs for their actual semantics.
- Add a skip link before repeated navigation.
- Keep source order aligned with visual and keyboard order.

## Keyboard and focus

- Every interactive feature works without a pointer.
- Focus indicators remain visible in light, dark, increased-contrast, and forced-color
  appearances.
- Focus order follows reading and task order.
- Opening an overlay places focus deliberately; closing it restores focus to the
  invoking control.
- Do not trap focus in non-modal content. Contain it inside a modal dialog until the
  dialog closes.
- Minimum target size is 44 by 44 CSS pixels, or equivalent spacing that prevents
  adjacent target errors.
- Hover information is also available on focus and does not contain inaccessible
  interactive content.

## Forms and status

- Describe the expected format before submission when it is not obvious.
- Use correct `type`, `autocomplete`, and `inputmode` values without replacing visible
  labels or validation semantics.
- Validate near the affected field and connect messages with `aria-describedby`.
- Set `aria-invalid` only while a field is invalid.
- Move focus to a concise error summary after a failed multi-field submission, while
  preserving each inline error.
- Announce asynchronous completion, warning, and failure in an appropriate live region.
- Do not announce every keystroke or intermediate loading frame.
- Show the final draft and request explicit consent before an agent invokes a
  side-effecting submission tool.
- Do not ask for information already entered in the same process. Auto-populate it or
  make the prior value selectable unless re-entry is essential, security-sensitive, or
  the old value is no longer valid.
- Let users review, correct, reverse, or explicitly confirm submissions that create a
  legal or financial commitment or modify or delete user-controlled data.

## Appearance preferences

Treat preferences as first-class states:

- `prefers-color-scheme`: independently tuned light and dark appearances.
- `prefers-contrast`: stronger text, boundaries, focus, and control differentiation.
- `prefers-reduced-motion`: static or cross-fade equivalents.
- `prefers-reduced-transparency`: opaque floating surfaces.
- `forced-colors`: system colors, native controls, and visible system focus.

Do not encode state only through hue, opacity, motion, or position.

## Reflow and zoom

- Support 200% text zoom and 400% browser zoom without lost content or two-dimensional
  scrolling, except for genuinely two-dimensional data such as a large table or map.
- Let controls and text wrap when necessary. Increase a container's block size before
  shrinking text.
- Test the longest supported translation and unbroken identifiers.
- Keep sticky content from covering the focused element or anchor destination.
- Do not disable user zoom.

## Images and media

- Write alt text for the purpose of the image in its context, not a visual inventory.
- Use empty alt text for decoration and redundant thumbnails.
- Give the linked Swarma mark the accessible name `Swarma` and the linked operator
  logo the accessible name `Relux Works`. Name either the
  link or the SVG, and hide the other source to avoid duplicate announcements.
- Hide a redundant decorative logo from assistive technology.
- Give charts, diagrams, and complex images a concise alternative plus nearby detailed
  data or explanation.
- Caption audio and video where speech carries meaning; provide a transcript when it
  improves access or discovery.
- Do not autoplay audible media. Provide keyboard-operable pause, stop, mute, volume,
  caption, and transcript paths appropriate to the medium.
- Do not lock content to portrait or landscape unless orientation is essential.
- Prohibit content that flashes more than three times in any one-second period; test
  borderline media against the general and red flash thresholds.

## Language and script

- Set the document `lang` and update it when the locale changes.
- Mark passages in another language with their own `lang`.
- Use script-specific font fallbacks and inspect shaping, line height, punctuation, and
  emphasis in every supported script family.
- Avoid artificial uppercase for scripts without a compatible case system.
- Keep the language selector's labels in their native language and expose the selected
  locale with `aria-current` or a native selection state.
- Format dates, numbers, currencies, plural forms, and names with locale-aware APIs.

## RTL architecture

Build one logical component tree for both directions:

```css
.component {
  margin-inline: auto;
  padding-inline: var(--layout-gutter);
  border-inline-start: 1px solid var(--color-border);
}

[dir="rtl"] .directional-icon {
  transform: scaleX(-1);
}
```

- Prefer logical properties: `inline-start`, `inline-end`, `block-start`, and
  `block-end`.
- Mirror directional navigation and progression icons. Do not mirror logos, media
  controls with universal symbols, product screenshots, or text inside images.
- Open drawers from logical end and maintain a reading-order DOM.
- Isolate URLs, code, email addresses, version strings, currency codes, and mixed LTR
  identifiers with `bdi`, `dir="ltr"`, or `unicode-bidi: isolate`.
- Isolate the Swarma mark and the Relux Works mark as LTR artwork. In forced colors, the
  Relux Works mark uses its bundled one-color asset with the sanctioned `CanvasText`
  path-fill override; the Swarma mark uses its supplied mono or white variant and no fill
  override ([brand-identity.md](brand-identity.md)). Do not use CSS mirroring or create an
  unapproved normal-theme variant.
- Do not assume one RTL locale validates all others. Inspect Arabic, Persian, and
  Hebrew independently because fonts, word lengths, punctuation, and digits differ.

## Swarma additions

- Role colours and status colours never carry meaning alone: the element's name or the status word
  is always in text (see [color-and-themes.md](color-and-themes.md)).
- A trust boundary's meaning is in its text label; the dash only repeats it.
- Book figures have `alt` equal to the book's caption and are surrounded by text that describes what
  they show (see [diagrams.md](diagrams.md)).
- Russian strings follow the book's style guide; check that screen readers read plain double quotes
  and the letter ё correctly in the target voices.

## Accessibility review checklist

- Page landmarks and heading order are meaningful.
- The complete flow works by keyboard and visible focus never disappears.
- Menus, dialogs, forms, errors, loading, and completion expose correct semantics.
- Text, controls, focus, and meaningful graphics meet their contrast targets.
- Light, dark, increased contrast, reduced motion, reduced transparency, and forced
  colors retain the same task and information.
- Zoom, reflow, long translations, and browser font-size changes do not overlap or
  clip content.
- Media alternatives describe the same useful information.
- The corporate mark has one useful name, uses the correct light or dark artwork, and
  never mirrors in RTL.
- Each script and each RTL locale has been visually inspected.
