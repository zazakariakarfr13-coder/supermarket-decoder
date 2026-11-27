import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import check_site  # noqa: E402
import i18n_pages  # noqa: E402

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>T</title></head><body><main><h1>T</h1>
<a href="{link}">x</a></main></body></html>
"""


class LanguageCheckTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.write("articles/a.html", "b.html")
        self.write("articles/b.html", "a.html")
        for lang in ("fr", "ar"):
            self.write(f"{lang}/articles/a.html", "b.html")
            self.write(f"{lang}/articles/b.html", "a.html")
        self.pages = ["articles/a.html", "articles/b.html"]
        self.fix()

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel, link):
        f = self.root / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(PAGE.format(link=link), encoding="utf-8")

    def fix(self):
        site = i18n_pages.Site(self.root, self.pages)
        for p in site.all_paths():
            f = self.root / p
            f.write_text(site.apply(f.read_text(encoding="utf-8"), p), encoding="utf-8")

    def check(self):
        return check_site.check_languages(self.root, self.pages)

    def test_clean(self):
        self.assertEqual(self.check(), [])

    def test_missing_twin(self):
        (self.root / "ar/articles/b.html").unlink()
        self.fix()
        self.assertTrue(any("missing ar twin" in e and "articles/b.html" in e for e in self.check()), self.check())

    def test_wrong_dir(self):
        f = self.root / "ar/articles/a.html"
        f.write_text(f.read_text(encoding="utf-8").replace(' dir="rtl"', ""), encoding="utf-8")
        self.assertTrue(any("ar/articles/a.html" in e and "rtl" in e for e in self.check()), self.check())

    def test_cross_language_link(self):
        self.write("fr/articles/a.html", "../../articles/b.html")
        self.fix()
        self.assertTrue(any("fr/articles/a.html: links to another language" in e for e in self.check()), self.check())

    def test_switcher_links_allowed(self):
        self.assertFalse(any("another language" in e for e in self.check()))

    def test_stale_markers(self):
        f = self.root / "fr/articles/a.html"
        f.write_text(f.read_text(encoding="utf-8").replace('class="lang-switch"', 'class="x"'), encoding="utf-8")
        self.assertTrue(any("out of date" in e for e in self.check()), self.check())


if __name__ == "__main__":
    unittest.main()
