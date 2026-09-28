#!/usr/bin/env python3
"""Build the static site into docs/ (what GitHub Pages serves).

    python3 build.py              # -> docs/index.html + docs/static/*
    python3 build.py --out site   # different output folder
    python3 build.py --cv ~/Documents/Resume/resume.pdf

GitHub Pages is static: there is no server to render at request time, so every
byte of HTML here is produced now, and the small interactive pieces (theme
switching, theme search, the two filters) are local browser state handled in
static/app.js.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import render  # noqa: E402

# only these ship; anything else in static/ stays out of the published site
ASSETS = ["style.css", "themes.css", "app.js"]


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the portfolio into static files")
    ap.add_argument("--out", default="docs", help="output directory (default: docs)")
    ap.add_argument("--cv", default=str(Path.home() / "Documents" / "Resume" / "resume.pdf"),
                    help="PDF to publish as cv.pdf")
    args = ap.parse_args()

    out = (ROOT / args.out).resolve()
    out_static = out / "static"

    themes_css = ROOT / "static" / "themes.css"
    themes_json = ROOT / "static" / "themes.json"
    if not themes_css.is_file() or not themes_json.is_file():
        print("theme files missing, run: python3 tools/build_themes.py", file=sys.stderr)
        return 1

    out.mkdir(parents=True, exist_ok=True)
    out_static.mkdir(parents=True, exist_ok=True)

    # pages
    (out / "index.html").write_text(render.index_page(), encoding="utf-8")
    (out / "themes.html").write_text(render.themes_page(), encoding="utf-8")
    (out / "404.html").write_text(render.not_found_page(), encoding="utf-8")

    # assets
    for name in ASSETS:
        shutil.copyfile(ROOT / "static" / name, out_static / name)
    shutil.copyfile(themes_css, out_static / "themes.css")
    shutil.copyfile(themes_json, out_static / "themes.json")

    # Jekyll would otherwise skip some paths on Pages
    (out / ".nojekyll").write_text("", encoding="utf-8")

    # the CV: taken as-is from the resume build
    cv_src = Path(args.cv).expanduser()
    if cv_src.is_file():
        shutil.copyfile(cv_src, out / "cv.pdf")
        cv_note = f"copied {cv_src}"
    else:
        cv_note = f"NOT FOUND at {cv_src} - cv.pdf will 404"
        # remove a stale copy so the page never links a file that is not there
        stale = out / "cv.pdf"
        if stale.exists():
            stale.unlink()

    themes = json.loads(themes_json.read_text(encoding="utf-8"))
    index = (out / "index.html").read_text(encoding="utf-8")
    themes_html = (out / "themes.html").read_text(encoding="utf-8")
    print(f"built {out.relative_to(ROOT)}/")
    print(f"  index.html    {len(index):>8,} bytes   (portfolio)")
    print(f"  themes.html   {len(themes_html):>8,} bytes   ({len(themes)} themes)")
    print(f"  404.html")
    print(f"  static/themes.css {themes_css.stat().st_size:>8,} bytes")
    print(f"  cv.pdf        {cv_note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
