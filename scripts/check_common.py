"""Shared repository traversal and prose handling for dependency-free checks."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SCRATCH = {".git", ".temp", "__pycache__"}


def files(root):
    return sorted(p for p in root.rglob("*")
                  if p.is_file() and not any(part in SCRATCH for part in p.relative_to(root).parts))


def prose(text, inline=True):
    """Omit fenced and inline code while retaining line positions for diagnostics."""
    lines = []
    fence = None
    for line in text.splitlines(keepends=True):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence):
                fence = None
            lines.append("\n" if line.endswith("\n") else "")
        elif marker:
            fence = marker[1]
            lines.append("\n" if line.endswith("\n") else "")
        else:
            lines.append(line)
    text = "".join(lines)
    return re.sub(r"(`+)(.*?)\1", lambda m: re.sub(r"[^\n]", " ", m[0]), text, flags=re.S) if inline else text
