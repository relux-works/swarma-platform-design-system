"""Require usable explicit CI policy without consulting a local fallback."""

import sys
from diagnostics import ci_tokens


if __name__ == "__main__":
    try:
        ci_tokens()
    except ValueError:
        print("configuration:0: identifier-deny-tokens", file=sys.stderr)
        raise SystemExit(1)
