# Swarma identity: where each choice comes from

The Swarma Platform Design System takes its identity from the Swarma book: the way the book is
typeset, the way its diagrams are drawn, and the ideas the platform is built on. Each choice below
names its source and says why it is the first association rather than a decorative pick. A choice
that cannot name a source does not belong in this system.

Source notation:

- `book/style.css:8` is a line in the book's print stylesheet.
- `diagram-style:40` is a line in the book's diagram guide (`editorial/diagram-style.ru.md`).
- `theme:34` is a line in the diagram theme (`scripts/diagram-kit/theme.toml`).
- `book.lua:12` is a line in the book's Pandoc filter (`book/filters/book.lua`).
- `style-guide:51` is a line in the book's Russian style guide (`editorial/style.ru.md`).
- "ch. 02, line 5" is a line in a chapter of the Russian book (`book/ru/`).

All paths are relative to the book sources.

## Summary

| Choice | Source | Used as |
| --- | --- | --- |
| PT Sans, PT Serif, PT Mono | `book/style.css:1-2`, `:70`, `:203`, `:275`, `:303`; `diagram-style:32`; `theme:5-8` | the only type family |
| Deep blue accent `#23466e` | `book/style.css:8`; used at `:106`, `:220`, `:226`, `:235`, `:350`, `:355`, `:371` | primary accent and link |
| Cool blue-grey neutrals | `book/style.css:5-9`, `:116`, `:310`, `:351` | page, surface and text neutrals |
| Eight semantic roles | `diagram-style:17-28`; `theme:75-115` | a role colour layer with the diagrams' meanings |
| Status badge colours | `book/style.css:257-270`; `book.lua:11-17` | status tokens, always with the word |
| Dashed rounded container for a trust boundary | `diagram-style:3`, `:40`; `theme:31-34` | boundary component, never generic grouping |
| Three layers numbered 0 to 2 | ch. 02, lines 3-7 | structural order and layer labels |
| No decoration | `diagram-style:9`, `:50` | rejected-pattern list and motion limits |
| White figure ground in every theme | `diagram-style:11`; every SVG in `book/diagrams/` | the diagram bridge |
| Exact version and exact content | ch. 03 "Одобрение относится к точным версиям" (line 47); ch. 03 "Человек подписывает своё действие" (lines 67-71) | version context and confirmation rules |
| Russian copy rules | `style-guide:50-51`, `:90` | rules for every Russian string |

## Type: the PT family

The book sets body text in PT Serif, headings and apparatus in PT Sans and code in PT Mono. The
stylesheet says so in its first comment (`book/style.css:1-2`) and applies it to the document body
(`:70`), headings (`:203`), code (`:275`) and tables (`:303`). The diagrams use the same faces:
names, descriptions and captions in PT Sans, code and identifiers in PT Mono (`diagram-style:32`,
`theme:5-8`). A reader who opens the book, a figure and the site sees one family.

This is the first association because the book uses no other type. The family was drawn with full
Cyrillic, which the Russian-first book and site need. Details, licence and self-hosting are in
[typography-and-content.md](typography-and-content.md).

## Colour: deep blue accent, cool neutrals

The book has one accent, `--accent: #23466e` (`book/style.css:8`). It marks the brand line on the
title page (`:106`), the rule under every chapter title (`:220`), chapter and section numbers
(`:226`, `:235`), the quotation bar (`:350`), links (`:355`) and part titles (`:371`). Nothing else
in the book is coloured that way, so it is the platform's colour by use, not by choice. The system
keeps it as the light-theme accent and link colour and derives the dark and more-contrast values
from the same hue (see [color-and-themes.md](color-and-themes.md)).

The book's neutrals are cool blue-greys: ink `#1d2126`, muted `#6b7280`, rule `#d5d9df`, code
ground `#f4f5f7` (`:5-9`), secondary text `#374151` (`:116`), table header `#eef1f5` (`:310`) and
quotation ground `#f5f7fa` (`:351`). The system's light neutrals take these values directly where
they meet the contrast targets: page `#f5f7fa`, subtle surface `#eef1f5`, text `#1d2126`, muted text
`#374151`, border `#d5d9df`. The book's muted grey `#6b7280` falls below 4.5:1 on `#eef1f5`, so
faint text uses the diagrams' label grey `#5f6670` (`theme:80`) instead.

## Semantic roles from the diagrams

Every book diagram gives each element exactly one role, and the colour says the role: human, agent,
service, store, key, external, alert, neutral (`diagram-style:15-26`). The guide states the purpose
in its opening line: the reader recognises a person, an agent, a key or an external system by
colour, and a trust boundary by its dash, on any page (`diagram-style:3`). The site inherits that
promise. When a page marks an agent, a key or an external system outside a figure, it uses the same
role colour with the same meaning, so text and figures agree.

The role layer is semantic, not decorative:

- A role colour appears only on something that has that role in the mechanism being described.
- A role colour never carries meaning alone: the element is named in text.
- Role colours are not used for buttons, links, focus or feedback states.

The diagram values were drawn for a white figure ground. For interface use on every page surface,
including hover surfaces, four values change and every other light-theme value is the diagram's own
(see [color-and-themes.md](color-and-themes.md), "Role layer"):

