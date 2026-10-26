# Typography and Content

Swarma uses the PT family the book is set in (see [swarma-identity.md](swarma-identity.md), "Type").
The type roles, the fixed responsive scale, the line measure and the writing standard are inherited
from the Relux Works product web design system; the faces, weights and Russian copy rules are
Swarma's.

## Type roles

| Role | Family | Weights | Use |
| --- | --- | --- | --- |
| Display | PT Sans | 700 | Product statement, page and section headings, the interim wordmark |
| Interface | PT Sans | 400, 700 | Navigation, controls, labels, tables, captions, data |
| Reading | PT Serif | 400, 700, italics | Long-form prose: documentation and editorial body text, lead paragraphs |
| Technical | PT Mono | 400 | Code, identifiers, version strings, chapter references, eyebrows, compact metadata |

The book uses the same split: PT Serif for the body, PT Sans for headings, tables and captions,
PT Mono for code (`book/style.css:1-2`). Short interface text stays in PT Sans; PT Serif is for
reading passages of several sentences.

```css
--font-display: "PT Sans", system-ui, sans-serif;
--font-ui: "PT Sans", system-ui, sans-serif;
--font-reading: "PT Serif", Georgia, serif;
--font-mono: "PT Mono", ui-monospace, SFMono-Regular, Consolas, monospace;
--font-arabic: "Noto Sans Arabic", "PT Sans", sans-serif;
--font-hebrew: "Noto Sans Hebrew", "PT Sans", sans-serif;
--font-armenian: "Noto Sans Armenian", "PT Sans", sans-serif;
--font-georgian: "Noto Sans Georgian", "PT Sans", sans-serif;
```

Apply script-specific fallbacks through `:lang()`. Use `font-synthesis: none`: PT Sans and PT Serif
ship real bold and italic faces, and PT Mono ships only Regular 400, so technical text is never
bold or italic. Where the inherited Relux rules ask for weight 500 or 600, Swarma uses 400 for body
and 700 for emphasis and headings, because the PT faces have no intermediate weights.

## Font files, licence and self-hosting

| Family | Package | Version checked | Weights and styles | Subsets |
| --- | --- | --- | --- | --- |
| PT Sans | `@fontsource/pt-sans` | 5.3.0 | 400, 700; normal and italic | latin, latin-ext, cyrillic, cyrillic-ext |
| PT Serif | `@fontsource/pt-serif` | 5.3.0 | 400, 700; normal and italic | latin, latin-ext, cyrillic, cyrillic-ext |
| PT Mono | `@fontsource/pt-mono` | 5.3.0 | 400; normal only | latin, latin-ext, cyrillic, cyrillic-ext |

- **Licence.** All three packages declare `OFL-1.1` and ship the SIL Open Font License 1.1 text.
  Their copyright lines differ (checked in each package's `LICENSE` and `metadata.json`, version
  5.3.0):

  | Family | Copyright line |
  | --- | --- |
  | PT Sans | Copyright © 2009 ParaType Ltd. |
  | PT Serif | Copyright © 2010 ParaType Ltd. |
  | PT Mono | Copyright © 2010 ParaType Inc., ParaType Ltd. |

  The OFL permits bundling and self-hosting; keep each package's licence text next to its shipped
  font files and do not sell the fonts on their own.
- **Self-hosting.** Install the packages as dependencies with the lockfile and serve the WOFF2 files
  from the product's own origin. No third-party font service: it would add a tracking request to
  every page.
- **Subsets.** Ship latin and cyrillic for the Russian-first and English surfaces; add latin-ext and
  cyrillic-ext only when content needs them. The packages split subsets by `unicode-range`, so
  browsers fetch only what a page uses.
- **Loading.** `font-display: swap`. Preload at most PT Sans 400 and 700 and PT Serif 400 in the
  subsets of the page's language. Reserve layout with stable line heights so the swap does not move
  controls.
- **Cyrillic.** The family was drawn with Cyrillic alongside Latin; check ё, й, ъ and the Russian
  quotation and punctuation set at every size in the scale, and inspect each script family
  independently as the QA reference requires.

Record the exact package versions in the product repository. A later version is acceptable after
the subsets, weights and licence are rechecked.

## Fixed responsive scale

Inherited from Relux without change. Font sizes change at deliberate breakpoints, never continuously
with viewport width.

