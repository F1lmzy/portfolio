# Portfolio site: one pre-rendered HTML page, 187 Monkeytype themes

Live at **https://f1lmzy.github.io/portfolio/**

    make build     # -> docs/index.html + docs/static/*
    make serve     # builds, then serves on http://127.0.0.1:8000
    make themes    # regenerate static/themes.css from data/monkeytype_themes/
    make test      # rebuilds, then checks the built site

## What it is

Two pages, both pre-rendered:

- `index.html` the portfolio: a header, then a two-column works grid that uses
  the full width. Left column: about, publications, bachelor thesis, technical
  skills. Right column: education, experience, projects. Rows are year-grouped
  with hairline rules and each entry is title-first with one meta line, so the
  page is about three screens instead of a long scroll.
- `themes.html` the theme picker: a live preview of the site chrome, a search
  box, a category filter, a random button and all 187 themes as rows with their
  palettes. It is deliberately not part of the portfolio, and the page is itself
  the preview of whatever theme you pick.

The theme feature is Monkeytype's: **all 187 themes**, each carrying its exact
upstream colour tokens, and 47 of them also their own custom CSS (the animated
carets, the colour-cycling links, the coloured nav pills). Hover a theme to
preview it, click to wear it. The choice is kept in `localStorage`, with an
inline `<head>` script so a reload does not flash.

## No framework, and why

This was built for htmx first, then for Alpine, and both were dropped once it was
clear the site would be hosted on GitHub Pages.

htmx's model is that the *server* holds state and answers with HTML. On Pages
there is no server, so every request would fetch a file that could not depend on
what the visitor did. Alpine is designed for exactly this client-side state, but
the state here is tiny: the chosen theme, a search box, a category filter and a
random button. That is about 120 lines of plain DOM code, so the honest answer
was neither library. What htmx would have bought (fragment URLs) is worth little
for six publications and ten projects, and costs a round trip to show them.

So everything is pre-rendered by `build.py` and `static/app.js` handles the
interaction. It degrades cleanly: with JavaScript off the whole page is still
there, all themes are still listed, and the default Monkeytype theme applies.

## Files

| Path | Role |
|---|---|
| `build.py` | writes both pages and copies assets into `docs/` |
| `render.py` | all HTML generation |
| `content.py` | the only content file: resume facts, publications, projects |
| `static/style.css` | layout and typography, driven by the theme tokens |
| `static/app.js` | theme switching, search, random, `/` shortcut |
| `static/cv.pdf` | the CV the `cv.pdf` link points at |
| `static/themes.css` | GENERATED: 187 `[data-theme]` blocks + ported CSS |
| `static/themes.json` | GENERATED: picker metadata (name, swatches, flags) |
| `tools/build_themes.py` | turns the vendored Monkeytype sources into the above |
| `data/monkeytype_themes/` | vendored upstream: `themes.ts` + 52 theme CSS files |
| `tests/test_site.py` | checks on the built output |
| `.github/workflows/pages.yml` | builds and deploys `docs/` to GitHub Pages |

`static/app.js` is shared by both pages and every lookup in it is optional, so
the portfolio page runs the same file with no picker present.

## How the theming works

`static/themes.css` holds one `[data-theme="<name>"]` block per theme: the ten
Monkeytype tokens, plus for 47 themes that theme's own CSS rewritten to this
site's markup. The page renders with `data-theme="godspeed"` on `<html>`, and
`static/app.js` swaps that attribute and saves it. There is no per-theme
stylesheet to fetch, so switching is instant and works offline.

The ported rules are the interesting part. `tools/build_themes.py` parses
`themes.ts` (a TypeScript object literal, read with a brace matcher) and each
custom CSS file, then:

- flattens nested `&` blocks into plain selectors
- maps Monkeytype's hooks onto this site: `[data-nav-item="test"]` to this nav's
  `about` (and so on down the nav, by position), `[data-ui-element="logoText"]`
  to `.brand-name`
- renames `--main-color` style variables to this site's `--main` style ones
- splits selector lists and drops only the parts naming elements this site does
  not have (`#words`, `.word`, `.pageSettings`, `crtmode`, svg logos), so one
  unknown target never takes a whole rule down with it
- hoists the 25 `@keyframes` once, globally

The run reports what it did: 187 themes, 208 ported rules, 25 keyframes, 17
themes with real animation, and it exits non-zero if any theme ends up unreadable.

### Which token paints what

| Token | What it paints | Why |
|---|---|---|
| `--bg` | the page background | the theme's background, untouched |
| `--text` | body prose | Monkeytype's typed-text colour, the bulk of the reading |
| `--accent` | headings, the name, links, active nav | the theme's signature colour, so 187 themes don't all read as one grey page |
| `--accent-soft` | selected rows, focus rings | the same hue where it only has to be seen, not read |
| `--muted` | metadata, years, tags, footer | from `sub`, which upstream tunes for untyped words |
| `--caret`, `--error` | nothing, or reserved | kept for fidelity |

### The deliberate deviations from upstream

Monkeytype colours a *typing test*, and two of its tokens are tuned for that rather
than for prose:

- `sub` marks text you have not typed yet and is meant to be faint, landing near
  2:1 on a page of prose. 146 of 187 themes need it lifted for `--muted`.
- `main` is spent on the caret and on filled buttons, so on its own background it
  often fails as type: 82 of 187 themes are under 4.5:1, serika's yellow on its own
  light grey worst at 1.46:1. All 82 get lifted for `--accent`. 32 themes fail
  4.5:1 even for their *own body text* (frozen_llama is #ffffff on #9bf2ea, 1.3:1),
  and those are lifted for `--text`.

The corrections are done in OKLCH, moving lightness only: hue cannot drift, and
chroma is pushed to whatever sRGB allows at the new lightness (capped at 1.5 times
the theme's own, so a nearly grey theme is not handed saturation it never had). This
is the difference between serika's headings being gold on its light background and
being mud. Mixing toward white or black, which is the obvious way to do it, is what
made every light theme converge on the same washed grey.

The direction of the move is chosen by measurement, not by assuming text is lighter
than background: honey's background is saturated mid-luminance, where black reaches
10:1 and white only 2:1. Where a colour had to move, the generated CSS keeps the
upstream value in a comment.

## Content

All facts live in `content.py`. The six journal articles, their venues, volumes,
pages and citation counts come from the DOI records (Crossref), and the list
itself was assembled from OpenAlex's author record for "Sri Rajkavin AV" and
cross-checked against Crossref's author query: the resume only carries two of the
six. The 2026 title is the publisher's own (Crossref holds a truncated "Signal"
for that DOI). Three preprint duplicates are deliberately excluded. Each project
is a repository on the user's own GitHub with a README behind the description;
the two entries with no public repository say so rather than quoting results.

## Licences

The page, layout, script and tooling are the author's own work. The vendored
Monkeytype sources and the CSS ported from them are GPL-3.0: see `NOTICE.md`.
