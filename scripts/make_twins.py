#!/usr/bin/env python3
"""Build the French and Arabic twins of the hand-written pages from their English originals.

Each translation lives in scripts/i18n/<lang>/pages/<name>.py:
    PAGE = "articles/e-numbers-explained.html"      # the English page
    R = [("English text", "texte français"), ...]     # replacements, applied in order (all occurrences)
The twin is written to <lang>/<PAGE>. Links to other pages stay relative (they point to the twins); links to
shared files (assets/, favicon.svg, gallery/, pins/) get one more "../". The build fails if an English piece
is no longer on the page (the English page changed: update the translation) or if a pair changes a number.

Usage: py -3 scripts/make_twins.py [--check]     (--check: exit 1 if any twin is out of date)
"""
from __future__ import annotations

import importlib
import pkgutil
import posixpath
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from i18n import guard  # noqa: E402

SHARED = ("assets/", "favicon.svg", "gallery/", "pins/", "robots.txt")
_URL = re.compile(r'((?:href|src)=")([^"#?]*)([^"]*")')
_UTM = re.compile(r"utm_content=[^&\"]*")


def shared_target(page: str, url: str) -> bool:
    if not url or url.startswith(("http:", "https:", "mailto:", "data:", "//", "/")):
        return False
    target = posixpath.normpath(posixpath.join(posixpath.dirname(page), url))
    return target.startswith(SHARED) or target in SHARED


def build(page: str, pairs, lang: str) -> str:
    text = (ROOT / page).read_text(encoding="utf-8").replace("\r\n", "\n")
    for i, (en, xx) in enumerate(pairs):
        if en not in text:
            raise ValueError(f"{lang}/{page}: piece {i} not found in the English page (it changed?): {en[:70]!r}")
        # the Gumroad tracking tag gets a language suffix (utm_content=x-fr): compare links without it
        guard.same(f"{lang}/{page}[{i}]", _UTM.sub("utm_content=", en), _UTM.sub("utm_content=", xx))
        text = text.replace(en, xx)
    return _URL.sub(lambda m: m.group(1) + ("../" + m.group(2) if shared_target(page, m.group(2)) else m.group(2)) + m.group(3), text)


def translations(lang: str):
    folder = ROOT / "scripts" / "i18n" / lang / "pages"
    if not folder.is_dir():
        return []
    mods = []
    for m in sorted(pkgutil.iter_modules([str(folder)]), key=lambda m: m.name):
        mods.append(importlib.import_module(f"i18n.{lang}.pages.{m.name}"))
    return mods


def main(argv) -> int:
    stale = []
    for lang in ("fr", "ar"):
        for mod in translations(lang):
            out = ROOT / lang / mod.PAGE
            html = build(mod.PAGE, mod.R, lang)
            if "--check" in argv:
                import i18n_pages
                site = i18n_pages.Site()
                current = out.read_text(encoding="utf-8") if out.is_file() else ""
                if site.apply(html, f"{lang}/{mod.PAGE}") != current:
                    stale.append(f"{lang}/{mod.PAGE}")
                continue
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(html, encoding="utf-8", newline="\n")
            print("wrote", f"{lang}/{mod.PAGE}")
    if "--check" in argv:
        for s in stale:
            print(f"out of date: {s} (run py -3 scripts/make_twins.py)")
        return 1 if stale else 0
    import i18n_pages
    return i18n_pages.main([])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
