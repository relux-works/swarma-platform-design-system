# Swarma Platform Design System

Design guidance, references, semantic tokens and approved operator artwork for Swarma web surfaces.
Start with [SKILL.md](SKILL.md) and its resource map. The design provenance is recorded in
[swarma-identity.md](references/swarma-identity.md).

## Tools and checks

The checks use Node 22.23.4 or newer, Python 3.12 or newer and Chromium through Playwright.
Node dependencies are exact versions in `package.json` and `package-lock.json`.
CI installs Node 22 and Python 3.14 with setup actions on self-hosted `relux-generic` Linux x64 runners.
From the repository root, install the locked dependencies and browser:

```sh
npm ci
export PLAYWRIGHT_BROWSERS_PATH="$PWD/.temp/playwright-browsers"
npx playwright install chromium
```

Keep that environment variable set for subsequent checks. A local installed Chromium can instead
be selected with `PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH`; record its version in validation evidence.
CI installs the browser version selected by the locked Playwright dependency.

| Tool / command | Purpose | Output |
| --- | --- | --- |
| `node scripts/run.mjs <command> [arguments...]` | Start the trusted output supervisor before checker code | Complete stdout/stderr are redacted before release; child exit code is retained |
| `npm ci` | Install the locked CommonMark, HTML, YAML, CSS and browser tooling | `node_modules/` |
| `npx playwright install chromium` | Install the Playwright Chromium binary | The configured browser cache |
| `node scripts/run.mjs python3 scripts/check_contrast.py` | Measure computed token pairs and forced-color roles in Chromium | Console; exit 0 only when every target passes |
| `node scripts/run.mjs python3 scripts/check_contrast.py --control` | Inject a known failing value in the browser fixture | Console; expected exit 1 with the intended light text-faint failure |
| `node scripts/run.mjs python3 scripts/check_contrast.py assets/tokens.css --report references/contrast-report.md` | Recompute the four base-palette report after all browser appearances pass | Markdown report and console |
| `node scripts/run.mjs python3 -m unittest discover -s scripts/tests -v` | Run clean and isolated negative controls | Console; temporary fixtures under `.temp/` are removed |
| `node scripts/run.mjs python3 scripts/check_hygiene.py` | Check raw source, filenames and consumer-decoded publication values | Redacted rule diagnostics; nonzero on failure |
| `node scripts/run.mjs python3 scripts/check_ci_tokens.py` | Require a usable explicit CI secret without local fallback | Redacted diagnostics; nonzero on invalid configuration |
| `node scripts/run.mjs python3 scripts/check_links.py` | Resolve local links and anchors from rendered Markdown | Redacted diagnostics; no external requests |
| GitHub Actions, `.github/workflows/ci.yml` | Run the same checks on pull requests and main pushes | Job logs; contrast-control log under `.temp/` |

Contrast loads the shipped stylesheet unchanged through a local file URL in a fresh Chromium
fixture. It renders one element per declared pair, reads foreground/background colors with
`getComputedStyle`, then computes WCAG 2.x luminance and alpha compositing in Python. CSS source
is never parsed for color values. The browser resolves selectors, comments, media queries,
layers, source order, important declarations and variables. A missing browser, unavailable
media emulation, unreadable resource, invalid semantic color or unsupported computed color
representation fails with `contrast-browser`. Network resources are blocked.

Sixteen appearances cross light/dark, increased contrast, reduced transparency and forced colors.
All 2,816 pair measurements must pass. Forced-color probes disable automatic color adjustment
so a wrong semantic mapping remains observable; separate system-color probes verify the mappings
against this browser's own system colors. Pressed controls use Highlight/HighlightText, while
default and hover use ButtonFace/ButtonText. Forced-color measurements describe this emulation,
not every operating-system high-contrast palette. The report retains the four base palettes and
704 pairs; every appearance must pass before it is written. The control changes only one value
in the fixture DOM; it never writes the stylesheet. CI requires exit exactly 1 and the intended
failing pair, so an unrelated crash cannot satisfy the control.

Hygiene scans repository files, including hidden publication directories. The explicit tooling exclusion list is
`.git`, `.hg`, `.svn`, `node_modules`, `.temp` and `__pycache__`, as exact basenames in
either file or directory form at every depth. Git worktree pointer files are therefore
excluded too. Other hidden paths, including `.github/`, remain scanned; publication symlinks
and read failures outside these exclusions still reject. Binary artwork formats may
contain non-text bytes. Other source files must be UTF-8 without a BOM or NUL bytes; violations fail
`publication-encoding`. Malformed JSON, SVG and CSS parse errors fail `publication-decode`.
CSS follows the pinned parser's CSS error recovery, including EOF termination of strings/comments.

Only `scripts/hygiene_rules.py` and `scripts/tests/test_ci.py` are exempt from generic-rule scanning;
they contain generic policies and synthetic plants. External literals still apply to both.
Russian punctuation checks exclude rendered Markdown code blocks and spans; identifier checks
retain both raw code examples and rendered text. Other formats have no Markdown code exemption.
Word hyphens, numeric ranges and Markdown list markers remain valid.

