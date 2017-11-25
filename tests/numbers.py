from decimal import Decimal
import unittest

from monero.numbers import to_atomic, from_atomic

class NumbersTestCase(unittest.TestCase):
    def test_simple_numbers(self):
        self.assertEqual(to_atomic(Decimal('0')), 0)
        self.assertEqual(from_atomic(0), Decimal('0'))
        self.assertEqual(to_atomic(Decimal('1')), 1000000000000)
        self.assertEqual(from_atomic(1000000000000), Decimal('1'))
        self.assertEqual(to_atomic(Decimal('0.000000000001')), 1)
        self.assertEqual(from_atomic(1), Decimal('0.000000000001'))

    def test_rounding(self):
        self.assertEqual(to_atomic(Decimal('1.0000000000004')), 1000000000000)
