import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import make_twins as mt  # noqa: E402


class TwinTests(unittest.TestCase):
    def test_shared_paths_get_one_more_level(self):
        self.assertTrue(mt.shared_target("decoder/index.html", "../assets/site.css"))
        self.assertTrue(mt.shared_target("index.html", "assets/nav.js"))
        self.assertFalse(mt.shared_target("decoder/index.html", "../articles/x.html"))
        self.assertFalse(mt.shared_target("index.html", "https://example.com/assets/x.js"))

    def test_build_replaces_and_rewrites(self):
        html = mt.build("articles/e-numbers-explained.html",
                        [("Additives without the panic", "Les additifs sans panique")], "fr")
        self.assertIn("Les additifs sans panique", html)
        self.assertIn('href="../../assets/site.css"', html)
        self.assertIn('href="../additives/e471.html"', html)

    def test_css_url_and_poster_paths_get_one_more_level(self):
        # the comic avatars live in CSS url(), the home animation's still frame in poster=""
        story = mt.build("story/index.html", [], "fr")
        self.assertIn("--av:url(../../assets/cast/mina.webp)", story)
        self.assertNotIn("--av:url(../assets/cast/", story)
        home = mt.build("index.html", [], "fr")
        self.assertIn('poster="../assets/video/crunch-box-poster.jpg"', home)

    def test_missing_piece_fails(self):
        with self.assertRaisesRegex(ValueError, "not found"):
            mt.build("articles/e-numbers-explained.html", [("No such English text", "x")], "fr")

    def test_number_change_fails(self):
        with self.assertRaisesRegex(ValueError, "numbers differ"):
            mt.build("articles/e-numbers-explained.html", [("E300 — ascorbic acid", "E301 — acide ascorbique")], "fr")


if __name__ == "__main__":
    unittest.main()
