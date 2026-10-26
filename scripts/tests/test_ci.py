"""Executable clean and planted controls for the repository's publication checks."""

from pathlib import Path
import os
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
            self.assertTrue(any(line.endswith(": " + rule) for line in result.stdout.splitlines()), result.stdout)
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
                self.put(path, "Use $swarma-platform-design-system")
                self.run_check("check_hygiene.py")
                self.put(path, "Use $swarma-platform-design-system_extra")
                self.run_check("check_hygiene.py", "matrix-event")
                self.put(path, "Use $swarma-platform-design-system\n$" + "A" * 24)
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


if __name__ == "__main__":
    unittest.main()
