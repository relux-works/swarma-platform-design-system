#!/usr/bin/env python3
"""Measure semantic token contrast using Chromium's computed styles.

The stylesheet is loaded unchanged in a local fixture. Every pair and appearance
is rendered by Playwright; Python composites the computed sRGB colors and writes
the existing four-palette report. The control adds one known failing value only
to the fixture DOM. No CSS declarations are parsed for color values.
"""

from diagnostics import run_cli
import argparse
import json
import os
from pathlib import Path
import subprocess
import re
import sys
from check_common import ROOT

PALETTES = ["light", "dark", "light-contrast", "dark-contrast"]
SURFACES = ["bg", "surface-subtle", "surface", "surface-raised", "surface-hover"]
ROLES = ["human", "agent", "service", "store", "key", "external", "alert", "neutral"]
STATUSES = ["now", "decided", "proposed", "spec", "open"]

# Targets: (normal appearance, increased-contrast appearance).
TEXT = (4.5, 7.0)
NON_TEXT = (3.0, 3.0)


def forced_roles():
    groups = {
        "Canvas": SURFACES + ["figure-ground", "text-inverse", "on-accent", "scrim", "material"],
        "CanvasText": ["brand-red", "brand-ink", "brand-white", "text", "text-muted", "text-faint",
                       "border", "border-strong", "divider", "success", "warning", "error", "info", "figure-frame"],
        "ButtonFace": ["control", "control-hover", "strong-action", "strong-action-hover"],
        "ButtonText": ["control-text", "on-strong-action"],
        "Highlight": ["control-pressed", "focus", "selection-bg"],
        "HighlightText": ["selection-text", "control-text-pressed"],
        "LinkText": ["accent", "accent-hover", "accent-pressed", "link", "link-hover"],
        "transparent": ["accent-soft"],
    }
    groups["Canvas"] += [f"role-{role}-fill" for role in ROLES] + [f"status-{status}-bg" for status in STATUSES]
    groups["CanvasText"] += [f"role-{role}-{part}" for role in ROLES for part in ["stroke", "text"]]
    groups["CanvasText"] += [f"status-{status}-text" for status in STATUSES]
    return {key: color.lower() for color, keys in groups.items() for key in keys}


def validate(palettes):
    required = set(forced_roles())
    for tokens in palettes.values():
        if not required <= tokens.keys():
            raise ValueError("missing semantic color token")
        for value in tokens.values():
            to_rgba(value)
        if to_rgba(tokens["bg"])[3] != 1:
            raise ValueError("root background must be opaque")


def to_rgba(value):
    value = value.strip().lower()
    if re.fullmatch(r"#[0-9a-f]{6}", value):
        return tuple(int(value[i:i + 2], 16) / 255 for i in (1, 3, 5)) + (1.0,)
    match = re.fullmatch(r"rgba?\(\s*([\d.]+),\s*([\d.]+),\s*([\d.]+)(?:,\s*([\d.]+))?\s*\)", value)
    if match:
        r, g, b, a = match.groups()
        a = a or "1"
        if all(0 <= float(channel) <= 255 for channel in (r, g, b)) and 0 <= float(a) <= 1:
            return (float(r) / 255, float(g) / 255, float(b) / 255, float(a))
    raise ValueError("unsupported or invalid color value")


def over(fg, bg):
    a = fg[3]
    return tuple(f * a + b * (1 - a) for f, b in zip(fg[:3], bg[:3]))


def luminance(rgb):
    channels = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def ratio(a, b):
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def pairs():
    """Yield (label, foreground token, background token, targets)."""
    for fg in ["text", "text-muted", "text-faint"]:
        for bg in SURFACES:
            yield f"{fg} on {bg}", fg, bg, TEXT
    for fg in ["accent", "accent-hover", "link", "link-hover"]:
        for bg in SURFACES:
            yield f"{fg} on {bg}", fg, bg, TEXT
    for fg in ["focus", "border-strong"]:
        for bg in SURFACES:
            yield f"{fg} on {bg}", fg, bg, NON_TEXT
    for fg in ["success", "warning", "error", "info"]:
        for bg in SURFACES:
            yield f"{fg} on {bg}", fg, bg, TEXT
    yield "on-accent on accent", "on-accent", "accent", TEXT
    yield "on-accent on accent-hover", "on-accent", "accent-hover", TEXT
    yield "on-strong-action on strong-action", "on-strong-action", "strong-action", TEXT
    yield "on-strong-action on strong-action-hover", "on-strong-action", "strong-action-hover", TEXT
    for bg in ["control", "control-hover"]:
        yield f"control-text on {bg}", "control-text", bg, TEXT
    yield "control-text-pressed on control-pressed", "control-text-pressed", "control-pressed", TEXT
    yield "selection-text on selection-bg", "selection-text", "selection-bg", TEXT
    yield "text on accent-soft", "text", "accent-soft", TEXT
    yield "accent on accent-soft", "accent", "accent-soft", TEXT
    for role in ROLES:
        yield f"role-{role}-text on role-{role}-fill", f"role-{role}-text", f"role-{role}-fill", TEXT
        for bg in SURFACES:
            yield f"role-{role}-text on {bg}", f"role-{role}-text", bg, TEXT
        yield f"role-{role}-stroke on role-{role}-fill", f"role-{role}-stroke", f"role-{role}-fill", NON_TEXT
        for bg in SURFACES:
            yield f"role-{role}-stroke on {bg}", f"role-{role}-stroke", bg, NON_TEXT
    for status in STATUSES:
        yield (f"status-{status}-text on status-{status}-bg", f"status-{status}-text",
               f"status-{status}-bg", TEXT)


