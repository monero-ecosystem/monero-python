import pytest
import unittest

from monero import const
from monero.address import Address, SubAddress, IntegratedAddress, address
from tests.utils import classproperty


class Tests(object):
    @classproperty
    def __test__(cls):
        return issubclass(cls, unittest.TestCase)

    def test_from_and_to_string(self):
        a = Address(self.addr)
        self.assertEqual(str(a), self.addr)
        self.assertEqual("{:s}".format(a), self.addr)
        self.assertEqual(a.spend_key(), self.psk)
        self.assertEqual(a.view_key(), self.pvk)
        self.assertEqual(hash(a), hash(self.addr))
        ba = Address(self.addr.encode())
        self.assertEqual(ba, a)
        ba = address(self.addr.encode())
        self.assertEqual(ba, a)

        ia = IntegratedAddress(self.iaddr)
        self.assertEqual(ia.payment_id(), self.pid)
        self.assertEqual(str(ia), self.iaddr)
        self.assertEqual("{:s}".format(ia), self.iaddr)
        self.assertEqual(ia.spend_key(), self.psk)
        self.assertEqual(ia.view_key(), self.pvk)
        self.assertEqual(ia.base_address(), a)
        ba = IntegratedAddress(self.iaddr.encode())
        self.assertEqual(ba, ia)
        ba = address(self.iaddr.encode())
        self.assertEqual(ba, ia)

        sa = SubAddress(self.subaddr)
        self.assertEqual(str(sa), self.subaddr)
        self.assertEqual("{:s}".format(sa), self.subaddr)
        ba = SubAddress(self.subaddr.encode())
        self.assertEqual(ba, sa)
        ba = address(self.subaddr.encode())
        self.assertEqual(ba, sa)

    def test_payment_id(self):
        a = Address(self.addr)
        ia = a.with_payment_id(self.pid)
        self.assertIsInstance(ia, IntegratedAddress)
        self.assertEqual(ia.payment_id(), self.pid)
        self.assertEqual(str(ia), self.iaddr)

    def test_recognition_and_comparisons(self):
        a = Address(self.addr)
        a2 = address(self.addr)
        self.assertIsInstance(a2, Address)
        self.assertEqual(a, a2)
        self.assertEqual(a, self.addr)
        self.assertEqual(self.addr, a)
        self.assertEqual(hash(a), hash(self.addr))
        self.assertEqual(a.net, self.net)
        self.assertEqual(a2.net, self.net)

        ia = IntegratedAddress(self.iaddr)
        ia2 = address(self.iaddr)
        self.assertIsInstance(ia, IntegratedAddress)
        self.assertEqual(ia, ia2)
        self.assertEqual(ia, self.iaddr)
        self.assertEqual(self.iaddr, ia)
        self.assertEqual(hash(ia), hash(self.iaddr))
        self.assertEqual(ia.net, self.net)
        self.assertEqual(ia2.net, self.net)
        self.assertEqual(ia2.base_address(), a)

        self.assertEqual(ia.view_key(), a.view_key())
        self.assertEqual(ia.spend_key(), a.spend_key())

        sa = SubAddress(self.subaddr)
        sa2 = address(self.subaddr)
        self.assertIsInstance(sa2, SubAddress)
        self.assertEqual(sa, sa2)
        self.assertEqual(sa, self.subaddr)
        self.assertEqual(self.subaddr, sa)
        self.assertEqual(hash(sa), hash(self.subaddr))
        self.assertEqual(sa.net, self.net)
        self.assertEqual(sa2.net, self.net)

        self.assertNotEqual(a, 0)

    def test_check_private_view_key(self):
        a = Address(self.addr)
        self.assertFalse(a.check_private_view_key(self.ssk))
        self.assertTrue(a.check_private_view_key(self.svk))
        self.assertFalse(a.check_private_view_key(self.psk))
        self.assertFalse(a.check_private_view_key(self.pvk))
        self.assertFalse(a.check_private_view_key('0000000000000000000000000000000000000000000000000000000000000000'))

    def test_check_private_spend_key(self):
        a = Address(self.addr)
        self.assertTrue(a.check_private_spend_key(self.ssk))
        self.assertFalse(a.check_private_spend_key(self.svk))
        self.assertFalse(a.check_private_spend_key(self.psk))
        self.assertFalse(a.check_private_spend_key(self.pvk))
        self.assertFalse(a.check_private_spend_key('0000000000000000000000000000000000000000000000000000000000000000'))

    def test_idempotence(self):
        a = Address(self.addr)
        a_idem = Address(a)
        self.assertEqual(a, a_idem)
        a_idem = Address(str(a))
        self.assertEqual(a, a_idem)
        a_idem = address(a)
        self.assertEqual(a, a_idem)

        ia = IntegratedAddress(self.iaddr)
        ia_idem = IntegratedAddress(ia)
        self.assertEqual(ia, ia_idem)
        ia_idem = IntegratedAddress(str(ia))
        self.assertEqual(ia, ia_idem)
        ia_idem = address(ia)
        self.assertEqual(ia, ia_idem)

    def test_invalid(self):
        self.assertRaises(ValueError, Address, self.addr_invalid)
        self.assertRaises(ValueError, Address, self.iaddr_invalid)
        a = Address(self.addr)
        self.assertRaises(TypeError, a.with_payment_id, 2**64+1)
        self.assertRaises(TypeError, a.with_payment_id, "%x" % (2**64+1))
        s = SubAddress(self.subaddr)
        self.assertRaises(TypeError, s.with_payment_id, 0)
        self.assertRaises(ValueError, address, 'whatever')
        self.assertRaises(ValueError, Address, 'whatever')
        self.assertRaises(ValueError, SubAddress, 'whatever')
        self.assertRaises(ValueError, IntegratedAddress, 'whatever')
        # Aeon
        self.assertRaises(
            ValueError,
            address,
            'Wmtj8UAJhdrhbKvwyBJmLEUZKHcffv2VHNBaq6oTxJFwJjUj3QwMUSS32mddSX7vchbxXdmb4QuZA9TsN47441f61yAYLQYTo')
        # invalid netbyte
        self.assertRaises(
            ValueError,
            address,
            'Cf6RinMUztY5otm6NEFjg3UWBBkXK6Lh23wKrLFMEcCY7i3A6aPLH9i4QMCkf6CdWk8Q9N7yoJf7ANKgtQMuPM6JANXgCWs')

    def test_type_mismatch(self):
        self.assertRaises(ValueError, Address, self.iaddr)
        self.assertRaises(ValueError, Address, self.subaddr)
        self.assertRaises(ValueError, IntegratedAddress, self.addr)
        self.assertRaises(ValueError, IntegratedAddress, self.subaddr)
        self.assertRaises(ValueError, SubAddress, self.addr)
        self.assertRaises(ValueError, SubAddress, self.iaddr)

    def test_subaddress_cannot_into_integrated(self):
        sa = SubAddress(self.subaddr)
        self.assertRaises(TypeError, sa.with_payment_id, self.pid)


