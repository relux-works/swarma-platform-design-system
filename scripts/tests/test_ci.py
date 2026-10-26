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
                                capture_output=True, text=True, timeout=60, env=environment)
        self.assertEqual(result.returncode, 1 if rule else 0, result.stdout + result.stderr)
        if rule:
            self.assertTrue(any(re.search(r": " + re.escape(rule) + r"(?:: |$)", line) for line in (result.stdout + result.stderr).splitlines()), result.stdout + result.stderr)
            print(f"control {script}: {rule}: exit {result.returncode}")
        return result

    # Ordinary reflow and invisible separators cannot conceal a literal; paragraph and code boundaries stay separate.
    def test_rendered_whitespace_policy(self):
        environment = {"IDENT_DENY_TOKENS": "zz reviewer omega"}
        for value in ["zz reviewer\nomega", "zz reviewer  omega", "zz reviewer\u00a0omega",
                      "zz review\u200der omega", "zz reviewer  \nomega", "zz **reviewer**\nomega",
                      "zzrevieweromega"]:
            with self.subTest(value=value):
                self.put("probe.md", value.replace("omega", "public"))
                self.run_check("check_hygiene.py", env=environment)
                self.put("probe.md", value)
                result = self.run_check("check_hygiene.py", "deny-token", environment)
                self.assertNotIn("zz reviewer omega", (result.stdout + result.stderr).lower())
        for value in ["zz reviewer\n\nomega", "zz reviewer\n\n```text\nomega\n```",
                      "<p>zz reviewer</p><p>omega</p>"]:
            self.put("probe.md", value)
            self.run_check("check_hygiene.py", env=environment)
        for path, value in [("probe.txt", "zz reviewer\nomega"),
                            ("probe.json", '{"label":"zz reviewer  omega"}'),
                            ("probe.css", 'p {content:"zz reviewer  omega"}')]:
            self.put("probe.md", "Public text")
            self.put(path, value)
            self.run_check("check_hygiene.py", "deny-token", environment)
            (self.root / path).unlink()

    # Hidden ARIA references are resolved by Chromium, including descriptions, roles absent from snapshots, and SVG.
    def test_full_accessibility_values(self):
        environment = {"IDENT_DENY_TOKENS": "zz reviewer omega"}
        for suffix in ["md", "html", "svg"]:
            for attribute in ["aria-labelledby", "aria-describedby"]:
                with self.subTest(suffix=suffix, attribute=attribute):
                    body = ('<span id="a" hidden>zz reviewer</span><span id="b" hidden>omega</span>'
                            '<button ' + attribute + '="a b">Public button</button>')
                    if suffix == "svg":
                        body = ('<svg xmlns="http://www.w3.org/2000/svg"><text id="a" display="none">zz reviewer</text>'
                                '<text id="b" display="none">omega</text><g role="button" tabindex="0" '
                                + attribute + '="a b"><text>Public button</text></g></svg>')
                    self.put("probe." + suffix, body.replace("omega", "public"))
                    self.run_check("check_hygiene.py", env=environment)
                    self.put("probe." + suffix, body)
                    self.run_check("check_hygiene.py", "deny-token", environment)
                    (self.root / ("probe." + suffix)).unlink()
        self.put("probe.html", '<span hidden id="a">Русский</span><span hidden id="b">— текст</span><button aria-labelledby="a b">Public</button>')
        self.run_check("check_hygiene.py", "russian-dash")
        self.put("probe.html", '<span hidden id="a">Русский</span><span hidden id="b">текст</span><button aria-labelledby="a b">Public</button>')
        self.run_check("check_hygiene.py")
        missing = self.run_check("check_hygiene.py", "identifier-scan", {
            "PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH": str(self.root / "zz-host-alpha-missing-browser")})
        self.assertNotIn("zz-host-alpha", missing.stdout + missing.stderr)
        self.assertNotIn("Traceback", missing.stdout + missing.stderr)

    # Git pointers and documented tooling are excluded in either form, while neighboring publications still reject.
    def test_git_metadata_forms(self):
        self.put("public.md", "Public text")
        pointer = "gitdir: /home/example/repository/.git/worktrees/sample-rev1"
        for script in ["check_hygiene.py", "check_links.py"]:
            self.put(".git", pointer)
            self.run_check(script)
            (self.root / ".git").unlink()
            self.put(".git/config", pointer)
            self.run_check(script)
            shutil.rmtree(self.root / ".git")
        self.put("published.txt", pointer)
        self.run_check("check_hygiene.py", "local-path")
        (self.root / "published.txt").unlink()
        for name in [".hg", ".svn", ".temp", "node_modules", "__pycache__"]:
            self.put(name + "/metadata", pointer)
        self.run_check("check_hygiene.py")
        self.put(".github/published.md", pointer)
        self.run_check("check_hygiene.py", "local-path")

    # Normalized denied basenames and split diagnostic writes redact without disclosing compact or spaced forms.
    def test_normalized_diagnostic_redaction(self):
        token = "zz reviewer omega"
        name = "zz\u200breviewer\u200domega.txt"
        self.put(name, "Public text")
        result = self.run_check("check_hygiene.py", "deny-token", {"IDENT_DENY_TOKENS":token})
        self.assertIn("[redacted]", result.stdout + result.stderr)
        self.assertNotIn(name, result.stdout + result.stderr)
        source = ("import sys; sys.path.insert(0, " + repr(str(ROOT / 'scripts')) + "); "
                  "from diagnostics import run_cli; "
                  "sys.exit(run_cli(lambda: print('zz reviewer\\n\\tomega') or 0, 'check-error'))")
        result = subprocess.run([sys.executable, '-c', source], capture_output=True, text=True,
                                env={**os.environ, 'IDENT_DENY_TOKENS':token})
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "[redacted]")
        source = ("import sys; sys.path.insert(0, " + repr(str(ROOT / 'scripts')) + "); "
                  "from diagnostics import run_cli; "
                  "sys.exit(run_cli(lambda: print('ZZ STRASSE') or 0, 'check-error'))")
        result = subprocess.run([sys.executable, '-c', source], capture_output=True, text=True,
                                env={**os.environ, 'IDENT_DENY_TOKENS':'zz straße'})
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "[redacted]")

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

    # Local file fallback works; an explicit nonempty environment list takes precedence.
    def test_external_file_fallback(self):
        self.put("home/.config/swarma-site/deny-tokens.txt", "zz-host-alpha\nzz-host-beta\n")
        env = {"HOME": str(self.root / "home"), "IDENT_DENY_TOKENS": "", "CI": ""}
        # The source lives outside the scanned fixture, just as the real local file does.
        scan = self.root / "publication"
        scan.mkdir()
        self.root = scan
        self.put("sample.txt", "zz-host-alpha")
        self.run_check("check_hygiene.py", "deny-token", env)
        self.run_check("check_hygiene.py", env={**env, "IDENT_DENY_TOKENS": "zz-host-gamma"})
        self.put("sample.txt", "Ordinary text")
        self.run_check("check_hygiene.py", env=env)

    # Every generic family rejects invisible and line-wrapped identifiers, with adjacent valid controls.
    def test_generic_normalization(self):
        cases = [("matrix-user", "@rea", "der:example.org"),
                 ("matrix-event", "$" + "A" * 12, "A" * 12),
                 ("matrix-room", "!" + "a" * 12, "a" * 12 + ":example.org"),
                 ("board-id", "TASK-000", "000-aaaaaa"),
                 ("internal-name", "example-de", "v1"),
                 ("local-path", "/Us", "ers/example"),
                 ("session-link", "https://chatgpt.com/co", "dex/example")]
        for rule, prefix, suffix in cases:
            for separator in ["\u200d", "\n"]:
                with self.subTest(rule=rule, separator=repr(separator)):
                    self.put("probe.txt", prefix + separator + "public")
                    self.run_check("check_hygiene.py")
                    self.put("probe.txt", prefix + separator + suffix)
                    self.run_check("check_hygiene.py", rule)
                    self.put("probe.txt", "Identifier " + prefix + separator + suffix + " in prose")
                    self.run_check("check_hygiene.py", rule)
        self.put("probe.txt", "@rea\n\nder:example.org")
        self.run_check("check_hygiene.py")
        for path, value in [("probe.json", '{"first":"@rea","second":"der:example.org"}'),
                            ("probe.yaml", 'first: "@rea"\nsecond: "der:example.org"'),
                            ("probe.yaml", 'uses: actions/checkout@v4\nname: Public step')]:
            self.put(path, value)
            self.run_check("check_hygiene.py")
            (self.root / path).unlink()
        self.put("config/public-repos.json", '{"repositories":["public-example"],"emails":["public@example.org"]}')
        for value, rule in [("https://github.com/relux-works/pri\u200dvate-example", "private-repository"),
                            ("https://git\nhub.com/relux-works/private-example", "private-repository"),
                            ("rea\u200dder@example.org", "email"), ("reader@exam\nple.org", "email")]:
            self.put("probe.txt", value)
            self.run_check("check_hygiene.py", rule)
        self.put("probe.txt", "https://github.com/relux-works/public-example.git public@example.org")
        self.run_check("check_hygiene.py")
        self.put("probe.txt", "https://git\nhub.com/relux-works/public-example.git public@exam\nple.org")
        self.run_check("check_hygiene.py")

    # A folded YAML scalar is one value; independent fields remain separate and malformed YAML rejects.
    def test_yaml_value_boundaries(self):
        self.put("probe.yaml", 'first: "@rea"\nsecond: "der:example.org"')
        self.run_check("check_hygiene.py")
        for value in ['label: "@rea\n  der:example.org"', 'label: >-\n  @rea\n  der:example.org',
                      'label: "@rea\\u200dder:example.org"']:
            self.put("probe.yaml", value.replace("der:example.org", "public"))
            self.run_check("check_hygiene.py")
            self.put("probe.yaml", value)
            self.run_check("check_hygiene.py", "matrix-user")
        self.put("probe.yaml", 'label: [')
        self.run_check("check_hygiene.py", "publication-decode")
        self.put("probe.yaml", 'label: Public text')
        self.run_check("check_hygiene.py")

    # The actual workflow guard rejects unusable Unicode secrets despite a valid ambient local policy.
    def test_workflow_secret_guard(self):
        workflow = (ROOT / ".github/workflows/ci.yml").read_text()
        step = workflow.split("      - name: Repository hygiene\n", 1)[1].split("      - name:", 1)[0]
        block = step.split("        run: |\n", 1)[1]
        command = "\n".join(line[10:] for line in block.splitlines())
        shutil.copytree(ROOT / "scripts", self.root / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
        self.put("home/.config/swarma-site/deny-tokens.txt", "zz-ambient-policy")
        publication = self.root / "publication"
        publication.mkdir()
        environment = {**os.environ, "HOME": str(self.root / "home"), "CI": "true", "IDENT_DENY_TOKENS_OPTIONAL": "1"}
        for token in ["", " , \n", "\u200d", "\u00a0", "\u00ad\u2060\ufeff", "a\u200db", "a\u00a0b", "at"]:
            with self.subTest(token=repr(token)):
                result = subprocess.run(["bash", "-e", "-o", "pipefail", "-c", command], cwd=self.root,
                                        env={**environment, "IDENT_DENY_TOKENS":token}, capture_output=True, text=True)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("identifier-deny-tokens", result.stdout + result.stderr)
                self.assertNotIn("zz-ambient-policy", result.stdout + result.stderr)
                if token == "at":
                    self.assertNotIn(token, result.stdout + result.stderr)
                self.run_check("check_hygiene.py", "identifier-deny-tokens", {**environment, "IDENT_DENY_TOKENS":token})
        # Use a real scan, rather than a stub, for the workflow's valid secret control.
        shutil.copytree(ROOT / "scripts", publication / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
        valid = "q" + "xz"
        for token in [valid, "q\u200dx\u00a0z", " , " + valid + "\n"]:
            result = subprocess.run(["bash", "-e", "-o", "pipefail", "-c", command], cwd=publication,
                                    env={**environment, "IDENT_DENY_TOKENS":token}, capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    # Linked and inline CSS yield the same AX verdict; imports/base/local assets load and missing dependencies reject.
    def test_linked_stylesheet_accessibility(self):
        environment = {"IDENT_DENY_TOKENS": "zz review omega"}
        self.put("styles/entry.css", '@import "nested/generated.css";')
        style = 'button::before {content:attr(data-prefix) " " attr(data-suffix)}'
        self.put("styles/nested/generated.css", style)
        body = ('<base href="../"><link rel="stylesheet" href="styles/entry.css" media="screen">'
                '<button data-prefix="zz review" data-suffix="omega"></button>')
        for suffix in ["html", "md"]:
            for document in [body, body.replace('<link rel="stylesheet" href="styles/entry.css" media="screen">', '<style>' + style + '</style>')]:
                self.put("pages/probe." + suffix, document.replace('data-suffix="omega"', 'data-suffix="public"'))
                self.run_check("check_hygiene.py", env=environment)
                self.put("pages/probe." + suffix, document)
                self.run_check("check_hygiene.py", "deny-token", environment)
            (self.root / ("pages/probe." + suffix)).unlink()
        self.put("pages/probe.html", body.replace('data-suffix="omega"', 'data-suffix="public"'))
        (self.root / "styles/nested/generated.css").unlink()
        self.run_check("check_hygiene.py", "publication-decode", environment)
        self.put("styles/nested/generated.css", "button {background-image:url(../../images/public.svg)}")
        self.put("images/public.svg", '<svg xmlns="http://www.w3.org/2000/svg"/>')
        self.run_check("check_hygiene.py", env=environment)
        (self.root / "images/public.svg").unlink()
        self.run_check("check_hygiene.py", "publication-decode", environment)

    # A missing or empty list fails in CI even if the local-only opt-out is set.
    def test_missing_tokens_in_ci(self):
        for optional in ["", "1"]:
            with self.subTest(optional=optional):
                self.run_check("check_hygiene.py", "identifier-deny-tokens",
                               {"IDENT_DENY_TOKENS": " , ", "CI": "true", "IDENT_DENY_TOKENS_OPTIONAL": optional})

        self.run_check("check_hygiene.py", "identifier-deny-tokens",
                       {"IDENT_DENY_TOKENS": "\u200b", "CI": "true"})

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
                 '`[Code](missing.md)`\n```md\n[Example](missing.md)\n```\n[Literal][undefined]\n')
        self.run_check("check_links.py")

    # A missing target, fragment, reference or out-of-repository path fails its intended resolution rule.
    def test_link_plants(self):
        self.put("target.md", "# Existing\n")
        for text, rule in [('[Missing](missing.md)', 'markdown-link'), ('![Missing](missing.svg)', 'markdown-link'),
                           ('<a href="missing.md">Missing</a>', 'markdown-link'),
                           ('[Missing](target.md#absent)', 'markdown-anchor'),
                           ('[Escape](../outside.md)', 'markdown-link')]:
            with self.subTest(text=text):
                self.put("page.md", text)
                result = subprocess.run([sys.executable, str(ROOT / "scripts/check_links.py"), "--root", str(self.root)],
                                        capture_output=True, text=True, timeout=60)
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
                            ("probe.css", 'p {content:"unfinished\n}'), ("probe.css", 'p {background: url(foo bar)}')]:
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

    # Browser-ignored corrective at-rules cannot conceal an effective white-on-white token override.
    def test_comment_separated_at_keyword(self):
        css = (ROOT / "assets/tokens.css").read_text()
        white = ':root {--color-text:#ffffff;--color-bg:#ffffff;}'
        ignored = ''.join('@/**/media (prefers-color-scheme: ' + scheme + ') {' + css + '}'
                          for scheme in ['light', 'dark'])
        self.contrast(css + white + ignored, r"FAIL light\s+text on bg\s+1\.00")
        valid = ''.join('@media/**/ (prefers-color-scheme: ' + scheme + ') {' + css + '}'
                        for scheme in ['light', 'dark'])
        self.contrast(css + white + valid)

    # Indented and nested CommonMark code has no live IDs or links; real markup and headings do.
    def test_indented_code_anchors(self):
        self.put("page.md", "[Ghost](target.md#ghost)")
        for code in ['    <div id="ghost">Text</div>\n',
                     '>     <div id="ghost">Text</div>\n',
                     '- Example\n\n      <div id="ghost">Text</div>\n']:
            with self.subTest(code=code):
                self.put("target.md", '# Actual\n\n' + code)
                self.run_check("check_links.py", "markdown-anchor")
                self.put("target.md", '# Ghost\n\n' + code)
                self.run_check("check_links.py")
        self.put("target.md", '<div id="ghost">Text</div>\n')
        self.put("page.md", '[Ghost](target.md#ghost)\n\n    [Code](missing.md)\n')
        self.run_check("check_links.py")

    # Formatting can split a prohibited literal in source but cannot hide its rendered contiguous text.
    def test_rendered_markdown_literals(self):
        for value in ['zz-host-**alpha**', 'zz-host-*alpha*', 'zz-host-__alpha__',
                      'zz-host-~~alpha~~', 'zz-host-`alpha`', 'zz-host-[alpha](https://example.org)']:
            with self.subTest(value=value):
                self.put("probe.md", value.replace("alpha", "public"))
                self.run_check("check_hygiene.py")
                self.put("probe.md", value)
                result = self.run_check("check_hygiene.py", "deny-token")
                self.assertNotIn("zz-host-alpha", (result.stdout + result.stderr).lower())
        self.put("probe.md", '@rea**der**:example.org')
        self.run_check("check_hygiene.py", "matrix-user")

    # Chromium independently confirms that the CommonMark result has no code-only anchor and joins emphasized text.
    def test_markdown_browser_witness(self):
        source = r"""
import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {inspectDocument} from './scripts/publication-engine.mjs';
const browser = await chromium.launch({executablePath:process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH || undefined});
try {
  const page = await browser.newPage();
  const negative = inspectDocument({suffix:'.md', source:'# Target\n\n    <div id="ghost">Code</div>\n\nzz-host-**alpha**'});
  await page.setContent(negative.html);
  assert.equal(await page.locator('#ghost').count(), 0);
  assert.ok((await page.locator('body').innerText()).includes('zz-host-alpha'));
  const positive = inspectDocument({suffix:'.md', source:'# Target `code`\n\n<div id="ghost">Public text</div>'});
  await page.setContent(positive.html);
  assert.equal(await page.locator('#ghost').count(), 1);
  assert.equal(await page.locator('#target-code').count(), 1);
  assert.ok(!(await page.locator('body').innerText()).includes('zz-host-alpha'));
  console.log('CommonMark browser witnesses and clean controls passed');
} finally { await browser.close(); }
"""
        result = subprocess.run(['node', '--input-type=module', '-e', source], cwd=ROOT,
                                env={**os.environ, 'TMPDIR': str(self.root)}, capture_output=True, text=True, timeout=90)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('browser witnesses and clean controls passed', result.stdout)

    # A genuine unreadable denied basename fails safely; a readable neighbor passes and permissions are restored.
    def test_unreadable_publication_redaction(self):
        path = self.root / "zz-host-alpha.txt"
        self.put(path.name, "Ordinary text")
        path.chmod(0)
        try:
            with self.assertRaises(PermissionError):
                path.read_text()
            result = self.run_check("check_hygiene.py", "identifier-scan")
            self.assertNotIn("zz-host-alpha", (result.stdout + result.stderr).lower())
            self.assertNotIn("Traceback", result.stdout + result.stderr)
        finally:
            path.chmod(0o600)
        path.rename(self.root / "readable.txt")
        self.run_check("check_hygiene.py")

    # Every check's top-level boundary suppresses exception payloads and redacts tokens split across writes.
    def test_top_level_diagnostic_boundaries(self):
        for module, rule in [('check_hygiene', 'identifier-scan'), ('check_links', 'markdown-link'),
                             ('check_contrast', 'contrast-browser')]:
            with self.subTest(module=module):
                source = ("import sys\nsys.path.insert(0, " + repr(str(ROOT / 'scripts')) + ")\n"
                          "import " + module + " as check\n"
                          "def broken():\n print('zz-host-', end='')\n print('alpha')\n"
                          " raise OSError('zz-host-alpha.txt')\n"
                          "sys.exit(check.run_cli(broken, " + repr(rule) + "))\n")
                result = subprocess.run([sys.executable, '-c', source], capture_output=True, text=True,
                                        env={**os.environ, 'IDENT_DENY_TOKENS': 'zz-host-alpha'})
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn(rule, result.stderr)
                self.assertIn('[redacted]', result.stdout)
                self.assertNotIn('zz-host-alpha', (result.stdout + result.stderr).lower())
                self.assertNotIn('Traceback', result.stdout + result.stderr)

    # An unreadable policy source prevents every check from emitting diagnostics whose values cannot be redacted.
    def test_unreadable_policy_stops_diagnostics(self):
        home = self.root / 'home'
        (home / '.config/swarma-site/deny-tokens.txt').mkdir(parents=True)
        for module in ['check_hygiene', 'check_links', 'check_contrast']:
            with self.subTest(module=module):
                source = ("import sys; sys.path.insert(0, " + repr(str(ROOT / 'scripts')) + "); "
                          "import " + module + " as check; "
                          "sys.exit(check.run_cli(lambda: print('zz-host-alpha.txt') or 0, 'check-error'))")
                result = subprocess.run([sys.executable, '-c', source], capture_output=True, text=True,
                                        env={**os.environ, 'HOME':str(home), 'IDENT_DENY_TOKENS':'', 'CI':''})
                self.assertEqual(result.returncode, 1)
                self.assertIn('identifier-deny-tokens', result.stdout + result.stderr)
                self.assertNotIn('zz-host-alpha', result.stdout + result.stderr)
        (home / '.config/swarma-site/deny-tokens.txt').rmdir()
        self.put('ordinary.txt', 'Public text')
        self.run_check('check_hygiene.py')

    # Traversal errors and publication symlinks reject without exposing denied directory names or reading targets.
    def test_traversal_redaction(self):
        directory = self.root / 'zz-host-alpha'
        directory.mkdir()
        directory.chmod(0)
        try:
            with self.assertRaises(PermissionError):
                list(directory.iterdir())
            for script, rule in [('check_hygiene.py', 'identifier-scan'), ('check_links.py', 'markdown-link')]:
                result = self.run_check(script, rule)
                self.assertNotIn('zz-host-alpha', (result.stdout + result.stderr).lower())
                self.assertNotIn('Traceback', result.stdout + result.stderr)
        finally:
            directory.chmod(0o700)
        self.put('readable.txt', 'Ordinary text')
        for script in ['check_hygiene.py', 'check_links.py']:
            self.run_check(script)
        (self.root / 'link.txt').symlink_to(self.root / 'readable.txt')
        self.run_check('check_hygiene.py', 'identifier-scan')
        (self.root / 'link.txt').unlink()
        self.run_check('check_hygiene.py')

    # Text publication rejects UTF-8 BOM and non-UTF-8 encodings; ordinary UTF-8 and binary artwork remain valid.
    def test_publication_encoding(self):
        for path, data in [('probe.md', b'\xef\xbb\xbfSwarma'),
                           ('probe.html', '<p>Swarma</p>'.encode('utf-16')),
                           ('probe.svg', '<svg><text>Swarma</text></svg>'.encode('utf-16')),
                           ('probe.txt', b'\xffSwarma'),
                           ('probe.html', '<p>Swarma</p>'.encode('utf-16-le'))]:
            with self.subTest(path=path):
                self.put(path, 'Swarma' if not path.endswith('.svg') else '<svg><text>Swarma</text></svg>')
                self.run_check('check_hygiene.py')
                (self.root / path).write_bytes(data)
                self.run_check('check_hygiene.py', 'publication-encoding')
                (self.root / path).unlink()
        (self.root / 'art.png').write_bytes(b'\xff\x00')
        self.run_check('check_hygiene.py')

    def contrast(self, css, diagnostic=None, report=False):
        self.put("tokens.css", css)
        command = [sys.executable, str(ROOT / "scripts/check_contrast.py"), str(self.root / "tokens.css")]
        if report:
            command += ["--report", str(self.root / "report.md")]
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
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

    # The former pressed mapping is a numeric browser failure; the approved HighlightText pairing passes.
    def test_pressed_forced_color_pair(self):
        css = (ROOT / "assets/tokens.css").read_text()
        self.contrast(css)
        self.contrast(css + '@media (forced-colors: active) {:root {--color-control-text-pressed:ButtonText;}}',
                      r"FAIL light/forced\s+control-text-pressed on control-pressed\s+[0-9.]+")

    # CSS validity and cascade behavior come from Chromium, including selectors, layers and modern color functions.
    def test_browser_css_contract(self):
        css = (ROOT / "assets/tokens.css").read_text()
        for plant in [': root {--color-text:#ffffff;}', '@ media (prefers-color-scheme: dark) {}',
                      '@media ("prefers-color-scheme": dark) {}',
                      '@layer extra {:root {--color-text:#ffffff;}}']:
            with self.subTest(plant=plant):
                self.contrast(css + plant)
        for plant in [':root {--color-text:var(--missing);}', ':root {--color-text:var(--color-text);}',
                      ':root {--color-text:#ffffff #000000;}', ':root {--color-text:rgb/**/(0,0,0);}',
                      ':root {--color-text:rgba(0,0,0,0 . 1);}', ':root {--color-text:Canvas/**/Text;}']:
            with self.subTest(plant=plant):
                self.contrast(css + plant, r"contrast-browser:")
        self.contrast(css + ':root {--color-text:light-dark(white,black);}', r"FAIL light")
        self.contrast(css + 'body {--color-text:#ffffff;}', r"FAIL light")
        self.contrast(css + '@supports (display:grid) {:root {--color-text:#ffffff;}}', r"FAIL light")

    # Real production scripts reject the review witnesses in a complete source copy, with a clean-copy control first.
    def test_complete_repository_regressions(self):
        publication = self.root / "publication"
        shutil.copytree(ROOT, publication, ignore=shutil.ignore_patterns(".temp", ".git", "__pycache__", "node_modules"))
        (publication / "node_modules").symlink_to(ROOT / "node_modules", target_is_directory=True)
        environment = {**os.environ, "IDENT_DENY_TOKENS": "zz" + "-integration-alpha", "CI": "true"}

        def invoke(script, rule=None):
            result = subprocess.run([sys.executable, str(publication / "scripts" / script)], cwd=publication,
                                    env=environment, capture_output=True, text=True, timeout=90)
            self.assertEqual(result.returncode, 1 if rule else 0, result.stdout + result.stderr)
            if rule:
                self.assertIn(rule, result.stdout + result.stderr)

        for script in ["check_hygiene.py", "check_links.py", "check_contrast.py"]:
            invoke(script)
        (publication / "references/encoded.md").write_text("Русский &#64;reader:example.org\nzz-integration-&#97;lpha")
        invoke("check_hygiene.py", "matrix-user")
        invoke("check_hygiene.py", "deny-token")
        (publication / "references/encoded.md").write_text('zz-integration-**alpha**')
        invoke("check_hygiene.py", "deny-token")
        prefix, ending = "zz" + "-integration-", "al" + "pha"
        for value in [prefix + "\n" + ending, prefix + "  " + ending, prefix + "\u200d" + ending,
                      '<span hidden id="a">' + prefix + '</span><span hidden id="b">' + ending
                      + '</span><button aria-labelledby="a b">Public</button>']:
            (publication / "references/encoded.md").write_text(value)
            invoke("check_hygiene.py", "deny-token")
        (publication / "references/encoded.md").write_text('[Ghost](target.md#ghost)')
        (publication / "references/target.md").write_text('```html\n<div id="ghost"></div>\n```')
        invoke("check_links.py", "markdown-anchor")
        (publication / "references/target.md").write_text('    <div id="ghost"></div>\n')
        invoke("check_links.py", "markdown-anchor")
        original = (publication / "assets/tokens.css").read_text()
        with (publication / "assets/tokens.css").open("a") as file:
            file.write(':root {--color-text:#ffffff;--color-bg:#ffffff;}')
        invoke("check_contrast.py", "FAIL light")
        with (publication / "assets/tokens.css").open("a") as file:
            file.write(''.join('@/**/media (prefers-color-scheme: ' + scheme + ') {' + original + '}'
                               for scheme in ['light', 'dark']))
        invoke("check_contrast.py", "FAIL light")


if __name__ == "__main__":
    unittest.main()