def measure(tokens, control):
    modes = []
    for forced in [False, True]:
        for reduced in [False, True]:
            for palette in PALETTES:
                modes.append({"name": palette + ("/reduced" if reduced else "") + ("/forced" if forced else ""),
                              "scheme": "dark" if palette.startswith("dark") else "light",
                              "contrast": "more" if palette.endswith("contrast") else "no-preference",
                              "reduced": "reduce" if reduced else "no-preference",
                              "forced": "active" if forced else "none"})
    payload = {"tokens": str(Path(tokens).resolve()), "modes": modes, "roles": forced_roles(), "control": control,
               "pairs": [{"fg": fg, "bg": bg} for _, fg, bg, _ in pairs()]}
    environment = {key: value for key, value in os.environ.items() if key != "IDENT_DENY_TOKENS"}
    result = subprocess.run(["node", str(ROOT / "scripts/measure-contrast.mjs")], input=json.dumps(payload),
                            capture_output=True, text=True, timeout=90, env=environment)
    if result.returncode:
        raise ValueError("contrast-browser")
    output = json.loads(result.stdout)
    if output.get("error") or len(output.get("appearances", [])) != len(modes):
        raise ValueError("contrast-browser")
    return output


def check(appearances):
    results = []
    for appearance in appearances:
        name, colors = appearance["name"], appearance["colors"]
        root = to_rgba(colors["bg"])
        if root[3] != 1:
            raise ValueError("root background must be opaque")
        for (label, _, _, targets), computed in zip(pairs(), appearance["pairs"], strict=True):
            target = targets[1] if name.split("/")[0].endswith("contrast") else targets[0]
            back = to_rgba(computed["background"])
            back_rgb = over(back, root) if back[3] < 1 else back[:3]
            fore = to_rgba(computed["foreground"])
            fore_rgb = over(fore, back_rgb + (1.0,)) if fore[3] < 1 else fore[:3]
            value = ratio(fore_rgb, back_rgb)
            results.append((name, label, value, target, value + 1e-9 >= target))
    return results


def informational(palettes):
    """Ratios that are recorded, not gated: they justify non-colour rules."""
    rows = []
    for name in PALETTES:
        tokens = palettes[name]
        rows.append((name, "link against text (links are underlined)",
                     ratio(to_rgba(tokens["link"])[:3], to_rgba(tokens["text"])[:3])))
        rows.append((name, "accent against info (info always carries a label)",
                     ratio(to_rgba(tokens["accent"])[:3], to_rgba(tokens["info"])[:3])))
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("tokens", nargs="?", default="assets/tokens.css")
    parser.add_argument("--report", help="write a Markdown report to this path")
    parser.add_argument("--control", action="store_true",
                        help="inject a known failing value; the run must exit 1")
    args = parser.parse_args()

    try:
        measured = measure(args.tokens, args.control)
        appearances = measured["appearances"]
        palettes = {item["name"]: item["colors"] for item in appearances if item["name"] in PALETTES}
        validate(palettes)
        results = check(appearances)
        report_results = [row for row in results if row[0] in PALETTES]
        expected = forced_roles()
        forced = [item for item in appearances if item["forced"]]
        forced_failures = [item["name"] for item in forced
                           if any(item["colors"][key] != item["system"][role] for key, role in expected.items())]
    except (ValueError, KeyError):
        print("contrast-browser: cannot measure semantic colors")
        return 1
    failures = [row for row in results if not row[4]]

    lines = [f"browser: Chromium {measured['browser']}"]
    for name, label, value, target, ok in results:
        lines.append(f"{'PASS' if ok else 'FAIL'} {name:15s} {label:45s} {value:6.2f} (target {target})")
    for name, label, value in informational(palettes):
        lines.append(f"INFO {name:15s} {label:45s} {value:6.2f}")
    for item in forced:
        name = item["name"]
        lines.append(f"{'FAIL' if name in forced_failures else 'PASS'} {name:32s} forced-color-role")
    lines.append(f"pairs: {len(results)}, failures: {len(failures)}, forced-color failures: {len(forced_failures)}")
    print("\n".join(lines))

    if args.report and not args.control and not failures and not forced_failures:
        import io
        with io.StringIO() as out:
            out.write("# Contrast report\n\n")
            out.write("Generated by `node scripts/run.mjs python3 scripts/check_contrast.py assets/tokens.css "
                      "--report references/contrast-report.md`. Do not edit by hand.\n\n")
            out.write("WCAG 2.x relative luminance. Targets: text 4.5:1 (7:1 in the more-contrast "
                      "palettes), non-text 3:1. Translucent tokens are composited over `--color-bg`.\n\n")
            out.write("Colors are measured with Chromium getComputedStyle. All 16 appearances must pass; "
                      "this report records the four base palettes. Forced-color control pairs are "
                      "ButtonText on ButtonFace (default/hover) and HighlightText on Highlight (pressed). "
                      "Their browser/OS-dependent ratios are checked and printed on each run.\n\n")
            out.write(f"Pairs checked: {len(report_results)}. Failures: 0.\n\n")
            for name in PALETTES:
                out.write(f"## {name}\n\n| Pair | Ratio | Target | Result |\n| --- | ---: | ---: | --- |\n")
                for p_name, label, value, target, ok in report_results:
                    if p_name == name:
                        out.write(f"| {label} | {value:.2f} | {target} | {'pass' if ok else 'FAIL'} |\n")
                for p_name, label, value in informational(palettes):
                    if p_name == name:
                        out.write(f"| {label} | {value:.2f} | recorded | info |\n")
                out.write("\n")
            text = out.getvalue().rstrip("\n") + "\n"
        with open(args.report, "w", encoding="utf-8") as handle:
            handle.write(text)
    return 1 if failures or forced_failures else 0


if __name__ == "__main__":
    sys.exit(run_cli(main, "contrast-browser"))
