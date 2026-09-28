#!/usr/bin/env python3
"""Checks on the built site. No network, no server: everything asserted against the
files in docs/ that GitHub Pages will serve.

    python3 tests/test_site.py            # build first with python3 build.py

These are the failures that actually break a Pages deploy: a link to a file that
was never built, an absolute path that breaks under /<repo>/, an external asset
that turns an offline page into a network dependency, or a theme that silently
lost its colour tokens.
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
        self.refs: list[tuple[str, str]] = []
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


def main() -> int:
    index_path = DOCS / "index.html"
    if not index_path.is_file():
        print("docs/index.html missing. Run: python3 build.py", file=sys.stderr)
        return 1

    html = index_path.read_text(encoding="utf-8")
    parser = LinkParser()
    parser.feed(html)

    themes = json.loads((STATIC / "themes.json").read_text(encoding="utf-8"))
    names = [t["name"] for t in themes]
    themes_css = (STATIC / "themes.css").read_text(encoding="utf-8")

    # ---- every theme is present, in both the markup and the stylesheet
    check(len(themes) == 187, f"expected 187 themes, found {len(themes)}")
    check(len(names) == len(set(names)), "duplicate theme names in themes.json")
    for name in names:
        if html.count(f'data-theme-name="{name}"') < 1:
            check(False, f"theme {name} missing from index.html")
            break
    else:
        check(True, "every theme appears in the picker")
    for name in names:
        if f'[data-theme="{name}"]' not in themes_css:
            check(False, f"theme {name} has no [data-theme] block in themes.css")
            break
    else:
        check(True, "every theme has a scoped block in themes.css")

    # ---- every theme carries all ten tokens
    missing_tokens = []
    for name in names:
        block = themes_css.split(f'[data-theme="{name}"] {{', 1)
        if len(block) < 2:
            missing_tokens.append(name)
            continue
        body = block[1].split("}", 1)[0]
        for var in ("--bg", "--main", "--caret", "--sub", "--sub-alt", "--text",
                    "--error", "--error-extra", "--colorful-error",
                    "--colorful-error-extra"):
            if f"{var}:" not in body:
                missing_tokens.append(f"{name}.{var}")
    check(not missing_tokens, f"themes missing tokens: {missing_tokens[:5]}")

    # ---- no dead CSS: braces balance, no upstream-only hooks leaked through
    check(themes_css.count("{") == themes_css.count("}"), "themes.css braces unbalanced")
    for hook in ("data-focused", "data-ui-element", "#words", ".pageSettings", "crtmode"):
        check(hook not in themes_css, f"upstream hook '{hook}' leaked into themes.css")

    # ---- local refs resolve, and nothing is *loaded* from a third party
    #      (outbound <a href> links are fine; a remote src or stylesheet is not)
    external = []
    for tag, url, attr in parser.refs:
        if url.startswith(("mailto:", "data:", "#")):
            continue
        if url.startswith(("http://", "https://")):
            if attr == "src" or tag == "link":
                external.append(url)
            continue
        target = (DOCS / url.split("#")[0].split("?")[0]).resolve()
        check(target.exists(), f"index.html references a missing file: {url}")
    check(not external,
          f"the page loads remote assets (would break offline): {external[:3]}")

    # ---- relative paths only, so a /<repo>/ Pages URL works
    check('href="/' not in html and 'src="/' not in html,
          "index.html contains a root-absolute path, which breaks under /<repo>/")

    # ---- in-page anchors all have a target
    for tag, url, attr in parser.refs:
        if url.startswith("#") and len(url) > 1:
            check(url[1:] in parser.ids, f"anchor {url} has no matching id")

    # ---- the content that must be on the page
    for needle, label in [
        ("National University of Singapore", "NUS education entry"),
        ("Imperial College London", "Imperial exchange entry"),
        ("Kabam Robotics", "Kabam experience entry"),
        ("Institute of High Performance Computing", "A*STAR experience entry"),
        ("StereoGS", "bachelor thesis"),
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
        check(needle in html, f"missing from the page: {label}")

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

    # ---- no em dashes anywhere in the visible copy, per the user's standing rule
    visible = re.sub(r"<script.*?</script>|<style.*?</style>", "", html, flags=re.S)
    check("\u2014" not in visible, "an em dash appears in the page copy")

    # ---- and no entity that got escaped a second time (renders as "&middot;")
    for entity in ("&amp;middot;", "&amp;ndash;", "&amp;mdash;", "&amp;nbsp;",
                   "&amp;amp;", "&amp;#"):
        check(entity not in html, f"double-escaped entity in the page: {entity}")
    title = re.search(r"<title>(.*?)</title>", html, re.S)
    check(bool(title) and "&" not in title.group(1),
          "the <title> still contains an HTML entity")

    # ---- the interactive hooks the script depends on still exist
    for cls in ("theme-item", "theme-preview", "theme-toolbar", "theme-list",
                "section", "entry", "listing", "year-col", "works-row",
                "works-col"):
        check(cls in parser.classes, f"markup lost the .{cls} hook")
    for el_id in ("theme-list", "theme-search", "theme-filter", "theme-count",
                  "theme-preview", "theme-current", "theme-random", "contact"):
        check(el_id in parser.ids, f"markup lost #{el_id}")

    # ---- app.js and style.css reference the same ids/classes they select
    app_js = (STATIC / "app.js").read_text(encoding="utf-8")
    for selector in ("theme-list", "theme-search", "theme-filter", "theme-count",
                     "theme-preview", "theme-current", "theme-random"):
        check(f'"{selector}"' in app_js, f"app.js no longer handles {selector}")
    check("data-theme" in app_js, "app.js does not set data-theme")
    check("localStorage" in app_js, "app.js does not persist the theme")

    # ---- the small script stays small, and nothing ships that we did not build
    check(len(app_js) < 8000, f"static/app.js grew to {len(app_js)} bytes")
    check(not (STATIC / "htmx4.min.js").exists(),
          "a vendored framework is still in static/")
    for page in ("index.html", "404.html", ".nojekyll"):
        check((DOCS / page).exists(), f"build output missing {page}")

    print(f"{CHECKS - len(FAILURES)}/{CHECKS} checks passed")
    if FAILURES:
        print("\nfailures:")
        for f in FAILURES:
            print("  -", f)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
