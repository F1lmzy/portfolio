"""HTML rendering for a single static page.

Everything is pre-rendered into one file: no server, no fragments, no framework.
The small amount of interactivity (theme switching, live theme search, the two
filters) is local state, so it lives in static/app.js and this module only has to
emit the markup that script works against. All URLs are relative, so the same
build works at a domain root or under /<repo>/ on GitHub Pages.
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


def slug(text: str) -> str:
    out = []
    for ch in text.lower():
        if ch.isalnum():
            out.append(ch)
        elif out and out[-1] != "-":
            out.append("-")
    return "".join(out).strip("-")


def swatches(colours: list[str]) -> str:
    """Six colour chips. The values ride on the parent as custom properties, which
    keeps a 187-row list much smaller than six inline background styles per row."""
    return ('<span class="swatches" aria-hidden="true">'
            + "<i></i>" * len(colours[:6]) + "</span>")


def swatch_vars(colours: list[str]) -> str:
    return "".join(f"--sw{n}:{c};" for n, c in enumerate(colours[:6], 1))


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
    is hovered in the picker shows up here."""
    return (
        f'<div class="theme-preview" id="theme-preview" data-theme="{esc(current)}">'
        '<div class="brand"><span class="brand-inner">'
        '<span class="brand-name">Kavin Sriraj</span></span>'
        '<span class="caret" aria-hidden="true"></span></div>'
        '<p class="brand-sub">Electrical Engineering undergraduate &middot; Singapore</p>'
        '<ul class="site-nav">'
        '<li><a data-nav-item="about" href="#about">about</a></li>'
        '<li><a data-nav-item="publications" href="#publications">papers</a></li>'
        '<li><a data-nav-item="projects" href="#projects">projects</a></li>'
        '<li><a data-nav-item="experience" href="#experience">experience</a></li>'
        '<li><a data-nav-item="themes" href="#themes">themes</a></li>'
        '<li><a data-nav-item="contact" href="#contact">contact</a></li>'
        "</ul>"
        '<p class="preview-line">Deformable 4D Gaussians fitted to monocular video, '
        'rendered as stereo pairs.<span class="caret" aria-hidden="true"></span></p>'
        '<p class="preview-line dim">PSNR &middot; SSIM &middot; LPIPS &middot; '
        "temporal flicker &middot; stereo consistency</p>"
        "</div>"
    )


def theme_section(current: str) -> str:
    rows = "".join(theme_item(t, current) for t in THEMES)
    return section(
        "themes", "Theme",
        '<p class="small dim">Every Monkeytype theme, all '
        f"{len(THEMES)} of them, with the exact upstream colour tokens and each "
        "theme&rsquo;s own custom CSS carried over. Hover to preview, click to "
        "wear it; the choice is stored locally in your browser.</p>"
        + '<noscript><p class="small">JavaScript is off, so the picker cannot '
          f'switch themes: you are seeing <strong>{esc(current)}</strong>. The rest '
          "of the page works normally.</p></noscript>"
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
        f"{len(THEMES)} Monkeytype themes",
    )


# ------------------------------------------------------------------- sections

def section_head(section_id: str, title: str, note: str = "") -> str:
    n = f'<span class="section-note">{esc(note)}</span>' if note else ""
    return f'<h2 id="{esc(section_id)}">{esc(title)}{n}</h2>'


def section(section_id: str, title: str, body: str, note: str = "") -> str:
    return (
        f'<section class="section" id="{esc(section_id)}">'
        f"{section_head(section_id, title, note)}{body}</section>"
    )


def drawer(rows: list[str], label: str = "more") -> str:
    return (
        f'<details class="drawer"><summary>{esc(label)}</summary>'
        f'<div class="drawer-body">{"".join(rows)}</div></details>'
    )


def filter_nav(kind: str, options: list[tuple[str, str]], active: str = "all") -> str:
    """Buttons, not links: this is local state, so there is no URL to point at."""
    btns = "".join(
        f'<button type="button" class="filter{" active" if value == active else ""}"'
        f' data-{esc(kind)}="{esc(value)}" aria-pressed="'
        f'{"true" if value == active else "false"}">{esc(label)}</button>'
        for value, label in options
    )
    return f'<div class="filter-nav" data-filter="{esc(kind)}">{btns}</div>'


def about_html() -> str:
    paras = "".join(f"<p>{esc(p)}</p>" for p in C.ABOUT)
    return section("about", "About", paras)