class AddressTestCase(Tests, unittest.TestCase):
    addr = '47ewoP19TN7JEEnFKUJHAYhGxkeTRH82sf36giEp9AcNfDBfkAtRLX7A6rZz18bbNHPNV7ex6WYbMN3aKisFRJZ8Ebsmgef'
    ssk = 'e0fe01d5794e240a26609250c0d7e01673219eececa3f499d5cfa20a75739b0a'
    svk = '6d9056aa2c096bfcd2f272759555e5764ba204dd362604a983fa3e0aafd35901'
    psk = '9f2a76d879aaf0670039dc8dbdca01f0ca26a2f6d93268e3674666bfdc5957e4'
    pvk = '716cfc7da7e6ce366935c55747839a85be798037ab189c7dd0f10b7f1690cb78'
    pid = '4a6f686e47616c74'
    iaddr = '4HMcpBpe4ddJEEnFKUJHAYhGxkeTRH82sf36giEp9AcNfDBfkAtRLX7A6rZz18bbNHPNV7ex6WYbMN3aKisFRJZ8M7yKhzQhKW3ECCLWQw'
    subaddr = '84LooD7i35SFppgf4tQ453Vi3q5WexSUXaVgut69ro8MFnmHwuezAArEZTZyLr9fS6QotjqkSAxSF6d1aDgsPoX849izJ7m'
    net = const.NET_MAIN
    addr_invalid = '47ewoP19TN7JCEnFKUJHAYhGxkeTRH82sf36giEp9AcNfDBfkAtRLX7A6rZz18bbNHPNV7ex6WYbMN3aKisFRJZ8Ebsmgef'
    iaddr_invalid = '4HMcpBpe4ddJEEnFKUJHAYhGxkyTRH82sf36giEp9AcNfDBfkAtRLX7A6rZz18bbNHPNV7ex6WYbMN3aKisFRJZ8M7yKhzQhKW3ECCLWQw'


