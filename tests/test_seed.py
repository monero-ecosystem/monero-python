#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from monero.seed import Seed

class SeedTestCase(unittest.TestCase):

    def test_mnemonic_seed(self):
        # Known good 25 word seed phrases should construct a class and register valid hex
        seed = Seed("wedge going quick racetrack auburn physics lectures light waist axes whipped habitat square awkward together injury niece nugget guarded hive obnoxious waxing faked folding square")
        self.assertEqual(seed.hex, "8ffa9f586b86d294d93731765d192765311bddc76a4fa60311f8af36bbf6fb06")

        # Known good 24 word seed phrases should construct a class, store phrase, and register valid hex
        seed = Seed("wedge going quick racetrack auburn physics lectures light waist axes whipped habitat square awkward together injury niece nugget guarded hive obnoxious waxing faked folding")
        self.assertEqual(seed.hex, "8ffa9f586b86d294d93731765d192765311bddc76a4fa60311f8af36bbf6fb06")

        # Known good 25 word hexadecimal strings should construct a class, store phrase, and register valid hex
        seed = Seed("8ffa9f586b86d294d93731765d192765311bddc76a4fa60311f8af36bbf6fb06")
        self.assertEqual(seed.phrase, "wedge going quick racetrack auburn physics lectures light waist axes whipped habitat square awkward together injury niece nugget guarded hive obnoxious waxing faked folding square")
        self.assertTrue(len(seed.hex) % 8 == 0)

        # Known good 13 word seed phrases should construct a class and register valid hex
        seed = Seed("ought knowledge upright innocent eldest nerves gopher fowls below exquisite aces basin fowls")
        self.assertEqual(seed.hex, "932d70711acc2d536ca11fcb79e05516")

        # Known good 12 word seed phrases should construct a class, store phrase, and register valid hex
        seed = Seed("ought knowledge upright innocent eldest nerves gopher fowls below exquisite aces basin")
        self.assertEqual(seed.hex, "932d70711acc2d536ca11fcb79e05516")

        # Known good 13 word hexadecimal strings should construct a class, store phrase, and register valid hex
        seed = Seed("932d70711acc2d536ca11fcb79e05516")
        self.assertEqual(seed.phrase, "ought knowledge upright innocent eldest nerves gopher fowls below exquisite aces basin fowls")
        self.assertTrue(len(seed.hex) % 8 == 0)

        # Generated seed phrases should be 25 words, register valid hex
        seed = Seed()
        seed_split = seed.phrase.split(" ")
        self.assertTrue(len(seed_split) == 25)
        self.assertTrue(len(seed.hex) % 8 == 0)

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


    def test_keys(self):
        seed = Seed("adjust mugged vaults atlas nasty mews damp toenail suddenly toxic possible "\
            "framed succeed fuzzy return demonstrate nucleus album noises peculiar virtual "\
            "rowboat inorganic jester fuzzy")
        self.assertFalse(seed.is_mymonero())
        self.assertEqual(
            seed.secret_spend_key(),
            '482700617ba810f94035d7f4d7ccc1a29878e165b4867872b705204c85406906')
        self.assertEqual(
            seed.secret_view_key(),
            '09ed72c713d3e9e19bef2f5204cf85f6cb25de7842aa0722abeb12697f171903')
        self.assertEqual(
            seed.public_spend_key(),
            '4ee576f52b9c6a824a3d5c2832d117177d2bb9992507c2c78788bb8dbaf4b640')
        self.assertEqual(
            seed.public_view_key(),
            'e1ef99d66312ec0b16b17c66c591ab59594e21621588b63b62fa69fe615a768e')
        self.assertEqual(
            seed.public_address(),
            '44cWztNFdAqNnycvZbUoj44vsbAEmKnx9aNgkjHdjtMsBrSeKiY8J4s2raH7EMawA2Fwo9utaRTV7Aw8EcTMNMxhH4YtKdH')
        self.assertEqual(
            seed.public_address(net='stagenet'),
            '54pZ5jHDGmwNnycvZbUoj44vsbAEmKnx9aNgkjHdjtMsBrSeKiY8J4s2raH7EMawA2Fwo9utaRTV7Aw8EcTMNMxhH6cuARW')

        seed = Seed("dwelt idols lopped blender haggled rabbits piloted value swagger taunts toolbox upgrade swagger")
        self.assertTrue(seed.is_mymonero())
        # check if the same seed without checksum matches the hex
        self.assertEqual(seed.hex, Seed(" ".join(seed.phrase.split(" ")[:12])).hex)
        # the following fails, #21 addresses that
        self.assertEqual(
            seed.secret_spend_key(),
            'a67505f92004dd6242b64acd16e34ecf788a2d28b6072091e054238d84591403')
        self.assertEqual(
            seed.secret_view_key(),
            '83f652cb370948c8cbcf06839df043aa8c0d0ed36e38b3c827c4c00370af1a0f')
        self.assertEqual(
            seed.public_address(),
            '47dwi1w9it69yZyTBBRD52ctQqw3B2FZx79bCEgVUKGHH2m7MjmaXrjeQfchMMkarG6AF9a36JvBWCyRaqEcUixpKLQRxdj')


if __name__ == "__main__":
    unittest.main()
