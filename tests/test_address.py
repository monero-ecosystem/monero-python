import unittest

from monero.address import Address, SubAddress, IntegratedAddress, address

class Tests(object):
    def test_from_and_to_string(self):
        a = Address(self.addr)
        self.assertEqual(str(a), self.addr)
        self.assertEqual(a.spend_key(), self.psk)
        self.assertEqual(a.view_key(), self.pvk)

        ia = IntegratedAddress(self.iaddr)
        self.assertEqual(ia.payment_id(), self.pid)
        self.assertEqual(str(ia), self.iaddr)
        self.assertEqual(ia.spend_key(), self.psk)
        self.assertEqual(ia.view_key(), self.pvk)
        self.assertEqual(ia.base_address(), a)

        sa = SubAddress(self.subaddr)
        self.assertEqual(str(sa), self.subaddr)

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
        self.assertEqual(a.is_mainnet(), self.mainnet)
        self.assertEqual(a.is_testnet(), self.testnet)
        self.assertEqual(a.is_stagenet(), self.stagenet)
        self.assertEqual(a2.is_mainnet(), self.mainnet)
        self.assertEqual(a2.is_testnet(), self.testnet)
        self.assertEqual(a2.is_stagenet(), self.stagenet)

        ia = IntegratedAddress(self.iaddr)
        ia2 = address(self.iaddr)
        self.assertIsInstance(ia, IntegratedAddress)
        self.assertEqual(ia, ia2)
        self.assertEqual(ia, self.iaddr)
        self.assertEqual(self.iaddr, ia)
        self.assertEqual(ia.is_mainnet(), self.mainnet)
        self.assertEqual(ia.is_testnet(), self.testnet)
        self.assertEqual(ia.is_stagenet(), self.stagenet)
        self.assertEqual(ia2.is_mainnet(), self.mainnet)
        self.assertEqual(ia2.is_testnet(), self.testnet)
        self.assertEqual(ia2.is_stagenet(), self.stagenet)
        self.assertEqual(ia2.base_address(), a)

        self.assertEqual(ia.view_key(), a.view_key())
        self.assertEqual(ia.spend_key(), a.spend_key())

        sa = SubAddress(self.subaddr)
        sa2 = address(self.subaddr)
        self.assertIsInstance(sa2, SubAddress)
        self.assertEqual(sa, sa2)
        self.assertEqual(sa, self.subaddr)
        self.assertEqual(self.subaddr, sa)
        self.assertEqual(sa.is_mainnet(), self.mainnet)
        self.assertEqual(sa.is_testnet(), self.testnet)
        self.assertEqual(sa.is_stagenet(), self.stagenet)
        self.assertEqual(sa2.is_mainnet(), self.mainnet)
        self.assertEqual(sa2.is_testnet(), self.testnet)
        self.assertEqual(sa2.is_stagenet(), self.stagenet)

        self.assertNotEqual(a, 0)

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

class AddressTestCase(unittest.TestCase, Tests):
    addr = '43aeKax1ts4BoEbSyzKVbbDRmc8nsnpZLUpQBYvhUxs3KVrodnaFaBEQMDp69u4VaiEG3LSQXA6M61mXPrztCLuh7PFUAmd'
    psk = '33a7ceb933b793408d49e82c0a34664a4be7117243cb77a64ef280b866d8aa6e'
    pvk = '96f70d63d9d3558b97a5dd200a170b4f45b3177a274aa90496ea683896ff6438'
    pid = '4a6f686e47616c74'
    subaddr = '83bK2pMxCQXdRyd6W1haNWYRsF6Qb3iGa8gxKEynm9U7cYoXrMHFwRrFFuxRSgnLtGe7LM8SmrPY6L3TVBa3UV3YLuVJ7Rw'
    iaddr = '4DHKLPmWW8aBoEbSyzKVbbDRmc8nsnpZLUpQBYvhUxs3KVrodnaFaBEQMDp69u4VaiEG3LSQXA6M61mXPrztCLuhAR6GpL18QNwE8h3TuF'
    mainnet = True
    testnet = False
    stagenet = False
    addr_invalid = '43aeKax1ts4boEbSyzKVbbDRmc8nsnpZLUpQBYvhUxs3KVrodnaFaBEQMDp69u4VaiEG3LSQXA6M61mXPrztCLuh7PFUAmd'
    iaddr_invalid = '4DHKLpmWW8aBoEbSyzKVbbDRmc8nsnpZLUpQBYvhUxs3KVrodnaFaBEQMDp69u4VaiEG3LSQXA6M61mXPrztCLuhAR6GpL18QNwE8h3TuF'


