#!/usr/bin/env python3
"""Text pieces of a hand-written page, for translation by position.

A page's translatable pieces are, in document order: every non-blank text node (outside <script>/<style>) and
the values of title=, alt=, aria-label=, placeholder= and of <meta name="description"> / og:title / og:description /
og:image:alt / twitter:title / twitter:description. A translation module lists the translated pieces in the same order
(T), plus SIG, a fingerprint of the English pieces: if the English page changes, the build stops until the
translation is updated.

Usage: py -3 scripts/segments.py dump articles/e-numbers-explained.html     (numbered pieces + SIG)
"""
from __future__ import annotations

import hashlib
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATTRS = {"title", "alt", "aria-label", "placeholder"}
META = {"description", "og:title", "og:description", "og:image:alt", "twitter:title", "twitter:description"}


class _Scan(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.spans = []  # (start, end) offsets of each piece in the source
        self.skip = 0
        self.lines = [0]

    def feed_text(self, text):
        for m in re.finditer("\n", text):
            self.lines.append(m.end())
        self.src = text
        self.feed(text)
        self.close()

    def _pos(self):
        line, col = self.getpos()
        return self.lines[line - 1] + col

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        start = self._pos()
        raw = self.get_starttag_text() or ""
        d = dict(attrs)
        names = set(ATTRS)
        if tag == "meta" and (d.get("name") in META or d.get("property") in META):
            names = {"content"}
        for m in re.finditer(r'\s([a-zA-Z:-]+)="([^"]*)"', raw):
            if m.group(1) in names and m.group(2).strip():
                self.spans.append((start + m.start(2), start + m.end(2)))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag in ("script", "style"):
            self.skip -= 1

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if self.skip or not data.strip():
            return
        start = self._pos()
        lead = len(data) - len(data.lstrip())
        core = data.strip()
        self.spans.append((start + lead, start + lead + len(core)))


def pieces(html: str):
    s = _Scan()
    s.feed_text(html)
    spans = sorted(set(s.spans))
    return spans, [html[a:b] for a, b in spans]


def signature(texts) -> str:
    return hashlib.sha1("\x1f".join(texts).encode("utf-8")).hexdigest()[:12]


def apply(html: str, translations) -> str:
    spans, texts = pieces(html)
    if len(translations) != len(texts):
        raise ValueError(f"{len(translations)} translated pieces for {len(texts)} English pieces")
    out, last = [], 0
    for (a, b), t in zip(spans, translations):
        out.append(html[last:a])
        out.append(t)
        last = b
    out.append(html[last:])
    return "".join(out)


def main(argv):
    if len(argv) == 3 and argv[1] == "dump":
        html = re.sub(r"<!--i18n:(head|switch)-->.*?<!--/i18n:\1-->", "",
                      (ROOT / argv[2]).read_text(encoding="utf-8").replace("\r\n", "\n"), flags=re.S)
        _, texts = pieces(html)
        print(f"SIG = {signature(texts)!r}  # {len(texts)} pieces")
        for i, t in enumerate(texts):
            print(f"{i}\t{t}")
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
