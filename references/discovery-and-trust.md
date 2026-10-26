# Discovery and Trust

Inherited from the Relux Works product web design system, with Swarma rules added in "Swarma facts".

## One public fact model

Treat every public surface as a view of one maintained fact model:

- Visible product copy and prices.
- Page title, description, canonical URL, and social metadata.
- Approved operator logo, favicon, avatar, and social artwork.
- Structured data and feeds.
- Locale and market variants.
- Documentation, release notes, and status pages.
- `llms.txt`, machine catalogs, MCP tools, and public APIs when they exist.

The same product must not be active on one surface, experimental on another, and
discontinued in a third. Keep ownership, availability, price, currency, language,
version, and support claims synchronized from structured source data where practical.

## Swarma facts

- **One source per fact.** Statements about the platform come from the Swarma book or its papers
  and name the chapter, section or paper they come from.
- **Design and state stay apart.** The book describes the platform by its design, in the present
  tense, and keeps the state of every part in its status chapter (book `book/ru/00-dlya-kogo.md`,
  "Дизайн и готовность"). A Swarma surface presents design as design and shows the state of a part
  only where that chapter states it, in its words, never higher.
- **Exact versions.** Every page that relies on the book or a paper names the version and date.
  Status data names the book version it was taken from.
- **Machine-facing agreement.** `llms.txt`, structured data and any agent-facing catalog carry the
  same facts as the visible pages, including the same status words, and no more.
- **No internal material.** No internal identifiers, session, machine or agent names, local paths
  or private repository links on any public surface.

## Product identity

Every public product page should answer:

- What is the product's literal name and category?
- What task does it perform and for whom?
- Is it available, in development, open source, private preview, or archived?
- Who operates it and how is it related to Relux Works?
- Which platforms, regions, languages, and integrations are supported?
- Where can a person inspect the product, documentation, source, status, or policy?

Use the product name as a first-viewport signal and in the document title. Do not make
the relationship to Relux Works ambiguous, but keep the product as the primary brand
on its own site.

Represent the operator with approved Relux Works artwork from
[brand-identity.md](brand-identity.md). Do not substitute a typed wordmark, recolored
symbol, or image-generated approximation.

## Metadata and localization

- Give every indexable page a specific title and description that agree with visible
  content.
- Use one canonical URL per language-market variant.
- Publish reciprocal `hreflang` links and an intentional `x-default`.
- Keep language and market separate: a Persian page may serve a founder in Germany,
  Canada, or the UAE without claiming a payment market in Iran.
- Render local currency only when the pricing and commercial terms actually apply to
  that market. Include the currency code in visible text and structured data.
- Keep structured offers synchronized mechanically with visible packages and prices.
- Set `Organization.logo` to an approved standalone Relux Works asset when the format
  accepts it. Keep the same operator identity in visible attribution and metadata.
- Provide theme-aware SVG favicons plus the platform fallbacks the product supports.
  Use approved plated avatars where a platform controls the crop or background.
- Build social images from approved outlined artwork and the same maintained fact
  model as the page. Never use live fallback type or generated logo geometry.
- Use meaningful, stable URLs. Redirect retired paths and avoid duplicate parameter
  variants.
- Derive `lastmod` from meaningful content history, not every build date.

## Evidence before claims

Search and answer systems need clear evidence more than additional machine-only prose.
Prioritize:

1. An inspectable real product state or workflow.
2. Specific compatibility and limitation data.
3. Dated documentation and release history.
4. Authorship, operator identity, policies, and contact paths.
5. Approved case studies, measurements, and methodology.
6. Structured metadata that restates the same verified facts.

Do not manufacture testimonial language, user counts, reliability percentages, or
security labels. If a metric is useful, publish its scope, date, and method.

## Agent-facing surfaces

Machine interfaces can reduce conversion friction but do not replace an understandable
website.

- A read-only MCP tool may return product capabilities, packages, prices, supported
  markets, and evidence.
- A side-effecting tool must describe the effect, require the minimum data, show a
  draft, and require explicit user consent before submission.
- Return stable identifiers, human-readable labels, currency codes, source URLs, and
  update timestamps.
- Keep tool data synchronized with visible pages and structured data.
- Explain a useful non-terminal path for people who do not use agent environments.
- Do not claim that an MCP endpoint, crawler hint, or `llms.txt` guarantees ranking or
  inclusion in an assistant marketplace.

Machine catalogs should be concise and factual. Publishing many near-duplicate files
without better evidence creates maintenance risk and inconsistent answers.

## Drafts and lifecycle

- Draft, preview, internal, and incomplete pages use `noindex` and stay out of public
  sitemaps and feeds.
- Archived products state their status and retain useful documentation where safe.
- Remove `in progress`, availability, or client relationship claims as soon as their
  factual state changes.
- Do not expose confidential client details merely to make a portfolio entry feel more
  concrete. Verify publication rights and use an approved description.
- Keep public status vocabulary bounded and documented.

## Security and privacy trust

- State what data is collected, why, for how long, and which provider receives it.
- Ask for permissions at the moment they become necessary.
- Avoid third-party tracking by default. If analytics are necessary, document the
  lawful basis and keep telemetry proportionate.
- Publish a security contact and vulnerability process for products with a meaningful
  attack surface.
- Never put private operator surfaces, customer records, tokens, or diagnostic payloads
  in public structured data or machine catalogs.
- Separate public product APIs from private administration with explicit authentication,
  authorization, audit history, and rate limits.

## Accessibility accountability

- Publish a localized accessibility statement using
  [accessibility-statement.md](../templates/accessibility-statement.md).
- Name WCAG 2.2 Level AA as the target and publish only the conformance status supported
  by the current evaluation.
- Include the last assessment date, tested browser and assistive-technology matrix,
  known limitations, accessible alternatives, and remediation status.
- Provide a monitored accessible feedback channel, expected response time, and
  escalation path. Do not require the inaccessible workflow itself to report a barrier.
- Keep the statement linked with a consistent label from the footer or support area and
  update it after material accessibility changes or at least annually.

## Release checklist

- Visible facts, structured data, MCP/API output, documentation, and feeds agree.
- Product and operator identity are unambiguous.
- Header, footer, favicon, avatar, `Organization.logo`, and social artwork use the
  correct approved mark, variant, crop, and text.
- Canonical, locale, market, and currency semantics are correct.
- Drafts and previews cannot be indexed accidentally.
- Claims link to evidence or have been removed.
- Social images show the actual product or domain object, preserve the approved Relux
  artwork, and remain readable in both common crops.
- Privacy, terms, support, source, status, and security links exist only when accurate.
- The accessibility statement and feedback channel are current and reachable.
