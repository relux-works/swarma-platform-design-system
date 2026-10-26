"""Resolve local links and anchors from rendered CommonMark and HTML."""

from diagnostics import run_cli
import argparse
from pathlib import Path
from urllib.parse import unquote, urlsplit
from check_common import ROOT, files
from publication_values import documents


def anchors(text, markdown=True):
    path = Path("target.md" if markdown else "target.html")
    return set(documents([(path, text)])[path]["ids"])


def check(root):
    errors = []
    sources = [(path, path.read_text(encoding="utf-8")) for path in files(root) if path.suffix.lower() == ".md"]
    rendered = documents(sources)
    targets = {}
    for path, _ in sources:
        info = rendered[path]
        location = f"{path.relative_to(root).as_posix()}:0"
        if info.get("error"):
            errors.append(f"{location}: publication-decode")
            continue
        for link in info["links"]:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            target = ((root / unquote(url.path).lstrip("/") if url.path.startswith("/") else path.parent / unquote(url.path)) if url.path else path).resolve()
            if not target.is_relative_to(root) or not target.exists():
                errors.append(f"{location}: markdown-link: missing local target")
            elif url.fragment and target.suffix.lower() in {".md", ".html", ".htm", ".svg"}:
                if target not in targets:
                    # Markdown targets use the exact same rendered heading/HTML IDs as source documents.
                    targets[target] = set(rendered[target]["ids"]) if target in rendered else anchors(target.read_text(encoding="utf-8"), target.suffix.lower() == ".md")
                if unquote(url.fragment) not in targets[target]:
                    errors.append(f"{location}: markdown-anchor: missing local fragment")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    errors = check(parser.parse_args().root.resolve())
    print("\n".join(errors) if errors else "Markdown link check passed")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(run_cli(main, "markdown-link"))