def publication_entry(pub: dict) -> str:
    authors = ", ".join(
        f'<strong>{esc(a)}</strong>' if a == pub["me"] else esc(a)
        for a in pub["authors"]
    )
    topics = "".join(f'<span class="tag">{esc(t)}</span>' for t in pub["topics"])
    keys = " ".join(slug(t) for t in pub["topics"])
    return (
        f'<article class="entry" data-topics="{esc(keys)}">'
        f'<div class="year-col">{pub["year"]}</div>'
        '<div class="entry-body">'
        f'<div class="entry-title"><a href="{esc(pub["doi_url"])}">'
        f'{esc(pub["title"])}</a></div>'
        f'<div class="entry-meta">{authors}</div>'
        f'<div class="entry-meta"><em>{esc(pub["venue"])}</em> {esc(pub["volume"])}:'
        f' {esc(pub["pages"])} &middot; {esc(pub["month"])} {pub["year"]}</div>'
        f'<div class="entry-note">{esc(pub["summary"])}</div>'
        f'<div class="tags">{topics}</div>'
        '<div class="entry-links">'
        f'<a href="{esc(pub["doi_url"])}">doi.org/{esc(pub["doi"])}</a>'
        f'<span class="cite-count">cited by {pub["citations"]}</span>'
        "</div></div></article>"
    )


def publications_html() -> str:
    pubs = sorted(C.PUBLICATIONS, key=lambda p: -p["year"])
    options = [("all", "all")] + [(slug(t), t.lower()) for t in C.PUBLICATION_TOPICS]
    cites = sum(p["citations"] for p in C.PUBLICATIONS)
    return section(
        "publications", "Publications",
        filter_nav("topic", options)
        + f'<div class="listing" id="pub-list">'
        + "".join(publication_entry(p) for p in pubs)
        + "</div>",
        f"{len(C.PUBLICATIONS)} journals \u00b7 {cites} citations",
    )


def thesis_html() -> str:
    t = C.THESIS
    bullets = "".join(f"<li>{esc(b)}</li>" for b in t["bullets"])
    tags = "".join(f'<span class="tag">{esc(s)}</span>' for s in t["stack"])
    return section(
        "thesis", "Bachelor Thesis",
        '<article class="entry"><div class="year-col">Thesis</div>'
        '<div class="entry-body">'
        f'<div class="entry-title">{esc(t["title"])}</div>'
        f'<div class="entry-meta">{esc(t["org"])} &middot; {esc(t["start"])}'
        f' &ndash; {esc(t["end"])}</div>'
        f'<div class="entry-note">{esc(t["summary"])}</div>'
        f'<ul class="bullets">{bullets}</ul>'
        f'<div class="tags">{tags}</div>'
        f'<div class="entry-links"><a href="{esc(t["repo"])}">repository</a></div>'
        "</div></article>",
        f'{t["start"]} \u2013 {t["end"]}',
    )


def project_entry(p: dict) -> str:
    bullets = "".join(f"<li>{esc(b)}</li>" for b in p["detail"])
    tags = "".join(f'<span class="tag">{esc(s)}</span>' for s in p["stack"])
    if p["repo"]:
        repo_link = f'<a href="{esc(p["repo"])}">{esc(p["repo_label"])}</a>'
    else:
        repo_link = f'<span class="dim">{esc(p["repo_label"])}</span>'
    return (
        f'<article class="entry" data-kind="{esc(slug(p["kind"]))}">'
        f'<div class="year-col">{p["year"]}</div>'
        '<div class="entry-body">'
        f'<div class="entry-title">{esc(p["name"])}</div>'
        f'<div class="entry-meta">{esc(p["kind"])}</div>'
        f'<div class="entry-note">{esc(p["summary"])}</div>'
        f'<div class="tags">{tags}</div>'
        f'<div class="entry-links">{repo_link}</div>'
        + drawer([f'<ul class="bullets">{bullets}</ul>'])
        + "</div></article>"
    )


def projects_html() -> str:
    items = sorted(C.PROJECTS, key=lambda p: (-p["year"], p["name"]))
    kinds: list[tuple[str, str]] = []
    for p in C.PROJECTS:
        key = slug(p["kind"])
        if key not in [k for k, _ in kinds]:
            kinds.append((key, p["kind"].lower()))
    options = [("all", "all")] + kinds
    repos = sum(1 for p in C.PROJECTS if p["repo"])
    return section(
        "projects", "Projects",
        filter_nav("kind", options)
        + '<div class="listing" id="project-list">'
        + "".join(project_entry(p) for p in items)
        + "</div>",
        f"{len(items)} entries \u00b7 {repos} with public repositories",
    )


