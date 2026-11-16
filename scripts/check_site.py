#!/usr/bin/env python3
"""Validate local HTML links, page assets and sitemap targets without dependencies."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE_URL = "https://zazakariakarfr13-coder.github.io/Zakaria"


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.targets = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        for attr in ("href", "src"):
            value = attrs.get(attr)
            if value:
                self.targets.append(value)


def resolve_local_target(page: Path, raw_url: str):
    parsed = urlsplit(raw_url.strip())
    if parsed.scheme or parsed.netloc or raw_url.startswith("//"):
        return None, parsed.fragment
    path = unquote(parsed.path)
    if not path:
        target = page
    elif path.startswith("/"):
        # GitHub Pages project paths are rooted below /Zakaria/.
        prefix = "/Zakaria/"
        if not path.startswith(prefix):
            return None, parsed.fragment
        target = ROOT / path[len(prefix):]
    else:
        target = page.parent / path
    if path.endswith("/") or (target.exists() and target.is_dir()):
        target = target / "index.html"
    try:
        target = target.resolve()
        target.relative_to(ROOT.resolve())
    except (ValueError, OSError):
        return None, parsed.fragment
    return target, parsed.fragment


def main():
    errors = []
    pages = sorted(ROOT.rglob("*.html"))
    if not pages:
        errors.append("No HTML pages were found.")

    known_ids = {}
    for page in pages:
        parser = PageParser()
        try:
            parser.feed(page.read_text(encoding="utf-8"))
        except (OSError, UnicodeError) as exc:
            errors.append(f"{page.relative_to(ROOT)}: cannot read page: {exc}")
            continue
        known_ids[page.resolve()] = parser.ids
        for raw in parser.targets:
            target, fragment = resolve_local_target(page, raw)
            if target is None:
                continue
            if not target.is_file():
                errors.append(f"{page.relative_to(ROOT)}: missing local target {raw!r}")
                continue
            if fragment and target.suffix.lower() == ".html":
                target_ids = known_ids.get(target.resolve())
                if target_ids is None:
                    target_parser = PageParser()
                    target_parser.feed(target.read_text(encoding="utf-8"))
                    target_ids = target_parser.ids
                    known_ids[target.resolve()] = target_ids
                if fragment not in target_ids:
                    errors.append(f"{page.relative_to(ROOT)}: missing fragment #{fragment} in {target.relative_to(ROOT)}")

    sitemap = ROOT / "sitemap.xml"
    try:
        root = ET.parse(sitemap).getroot()
        for loc in root.findall(".//{*}loc"):
            value = (loc.text or "").strip()
            if not value.startswith(SITE_URL):
                errors.append(f"sitemap.xml: unexpected URL {value!r}")
                continue
            path = unquote(urlsplit(value).path)
            prefix = "/Zakaria/"
            relative = path[len(prefix):] if path.startswith(prefix) else ""
            target = ROOT / relative
            if not relative or relative.endswith("/"):
                target = target / "index.html"
            if not target.is_file():
                errors.append(f"sitemap.xml: missing target for {value}")
    except (OSError, ET.ParseError) as exc:
        errors.append(f"sitemap.xml: cannot parse sitemap: {exc}")

    robots = ROOT / "robots.txt"
    if not robots.is_file() or f"Sitemap: {SITE_URL}/sitemap.xml" not in robots.read_text(encoding="utf-8"):
        errors.append("robots.txt: sitemap declaration is missing or incorrect.")

    if errors:
        print("Site validation failed:")
        for error in errors:
            print(f" - {error}")
        return 1

    print(f"Site validation passed: {len(pages)} HTML pages and all local links/assets/sitemap targets checked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
