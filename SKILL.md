---
name: swarma-platform-design-system
description: >
  Design, build, migrate, or review web surfaces of the Swarma platform (the public site,
  documentation, and operator or project web tools) with the Swarma Platform Design System:
  a fork of the Relux Works product web design system whose identity comes from the Swarma
  book. Covers the PT type family, the deep-blue accent and cool neutrals, the eight diagram
  roles and the book's status colours as semantic tokens, the dashed trust-boundary sign,
  book figures on their white ground, the approved Swarma Quorum mark and the Relux Works
  operator lockup, light/dark/high-contrast/forced-colors themes, responsive grids, motion limits,
  WCAG 2.2 AA accessibility, RTL, the book's Russian copy rules, evidence-led content, agent
  discoverability, and visual QA. Russian triggers include дизайн сайта Swarma, дизайн-система
  Swarma, айдентика Swarma, шрифты PT, палитра Swarma, роли диаграмм, граница доверия, тёмная
  тема, вёрстка, сетка, доступность and визуальная проверка.
---

# Swarma Platform Design System

Give every Swarma surface the look of the Swarma book: the same type, the same deep-blue accent,
the same role colours with the same meanings, the same sign for a trust boundary. Keep the
foundations inherited from the Relux Works product web design system: geometry, the type scale,
semantic tokens, complete theme states, accessibility, the QA matrix and factual writing.

Read [swarma-identity.md](references/swarma-identity.md) first. It names the book source of every
identity choice and the candidates the system rejects.

## Start with the repository

- Inspect the stack, existing tokens, components, routes, locales, logo, favicon, social assets,
  metadata, tests and project instructions before proposing visual changes.
- Identify the primary audience and choose a page archetype from
  [foundations.md](references/foundations.md). Swarma's public surfaces are mostly documentation and
  editorial publication.
- Find the product's design contract. It records the decisions this system leaves to the product:
  whether book figures are shown, whether status uses colour, and which Swarma brand-asset files it
  copies from the pinned commit.
- Treat existing user changes as intentional. Do not overwrite unrelated work.

## Establish the design contract

Before implementation, state the contract in working notes or the product repository:

- **Product promise:** the literal job the surface performs.
- **Primary experience:** what must be visible or usable in the first viewport.
- **Swarma invariants:** PT type roles, the Swarma palette and tokens, the role and status layers,
  the trust-boundary sign, theme behaviour, accessibility and factual writing.
- **Identity:** the Swarma Quorum mark from the brand-assets repository at the pinned commit
  (lockup variants, favicons and app icons) and the Relux Works operator placement.
- **Evidence:** the book chapters, papers, figures or real interface states that make the page
  credible, and how the state of each part is sourced.
- **Asset dependencies:** self-hosted PT font packages and subsets, figure sources, Swarma
  brand-asset files with their manifest checksums, operator artwork variants.
- **Validation matrix:** routes, widths, themes, languages, directions and states.

Do not invent a decorative identity to fill space, and do not draw, redraw or recolour a Swarma
mark: use the approved files.

## Apply the system

### Identity

- The Swarma mark is the owner-approved Quorum identity. Its source of truth is the brand-assets
  repository at the commit pinned in [brand-identity.md](references/brand-identity.md). The header
  shows the horizontal lockup: the dark variant in dark appearances, the mono or white variant in
  forced colours. Favicons and app icons come from the same commit. Never recreate the wordmark
  with live text, recolour the mark or apply a CSS filter to it.
- Swarma leads in the header. Relux Works appears as operator in the footer, with an approved SVG
  from `assets/` copied unchanged: ink lockup on light surfaces, dark lockup on dark surfaces,
  one-colour artwork under forced colours.
- Keep the operator colours fixed at Relux red `#F60D10`, ink `#181A18` and knockout white
  `#FFFFFF`. They are not Swarma interface colours.

### Typography and writing

- Use PT Sans for display and interface text, PT Serif for reading prose and PT Mono for technical
  text, self-hosted from the OFL-licensed packages listed in
  [typography-and-content.md](references/typography-and-content.md).
- Keep the inherited fixed responsive scale, a 45rem reading measure and `letter-spacing: 0`. Use
  weights 400 and 700 only; PT Mono has 400 only.
- Write calm, direct, technically accurate copy backed by the book or a paper. Describe the design
  as design; show the state of a part only where the book's status chapter states it.
- Every Russian string follows the book's Russian style guide: no guillemets, no connector dashes,
  plain double quotes for quotations and chapter titles, the letter ё.

### Color and themes

- Use the semantic tokens in [tokens.css](assets/tokens.css). Components never hold literal colours.
- Support light, dark, light more contrast, dark more contrast, reduced transparency and forced
  colours. Dark mode is tuned separately, not inverted.
- Use the role layer only with the meanings of the book's diagrams and the status layer only with
  the book's five status words, always with text. See [color-and-themes.md](references/color-and-themes.md).
- After any token change, run `python3 scripts/check_contrast.py assets/tokens.css`; it must exit 0,
  and the `--control` run must exit 1. Regenerate
  [contrast-report.md](references/contrast-report.md) with `--report`.

### Layout and components

- Use the inherited container, spacing, radii (8 px at most), stable header zones and responsive
  grid from [layout-and-components.md](references/layout-and-components.md).
- Prefer full-width bands and unframed layouts. Cards only for repeated framed items, tools or
  modals; never nest cards.