def experience_html() -> str:
    rows = []
    for job in C.EXPERIENCE:
        bullets = "".join(f"<li>{esc(b)}</li>" for b in job["bullets"])
        tags = "".join(f'<span class="tag">{esc(s)}</span>' for s in job["stack"])
        rows.append(
            '<article class="entry">'
            f'<div class="year-col">{esc(job["start"][-4:])}</div>'
            '<div class="entry-body">'
            f'<div class="entry-title">{esc(job["role"])}</div>'
            f'<div class="entry-meta">{esc(job["org"])} &middot; {esc(job["place"])}'
            f' &middot; {esc(job["start"])} &ndash; {esc(job["end"])}</div>'
            f'<div class="entry-note">{esc(job["summary"])}</div>'
            f'<ul class="bullets">{bullets}</ul>'
            f'<div class="tags">{tags}</div></div></article>'
        )
    return section("experience", "Experience",
                   f'<div class="listing">{"".join(rows)}</div>')


def education_html() -> str:
    rows = []
    for ed in C.EDUCATION:
        rows.append(
            '<article class="entry">'
            f'<div class="year-col">{esc(ed["start"][-4:])}</div>'
            '<div class="entry-body">'
            f'<div class="entry-title">{esc(ed["school"])}</div>'
            f'<div class="entry-meta">{esc(ed["degree"])}</div>'
            f'<div class="entry-meta">{esc(ed["start"])} &ndash; {esc(ed["end"])}'
            f' &middot; {esc(ed["place"])}</div>'
            f'<div class="entry-note">{esc(ed["detail"])}</div>'
            "</div></article>"
        )
    return section("education", "Education",
                   f'<div class="listing">{"".join(rows)}</div>')


def skills_html() -> str:
    rows = []
    for label, items in C.SKILLS:
        tags = "".join(f'<span class="tag">{esc(i)}</span>' for i in items)
        rows.append(
            '<article class="entry">'
            f'<div class="year-col">{esc(label)}</div>'
            f'<div class="entry-body"><div class="tags">{tags}</div></div></article>'
        )
    return section("skills", "Technical Skills",
                   f'<div class="listing">{"".join(rows)}</div>')


# ----------------------------------------------------------------------- shell

def nav_html() -> str:
    items = [
        ("about", "about", "#about"),
        ("publications", "papers", "#publications"),
        ("thesis", "thesis", "#thesis"),
        ("projects", "projects", "#projects"),
        ("experience", "experience", "#experience"),
        ("education", "education", "#education"),
        ("themes", "themes", "#themes"),
        ("contact", "contact", f'mailto:{C.CONTACT["email"]}'),
    ]
    lis = "".join(
        f'<li><a href="{esc(href)}" data-nav-item="{esc(slot)}">{esc(label)}</a></li>'
        for slot, label, href in items
    )
    return f'<ul class="site-nav">{lis}</ul>'


def header_html() -> str:
    c = C.CONTACT
    return (
        '<header class="site-header">'
        '<h1 class="brand"><span class="brand-inner">'
        f'<span class="brand-name">{esc(C.NAME)}</span></span>'
        '<span id="caret" aria-hidden="true"></span></h1>'
        f'<p class="brand-sub">{esc(C.TAGLINE)}</p>'
        '<div class="header-links">'
        f'<span>{esc(C.LOCATION)}</span>'
        f'<a href="mailto:{esc(c["email"])}">{esc(c["email"])}</a>'
        f'<a href="{esc(c["github"])}">github/{esc(c["github_handle"])}</a>'
        f'<a href="{esc(c["linkedin"])}">linkedin/{esc(c["linkedin_handle"])}</a>'
        '<a href="cv.pdf">cv.pdf</a>'
        "</div>" + nav_html() + "</header>"
    )


def footer_html(current: str) -> str:
    c = C.CONTACT
    return (
        '<footer class="site-footer" id="contact">'
        f'<span>theme <span class="theme-current" id="theme-current">'
        f"{esc(current)}</span></span>"
        f"<span>{len(THEMES)} Monkeytype themes</span>"
        f'<a href="mailto:{esc(c["email"])}">{esc(c["email"])}</a>'
        f'<a href="{esc(c["github"])}">github</a>'
        f'<a href="{esc(c["linkedin"])}">linkedin</a>'
        "<span>static on github pages</span>"
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
    body = (
        header_html()
        + "<main>"
        + about_html()
        + publications_html()
        + thesis_html()
        + projects_html()
        + experience_html()
        + education_html()
        + skills_html()
        + theme_section(DEFAULT_THEME)
        + "</main>"
        + footer_html(DEFAULT_THEME)
    )
    return shell(
        f"{C.NAME} &middot; Electrical Engineering",
        body,
        "Kavin Sriraj, Electrical Engineering undergraduate at the National "
        "University of Singapore. Publications, projects, thesis and experience.",
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
