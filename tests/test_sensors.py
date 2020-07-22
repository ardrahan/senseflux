import unittest
from senseflux.sensors import *


class Util(unittest.TestCase):

    def test_voltage_to_temp(self):
        self.assertEqual(voltage_to_temperature(0.0), -40)
        self.assertAlmostEqual(voltage_to_temperature(1.0), 1.67)
        self.assertAlmostEqual(voltage_to_temperature(2.2), 51.674)
        self.assertEqual(voltage_to_temperature(3.0), 85.01)

    def test_three_volt_range(self):
        self.assertEqual(three_volt_range(0.0), 0)
        self.assertEqual(three_volt_range(1.5), 50)
        self.assertEqual(three_volt_range(3.0), 100)
