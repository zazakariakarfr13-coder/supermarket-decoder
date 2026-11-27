"""Build the search indexes: every public page with its title, description and menu group, one file per
language: assets/search-index.json (English), search-index.fr.json, search-index.ar.json.

Usage: python scripts/make_search_index.py      (re-run after adding or renaming a page)
The homepage search and the menu on every page (assets/nav.js) read these files.
scripts/check_site.py fails if a committed file is out of date.
"""
from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANGS = ("en", "fr", "ar")
PREFIX = {"en": "", "fr": "fr/", "ar": "ar/"}


def out_file(lang: str) -> Path:
    return ROOT / "assets" / ("search-index.json" if lang == "en" else f"search-index.{lang}.json")


SKIP_DIRS = {".git", "graphify-out", "node_modules", "scripts"}

GROUPS = ["Start here", "Free guides", "Articles", "E-numbers", "Factory vs. Kitchen", "Comic & stories", "About"]
FIXED = {  # path -> (group, label)
    "index.html": ("Start here", "Home"),
    "decoder/index.html": ("Start here", "Ingredient Decoder (free tool)"),
    "free-resources/index.html": ("Start here", "All free resources"),
    "additives/index.html": ("E-numbers", "All E-number pages"),
    "factory-vs-kitchen/index.html": ("Factory vs. Kitchen", "All Factory vs. Kitchen foods"),
    "story/index.html": ("Comic & stories", "Comic: Episode 01"),
    "story/episode-02.html": ("Comic & stories", "Comic: Episode 02, Liquid Alibis"),
    "about.html": ("About", "About"),
    "sources.html": ("About", "Sources"),
}
FOLDER_GROUP = {"free-resources": "Free guides", "articles": "Articles", "additives": "E-numbers", "factory-vs-kitchen": "Factory vs. Kitchen",
                "stories": "Comic & stories", "story": "Comic & stories"}

# Menu groups and fixed labels in French and Arabic (same order as English).
GROUP_TR = {
    "fr": ["Pour commencer", "Guides gratuits", "Articles", "Additifs (E)", "Usine ou cuisine", "BD et histoires", "À propos"],
    "ar": ["ابدأ من هنا", "أدلة مجانية", "مقالات", "الإضافات (E)", "المصنع أم المطبخ", "قصص مصوّرة", "من نحن"],
}
LABEL_TR = {
    "fr": {"Home": "Accueil", "Ingredient Decoder (free tool)": "Décodeur d’ingrédients (outil gratuit)",
           "All free resources": "Toutes les ressources gratuites", "All E-number pages": "Toutes les fiches additifs",
           "All Factory vs. Kitchen foods": "Tous les produits Usine ou cuisine", "Comic: Episode 01": "BD : épisode 01",
           "Comic: Episode 02, Liquid Alibis": "BD : épisode 02, Alibis liquides", "About": "À propos", "Sources": "Sources"},
    "ar": {"Home": "الرئيسية", "Ingredient Decoder (free tool)": "مفكّك المكوّنات (أداة مجانية)",
           "All free resources": "كل الموارد المجانية", "All E-number pages": "كل صفحات الإضافات",
           "All Factory vs. Kitchen foods": "كل منتجات المصنع أم المطبخ", "Comic: Episode 01": "قصة مصوّرة: الحلقة 01",
           "Comic: Episode 02, Liquid Alibis": "قصة مصوّرة: الحلقة 02، حُجج سائلة", "About": "من نحن", "Sources": "المصادر"},
}


def groups(lang: str) -> list[str]:
    return GROUPS if lang == "en" else GROUP_TR[lang]


def _tr_group(group: str, lang: str) -> str:
    return group if lang == "en" else GROUP_TR[lang][GROUPS.index(group)]


def _first(pattern: str, html: str) -> str:
    m = re.search(pattern, html, re.S | re.I)
    return unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else ""


def page_entry(path: Path, lang: str = "en") -> dict | None:
    rel = path.relative_to(ROOT).as_posix()[len(PREFIX[lang]):]
    html = path.read_text(encoding="utf-8", errors="replace")
    if rel == "404.html" or re.search(r'<meta[^>]+name="robots"[^>]+noindex', html, re.I):
        return None
    title = _first(r"<title>(.*?)</title>", html)
    desc = _first(r'<meta[^>]+name="description"[^>]+content="([^"]*)"', html)
    h1 = _first(r"<h1[^>]*>(.*?)</h1>", html)
    if rel in FIXED:
        group, label = FIXED[rel]
        label = label if lang == "en" else LABEL_TR[lang][label]
    else:
        group = FOLDER_GROUP.get(rel.split("/")[0], "About")
        label = re.split(r"\s+[|—–]\s+", title)[0].strip() or h1
        if group == "E-numbers":
            label = label.split(":")[0].strip()
    url = PREFIX[lang] + (rel[: -len("index.html")] if rel.endswith("index.html") else rel)
    return {"u": url, "t": label, "g": _tr_group(group, lang), "k": " ".join(x for x in (title, h1, desc) if x)}


def _lang_of(parts: tuple) -> str:
    return parts[0] if parts and parts[0] in ("fr", "ar") else "en"


def build_index(lang: str = "en") -> dict:
    pages = []
    for path in sorted(ROOT.rglob("*.html")):
        parts = path.relative_to(ROOT).parts
        if SKIP_DIRS & set(parts) or _lang_of(parts) != lang:
            continue
        entry = page_entry(path, lang)
        if entry:
            pages.append(entry)
    order = {g: i for i, g in enumerate(groups(lang))}
    fixed_first = {rel: i for i, rel in enumerate(FIXED)}
    def rel_of(u: str) -> str:
        u = u[len(PREFIX[lang]):]
        return u if u.endswith(".html") else u + "index.html"
    pages.sort(key=lambda p: (order[p["g"]], fixed_first.get(rel_of(p["u"]), 99), p["t"].lower()))
    return {"groups": groups(lang), "pages": pages}


def render(lang: str = "en") -> str:
    return json.dumps(build_index(lang), ensure_ascii=False, indent=1) + "\n"


if __name__ == "__main__":
    for lang in LANGS:
        out_file(lang).write_text(render(lang), encoding="utf-8")
        print(f"wrote {out_file(lang).relative_to(ROOT)} ({len(build_index(lang)['pages'])} pages)")
