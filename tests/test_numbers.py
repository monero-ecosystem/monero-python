from decimal import Decimal
import sys
import unittest

from monero.numbers import to_atomic, from_atomic, as_monero, PaymentID

class NumbersTestCase(unittest.TestCase):
    def test_simple_numbers(self):
        self.assertEqual(to_atomic(Decimal('0')), 0)
        self.assertEqual(from_atomic(0), Decimal('0'))
        self.assertEqual(to_atomic(Decimal('1')), 1000000000000)
        self.assertEqual(from_atomic(1000000000000), Decimal('1'))
        self.assertEqual(to_atomic(Decimal('0.000000000001')), 1)
        self.assertEqual(from_atomic(1), Decimal('0.000000000001'))

    def test_numeric_types(self):
        "Only check if conversion of given type succeeds or fails."
        self.assertTrue(to_atomic(1))
        self.assertTrue(to_atomic(1.0))
        if hasattr(sys, 'maxint'):  # Python 2.x
            self.assertTrue(to_atomic(sys.maxint + 1))
        self.assertRaises(ValueError, to_atomic, '1')

    def test_rounding(self):
        self.assertEqual(to_atomic(Decimal('1.0000000000004')), 1000000000000)
        self.assertEqual(as_monero(Decimal('1.0000000000014')), Decimal('1.000000000001'))

    def test_payment_id(self):
        pid = PaymentID('0')
        self.assertTrue(pid.is_short())
        self.assertEqual(pid, 0)
        self.assertEqual(pid, '0000000000000000')
        self.assertEqual(PaymentID(pid), pid)
        self.assertNotEqual(pid, None)
        pid = PaymentID('abcdef')
        self.assertTrue(pid.is_short())
        self.assertEqual(pid, 0xabcdef)
        self.assertEqual(pid, '0000000000abcdef')
        self.assertEqual(PaymentID(pid), pid)
        pid = PaymentID('1234567812345678')
        self.assertTrue(pid.is_short())
        self.assertEqual(pid, 0x1234567812345678)
        self.assertEqual(pid, '1234567812345678')
        self.assertEqual(PaymentID(pid), pid)
        pid = PaymentID('a1234567812345678')
        self.assertFalse(pid.is_short())
        self.assertEqual(pid, 0xa1234567812345678)
        self.assertEqual(pid, '00000000000000000000000000000000000000000000000a1234567812345678')
        self.assertEqual(PaymentID(pid), pid)
        self.assertRaises(ValueError, PaymentID, 2**256+1)
