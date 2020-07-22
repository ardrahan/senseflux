import unittest
from senseflux.util import veghub_time_to_timestamp


class Util(unittest.TestCase):

    def test_veghub_time_to_timestamp(self):
        self.assertEqual(veghub_time_to_timestamp("2020-07-18 18:55:37"), 1595098537)
