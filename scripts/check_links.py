"""Resolve local Markdown links and fragments without fetching external destinations."""

import argparse
import html
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
from check_common import ROOT, files, prose


def destination(text, start):
    """Read an angle-delimited or balanced, optionally escaped Markdown destination."""
    if text[start:start + 1] == "<":
        end = text.find(">", start + 1)
        return text[start + 1:end] if end >= 0 else None
    result, depth, index = [], 0, start
    while index < len(text):
        char = text[index]
        if char == "\\" and index + 1 < len(text):
            index += 1
            result.append(text[index])
        elif char == "(":
            depth += 1
            result.append(char)
        elif char == ")":
            if not depth:
                break
            depth -= 1
            result.append(char)
        elif char.isspace() and not depth:
            break
        else:
            result.append(char)
        index += 1
    return "".join(result) if depth == 0 else None


class IDs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.values = set()
        self.links = []

    def handle_starttag(self, tag, attrs):
        self.values.update(value for key, value in attrs if key == "id" or (tag == "a" and key == "name"))
        self.links.extend((self.getpos()[0], value) for key, value in attrs if key in {"href", "src"} and value is not None)


def anchors(text, markdown=True):
    parser = IDs()
    parser.feed(prose(text) if markdown else text)
    found, counts = parser.values, {}
    if not markdown:
        return found
    previous = ""
    for line in prose(text, inline=False).splitlines():
        heading = re.match(r"^ {0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        value = heading[1] if heading else previous if re.fullmatch(r" {0,3}(?:=+|-+)\s*", line) else None
        if value:
            value = re.sub(r"<[^>]+>", "", html.unescape(value)).lower()
            value = re.sub(r"!?\[([^]]+)\]\([^)]*\)", r"\1", value)
            slug = re.sub(r"[^\w\- ]", "", value).replace(" ", "-")
            count = counts.get(slug, 0)
            counts[slug] = count + 1
            found.add(f"{slug}-{count}" if count else slug)
        previous = line.strip()
    return found


def check(root):
    errors = []
    for path in files(root):
        if path.suffix.lower() != ".md":
            continue
        body = prose(path.read_text(encoding="utf-8"))
        references = {}
        links = []
        for match in re.finditer(r"(?m)^ {0,3}\[([^]\n]+)\]:[ \t]*", body):
            value = destination(body, match.end())
            references[" ".join(match[1].casefold().split())] = value
            links.append((match.start(), value))
        for match in re.finditer(r"(?<!\\)\]\([ \t\n]*", body):
            links.append((match.start(), destination(body, match.end())))
        for match in re.finditer(r"\[([^]\n]+)\](?:\[([^]\n]*)\])?", body):
            key = " ".join((match[2] or match[1]).casefold().split())
            if match[2] is not None or key in references:
                links.append((match.start(), references.get(key)))
        parser = IDs()
        parser.feed(body)
        lines = body.splitlines(keepends=True)
        links.extend((sum(map(len, lines[:number - 1])), value) for number, value in parser.links)
        for offset, link in links:
            location = f"{path.relative_to(root).as_posix()}:{body.count(chr(10), 0, offset) + 1}"
            if link is None:
                errors.append(f"{location}: markdown-link: undefined or malformed destination")
                continue
            url = urlsplit(html.unescape(link))
            if url.scheme or url.netloc:
                continue
            target = (root / unquote(url.path).lstrip("/") if url.path.startswith("/") else path.parent / unquote(url.path)) if url.path else path
            target = target.resolve()
            if not target.is_relative_to(root) or not target.exists():
                errors.append(f"{location}: markdown-link: missing local target")
            elif url.fragment and target.suffix.lower() in {".md", ".html", ".htm", ".svg"}:
                if unquote(url.fragment) not in anchors(target.read_text(encoding="utf-8"), target.suffix.lower() == ".md"):
                    errors.append(f"{location}: markdown-anchor: missing local fragment")
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    errors = check(parser.parse_args().root.resolve())
    print("\n".join(errors) if errors else "Markdown link check passed")
    raise SystemExit(bool(errors))
