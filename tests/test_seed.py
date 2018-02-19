#!/usr/bin/env python

import unittest
from monero.seed import Seed, get_checksum

class SeedTestCase(unittest.TestCase):

    def test_mnemonic_seed(self):
        # Known good 25 word seed phrases should construct a class, validate checksum, and register valid hex
        seed = Seed("wedge going quick racetrack auburn physics lectures light waist axes whipped habitat square awkward together injury niece nugget guarded hive obnoxious waxing faked folding square")
        self.assertTrue(seed.validate_checksum())
        self.assertEqual(seed.hex, "8ffa9f586b86d294d93731765d192765311bddc76a4fa60311f8af36bbf6fb06")

        # Known good 24 word seed phrases should construct a class, store phrase with valid checksum, and register valid hex
        seed = Seed("wedge going quick racetrack auburn physics lectures light waist axes whipped habitat square awkward together injury niece nugget guarded hive obnoxious waxing faked folding")
        seed.encode_seed()
        self.assertTrue(seed.validate_checksum())
        self.assertEqual(seed.hex, "8ffa9f586b86d294d93731765d192765311bddc76a4fa60311f8af36bbf6fb06")

        # Known good 25 word hexadecimal strings should construct a class, store phrase with valid checksum, and register valid hex
        seed = Seed("8ffa9f586b86d294d93731765d192765311bddc76a4fa60311f8af36bbf6fb06")
        self.assertTrue(seed.validate_checksum())
        self.assertEqual(seed.phrase, "wedge going quick racetrack auburn physics lectures light waist axes whipped habitat square awkward together injury niece nugget guarded hive obnoxious waxing faked folding square")

        # Known good 13 word seed phrases should construct a class, validate checksum, and register valid hex
        seed = Seed("ought knowledge upright innocent eldest nerves gopher fowls below exquisite aces basin fowls")
        self.assertTrue(seed.validate_checksum())
        self.assertEqual(seed.hex, "932d70711acc2d536ca11fcb79e05516")

        # Known good 12 word seed phrases should construct a class, store phrase with valid checksum, and register valid hex
        seed = Seed("ought knowledge upright innocent eldest nerves gopher fowls below exquisite aces basin")
        seed.encode_seed()
        self.assertTrue(seed.validate_checksum())
        self.assertEqual(seed.hex, "932d70711acc2d536ca11fcb79e05516")

        # Known good 13 word hexadecimal strings should construct a class, store phrase with valid checksum, and register valid hex
        seed = Seed("932d70711acc2d536ca11fcb79e05516")
        self.assertTrue(seed.validate_checksum())
        self.assertEqual(seed.phrase, "ought knowledge upright innocent eldest nerves gopher fowls below exquisite aces basin fowls")

        # Generated seed phrases should be 25 words, validate checksum, register valid hex, and return matching outputs for decode/encode
        seed = Seed()
        seed_split = seed.phrase.split(" ")
        self.assertTrue(len(seed_split) == 25)
        self.assertTrue(seed.validate_checksum())
        self.assertTrue(len(seed.hex) % 8 == 0)
        self.assertEqual(seed.hex, seed.decode_seed())
        self.assertEqual(seed.phrase, seed.encode_seed())

        # Invalid phrases should not be allowed
        with self.assertRaises(ValueError) as ts:
            Seed("oh damn you thought fool")
        self.assertEqual(ts.expected, ValueError)
        with self.assertRaises(ValueError) as ts:
            Seed("Thi5isMyS3cr3tPa55w0rd")
        self.assertEqual(ts.expected, ValueError)
        with self.assertRaises(ValueError) as ts:
            Seed(" ")
        self.assertEqual(ts.expected, ValueError)
        with self.assertRaises(ValueError) as ts:
            Seed("\\x008")
        self.assertEqual(ts.expected, ValueError)

if __name__ == "__main__":
    unittest.main()
