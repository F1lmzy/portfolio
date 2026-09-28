#!/usr/bin/env python3
"""Checks on the built site. No network, no server: everything asserted against the
files in docs/ that GitHub Pages will serve.

    python3 tests/test_site.py            # build first with python3 build.py

These are the failures that actually break a Pages deploy: a link to a file that
was never built, an absolute path that breaks under /<repo>/, an external asset
that turns an offline page into a network dependency, or a theme that silently
lost its colour tokens.

The site is two pages: index.html (the portfolio) and themes.html (the picker).
Checks are made against whichever page should carry the thing in question, and
the split itself is asserted, so themes cannot drift back onto the main page.
"""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
STATIC = ROOT / "static"

FAILURES: list[str] = []
CHECKS = 0


def check(condition: bool, label: str) -> None:
    global CHECKS
    CHECKS += 1
    if not condition:
        FAILURES.append(label)


class LinkParser(HTMLParser):
    """Collect every URL the browser would resolve itself."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.refs: list[tuple[str, str, str]] = []
        self.ids: set[str] = set()
        self.classes: set[str] = set()
        self.tags: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.tags.append(tag)
        if "id" in a:
            self.ids.add(a["id"])
        for cls in (a.get("class") or "").split():
            self.classes.add(cls)
        for attr in ("href", "src"):
            if a.get(attr):
                self.refs.append((tag, a[attr], attr))


def page(name: str) -> tuple[str, LinkParser]:
    html = (DOCS / name).read_text(encoding="utf-8")
    parser = LinkParser()
    parser.feed(html)
    return html, parser


def main() -> int:
    for required in ("index.html", "themes.html"):
        if not (DOCS / required).is_file():
            print(f"docs/{required} missing. Run: python3 build.py", file=sys.stderr)
            return 1

    html, index = page("index.html")
    themes_html, picker = page("themes.html")
    PAGES = {"index.html": (html, index), "themes.html": (themes_html, picker)}

    themes = json.loads((STATIC / "themes.json").read_text(encoding="utf-8"))
    names = [t["name"] for t in themes]
    themes_css = (STATIC / "themes.css").read_text(encoding="utf-8")

    # ---- every theme is present, in the picker markup and in the stylesheet
    check(len(themes) == 187, f"expected 187 themes, found {len(themes)}")
    check(len(names) == len(set(names)), "duplicate theme names in themes.json")
    missing_markup = [n for n in names if f'data-theme-name="{n}"' not in themes_html]
    check(not missing_markup, f"themes missing from themes.html: {missing_markup[:5]}")
    missing_css = [n for n in names if f'[data-theme="{n}"]' not in themes_css]
    check(not missing_css, f"themes with no [data-theme] block: {missing_css[:5]}")

    # ---- every theme carries all ten tokens
    token_names = ("--bg", "--main", "--caret", "--sub", "--sub-alt", "--text",
                   "--error", "--error-extra", "--colorful-error",
                   "--colorful-error-extra")
    missing_tokens = []
    for name in names:
        block = themes_css.split(f'[data-theme="{name}"] {{', 1)
        if len(block) < 2:
            missing_tokens.append(name)
            continue
        body = block[1].split("}", 1)[0]
        missing_tokens += [f"{name}.{v}" for v in token_names if f"{v}:" not in body]
    check(not missing_tokens, f"themes missing tokens: {missing_tokens[:5]}")

    # ---- no dead CSS: braces balance, no upstream-only hooks leaked through
    check(themes_css.count("{") == themes_css.count("}"), "themes.css braces unbalanced")
    for hook in ("data-focused", "data-ui-element", "#words", ".pageSettings", "crtmode"):
        check(hook not in themes_css, f"upstream hook '{hook}' leaked into themes.css")

    # ---- the split: the picker lives on its own page and nowhere else
    check("theme-item" not in index.classes,
          "the theme picker is back on the portfolio page")
    check("data-theme-name=" not in html,
          "the portfolio page carries theme rows again")
    check("theme-item" in picker.classes, "themes.html has no theme rows")
    check("theme-preview" in picker.classes, "themes.html has no preview pane")
    for href in ('href="themes.html"', 'href="index.html"'):
        check(href in themes_html, f"themes.html is missing {href}")
    check('href="themes.html"' in html, "the portfolio does not link to themes.html")
    check('href="index.html"' in themes_html, "themes.html does not link back")

    # ---- local refs resolve on both pages, and nothing is *loaded* remotely
    for name, (page_html, parser) in PAGES.items():
        external = []
        for tag, url, attr in parser.refs:
            if url.startswith(("mailto:", "data:")):
                continue
            if url.startswith(("http://", "https://")):
                if attr == "src" or tag == "link":
                    external.append(url)
                continue
            # a link may point at this page or the other one, optionally with a
            # fragment: the file must exist and the fragment must have a target
            path, _, frag = url.partition("#")
            target_page = path or name
            if path:
                check((DOCS / path).resolve().exists(),
                      f"{name} references a missing file: {url}")
            if frag and target_page in PAGES:
                check(frag in PAGES[target_page][1].ids,
                      f"{name}: {url} has no #{frag} target in {target_page}")
        check(not external,
              f"{name} loads remote assets (would break offline): {external[:3]}")
        # ---- relative paths only, so a /<repo>/ Pages URL works
        check('href="/' not in page_html and 'src="/' not in page_html,
              f"{name} contains a root-absolute path, which breaks under /<repo>/")

    # ---- the content that must be on the portfolio page
    for needle, label in [
        ("National University of Singapore", "NUS education entry"),
        ("Imperial College London", "Imperial exchange entry"),
        ("Kabam Robotics", "Kabam experience entry"),
        ("Institute of High Performance Computing", "A*STAR experience entry"),
        ("StereoGS", "bachelor thesis"),
        ("Final-year Electrical Engineering student", "final year, exchange finished"),
        ("Completed year-long exchange", "exchange marked complete"),
        # all six journal articles, including the four the resume omits
        ("Sensors and Actuators A: Physical", "Elsevier journal article"),
        ("10.1016/j.sna.2025.117170", "Elsevier DOI"),
        ("Hilbert-Huang", "2026 tool wear paper"),
        ("10.14445/23488379/IJEEE-V13I2P104", "2026 DOI"),
        ("Federated Learning-Based", "2024 federated learning paper"),
        ("10.14445/23488549/IJECE-V11I9P120", "IJECE DOI"),
        ("Comparative Analysis of MLP, CNN, RNN", "2024 deep learning paper"),
        ("10.14445/23488379/IJEEE-V11I9P127", "IJEEE 11(9) DOI"),
        ("10.14445/22315381/IJETT-V73I1P123", "IJETT DOI"),
        ("10.14445/23488379/IJEEE-V11I12P106", "IJEEE 11(12) DOI"),
        ("cited by 8", "highest citation count"),
        ("6 journals", "publication count"),
        ("28 citations", "total citations"),
        ("github/F1lmzy", "GitHub link"),
        ("cv.pdf", "CV link"),
    ]:
        check(needle in html, f"missing from the portfolio: {label}")

    # ---- the layout is the two-column works grid, not one long column
    check('class="works-row"' in html, "the works grid is missing")
    check(html.count('class="works-col"') == 2,
          f"expected 2 works columns, found {html.count('class=\"works-col\"')}")
    # ---- and the entries are title-only: no leftover descriptions
    for gone, label in [("data-topics=", "publication topic attributes"),
                        ("data-kind=", "project kind attributes"),
                        ('class="tag"', "topic tag chips"),
                        ("details class=\"drawer\"", "project detail drawers")]:
        check(gone not in html, f"stale description markup still present: {label}")

    # ---- no em dashes in any visible copy, per the user's standing rule
    for name, page_html in (("index.html", html), ("themes.html", themes_html)):
        visible = re.sub(r"<script.*?</script>|<style.*?</style>", "", page_html, flags=re.S)
        check("\u2014" not in visible, f"an em dash appears in {name}")

    # ---- and no entity that got escaped a second time (renders as "&middot;")
    for name, page_html in (("index.html", html), ("themes.html", themes_html)):
        for entity in ("&amp;middot;", "&amp;ndash;", "&amp;mdash;", "&amp;nbsp;",
                       "&amp;amp;", "&amp;#"):
            check(entity not in page_html,
                  f"double-escaped entity in {name}: {entity}")
        title = re.search(r"<title>(.*?)</title>", page_html, re.S)
        check(bool(title) and "&" not in title.group(1),
              f"the {name} <title> still contains an HTML entity")

    # ---- the interactive hooks the script depends on
    for cls in ("theme-item", "theme-preview", "theme-toolbar", "theme-list"):
        check(cls in picker.classes, f"themes.html lost the .{cls} hook")
    for cls in ("section", "entry", "listing", "year-col", "works-row", "works-col"):
        check(cls in index.classes, f"index.html lost the .{cls} hook")
    for el_id in ("theme-list", "theme-search", "theme-filter", "theme-count",
                  "theme-preview", "theme-random"):
        check(el_id in picker.ids, f"themes.html lost #{el_id}")
    for el_id in ("theme-current", "contact"):
        check(el_id in index.ids, f"index.html lost #{el_id}")
        check(el_id in picker.ids, f"themes.html lost #{el_id}")

    # ---- app.js and the markup still agree, and the script works on both pages
    app_js = (STATIC / "app.js").read_text(encoding="utf-8")
    for selector in ("theme-list", "theme-search", "theme-filter", "theme-count",
                     "theme-preview", "theme-current", "theme-random"):
        check(f'"{selector}"' in app_js, f"app.js no longer handles {selector}")
    check("data-theme" in app_js, "app.js does not set data-theme")
    check("localStorage" in app_js, "app.js does not persist the theme")
    # every element app.js looks up must be optional, or the portfolio page throws
    for guard in ("if (picker)", "if (search)", "if (kindFilter)", "if (random)"):
        check(guard in app_js, f"app.js is missing the guard {guard}")

    # ---- the small script stays small, and nothing ships that we did not build
    check(len(app_js) < 8000, f"static/app.js grew to {len(app_js)} bytes")
    check(not (STATIC / "htmx4.min.js").exists(),
          "a vendored framework is still in static/")
    for built in ("index.html", "themes.html", "404.html", ".nojekyll"):
        check((DOCS / built).exists(), f"build output missing {built}")

    print(f"{CHECKS - len(FAILURES)}/{CHECKS} checks passed")
    if FAILURES:
        print("\nfailures:")
        for f in FAILURES:
            print("  -", f)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