class TestnetAddressTestCase(AddressTestCase, Tests):
    addr = '9vgV48wWAPTWik5QSUSoGYicdvvsbSNHrT9Arsx1XBTz6VrWPSgfmnUKSPZDMyX4Ms8R9TkhB4uFqK9s5LUBbV6YQN2Q9ag'
    psk = '5cbcfbcea7cc62b1aeb76758ad8df5f8cbe0c63d40c8cd9c49377bbc9c9b9520'
    pvk = 'de048ca310ff7d6e3b6714bccdebd62c56d680a10272846c875241fa2c5fc1cf'
    pid = '4a6f686e47616c74'
    iaddr = 'A6PA4wkzmeyWik5QSUSoGYicdvvsbSNHrT9Arsx1XBTz6VrWPSgfmnUKSPZDMyX4Ms8R9TkhB4uFqK9s5LUBbV6YbfyqvDecDn3E7cvp9b'
    subaddr = 'BbBjyYoYNNwFfL8RRVRTMiZUofBLpjRxdNnd5E4LyGcAK5CEsnL3gmE5QkrDRta7RPficGHcFdR6rUwWcjnwZVvCE3tLxhJ'
    mainnet = False
    testnet = True
    stagenet = False
    addr_invalid = '9vgV48wWAPTWik5QSUSoGYicdvvsbSNHrT9Arsx1XBTz6VrWPSgfmnUKSPZDMyX4Ms8R9TkhB4uFqK9s5LUbbV6YQN2Q9ag'
    iaddr_invalid = 'A6PA4wkzmeyWik5qSUSoGYicdvvsbSNHrT9Arsx1XBTz6VrWPSgfmnUKSPZDMyX4Ms8R9TkhB4uFqK9s5LUBbV6YbfyqvDecDn3E7cvp9b'


class StagenetAddressTestCase(AddressTestCase, Tests):
    addr = '56cXYWG13YKaT9z1aEy2hb9TZNnxrW3zE9S4nTQVDux5Qq7UYsmjuux3Zstxkorj9HAufyWLU3FwHW4uERQF6tkeUVogGN3'
    psk = '7e33891fe6ea30c7fd79d48e250906329104dc77407cf732699f41564df8ca8e'
    pvk = '77a3720428f91f0f58a196bb374f703b3ca45fa55f0764adc81ff241c4c797f3'
    pid = '4a6f686e47616c74'
    iaddr = '5GKCZK5VeoqaT9z1aEy2hb9TZNnxrW3zE9S4nTQVDux5Qq7UYsmjuux3Zstxkorj9HAufyWLU3FwHW4uERQF6tkehhE4RH8N7QfEAC8jMy'
    subaddr = '7417qYoKBoYXCugU2KvJBZExmyjav4n1MVME74AeWNwxQ39wKtbWdyP6YGuMK6C7HkAjBuVcbUYmCWbxDLwk9GAX4qyb48U'
    mainnet = False
    testnet = False
    stagenet = True
    addr_invalid ='7417qYoKBoYXCugU2KvJBZExmyjav4n1MVME74AeWNwxQ39wKtbWdyP6YGuMK6C7HkAjBuVcbUYmCWbyDLwk9GAX4qyb48U'
    iaddr_invalid = '5GKCZK5VeuqaT9z1aEy2hb9TZNnxrW3zE9S4nTQVDux5Qq7UYsmjuux3Zstxkorj9HAufyWLU3FwHW4uERQF6tkehhE4RH8N7QfEAC8jMy'
