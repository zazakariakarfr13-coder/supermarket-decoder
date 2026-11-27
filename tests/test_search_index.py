import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import make_search_index as msi  # noqa: E402

PAGE = '<html><head><title>{t} | Supermarket Decoder</title><meta name="description" content="d"></head><body><h1>{t}</h1></body></html>'


class SearchIndexTests(unittest.TestCase):
    def test_english_file_is_current_and_unchanged_format(self):
        self.assertEqual((ROOT / "assets/search-index.json").read_text(encoding="utf-8"), msi.render("en"))

    def test_languages_are_kept_apart(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for rel, t in [("articles/a.html", "Sugar"), ("fr/articles/a.html", "Sucre"), ("ar/articles/a.html", "السكر")]:
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                (root / rel).write_text(PAGE.format(t=t), encoding="utf-8")
            old = msi.ROOT
            msi.ROOT = root
            try:
                en, fr, ar = (msi.build_index(l) for l in ("en", "fr", "ar"))
            finally:
                msi.ROOT = old
        self.assertEqual([p["u"] for p in en["pages"]], ["articles/a.html"])
        self.assertEqual([p["u"] for p in fr["pages"]], ["fr/articles/a.html"])
        self.assertEqual(fr["pages"][0]["g"], "Articles")
        self.assertEqual(ar["pages"][0]["g"], "مقالات")
        self.assertEqual(fr["groups"][0], "Pour commencer")
        self.assertEqual(len(fr["groups"]), len(en["groups"]))


if __name__ == "__main__":
    unittest.main()
