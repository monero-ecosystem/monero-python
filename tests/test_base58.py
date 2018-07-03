import unittest

from monero.base58 import decode, encode


class Base58EncodeTestCase(unittest.TestCase):
    def test_encode_empty(self):
        self.assertEqual(encode(''), '')

    def test_encode_invalid_hex_length(self):
        with self.assertRaises(ValueError) as cm:
            encode('abcde')
        self.assertEqual(str(cm.exception), 'Hex string has invalid length: 5')


class Base58DecodeTestCase(unittest.TestCase):
    def test_decode_empty(self):
        self.assertEqual(decode(''), '')

    def test_decode_invalid_length_block(self):
        with self.assertRaises(ValueError) as cm:
            decode('f')
        self.assertEqual(str(cm.exception), 'Invalid encoded length: 1')
