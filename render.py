"""HTML rendering for a single static page.

Layout follows the reference: a wide two-column works grid that uses the full
width, year-grouped rows separated by hairline rules, and one-line entries where
the title is the content. Everything is pre-rendered: no server, no fragments, no
framework. The small amount of interactivity (theme switching, theme search) is
local state handled in static/app.js. All URLs are relative, so the same build
works at a domain root or under /<repo>/ on GitHub Pages.
"""

from __future__ import annotations

import html
import json
from pathlib import Path

import content as C

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"

THEMES: list[dict] = json.loads((STATIC / "themes.json").read_text(encoding="utf-8"))
DEFAULT_THEME = "serika_dark"

FAVICON = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E"
    "%3Crect width='16' height='16' rx='3' fill='%23323437'/%3E"
    "%3Crect x='6' y='3' width='4' height='10' fill='%23e2b714'/%3E%3C/svg%3E"
)

# reads the saved theme before first paint so a reload does not flash the default
NO_FLASH = (
    "<script>try{var t=localStorage.getItem('mt_theme');"
    "if(t)document.documentElement.setAttribute('data-theme',t)}catch(e){}</script>"
)


def esc(value) -> str:
    return html.escape(str(value), quote=True)


# ------------------------------------------------------------------- atoms

def swatches(colours: list[str]) -> str:
    """Six colour chips. The values ride on the parent as custom properties, which
    keeps a 187-row list much smaller than six inline background styles per row."""
    return ('<span class="swatches" aria-hidden="true">'
            + "<i></i>" * len(colours[:6]) + "</span>")


def swatch_vars(colours: list[str]) -> str:
    return "".join(f"--sw{n}:{c};" for n, c in enumerate(colours[:6], 1))


def section_head(section_id: str, title: str, note: str = "") -> str:
    n = f'<span class="section-note">{esc(note)}</span>' if note else ""
    return f'<h2 id="{esc(section_id)}">{esc(title)}{n}</h2>'


def section(section_id: str, title: str, body: str, note: str = "") -> str:
    return (
        f'<section class="section" id="{esc(section_id)}">'
        f"{section_head(section_id, title, note)}{body}</section>"
    )


def row(year: str, body: str, show_year: bool = True) -> str:
    """One year-grouped row. The year prints once per group, so a run of entries
    from the same year does not repeat it, as in the reference layout."""
    cell = (f'<div class="year-col">{esc(year)}</div>' if show_year
            else '<div class="year-col" aria-hidden="true"></div>')
    return f'<article class="entry">{cell}<div class="entry-body">{body}</div></article>'


def listing(rows: list[str]) -> str:
    return f'<div class="listing">{"".join(rows)}</div>'


def group_flags(items: list[dict], key: str) -> list[bool]:
    flags, seen = [], set()
    for item in items:
        flags.append(item[key] not in seen)
        seen.add(item[key])
    return flags


# ------------------------------------------------------------------ sections

def about_html() -> str:
    paras = "".join(f"<p>{esc(p)}</p>" for p in C.ABOUT)
    return section("about", "About", paras)


def publication_row(pub: dict, show_year: bool) -> str:
    authors = ", ".join(
        f"<strong>{esc(a)}</strong>" if a == pub["me"] else esc(a)
        for a in pub["authors"]
    )
    cited = f'cited by {pub["citations"]}' if pub["citations"] else "no citations yet"
    body = (
        f'<div class="entry-title"><a href="{esc(pub["doi_url"])}">'
        f'{esc(pub["title"])}</a></div>'
        f'<div class="entry-meta">{authors}</div>'
        f'<div class="entry-meta"><em>{esc(pub["venue"])}</em> '
        f'{esc(pub["volume"])}: {esc(pub["pages"])} &middot; {esc(pub["month"])} '
        f'{pub["year"]} &middot; {cited}</div>'
    )
    return row(pub["year"], body, show_year)


def publications_html() -> str:
    pubs = sorted(C.PUBLICATIONS, key=lambda p: (-p["year"], p["venue"], p["title"]))
    flags = group_flags(pubs, "year")
    rows = [publication_row(p, f) for p, f in zip(pubs, flags)]
    return section(
        "publications", "Publications", listing(rows),
        f"{len(pubs)} journals \u00b7 {C.TOTAL_CITATIONS} citations",
    )


def thesis_html() -> str:
    t = C.THESIS
    body = (
        f'<div class="entry-title">{esc(t["title"])}</div>'
        f'<div class="entry-meta">{esc(t["org"])} &middot; {esc(t["start"])} to '
        f'{esc(t["end"])}</div>'
        f'<div class="entry-links"><a href="{esc(t["repo"])}">repository</a></div>'
    )
    return section("thesis", "Bachelor Thesis", listing([row("thesis", body)]))


