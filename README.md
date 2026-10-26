# Swarma Platform Design System

Design guidance, references, semantic tokens and approved operator artwork for Swarma web surfaces.
Start with [SKILL.md](SKILL.md) and its resource map. The design provenance is recorded in
[swarma-identity.md](references/swarma-identity.md).

## Tools and checks

All checks use Python 3.12 or newer and its standard library. No package installation is needed.
Run these commands from the repository root:

| Tool / command | Purpose | Output |
| --- | --- | --- |
| `python3 scripts/check_contrast.py` | Check all declared token contrast pairs | Console; exit 0 when every target passes |
| `python3 scripts/check_contrast.py --control` | Inject a known contrast violation in memory | Console; expected exit 1 with a failing light text-faint pair |
| `python3 scripts/check_contrast.py assets/tokens.css --report references/contrast-report.md` | Recompute the contrast report after a token change | Markdown report and console |
| `python3 -m unittest discover -s scripts/tests -v` | Run positive and isolated negative controls for hygiene and link checks | Console; temporary fixtures under `.temp/` are removed automatically |
| `python3 scripts/check_hygiene.py` | Reject internal identifiers in UTF-8 source and filenames; reject guillemets and connector dashes in Russian prose | Console diagnostics by path, line and rule |
| `python3 scripts/check_links.py` | Resolve relative Markdown links, images and reference destinations, including local heading and explicit HTML anchors | Console diagnostics; no external requests |
| GitHub Actions, `.github/workflows/ci.yml` | Run the same checks in one `check` job on pull requests and pushes to main | Hosted logs; contrast-control log in `.temp/` |

The contrast command accepts an optional token-file argument, defaulting to `assets/tokens.css`.
CI requires the contrast control to exit exactly 1 and report the intended failing pair;
an unrelated crash or an unexpectedly passing control does not satisfy the gate.
The unit controls similarly assert each planted hygiene/link violation's named rule and exit 1.

Hygiene scans repository files, including hidden publication directories. Git metadata, `.temp/`
scratch and Python bytecode caches are omitted. Binary artwork is omitted from text decoding.
Only `scripts/hygiene_rules.py` and `scripts/tests/test_ci.py` are exempt from generic-rule scanning:
they contain generic policy patterns and isolated synthetic violations. No publication directory
is exempt. Identifier rules still apply inside code examples elsewhere. Russian punctuation rules
apply to UTF-8 files containing Cyrillic prose, including metadata; fenced/inline code is omitted for this
prose-only rule. Word hyphens and numeric ranges remain valid.
The exact public skill invocation for `swarma-platform-design-system` is permitted only in
`agents/openai.yaml` and `locales/metadata.json`: its command prefix otherwise resembles an event
token. This exception covers only that complete invocation, never a longer token or another ID.

Markdown links are resolved relative to their source file; leading-slash destinations resolve
from the repository root. Percent escapes, balanced parentheses, angle destinations, reference
links, HTML href/src attributes, heading fragments and explicit HTML IDs are supported. Links may not escape the repository.
Fenced/inline code examples are omitted; external URLs are not fetched. This check establishes
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

Configure the repository secret `IDENT_DENY_TOKENS` before CI; the workflow supplies it to the check job.
CI fails if neither source provides a nonempty list, regardless of `IDENT_DENY_TOKENS_OPTIONAL`.
Locally, missing tokens print a warning, run the generic checks and exit nonzero by default.
For an explicit generic-only local run, use:

```sh
IDENT_DENY_TOKENS_OPTIONAL=1 python3 scripts/check_hygiene.py
```

The unit controls use synthetic tokens and temporary home directories. They test configured and unconfigured
plants, file fallback and environment precedence, mandatory CI configuration and the local-only opt-out.
