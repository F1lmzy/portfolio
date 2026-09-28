#!/usr/bin/env python3
"""Build static/themes.css and static/themes.json from the vendored Monkeytype sources.

Inputs (vendored, do not hand-edit):
  data/monkeytype_themes/themes.ts   upstream frontend/src/ts/constants/themes.ts
  data/monkeytype_themes/*.css       upstream frontend/static/themes/<name>.css (52 files)

Outputs (generated, do not hand-edit):
  static/themes.css   [data-theme="<name>"] blocks: the 10 Monkeytype colour tokens,
                      plus ported versions of each theme's custom CSS.
  static/themes.json  [{name, hasCss, fx, swatch}] for the picker.

Every theme gets its exact upstream colour tokens. Themes whose upstream CSS only
restyles Monkeytype chrome are ported through SELECTOR_MAP; a selector this site
cannot honour is dropped individually (selector lists are split first, so one
unknown target never takes a whole rule with it).
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "monkeytype_themes"
OUT_CSS = ROOT / "static" / "themes.css"
OUT_JSON = ROOT / "static" / "themes.json"

TOKENS = [
    "bg", "main", "caret", "sub", "subAlt", "text",
    "error", "errorExtra", "colorfulError", "colorfulErrorExtra",
]
VAR = {
    "bg": "--bg", "main": "--main", "caret": "--caret", "sub": "--sub",
    "subAlt": "--sub-alt", "text": "--text", "error": "--error",
    "errorExtra": "--error-extra", "colorfulError": "--colorful-error",
    "colorfulErrorExtra": "--colorful-error-extra",
}
VAR_RENAME = {
    "--bg-color": "--bg",
    "--main-color": "--main",
    "--caret-color": "--caret",
    "--sub-color": "--sub",
    "--sub-alt-color": "--sub-alt",
    "--text-color": "--text",
    "--error-color": "--error",
    "--error-extra-color": "--error-extra",
    "--colorful-error-color": "--colorful-error",
    "--colorful-error-extra-color": "--colorful-error-extra",
}

# Monkeytype nav slots -> this site's nav items. Applied by a function, in one pass.
NAV_MAP = {
    "test": "about",
    "leaderboards": "publications",
    "about": "projects",
    "settings": "experience",
    "alerts": "themes",
    "account": "contact",
    "login": "contact",
}

# Exact-substring selector renames, longest key matched first.
SELECTOR_MAP = {
    '[data-ui-element="logoText"]': ".brand-name",
    '[data-ui-element="logoSubtext"]': ".brand-sub",
    # the preview pane reproduces the same markup outside <header>, so drop the
    # header scoping once the logo hooks have been rewritten
    ".site-header .brand-name": ".brand-name",
    ".site-header .brand-sub": ".brand-sub",
    '[data-ui-element="logo"]:hover h1': ".brand:hover",
    '[data-ui-element="logo"]:hover': ".brand:hover",
    '[data-ui-element="logo"] h1': ".brand",
    '[data-ui-element="logo"] > div': ".brand-inner",
    '[data-ui-element="logo"]': ".brand",
    "a:not(.button):not([data-ui-variant=\"button\"]):hover": "a:hover",
    "a:not([data-ui-variant=\"button\"]):hover": "a:hover",
    "button.text:hover, .button.text:hover, .textButton:hover, "
    "button[data-ui-variant=\"text\"]:hover": "a:hover",
    "button.text.active, .button.text.active, .textButton.active": ".filter-nav a.active",
    "button.text:hover, .textButton:hover": "a:hover",
    ".row .textButton:not(.active)": ".filter-nav a:not(.active)",
    ".textButton": ".filter-nav a",
    "input[type=\"button\"]": "button",
    "input[type=\"reset\"]": "button",
    "input[type=\"submit\"]": "button",
    ".button": "button",
    ".row": ".listing",
    "header": ".site-header",
}

# A selector part containing any of these is dropped: no such element here.
DROP_TOKENS = [
    "#words", ".word", "letter", ".pageSettings", ".pageAccount", "#result",
    ".view-account", ".levelAndBar", ".xpBar", "data-focused", "crtmode",
    "#restartTestButton", "#showWordHistoryButton", "#saveScreenshotButton",
    "#nextTestButton", "#watchReplayButton", "#watchVideoAdButton",
    "#practiseWordsButton", ".scrollToTopButton", ".afk", ".timeToday",
    ".discord", "navAvatar", "notificationBubble", "userLevel", "accountMenu",
    "testConfig", "aria-label", "balloon", "logoIcon",
    "::before", "::after", "> i", "svg", "input", "textarea", "select",
    ".incorrect", ".error", ".activeWord",
    ":root", "commandLine", ".colorfulMode", ".pageAbout", ".modal",
    "body {", "html {",
    # the page has no blinking caret element, so a theme's caret styling goes too
    "#caret",
]

DROP_DECL_PROPS = [
    "--themable-button", "--nav-focus-opacity", "--correct-letter",
    "--untyped-letter", "--incorrect-letter", "--extra-letter", "--crt-",
    "--roundness", "--theme-bg-stripe", "--current-color", "--bg-color-stripe",
]
FX_HINT = re.compile(
    r"animation|@keyframes|linear-gradient|text-shadow|rotateY|10rem", re.I
)
ALLOWED_NAV_ATTR = re.compile(r'\[data-nav-item="[a-z]+"\]')


# ---------------------------------------------------------------- ts parsing

def parse_themes_ts(text: str) -> dict[str, dict]:
    anchor = "export const themes: Record<ThemeName, Theme> = "
    start = text.index(anchor) + len(anchor)
    depth, end = 0, None
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    if end is None:
        raise SystemExit("could not find the end of the themes object")
    body = text[start + 1:end]

    themes: dict[str, dict] = {}
    pat = re.compile(r"[\"']?([A-Za-z0-9_-]+)[\"']?\s*:\s*\{")
    i = 0
    while True:
        m = pat.search(body, i)
        if not m:
            break
        j, d = m.end() - 1, 0
        while j < len(body):
            if body[j] == "{":
                d += 1
            elif body[j] == "}":
                d -= 1
                if d == 0:
                    break
            j += 1
        block = body[m.end():j]
        theme: dict = {}
        for k, v in re.findall(
            r"[\"']?(\w+)[\"']?\s*:\s*(true|false|\"#[0-9a-fA-F]{3,8}\"|'#[0-9a-fA-F]{3,8}')",
            block,
        ):
            theme[k] = True if v == "true" else False if v == "false" else v.strip("\"'")
        themes[m.group(1)] = theme
        i = j + 1
    return themes


# --------------------------------------------------------- css block walking

def strip_comments(css: str) -> str:
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def split_body(body: str) -> tuple[str, list[tuple[str, str]]]:
    """Split a rule body into (declarations text, [(prelude, inner body), ...]).

    A nested block's selector may sit right after the parent's last declaration
    (`color: red; &:hover { ... }`), so the pending text is split at its last
    semicolon: everything before it is declarations, the tail is the selector.
    """
    decls, blocks, buf, i = [], [], [], 0
    while i < len(body):
        ch = body[i]
        if ch == "{":
            pending = "".join(buf)
            buf = []
            if ";" in pending:
                head, _, tail = pending.rpartition(";")
                decls.append(head + ";")
                prelude = tail.strip()
            else:
                prelude = pending.strip()
            depth, j = 1, i + 1
            while j < len(body) and depth:
                if body[j] == "{":
                    depth += 1
                elif body[j] == "}":
                    depth -= 1
                j += 1
            blocks.append((prelude, body[i + 1:j - 1]))
            i = j
            continue
        if ch == "}":
            i += 1
            continue
        buf.append(ch)
        i += 1
    decls.append("".join(buf))
    return "".join(decls), blocks


def parse_decls(text: str) -> list[tuple[str, str]]:
    decls = []
    for part in text.split(";"):
        if ":" not in part:
            continue
        prop, _, val = part.partition(":")
        prop, val = prop.strip(), val.strip()
        if not prop or not val or prop.startswith("@"):
            continue
        decls.append((prop, re.sub(r"\s+", " ", val)))
    return decls


def rename_vars(text: str) -> str:
    for old, new in VAR_RENAME.items():
        text = text.replace(old, new)
    return text


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    h = value.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) == 4:  # #rgba
        h = "".join(c * 2 for c in h[:3])
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def relative_luminance(rgb: tuple[int, int, int]) -> float:
    def channel(v: int) -> float:
        v = v / 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg: str, bg: str) -> float:
    a, b = relative_luminance(hex_to_rgb(fg)), relative_luminance(hex_to_rgb(bg))
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


def _srgb_to_linear(v: float) -> float:
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(v: float) -> float:
    return v * 12.92 if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055


def hex_to_oklch(value: str) -> tuple[float, float, float]:
    """sRGB hex to (lightness, chroma, hue) in OKLCH."""
    r, g, b = (_srgb_to_linear(v / 255) for v in hex_to_rgb(value))
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = (c ** (1 / 3) if c >= 0 else -((-c) ** (1 / 3)) for c in (l, m, s))
    L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    bb = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return L, math.hypot(a, bb), math.atan2(bb, a)


def _oklch_to_rgb(L: float, a: float, b: float) -> tuple[float, float, float]:
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    return (
        4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    )


CHROMA_CAP = 1.5


def _at(L: float, C: float, H: float, cap: float = CHROMA_CAP) -> str | None:
    """The colour at this lightness: chroma as high as sRGB allows at that
    lightness, never more than `cap` times the theme's own.

    A colour that has to move in lightness should not lose its colour on the way.
    Darkening serika's yellow for a light background can support *more* chroma than
    the original, and using it is the difference between a gold heading and mud.
    The cap exists so a nearly grey theme is not handed saturation it never had.
    """
    if not 0.0 <= L <= 1.0:
        return None
    a, b = C * math.cos(H), C * math.sin(H)
    lo, hi = 0.0, cap  # in-gamut chroma is a single interval from 0, so bisect it
    for _ in range(24):
        mid = (lo + hi) / 2
        if all(-1e-4 <= v <= 1 + 1e-4 for v in _oklch_to_rgb(L, a * mid, b * mid)):
            lo = mid
        else:
            hi = mid
    # achromatic is in gamut for every lightness, so this always has a fallback:
    # it is what keeps white and black reachable at the ends of a search
    return _hex_of(_oklch_to_rgb(L, a * lo, b * lo))


def _hex_of(rgb: tuple[float, float, float]) -> str:
    return "#%02x%02x%02x" % tuple(
        max(0, min(255, round(_linear_to_srgb(max(0.0, min(1.0, v))) * 255)))
        for v in rgb
    )


def lift(colour: str, bg: str, target: float = 4.5) -> str:
    """Move a colour's lightness until it clears `target` against `bg`, keeping its
    hue and as much chroma as the sRGB gamut allows.

    Mixing toward white or black desaturates, and that is what made 187 very
    different themes converge on the same washed grey. Correcting in OKLCH instead
    means a theme's own colour survives: when serika's yellow has to darken to be
    readable on serika's light grey, it stays yellow rather than turning mud. Only
    lightness moves, only as far as the target needs, and the direction is chosen by
    measurement rather than assumption: honey's background #f2aa00 is a saturated
    mid-tone where black reaches 10:1 but white only 2:1.
    """
    if contrast(colour, bg) >= target:
        return colour
    L, C, H = hex_to_oklch(colour)
    reachable: list[tuple[float, str]] = []
    for lighten in (True, False):
        end = _at(1.0 if lighten else 0.0, C, H)
        if not end or contrast(end, bg) < target:
            continue
        lo, hi = (L, 1.0) if lighten else (0.0, L)
        for _ in range(28):
            mid = (lo + hi) / 2
            got = _at(mid, C, H)
            if got and contrast(got, bg) >= target:
                if lighten:
                    hi = mid
                else:
                    lo = mid
            elif lighten:
                lo = mid
            else:
                hi = mid
        picked = _at(hi if lighten else lo, C, H)
        if picked:
            reachable.append((abs((hi if lighten else lo) - L), picked))
    if reachable:
        return min(reachable)[1]
    best = colour  # nothing reaches the target: take whichever end gets closest
    for probe in (_at(1.0, C, H), _at(0.0, C, H)):
        if probe and contrast(probe, bg) > contrast(best, bg):
            best = probe
    return best


def readable(colour: str, bg: str, target: float = 4.5) -> str:
    """A readable version of `colour` on `bg`, hue and chroma preserved.

    Body text matters most: frozen_llama ships pale text on a pale background at
    1.3:1, which is unreadable rather than stylish.
    """
    return lift(colour, bg, target)


def muted_colour(theme: dict) -> str:
    """A secondary text colour for this theme that is actually readable.

    Monkeytype's `sub` is tuned for untyped words in a typing test, so on a page
    of prose it often lands near 2:1. Lift it toward `text` by the smallest step
    that reaches 4.5:1 against `bg`, which keeps the visual hierarchy instead of
    flattening everything into body colour. A theme whose `sub` already passes is
    left exactly as upstream ships it. The direction is decided by measurement,
    not by "assume text is lighter": for a theme such as nord_light, where the
    upstream `text` is itself the low-contrast colour, mixing toward it would
    make things worse.
    """
    sub, bg = theme["sub"], theme["bg"]
    if contrast(sub, bg) >= 4.5:
        return sub
    return lift(sub, bg, 4.5)


def text_colour(theme: dict) -> str:
    return lift(theme["text"], theme["bg"], 4.5)


def accent_colour(theme: dict, target: float = 4.5) -> str:
    """The theme's `main`, made legible as type.

    Monkeytype spends `main` on the caret and on filled buttons, so on its own
    background it is often below text contrast: 82 of 187 themes fail 4.5:1, and
    serika's yellow on its light grey is the worst at 1.46:1. Headings, links and
    the name are exactly where that signature colour belongs, so it is lifted
    rather than abandoned for grey.
    """
    return lift(theme["main"], theme["bg"], target)


def map_selector_part(sel: str) -> str | None:
    """Rewrite one selector; None means drop just this selector."""
    sel = sel.strip()
    if not sel or sel in ("*", "&", "body", "html", ":root", "body, html"):
        return None
    if any(tok in sel for tok in DROP_TOKENS):
        return None
    sel = re.sub(
        r'\[data-nav-item="([a-z_]+)"\]',
        lambda m: f'[data-nav-item="{NAV_MAP.get(m.group(1), m.group(1))}"]',
        sel,
    )
    sel = sel.replace("[data-nav-item]", ".site-nav a")
    for old in sorted(SELECTOR_MAP, key=len, reverse=True):
        sel = sel.replace(old, SELECTOR_MAP[old])
    sel = re.sub(r"\s+", " ", sel).strip().strip(",").strip()
    if not sel or "&" in sel:
        return None
    # only our own nav hooks may survive with a data- attribute
    if re.sub(ALLOWED_NAV_ATTR, "", sel).find("[data-") >= 0:
        return None
    return sel


def map_selector_list(sel: str) -> str | None:
    parts = [p for p in (map_selector_part(p) for p in sel.split(",")) if p]
    return ", ".join(dict.fromkeys(parts)) if parts else None


def flatten(css: str, parent: str | None, keyframes: dict, out: list, media: str | None = None):
    """Flatten nested CSS to (selector-list, declarations, media) tuples."""
    for kind, prelude, body in split_blocks(strip_comments(css)):
        if prelude and prelude.startswith("@"):
            if prelude.startswith("@keyframes"):
                name = re.match(r"@keyframes\s+([\w-]+)", prelude)
                if name and name.group(1) not in keyframes:
                    keyframes[name.group(1)] = body
            elif prelude.startswith("@media") or prelude.startswith("@supports"):
                flatten(body, parent, keyframes, out, media=prelude if not media else media)
            continue

        decls_text, children = split_body(body)
        decls = parse_decls(decls_text)

        composed = None
        if prelude:
            if parent:
                if "&" in prelude:
                    composed = prelude.replace("&", parent)
                elif prelude.startswith(":") or prelude.startswith("["):
                    composed = parent + prelude
                else:
                    composed = parent + " " + prelude
            else:
                composed = prelude
        elif parent:
            composed = parent

        if decls and composed:
            out.append((composed, decls, media))
        if children:
            flatten(
                "\n".join(f"{p} {{{b}}}" if p else b for p, b in children),
                composed or parent,
                keyframes,
                out,
                media=media,
            )


def split_blocks(css: str):
    out, buf, i = [], [], 0
    while i < len(css):
        ch = css[i]
        if ch == "{":
            prelude = "".join(buf).strip()
            buf = []
            depth, j = 1, i + 1
            while j < len(css) and depth:
                if css[j] == "{":
                    depth += 1
                elif css[j] == "}":
                    depth -= 1
                j += 1
            out.append(("at" if prelude.startswith("@") else "rule", prelude, css[i + 1:j - 1]))
            i = j
            continue
        if ch == "}":
            i += 1
            continue
        buf.append(ch)
        i += 1
    rest = "".join(buf).strip()
    if rest:
        out.append(("rule", None, rest))
    return out


# ----------------------------------------------------------------------- main

def build_theme_extra(name: str, src: str, keyframes: dict) -> tuple[str, int, bool]:
    """Return (scoped css, rule count, has-effects) for one theme's custom CSS."""
    rules: list = []
    flatten(src, None, keyframes, rules)
    scoped: list[str] = []
    fx = False
    for sel, decls, media in rules:
        keep = []
        for prop, val in decls:
            if any(prop.startswith(d) for d in DROP_DECL_PROPS):
                continue
            if prop == "background-image" and "url(" in val:
                continue  # chaos_theory caret sprite: no local asset
            keep.append((prop, rename_vars(val)))
        if not keep:
            continue
        mapped = map_selector_list(sel)
        if not mapped:
            continue
        body = " ".join(f"{p}: {v};" for p, v in keep)
        # every selector in the list needs the theme scope, not just the first
        scoped_line = ", ".join(
            f'[data-theme="{name}"] {s}' for s in mapped.split(", ")
        ) + f" {{ {body} }}"
        if media:
            scoped_line = f"{media} {{ {scoped_line} }}"
        scoped.append(scoped_line)
        if FX_HINT.search(body):
            fx = True
    return "\n".join(scoped), len(scoped), fx


