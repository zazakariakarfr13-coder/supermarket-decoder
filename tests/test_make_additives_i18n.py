import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import i18n_pages  # noqa: E402
import make_additives as ma  # noqa: E402
from additives_data import ADDITIVES  # noqa: E402


def mirror():
    """English text copied as a stand-in translation (passes the number guard)."""
    return {a["slug"]: {k: copy.deepcopy(a[k]) for k in ma.TEXT_FIELDS + ma.FREE_FIELDS} for a in ADDITIVES}


class AdditiveI18nTests(unittest.TestCase):
    def test_english_output_unchanged(self):
        site = i18n_pages.Site()
        for a in ADDITIVES:
            path = f"additives/{a['slug']}.html"
            self.assertEqual(site.apply(ma.additive_page(a, "en"), path), (ROOT / path).read_text(encoding="utf-8"), path)
        self.assertEqual(site.apply(ma.index_page("en"), "additives/index.html"),
                         (ROOT / "additives/index.html").read_text(encoding="utf-8"))

    def test_french_page_paths_and_lang(self):
        items = ma.localized("fr", mirror())
        html = ma.additive_page(items[0], "fr")
        self.assertIn('<html lang="fr">', html)
        self.assertIn('href="../../assets/site.css"', html)
        self.assertIn('href="../decoder/#list=', html)
        self.assertIn("utm_content=e471-fr", html)
        self.assertNotIn("Its job", html)

    def test_arabic_is_rtl(self):
        html = ma.additive_page(ma.localized("ar", mirror())[0], "ar")
        self.assertIn('<html lang="ar" dir="rtl">', html)

    def test_missing_field_fails(self):
        tr = mirror()
        del tr["e471"]["safety"]
        with self.assertRaisesRegex(ValueError, "e471.safety"):
            ma.localized("fr", tr)

    def test_number_change_fails(self):
        tr = mirror()
        tr["e951"]["safety"] = tr["e951"]["safety"].replace("40 mg", "45 mg")
        with self.assertRaisesRegex(ValueError, "numbers differ"):
            ma.localized("fr", tr)

    def test_ui_tables_complete(self):
        self.assertEqual(set(ma.UI["en"]), set(ma.UI["fr"]))
        self.assertEqual(set(ma.UI["en"]), set(ma.UI["ar"]))


if __name__ == "__main__":
    unittest.main()
