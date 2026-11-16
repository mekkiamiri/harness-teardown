import unittest

from cache import CacheLRU


class TestCache(unittest.TestCase):
    def test_lecture_rafraichit(self):
        c = CacheLRU(2)
        c.ecrire("a", 1)
        c.ecrire("b", 2)
        c.lire("a")
        c.ecrire("c", 3)
        self.assertEqual(c.lire("a"), 1)
        self.assertIsNone(c.lire("b"))

    def test_reecriture_sans_eviction(self):
        c = CacheLRU(2)
        c.ecrire("a", 1)
        c.ecrire("b", 2)
        c.ecrire("a", 10)
        self.assertEqual(c.lire("a"), 10)
        self.assertEqual(c.lire("b"), 2)

    def test_reecriture_rafraichit(self):
        c = CacheLRU(2)
        c.ecrire("a", 1)
        c.ecrire("b", 2)
        c.ecrire("a", 10)
        c.ecrire("c", 3)
        self.assertIsNone(c.lire("b"))
        self.assertEqual(c.lire("a"), 10)