- Use the Swarma components where the content calls for them: trust boundary, role marker, status
  badge, layer order, book figure, version context. The dashed container means a trust boundary and
  nothing else.
- Keep controls stable across states; state changes must not resize the surrounding layout.

### Book figures

- Show book diagrams unchanged, as images, on their white ground in every theme, with a frame, the
  book's caption, a source line and a text alternative. Pages stay complete without them. See
  [diagrams.md](references/diagrams.md).

### Motion and interaction

- Immediate press feedback, short interruptible transitions, `transform` and `opacity` only for
  ordinary state changes. Identity artwork, figures and structural components never animate. See
  [motion-and-interaction.md](references/motion-and-interaction.md).
- A consequential action shows the exact content it will submit before the person confirms it.

### Accessibility and internationalization

- WCAG 2.2 Level AA is the minimum for every route, state and required third-party step. Do not
  claim conformance until the automated and manual gates pass.
- Treat system theme, increased contrast, reduced motion, reduced transparency, forced colours,
  keyboard operation, zoom and reflow as product states.
- Build one logical LTR/RTL component system; isolate URLs, code, versions and both identities as
  LTR. Read [accessibility-and-i18n.md](references/accessibility-and-i18n.md) and
  [wcag-2.2-aa.md](references/wcag-2.2-aa.md).

### Discovery and trust

- Keep visible facts, metadata, structured data, `llms.txt` and other machine-facing surfaces in
  agreement, including status words and versions. See
  [discovery-and-trust.md](references/discovery-and-trust.md).

## Validate before declaring completion

Read and execute [quality-assurance.md](references/quality-assurance.md):

- Run the repository's build, lint, unit, accessibility and visual checks, and the contrast check.
- Run the `axe-core` gate and the required browser and screen-reader matrix.
- Inspect representative routes at 390, 768, 1440 and 1920 CSS px in light, dark, increased
  contrast, reduced motion and forced colours, in every supported script and direction.
- Check the Swarma mark variants against the pinned files, the operator artwork, the favicon,
  metadata and social images.
- Check book figures in every theme, and role and status markers for their text labels.
- Inspect screenshots yourself. A clean automated report does not prove good hierarchy.

## Reject these patterns

- Swarm, hive or bee imagery, particles, node-graph or network backdrops.
- Glow, gradient orbs, bokeh, decorative glass or one-hue washes as page structure.
- A drawn, traced, regenerated or recoloured Swarma mark, a live-text wordmark, a CSS filter on
  the mark, or any Swarma symbol other than the approved Quorum files.
- Redrawn, retyped, stretched, mirrored, animated or recoloured Relux Works artwork.
- Role or status colours used without text, for decoration, or with a meaning the book does not
  give them.
- A dashed container used for grouping, cards or callouts instead of a trust boundary.
- Recoloured, inverted or dark-themed book figures.
- Pure black or pure white interface colours (book figures' white ground and the operator's
  knockout white are the only exceptions).
- Large empty heroes, split hero cards or centred stacks with unrelated visual axes.
- Radii above 8 px in the interface; negative letter spacing; viewport-scaled font sizes.
- Hidden focus, hover-only information or motion without a reduced-motion equivalent.
- `overflow-x: hidden` used to conceal broken geometry.
- Generic claims about innovation, security, scale or AI capability without a book source or an
  observable artifact; status stated anywhere except from its source.
- Guillemets or connector dashes in Russian copy.

## What is inherited and what changed

This system is a fork. The Relux Works rules on geometry, the type scale, the token architecture,
theme states, motion, accessibility, internationalisation, discovery and QA apply unchanged unless a
reference marks a Swarma change. The full list is in [foundations.md](references/foundations.md),
"What Swarma inherits and what it changes". The licence and copyright stay with Relux Works; see
`LICENSE` and `NOTICE`.

## Resource map

- [swarma-identity.md](references/swarma-identity.md): every identity choice and its book source.
- [foundations.md](references/foundations.md): inheritance table, invariants, archetypes, worked
  example, decision record.
- [brand-identity.md](references/brand-identity.md): the Swarma Quorum mark, its source and usage
  rules, and the Relux Works operator artwork.
- [typography-and-content.md](references/typography-and-content.md): PT family, licence,
  self-hosting, scale, writing and Russian copy.
- [color-and-themes.md](references/color-and-themes.md): palette, role and status layers, themes,
  contrast evidence.
- [contrast-report.md](references/contrast-report.md): generated contrast results for every pair.
- [layout-and-components.md](references/layout-and-components.md): geometry, header, sections,
  controls and the Swarma components.
- [diagrams.md](references/diagrams.md): book figures on Swarma surfaces.
- [motion-and-interaction.md](references/motion-and-interaction.md): feedback, interruption,
  transitions, reduced motion.
- [accessibility-and-i18n.md](references/accessibility-and-i18n.md): semantics, keyboard, forms,
  themes, scripts and RTL.
- [wcag-2.2-aa.md](references/wcag-2.2-aa.md): conformance target and release profile.
- [discovery-and-trust.md](references/discovery-and-trust.md): facts, metadata, machine-facing
  surfaces.
- [quality-assurance.md](references/quality-assurance.md): test matrix, geometry checks, completion
  gate.
- [tokens.css](assets/tokens.css): the Swarma token contract.
- `scripts/check_contrast.py`: contrast check with a failing control.
- `assets/relux-*`: approved Relux Works operator artwork.
- [accessibility-statement.md](templates/accessibility-statement.md): public statement template.
