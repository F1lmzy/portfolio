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
    # the preview pane carries the same class, so a theme's caret styling shows
    # up in the live preview as well as on the real header
    "#caret": "#caret, .caret",
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


def mix_hex(a: str, b: str, weight_a: float) -> str:
    ra, rb = hex_to_rgb(a), hex_to_rgb(b)
    return "#%02x%02x%02x" % tuple(
        round(weight_a * x + (1 - weight_a) * y) for x, y in zip(ra, rb)
    )


def readable(colour: str, bg: str, target: float = 4.5) -> str:
    """Push a colour toward white or black until it clears `target` against `bg`.

    A handful of upstream themes fail this against their own background even for
    body text (frozen_llama ships pale text on a pale background at 1.3:1), which
    makes the page unreadable rather than stylish. The hue is kept: the colour is
    only mixed toward white or black. Both directions are tried and the better one
    wins, because background luminance does not settle it: honey's background
    #f2aa00 is saturated mid-luminance, where black reaches 10:1 but white only 2:1.
    """
    if contrast(colour, bg) >= target:
        return colour
    best = colour
    for toward in ("#ffffff", "#000000"):
        for weight in (0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0):
            candidate = mix_hex(colour, toward, weight)
            if contrast(candidate, bg) >= target:
                return candidate
            if contrast(candidate, bg) > contrast(best, bg):
                best = candidate
    return best


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
    bg, sub, text = theme["bg"], theme["sub"], theme["text"]
    if contrast(sub, bg) >= 4.5:
        return sub
    for weight in (0.75, 0.55, 0.35, 0.2):
        candidate = mix_hex(sub, text, weight)
        if contrast(candidate, bg) >= 4.5:
            return candidate
    return readable(text, bg)


def text_colour(theme: dict) -> str:
    return readable(theme["text"], theme["bg"])


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
        note = ""
        if text_colour(t).lower() != t["text"].lower():
            # a few upstream themes ship body text under 4.5:1 on their own
            # background; keep the note in the output so the deviation is visible
            note = f"  /* --text lifted from {t['text']} to stay readable */\n"
            effective["text"] = text_colour(t)
        toks = "\n".join(f"  {VAR[k]}: {effective[k]};" for k in TOKENS if k in effective)
        toks += f"\n  --muted: {muted_colour(t)};"
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
    print("lowest muted contrast: " + ", ".join(
        f"{n} {contrast(muted_colour(themes[n]), themes[n]['bg']):.2f}:1" for n in worst))
    print(f"wrote static/themes.css  ({OUT_CSS.stat().st_size} bytes)")
    print(f"wrote static/themes.json ({OUT_JSON.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
