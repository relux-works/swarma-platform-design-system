"""Evaluate the accepted token stylesheet without relying on palette comments.

The contract permits :root declarations and conjunctions of the four supported
media features. Other selectors, at-rules, nesting and unresolved values reject.
Within that contract, source order, !important and var() determine effective values.
"""

from css_syntax import Token, serialize, significant, tokenize

MEDIA = {
    "prefers-color-scheme": {"light", "dark"},
    "prefers-contrast": {"no-preference", "more"},
    "prefers-reduced-transparency": {"no-preference", "reduce"},
    "forced-colors": {"none", "active"},
}


def conditions(tokens):
    compact = significant(tokens)
    if any(token.kind not in {"symbol", "word"} for token in compact):
        raise ValueError("unsupported media token")
    values = [token.value.lower() for token in compact]
    result = []
    while values:
        if len(values) < 5 or values[0] != "(" or values[2] != ":" or values[4] != ")":
            raise ValueError("unsupported media condition")
        name, value = values[1], values[3]
        if name not in MEDIA or value not in MEDIA[name]:
            raise ValueError("unsupported media feature or value")
        result.append((name, value))
        values = values[5:]
        if values:
            if values.pop(0) != "and" or not values:
                raise ValueError("unsupported media operator")
    if not result:
        raise ValueError("missing media condition")
    return result


def declarations(tokens):
    chunks, chunk, depth = [], [], 0
    for token in tokens:
        if token.kind == "symbol":
            if token.value in {"(", "["}:
                depth += 1
            elif token.value in {")", "]"}:
                depth -= 1
                if depth < 0:
                    raise ValueError("unbalanced declaration")
            elif token.value in {"{", "}"}:
                raise ValueError("nested declaration is unsupported")
            elif token.value == ";" and not depth:
                chunks.append(chunk)
                chunk = []
                continue
        chunk.append(token)
    if depth:
        raise ValueError("unbalanced declaration")
    chunks.append(chunk)
    for chunk in chunks:
        positions = [(index, token) for index, token in enumerate(chunk) if token.kind != "space"]
        if not positions:
            continue
        if len(positions) < 3 or positions[0][1].kind != "word" or positions[1][1] != Token("symbol", ":"):
            raise ValueError("unsupported declaration")
        name, value = positions[0][1].value, chunk[positions[1][0] + 1:]
        if not name.startswith("--") and name.lower() != "color-scheme":
            raise ValueError("only token and color-scheme declarations are supported")
        positions = [(index, token) for index, token in enumerate(value) if token.kind != "space"]
        important = len(positions) >= 2 and positions[-2][1] == Token("symbol", "!") and positions[-1][1].kind == "word" and positions[-1][1].value.lower() == "important"
        if important:
            value = value[:positions[-2][0]]
        if not significant(value) or any(token == Token("symbol", "!") for token in value):
            raise ValueError("invalid declaration importance or value")
        yield name, value, important


def rules(css):
    tokens = tokenize(css)
    result = []

    def block(start, end, media):
        index = start
        while index < end:
            if tokens[index].kind == "space":
                index += 1
                continue
            opening = index
            while opening < end and tokens[opening] != Token("symbol", "{"):
                if tokens[opening] in {Token("symbol", ";"), Token("symbol", "}")}:
                    raise ValueError("unsupported statement or unmatched block")
                opening += 1
            if opening == end:
                raise ValueError("missing rule block")
            level, closing = 1, opening + 1
            while closing < end and level:
                if tokens[closing] == Token("symbol", "{"):
                    level += 1
                elif tokens[closing] == Token("symbol", "}"):
                    level -= 1
                closing += 1
            if level:
                raise ValueError("unclosed rule block")
            raw_prelude = tokens[index:opening]
            prelude = significant(raw_prelude)
            if prelude[:1] == [Token("symbol", "@")]:
                if len(prelude) < 2 or raw_prelude[1].kind == "space" or prelude[1].kind not in {"word", "function"} or prelude[1].value.lower() != "media":
                    raise ValueError("unsupported at-rule")
                block(opening + 1, closing - 1, media + conditions(prelude[2:]))
            elif serialize(raw_prelude) == ":root":
                result.extend((media, name, value, important) for name, value, important in declarations(tokens[opening + 1:closing - 1]))
            else:
                raise ValueError("unsupported selector")
            index = closing

    block(0, len(tokens), [])
    return result


def effective(ruleset, environment):
    winners = {}
    for order, (media, name, value, important) in enumerate(ruleset):
        if all(environment[feature] == expected for feature, expected in media):
            if name not in winners or (important, order) >= winners[name][:2]:
                winners[name] = important, order, value

    def resolve(name, visiting):
        if name not in winners or name in visiting:
            raise ValueError("missing or cyclic token reference")
        return substitute(winners[name][2], visiting | {name})

    def substitute(tokens, visiting):
        output, index = [], 0
        while index < len(tokens):
            if tokens[index].kind == "function" and tokens[index].value.lower() == "var" and tokens[index + 1:index + 2] == [Token("symbol", "(")]:
                depth, end = 1, index + 2
                while end < len(tokens) and depth:
                    if tokens[end] == Token("symbol", "("):
                        depth += 1
                    elif tokens[end] == Token("symbol", ")"):
                        depth -= 1
                    end += 1
                if depth:
                    raise ValueError("unclosed variable reference")
                arguments = tokens[index + 2:end - 1]
                positions = [(offset, token) for offset, token in enumerate(arguments) if token.kind != "space"]
                if not positions or positions[0][1].kind != "word" or not positions[0][1].value.startswith("--"):
                    raise ValueError("unsupported variable reference")
                reference = positions[0][1].value
                if len(positions) > 1 and positions[1][1] != Token("symbol", ","):
                    raise ValueError("unsupported variable fallback")
                if reference not in winners and len(positions) > 2:
                    output.extend(substitute(arguments[positions[1][0] + 1:], visiting))
                else:
                    output.extend(resolve(reference, visiting))
                index = end
            else:
                output.append(tokens[index])
                index += 1
        return output

    return {name.removeprefix("--color-"): serialize(resolve(name, set()))
            for name in winners if name.startswith("--color-")}


def palettes(css):
    ruleset = rules(css)
    normal, reduced, forced = {}, {}, {}
    for name in ["light", "dark", "light-contrast", "dark-contrast"]:
        for transparency in [False, True]:
            for force in [False, True]:
                environment = {
                    "prefers-color-scheme": "dark" if name.startswith("dark") else "light",
                    "prefers-contrast": "more" if name.endswith("contrast") else "no-preference",
                    "prefers-reduced-transparency": "reduce" if transparency else "no-preference",
                    "forced-colors": "active" if force else "none",
                }
                label = name + ("/reduced" if transparency else "")
                target = forced if force else reduced if transparency else normal
                target[label] = effective(ruleset, environment)
    return normal, reduced, forced
