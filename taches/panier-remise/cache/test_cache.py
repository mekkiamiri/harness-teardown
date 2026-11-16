import unittest

from panier import total
from prix import appliquer_remise


class TestCache(unittest.TestCase):
    def test_panier_vide(self):
        self.assertEqual(total([], 10), 0)

    def test_remise_quart(self):
        self.assertEqual(total([(100, 1)], 25), 75.0)

    def test_appliquer_remise_pourcentage_entier(self):
        self.assertAlmostEqual(appliquer_remise(200, 50), 100)
        self.assertAlmostEqual(appliquer_remise(80, 0), 80)
