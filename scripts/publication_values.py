"""Decode values in the repository's publication formats, once per consumer context."""

import html
from html.parser import HTMLParser
import json
import re
from urllib.parse import unquote
from xml.etree import ElementTree
from check_common import prose
from css_syntax import publication_text

URL_ATTRIBUTES = {"href", "src", "srcset", "action", "poster"}


def attribute_values(name, value):
    yield value
    if name in URL_ATTRIBUTES:
        yield unquote(value)
    if name == "style":
        yield from publication_text(value)


class Markup(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.values, self.text, self.styles = [], [], []
        self.in_style = False

    def handle_starttag(self, tag, attrs):
        self.in_style = self.in_style or tag == "style"
        for name, value in attrs:
            if value is not None:
                self.values.extend(attribute_values(name, value))

    def handle_endtag(self, tag):
        if tag == "style":
            self.in_style = False

    def handle_data(self, data):
        (self.styles if self.in_style else self.text).append(data)

    def decoded(self):
        for style in self.styles:
            yield from publication_text(style)
        yield "".join(self.text)
        yield from self.values


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)
    elif isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from strings(item)


def decoded(path, text):
    suffix = path.suffix.lower()
    if suffix == ".json":
        yield from strings(json.loads(text))
    elif suffix == ".svg":
        root = ElementTree.fromstring(text)
        yield "".join(root.itertext())
        for element in root.iter():
            if element.tag.rsplit("}", 1)[-1] == "style":
                yield from publication_text("".join(element.itertext()))
            for name, value in element.attrib.items():
                yield from attribute_values(name.rsplit("}", 1)[-1], value)
    elif suffix == ".css":
        yield from publication_text(text)
    elif suffix in {".md", ".html", ".htm"}:
        body = prose(text) if suffix == ".md" else text
        parser = Markup()
        parser.feed(body)
        parser.close()
        yield from parser.decoded()
        if suffix == ".md":
            # Markdown entities and escaped punctuation are decoded outside source code spans/fences.
            yield html.unescape(re.sub(r"\\([!\"#$%&'()*+,\-./:;<=>?@\[\]\\^_`{|}~])", r"\1", body))
            from check_links import destination
            for match in re.finditer(r"\]\([ \t\n]*|(?m:^ {0,3}\[[^]\n]+\]:[ \t]*)", body):
                value = destination(body, match.end())
                if value is not None:
                    yield unquote(html.unescape(value))
