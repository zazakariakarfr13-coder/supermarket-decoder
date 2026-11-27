#!/usr/bin/env python3
"""Shared language markup for every public page, and the multilingual sitemap.

Usage:
  py -3 scripts/i18n_pages.py          rewrite the marker blocks on every page and sitemap.xml
  py -3 scripts/i18n_pages.py --check  exit 1 if anything would change (used by check_site.py)

English pages live where they always did; French twins under fr/, Arabic under ar/ (same file names).
On each page this script owns:
  - <html lang> (and dir="rtl" for Arabic), the canonical and og:url (own language),
  - a block before </head> between <!--i18n:head--> markers: hreflang links, og:locale, language styles,
  - a block right after <body> between <!--i18n:switch--> markers: the EN · FR · عربي switcher.
Only twins that exist are linked, so pages can be translated one by one.
"""
from __future__ import annotations

import posixpath
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://zazakariakarfr13-coder.github.io/supermarket-decoder"
LANGS = ("en", "fr", "ar")
PREFIX = {"en": "", "fr": "fr/", "ar": "ar/"}
LOCALE = {"en": "en_US", "fr": "fr_FR", "ar": "ar_AR"}
LABEL = {"en": "EN", "fr": "FR", "ar": "عربي"}
ARIA = {"en": "Language", "fr": "Langue", "ar": "اللغة"}

_HEAD = re.compile(r"<!--i18n:head-->.*?<!--/i18n:head-->", re.S)
_SWITCH = re.compile(r"<!--i18n:switch-->.*?<!--/i18n:switch-->", re.S)
_HTML = re.compile(r"<html\b[^>]*>")
_BODY = re.compile(r"<body\b[^>]*>")
_CANON = re.compile(r'(<link rel="canonical" href=")[^"]*(")')
_OGURL = re.compile(r'(<meta property="og:url" content=")[^"]*(")')


def lang_of(path: str) -> str:
    first = path.split("/", 1)[0]
    return first if first in ("fr", "ar") else "en"


def base_of(path: str) -> str:
    return path[len(PREFIX[lang_of(path)]):]


def twin(path: str, lang: str) -> str:
    return PREFIX[lang] + base_of(path)


def page_url(path: str) -> str:
    return f"{SITE}/{path[: -len('index.html')] if path.endswith('index.html') else path}"


def rel(from_path: str, to_path: str) -> str:
    return posixpath.relpath(to_path, posixpath.dirname(from_path) or ".")


def public_pages(root: Path = ROOT) -> list[str]:
    """English pages listed in the sitemap today, in sitemap order (the 404 and redirects are not public)."""
    text = (root / "sitemap.xml").read_text(encoding="utf-8")
    out = []
    for loc in re.findall(r"<loc>([^<]+)</loc>", text):
        p = loc[len(SITE) + 1:] if loc.startswith(SITE + "/") else None
        if p is None or lang_of(p) != "en":
            continue
        p = p + "index.html" if p == "" or p.endswith("/") else p
        if p not in out:
            out.append(p)
    return out


class Site:
    def __init__(self, root: Path = ROOT, pages: list[str] | None = None):
        self.root = Path(root)
        self.pages = pages if pages is not None else public_pages(self.root)

    def exists(self, path: str) -> bool:
        return (self.root / path).is_file()

    def langs_for(self, base: str) -> list[str]:
        return [lang for lang in LANGS if self.exists(twin(base, lang))]

    def head_block(self, path: str) -> str:
        lang, base = lang_of(path), base_of(path)
        have = self.langs_for(base)
        lines = []
        if len(have) > 1:
            lines += [f'<link rel="alternate" hreflang="{l}" href="{page_url(twin(base, l))}">' for l in have]
            lines.append(f'<link rel="alternate" hreflang="x-default" href="{page_url(base)}">')
        lines.append(f'<meta property="og:locale" content="{LOCALE[lang]}">')
        lines.append(f'<link rel="stylesheet" href="{rel(path, "assets/i18n.css")}">')
        if lang == "ar":
            lines.append(f'<link rel="stylesheet" href="{rel(path, "assets/lang-ar.css")}">')
        return "<!--i18n:head-->" + "".join(lines) + "<!--/i18n:head-->"

    def switcher(self, path: str) -> str:
        lang, base = lang_of(path), base_of(path)
        items = []
        for other in self.langs_for(base):
            if other == lang:
                items.append(f'<span aria-current="true">{LABEL[other]}</span>')
            else:
                items.append(f'<a href="{rel(path, twin(base, other))}" hreflang="{other}" lang="{other}">{LABEL[other]}</a>')
        if len(items) < 2:
            return ""
        return (f'<!--i18n:switch--><nav class="lang-switch" aria-label="{ARIA[lang]}">' + "".join(items)
                + "</nav><!--/i18n:switch-->")

    def apply(self, text: str, path: str) -> str:
        lang = lang_of(path)
        text = _SWITCH.sub("", _HEAD.sub("", text))
        text = _HTML.sub(f'<html lang="{lang}" dir="rtl">' if lang == "ar" else f'<html lang="{lang}">', text, count=1)
        text = _CANON.sub(lambda m: m.group(1) + page_url(path) + m.group(2), text, count=1)
        text = _OGURL.sub(lambda m: m.group(1) + page_url(path) + m.group(2), text, count=1)
        text = text.replace("</head>", self.head_block(path) + "</head>", 1)
        switch = self.switcher(path)
        if switch:
            m = _BODY.search(text)
            text = text[: m.end()] + switch + text[m.end():]
        return text

    def all_paths(self) -> list[str]:
        return [twin(p, l) for p in self.pages for l in LANGS if self.exists(twin(p, l))]

    def sitemap(self) -> str:
        urls = []
        for base in self.pages:
            have = self.langs_for(base)
            alts = ""
            if len(have) > 1:
                alts = "".join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{page_url(twin(base, l))}"/>' for l in have)
                alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="{page_url(base)}"/>'
            urls += [f"  <url><loc>{page_url(twin(base, l))}</loc>{alts}</url>" for l in have]
        return ('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
                + "\n".join(urls) + "\n</urlset>\n")

    def changes(self) -> dict[str, str]:
        """{relative path: new text} for every file that would change."""
        out = {}
        for path in self.all_paths():
            f = self.root / path
            old = f.read_text(encoding="utf-8")
            new = self.apply(old, path)
            if new != old:
                out[path] = new
        sm = self.root / "sitemap.xml"
        new_sm = self.sitemap()
        if sm.read_text(encoding="utf-8") != new_sm:
            out["sitemap.xml"] = new_sm
        return out


def main(argv: list[str]) -> int:
    site = Site()
    changes = site.changes()
    if "--check" in argv:
        for p in changes:
            print(f"out of date: {p} (run py -3 scripts/i18n_pages.py)")
        return 1 if changes else 0
    for p, text in changes.items():
        (ROOT / p).write_text(text, encoding="utf-8", newline="\n")
    print(f"Updated {len(changes)} files; {len(site.all_paths())} pages in {len(LANGS)} languages.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
