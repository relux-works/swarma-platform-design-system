"""Reject internal identifiers and forbidden punctuation in Russian Markdown prose."""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from xml.etree.ElementTree import ParseError
from check_common import ROOT, files, prose
from hygiene_rules import EMAIL, IDENTIFIERS, INVOCATION_FILES, PUBLIC_INVOCATION, REPOSITORY, RUSSIAN, RUSSIAN_RULES
from publication_values import decoded

# Only generic policy definitions and the isolated controls have generic-rule exemptions.
EXEMPT = {"scripts/hygiene_rules.py", "scripts/tests/test_ci.py"}


def deny_tokens():
    def split(text):
        return [token.strip() for token in re.split(r"[,\r\n]+", text) if token.strip()]
    tokens = split(os.environ.get("IDENT_DENY_TOKENS", ""))
    if tokens:
        return tokens
    try:
        return split((Path.home() / ".config" / "swarma-site" / "deny-tokens.txt").read_text(encoding="utf-8"))
    except FileNotFoundError:
        return []


def check(root):
    errors = []
    try:
        tokens = deny_tokens()
    except (OSError, UnicodeError):
        tokens = []
        errors.append("configuration:0: identifier-deny-tokens")
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
        for token in tokens:
            value = re.sub(re.escape(token), "[redacted]", value, flags=re.IGNORECASE)
        return value

    for path in files(root):
        relative = path.relative_to(root).as_posix()
        label = redacted(relative)
        if any(token.lower() in relative.lower() for token in tokens):
            errors.append(f"{label}:0: deny-token")
        if relative not in EXEMPT:
            for rule, pattern in IDENTIFIERS.items():
                if pattern.search(relative):
                    errors.append(f"{label}:0: {rule}")
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            if path.suffix.lower() in {".json", ".svg", ".css", ".md", ".html", ".htm"}:
                errors.append(f"{label}:0: publication-decode")
            continue  # Binary artwork is not prose or source text; filenames remain checked.
        body = prose(text) if path.suffix.lower() == ".md" else text
        views = [(text, body, 1)]
        try:
            views.extend((value, value, 0) for value in decoded(path, text))
        except (ValueError, ParseError):
            errors.append(f"{label}:0: publication-decode")
        russian = any(RUSSIAN.search(body) for _, body, _ in views)
        for value, body, start in views:
            # External literals are forbidden even in the exempt policy and control sources.
            for number, line in enumerate(value.splitlines(), start):
                if any(token.lower() in line.lower() for token in tokens):
                    errors.append(f"{label}:{number if start else 0}: deny-token")
                if relative in EXEMPT:
                    continue
                for rule, pattern in IDENTIFIERS.items():
                    candidate = PUBLIC_INVOCATION.sub("", line) if rule == "matrix-event" and relative in INVOCATION_FILES else line
                    if pattern.search(candidate):
                        errors.append(f"{label}:{number if start else 0}: {rule}")
                for match in REPOSITORY.finditer(line):
                    repository = re.sub(r"\.git$", "", match[1], flags=re.IGNORECASE)
                    if repository not in allowlist["repositories"]:
                        errors.append(f"{label}:{number if start else 0}: private-repository")
                for match in EMAIL.finditer(line):
                    if match[0] not in allowlist["emails"]:
                        errors.append(f"{label}:{number if start else 0}: email")
            if russian and relative not in EXEMPT:
                for number, line in enumerate(body.splitlines(), start):
                    for rule, pattern in RUSSIAN_RULES.items():
                        if pattern.search(line):
                            errors.append(f"{label}:{number if start else 0}: {rule}")
    return list(dict.fromkeys(errors))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    errors = check(args.root.resolve())
    print("\n".join(errors) if errors else "Hygiene check passed")
    raise SystemExit(bool(errors))
