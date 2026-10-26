"""Canonical publication matching and redaction, retaining paragraph boundaries."""

import re
import unicodedata

SPACES = re.compile(r"\s+")
PARAGRAPH = re.compile(r"\n[\t \r]*\n+")


def unformatted(value):
    return "".join(letter for letter in value if unicodedata.category(letter) != "Cf")


def normalized(value):
    return SPACES.sub(" ", unformatted(value)).strip()


def compact(value):
    return SPACES.sub("", unformatted(value))


def ascii_fold(value):
    return value.translate(str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"))


def candidates(value, *, separator_free=True):
    # Preserve word boundaries around a wrapped identifier before also trying the fully compact form.
    unwrapped = re.sub(r"[ \t]*\r?\n[ \t]*", "", unformatted(value))
    views = (normalized(value), normalized(unwrapped))
    return tuple(dict.fromkeys(views + ((compact(value),) if separator_free else ())))


def token_match(value, tokens):
    normal, joined = ascii_fold(normalized(value)), ascii_fold(compact(value))
    return any(ascii_fold(normalized(token)) in normal or ascii_fold(compact(token)) in joined
               for token in tokens if compact(token))


def match_views(value, start=0, *, join_lines=True):
    """Retain source locations for individual lines; joined paragraph views have line zero."""
    lines = [(line, number if start else 0) for number, line in enumerate(value.splitlines(), start)]
    paragraphs = [(part, 0) for part in PARAGRAPH.split(value) if part.strip()] if join_lines else []
    return list(dict.fromkeys((part, line) for part, line in lines + paragraphs if part.strip()))


def redact(value, tokens):
    # Map the same separator-free ASCII comparison back to original character spans.
    folded, positions = [], []
    for index, letter in enumerate(value):
        if compact(letter):
            units = ascii_fold(letter)
            folded.extend(units)
            positions.extend([index] * len(units))
    joined, spans = "".join(folded), []
    for token in set(tokens):
        needle, offset = ascii_fold(compact(token)), 0
        if not needle:
            continue
        while (found := joined.find(needle, offset)) >= 0:
            spans.append((positions[found], positions[found + len(needle) - 1] + 1))
            offset = found + 1
    merged = []
    for start, end in sorted(spans):
        if merged and start < merged[-1][1]:
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    for start, end in reversed(merged):
        value = value[:start] + "[redacted]" + value[end:]
    return value
