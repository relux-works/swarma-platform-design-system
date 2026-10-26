# Swarma Platform Design System

Design guidance, references, semantic tokens and approved operator artwork for Swarma web surfaces.
Start with [SKILL.md](SKILL.md) and its resource map. The design provenance is recorded in
[swarma-identity.md](references/swarma-identity.md).

## Tools and checks

All checks use Python 3.12 or newer and its standard library. No package installation is needed.
CI uses self-hosted Linux x64 runners and asserts Python 3.14 from PATH.
Run these commands from the repository root:

| Tool / command | Purpose | Output |
| --- | --- | --- |
| `python3 scripts/check_contrast.py` | Check effective token contrast pairs and forced-color roles | Console; exit 0 when every target passes |
| `python3 scripts/check_contrast.py --control` | Inject a known contrast violation in memory | Console; expected exit 1 with a failing light text-faint pair |
| `python3 scripts/check_contrast.py assets/tokens.css --report references/contrast-report.md` | Recompute the contrast report after a token change | Markdown report and console |
| `python3 -m unittest discover -s scripts/tests -v` | Run positive and isolated negative controls for publication checks | Console; temporary fixtures under `.temp/` are removed automatically |
| `python3 scripts/check_hygiene.py` | Reject internal identifiers in UTF-8 source and filenames; reject guillemets and connector dashes in Russian prose | Console diagnostics by path, source line (0 for decoded values) and rule |
| `python3 scripts/check_links.py` | Resolve relative Markdown links, images and reference destinations, including local heading and explicit HTML anchors | Console diagnostics; no external requests |
| GitHub Actions, `.github/workflows/ci.yml` | Run the same checks in one `check` job on pull requests and pushes to main | Hosted logs; contrast-control log in `.temp/` |

The contrast command accepts an optional token-file argument, defaulting to `assets/tokens.css`.
It evaluates the complete stylesheet, including declarations outside palette comments. The accepted
stylesheet contract is deliberately narrow: `:root` declarations, custom properties and `color-scheme`,
and nested `@media` conjunctions for `prefers-color-scheme` (light/dark), `prefers-contrast`
(no-preference/more), `prefers-reduced-transparency` (no-preference/reduce), and `forced-colors`
(none/active). Within this contract it applies source order, `!important`, CSS escapes and `var()`
references/fallbacks. Other selectors, at-rules, unresolved/cyclic references, unsupported color values
and malformed syntax fail with `contrast-css`; expanding the stylesheet contract requires expanding
and testing the evaluator. This is a restricted static evaluator, not a general browser CSS engine.

All effective semantic colors are resolved in 16 appearance combinations. Eight numeric appearances
(the four palettes, each with and without reduced transparency) measure 1,408 declared pairs using
six-digit hex and legacy `rgba()` colors. Root backgrounds must be opaque. The other eight forced-color
appearances must preserve the documented system-color roles. Their numeric colors depend on the browser
and operating system, so this check establishes role preservation rather than an OS contrast ratio.
The generated report retains the four base palettes and 704 pairs; report writing requires all
appearances to pass. Token values, forced-color mappings and non-palette tokens are not changed by checks.
CI requires the contrast control to exit exactly 1 and report the intended failing pair;
an unrelated crash or an unexpectedly passing control does not satisfy the gate.
The unit controls assert each planted hygiene/link violation's named rule and exit 1, and exercise
late root/media overrides, important precedence, variable references, unsupported CSS and forced-color
role violations. A complete-repository fixture runs the production checks before and after plants.

Hygiene scans repository files, including hidden publication directories. Git metadata, `.temp/`
scratch and Python bytecode caches are omitted. Binary artwork is omitted from text decoding.
Only `scripts/hygiene_rules.py` and `scripts/tests/test_ci.py` are exempt from generic-rule scanning:
they contain generic policy patterns and isolated synthetic violations. No publication directory
is exempt. Identifier rules still apply inside code examples elsewhere. Russian punctuation rules
apply to UTF-8 files containing Cyrillic prose, including metadata; Markdown fenced/inline code is
omitted for this prose-only rule. Backticks in other formats do not create a prose exemption.
Word hyphens and numeric ranges remain valid.

In addition to raw source, hygiene scans publication values after format-specific decoding: Markdown
entities, inline HTML attributes and link destinations; HTML text/attributes; XML-decoded SVG text,
titles, descriptions and attributes; parsed JSON keys/string values; and CSS escaped identifiers,
strings, generated content and URLs. Embedded style attributes/elements use CSS decoding. URL targets
also receive percent decoding. Decoding follows each consumer context once, without recursively
unescaping entity-looking text in JSON or CSS strings. Malformed supported JSON, SVG or CSS lexical
input fails with `publication-decode`. Both generic rules and external literals apply to decoded values;
decoded diagnostics use line 0 because their positions can span source lines.
The exact public skill invocation for `swarma-platform-design-system` is permitted only in
`agents/openai.yaml` and `locales/metadata.json`: its command prefix otherwise resembles an event
token. This exception covers only that complete invocation, never a longer token or another ID.

Markdown links are resolved relative to their source file; leading-slash destinations resolve
from the repository root. Percent escapes, balanced parentheses, angle destinations, reference
links, HTML href/src attributes, heading fragments and explicit HTML IDs are supported. Links may not escape the repository.
Fenced/inline code examples supply neither links nor HTML IDs. Inline-code text in real Markdown
headings still contributes to heading slugs; literal HTML/SVG target IDs are read as markup.
External URLs are not fetched. This check establishes
local resolution, not external reachability. No deployment workflow is included.

## External identifier tokens

Tracked policies and control fixtures contain generic identifier shapes and synthetic names only.
Generic rules cover Matrix IDs, board IDs, local paths, session URLs and workplace-name shapes.
Repository links and email addresses require exact entries in `config/public-repos.json`, initially empty.
Real internal names come from `IDENT_DENY_TOKENS` (comma-separated literals), or the untracked file
`$HOME/.config/swarma-site/deny-tokens.txt` (one literal per line; commas are also accepted).
A nonempty environment list takes precedence over the file. Matches are case-insensitive literal substrings.
The external list applies to filenames and all UTF-8 sources, including the policy and control files exempt
from generic rules. Diagnostics report rule names and redact matching filenames, never token values.
Keep real tokens out of source, fixtures, documentation, command arguments and logs.

Configure the repository secret `IDENT_DENY_TOKENS` before CI; the workflow supplies it only to the repository hygiene step.
That step rejects an empty or delimiter-only secret before running hygiene, without using a local-file fallback.
CI requires a nonempty repository secret, regardless of `IDENT_DENY_TOKENS_OPTIONAL`.
Locally, missing tokens print a warning, run the generic checks and exit nonzero by default.
For an explicit generic-only local run, use:

```sh
IDENT_DENY_TOKENS_OPTIONAL=1 python3 scripts/check_hygiene.py
```

The unit controls use synthetic tokens and temporary home directories. They test configured and unconfigured
plants, file fallback and environment precedence, mandatory CI configuration and the local-only opt-out.