| Role value | Diagram | Interface | Reason |
| --- | --- | --- | --- |
| human and neutral stroke | `#8b929c` (`theme:78`, `:113`) | `#747c87` | 2.80:1 and 2.93:1 against their fills, below 3:1 for a boundary |
| external stroke | `#d9690f` (`theme:103`) | `#d0650e` | 2.96:1 on the light hover surface, below 3:1 for a boundary |
| external label | `#b9580b` (`theme:105`) | `#a04c09` | 4.28:1 on its fill, below 4.5:1 for text |

Dark and more-contrast role values are new; the diagrams have no dark theme (`diagram-style:11`).

## Status colours from the book

The book turns each status marker into a coloured badge that always contains the word
(`book.lua:3-6`, `:21-27`). The mapping is fixed: "работает сегодня" is `now`, "решено" is `dec`,
"предложено" is `prop`, "спецификация" is `spec`, "открыто" is `open` (`book.lua:11-17`), with
pale-ground badge colours in `book/style.css:266-270`. The system keeps these as status tokens and
the same rule: the badge text is the status word, and colour only repeats it. An unknown marker is
an error in the book (`book.lua:22-25`); a status component in this system rejects an unknown word
in the same way. Status is shown only where its source states it.

## The trust boundary

The diagrams draw a trust boundary as a dashed rounded container in the colour of the role that
controls the zone (`diagram-style:40`), with a 2 px stroke and an `8 6` dash (`theme:31-34`). The
guide forbids it for mere visual grouping: the container means a machine, an OS account, a process
or an owner's domain (`diagram-style:40`). The book's whole subject is where trust ends: the runtime
draws physical boundaries between agents (ch. 02, line 39), and the principles chapter is a list of
boundaries and their limits (ch. 03, lines 7-79).

The system adopts the dashed container as the one visual sign of a trust boundary in the interface
(`--boundary-width`, `--boundary-dash` in `assets/tokens.css`). It is used only where the content
describes a boundary, with the same role colour for the controlling side, and never as a card,
divider or decorative frame. See [layout-and-components.md](layout-and-components.md).

## Three layers

Swarma has three layers, numbered from the bottom: Swarma Chain is layer 0, Swarma Protocol layer 1,
Swarma Runtime layer 2 (ch. 02, lines 3-5). The book's first figure is that stack (ch. 02, line 7;
`book/diagrams/three-layers.svg`). The system uses the stack as a structural order, not an image:
where the three layers appear together they are listed in one fixed order with their layer number
in the technical face, and pages about a layer carry its number in the page metadata. No stacked-
slab illustration, isometric block or icon stands in for the layers.

## No decoration

The diagrams have no shadows, gradients, icons or volume, few colours, and a fixed meaning for each
colour (`diagram-style:9`). A figure allows one accent signal, and only when the whole figure is
about it (`diagram-style:50`). The system carries that restraint into the interface. It rejects
swarm or bee imagery, particles, node-graph backdrops, glow and gradient fields: none of them
appears in the book, and each would add colour without meaning. Motion follows the same rule: it
shows a state change and stops (see [motion-and-interaction.md](motion-and-interaction.md)).

## Figures keep their white ground

Every book figure carries a white ground and stays the same light rectangle on a dark page or in a
dark reader theme; the diagrams have no second, dark theme (`diagram-style:11`). Each SVG in
`book/diagrams/` starts with a full-size white rectangle. The system therefore never recolours or
inverts a book figure. See [diagrams.md](diagrams.md).

## Exact versions and exact content

Two principles of the book become interface rules.

- "Одобрение относится к точным версиям" (ch. 03, line 47): a check refers to an exact object.
  Pages that rely on the book or a paper name its exact version and date, and status data names the
  book version it came from.
- "Человек подписывает своё действие" (ch. 03, line 67): a signature is placed only over what the
  signing party received in full and checked (ch. 03, line 71). Any consequential action on a Swarma
  surface shows the exact content it will submit before the person confirms it. This agrees with the
  inherited Relux rule on side-effecting actions.

## Russian copy

The book's Russian style guide bans guillemets and the dash used as a connector, allows plain double
quotes only for real quotations, chapter titles and conditional readings, and requires the letter ё
(`style-guide:50-51`, `:90`). Every Russian string in a Swarma surface follows it. See
[typography-and-content.md](typography-and-content.md).

## Rejected candidates

| Candidate | Why it is not part of the identity |
| --- | --- |
| Swarm, hive or bee imagery | Not in the book's figures or typography; the book's style guide excludes apiary names (`style-guide:83`) |
| Particles, node graphs, network backdrops | Decoration standing in for the mechanism; the diagrams show real elements with roles |
| Glow, gradients, glass | Explicitly absent from the diagrams (`diagram-style:9`) |
| Uppercase tracked labels from the print title page | `book/style.css:104` tracks the print brand line by 0.18 em; the family rule keeps `letter-spacing: 0` on screen for multilingual consistency. Tracked uppercase stays inside the diagrams (`theme:36`) |
| Justified, hyphenated body text | A print choice (`book/style.css:74`, `:85`); on screen it produces uneven word spacing at narrow widths, so web text is left-aligned |
| A Swarma logo, symbol or mark | The owner draws the mark; the system leaves a slot and draws nothing (see [brand-identity.md](brand-identity.md)) |