def experience_html() -> str:
    rows, flags = [], group_flags(C.EXPERIENCE, "start")
    for job, show in zip(C.EXPERIENCE, flags):
        bullets = "".join(f"<li>{esc(b)}</li>" for b in job["bullets"])
        body = (
            f'<div class="entry-title">{esc(job["role"])}</div>'
            f'<div class="entry-meta">{esc(job["org"])} &middot; {esc(job["place"])}'
            f' &middot; {esc(job["start"])} to {esc(job["end"])}</div>'
            f'<ul class="bullets">{bullets}</ul>'
        )
        rows.append(row(job["start"][-4:], body, show))
    return section("experience", "Experience", listing(rows))


def education_html() -> str:
    rows, flags = [], group_flags(C.EDUCATION, "start")
    for ed, show in zip(C.EDUCATION, flags):
        body = (
            f'<div class="entry-title">{esc(ed["school"])}</div>'
            f'<div class="entry-meta">{esc(ed["degree"])}</div>'
            f'<div class="entry-meta">{esc(ed["start"])} to {esc(ed["end"])}'
            f' &middot; {esc(ed["place"])} &middot; {esc(ed["detail"])}</div>'
        )
        rows.append(row(ed["start"][-4:], body, show))
    return section("education", "Education", listing(rows))


def projects_html() -> str:
    rows, flags = [], group_flags(C.PROJECTS, "year")
    for p, show in zip(C.PROJECTS, flags):
        if p["repo"]:
            name = f'<a href="{esc(p["repo"])}">{esc(p["name"])}</a>'
        else:
            name = f'{esc(p["name"])} <span class="dim">(no repository)</span>'
        body = (
            f'<div class="entry-title">{name}</div>'
            f'<div class="entry-meta">{esc(p["kind"])} &middot; {esc(p["stack"])}</div>'
        )
        rows.append(row(p["year"], body, show))
    repos = sum(1 for p in C.PROJECTS if p["repo"])
    return section("projects", "Projects", listing(rows),
                   f"{len(C.PROJECTS)} entries \u00b7 {repos} repositories")


def skills_html() -> str:
    rows = "".join(
        f'<article class="entry"><div class="year-col">{esc(label)}</div>'
        f'<div class="entry-body entry-meta">{esc(values)}</div></article>'
        for label, values in C.SKILLS
    )
    return section("skills", "Technical Skills", f'<div class="listing">{rows}</div>')


# ------------------------------------------------------------------ the picker

def theme_item(theme: dict, current: str) -> str:
    name = theme["name"]
    flags = []
    if theme["fx"]:
        flags.append("fx")
    if theme["rules"]:
        flags.append("custom")
    fx = '<span class="fx">fx</span>' if theme["fx"] else ""
    return (
        f'<button type="button" class="theme-item" data-theme-name="{esc(name)}"'
        f' data-name="{esc(name.lower())}" data-flags="{esc(" ".join(flags))}"'
        f' aria-current="{"true" if name == current else "false"}"'
        f' style="{swatch_vars(theme["swatch"])}">'
        f'{swatches(theme["swatch"])}<span class="theme-name">{esc(name)}</span>{fx}'
        "</button>"
    )


def preview_pane(current: str) -> str:
    """A live mock of the page rendered with real site classes, so whichever theme
    is hovered in the picker shows up here. Its links are inert (CSS disables
    pointer events) but point at real destinations so no anchor is dead."""
    return (
        f'<div class="theme-preview" id="theme-preview" data-theme="{esc(current)}">'
        '<div class="brand"><span class="brand-inner">'
        '<span class="brand-name">Kavin Sriraj</span></span></div>'
        '<p class="brand-sub">Final-year Electrical Engineering student &middot; Singapore</p>'
        '<ul class="site-nav">'
        '<li><a data-nav-item="about" href="index.html#about">about</a></li>'
        '<li><a data-nav-item="publications" href="index.html#publications">papers</a></li>'
        '<li><a data-nav-item="projects" href="index.html#projects">projects</a></li>'
        '<li><a data-nav-item="experience" href="index.html#experience">experience</a></li>'
        '<li><a data-nav-item="themes" href="themes.html">themes</a></li>'
        '<li><a data-nav-item="contact" href="index.html#contact">contact</a></li>'
        "</ul>"
        '<p class="preview-line">Fault diagnosis, computer vision and embedded '
        "firmware.</p>"
        "</div>"
    )


def theme_section(current: str) -> str:
    rows = "".join(theme_item(t, current) for t in THEMES)
    return section(
        "themes", "Theme",
        f'<p class="small dim">All {len(THEMES)} Monkeytype themes, with the exact '
        "upstream colour tokens and each theme&rsquo;s own custom CSS. Hover to "
        "preview, click to wear it; the choice is stored locally in your browser "
        "and follows you back to the "
        '<a href="index.html">portfolio</a>. Press <kbd>/</kbd> to search.</p>'
        + '<noscript><p class="small">JavaScript is off, so the picker cannot '
          f'switch themes: you are seeing <strong>{esc(current)}</strong>. The '
          "list below still shows every theme.</p></noscript>"
        + preview_pane(current)
        + '<div class="theme-toolbar">'
          '<input type="search" id="theme-search" placeholder="search themes"'
          ' autocomplete="off" spellcheck="false" aria-label="search themes">'
          '<select id="theme-filter" aria-label="filter themes">'
          '<option value="all">all themes</option>'
          '<option value="custom">custom css</option>'
          '<option value="fx">with effects</option>'
          "</select>"
          '<button type="button" id="theme-random">random</button>'
          f'<span class="theme-count" id="theme-count">{len(THEMES)} of '
          f"{len(THEMES)} themes</span>"
          "</div>"
        + f'<div class="theme-list" id="theme-list">{rows}</div>'
        + '<p class="small dim theme-empty" id="theme-empty" hidden>'
          "No theme by that name.</p>",
    )


