Third-party notices
===================

Monkeytype themes
-----------------
data/monkeytype_themes/ contains 53 files copied from the Monkeytype project:

  frontend/src/ts/constants/themes.ts
  frontend/static/themes/*.css          (the 52 themes that carry custom CSS)

  https://github.com/monkeytypegame/monkeytype

Monkeytype is licensed under the GNU General Public License v3.0. Those vendored
files remain under that licence, and so do the parts of the generated
static/themes.css that are derived from them (the ported rules, rewritten by
tools/build_themes.py to target this site's markup).

Everything else in this repository (the page, the layout stylesheet, the client
script, the build tooling and the content) is the author's own work.

The theme colour values themselves are the themes' published palettes and are
reproduced unchanged, apart from two documented readability adjustments in
build_themes.py: --muted, and --text where an upstream theme's own body text
falls below a 4.5:1 contrast ratio against its own background.
