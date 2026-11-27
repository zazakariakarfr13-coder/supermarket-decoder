import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from i18n import guard  # noqa: E402


class GuardTests(unittest.TestCase):
    def test_ecodes_and_numbers(self):
        guard.same("x", "EFSA set 40 mg in 2013 for E951.", "L’EFSA a fixé 40 mg en 2013 pour E951.")
        with self.assertRaises(ValueError):
            guard.same("x", "E150d is darkest.", "E150c est le plus foncé.")
        with self.assertRaises(ValueError):
            guard.same("x", "about 0.1 to 0.5%", "environ 0,1 à 0,6 %")

    def test_arabic_words(self):
        guard.same("x", "within 2 hours", "خلال ساعتين")

    def test_lists_and_pairs(self):
        guard.same_list("faq", [("Q 1?", "A 2.")], [["س 1؟", "ج 2."]])
        with self.assertRaises(ValueError):
            guard.same_list("faq", [("Q", "A")], [])


if __name__ == "__main__":
    unittest.main()


class ArabicConjunctionTests(unittest.TestCase):
    def test_waw_before_ecode(self):
        guard.same("x", "E150c and E150d", "E150c وE150d")


class EntityTest(unittest.TestCase):
    def test_html_entity_is_not_a_number(self):
        guard.same("x", "Decoder&#x27;s guide", "le guide du Decoder")
