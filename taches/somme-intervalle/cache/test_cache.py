import unittest

from intervalle import somme_intervalle


class TestCache(unittest.TestCase):
    def test_bornes_egales(self):
        self.assertEqual(somme_intervalle(5, 5), 5)

    def test_negatifs(self):
        self.assertEqual(somme_intervalle(-2, 2), 0)
        self.assertEqual(somme_intervalle(-3, -1), -6)

    def test_grand(self):
        self.assertEqual(somme_intervalle(1, 100), 5050)

    def test_a_superieur(self):
        self.assertEqual(somme_intervalle(10, -10), 0)