def main() -> int:
    themes = parse_themes_ts((SRC / "themes.ts").read_text(encoding="utf-8"))
    if len(themes) < 150:
        print(f"only parsed {len(themes)} themes, refusing to write", file=sys.stderr)
        return 1
    css_files = {p.stem: p.read_text(encoding="utf-8") for p in SRC.glob("*.css")}
    missing_css = [n for n, t in themes.items() if t.get("hasCss") and n not in css_files]
    if missing_css:
        print(f"WARN hasCss themes with no vendored css: {missing_css}", file=sys.stderr)

    keyframes: dict[str, str] = {}
    blocks, meta = [], []
    ported = 0
    for name in sorted(themes, key=lambda n: n.lower()):
        t = themes[name]
        missing = [k for k in TOKENS if k not in t]
        if missing:
            print(f"WARN {name}: missing tokens {missing}", file=sys.stderr)
        effective = dict(t)
        notes = []
        if text_colour(t).lower() != t["text"].lower():
            # a few upstream themes ship body text under 4.5:1 on their own
            # background; keep the note in the output so the deviation is visible
            notes.append(f"--text lifted from {t['text']}")
            effective["text"] = text_colour(t)
        accent = accent_colour(t)
        if accent.lower() != t["main"].lower():
            notes.append(f"--accent lifted from {t['main']}")
        note = "".join(f"  /* {n} to stay readable */\n" for n in notes)
        toks = "\n".join(f"  {VAR[k]}: {effective[k]};" for k in TOKENS if k in effective)
        toks += f"\n  --muted: {muted_colour(t)};"
        # --accent is for type (headings, links, the name); --accent-soft for
        # decoration that only has to be seen, not read (selected rows, tint fills)
        toks += f"\n  --accent: {accent};"
        toks += f"\n  --accent-soft: {accent_colour(t, 3.0)};"
        chunk = [f'[data-theme="{name}"] {{\n{note}{toks}\n}}']
        fx = False
        rules = 0
        if t.get("hasCss") and name in css_files:
            extra, rules, fx = build_theme_extra(name, css_files[name], keyframes)
            if extra:
                chunk.append(extra)
                ported += rules
        blocks.append("\n".join(chunk))
        meta.append({
            "name": name,
            "hasCss": bool(t.get("hasCss")),
            "fx": bool(fx),
            "rules": rules,
            "swatch": [t.get(k, "#000000") for k in
                       ("bg", "main", "sub", "text", "caret", "error")],
        })

    header = (
        "/* GENERATED by tools/build_themes.py - do not edit.\n"
        f"   {len(themes)} Monkeytype themes from monkeytypegame/monkeytype\n"
        "   frontend/src/ts/constants/themes.ts\n"
        f"   plus {ported} ported rules from frontend/static/themes/*.css\n"
        "   Regenerate: make themes */\n"
    )
    kf = "\n".join(f"@keyframes {k} {{{b.strip()}}}" for k, b in sorted(keyframes.items()))
    OUT_CSS.write_text(header + "\n" + kf + "\n\n" + "\n\n".join(blocks) + "\n", encoding="utf-8")
    OUT_JSON.write_text(json.dumps(meta, indent=1) + "\n", encoding="utf-8")

    # A colour the page paints text with must clear its floor, or the theme is
    # quietly unreadable. This is a build error rather than a warning: it means
    # lift() failed, which is exactly how the washed-out colours got shipped once.
    floors = (
        (4.5, "text", lambda t: text_colour(t)),
        (4.5, "muted", lambda t: muted_colour(t)),
        (4.5, "accent", lambda t: accent_colour(t)),
        (3.0, "accent-soft", lambda t: accent_colour(t, 3.0)),
    )
    unreadable = []
    for name, t in themes.items():
        for floor, label, fn in floors:
            value = fn(t)
            got = contrast(value, t["bg"])
            if got < floor - 0.01:
                unreadable.append(f"{name}.{label} {value} {got:.2f}:1 < {floor}")
    if unreadable:
        print(f"FAIL {len(unreadable)} theme colours under their floor:", file=sys.stderr)
        for line in unreadable[:10]:
            print("  " + line, file=sys.stderr)
        return 1

    print(f"themes:            {len(themes)}")
    print(f"ported css rules:  {ported}")
    print(f"keyframes:         {len(keyframes)}")
    print(f"themes with fx:    {sum(1 for m in meta if m['fx'])}")
    lifted = sum(1 for n, t in themes.items()
                 if muted_colour(t).lower() != t["sub"].lower())
    text_fixed = [n for n, t in themes.items()
                  if text_colour(t).lower() != t["text"].lower()]
    worst = sorted(themes, key=lambda n: contrast(muted_colour(themes[n]), themes[n]["bg"]))[:3]
    print(f"muted lifted for readability: {lifted}/{len(themes)} themes")
    print(f"body text lifted (upstream under 4.5:1): {len(text_fixed)} {text_fixed}")
    accented = sum(1 for t in themes.values()
                   if accent_colour(t).lower() != t["main"].lower())
    print(f"accent lifted for headings/links: {accented}/{len(themes)} themes")
    print("lowest muted contrast: " + ", ".join(
        f"{n} {contrast(muted_colour(themes[n]), themes[n]['bg']):.2f}:1" for n in worst))
    worst_accent = sorted(themes, key=lambda n: contrast(accent_colour(themes[n]), themes[n]["bg"]))[:3]
    print("lowest accent contrast: " + ", ".join(
        f"{n} {contrast(accent_colour(themes[n]), themes[n]['bg']):.2f}:1" for n in worst_accent))
    print(f"wrote static/themes.css  ({OUT_CSS.stat().st_size} bytes)")
    print(f"wrote static/themes.json ({OUT_JSON.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
