import unittest

from palindrome import est_palindrome


class TestCache(unittest.TestCase):
    def test_ponctuation(self):
        self.assertTrue(est_palindrome("A man, a plan, a canal: Panama!"))

    def test_vide(self):
        self.assertTrue(est_palindrome(""))

    def test_chiffres(self):
        self.assertTrue(est_palindrome("12 3-21"))
        self.assertFalse(est_palindrome("123"))

    def test_accents_non_traites(self):
        self.assertFalse(est_palindrome("été e"))
