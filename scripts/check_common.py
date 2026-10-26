"""Shared fail-closed traversal for publication checks."""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRATCH = {".git", ".temp", "__pycache__", "node_modules"}


def files(root):
    if not root.is_dir():
        raise ValueError("missing publication root")

    def failed(error):
        raise error

    found = []
    for directory, names, entries in os.walk(root, onerror=failed, followlinks=False):
        names[:] = sorted(name for name in names if name not in SCRATCH)
        if any((Path(directory) / name).is_symlink() for name in names):
            raise ValueError("unsupported directory symlink")
        for name in entries:
            path = Path(directory) / name
            if path.is_symlink():
                raise ValueError("unsupported publication symlink")
            found.append(path)
    return sorted(found)
