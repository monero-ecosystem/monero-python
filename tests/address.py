import unittest

from monero.address import Address, IntegratedAddress, address

class Tests(object):
    def test_from_and_to_string(self):
        a = Address(self.addr)
        self.assertEqual(str(a), self.addr)
        self.assertEqual(a.get_spend_key(), self.psk)
        self.assertEqual(a.get_view_key(), self.pvk)

        ia = IntegratedAddress(self.iaddr)
        self.assertEqual(ia.get_payment_id(), self.pid)
        self.assertEqual(str(ia), self.iaddr)
        self.assertEqual(ia.get_spend_key(), self.psk)
        self.assertEqual(ia.get_view_key(), self.pvk)
        self.assertEqual(ia.get_base_address(), a)

    def test_payment_id(self):
        a = Address(self.addr)
        ia = a.with_payment_id(self.pid)
        self.assertIsInstance(ia, IntegratedAddress)
        self.assertEqual(ia.get_payment_id(), self.pid)
        self.assertEqual(str(ia), self.iaddr)

    def test_recognition_and_comparisons(self):
        a = Address(self.addr)
        a2 = address(self.addr)
        self.assertIsInstance(a2, Address)
        self.assertEqual(a, a2)
        self.assertEqual(a, self.addr)
        self.assertEqual(self.addr, a)
        self.assertEqual(a.is_testnet(), self.testnet)
        self.assertEqual(a2.is_testnet(), self.testnet)

        ia = IntegratedAddress(self.iaddr)
        ia2 = address(self.iaddr)
        self.assertIsInstance(ia, IntegratedAddress)
        self.assertEqual(ia, ia2)
        self.assertEqual(ia, self.iaddr)
        self.assertEqual(self.iaddr, ia)
        self.assertEqual(ia.is_testnet(), self.testnet)
        self.assertEqual(ia2.is_testnet(), self.testnet)
        self.assertEqual(ia2.get_base_address(), a)

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

class AddressTestCase(unittest.TestCase, Tests):
    addr = '43aeKax1ts4BoEbSyzKVbbDRmc8nsnpZLUpQBYvhUxs3KVrodnaFaBEQMDp69u4VaiEG3LSQXA6M61mXPrztCLuh7PFUAmd'
    psk = '33a7ceb933b793408d49e82c0a34664a4be7117243cb77a64ef280b866d8aa6e'
    pvk = '96f70d63d9d3558b97a5dd200a170b4f45b3177a274aa90496ea683896ff6438'
    pid = '4a6f686e47616c74'
    iaddr = '4DHKLPmWW8aBoEbSyzKVbbDRmc8nsnpZLUpQBYvhUxs3KVrodnaFaBEQMDp69u4VaiEG3LSQXA6M61mXPrztCLuhAR6GpL18QNwE8h3TuF'
    testnet = False


class TestnetAddressTestCase(AddressTestCase, Tests):
    addr = '9u9j6xG1GNu4ghrdUL35m5PQcJV69YF8731DSTDoh7pDgkBWz2LWNzncq7M5s1ARjPRhvGPX4dBUeC3xNj4wzfrjV6SY3e9'
    psk = '345b201b8d1ba216074e3c45ca606c85f68563f60d0b8c0bfab5123f80692aed'
    pvk = '9deb70cc7e1e23d635de2d5a3086a293b4580dc2b9133b4211bc09f22fadc4f9'
    pid = '4a6f686e47616c74'
    iaddr = 'A4rQ7m5VseR4ghrdUL35m5PQcJV69YF8731DSTDoh7pDgkBWz2LWNzncq7M5s1ARjPRhvGPX4dBUeC3xNj4wzfrjihS6W83Km1mE7W3kMa'
    testnet = True
