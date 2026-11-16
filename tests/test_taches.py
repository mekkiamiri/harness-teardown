"""Le jeu de tâches : faisable, vérifiable, et impossible à réussir en modifiant les tests."""
import tempfile
import unittest
from pathlib import Path

from tests.aide import RACINE

import taches


class TestTaches(unittest.TestCase):
    def test_nombre(self):
        self.assertTrue(5 <= len(taches.lister()) <= 8)

    def test_chaque_tache_est_valide(self):
        for t in taches.lister():
            with self.subTest(tache=t["id"]):
                self.assertEqual(taches.verifier(t), [])

    def test_tests_caches_hors_espace(self):
        t = taches.charger("cache-lru")
        with tempfile.TemporaryDirectory() as tmp:
            espace = taches.preparer(t, Path(tmp) / "k")
            self.assertFalse(list(espace.rglob("test_cache.py")))
            self.assertFalse((espace / "solution").exists())

    def test_tricher_sur_les_tests_ne_paie_pas(self):
        t = taches.charger("somme-intervalle")
        with tempfile.TemporaryDirectory() as tmp:
            espace = taches.preparer(t, Path(tmp) / "k")
            (espace / "tests" / "test_visible.py").write_text("import unittest\n")
            note = taches.noter(t, espace)
            self.assertFalse(note["reussi"])
            self.assertTrue(note["tests_modifies"])

    def test_correctif_partiel_echoue(self):
        """Corriger seulement ce que montrent les tests visibles ne suffit pas (fusion : tri oublié)."""
        t = taches.charger("fusion-intervalles")
        with tempfile.TemporaryDirectory() as tmp:
            espace = taches.preparer(t, Path(tmp) / "k")
            code = (espace / "fusion.py").read_text(encoding="utf-8")
            (espace / "fusion.py").write_text(code.replace("debut < resultat", "debut <= resultat"))
            self.assertFalse(taches.noter(t, espace)["reussi"])


if __name__ == "__main__":
    unittest.main()
