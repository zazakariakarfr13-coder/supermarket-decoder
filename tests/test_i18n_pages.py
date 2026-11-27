import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import i18n_pages as ip  # noqa: E402

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>T</title>
<link rel="canonical" href="https://zazakariakarfr13-coder.github.io/supermarket-decoder/articles/x.html">
</head><body class="with-side"><header><a href="../index.html">SD</a></header><main><h1>T</h1></main></body></html>
"""


class I18nPagesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for p in ["articles/x.html", "fr/articles/x.html", "ar/articles/x.html", "index.html", "fr/index.html"]:
            f = self.root / p
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(PAGE, encoding="utf-8")
        self.site = ip.Site(self.root, ["index.html", "articles/x.html"])

    def tearDown(self):
        self.tmp.cleanup()

    def test_paths(self):
        self.assertEqual(ip.twin("articles/x.html", "fr"), "fr/articles/x.html")
        self.assertEqual(ip.lang_of("ar/articles/x.html"), "ar")
        self.assertEqual(ip.base_of("fr/articles/x.html"), "articles/x.html")
        self.assertEqual(ip.page_url("decoder/index.html"), ip.SITE + "/decoder/")
        self.assertEqual(ip.page_url("fr/index.html"), ip.SITE + "/fr/")

    def test_head_block_hreflang(self):
        out = self.site.apply(PAGE, "fr/articles/x.html")
        for lang, pre in [("en", ""), ("fr", "fr/"), ("ar", "ar/"), ("x-default", "")]:
            self.assertIn(f'<link rel="alternate" hreflang="{lang}" href="{ip.SITE}/{pre}articles/x.html">', out)
        self.assertIn('<meta property="og:locale" content="fr_FR">', out)
        self.assertIn('<html lang="fr">', out)
        self.assertIn(f'<link rel="canonical" href="{ip.SITE}/fr/articles/x.html">', out)

    def test_arabic_direction_and_style(self):
        out = self.site.apply(PAGE, "ar/articles/x.html")
        self.assertIn('<html lang="ar" dir="rtl">', out)
        self.assertIn('href="../../assets/lang-ar.css"', out)
        self.assertIn('href="../../assets/i18n.css"', out)

    def test_switcher(self):
        out = self.site.apply(PAGE, "fr/articles/x.html")
        self.assertIn('<a href="../../articles/x.html" hreflang="en" lang="en">EN</a>', out)
        self.assertIn('<span aria-current="true">FR</span>', out)
        self.assertIn('<a href="../../ar/articles/x.html" hreflang="ar" lang="ar">عربي</a>', out)
        self.assertLess(out.index('<body class="with-side">'), out.index('class="lang-switch"'))

    def test_missing_twin_is_left_out(self):
        out = self.site.apply(PAGE, "index.html")  # no ar/index.html yet
        self.assertNotIn('hreflang="ar"', out)
        self.assertIn('hreflang="fr"', out)

    def test_idempotent(self):
        once = self.site.apply(PAGE, "articles/x.html")
        self.assertEqual(self.site.apply(once, "articles/x.html"), once)

    def test_english_keeps_its_body(self):
        out = self.site.apply(PAGE, "articles/x.html")
        self.assertIn('<html lang="en">', out)
        self.assertIn("<main><h1>T</h1></main>", out)

    def test_sitemap(self):
        sm = self.site.sitemap()
        self.assertIn('xmlns:xhtml="http://www.w3.org/1999/xhtml"', sm)
        self.assertIn(f"<loc>{ip.SITE}/ar/articles/x.html</loc>", sm)
        self.assertIn(f'<xhtml:link rel="alternate" hreflang="x-default" href="{ip.SITE}/articles/x.html"/>', sm)
        self.assertNotIn(f"<loc>{ip.SITE}/ar/</loc>", sm)
        self.assertEqual(sm.count("<url>"), 5)


if __name__ == "__main__":
    unittest.main()
