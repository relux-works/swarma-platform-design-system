"""Canonical publication matching and redaction, retaining paragraph boundaries."""

import re

# Include non-spacing format characters commonly introduced by editing and copy/paste.
SEPARATORS = r"[\s\u180e\u200b-\u200d\u2060\ufeff]"
SPACES = re.compile(SEPARATORS + "+")
PARAGRAPH = re.compile(r"\n[\t \r]*\n+")


def normalized(value):
    return SPACES.sub(" ", value).strip()


def compact(value):
    return SPACES.sub("", value)


def token_match(value, tokens):
    normal, joined = normalized(value).casefold(), compact(value).casefold()
    return any(normalized(token).casefold() in normal or compact(token).casefold() in joined
               for token in tokens if compact(token))


def match_views(value, start=0):
    """Retain source locations for individual lines; joined paragraph views have line zero."""
    lines = [(line, number if start else 0) for number, line in enumerate(value.splitlines(), start)]
    paragraphs = [(part, 0) for part in PARAGRAPH.split(value) if part.strip()]
    return list(dict.fromkeys((normalized(part), line) for part, line in lines + paragraphs if part.strip()))


def redact(value, tokens):
    # Map the same separator-free casefold used by the verdict back to original character spans.
    folded, positions = [], []
    for index, letter in enumerate(value):
        if not SPACES.fullmatch(letter):
            units = letter.casefold()
            folded.extend(units)
            positions.extend([index] * len(units))
    joined, spans = "".join(folded), []
    for token in set(tokens):
        needle, offset = compact(token).casefold(), 0
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
