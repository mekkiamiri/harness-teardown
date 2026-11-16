import unittest

from duree import en_minutes


class TestVisible(unittest.TestCase):
    def test_heures_minutes(self):
        self.assertEqual(en_minutes("1h30m"), 90)

    def test_minutes_seules(self):
        self.assertEqual(en_minutes("45m"), 45)