Markdown uses pinned markdown-it CommonMark with tables and strikethrough enabled. Its rendered
HTML supplies attributes, links and anchors. Hygiene loads that HTML into Chromium for
`innerText`, decoded text nodes and full accessibility-tree names, descriptions and values,
across light and dark schemes at 1280px and 390px widths, each with forced colors inactive and active.
Rendered documents run in batches of at most eight within the existing browser and subprocess deadlines;
every document and all eight states remain required, and a failed batch rejects the scan.
Text, decoded attributes, computed pseudo-element content and full accessibility values are collected in all eight states,
including hidden `aria-labelledby` and `aria-describedby` references. Prose punctuation
excludes code/pre elements in that same browser DOM. A synthetic origin preserves each document's
location, base URLs, linked stylesheets, CSS imports and local images/fonts. Requests are fulfilled
from files inside the publication root; missing or escaping local resources reject the scan.
Scripts, service workers and remote resources are blocked. A missing browser or failed
render rejects the scan. Link resolution only needs the CommonMark/HTML parser and does not
launch Chromium.
parse5 supplies the HTML tree; github-slugger assigns IDs to rendered Markdown headings, including
inline-code text. Fenced, inline, indented and nested code examples create no live HTML IDs or
links. Undefined reference syntax remains literal text, as in CommonMark. Real reference links,
images and HTML links are resolved; local targets cannot escape the repository. External targets
are not fetched. This establishes local resolution, not external reachability.

The same Node publication engine is shared by hygiene and link checks. HTML text/attributes,
XML-parsed SVG values, JSON keys/string values, pinned YAML parser values and CSS Tree's parsed strings/identifiers/URLs
receive the same generic and external rules as raw source. Adjacent CSS generated-content
strings are joined. URL values receive percent decoding once; entity-looking CSS/JSON strings
are not recursively HTML-decoded. The URL decoder is copied from the site's publication module
at the provenance commit recorded in `scripts/css-publication.mjs`; HTML parsing and heading slugs
use the same dependency versions as the site. No reusable package or external service is required.

The exact public skill invocation for `swarma-platform-design-system` is permitted only in
`agents/openai.yaml` and `locales/metadata.json`, where its command prefix resembles an event token.
That exception covers only the complete invocation. Diagnostics use source line 0 for decoded
values and rendered links. Use the supervised commands above for every Python or Node project entry point. The trusted Node bootstrap starts
before Python/Node parses the child entry point or imports its modules. All child stdout/stderr, including syntax/import
failures and split writes, is buffered until exit and redacted before release. Signals are forwarded and child exit codes
are retained. A bootstrap policy failure emits only a fixed diagnostic. The in-process Python handler remains secondary
protection. Internal Node engines use captured structured-data pipes inside the supervised Python process; their raw
stderr is never forwarded, and their policy input is not rewritten. Direct unsupervised interpreter commands are outside
this diagnostic boundary. Publication values from different render states remain separate; they are never joined into
one token. Filesystem failures and publication symlinks reject safely without
exception payloads or tracebacks. There is no deployment workflow.

## External identifier tokens

Tracked policies and control fixtures contain generic identifier shapes and synthetic names only.
Generic rules cover Matrix IDs, board IDs, local paths, session URLs and workplace-name shapes.
Repository links and email addresses require exact entries in `config/public-repos.json`.
Real internal names come from `IDENT_DENY_TOKENS` (comma-separated literals), or the untracked file
`$HOME/.config/swarma-site/deny-tokens.txt` (one literal per line; commas are also accepted).
A nonempty environment list takes precedence over the file locally. Every token must match
`[a-z0-9][a-z0-9._-]{2,}` in full after trimming ASCII whitespace; one invalid entry or an empty configured
file rejects with fixed `identifier-deny-tokens` diagnostics without echoing the value. Matching folds ASCII
uppercase only; Unicode case folding is not performed. Literal matching
removes Unicode format characters and collapses Unicode whitespace (including line breaks and NBSP),
then also compares separator-free forms. Generic identifier patterns use the same normalizer,
including separator-free and unwrapped forms. Source and rendered paragraph boundaries remain
separate; ordinary single line wraps do not. Raw JSON/YAML records stay on their own lines;
decoded JSON/YAML keys and string values are inspected separately, including folded YAML scalars.
Malformed or unsupported YAML rejects `publication-decode`. Exact repository/email allowlists
retain word boundaries while removing format characters and rejoining line wraps.
Diagnostics redact both spaced and separator-free spellings, including split writes.
The external list applies to filenames and all UTF-8 sources, including the policy and control files exempt
from generic rules. Diagnostics report rule names and redact matching filenames, never token values.
Keep real tokens out of source, fixtures, documentation, command arguments and logs.

Configure the repository secret `IDENT_DENY_TOKENS` before CI; the workflow supplies it only to the repository hygiene step.
That step runs `node scripts/run.mjs python3 scripts/check_ci_tokens.py` before hygiene. The shared guard enforces the same ASCII-only grammar for every entry. Greek letters, invisible characters,
NBSP and uppercase entries reject; the explicit list must be nonempty.
CI uses only a valid explicit secret and never reads the local fallback file,
regardless of `IDENT_DENY_TOKENS_OPTIONAL`.
Locally, missing tokens print a warning, run the generic checks and exit nonzero by default.
For an explicit generic-only local run, use:

```sh
IDENT_DENY_TOKENS_OPTIONAL=1 node scripts/run.mjs python3 scripts/check_hygiene.py
```

The unit controls use synthetic tokens and temporary home directories. They test configured and unconfigured
plants, file fallback and environment precedence, mandatory CI configuration and the local-only opt-out.
