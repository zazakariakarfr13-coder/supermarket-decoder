"""Build assets/search-index.json: every public page with its title, description and menu group.

Usage: python scripts/make_search_index.py      (re-run after adding or renaming a page)
The homepage search and the menu on every page (assets/nav.js) read this file.
scripts/check_site.py fails if the committed file is out of date.
"""
from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "search-index.json"
SKIP_DIRS = {".git", "graphify-out", "node_modules", "scripts"}

GROUPS = ["Start here", "Free guides", "Articles", "E-numbers", "Comic & stories", "About"]
FIXED = {  # path -> (group, label)
    "index.html": ("Start here", "Home"),
    "decoder/index.html": ("Start here", "Ingredient Decoder (free tool)"),
    "free-resources/index.html": ("Start here", "All free resources"),
    "additives/index.html": ("E-numbers", "All E-number pages"),
    "story/index.html": ("Comic & stories", "Comic: Episode 01"),
    "story/episode-02.html": ("Comic & stories", "Comic: Episode 02, Liquid Alibis"),
    "about.html": ("About", "About"),
    "sources.html": ("About", "Sources"),
}
FOLDER_GROUP = {"free-resources": "Free guides", "articles": "Articles", "additives": "E-numbers",
                "stories": "Comic & stories", "story": "Comic & stories"}


def _first(pattern: str, html: str) -> str:
    m = re.search(pattern, html, re.S | re.I)
    return unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else ""


def page_entry(path: Path) -> dict | None:
    rel = path.relative_to(ROOT).as_posix()
    html = path.read_text(encoding="utf-8", errors="replace")
    if rel == "404.html" or re.search(r'<meta[^>]+name="robots"[^>]+noindex', html, re.I):
        return None
    title = _first(r"<title>(.*?)</title>", html)
    desc = _first(r'<meta[^>]+name="description"[^>]+content="([^"]*)"', html)
    h1 = _first(r"<h1[^>]*>(.*?)</h1>", html)
    if rel in FIXED:
        group, label = FIXED[rel]
    else:
        group = FOLDER_GROUP.get(rel.split("/")[0], "About")
        label = re.split(r"\s+[|—–]\s+", title)[0].strip() or h1
        if group == "E-numbers":
            label = label.split(":")[0].strip()
    url = rel[: -len("index.html")] if rel.endswith("index.html") else rel
    return {"u": url, "t": label, "g": group, "k": " ".join(x for x in (title, h1, desc) if x)}


def build_index() -> dict:
    pages = []
    for path in sorted(ROOT.rglob("*.html")):
        if SKIP_DIRS & set(path.relative_to(ROOT).parts):
            continue
        entry = page_entry(path)
        if entry:
            pages.append(entry)
    order = {g: i for i, g in enumerate(GROUPS)}
    fixed_first = {rel: i for i, rel in enumerate(FIXED)}
    def rel_of(u: str) -> str:
        return u if u.endswith(".html") else u + "index.html"
    pages.sort(key=lambda p: (order[p["g"]], fixed_first.get(rel_of(p["u"]), 99), p["t"].lower()))
    return {"groups": GROUPS, "pages": pages}


def render() -> str:
    return json.dumps(build_index(), ensure_ascii=False, indent=1) + "\n"


if __name__ == "__main__":
    OUT.write_text(render(), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(build_index()['pages'])} pages)")