| Role | Desktop | Mobile | Line height | Face |
| --- | --- | --- | --- | --- |
| Product statement | 4.5rem | 2.75rem | 1.02-1.06 | PT Sans 700 |
| Page heading | 3.5rem | 2.5rem | 1.06-1.10 | PT Sans 700 |
| Section heading | 2.75rem | 2rem | 1.10-1.16 | PT Sans 700 |
| Subsection heading | 1.25rem | 1.125rem | 1.30-1.38 | PT Sans 700 |
| Lead | 1.25rem | 1.125rem | 1.50-1.60 | PT Serif 400 |
| Body | 1rem | 1rem | 1.55-1.65 | PT Serif 400 (reading) or PT Sans 400 (interface) |
| Compact interface | 0.8125rem | 0.8125rem | 1.35-1.45 | PT Sans 400 |
| Technical eyebrow | 0.75rem | 0.75rem | 1.35-1.45 | PT Mono 400 |

PT Mono at 0.75rem is the smallest text in the system. Check it at 200% text zoom and in Cyrillic.

## Spacing and line measure

Inherited from Relux:

- Keep `letter-spacing: 0` on every role. The book tracks its printed brand line and uppercase
  legend labels (`book/style.css:104`, `:145`); on screen the family rule wins. Tracked uppercase
  stays inside book figures.
- Set reading content to at most `45rem`, roughly 55-75 characters per line.
- Left-align web text. The book justifies and hyphenates for print (`book/style.css:74`, `:85`);
  on screen justification opens uneven gaps at narrow widths.
- Use `text-wrap: balance` for headings where it does not cause unstable reflow, and
  `text-wrap: pretty` for prose as progressive enhancement.
- Use `overflow-wrap: anywhere` for URLs and identifiers, not for ordinary words.
- Scale text-related spacing in `rem`.

## Hierarchy

Inherited from Relux, with the PT weights:

- Product statement: PT Sans 700, one concrete idea, normally no more than three lines on desktop.
- Section heading: PT Sans 700, aligned to the section grid.
- Body and lead: weight 400, neutral text token, comfortable measure.
- Technical label: PT Mono 400, short; uppercase only where the script supports it naturally.
- Interface label: sentence case, specific to the action or destination.

Build hierarchy with size, weight, line height, position and whitespace. Do not solve it with more
colour or uppercase. Do not repeat the same statement in the eyebrow, heading, paragraph and button.

## Writing standard

Inherited from Relux. Write as an engineer explaining a product to another capable person: what it
does, for whom, under which constraints and what happens next. Prefer observable nouns and verbs.
Attach quantities to a date, method or scope. Replace generic AI language with the actual agent,
model, harness, approval or failure mode. No ornamental antithesis, no feature narration in the
interface, concrete calls to action.

Swarma adds two rules from the book:

- **Design and state stay apart.** The book describes the platform by its design, in the present
  tense, and keeps the state of every part in one chapter, "Где мы и что дальше" (book
  `book/ru/00-dlya-kogo.md`, section "Дизайн и готовность"). A Swarma surface states the state of a
  part only where that chapter does, in its words.
- **Limits beside guarantees.** The book names the limits of each guarantee next to it (book
  `book/ru/00-dlya-kogo.md`, section "Читатель"). A Swarma page does the same.

## Russian copy

Every Russian string on a Swarma surface follows the book's Russian style guide
(`editorial/style.ru.md` in the book sources). It replaces the inherited Relux advice on Russian
copy:

- No guillemets. Plain double quotes only for real quotations, chapter titles and conditional
  readings; identifiers, commands and file names in backticks.
- No dash, long or short, as a connector. Use a comma, colon, parentheses or a new sentence. A
  hyphen in compound words and in numeric ranges stays.
- The letter ё wherever it belongs.
- No antithesis of the "это не X, а Y" kind, no empty openers, no promotional adjectives about the
  platform, no closing paragraph that restates the section.
- English technical terms stay unquoted only when they match a code identifier or the Russian term
  loses precision; otherwise use the Russian term.
- Product names are written exactly as the book names them.

Check case, agreement, punctuation and natural word order after localisation.

## Claims and evidence

Inherited from Relux: every important claim maps to at least one inspectable item (live state,
documented interface, dated measurement, concrete control, repository or release). For Swarma, the
book and the papers are the primary evidence, cited by chapter and section. Do not fill a missing
proof with decorative statistics.