# ----------------------------------------------------------------------- shell

def nav_html(current: str = "") -> str:
    items = [
        ("about", "about", "index.html#about"),
        ("thesis", "thesis", "index.html#thesis"),
        ("publications", "papers", "index.html#publications"),
        ("projects", "projects", "index.html#projects"),
        ("experience", "experience", "index.html#experience"),
        ("education", "education", "index.html#education"),
        ("themes", "themes", "themes.html"),
        ("contact", "contact", f'mailto:{C.CONTACT["email"]}'),
    ]
    lis = "".join(
        f'<li><a href="{esc(href)}" data-nav-item="{esc(slot)}"'
        f'{" aria-current=\"true\"" if slot == current else ""}>'
        f"{esc(label)}</a></li>"
        for slot, label, href in items
    )
    return f'<ul class="site-nav">{lis}</ul>'


def header_html(current: str = "") -> str:
    c = C.CONTACT
    return (
        '<header class="site-header">'
        '<h1 class="brand"><span class="brand-inner">'
        f'<span class="brand-name">{esc(C.NAME)}</span></span></h1>'
        f'<p class="brand-sub">{esc(C.TAGLINE)}</p>'
        '<div class="header-links">'
        f'<span>{esc(C.LOCATION)}</span>'
        f'<a href="mailto:{esc(c["email"])}">{esc(c["email"])}</a>'
        f'<a href="{esc(c["github"])}">github/{esc(c["github_handle"])}</a>'
        f'<a href="{esc(c["linkedin"])}">linkedin/{esc(c["linkedin_handle"])}</a>'
        f'<a href="{esc(c["cv"])}">cv.pdf</a>'
        "</div>" + nav_html(current) + "</header>"
    )


def footer_html(current: str) -> str:
    c = C.CONTACT
    return (
        '<footer class="site-footer" id="contact">'
        f'<span>theme <span class="theme-current" id="theme-current">'
        f"{esc(current)}</span></span>"
        f'<a href="themes.html">{len(THEMES)} Monkeytype themes</a>'
        f'<a href="mailto:{esc(c["email"])}">{esc(c["email"])}</a>'
        f'<a href="{esc(c["github"])}">github</a>'
        f'<a href="{esc(c["linkedin"])}">linkedin</a>'
        "</footer>"
    )


def shell(title: str, body: str, description: str) -> str:
    return (
        "<!doctype html>\n"
        f'<html lang="en" data-theme="{DEFAULT_THEME}">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{esc(title)}</title>\n"
        f'<meta name="description" content="{esc(description)}">\n'
        f'<link rel="icon" href="{FAVICON}">\n'
        '<link rel="stylesheet" href="static/style.css">\n'
        '<link rel="stylesheet" href="static/themes.css">\n'
        f"{NO_FLASH}\n"
        '<script src="static/app.js" defer></script>\n'
        "</head>\n"
        f"<body>\n{body}\n</body>\n</html>\n"
    )


def index_page() -> str:
    # the two columns are balanced by measured height: About + Thesis +
    # Publications + Skills against Education + Experience + Projects. The
    # thesis leads the papers: it is the newer, larger piece of work.
    left = about_html() + thesis_html() + publications_html() + skills_html()
    right = education_html() + experience_html() + projects_html()
    body = (
        header_html()
        + "<main>"
        + '<div class="works-row">'
        + f'<div class="works-col">{left}</div>'
        + f'<div class="works-col">{right}</div>'
        + "</div>"
        + "</main>"
        + footer_html(DEFAULT_THEME)
    )
    return shell(
        f"{C.NAME} \u00b7 Electrical Engineering",
        body,
        "Kavin Sriraj, final-year Electrical Engineering student at the National "
        "University of Singapore. Thesis, publications, projects and experience.",
    )


def themes_page() -> str:
    """The theme picker lives on its own page: the portfolio stays a portfolio,
    and this page is itself the preview of whatever theme is picked."""
    body = (
        header_html("themes")
        + "<main>"
        + theme_section(DEFAULT_THEME)
        + "</main>"
        + footer_html(DEFAULT_THEME)
    )
    return shell(
        "Themes \u00b7 " + C.NAME,
        body,
        f"All {len(THEMES)} Monkeytype themes, with their upstream colour tokens "
        "and custom CSS, to preview and apply.",
    )


def not_found_page() -> str:
    body = (
        header_html()
        + '<main><section class="section"><h2>404</h2>'
        '<p>Nothing at that address. <a href="./">Back to the portfolio</a>.</p>'
        "</section></main>"
        + footer_html(DEFAULT_THEME)
    )
    return shell("Not found", body, "Page not found.")
