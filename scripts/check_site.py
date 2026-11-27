#!/usr/bin/env python3
"""Validate local links, fragments, sitemap targets and basic page metadata."""

from html.parser import HTMLParser
import re
import csv
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit
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


_A_HREF = re.compile(r'<a\b[^>]*\shref="([^"]+)"', re.I)
_SWITCH_BLOCK = re.compile(r"<!--i18n:switch-->.*?<!--/i18n:switch-->", re.S)


def check_languages(root: Path = ROOT, pages=None) -> list:
    """French and Arabic twins: every language present once a page is translated, right lang/dir,
    marker blocks current (scripts/i18n_pages.py), and no links from one language into another
    (the language switcher excepted)."""
    import i18n_pages as ip
    site = ip.Site(root, pages)
    errors = []
    for base in site.pages:
        have = site.langs_for(base)
        if len(have) > 1:
            for lang in ip.LANGS:
                if lang not in have:
                    errors.append(f"missing {lang} twin: {base}")
    for path in site.all_paths():
        f = root / path
        text = f.read_text(encoding="utf-8", errors="replace")
        lang = ip.lang_of(path)
        m = re.search(r"<html\b[^>]*>", text)
        tag = m.group(0) if m else ""
        if f'lang="{lang}"' not in tag:
            errors.append(f'{path}: needs <html lang="{lang}">')
        if lang == "ar" and 'dir="rtl"' not in tag:
            errors.append(f'{path}: needs dir="rtl" on <html>')
        if site.apply(text, path) != text:
            errors.append(f"{path}: language markup out of date (run py -3 scripts/i18n_pages.py)")
        for href in _A_HREF.findall(_SWITCH_BLOCK.sub("", text)):
            parsed = urlsplit(href)
            if parsed.scheme or parsed.netloc or href.startswith(("#", "//", "mailto:")) or not parsed.path:
                continue
            target = (f.parent / unquote(parsed.path)).resolve()
            if target.is_dir() or parsed.path.endswith("/"):
                target = target / "index.html"
            try:
                rel = target.relative_to(Path(root).resolve()).as_posix()
            except ValueError:
                continue
            if not rel.endswith(".html") or rel == "404.html" or rel.startswith("assets/"):
                continue
            if ip.lang_of(rel) != lang:
                errors.append(f"{path}: links to another language: {href}")
    sm = root / "sitemap.xml"
    if sm.is_file() and sm.read_text(encoding="utf-8") != site.sitemap():
        errors.append("sitemap.xml: out of date (run py -3 scripts/i18n_pages.py)")
    return errors


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

    for lang in make_search_index.LANGS:
        index_file = make_search_index.out_file(lang)
        if not index_file.is_file() or index_file.read_text(encoding="utf-8") != make_search_index.render(lang):
            errors.append(f"{index_file.relative_to(ROOT).as_posix()} is out of date: run python scripts/make_search_index.py")
    # French and Arabic twins of the hand-written pages must match their English page + translation.
    import make_twins  # noqa: E402
    try:
        import contextlib, io
        with contextlib.redirect_stdout(io.StringIO()) as out:
            stale = make_twins.main(["--check"])
        if stale:
            errors.extend(line for line in out.getvalue().splitlines() if line.strip())
    except ValueError as exc:  # an English page changed under its translation, or a number differs
        errors.append(f"translations: {exc}")
    for entry in [e for lang in make_search_index.LANGS for e in make_search_index.build_index(lang)["pages"]]:
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
    decoder_html = "\n".join((ROOT / f).read_text(encoding="utf-8", errors="replace")
                             for f in ("decoder/index.html", "assets/decoder.js", "assets/decoder-scan.js"))
    for required in (
        'aria-label="Live camera preview for barcode scanning"',
        'credentials: "omit"',
        'referrerPolicy: "no-referrer"',
        'referrerpolicy="no-referrer"',
        's.referrerPolicy = "no-referrer"',
        'Camera ready. Hold the barcode inside the highlighted box.',
        '#sample=(bar|bread|cola|yog)',
        'Possible ultra-processed formulation (NOVA group 4)',
        'a clue alone does not confirm NOVA group 4',
        'not a formal classification',
        'do not necessarily make up most of the product together',
        'standard connection data such as your IP address',
        'image URL supplied in the community record',
    ):
        if required not in decoder_html:
            errors.append(f"decoder/index.html: expected privacy, accessibility or accuracy safeguard is missing {required!r}.")
    if "these make up most of the product." in decoder_html:
        errors.append("decoder/index.html: first-three ingredient wording overstates the combined share of the product.")
    if "The most complete list in the database is in French." in decoder_html:
        errors.append("decoder/index.html: language-field selection is described too confidently.")
    if "is an approved additive code." in decoder_html:
        errors.append("decoder/index.html: an E-number identifier must not be described as universally approved.")
    if "is an additive identifier." not in decoder_html:
        errors.append("decoder/index.html: E-number fallback should describe the code as an identifier.")
    if "not proof of current authorisation in every country or food category" not in decoder_html:
        errors.append("decoder/index.html: add a jurisdiction caveat for E-number authorisation.")

    # Factory vs. Kitchen verdict filters must expose their controlled list and announce result counts.
    factory_html = (ROOT / "factory-vs-kitchen" / "index.html").read_text(encoding="utf-8", errors="replace")
    factory_script = factory_html[factory_html.rfind("<script>"):]
    for required in (
        'id="food-grid"',
        'id="filter-status"',
        'role="status"',
        'aria-live="polite"',
        'aria-controls="food-grid"',
        'Kitchen scores are editorial judgments, not lab measurements.',
        'Store-price and home-cost figures are illustrative estimates',
    ):
        if required not in factory_html:
            errors.append(f"factory-vs-kitchen/index.html: expected accessibility or estimate disclosure is missing {required!r}.")
    for required in ("filter-status", "status.textContent", "card.hidden"):
        if required not in factory_script:
            errors.append(f"factory-vs-kitchen/index.html: verdict-filter behaviour is missing {required!r}.")

    # Every directly reachable Factory vs. Kitchen detail page must explain that
    # scores and cost figures are editorial estimates, not official measurements.
    fvk_details = sorted(p for p in (ROOT / "factory-vs-kitchen").glob("*.html") if p.name != "index.html")
    if not fvk_details:
        errors.append("factory-vs-kitchen: no product detail pages were found.")
    for detail_page in fvk_details:
        detail_html = detail_page.read_text(encoding="utf-8", errors="replace")
        for required in (
            "The kitchen score is an editorial estimate",
            "not a lab measurement or official rating",
            "rough US examples, not live quotes",
            "vary by retailer, location, date, portion size and pantry assumptions",
        ):
            if required not in detail_html:
                errors.append(f"{detail_page.relative_to(ROOT)}: missing estimate-method disclosure {required!r}.")

    errors.extend(check_languages())
    # Pinterest Factory-vs-Kitchen campaign: keep the public creative manifest
    # complete, accessible, correctly linked and measurable before assets are reused.
    pin_dir = ROOT / "pins" / "fvk"
    pin_manifest = pin_dir / "pins.csv"
    pin_files = set()
    if not pin_manifest.is_file():
        errors.append("pins/fvk/pins.csv: campaign manifest is missing.")
    else:
        try:
            with pin_manifest.open(encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                required_columns = {"file", "title", "description", "link", "alt_text"}
                if not required_columns.issubset(set(reader.fieldnames or [])):
                    errors.append("pins/fvk/pins.csv: required campaign columns are missing.")
                for row_number, row in enumerate(reader, start=2):
                    filename = (row.get("file") or "").strip()
                    if not filename or filename in pin_files:
                        errors.append(f"pins/fvk/pins.csv:{row_number}: missing or duplicate image filename.")
                        continue
                    pin_files.add(filename)
                    for field in ("title", "description", "alt_text"):
                        if not (row.get(field) or "").strip():
                            errors.append(f"pins/fvk/pins.csv:{row_number}: {field} is empty.")
                    image_path = pin_dir / filename
                    if not image_path.is_file():
                        errors.append(f"pins/fvk/pins.csv:{row_number}: missing creative {filename}.")
                    else:
                        try:
                            header = image_path.read_bytes()[:24]
                            if header[:4] != bytes((137, 80, 78, 71)):
                                errors.append(f"{image_path.relative_to(ROOT)}: expected a PNG image.")
                            elif int.from_bytes(header[16:20], "big") != 1000 or int.from_bytes(header[20:24], "big") != 1500:
                                errors.append(f"{image_path.relative_to(ROOT)}: expected 1000x1500 Pinterest dimensions.")
                        except OSError as exc:
                            errors.append(f"{image_path.relative_to(ROOT)}: cannot read creative: {exc}")
                    raw_link = (row.get("link") or "").strip()
                    parsed_link = urlsplit(raw_link)
                    if parsed_link.scheme != "https" or parsed_link.netloc != "zazakariakarfr13-coder.github.io":
                        errors.append(f"pins/fvk/pins.csv:{row_number}: link is not a secure link to this project's Pages site.")
                        continue
                    if not parsed_link.path.startswith(PROJECT_PREFIX + "factory-vs-kitchen/"):
                        errors.append(f"pins/fvk/pins.csv:{row_number}: Pin does not link directly to Factory vs. Kitchen.")
                        continue
                    expected_page = ROOT / parsed_link.path[len(PROJECT_PREFIX):]
                    if not expected_page.is_file():
                        errors.append(f"pins/fvk/pins.csv:{row_number}: linked product page does not exist.")
                    if expected_page.stem != Path(filename).stem:
                        errors.append(f"pins/fvk/pins.csv:{row_number}: image and destination product do not match.")
                    query = parse_qs(parsed_link.query)
                    if query.get("utm_source") != ["pinterest"] or query.get("utm_campaign") != ["factory_vs_kitchen"] or query.get("utm_content") != [Path(filename).stem]:
                        errors.append(f"pins/fvk/pins.csv:{row_number}: Pinterest UTM parameters are missing or inconsistent.")
        except (OSError, UnicodeError, csv.Error) as exc:
            errors.append(f"pins/fvk/pins.csv: cannot parse campaign manifest: {exc}")
    if pin_dir.is_dir():
        actual_pin_files = {p.name for p in pin_dir.glob("*.png") if p.name != "_contact-sheet.png"}
        if actual_pin_files != pin_files:
            errors.append("pins/fvk: PNG campaign assets and pins.csv rows do not match.")

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
