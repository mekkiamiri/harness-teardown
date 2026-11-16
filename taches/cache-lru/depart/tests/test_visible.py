import unittest

from cache import CacheLRU


class TestVisible(unittest.TestCase):
    def test_lecture(self):
        c = CacheLRU(2)
        c.ecrire("a", 1)
        self.assertEqual(c.lire("a"), 1)
        self.assertIsNone(c.lire("z"))

    def test_eviction(self):
        c = CacheLRU(2)
        c.ecrire("a", 1)
        c.ecrire("b", 2)
        c.ecrire("c", 3)
        self.assertEqual(c.lire("c"), 3)
        self.assertIsNone(c.lire("a"))