class TestnetAddressTestCase(Tests, unittest.TestCase):
    addr = '9wuKTHsxGiwEsMp2fYzJiVahyhU2aZi1oZ6R6fK5U64uRa1Pxi8diZh2S1GJFqYXRRhcbfzfWiPD819zKEZkXTMwP7hMs5N'
    ssk = '4f5b7af2c1942067ba33d34318b9735cb46ab5d50b75294844c82a9dd872c201'
    svk = '60cf228f2bf7f6a70643afe9468fde254145dbd3aab4072ede14bf8bae914103'
    psk = '7cf743dcfd23d452e9b2936caeb622c9849f1ff1ddfd62bfdfac64113c1a4e92'
    pvk = 'e3924b14d99a9c088e5a45278d5218f2d053b1c03c480f00ed2ee3dce80806c4'
    pid = '4a6f686e47616c74'
    subaddr = 'BaU3yLuDqdcETYzeF7vFSVEKNR4sSGxBV1Evrw5yNBf2VMiuAwfDmiF3RHqLHkaA5A6RGiNNRUqvtaqhMtdjA1SQ1tnQV8D'
    iaddr = 'A7bzU6hSszTEsMp2fYzJiVahyhU2aZi1oZ6R6fK5U64uRa1Pxi8diZh2S1GJFqYXRRhcbfzfWiPD819zKEZkXTMwZqGSmLeBXqMEBnZVkh'
    net = const.NET_TEST
    addr_invalid = '9wuKTHsxGiwEsMp3fYzJiVahyhU2aZi1oZ6R6fK5U64uRa1Pxi8diZh2S1GJFqYXRRhcbfzfWiPD819zKEZkXTMwP7hMs5N'
    iaddr_invalid = 'A7bzU6hSszTEsMp2fYzJiVahyhU2aZi2oZ6R6fK5U64uRa1Pxi8diZh2S1GJFqYXRRhcbfzfWiPD819zKEZkXTMwZqGSmLeBXqMEBnZVkh'


class StagenetAddressTestCase(Tests, unittest.TestCase):
    addr = '52jzuBBUMty3xPL3JsQxGP74LDuV6E1LS8Zda1PbdqQjGzFmH6N9ep9McbFKMALujVT9S5mKpbEgC5VPhfoAiVj8LdAqbp6'
    ssk = 'a8733c61797115db4ec8a5ce39fb811f81dd4ec163b880526683e059c7e62503'
    svk = 'fd5c0d25f8f994268079a4f7844274dc870a7c2b88fbfc24ba318375e1d9430f'
    psk = '180c1d7bbf7f2e11aa90d0f61bf49024370e01cd54f33f2d36bba0357c9c205f'
    pvk = '94b66a81e646927b3da74392306f789c5024734b4ce6351ad74c4c7d7351b3ad'
    pid = '4a6f686e47616c74'
    subaddr = '7AeQwvrLtPeYoXVPRkEu8oEL7N9wnqHjYKwSvTf6YKbHgYmw6AJMsjggzVLo21egMK9qcoV1mxCTfP4FbaGb7JEMDfpLetk'
    iaddr = '5CSfuyzxyAV3xPL3JsQxGP74LDuV6E1LS8Zda1PbdqQjGzFmH6N9ep9McbFKMALujVT9S5mKpbEgC5VPhfoAiVj8Vz8ySmoqYgTE8dR1yS'
    net = const.NET_STAGE
    addr_invalid = '52jzuBBUMty3xPL3JsQxGP74LDuV6H1LS8Zda1PbdqQjGzFmH6N9ep9McbFKMALujVT9S5mKpbEgC5VPhfoAiVj8LdAqbp6'
    iaddr_invalid = '5CSfuyzxyAV3xPL3JsQxGP74LDuV6E1LS8Zda1PbdqQjGzFmH6N9ep9McbFKMALujVT9S5mKppEgC5VPhfoAiVj8Vz8ySmoqYgTE8dR1yS'


class KnownBugsTest(unittest.TestCase):
    def test_issue27(self):
        addr = '41tjz19p4qc2gudqnwsdrhgcgxud8bgxy84ufe869nyw7ywbxw9s9gqbix7piu9d7qjvbjtrdnbubhcf663ydq3bsxj1brL'
        self.assertRaises(ValueError, Address, addr)
        self.assertRaises(ValueError, SubAddress, addr)
        self.assertRaises(ValueError, IntegratedAddress, addr)
        self.assertRaises(ValueError, address, addr)
