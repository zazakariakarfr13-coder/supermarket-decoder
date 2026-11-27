import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import i18n_pages  # noqa: E402
import make_fvk as mf  # noqa: E402
from fvk_data import GLOSS, PRODUCTS  # noqa: E402


def mirror():
    return {p["slug"]: {k: copy.deepcopy(p[k]) for k in mf.TEXT_FIELDS} for p in PRODUCTS}


class FvkI18nTests(unittest.TestCase):
    def test_english_output_unchanged(self):
        site = i18n_pages.Site()
        for i, p in enumerate(PRODUCTS):
            path = f"factory-vs-kitchen/{p['slug']}.html"
            self.assertEqual(site.apply(mf.product_page(p, i), path), (ROOT / path).read_text(encoding="utf-8"), path)
        self.assertEqual(site.apply(mf.index_page(), "factory-vs-kitchen/index.html"),
                         (ROOT / "factory-vs-kitchen/index.html").read_text(encoding="utf-8"))

    def test_french_page(self):
        items = mf.localized("fr", mirror())
        html = mf.product_page(items[0], 0, "fr", items, {"selle": "Une forme."})
        self.assertIn('<html lang="fr">', html)
        self.assertIn("utm_content=pringles-fr", html)
        self.assertNotIn("Kitchen score", html)

    def test_arabic_gloss_matches_with_article(self):
        T = mf.Terms({"مِبثق": "آلة."}, "ar")
        out = T("يمرّ العجين في المِبثق ثم يخرج.")
        self.assertIn('class="term"', T.finish(out))

    def test_missing_field_fails(self):
        tr = mirror()
        del tr["nutella"]["secret"]
        with self.assertRaisesRegex(ValueError, "nutella.secret"):
            mf.localized("fr", tr)

    def test_price_change_fails(self):
        tr = mirror()
        tr["nutella"]["cost"] = ("about $5 a jar", tr["nutella"]["cost"][1])
        with self.assertRaisesRegex(ValueError, "numbers differ"):
            mf.localized("fr", tr)

    def test_ui_complete(self):
        self.assertEqual(set(mf.UI["en"]), set(mf.UI["fr"]))
        self.assertEqual(set(mf.UI["en"]), set(mf.UI["ar"]))


if __name__ == "__main__":
    unittest.main()
