"""Require usable explicit CI policy without consulting a local fallback."""

import sys
from diagnostics import ci_tokens, redacted


if __name__ == "__main__":
    if not ci_tokens():
        print(redacted("configuration:0: identifier-deny-tokens: require a token with at least three visible characters"), file=sys.stderr)
        raise SystemExit(1)
