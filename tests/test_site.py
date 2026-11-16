"""Page de démo et slides : à jour, et sans résultat inventé."""
import re
import unittest

from tests.aide import RACINE

import build_site


class TestPage(unittest.TestCase):
    def setUp(self):
        self.html = (RACINE / "docs" / "index.html").read_text(encoding="utf-8")

    def test_pieces_a_jour(self):
        self.assertEqual(build_site.page_a_jour(self.html), self.html)

    def test_resultats_a_mesurer(self):
        self.assertIn("à mesurer", self.html)
        texte = re.sub(r"<style>.*?</style>", "", self.html, flags=re.S)
        self.assertNotRegex(texte, r"\d+\s?%")

    def test_sources_du_debat(self):
        for url in ("youtube.com/watch?v=7Y4sbZgBdnc", "philschmid.de/superhuman-bash",
                    "anthropic.com/engineering/harness-design-long-running-apps",
                    "blog.railway.com/p/skills-issue-writing-skills"):
            self.assertIn(url, self.html)


class TestSlides(unittest.TestCase):
    def test_slides_construites_depuis_la_source(self):
        source = (RACINE / "slides" / "slides.html").read_text(encoding="utf-8")
        construit = (RACINE / "docs" / "slides" / "index.html").read_text(encoding="utf-8")
        n = source.count('<section class="slide">')
        self.assertTrue(16 <= n <= 20, n)
        self.assertEqual(construit.count('<section class="slide">'), n)
        for titre in re.findall(r"<h2[^>]*>(.*?)</h2>", source):
            self.assertIn(titre, construit)

    def test_tableau_des_resultats_vide(self):
        source = (RACINE / "slides" / "slides.html").read_text(encoding="utf-8")
        self.assertNotRegex(source, r'<td class="n">[^<—]*\d')
        self.assertIn('class="todo', source)


if __name__ == "__main__":
    unittest.main()
