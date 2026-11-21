#!/usr/bin/env python3
"""Validate local links, fragments, sitemap targets and basic page metadata."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE_URL = "https://zazakariakarfr13-coder.github.io/supermarket-decoder"
PROJECT_PREFIX = "/supermarket-decoder/"


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
        self.og = set()
        self.noindex = False

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
        if tag == "meta" and attrs.get("property", "").startswith("og:") and attrs.get("content", "").strip():
            self.og.add(attrs["property"])
        if tag == "meta" and attrs.get("name", "").lower() == "robots" and "noindex" in attrs.get("content", "").lower():
            self.noindex = True
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
        elif not parser.noindex and not 110 <= len(parser.description) <= 165:
            warnings.append(f"{relative}: meta description is {len(parser.description)} characters; aim for 110-165.")
        if not parser.noindex:
            missing_og = {"og:title", "og:description", "og:image", "og:url"} - parser.og
            if missing_og:
                errors.append(f"{relative}: missing share tags {', '.join(sorted(missing_og))} (needed for Pinterest and social previews).")
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
            # "#list=..." is the decoder's prefilled ingredient list, not an anchor
            if fragment and not fragment.startswith("list=") and target.suffix.lower() == ".html":
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
        ".jpg": lambda header: header.startswith(bytes((255, 216, 255))),
        ".jpeg": lambda header: header.startswith(bytes((255, 216, 255))),
        ".png": lambda header: header.startswith(bytes((137, 80, 78, 71, 13, 10, 26, 10))),
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

    # Menu + homepage search: the page list must be current and every listed page must load the menu.
    sys.path.insert(0, str(ROOT / "scripts"))
    import make_search_index  # noqa: E402

    index_file = ROOT / "assets" / "search-index.json"
    if not index_file.is_file() or index_file.read_text(encoding="utf-8") != make_search_index.render():
        errors.append("assets/search-index.json is out of date: run python scripts/make_search_index.py")
    for entry in make_search_index.build_index()["pages"]:
        rel = entry["u"] if entry["u"].endswith(".html") else entry["u"] + "index.html"
        if "assets/nav.js" not in (ROOT / rel).read_text(encoding="utf-8", errors="replace"):
            errors.append(f"{rel}: missing the menu script (assets/nav.js)")

    # Homepage search should expose its expanded state and announce result counts to assistive technology.
    home_html = (ROOT / "index.html").read_text(encoding="utf-8", errors="replace")
    nav_js = (ROOT / "assets" / "nav.js").read_text(encoding="utf-8", errors="replace")
    for required in (
        'aria-controls="sd-results"',
        'id="sd-search-status"',
        'role="status"',
        'aria-live="polite"',
    ):
        if required not in home_html:
            errors.append(f"index.html: accessible site-search markup is missing {required!r}.")
    for required in ('sd-search-status', 'status.textContent'):
        if required not in nav_js:
            errors.append(f"assets/nav.js: accessible search behaviour is missing {required!r}.")

    # Decoder safeguards: disclose the external barcode lookup, label the live preview,
    # preserve compact demo links, and avoid overstating ingredient-order/NOVA heuristics.
    decoder_html = (ROOT / "decoder" / "index.html").read_text(encoding="utf-8", errors="replace")
    for required in (
        'aria-label="Live camera preview for barcode scanning"',
        'credentials: "omit"',
        'referrerPolicy: "no-referrer"',
        'Camera ready. Hold the barcode inside the highlighted box.',
        '#sample=(bar|bread|cola|yog)',
        'Possible ultra-processed formulation (NOVA group 4)',
        'a clue alone does not confirm NOVA group 4',
        'not a formal classification',
        'do not necessarily make up most of the product together',
        'standard connection data such as your IP address',
    ):
        if required not in decoder_html:
            errors.append(f"decoder/index.html: expected privacy, accessibility or accuracy safeguard is missing {required!r}.")
    if "these make up most of the product." in decoder_html:
        errors.append("decoder/index.html: first-three ingredient wording overstates the combined share of the product.")
    if "The most complete list in the database is in French." in decoder_html:
        errors.append("decoder/index.html: language-field selection is described too confidently.")

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
