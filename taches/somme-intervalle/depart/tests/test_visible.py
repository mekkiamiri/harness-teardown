import unittest

from intervalle import somme_intervalle


class TestVisible(unittest.TestCase):
    def test_petit_intervalle(self):
        self.assertEqual(somme_intervalle(1, 3), 6)

    def test_intervalle_vide(self):
        self.assertEqual(somme_intervalle(3, 1), 0)
