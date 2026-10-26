"""Executable clean and planted controls for the repository's publication checks."""

from pathlib import Path
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class Controls(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / ".temp"
        scratch.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix="ci-control-", dir=scratch)
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def put(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    def run_check(self, script, rule=None, env=None):
        environment = {**os.environ, "HOME": str(self.root), "CI": "", "IDENT_DENY_TOKENS": "zz-host-alpha",
                       "IDENT_DENY_TOKENS_OPTIONAL": "", **(env or {})}
        result = subprocess.run([sys.executable, str(ROOT / "scripts" / script), "--root", str(self.root)],
                                capture_output=True, text=True, timeout=10, env=environment)
        self.assertEqual(result.returncode, 1 if rule else 0, result.stdout + result.stderr)
        if rule:
            self.assertTrue(any(re.search(r": " + re.escape(rule) + r"(?:: |$)", line) for line in result.stdout.splitlines()), result.stdout)
            print(f"control {script}: {rule}: exit {result.returncode}")
        return result

    # A synthetic literal fails only when configured, including case variants and punctuation.
    def test_external_tokens(self):
        self.put("sample.txt", "ZZ-HOST-ALPHA and zz.host+alpha")
        self.run_check("check_hygiene.py", "deny-token")
        self.run_check("check_hygiene.py", env={"IDENT_DENY_TOKENS": "zz-host-beta"})
        self.run_check("check_hygiene.py", "deny-token", {"IDENT_DENY_TOKENS": " , zz.host+alpha, "})
        self.put("sample.txt", "zzXhosttalpha")
        self.run_check("check_hygiene.py", env={"IDENT_DENY_TOKENS": "zz.host+alpha"})

    # External tokens cover normally exempt policy sources and filenames without echoing values.
    def test_external_scope_and_redaction(self):
        for path in ["scripts/hygiene_rules.py", "scripts/tests/test_ci.py", ".github/probe.yml", "zz-host-alpha.md"]:
            with self.subTest(path=path):
                self.put(path, "zz-host-alpha")
                result = self.run_check("check_hygiene.py", "deny-token")
                self.assertNotIn("zz-host-alpha", result.stdout.lower())
                (self.root / path).unlink()

    # File fallback is valid in CI, while an explicit nonempty environment list takes precedence.
    def test_external_file_fallback(self):
        self.put("home/.config/swarma-site/deny-tokens.txt", "zz-host-alpha\nzz-host-beta\n")
        env = {"HOME": str(self.root / "home"), "IDENT_DENY_TOKENS": "", "CI": "true"}
        # The source lives outside the scanned fixture, just as the real local file does.
        scan = self.root / "publication"
        scan.mkdir()
        self.root = scan
        self.put("sample.txt", "zz-host-alpha")
        self.run_check("check_hygiene.py", "deny-token", env)
        self.run_check("check_hygiene.py", env={**env, "IDENT_DENY_TOKENS": "zz-host-gamma"})
        self.put("sample.txt", "Ordinary text")
        self.run_check("check_hygiene.py", env=env)

    # A missing or empty list fails in CI even if the local-only opt-out is set.
    def test_missing_tokens_in_ci(self):
        for optional in ["", "1"]:
            with self.subTest(optional=optional):
                self.run_check("check_hygiene.py", "identifier-deny-tokens",
                               {"IDENT_DENY_TOKENS": " , ", "CI": "true", "IDENT_DENY_TOKENS_OPTIONAL": optional})

    # Local absence warns and fails unless explicitly optional; generic checks remain active.
    def test_optional_local_tokens(self):
        env = {"IDENT_DENY_TOKENS": "", "CI": ""}
        missing = self.run_check("check_hygiene.py", "identifier-deny-tokens", env)
        self.assertIn("Warning: external deny tokens are missing", missing.stderr)
        optional = self.run_check("check_hygiene.py", env={**env, "IDENT_DENY_TOKENS_OPTIONAL": "1"})
        self.assertIn("Warning: external deny tokens are missing", optional.stderr)
        self.put("sample.txt", "@reader:example.org")
        self.run_check("check_hygiene.py", "matrix-user", {**env, "IDENT_DENY_TOKENS_OPTIONAL": "1"})

    # Session URLs and repository/email allowlists reject neighbors while accepting exact public entries.
    def test_generic_link_and_email_rules(self):
        self.put("config/public-repos.json", '{"repositories":["public-example"],"emails":["public@example.org"]}')
        self.put("sample.txt", "https://github.com/relux-works/public-example.git public@example.org")
        self.run_check("check_hygiene.py")
        for value, rule in [("https://github.com/relux-works/public-example-extra", "private-repository"),
                            ("other@example.org", "email"), ("https://claude.ai/code/session_example", "session-link"),
                            ("https://chatgpt.com/codex/example", "session-link"), ("C:\\Users\\reader", "local-path")]:
            with self.subTest(rule=rule):
                self.put("sample.txt", value)
                self.run_check("check_hygiene.py", rule)

    # Malformed allowlists fail configuration validation; a well-formed empty list is accepted.
    def test_allowlist_validation(self):
        for value in ['{', '[]', '{"repositories":[1],"emails":[]}', '{"repositories":[],"emails":"all"}']:
            with self.subTest(value=value):
                self.put("config/public-repos.json", value)
                self.run_check("check_hygiene.py", "identifier-allowlist")
        self.put("config/public-repos.json", '{"repositories":[],"emails":[]}')
        self.run_check("check_hygiene.py")

    # Ordinary web code, Russian hyphens/ranges, list markers and code examples are valid publication text.
    def test_hygiene_clean(self):
        self.put("prose.md", '# Swarma\n\nРусско-английский текст, ёж, 1-2 шага.\n\n- Пункт.\n\n`пример — кода`\n\n```text\n«код»\n```\n')
        self.put("style.css", '@media (min-width: 1px) { a { color: inherit !important; } }')
        self.put("script.js", 'const text = `${value}!`;')
        self.run_check("check_hygiene.py")

    # Only the exact public skill invocation in its two metadata files avoids the event-token collision.
    def test_public_invocation(self):
        for path in ["agents/openai.yaml", "locales/metadata.json"]:
            with self.subTest(path=path):
                def put_value(value):
                    self.put(path, json.dumps(value) if path.endswith(".json") else value)
                put_value("Use $swarma-platform-design-system")
                self.run_check("check_hygiene.py")
                put_value("Use $swarma-platform-design-system_extra")
                self.run_check("check_hygiene.py", "matrix-event")
                put_value("Use $swarma-platform-design-system\n$" + "A" * 24)
                self.run_check("check_hygiene.py", "matrix-event")
                (self.root / path).unlink()
        self.put("other.md", "$swarma-platform-design-system")
        self.run_check("check_hygiene.py", "matrix-event")

    # Russian metadata and HTML prose obey the same punctuation policy as Markdown.
    def test_russian_metadata_and_html(self):
        for path in ["metadata.json", "page.html"]:
            with self.subTest(path=path):
                self.put(path, '{"text": "Русский «текст»"}')
                self.run_check("check_hygiene.py", "russian-guillemets")
                (self.root / path).unlink()

    # Every identifier family and listed prefix/path form fails its precise rule in an isolated fixture.
    def test_hygiene_identifiers(self):
        cases = [("matrix-user", "@reader:example.org"), ("matrix-event", "$" + "A" * 24),
                 ("matrix-room", "!" + "a" * 24 + ":example.org")]
        cases += [("board-id", prefix + "-000000-aaaaaa") for prefix in ["TASK", "STORY", "BUG", "EPIC"]]
        cases += [("internal-name", value) for value in ["sample-dev1", "sample_rev1", "sample_orch"]]
        cases += [("local-path", path) for path in ["/Users/example", "/home/example/file", "~/example"]]
        for rule, value in cases:
            with self.subTest(rule=rule, value=value):
                self.put("sample.txt", value)
                self.run_check("check_hygiene.py", rule)

    # Russian guillemets and connector dashes reject; the adjacent valid prose control remains accepted.
    def test_russian_punctuation(self):
        for value, rule in [('Русский «текст»', 'russian-guillemets'), ('Русский »текст', 'russian-guillemets'),
                            ('Русский — текст', 'russian-dash'), ('Русский – текст', 'russian-dash'),
                            ('Русский - текст', 'russian-dash')]:
            with self.subTest(value=value):
                self.put("sample.md", value)
                self.run_check("check_hygiene.py", rule)
                self.put("sample.md", "Русский текст, ёж.")
                self.run_check("check_hygiene.py")

    # Hidden publication directories and filenames are scanned; exclusions do not cover other script files.
    def test_hygiene_scan_scope(self):
        for path in [".github/sample.yml", "scripts/example.py", "references/sample.md"]:
            with self.subTest(path=path):
                self.put(path, "@reader:example.org")
                self.run_check("check_hygiene.py", "matrix-user")
                (self.root / path).unlink()
        self.put("TASK-000000-aaaaaa.md", "Ordinary prose")
        self.run_check("check_hygiene.py", "board-id")
        (self.root / "TASK-000000-aaaaaa.md").unlink()
        (self.root / "TASK-000000-aaaaaa.png").write_bytes(b"\xff\x00")
        self.run_check("check_hygiene.py", "board-id")

    # Existing paths, encoded/spaced/balanced names, images, references and real heading/HTML anchors resolve.
    def test_links_clean(self):
        self.put("target.md", '# Target `code`\n\n## Target code\n\nРусский заголовок\n===\n\n<a id="explicit"></a>\n')
        self.put("a (b).svg", '<svg id="image"></svg>')
        self.put("docs/page.md", '[Root](/target.md#target-code)\n[Duplicate](../target.md#target-code-1)\n'
                 '[RU](../target.md#русский-заголовок)\n[ID](../target.md#explicit)\n'
                 '![Image](<../a (b).svg#image>)\n[Escaped](../a%20(b).svg)\n'
                 '[Named][ref]\n[ref][]\n[ref]\n[ref]: ../target.md "Title"\n<a href="../target.md#explicit">HTML</a>\n'
                 '[External](https://example.org/missing)\n[Mail](mailto:reader@example.org)\n'
                 '`[Code](missing.md)`\n```md\n[Example](missing.md)\n```\n')
        self.run_check("check_links.py")

    # A missing target, fragment, reference or out-of-repository path fails its intended resolution rule.
    def test_link_plants(self):
        self.put("target.md", "# Existing\n")
        for text, rule in [('[Missing](missing.md)', 'markdown-link'), ('![Missing](missing.svg)', 'markdown-link'),
                           ('<a href="missing.md">Missing</a>', 'markdown-link'),
                           ('[Missing][undefined]', 'markdown-link'), ('[Missing](target.md#absent)', 'markdown-anchor'),
                           ('[Escape](../outside.md)', 'markdown-link')]:
            with self.subTest(text=text):
                self.put("page.md", text)
                result = subprocess.run([sys.executable, str(ROOT / "scripts/check_links.py"), "--root", str(self.root)],
                                        capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn(": " + rule + ": ", result.stdout)
                print(f"control check_links.py: {rule}: exit {result.returncode}")

    # Publication consumers decode entities, JSON strings and CSS escapes before applying identifier policy.
    def test_decoded_identifier_values(self):
        cases = [
            ("probe.md", "Русский &#64;reader:example.org", "matrix-user"),
            ("probe.md", "Русский &commat;reader:example.org", "matrix-user"),
            ("probe.md", '<a title="&#64;reader:example.org">Text</a>', "matrix-user"),
            ("probe.md", "[Target](/&#85;sers/reader/file)", "local-path"),
            ("probe.md", "[Target](%2FUsers%2Freader%2Ffile)", "local-path"),
            ("probe.svg", '<svg xmlns="http://www.w3.org/2000/svg"><text>&#x40;reader:example.org</text></svg>', "matrix-user"),
            ("probe.svg", '<svg xmlns="http://www.w3.org/2000/svg" aria-label="&#64;reader:example.org"/>', "matrix-user"),
            ("probe.svg", '<svg xmlns="http://www.w3.org/2000/svg"><title>&#64;reader:example.org</title></svg>', "matrix-user"),
            ("probe.svg", '<svg xmlns="http://www.w3.org/2000/svg"><desc>&#64;reader:example.org</desc></svg>', "matrix-user"),
            ("probe.json", r'{"label":"\u0040reader:example.org"}', "matrix-user"),
            ("probe.json", r'{"\u0040reader:example.org":["Text"]}', "matrix-user"),
            ("probe.css", r'p::after { content: "\40 reader:example.org"; }', "matrix-user"),
            ("probe.css", r'p::after { content: "\000040reader:example.org"; }', "matrix-user"),
            ("probe.css", r'p::after { content: "\@reader:example.org"; }', "matrix-user"),
            ("probe.css", 'p::after { content: "\\40 rea\\\nder:example.org"; }', "matrix-user"),
            ("probe.css", r'p { background: url("\2f Users/reader/file"); }', "local-path"),
            ("probe.css", 'p { background: url("%2FUsers%2Freader%2Ffile"); }', "local-path"),
            ("probe.css", 'p { background: url(%2FUsers%2Freader%2Ffile); }', "local-path"),
            ("probe.css", 'p {content:"zz-host-" "alpha"}', "deny-token"),
            ("probe.svg", '<svg xmlns="http://www.w3.org/2000/svg"><style>p {content:"\\40 reader:example.org"}</style></svg>', "matrix-user"),
        ]
        for path, value, rule in cases:
            with self.subTest(path=path, value=value):
                clean = {".md": "Swarma &#38; text", ".svg": "<svg><text>Swarma &#38; text</text></svg>",
                         ".json": r'{"label":"\u0053warma"}', ".css": r'p {content:"\53 warma"}'}
                self.put(path, clean[Path(path).suffix])
                self.run_check("check_hygiene.py")
                self.put(path, value)
                self.run_check("check_hygiene.py", rule)
                (self.root / path).unlink()

    # The external list and prose rules apply after each format's own decoding, with adjacent valid controls.
    def test_decoded_external_tokens_and_punctuation(self):
        cases = [
            ("probe.md", "zz-host-&#97;lpha", "Русский &#171;текст&#187;", "Swarma &#38; текст"),
            ("probe.svg", '<svg><text>zz-host-&#97;lpha</text></svg>', '<svg><text>Русский &#171;текст&#187;</text></svg>', '<svg><text>Swarma &#38; текст</text></svg>'),
            ("probe.json", r'{"label":"zz-host-\u0061lpha"}', r'{"label":"Русский \u00abтекст\u00bb"}', r'{"label":"\u0053warma"}'),
            ("probe.css", r'p {content:"zz-host-\61 lpha"}', r'p {content:"Русский \ab текст\bb "}', r'p {content:"\53 warma"}'),
        ]
        for path, token, punctuation, clean in cases:
            with self.subTest(path=path):
                self.put(path, clean)
                self.run_check("check_hygiene.py")
                self.put(path, token)
                self.run_check("check_hygiene.py", "deny-token")
                self.put(path, punctuation)
                self.run_check("check_hygiene.py", "russian-guillemets")
                (self.root / path).unlink()
        self.put("probe.json", r'{"label":"Русский \u2014 текст"}')
        self.run_check("check_hygiene.py", "russian-dash")

    # Decoding follows the consumer once; CSS/JSON entity-looking text and encoded Markdown code stay literal.
    def test_decoding_context_boundaries(self):
        for path, value in [
            ("probe.md", "&amp;#64;reader:example.org\n`Русский &#171;код&#187;`"),
            ("probe.css", r'p {content:"\26 #64;reader:example.org"}'),
            ("probe.json", '{"label":"&#64;reader:example.org"}'),
            ("probe.svg", '<svg><text>&amp;#64;reader:example.org</text></svg>'),
        ]:
            with self.subTest(path=path):
                self.put(path, value)
                self.run_check("check_hygiene.py")
                (self.root / path).unlink()
        # Backticks in metadata are rendered text, not a Markdown code exemption.
        self.put("probe.json", r'{"label":"`Русский \u00abтекст\u00bb`"}')
        self.run_check("check_hygiene.py", "russian-guillemets")

    # Malformed supported formats cannot silently skip the decoded-value policy.
    def test_publication_decode_errors(self):
        for path, value in [("probe.json", '{"label":'), ("probe.svg", '<svg><text>'),
                            ("probe.css", 'p {content:"unfinished}'), ("probe.css", '/* unfinished')]:
            with self.subTest(path=path):
                self.put(path, value)
                self.run_check("check_hygiene.py", "publication-decode")
                (self.root / path).unlink()

    # Fenced and inline code supply neither HTML IDs nor links; real headings and HTML/SVG IDs still resolve.
    def test_code_only_anchors(self):
        self.put("page.md", "[Target](target.md#ghost)")
        for code in ['```html\n<div id="ghost">Example</div>\n```\n', '`<div id="ghost">Example</div>`\n',
                     '~~~html\n<div id="ghost">Example</div>\n~~~\n', '``<div id="ghost">Example</div>``\n']:
            with self.subTest(code=code):
                self.put("target.md", "# Actual `heading`\n\n" + code)
                self.run_check("check_links.py", "markdown-anchor")
                self.put("target.md", '# Ghost\n\n' + code)
                self.run_check("check_links.py")
        self.put("target.md", '# Actual `heading`\n\n<a id="ghost"></a>\n')
        self.run_check("check_links.py")
        self.put("page.md", "[Target](target.md#actual-heading)\n`[Ignored](missing.md)`\n```md\n[Ignored](absent.md)\n```")
        self.run_check("check_links.py")
        for path in ["target.html", "target.svg"]:
            self.put(path, '<svg id="literal"><text>`code`</text></svg>')
            self.put("page.md", f"[Literal]({path}#literal)")
            self.run_check("check_links.py")

    def contrast(self, css, diagnostic=None, report=False):
        self.put("tokens.css", css)
        command = [sys.executable, str(ROOT / "scripts/check_contrast.py"), str(self.root / "tokens.css")]
        if report:
            command += ["--report", str(self.root / "report.md")]
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 1 if diagnostic else 0, result.stdout + result.stderr)
        if diagnostic:
            self.assertRegex(result.stdout + result.stderr, diagnostic)
            print(f"control contrast: {diagnostic}: exit {result.returncode}")
        return result

    # Actual late root declarations change measured contrast; earlier superseded declarations and comments do not.
    def test_contrast_root_cascade(self):
        css = (ROOT / "assets/tokens.css").read_text()
        plant = ':root { --color-text: #ffffff; --color-bg: #ffffff; }'
        self.contrast(css + plant, r"FAIL light\s+text on bg\s+1\.00")
        self.contrast(plant + css)
        self.contrast(css + '/* ' + plant + ' */', report=True)
        self.assertEqual((self.root / "report.md").read_text(), (ROOT / "references/contrast-report.md").read_text())

    # Media selection, reduced transparency, important precedence and variable resolution affect the measured values.
    def test_contrast_media_important_and_variables(self):
        css = (ROOT / "assets/tokens.css").read_text()
        plant = ':root { --color-text: #ffffff; --color-bg: #ffffff; }'
        dark = self.contrast(css + '@media (prefers-color-scheme: dark) {' + plant + '}', r"FAIL dark\s+text on bg\s+1\.00")
        self.assertRegex(dark.stdout, r"PASS light\s+text on bg")
        self.contrast(css + '@media (prefers-reduced-transparency: reduce) {' + plant + '}', r"FAIL light/reduced\s+text on bg\s+1\.00")
        important = re.sub(r'(--color-[\w-]+:\s*[^;]+);', r'\1 !important;', css)
        self.contrast(important + plant)
        self.contrast(css + ':root {--color-text:#ffffff !important;--color-bg:#ffffff !important;}'
                      + ':root {--color-text:#000000;}', r"FAIL light\s+text on bg\s+1\.00")
        self.contrast(css + ':root {--color-text:var(--missing,var(--color-text-muted));}')
        self.contrast(css + ':root { --probe: #ffffff; --color-text: var(--probe); --color-bg: var(--probe); }', r"FAIL light\s+text on bg\s+1\.00")

    # Forced colors are checked against symbolic system roles, not invented numeric OS color values.
    def test_contrast_forced_colors(self):
        css = (ROOT / "assets/tokens.css").read_text()
        self.contrast(css)
        self.contrast(css + '@media (forced-colors: active) {:root {--color-text: Canvas;}}', r"forced-color-role")

    # Unknown cascade constructs and unresolved colors reject explicitly rather than producing misleading passing ratios.
    def test_contrast_unsupported_contract(self):
        css = (ROOT / "assets/tokens.css").read_text()
        for plant in ['body {--color-text:#ffffff;}', '@layer extra {:root {--color-text:#ffffff;}}',
                      '@supports (display:grid) {:root {--color-text:#ffffff;}}', '@import "other.css";',
                      ':root {--color-text:var(--missing);}', ':root {--color-text:var(--color-text);}',
                      ':root {--color-text:light-dark(white,black);}', ':root {--color-text:#ffffff;',
                      ': root {--color-text:#ffffff;}', '@ media (prefers-color-scheme: dark) {}',
                      '@media ("prefers-color-scheme": dark) {}',
                      ':root {--color-text:rgba(0,0,0,2);}', ':root {--color-text:#ffffff #000000;}',
                      ':root {--color-text:rgb/**/(0,0,0);}', ':root {--color-text:rgba(0,0,0,0 . 1);}',
                      ':root {--color-text:Canvas/**/Text;}']:
            with self.subTest(plant=plant):
                self.contrast(css + plant, r"contrast-css:")

    # Real production scripts reject the review witnesses in a complete source copy, with a clean-copy control first.
    def test_complete_repository_regressions(self):
        publication = self.root / "publication"
        shutil.copytree(ROOT, publication, ignore=shutil.ignore_patterns(".temp", ".git", "__pycache__"))
        environment = {**os.environ, "IDENT_DENY_TOKENS": "zz" + "-integration-alpha", "CI": "true"}

        def invoke(script, rule=None):
            result = subprocess.run([sys.executable, str(publication / "scripts" / script)], cwd=publication,
                                    env=environment, capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 1 if rule else 0, result.stdout + result.stderr)
            if rule:
                self.assertIn(rule, result.stdout + result.stderr)

        for script in ["check_hygiene.py", "check_links.py", "check_contrast.py"]:
            invoke(script)
        (publication / "references/encoded.md").write_text("Русский &#64;reader:example.org\nzz-integration-&#97;lpha")
        invoke("check_hygiene.py", "matrix-user")
        invoke("check_hygiene.py", "deny-token")
        (publication / "references/encoded.md").write_text('[Ghost](target.md#ghost)')
        (publication / "references/target.md").write_text('```html\n<div id="ghost"></div>\n```')
        invoke("check_links.py", "markdown-anchor")
        with (publication / "assets/tokens.css").open("a") as file:
            file.write(':root {--color-text:#ffffff;--color-bg:#ffffff;}')
        invoke("check_contrast.py", "FAIL light")


if __name__ == "__main__":
    unittest.main()
