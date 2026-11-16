import unittest

from fusion import fusionner


class TestVisible(unittest.TestCase):
    def test_chevauchement(self):
        self.assertEqual(fusionner([[1, 3], [2, 6], [8, 10]]), [[1, 6], [8, 10]])

    def test_se_touchent(self):
        self.assertEqual(fusionner([[1, 4], [4, 5]]), [[1, 5]])
