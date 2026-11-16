import unittest

from panier import total


class TestVisible(unittest.TestCase):
    def test_sans_remise(self):
        self.assertEqual(total([(19.99, 3)]), 59.97)

    def test_remise_dix(self):
        self.assertEqual(total([(10, 2)], 10), 18.0)
