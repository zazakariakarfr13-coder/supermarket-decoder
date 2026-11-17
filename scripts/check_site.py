#!/usr/bin/env python3
"""Validate local links, fragments, sitemap targets and basic page metadata."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE_URL = "https://zazakariakarfr13-coder.github.io/Zakaria"
PROJECT_PREFIX = "/Zakaria/"


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.targets = []
        self.ids = set()
        self.title_parts = []
        self.in_title = False
        self.description = None
        self.canonical = None
        self.h1_count = 0
        self.images_without_alt = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "title":
            self.in_title = True
        if tag == "h1":
            self.h1_count += 1
        if tag == "img" and "alt" not in attrs:
            self.images_without_alt += 1
        if tag == "meta" and attrs.get("name", "").lower() == "description":
            self.description = attrs.get("content", "").strip()
        if tag == "link" and "canonical" in attrs.get("rel", "").lower().split():
            self.canonical = attrs.get("href", "").strip()
        for attr in ("href", "src"):
            value = attrs.get(attr)
            if value:
                self.targets.append(value)

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title_parts.append(data)

    @property
    def title(self):
        return " ".join(" ".join(self.title_parts).split())


def resolve_local_target(page: Path, raw_url: str):
    parsed = urlsplit(raw_url.strip())
    if parsed.scheme or parsed.netloc or raw_url.startswith("//"):
        return None, parsed.fragment
    path = unquote(parsed.path)
    if not path:
        target = page
    elif path.startswith("/"):
        if not path.startswith(PROJECT_PREFIX):
            return None, parsed.fragment
        target = ROOT / path[len(PROJECT_PREFIX):]
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
    warnings = []
    pages = sorted(ROOT.rglob("*.html"))
    if not pages:
        errors.append("No HTML pages were found.")

    parsed_pages = {}
    for page in pages:
        parser = PageParser()
        relative = page.relative_to(ROOT)
        try:
            parser.feed(page.read_text(encoding="utf-8"))
        except (OSError, UnicodeError) as exc:
            errors.append(f"{relative}: cannot read page: {exc}")
            continue
        parsed_pages[page.resolve()] = parser

        if not parser.title:
            errors.append(f"{relative}: missing <title>.")
        if not parser.description:
            warnings.append(f"{relative}: missing meta description.")
        if parser.h1_count == 0:
            warnings.append(f"{relative}: no H1 heading found.")
        elif parser.h1_count > 1:
            warnings.append(f"{relative}: {parser.h1_count} H1 headings found; check heading hierarchy.")
        if parser.images_without_alt:
            warnings.append(f"{relative}: {parser.images_without_alt} image(s) missing an alt attribute.")

    for page in pages:
        parser = parsed_pages.get(page.resolve())
        if parser is None:
            continue
        for raw in parser.targets:
            target, fragment = resolve_local_target(page, raw)
            if target is None:
                continue
            if not target.is_file():
                errors.append(f"{page.relative_to(ROOT)}: missing local target {raw!r}")
                continue
            if fragment and target.suffix.lower() == ".html":
                target_parser = parsed_pages.get(target.resolve())
                if target_parser is None:
                    target_parser = PageParser()
                    try:
                        target_parser.feed(target.read_text(encoding="utf-8"))
                    except (OSError, UnicodeError) as exc:
                        errors.append(f"{target.relative_to(ROOT)}: cannot read fragment target: {exc}")
                        continue
                    parsed_pages[target.resolve()] = target_parser
                if fragment not in target_parser.ids:
                    errors.append(
                        f"{page.relative_to(ROOT)}: missing fragment #{fragment} "
                        f"in {target.relative_to(ROOT)}"
                    )


    # Catch mislabeled or damaged raster assets before they become broken page images.
    image_signatures = {
        ".jpg": lambda header: header.startswith(b"\\xff\\xd8\\xff"),
        ".jpeg": lambda header: header.startswith(b"\\xff\\xd8\\xff"),
        ".png": lambda header: header.startswith(b"\\x89PNG\\r\\n\\x1a\\n"),
        ".gif": lambda header: header.startswith((b"GIF87a", b"GIF89a")),
        ".webp": lambda header: len(header) >= 12 and header[:4] == b"RIFF" and header[8:12] == b"WEBP",
    }
    for asset in sorted(ROOT.rglob("*")):
        if not asset.is_file():
            continue
        matcher = image_signatures.get(asset.suffix.lower())
        if matcher is None:
            continue
        try:
            header = asset.read_bytes()[:16]
        except OSError as exc:
            errors.append(f"{asset.relative_to(ROOT)}: cannot read image asset: {exc}")
            continue
        if not matcher(header):
            warnings.append(
                f"{asset.relative_to(ROOT)}: file extension does not match its raster image signature."
            )

    # Canonical URLs should be unique to each page when supplied, and stay on this site.
    seen_canonicals = {}
    for page, parser in parsed_pages.items():
        canonical = parser.canonical
        if not canonical:
            continue
        relative = Path(page).relative_to(ROOT)
        if not canonical.startswith(SITE_URL):
            errors.append(f"{relative}: canonical URL is outside the expected site: {canonical}")
        if canonical in seen_canonicals:
            errors.append(
                f"{relative}: duplicate canonical URL also used by "
                f"{seen_canonicals[canonical]}: {canonical}"
            )
        else:
            seen_canonicals[canonical] = relative

    sitemap = ROOT / "sitemap.xml"
    try:
        root = ET.parse(sitemap).getroot()
        for loc in root.findall(".//{*}loc"):
            value = (loc.text or "").strip()
            if not value.startswith(SITE_URL):
                errors.append(f"sitemap.xml: unexpected URL {value!r}")
                continue
            path = unquote(urlsplit(value).path)
            relative = path[len(PROJECT_PREFIX):] if path.startswith(PROJECT_PREFIX) else ""
            target = ROOT / relative
            if not relative or relative.endswith("/"):
                target = target / "index.html"
            if not target.is_file():
                errors.append(f"sitemap.xml: missing target for {value}")
    except (OSError, ET.ParseError) as exc:
        errors.append(f"sitemap.xml: cannot parse sitemap: {exc}")

    robots = ROOT / "robots.txt"
    try:
        robots_content = robots.read_text(encoding="utf-8")
        if f"Sitemap: {SITE_URL}/sitemap.xml" not in robots_content:
            errors.append("robots.txt: sitemap declaration is missing or incorrect.")
    except (OSError, UnicodeError) as exc:
        errors.append(f"robots.txt: cannot read file: {exc}")

    if warnings:
        print("Site validation warnings:")
        for warning in warnings:
            print(f" - {warning}")

    if errors:
        print("Site validation failed:")
        for error in errors:
            print(f" - {error}")
        return 1

    print(
        f"Site validation passed: {len(pages)} HTML pages, local links/assets/fragments, "
        "sitemap targets and available metadata checked."
    )
    if warnings:
        print(f"{len(warnings)} non-blocking warning(s) need review.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
