"""Reject internal identifiers and forbidden punctuation in Russian Markdown prose."""

from diagnostics import deny_tokens, run_cli
import argparse
import json
import os
import re
import sys
from pathlib import Path
from check_common import ROOT, files
from hygiene_rules import EMAIL, IDENTIFIERS, INVOCATION_FILES, PUBLIC_INVOCATION, REPOSITORY, RUSSIAN, RUSSIAN_RULES
from publication_values import MARKUP, documents, strings
from publication_policy import candidates, match_views, normalized, redact, token_match, unformatted

# Only generic policy definitions and the isolated controls have generic-rule exemptions.
EXEMPT = {"scripts/hygiene_rules.py", "scripts/tests/test_ci.py"}
BINARY = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".woff", ".woff2", ".ttf", ".otf"}


def check(root):
    errors = []
    try:
        tokens = deny_tokens()
    except (OSError, UnicodeError, ValueError):
        return ["configuration:0: identifier-deny-tokens"]
    ci = os.environ.get("CI", "").lower() not in {"", "0", "false"}
    if not tokens:
        if not ci:
            print("Warning: external deny tokens are missing; only generic rules are running", file=sys.stderr)
        if ci or os.environ.get("IDENT_DENY_TOKENS_OPTIONAL") != "1":
            errors.append("configuration:0: identifier-deny-tokens")
    allowlist_path = root / "config/public-repos.json"
    try:
        allowlist = json.loads(allowlist_path.read_text(encoding="utf-8")) if allowlist_path.exists() else {"repositories": [], "emails": []}
        if not isinstance(allowlist, dict) or any(not isinstance(allowlist.get(key), list) or any(not isinstance(item, str) for item in allowlist[key]) for key in ["repositories", "emails"]):
            raise ValueError("invalid allowlist")
    except (OSError, ValueError):
        return ["configuration:0: identifier-allowlist"]

    def redacted(value):
        return redact(value, tokens)

    records = []
    for path in files(root):
        relative = path.relative_to(root).as_posix()
        if token_match(relative, tokens):
            errors.append(f"{relative}:0: deny-token")
        if relative not in EXEMPT:
            for rule, pattern in IDENTIFIERS.items():
                if any(pattern.search(candidate) for candidate in candidates(relative)):
                    errors.append(f"{relative}:0: {rule}")
        try:
            text = path.read_text(encoding="utf-8")
            if path.suffix.lower() not in BINARY and (text.startswith("\ufeff") or "\0" in text):
                errors.append(f"{relative}:0: publication-encoding")
            else:
                records.append((path, text))
        except UnicodeDecodeError:
            if path.suffix.lower() not in BINARY:
                errors.append(f"{relative}:0: publication-encoding")
        except OSError:
            errors.append(f"{relative}:0: identifier-scan: cannot read publication")
    rendered = documents([(path, text) for path, text in records if path.suffix.lower() in MARKUP], rendered=True, root=root)
    for path, text in records:
        relative = path.relative_to(root).as_posix()
        label = redacted(relative)
        info = rendered.get(path)
        views = [(text, info["prose"] if info and not info.get("error") else text, 1)]
        if info:
            if info.get("error"):
                errors.append(f"{label}:0: publication-decode")
            else:
                views.extend((value, value, 0) for value in info["values"])
                for state in info.get("states", [info]):
                    views.append((state["text"], state["prose"], 0))
                    views.extend((value, value if prose else "", 0) for value, prose in state.get("decoded", []) + state.get("accessible", []))
                    views.extend((value, value, 0) for value in state.get("computed", []))
        elif path.suffix.lower() == ".json":
            try:
                views.extend((value, value, 0) for value in strings(json.loads(text)))
            except ValueError:
                errors.append(f"{label}:0: publication-decode")
        # Identical observations have the same rules and location within this document.
        # Deduplicate complete views, preserving prose flags and state boundaries rather than joining states.
        views = list(dict.fromkeys(views))
        russian = any(RUSSIAN.search(body) for _, body, _ in views)
        for value, body, start in views:
            # External literals are forbidden even in the exempt policy and control sources.
            # Raw structured records stay on their source lines; decoded JSON values are independent views.
            join_lines = not (start and path.suffix.lower() in {".json", ".yaml", ".yml"})
            for line, number in match_views(value, start, join_lines=join_lines):
                if token_match(line, tokens):
                    errors.append(f"{label}:{number if start else 0}: deny-token")
                if relative in EXEMPT:
                    continue
                for rule, pattern in IDENTIFIERS.items():
                    candidate = PUBLIC_INVOCATION.sub("", unformatted(line)) if rule == "matrix-event" and relative in INVOCATION_FILES else line
                    if any(pattern.search(view) for view in candidates(candidate)):
                        errors.append(f"{label}:{number if start else 0}: {rule}")
                # Exact allowlist entries retain surrounding word boundaries, including adjacent public entries.
                for candidate in candidates(line, separator_free=False):
                    for match in REPOSITORY.finditer(candidate):
                        repository = re.sub(r"\.git$", "", match[1], flags=re.IGNORECASE)
                        if repository not in allowlist["repositories"]:
                            errors.append(f"{label}:{number if start else 0}: private-repository")
                    for match in EMAIL.finditer(candidate):
                        if match[0] not in allowlist["emails"]:
                            errors.append(f"{label}:{number if start else 0}: email")
            if russian and relative not in EXEMPT:
                for line, number in match_views(body, start):
                    for rule, pattern in RUSSIAN_RULES.items():
                        if pattern.search(normalized(line)):
                            errors.append(f"{label}:{number if start and info is None else 0}: {rule}")
    return list(dict.fromkeys(redacted(error) for error in errors))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    errors = check(args.root.resolve())
    print("\n".join(errors) if errors else "Hygiene check passed")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(run_cli(main, "identifier-scan"))
