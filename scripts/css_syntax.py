"""Small CSS lexer shared by publication decoding and the restricted token cascade.

Escapes follow CSS Syntax: up to six hex digits, optional following whitespace,
and escaped string newlines. This does not attempt browser error recovery.
"""

from dataclasses import dataclass
import re
from urllib.parse import unquote


@dataclass(frozen=True)
class Token:
    kind: str
    value: str


def escape(source, index, string=False):
    index += 1
    if index >= len(source):
        raise ValueError("incomplete CSS escape")
    if source[index] == "\n":
        if not string:
            raise ValueError("newline in CSS identifier escape")
        return "", index + 1
    match = re.match(r"[0-9a-fA-F]{1,6}", source[index:])
    if match:
        value = int(match[0], 16)
        character = chr(value) if 0 < value <= 0x10ffff and not 0xd800 <= value <= 0xdfff else "\ufffd"
        index += len(match[0])
        if source[index:index + 1] in {" ", "\t", "\n", "\f"}:
            index += 1
        return character, index
    return source[index], index + 1


def tokenize(source):
    source = source.replace("\r\n", "\n").replace("\r", "\n").replace("\f", "\n").replace("\0", "\ufffd")
    tokens, index = [], 0
    while index < len(source):
        character = source[index]
        if source.startswith("/*", index):
            end = source.find("*/", index + 2)
            if end < 0:
                raise ValueError("unterminated CSS comment")
            index = end + 2
        elif character.isspace():
            end = index + 1
            while end < len(source) and source[end].isspace():
                end += 1
            tokens.append(Token("space", source[index:end]))
            index = end
        elif character in {"'", '"'}:
            quote, value = character, []
            index += 1
            while index < len(source) and source[index] != quote:
                if source[index] == "\n":
                    raise ValueError("newline in CSS string")
                if source[index] == "\\":
                    character, index = escape(source, index, string=True)
                else:
                    character, index = source[index], index + 1
                value.append(character)
            if index >= len(source):
                raise ValueError("unterminated CSS string")
            index += 1
            tokens.append(Token("string", "".join(value)))
        elif character.isalnum() or character in {"-", "_", "\\"} or ord(character) >= 128:
            value = []
            while index < len(source):
                character = source[index]
                if character == "\\":
                    character, index = escape(source, index)
                elif character.isalnum() or character in {"-", "_"} or ord(character) >= 128:
                    index += 1
                else:
                    break
                value.append(character)
            tokens.append(Token("function" if source[index:index + 1] == "(" else "word", "".join(value)))
        else:
            tokens.append(Token("symbol", character))
            index += 1
    return tokens


def significant(tokens):
    return [token for token in tokens if token.kind != "space"]


def serialize(tokens):
    output, previous = [], None
    for token in tokens:
        if previous and previous.kind == "word" and (token.kind in {"word", "function"} or token == Token("symbol", "(")):
            output.append(" ")  # Comments cannot merge independent lexical tokens into a new color/function.
        output.append(('"' + token.value.replace("\\", "\\\\").replace('"', '\\"') + '"')
                      if token.kind == "string" else token.value)
        previous = token
    return "".join(output).strip()


def publication_text(source):
    # Adjacent CSS string tokens concatenate when used for generated content.
    tokens = tokenize(source)
    values, group = [serialize(tokens)], []
    for index, token in enumerate(tokens):
        if token.kind == "function" and token.value.lower() == "url":
            end = index + 2
            while end < len(tokens) and tokens[end] != Token("symbol", ")"):
                end += 1
            argument = significant(tokens[index + 2:end])
            value = argument[0].value if len(argument) == 1 and argument[0].kind == "string" else serialize(argument)
            values.append(unquote(value))
    for token in tokens:
        if token.kind == "string":
            group.append(token.value)
        elif token.kind != "space" and group:
            values.append("".join(group))
            group = []
    if group:
        values.append("".join(group))
    return values
