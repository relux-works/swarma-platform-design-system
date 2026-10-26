"""One redaction boundary for check output, including unexpected exceptions."""

import contextlib
import io
import os
from pathlib import Path
import re
import sys

_loaded = []


def split(text):
    return [token.strip() for token in re.split(r"[,\r\n]+", text) if token.strip()]


def deny_tokens():
    global _loaded
    _loaded = split(os.environ.get("IDENT_DENY_TOKENS", ""))
    if not _loaded:
        try:
            _loaded = split((Path.home() / ".config/swarma-site/deny-tokens.txt").read_text(encoding="utf-8"))
        except FileNotFoundError:
            pass
    return _loaded


def redacted(text):
    for token in set(_loaded + split(os.environ.get("IDENT_DENY_TOKENS", ""))):
        text = re.sub(re.escape(token), "[redacted]", text, flags=re.IGNORECASE)
    return text


def unexpected(_kind, _error, _traceback):
    # Import-time errors also fail without printing exception values, paths or tracebacks.
    sys.stderr.write(redacted("configuration:0: check-error: cannot run check\n"))


sys.excepthook = unexpected


def run_cli(main, rule):
    """Buffer complete streams so a token split between writes is still redacted."""
    output, errors = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
        try:
            try:
                deny_tokens()
            except (OSError, UnicodeError):
                print("configuration:0: identifier-deny-tokens: cannot load redaction policy", file=sys.stderr)
                code = 1
            else:
                code = main()
        except SystemExit as error:
            code = error.code if isinstance(error.code, int) else 1
        except Exception:
            print(f"configuration:0: {rule}: cannot run check", file=sys.stderr)
            code = 1
    sys.stdout.write(redacted(output.getvalue()))
    sys.stderr.write(redacted(errors.getvalue()))
    return code
