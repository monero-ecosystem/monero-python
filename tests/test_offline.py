import json
import os
import unittest

from monero.backends.offline import OfflineWallet
from monero.wallet import Wallet
from tests.utils import classproperty


class Tests(object):
    @classproperty
    def __test__(cls):
        return issubclass(cls, unittest.TestCase)

    def setUp(self):
        self.subaddresses = json.load(open(os.path.join(
                os.path.dirname(__file__),
                'data',
                '{}-subaddrs.json'.format(self.net))))
        self.wallet = Wallet(OfflineWallet(self.addr, view_key=self.svk))

    def test_subaddresses(self):
        major = 0
        for acc in self.subaddresses:
            minor = 0
            for subaddr in acc:
                self.assertEqual(
                        self.wallet.get_address(major, minor),
                        subaddr,
                        msg='major={}, minor={}'.format(major,minor))
                minor += 1
            major += 1


class AddressTestCase(Tests, unittest.TestCase):
    addr = '47ewoP19TN7JEEnFKUJHAYhGxkeTRH82sf36giEp9AcNfDBfkAtRLX7A6rZz18bbNHPNV7ex6WYbMN3aKisFRJZ8Ebsmgef'
    ssk = 'e0fe01d5794e240a26609250c0d7e01673219eececa3f499d5cfa20a75739b0a'
    svk = '6d9056aa2c096bfcd2f272759555e5764ba204dd362604a983fa3e0aafd35901'
    net = 'mainnet'

    def test_subaddress_out_of_range(self):
        self.assertRaises(ValueError, self.wallet.get_address, 0, -1)
        self.assertRaises(ValueError, self.wallet.get_address, -1, 0)
        self.assertRaises(ValueError, self.wallet.get_address, 1, 2**32)
        self.assertRaises(ValueError, self.wallet.get_address, 2**32, 1)


class TestnetAddressTestCase(Tests, unittest.TestCase):
    addr = '9wuKTHsxGiwEsMp2fYzJiVahyhU2aZi1oZ6R6fK5U64uRa1Pxi8diZh2S1GJFqYXRRhcbfzfWiPD819zKEZkXTMwP7hMs5N'
    ssk = '4f5b7af2c1942067ba33d34318b9735cb46ab5d50b75294844c82a9dd872c201'
    svk = '60cf228f2bf7f6a70643afe9468fde254145dbd3aab4072ede14bf8bae914103'
    net = 'testnet'


class StagenetAddressTestCase(Tests, unittest.TestCase):
    addr = '52jzuBBUMty3xPL3JsQxGP74LDuV6E1LS8Zda1PbdqQjGzFmH6N9ep9McbFKMALujVT9S5mKpbEgC5VPhfoAiVj8LdAqbp6'
    ssk = 'a8733c61797115db4ec8a5ce39fb811f81dd4ec163b880526683e059c7e62503'
    svk = 'fd5c0d25f8f994268079a4f7844274dc870a7c2b88fbfc24ba318375e1d9430f'
    net = 'stagenet'
