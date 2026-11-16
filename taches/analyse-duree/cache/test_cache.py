import unittest

from duree import en_minutes


class TestCache(unittest.TestCase):
    def test_heures_seules(self):
        self.assertEqual(en_minutes("2h"), 120)

    def test_zero_padding(self):
        self.assertEqual(en_minutes("10h05m"), 605)
        self.assertEqual(en_minutes("0h5m"), 5)

    def test_invalides(self):
        for texte in ["", "abc", "1h30", "h", "m", "1 h"]:
            with self.subTest(texte=texte):
                with self.assertRaises(ValueError):
                    en_minutes(texte)
