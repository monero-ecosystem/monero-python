from datetime import datetime
from decimal import Decimal
import unittest
import warnings

from monero.wallet import Wallet
from monero.account import Account
from monero.address import address
from monero.numbers import PaymentID
from monero.transaction import IncomingPayment, Transaction

class FiltersTestCase(unittest.TestCase):
    def setUp(self):
        class MockBackend(object):
            def __init__(self):
                self.transfers = []
                tx = Transaction(
                    timestamp=datetime(2018, 1, 29, 15, 0, 25),
                    height=1087606,
                    hash='a0b876ebcf7c1d499712d84cedec836f9d50b608bb22d6cb49fd2feae3ffed14',
                    fee=Decimal('0.00352891'))
                pm = IncomingPayment(
                    amount=Decimal('1'),
                    local_address=address('Bf6ngv7q2TBWup13nEm9AjZ36gLE6i4QCaZ7XScZUKDUeGbYEHmPRdegKGwLT8tBBK7P6L32RELNzCR6QzNFkmogDjvypyV'),
                    payment_id=PaymentID('0166d8da6c0045c51273dd65d6f63734beb8a84e0545a185b2cfd053fced9f5d'),
                    transaction=tx)
                self.transfers.append(pm)
                tx = Transaction(
                    timestamp=datetime(2018, 1, 29, 14, 57, 47),
                    height=1087601,
                    hash='f34b495cec77822a70f829ec8a5a7f1e727128d62e6b1438e9cb7799654d610e',
                    fee=Decimal('0.008661870000'))
                pm = IncomingPayment(
                    amount=Decimal('3.000000000000'),
                    local_address=address('BhE3cQvB7VF2uuXcpXp28Wbadez6GgjypdRS1F1Mzqn8Advd6q8VfaX8ZoEDobjejrMfpHeNXoX8MjY8q8prW1PEALgr1En'),
                    payment_id=PaymentID('f75ad90e25d71a12'),
                    transaction=tx)
                self.transfers.append(pm)
                tx = Transaction(
                    timestamp=datetime(2018, 1, 29, 13, 17, 18),
                    height=1087530,
                    hash='5c3ab739346e9d98d38dc7b8d36a4b7b1e4b6a16276946485a69797dbf887cd8',
                    fee=Decimal('0.000962550000'))
                pm = IncomingPayment(
                    amount=Decimal('10.000000000000'),
                    local_address=address('9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC'),
                    payment_id=PaymentID('f75ad90e25d71a12'),
                    transaction=tx)
                self.transfers.append(pm)
                tx = Transaction(
                    timestamp=datetime(2018, 1, 29, 13, 17, 18),
                    height=1087530,
                    hash='4ea70add5d0c7db33557551b15cd174972fcfc73bf0f6a6b47b7837564b708d3',
                    fee=Decimal('0.000962550000'))
                pm = IncomingPayment(
                    amount=Decimal('4.000000000000'),
                    local_address=address('9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC'),
                    payment_id=PaymentID('f75ad90e25d71a12'),
                    transaction=tx)
                self.transfers.append(pm)
                tx = Transaction(
                    timestamp=datetime(2018, 1, 29, 13, 17, 18),
                    height=1087530,
                    hash='e9a71c01875bec20812f71d155bfabf42024fde3ec82475562b817dcc8cbf8dc',
                    fee=Decimal('0.000962550000'))
                pm = IncomingPayment(
                    amount=Decimal('2.120000000000'),
                    local_address=address('9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC'),
                    payment_id=PaymentID('cb248105ea6a9189'),
                    transaction=tx)
                self.transfers.append(pm)
                tx = Transaction(
                    timestamp=datetime(2018, 1, 29, 14, 57, 47),
                    height=1087601,
                    hash='5ef7ead6a041101ed326568fbb59c128403cba46076c3f353cd110d969dac808',
                    fee=Decimal('0.000962430000'))
                pm = IncomingPayment(
                    amount=Decimal('7.000000000000'),
                    local_address=address('BhE3cQvB7VF2uuXcpXp28Wbadez6GgjypdRS1F1Mzqn8Advd6q8VfaX8ZoEDobjejrMfpHeNXoX8MjY8q8prW1PEALgr1En'),
                    payment_id=PaymentID('0000000000000000'),
                    transaction=tx)
                self.transfers.append(pm)
                tx = Transaction(
                    timestamp=datetime(2018, 1, 29, 13, 17, 18),
                    height=1087530,
                    hash='cc44568337a186c2e1ccc080b43b4ae9db26a07b7afd7edeed60ce2fc4a6477f',
                    fee=Decimal('0.000962550000'))
                pm = IncomingPayment(
                    amount=Decimal('10.000000000000'),
                    local_address=address('9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC'),
                    payment_id=PaymentID('0000000000000000'),
                    transaction=tx)
                self.transfers.append(pm)
                tx = Transaction(
                    timestamp=datetime(2018, 1, 29, 21, 13, 28),
                    height=None,
                    hash='d29264ad317e8fdb55ea04484c00420430c35be7b3fe6dd663f99aebf41a786c',
                    fee=Decimal('0.000961950000'))
                pm = IncomingPayment(
                    amount=Decimal('3.140000000000'),
                    local_address=address('9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC'),
                    payment_id=PaymentID('03f6649304ea4cb2'),
                    transaction=tx)
                self.transfers.append(pm)

            def height(self):
                return 1087607

            def accounts(self):
                return [Account(self, 0)]

            def transfers_in(self, account, pmtfilter):
                return list(pmtfilter.filter(self.transfers))

        self.wallet = Wallet(MockBackend())

    def test_filter_none(self):
        pmts = self.wallet.incoming()
        self.assertEqual(len(pmts), 7)

    def test_filter_payment_id(self):
        pmts = self.wallet.incoming(payment_id='cb248105ea6a9189')
        self.assertEqual(len(pmts), 1)
        self.assertEqual(
            pmts[0].transaction.hash,
            'e9a71c01875bec20812f71d155bfabf42024fde3ec82475562b817dcc8cbf8dc')
        pmts = self.wallet.incoming(payment_id='f75ad90e25d71a12')
        self.assertEqual(len(pmts), 3)
        pmts = self.wallet.incoming(payment_id=('cb248105ea6a9189', 'f75ad90e25d71a12'))
        self.assertEqual(len(pmts), 4)
        self.assertEqual(
            pmts,
            self.wallet.incoming(payment_id=(PaymentID('cb248105ea6a9189'), 'f75ad90e25d71a12')))

    def test_filter_address(self):
        pmts = self.wallet.incoming(
            local_address='BhE3cQvB7VF2uuXcpXp28Wbadez6GgjypdRS1F1Mzqn8Advd6q8VfaX8ZoEDobjejrMfpHeNXoX8MjY8q8prW1PEALgr1En')
        self.assertEqual(len(pmts), 2)
        self.assertEqual(
            pmts,
            self.wallet.incoming(
                local_address=address('BhE3cQvB7VF2uuXcpXp28Wbadez6GgjypdRS1F1Mzqn8Advd6q8VfaX8ZoEDobjejrMfpHeNXoX8MjY8q8prW1PEALgr1En')))
        pmts = self.wallet.incoming(
            local_address=(
                'BhE3cQvB7VF2uuXcpXp28Wbadez6GgjypdRS1F1Mzqn8Advd6q8VfaX8ZoEDobjejrMfpHeNXoX8MjY8q8prW1PEALgr1En',
                'Bf6ngv7q2TBWup13nEm9AjZ36gLE6i4QCaZ7XScZUKDUeGbYEHmPRdegKGwLT8tBBK7P6L32RELNzCR6QzNFkmogDjvypyV'))
        self.assertEqual(len(pmts), 3)

    def test_filter_mempool(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            pmts = self.wallet.incoming()
            self.assertEqual(len(pmts), 7)
            for p in pmts:
                self.assertGreater(self.wallet.confirmations(p.transaction), 0)
            pmts = self.wallet.incoming(unconfirmed=True)
            self.assertEqual(len(pmts), 8)
            pmts = self.wallet.incoming(unconfirmed=True, confirmed=False)
            self.assertEqual(len(pmts), 1)
            self.assertEqual(
                pmts[0].transaction.hash,
                'd29264ad317e8fdb55ea04484c00420430c35be7b3fe6dd663f99aebf41a786c')
            self.assertEqual(self.wallet.confirmations(pmts[0]), 0)
            self.assertEqual(self.wallet.confirmations(pmts[0].transaction), 0)
            self.assertEqual(len(w), 0)
            pmts = self.wallet.incoming(unconfirmed=True, confirmed=False, min_height=1)
            self.assertEqual(len(pmts), 0)
            self.assertEqual(len(w), 1)
            self.assertIs(w[0].category, RuntimeWarning)
            pmts = self.wallet.incoming(unconfirmed=True, confirmed=False, max_height=99999999999999)
            self.assertEqual(len(pmts), 0)
            self.assertEqual(len(w), 2)
            self.assertIs(w[1].category, RuntimeWarning)
            pmts = self.wallet.incoming(payment_id='03f6649304ea4cb2')
            self.assertEqual(len(pmts), 0)
            pmts = self.wallet.incoming(unconfirmed=True, payment_id='03f6649304ea4cb2')
            self.assertEqual(len(pmts), 1)
            pmts = self.wallet.incoming(
                local_address='9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC')
            self.assertEqual(len(pmts), 4)
            pmts = self.wallet.incoming(
                unconfirmed=True,
                local_address='9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC')
            self.assertEqual(len(pmts), 5)
            pmts = self.wallet.incoming(
                local_address='9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                payment_id='03f6649304ea4cb2')
            self.assertEqual(len(pmts), 0)
            pmts = self.wallet.incoming(
                unconfirmed=True,
                local_address='9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                payment_id='03f6649304ea4cb2')
            self.assertEqual(len(pmts), 1)
            self.assertEqual(len(w), 2)

    def test_filter_mempool_absent(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            pmts = self.wallet.incoming()
            self.assertEqual(len(pmts), 7)
            for p in pmts:
                self.assertGreater(self.wallet.confirmations(p.transaction), 0)
            pmts = self.wallet.incoming(unconfirmed=False)
            self.assertEqual(len(pmts), 7)
            pmts = self.wallet.incoming(confirmed=True)
            self.assertEqual(len(pmts), 7)
            pmts = self.wallet.incoming(confirmed=True, unconfirmed=False)
            self.assertEqual(len(pmts), 7)
            self.assertEqual(len(w), 0)

    def test_filter_mempool_present(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            pmts = self.wallet.incoming(unconfirmed=True)
            self.assertEqual(len(pmts), 8)
            pmts = self.wallet.incoming(unconfirmed=True, confirmed=False)
            self.assertEqual(len(pmts), 1)
            self.assertEqual(
                pmts[0].transaction.hash,
                'd29264ad317e8fdb55ea04484c00420430c35be7b3fe6dd663f99aebf41a786c')
            self.assertEqual(self.wallet.confirmations(pmts[0]), 0)
            self.assertEqual(self.wallet.confirmations(pmts[0].transaction), 0)
            self.assertEqual(len(w), 0)

    def test_filter_mempool_filter_height(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            # mempool is always excluded and warnings are generated
            pmts = self.wallet.incoming(unconfirmed=True, confirmed=False, min_height=1)
            self.assertEqual(len(pmts), 0)
            self.assertEqual(len(w), 1)
            self.assertIs(w[0].category, RuntimeWarning)
            pmts = self.wallet.incoming(unconfirmed=True, confirmed=False, max_height=99999999999999)
            self.assertEqual(len(pmts), 0)
            self.assertEqual(len(w), 2)
            self.assertIs(w[1].category, RuntimeWarning)

    def test_filter_mempool_filter_payment_id(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            # mempool excluded
            pmts = self.wallet.incoming(payment_id='03f6649304ea4cb2')
            self.assertEqual(len(pmts), 0)
            # mempool included
            pmts = self.wallet.incoming(unconfirmed=True, payment_id='03f6649304ea4cb2')
            self.assertEqual(len(pmts), 1)
            self.assertEqual(
                pmts[0].transaction.hash,
                'd29264ad317e8fdb55ea04484c00420430c35be7b3fe6dd663f99aebf41a786c')
            self.assertEqual(len(w), 0)

    def test_filter_mempool_filter_address(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            # mempool excluded
            pmts = self.wallet.incoming(
                local_address='9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC')
            self.assertEqual(len(pmts), 4)
            # mempool included
            pmts = self.wallet.incoming(
                unconfirmed=True,
                local_address='9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC')
            self.assertEqual(len(pmts), 5)
            self.assertEqual(len(w), 0)

    def test_filter_mempool_filter_address_and_payment_id(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            # mempool excluded
            pmts = self.wallet.incoming(
                local_address='9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                payment_id='03f6649304ea4cb2')
            self.assertEqual(len(pmts), 0)
            # mempool included
            pmts = self.wallet.incoming(
                unconfirmed=True,
                local_address='9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                payment_id='03f6649304ea4cb2')
            self.assertEqual(len(pmts), 1)
            self.assertEqual(
                pmts[0].transaction.hash,
                'd29264ad317e8fdb55ea04484c00420430c35be7b3fe6dd663f99aebf41a786c')
            self.assertEqual(len(w), 0)

    def test_filter_mempool_filter_txid(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            # mempool excluded
            pmts = self.wallet.incoming(
                tx_id='d29264ad317e8fdb55ea04484c00420430c35be7b3fe6dd663f99aebf41a786c')
            self.assertEqual(len(pmts), 0)
            # mempool included
            pmts = self.wallet.incoming(
                unconfirmed=True,
                tx_id='d29264ad317e8fdb55ea04484c00420430c35be7b3fe6dd663f99aebf41a786c')
            self.assertEqual(len(pmts), 1)
            self.assertEqual(
                pmts[0].transaction.hash,
                'd29264ad317e8fdb55ea04484c00420430c35be7b3fe6dd663f99aebf41a786c')
            self.assertEqual(len(w), 0)

    def test_filter_excessive(self):
        self.assertRaises(ValueError, self.wallet.incoming, excessive_argument='foo')
