import unittest

from palindrome import est_palindrome


class TestVisible(unittest.TestCase):
    def test_simple(self):
        self.assertTrue(est_palindrome("radar"))

    def test_casse(self):
        self.assertTrue(est_palindrome("Kayak"))

    def test_pas_palindrome(self):
        self.assertFalse(est_palindrome("python"))
