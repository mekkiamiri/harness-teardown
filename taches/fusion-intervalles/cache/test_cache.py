import unittest

from fusion import fusionner


class TestCache(unittest.TestCase):
    def test_desordre(self):
        self.assertEqual(fusionner([[8, 10], [1, 3], [2, 6]]), [[1, 6], [8, 10]])

    def test_vide(self):
        self.assertEqual(fusionner([]), [])

    def test_inclus(self):
        self.assertEqual(fusionner([[1, 10], [2, 3]]), [[1, 10]])

    def test_entree_intacte(self):
        entree = [[5, 6], [1, 5]]
        fusionner(entree)
        self.assertEqual(entree, [[5, 6], [1, 5]])
