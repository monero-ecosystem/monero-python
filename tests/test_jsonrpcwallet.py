from datetime import datetime
from decimal import Decimal
import responses
try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock

from monero.wallet import Wallet
from monero.address import BaseAddress, Address, SubAddress
from monero.seed import Seed
from monero.transaction import IncomingPayment, OutgoingPayment, Transaction
from monero.backends.jsonrpc import JSONRPCWallet

from .base import JSONTestCase

class JSONRPCWalletTestCase(JSONTestCase):
    data_subdir = 'test_jsonrpcwallet'
    accounts_result = {'id': 0,
        'jsonrpc': '2.0',
        'result': {'subaddress_accounts': [{'account_index': 0,
                                         'balance': 224916129245183,
                                         'base_address': '9vgV48wWAPTWik5QSUSoGYicdvvsbSNHrT9Arsx1XBTz6VrWPSgfmnUKSPZDMyX4Ms8R9TkhB4uFqK9s5LUBbV6YQN2Q9ag',
                                         'label': 'Primary account',
                                         'unlocked_balance': 224916129245183},
                                        {'account_index': 1,
                                         'balance': 3981420960933,
                                         'base_address': 'BaCBwYSK9BGSuKxb2msXEj4mmpvZYJexYHfqx7kNPDrXDePVXSfoofxGquhXxpA4uxawcnVnouusMDgP74CACa7e9siimpj',
                                         'label': 'Untitled account',
                                         'unlocked_balance': 3981420960933},
                                        {'account_index': 2,
                                         'balance': 7256159239955,
                                         'base_address': 'BgCseuY3jFJAZS7kt9mrNg7fEG3bo5BV91CTyKbYu9GFiU6hUZhvdNWCTUdQNPNcA4PyFApsFr3EsQDEDfT3tQSY1mVZeP2',
                                         'label': 'Untitled account',
                                         'unlocked_balance': 7256159239955}],
                'total_balance': 236153709446071,
                'total_unlocked_balance': 236153709446071}}

    @patch('monero.backends.jsonrpc.wallet.requests.post')
    def test_seed(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = self.accounts_result
        self.wallet = Wallet(JSONRPCWallet())
        phrase = 'phrases petals speedy fuming ascend weird duplex identity ' \
           'yearbook masterful elope omission height empty react hope ' \
           'left iceberg leisure bobsled pyramid ammo sorry tiers ' \
           'pyramid'
        mock_post.return_value.json.return_value = {'id': 0,
            'jsonrpc': '2.0',
            'result': {'key': phrase}}
        seed = self.wallet.seed()
        self.assertIsInstance(seed, Seed)
        self.assertEqual(seed.phrase, phrase)

    @patch('monero.backends.jsonrpc.wallet.requests.post')
    def test_balance(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = self.accounts_result
        self.wallet = Wallet(JSONRPCWallet())
        mock_post.return_value.json.return_value = {'id': 0,
            'jsonrpc': '2.0',
            'result': {'balance': 224916129245183,
                    'per_subaddress': [{'address': '9vgV48wWAPTWik5QSUSoGYicdvvsbSNHrT9Arsx1XBTz6VrWPSgfmnUKSPZDMyX4Ms8R9TkhB4uFqK9s5LUBbV6YQN2Q9ag',
                                        'address_index': 0,
                                        'balance': 189656129245183,
                                        'label': 'Primary account',
                                        'num_unspent_outputs': 2,
                                        'unlocked_balance': 189656129245183},
                                       {'address': 'BfJ5W7dZGaYih6J63YvhiDSKpVUUZbVrEhLRCY6L6TdnEfzJmwP6aUJZQQnzLQ2NMTKMAC8hiJsoiNC7jbEUZ8tmBoJcnN1',
                                        'address_index': 5,
                                        'balance': 260000000000,
                                        'label': '(Untitled address)',
                                        'num_unspent_outputs': 1,
                                        'unlocked_balance': 260000000000},
                                       {'address': 'BbkS4mn6gcgUidn2znLa2J6eSBkbGjGX4doeDCKAzT2A3t1cjbquQGjhYgiMHiKTrY8ojk6Zjqi1ufvfuPwyKv4hNnMruro',
                                        'address_index': 7,
                                        'balance': 35000000000000,
                                        'label': '(Untitled address)',
                                        'num_unspent_outputs': 5,
                                        'unlocked_balance': 35000000000000}],
                    'unlocked_balance': 224916129245183}}
        locked = self.wallet.balance()
        unlocked = self.wallet.balance(unlocked=True)
        balances = self.wallet.balances()
        self.assertEqual(balances[0], locked)
        self.assertEqual(balances[1], unlocked)
        self.assertIsInstance(locked, Decimal)
        self.assertIsInstance(unlocked, Decimal)
        self.assertIsInstance(balances[0], Decimal)
        self.assertIsInstance(balances[1], Decimal)
        self.assertEqual(locked, Decimal('224.916129245183'))

    @responses.activate
    def test_address(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_address-00-get_accounts.json'),
            status=200)
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_address-10-getaddress.json'),
            status=200)
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_address-10-getaddress.json'),
            status=200)
        self.wallet = Wallet(JSONRPCWallet())
        waddr = self.wallet.address()
        a0addr = self.wallet.accounts[0].address()
        self.assertEqual(len(responses.calls), 3)
        self.assertEqual(waddr, a0addr)
        self.assertIsInstance(waddr, Address)
        self.assertEqual(
            waddr,
            '596ETuuDVZSNox73YLctrHaAv72fBboxy3atbEMnP3QtdnGFS9KWuHYGuy831SKWLUVCgrRfWLCxuCZ2fbVGh14X7mFrefy')
        self.assertEqual(waddr.label, 'Primary account')
        self.assertEqual(a0addr.label, 'Primary account')

    @responses.activate
    def test_account_creation(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_account_creation-00-get_accounts.json'),
            status=200)
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_account_creation-10-create_account.json'),
            status=200)
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_account_creation-20-getbalance.json'),
            status=200)
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_account_creation-30-get_accounts.json'),
            status=200)
        w = Wallet(JSONRPCWallet())
        self.assertEqual(1, len(w.accounts))
        w.new_account('account 1')
        self.assertEqual(2, len(w.accounts))
        self.assertEqual('account 1', w.accounts[1].label)
        self.assertEqual(0, w.accounts[1].balance())
        acc0, acc1 = w.accounts
        w.refresh()
        self.assertEqual(2, len(w.accounts))
        self.assertEqual('account 1', w.accounts[1].label)
        self.assertEqual([acc0, acc1], w.accounts)

    @responses.activate
    def test_new_address(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_new_address-00-get_accounts.json'),
            status=200)
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_new_address-10-new_address_account_0.json'),
            status=200)
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_new_address-20-new_address_account_1.json'),
            status=200)
        w = Wallet(JSONRPCWallet())
        subaddr, index = w.new_address()
        self.assertIsInstance(subaddr, SubAddress)
        self.assertIsInstance(index, int)
        subaddr, index = w.accounts[1].new_address()
        self.assertIsInstance(subaddr, SubAddress)
        self.assertIsInstance(index, int)

    @patch('monero.backends.jsonrpc.wallet.requests.post')
    def test_incoming_confirmed(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = self.accounts_result
        self.wallet = Wallet(JSONRPCWallet())
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'id': 0,
            'jsonrpc': '2.0',
            'result': {'in': [{'address': 'BhE3cQvB7VF2uuXcpXp28Wbadez6GgjypdRS1F1Mzqn8Advd6q8VfaX8ZoEDobjejrMfpHeNXoX8MjY8q8prW1PEALgr1En',
                            'amount': 3000000000000,
                            'double_spend_seen': False,
                            'fee': 8661870000,
                            'height': 1087601,
                            'note': '',
                            'payment_id': 'f75ad90e25d71a12',
                            'subaddr_index': {'major': 0, 'minor': 1},
                            'timestamp': 1517234267,
                            'txid': 'f34b495cec77822a70f829ec8a5a7f1e727128d62e6b1438e9cb7799654d610e',
                            'type': 'in',
                            'unlock_time': 0},
                           {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                            'amount': 10000000000000,
                            'double_spend_seen': False,
                            'fee': 962550000,
                            'height': 1087530,
                            'note': '',
                            'payment_id': 'f75ad90e25d71a12',
                            'subaddr_index': {'major': 0, 'minor': 0},
                            'timestamp': 1517228238,
                            'txid': '5c3ab739346e9d98d38dc7b8d36a4b7b1e4b6a16276946485a69797dbf887cd8',
                            'type': 'in',
                            'unlock_time': 0},
                           {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                            'amount': 4000000000000,
                            'double_spend_seen': False,
                            'fee': 962550000,
                            'height': 1087530,
                            'note': '',
                            'payment_id': 'f75ad90e25d71a12',
                            'subaddr_index': {'major': 0, 'minor': 0},
                            'timestamp': 1517228238,
                            'txid': '4ea70add5d0c7db33557551b15cd174972fcfc73bf0f6a6b47b7837564b708d3',
                            'type': 'in',
                            'unlock_time': 0},
                           {'address': 'BhE3cQvB7VF2uuXcpXp28Wbadez6GgjypdRS1F1Mzqn8Advd6q8VfaX8ZoEDobjejrMfpHeNXoX8MjY8q8prW1PEALgr1En',
                            'amount': 7000000000000,
                            'double_spend_seen': False,
                            'fee': 962430000,
                            'height': 1087601,
                            'note': '',
                            'payment_id': '0000000000000000',
                            'subaddr_index': {'major': 0, 'minor': 1},
                            'timestamp': 1517234267,
                            'txid': '5ef7ead6a041101ed326568fbb59c128403cba46076c3f353cd110d969dac808',
                            'type': 'in',
                            'unlock_time': 0},
                           {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                            'amount': 10000000000000,
                            'double_spend_seen': False,
                            'fee': 962550000,
                            'height': 1087530,
                            'note': '',
                            'payment_id': '0000000000000000',
                            'subaddr_index': {'major': 0, 'minor': 0},
                            'timestamp': 1517228238,
                            'txid': 'cc44568337a186c2e1ccc080b43b4ae9db26a07b7afd7edeed60ce2fc4a6477f',
                            'type': 'in',
                            'unlock_time': 0},
                           {'address': 'Bf6ngv7q2TBWup13nEm9AjZ36gLE6i4QCaZ7XScZUKDUeGbYEHmPRdegKGwLT8tBBK7P6L32RELNzCR6QzNFkmogDjvypyV',
                            'amount': 8000000000000,
                            'double_spend_seen': False,
                            'fee': 960990000,
                            'height': 1088394,
                            'note': '',
                            'payment_id': '0000000000000000',
                            'subaddr_index': {'major': 0, 'minor': 2},
                            'timestamp': 1517335388,
                            'txid': 'bc8b7ef53552c2d4bce713f513418894d0e2c8dcaf72e681e1d4d5a202f1eb62',
                            'type': 'in',
                            'unlock_time': 0},
                           {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                            'amount': 2120000000000,
                            'double_spend_seen': False,
                            'fee': 962550000,
                            'height': 1087530,
                            'note': '',
                            'payment_id': 'cb248105ea6a9189',
                            'subaddr_index': {'major': 0, 'minor': 0},
                            'timestamp': 1517228238,
                            'txid': 'e9a71c01875bec20812f71d155bfabf42024fde3ec82475562b817dcc8cbf8dc',
                            'type': 'in',
                            'unlock_time': 0},
                           {'address': 'Bf6ngv7q2TBWup13nEm9AjZ36gLE6i4QCaZ7XScZUKDUeGbYEHmPRdegKGwLT8tBBK7P6L32RELNzCR6QzNFkmogDjvypyV',
                            'amount': 1000000000000,
                            'double_spend_seen': False,
                            'fee': 3528910000,
                            'height': 1087606,
                            'note': '',
                            'payment_id': '0166d8da6c0045c51273dd65d6f63734beb8a84e0545a185b2cfd053fced9f5d',
                            'subaddr_index': {'major': 0, 'minor': 2},
                            'timestamp': 1517234425,
                            'txid': 'a0b876ebcf7c1d499712d84cedec836f9d50b608bb22d6cb49fd2feae3ffed14',
                            'type': 'in',
                            'unlock_time': 0},
                           {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                            'amount': 3140000000000,
                            'double_spend_seen': False,
                            'fee': 961950000,
                            'height': 1087858,
                            'note': '',
                            'payment_id': '03f6649304ea4cb2',
                            'subaddr_index': {'major': 0, 'minor': 0},
                            'timestamp': 1517256811,
                            'txid': 'd29264ad317e8fdb55ea04484c00420430c35be7b3fe6dd663f99aebf41a786c',
                            'type': 'in',
                            'unlock_time': 0}]}}
        pay_in = self.wallet.incoming()
        self.assertEqual(len(list(pay_in)), 9)
        for pmt in pay_in:
            self.assertIsInstance(pmt, IncomingPayment)
            self.assertIsInstance(pmt.local_address, BaseAddress)
            self.assertIsInstance(pmt.amount, Decimal)
            self.assertIsInstance(pmt.transaction, Transaction)
            self.assertIsInstance(pmt.transaction.fee, Decimal)
            self.assertIsInstance(pmt.transaction.height, int)

    @patch('monero.backends.jsonrpc.wallet.requests.post')
    def test_incoming_confirmed_and_unconfirmed(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = self.accounts_result
        self.wallet = Wallet(JSONRPCWallet())
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'id': 0,
            'jsonrpc': '2.0',
            'result': {'in': [{'address': 'BhE3cQvB7VF2uuXcpXp28Wbadez6GgjypdRS1F1Mzqn8Advd6q8VfaX8ZoEDobjejrMfpHeNXoX8MjY8q8prW1PEALgr1En',
                            'amount': 3000000000000,
                            'double_spend_seen': False,
                            'fee': 8661870000,
                            'height': 1087601,
                            'note': '',
                            'payment_id': 'f75ad90e25d71a12',
                            'subaddr_index': {'major': 0, 'minor': 1},
                            'timestamp': 1517234267,
                            'txid': 'f34b495cec77822a70f829ec8a5a7f1e727128d62e6b1438e9cb7799654d610e',
                            'type': 'in',
                            'unlock_time': 0},
                           {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                            'amount': 10000000000000,
                            'double_spend_seen': False,
                            'fee': 962550000,
                            'height': 1087530,
                            'note': '',
                            'payment_id': 'f75ad90e25d71a12',
                            'subaddr_index': {'major': 0, 'minor': 0},
                            'timestamp': 1517228238,
                            'txid': '5c3ab739346e9d98d38dc7b8d36a4b7b1e4b6a16276946485a69797dbf887cd8',
                            'type': 'in',
                            'unlock_time': 0},
                           {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                            'amount': 4000000000000,
                            'double_spend_seen': False,
                            'fee': 962550000,
                            'height': 1087530,
                            'note': '',
                            'payment_id': 'f75ad90e25d71a12',
                            'subaddr_index': {'major': 0, 'minor': 0},
                            'timestamp': 1517228238,
                            'txid': '4ea70add5d0c7db33557551b15cd174972fcfc73bf0f6a6b47b7837564b708d3',
                            'type': 'in',
                            'unlock_time': 0},
                           {'address': 'BhE3cQvB7VF2uuXcpXp28Wbadez6GgjypdRS1F1Mzqn8Advd6q8VfaX8ZoEDobjejrMfpHeNXoX8MjY8q8prW1PEALgr1En',
                            'amount': 7000000000000,
                            'double_spend_seen': False,
                            'fee': 962430000,
                            'height': 1087601,
                            'note': '',
                            'payment_id': '0000000000000000',
                            'subaddr_index': {'major': 0, 'minor': 1},
                            'timestamp': 1517234267,
                            'txid': '5ef7ead6a041101ed326568fbb59c128403cba46076c3f353cd110d969dac808',
                            'type': 'in',
                            'unlock_time': 0},
                           {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                            'amount': 10000000000000,
                            'double_spend_seen': False,
                            'fee': 962550000,
                            'height': 1087530,
                            'note': '',
                            'payment_id': '0000000000000000',
                            'subaddr_index': {'major': 0, 'minor': 0},
                            'timestamp': 1517228238,
                            'txid': 'cc44568337a186c2e1ccc080b43b4ae9db26a07b7afd7edeed60ce2fc4a6477f',
                            'type': 'in',
                            'unlock_time': 0},
                           {'address': 'Bf6ngv7q2TBWup13nEm9AjZ36gLE6i4QCaZ7XScZUKDUeGbYEHmPRdegKGwLT8tBBK7P6L32RELNzCR6QzNFkmogDjvypyV',
                            'amount': 8000000000000,
                            'double_spend_seen': False,
                            'fee': 960990000,
                            'height': 1088394,
                            'note': '',
                            'payment_id': '0000000000000000',
                            'subaddr_index': {'major': 0, 'minor': 2},
                            'timestamp': 1517335388,
                            'txid': 'bc8b7ef53552c2d4bce713f513418894d0e2c8dcaf72e681e1d4d5a202f1eb62',
                            'type': 'in',
                            'unlock_time': 0},
                           {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                            'amount': 2120000000000,
                            'double_spend_seen': False,
                            'fee': 962550000,
                            'height': 1087530,
                            'note': '',
                            'payment_id': 'cb248105ea6a9189',
                            'subaddr_index': {'major': 0, 'minor': 0},
                            'timestamp': 1517228238,
                            'txid': 'e9a71c01875bec20812f71d155bfabf42024fde3ec82475562b817dcc8cbf8dc',
                            'type': 'in',
                            'unlock_time': 0},
                           {'address': 'Bf6ngv7q2TBWup13nEm9AjZ36gLE6i4QCaZ7XScZUKDUeGbYEHmPRdegKGwLT8tBBK7P6L32RELNzCR6QzNFkmogDjvypyV',
                            'amount': 1000000000000,
                            'double_spend_seen': False,
                            'fee': 3528910000,
                            'height': 1087606,
                            'note': '',
                            'payment_id': '0166d8da6c0045c51273dd65d6f63734beb8a84e0545a185b2cfd053fced9f5d',
                            'subaddr_index': {'major': 0, 'minor': 2},
                            'timestamp': 1517234425,
                            'txid': 'a0b876ebcf7c1d499712d84cedec836f9d50b608bb22d6cb49fd2feae3ffed14',
                            'type': 'in',
                            'unlock_time': 0},
                           {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                            'amount': 3140000000000,
                            'double_spend_seen': False,
                            'fee': 961950000,
                            'height': 1087858,
                            'note': '',
                            'payment_id': '03f6649304ea4cb2',
                            'subaddr_index': {'major': 0, 'minor': 0},
                            'timestamp': 1517256811,
                            'txid': 'd29264ad317e8fdb55ea04484c00420430c35be7b3fe6dd663f99aebf41a786c',
                            'type': 'in',
                            'unlock_time': 0}],
                    'pool': [{'address': 'Bf6ngv7q2TBWup13nEm9AjZ36gLE6i4QCaZ7XScZUKDUeGbYEHmPRdegKGwLT8tBBK7P6L32RELNzCR6QzNFkmogDjvypyV',
                              'amount': 1000000000000,
                              'double_spend_seen': False,
                              'fee': 960960000,
                              'height': 0,
                              'note': '',
                              'payment_id': '0000000000000000',
                              'subaddr_index': {'major': 0, 'minor': 2},
                              'timestamp': 1517336242,
                              'txid': 'f349c6badfa7f6e46666db3996b569a05c6ac4e85417551ec208d96f8a37294a',
                              'type': 'pool',
                              'unlock_time': 0},
                             {'address': 'BhE3cQvB7VF2uuXcpXp28Wbadez6GgjypdRS1F1Mzqn8Advd6q8VfaX8ZoEDobjejrMfpHeNXoX8MjY8q8prW1PEALgr1En',
                              'amount': 1000000000000,
                              'double_spend_seen': False,
                              'fee': 960960000,
                              'height': 0,
                              'note': '',
                              'payment_id': '1f2510a597bd634bbd130cf21e63b4ad01f4565faf0d3eb21589f496bf28f7f2',
                              'subaddr_index': {'major': 0, 'minor': 1},
                              'timestamp': 1517336242,
                              'txid': '41304bbb514d1abdfdb0704bf70f8d2ec4e753c57aa34b6d0525631d79113b87',
                              'type': 'pool',
                              'unlock_time': 0}]}}
        pay_in = self.wallet.incoming(unconfirmed=True)
        self.assertEqual(len(list(pay_in)), 11)
        for pmt in pay_in:
            self.assertIsInstance(pmt, IncomingPayment)
            self.assertIsInstance(pmt.local_address, BaseAddress)
            self.assertIsInstance(pmt.amount, Decimal)
            self.assertIsInstance(pmt.transaction, Transaction)
            self.assertIsInstance(pmt.transaction.fee, Decimal)
            self.assertIsInstance(pmt.transaction.height, (int, type(None)))


    @patch('monero.backends.jsonrpc.wallet.requests.post')
    def test_incoming_unconfirmed(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = self.accounts_result
        self.wallet = Wallet(JSONRPCWallet())
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'id': 0,
            'jsonrpc': '2.0',
            'result': {'pool': [{'address': 'Bf6ngv7q2TBWup13nEm9AjZ36gLE6i4QCaZ7XScZUKDUeGbYEHmPRdegKGwLT8tBBK7P6L32RELNzCR6QzNFkmogDjvypyV',
                              'amount': 1000000000000,
                              'double_spend_seen': False,
                              'fee': 960960000,
                              'height': 0,
                              'note': '',
                              'payment_id': '0000000000000000',
                              'subaddr_index': {'major': 0, 'minor': 2},
                              'timestamp': 1517336242,
                              'txid': 'f349c6badfa7f6e46666db3996b569a05c6ac4e85417551ec208d96f8a37294a',
                              'type': 'pool',
                              'unlock_time': 0},
                             {'address': 'BhE3cQvB7VF2uuXcpXp28Wbadez6GgjypdRS1F1Mzqn8Advd6q8VfaX8ZoEDobjejrMfpHeNXoX8MjY8q8prW1PEALgr1En',
                              'amount': 1000000000000,
                              'double_spend_seen': False,
                              'fee': 960960000,
                              'height': 0,
                              'note': '',
                              'payment_id': '1f2510a597bd634bbd130cf21e63b4ad01f4565faf0d3eb21589f496bf28f7f2',
                              'subaddr_index': {'major': 0, 'minor': 1},
                              'timestamp': 1517336242,
                              'txid': '41304bbb514d1abdfdb0704bf70f8d2ec4e753c57aa34b6d0525631d79113b87',
                              'type': 'pool',
                              'unlock_time': 0}]}}
        pay_in = self.wallet.incoming(unconfirmed=True, confirmed=False)
        self.assertEqual(len(list(pay_in)), 2)
        for pmt in pay_in:
            self.assertIsInstance(pmt, IncomingPayment)
            self.assertIsInstance(pmt.local_address, BaseAddress)
            self.assertIsInstance(pmt.amount, Decimal)
            self.assertIsInstance(pmt.transaction, Transaction)
            self.assertIsInstance(pmt.transaction.fee, Decimal)
            self.assertIs(pmt.transaction.height, None)

    @responses.activate
    def test_incoming_by_tx_id(self):
        # 3 payments in one transaction
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_incoming_by_tx_id-00-get_accounts.json'),
            status=200)
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_incoming_by_tx_id-7ab84-get_transfer_by_txid.json'),
            status=200)
        self.wallet = Wallet(JSONRPCWallet())
        pmts = self.wallet.incoming(tx_id='7ab84fe2fb34467c590cde2f7d6ba7de5928a2db6c84c6ccfff8962eca0ad99c')
        self.assertEqual(len(pmts), 3)
        self.assertEqual(pmts[0].amount, Decimal(1))
        self.assertEqual(pmts[1].amount, Decimal(1))
        self.assertEqual(pmts[2].amount, Decimal(2))

    @responses.activate
    def test_incoming_by_tx_id__with_min_height(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_incoming_by_tx_id-00-get_accounts.json'),
            status=200)
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_incoming_by_tx_id-7ab84-get_transfer_by_txid.json'),
            status=200)
        self.wallet = Wallet(JSONRPCWallet())
        pmts = self.wallet.incoming(min_height=409223,
            tx_id='7ab84fe2fb34467c590cde2f7d6ba7de5928a2db6c84c6ccfff8962eca0ad99c')
        self.assertEqual(len(pmts), 3)
        self.assertEqual(pmts[0].amount, Decimal(1))
        self.assertEqual(pmts[1].amount, Decimal(1))
        self.assertEqual(pmts[2].amount, Decimal(2))

    @responses.activate
    def test_incoming_by_tx_id__with_max_height(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_incoming_by_tx_id-00-get_accounts.json'),
            status=200)
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_incoming_by_tx_id-7ab84-get_transfer_by_txid.json'),
            status=200)
        self.wallet = Wallet(JSONRPCWallet())
        pmts = self.wallet.incoming(max_height=409223,
            tx_id='7ab84fe2fb34467c590cde2f7d6ba7de5928a2db6c84c6ccfff8962eca0ad99c')
        self.assertEqual(len(pmts), 0)

    @responses.activate
    def test_incoming_by_tx_id__not_found(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_incoming_by_tx_id-00-get_accounts.json'),
            status=200)
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_incoming_by_tx_id-e0b15-get_transfer_by_txid.json'),
            status=200)
        self.wallet = Wallet(JSONRPCWallet())
        pmts = self.wallet.incoming(tx_id='e0b15ac819c94ed9ba81edb955a98c696f3216335960ccf90018d76a8dcb0e7e')
        self.assertEqual(len(pmts), 0)

    @responses.activate
    def test_incoming_by_tx_id__multiple_ids(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_incoming_by_tx_id-00-get_accounts.json'),
            status=200)
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_incoming_by_tx_id-7ab84-get_transfer_by_txid.json'),
            status=200)
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_incoming_by_tx_id-55e75-get_transfer_by_txid.json'),
            status=200)
        self.wallet = Wallet(JSONRPCWallet())
        pmts = self.wallet.incoming(tx_id=[
            '7ab84fe2fb34467c590cde2f7d6ba7de5928a2db6c84c6ccfff8962eca0ad99c',
            '55e758d7d259bb316551ddcdd4808711de99c30b8b5c52de3e95e563fd92d156'])
        self.assertEqual(len(pmts), 4)
        self.assertEqual(pmts[0].amount, Decimal(4))
        self.assertEqual(pmts[1].amount, Decimal(1))
        self.assertEqual(pmts[2].amount, Decimal(1))
        self.assertEqual(pmts[3].amount, Decimal(2))

    @responses.activate
    def test_incoming_by_tx_id__mempool(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_incoming_by_tx_id-00-get_accounts.json'),
            status=200)
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_incoming_by_tx_id-31b52-get_transfer_by_txid.json'),
            status=200)
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_incoming_by_tx_id-31b52-get_transfer_by_txid.json'),
            status=200)
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_incoming_by_tx_id-31b52-get_transfer_by_txid.json'),
            status=200)
        self.wallet = Wallet(JSONRPCWallet())
        pmts = self.wallet.incoming(
            tx_id='31b527fb9c27e759d56892fef93136df1057186c5cf4e3c93c5298b70160f562')
        self.assertEqual(len(pmts), 0)
        pmts = self.wallet.incoming(
            tx_id='31b527fb9c27e759d56892fef93136df1057186c5cf4e3c93c5298b70160f562',
            unconfirmed=True)
        self.assertEqual(len(pmts), 1)
        pmts = self.wallet.incoming(
            tx_id='31b527fb9c27e759d56892fef93136df1057186c5cf4e3c93c5298b70160f562',
            confirmed=False)
        self.assertEqual(len(pmts), 0)

    @responses.activate
    def test_outgoing_by_tx_id(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_outgoing_by_tx_id-00-get_accounts.json'),
            status=200)
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_outgoing_by_tx_id-362c3-get_transfer_by_txid.json'),
            status=200)
        self.wallet = Wallet(JSONRPCWallet())
        acc = self.wallet.accounts[1]
        pmts = acc.outgoing(tx_id='362c3a4e601d5847b3882c3debfd28a0ee31654e433c38498539677199c304c2')
        self.assertEqual(len(pmts), 1)
        self.assertEqual(pmts[0].amount, Decimal('0.52'))

    @responses.activate
    def test_outgoing_by_tx_id__mempool(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_outgoing_by_tx_id-00-get_accounts.json'),
            status=200)
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_outgoing_by_tx_id-afaf0-get_transfer_by_txid.json'),
            status=200)
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_outgoing_by_tx_id-afaf0-get_transfer_by_txid.json'),
            status=200)
        self.wallet = Wallet(JSONRPCWallet())
        acc = self.wallet.accounts[1]
        pmts = acc.outgoing(tx_id='afaf04e5e40c6b60fc7cc928a88843fc96031ec2b567c310ee61abf3d00020da')
        self.assertEqual(len(pmts), 0)
        pmts = acc.outgoing(
            tx_id='afaf04e5e40c6b60fc7cc928a88843fc96031ec2b567c310ee61abf3d00020da',
            unconfirmed=True)
        self.assertEqual(len(pmts), 1)

    @responses.activate
    def test_outgoing_by_tx_id__multiple_ids(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_outgoing_by_tx_id-00-get_accounts.json'),
            status=200)
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_outgoing_by_tx_id-362c3-get_transfer_by_txid.json'),
            status=200)
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_outgoing_by_tx_id-eda89-get_transfer_by_txid.json'),
            status=200)
        self.wallet = Wallet(JSONRPCWallet())
        acc = self.wallet.accounts[1]
        pmts = acc.outgoing(tx_id=[
            '362c3a4e601d5847b3882c3debfd28a0ee31654e433c38498539677199c304c2',
            'eda891adf76993f9066abd56a8a5aa5c51a7618298cab59ec37739f1c960596d'])
        self.assertEqual(len(pmts), 2)
        self.assertEqual(pmts[0].amount, Decimal('0.52'))
        self.assertEqual(pmts[1].amount, Decimal('0.0212'))

    @patch('monero.backends.jsonrpc.wallet.requests.post')
    def test_incoming_by_payment_ids(self, mock_post):
        # These queries will use get_bulk_payments RPC method instead of get_transfers
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = self.accounts_result
        self.wallet = Wallet(JSONRPCWallet())
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'id': 0,
            'jsonrpc': '2.0',
            'result': {'payments': [{'address': 'BhE3cQvB7VF2uuXcpXp28Wbadez6GgjypdRS1F1Mzqn8Advd6q8VfaX8ZoEDobjejrMfpHeNXoX8MjY8q8prW1PEALgr1En',
                                  'amount': 3000000000000,
                                  'block_height': 1087601,
                                  'payment_id': 'f75ad90e25d71a12',
                                  'subaddr_index': {'major': 0, 'minor': 1},
                                  'tx_hash': 'f34b495cec77822a70f829ec8a5a7f1e727128d62e6b1438e9cb7799654d610e',
                                  'unlock_time': 0},
                                 {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                                  'amount': 10000000000000,
                                  'block_height': 1087530,
                                  'payment_id': 'f75ad90e25d71a12',
                                  'subaddr_index': {'major': 0, 'minor': 0},
                                  'tx_hash': '5c3ab739346e9d98d38dc7b8d36a4b7b1e4b6a16276946485a69797dbf887cd8',
                                  'unlock_time': 0},
                                 {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                                  'amount': 4000000000000,
                                  'block_height': 1087530,
                                  'payment_id': 'f75ad90e25d71a12',
                                  'subaddr_index': {'major': 0, 'minor': 0},
                                  'tx_hash': '4ea70add5d0c7db33557551b15cd174972fcfc73bf0f6a6b47b7837564b708d3',
                                  'unlock_time': 0}]}}
        pay_in = self.wallet.incoming(payment_id='f75ad90e25d71a12')
        self.assertEqual(len(list(pay_in)), 3)
        for pmt in pay_in:
            self.assertIsInstance(pmt, IncomingPayment)
            self.assertIsInstance(pmt.local_address, BaseAddress)
            self.assertIsInstance(pmt.amount, Decimal)
            self.assertIsInstance(pmt.transaction, Transaction)
# Fee is not returned by this RPC method!
#            self.assertIsInstance(pmt.transaction.fee, Decimal)
            self.assertIsInstance(pmt.transaction.height, int)
            self.assertEqual(pmt.payment_id, 'f75ad90e25d71a12')

        mock_post.return_value.json.return_value = {
            'id': 0,
            'jsonrpc': '2.0',
            'result': {'payments': [{'address': 'BhE3cQvB7VF2uuXcpXp28Wbadez6GgjypdRS1F1Mzqn8Advd6q8VfaX8ZoEDobjejrMfpHeNXoX8MjY8q8prW1PEALgr1En',
                                  'amount': 3000000000000,
                                  'block_height': 1087601,
                                  'payment_id': 'f75ad90e25d71a12',
                                  'subaddr_index': {'major': 0, 'minor': 1},
                                  'tx_hash': 'f34b495cec77822a70f829ec8a5a7f1e727128d62e6b1438e9cb7799654d610e',
                                  'unlock_time': 0},
                                 {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                                  'amount': 10000000000000,
                                  'block_height': 1087530,
                                  'payment_id': 'f75ad90e25d71a12',
                                  'subaddr_index': {'major': 0, 'minor': 0},
                                  'tx_hash': '5c3ab739346e9d98d38dc7b8d36a4b7b1e4b6a16276946485a69797dbf887cd8',
                                  'unlock_time': 0},
                                 {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                                  'amount': 4000000000000,
                                  'block_height': 1087530,
                                  'payment_id': 'f75ad90e25d71a12',
                                  'subaddr_index': {'major': 0, 'minor': 0},
                                  'tx_hash': '4ea70add5d0c7db33557551b15cd174972fcfc73bf0f6a6b47b7837564b708d3',
                                  'unlock_time': 0},
                                 {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                                  'amount': 2120000000000,
                                  'block_height': 1087530,
                                  'payment_id': 'cb248105ea6a9189',
                                  'subaddr_index': {'major': 0, 'minor': 0},
                                  'tx_hash': 'e9a71c01875bec20812f71d155bfabf42024fde3ec82475562b817dcc8cbf8dc',
                                  'unlock_time': 0}]}}
        ids = ('f75ad90e25d71a12', 'cb248105ea6a9189')
        pay_in = self.wallet.incoming(payment_id=ids)
        self.assertEqual(len(list(pay_in)), 4)
        for pmt in pay_in:
            self.assertIsInstance(pmt, IncomingPayment)
            self.assertIsInstance(pmt.local_address, BaseAddress)
            self.assertIsInstance(pmt.amount, Decimal)
            self.assertIsInstance(pmt.transaction, Transaction)
# Fee is not returned by this RPC method!
#            self.assertIsInstance(pmt.transaction.fee, Decimal)
            self.assertIsInstance(pmt.transaction.height, int)
            self.assertIn(pmt.payment_id, ids)

    @patch('monero.backends.jsonrpc.wallet.requests.post')
    def test_outgoing(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = self.accounts_result
        self.wallet = Wallet(JSONRPCWallet())
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'id': 0,
            'jsonrpc': '2.0',
            'result': {'out': [{'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                             'amount': 70000000000,
                             'destinations': [{'address': 'BaB4Xsi9fBPDutsdNWTzNN5qgmTE2WUwnMGm5ukkb9TXUJHQLyZhQikekhHX8zhmRn3VTJeniuMXJHuCHfKyPk1XQDfk9bw',
                                               'amount': 70000000000}],
                             'double_spend_seen': False,
                             'fee': 960900000,
                             'height': 1088441,
                             'note': '',
                             'payment_id': '0000000000000000',
                             'subaddr_index': {'major': 0, 'minor': 0},
                             'timestamp': 1517342302,
                             'txid': 'e32cccd7522e760b1c8a571fd08c75e7a1d822874380edc9656f58284eeb2fe5',
                             'type': 'out',
                             'unlock_time': 0},
                            {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                             'amount': 21000000000000,
                             'destinations': [{'address': 'BczAN2ZV5MENFAqSBdJJpzW9CMqURR9XTCjihzEGHzCV58YFRZHYuhk2huFsBrbPtDN2dGWHgiY1CRTUAPeDJg1ZFCzCssT',
                                               'amount': 21000000000000}],
                             'double_spend_seen': False,
                             'fee': 960990000,
                             'height': 1088394,
                             'note': '',
                             'payment_id': '0000000000000000',
                             'subaddr_index': {'major': 0, 'minor': 0},
                             'timestamp': 1517335388,
                             'txid': 'edc7c28e7b07486be48dac0a178f25a3505114267ddaf3e62ab00d9a6e996044',
                             'type': 'out',
                             'unlock_time': 0},
                            {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                             'amount': 210000000000,
                             'destinations': [{'address': 'Bg2iRGq5f6iXf3gXYps9AJFWuhhtL74o8GE4JrBPFN3ViuyuTDcPSVqckGeNSU1brSFbdYJ5jjVerJ8Cb4aGJwJTSvzzHwf',
                                               'amount': 210000000000}],
                             'double_spend_seen': False,
                             'fee': 960810000,
                             'height': 1088479,
                             'note': '',
                             'payment_id': '0000000000000000',
                             'subaddr_index': {'major': 0, 'minor': 0},
                             'timestamp': 1517344830,
                             'txid': 'd09666238129a1e2a71a9b7c6b30564a95baef926556bb658785cb9c38d9b25a',
                             'type': 'out',
                             'unlock_time': 0},
                            {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                             'amount': 1111111111000,
                             'double_spend_seen': False,
                             'fee': 960750000,
                             'height': 1088516,
                             'note': '',
                             'payment_id': '0000000000000000',
                             'subaddr_index': {'major': 0, 'minor': 0},
                             'timestamp': 1517347450,
                             'txid': '551721b5358b02565d6a9862867e3806b9a2e0d5aa5158d4d30940251d27bbdd',
                             'type': 'out',
                             'unlock_time': 0},
                            {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                             'amount': 70000000000,
                             'destinations': [{'address': 'BaB4Xsi9fBPDutsdNWTzNN5qgmTE2WUwnMGm5ukkb9TXUJHQLyZhQikekhHX8zhmRn3VTJeniuMXJHuCHfKyPk1XQDfk9bw',
                                               'amount': 70000000000}],
                             'double_spend_seen': False,
                             'fee': 960900000,
                             'height': 1088438,
                             'note': '',
                             'payment_id': '0000000000000000',
                             'subaddr_index': {'major': 0, 'minor': 0},
                             'timestamp': 1517341824,
                             'txid': '21e7eb651e8a2bc7661975e965ac6b30a6f4033c6a02e96320e41139ad3e307c',
                             'type': 'out',
                             'unlock_time': 0},
                            {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                             'amount': 3333333333330,
                             'double_spend_seen': False,
                             'fee': 960750000,
                             'height': 1088521,
                             'note': '',
                             'payment_id': '0000000000000000',
                             'subaddr_index': {'major': 0, 'minor': 0},
                             'timestamp': 1517347785,
                             'txid': '5d15fef66fe8de715bcbf2c181f97b9932f9f843aef4724f3026fa3cd1082c68',
                             'type': 'out',
                             'unlock_time': 0},
                            {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                             'amount': 1000000000000,
                             'destinations': [{'address': 'Bg2iRGq5f6iXf3gXYps9AJFWuhhtL74o8GE4JrBPFN3ViuyuTDcPSVqckGeNSU1brSFbdYJ5jjVerJ8Cb4aGJwJTSvzzHwf',
                                               'amount': 1000000000000}],
                             'double_spend_seen': False,
                             'fee': 960990000,
                             'height': 1088394,
                             'note': '',
                             'payment_id': '6cc9350927868849',
                             'subaddr_index': {'major': 0, 'minor': 0},
                             'timestamp': 1517335388,
                             'txid': '5e8f392a42899294e6b679ddac13cfe1dfe7f034b1e347424218af06c3dfdc85',
                             'type': 'out',
                             'unlock_time': 0},
                            {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                             'amount': 2450000000000,
                             'destinations': [{'address': '9vgV48wWAPTWik5QSUSoGYicdvvsbSNHrT9Arsx1XBTz6VrWPSgfmnUKSPZDMyX4Ms8R9TkhB4uFqK9s5LUBbV6YQN2Q9ag',
                                               'amount': 2450000000000}],
                             'double_spend_seen': False,
                             'fee': 961350000,
                             'height': 1088184,
                             'note': '',
                             'payment_id': '6cc9350927868849',
                             'subaddr_index': {'major': 0, 'minor': 0},
                             'timestamp': 1517299877,
                             'txid': '2b41226d45edb875634694fccd95f3c174daa5062763eee619ed4475a7b9207a',
                             'type': 'out',
                             'unlock_time': 0},
                            {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                             'amount': 1000000000000,
                             'destinations': [{'address': 'BZHa2Fm9yn3by1CWTBruWxEuZ5TqyMLiBQAFrHM6aniLfjTBWkA4E4kif63YS7wmbFW5UBwrFSKNoiSQ2mE8SS5S6uzgvoc',
                                               'amount': 1000000000000}],
                             'double_spend_seen': False,
                             'fee': 961350000,
                             'height': 1088184,
                             'note': '',
                             'payment_id': '0000000000000000',
                             'subaddr_index': {'major': 0, 'minor': 0},
                             'timestamp': 1517299877,
                             'txid': '40de45db57eb87eb8395baf5c1dc705602938317d043f463e68ed85b7108f9f3',
                             'type': 'out',
                             'unlock_time': 0},
                            {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                             'amount': 123000000000,
                             'destinations': [{'address': 'BYeK7sZ9DhkASZpMrhGw6yFynaDy5PJ8T2CeogvGTFfT2kMQdTNJFQpDXpoHNBPTyNfrxERdRje9bBJh7LTqN4oDUVVvzAe',
                                               'amount': 123000000000}],
                             'double_spend_seen': False,
                             'fee': 3843000000,
                             'height': 1088523,
                             'note': '',
                             'payment_id': '0000000000000000',
                             'subaddr_index': {'major': 0, 'minor': 0},
                             'timestamp': 1517347908,
                             'txid': 'e291fe40c6102a6193c82ac33227c08e5b30a863dba1bc63e13043a25abbb97a',
                             'type': 'out',
                             'unlock_time': 0},
                            {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                             'amount': 2220000000000,
                             'double_spend_seen': False,
                             'fee': 3843840000,
                             'height': 1088411,
                             'note': '',
                             'payment_id': '0000000000000000',
                             'subaddr_index': {'major': 0, 'minor': 0},
                             'timestamp': 1517339862,
                             'txid': 'a8829744952facbfdaab21ca193298edb1fa16f688cd5dbcdff3ed3968155f28',
                             'type': 'out',
                             'unlock_time': 0}]}}
        pay_out = self.wallet.outgoing()
        self.assertEqual(len(list(pay_out)), 11)
        for pmt in pay_out:
            self.assertIsInstance(pmt, OutgoingPayment)
            self.assertIsInstance(pmt.local_address, Address)
            self.assertIsInstance(pmt.amount, Decimal)
            self.assertIsInstance(pmt.timestamp, datetime)
            self.assertIsInstance(pmt.transaction, Transaction)
            self.assertIsInstance(pmt.transaction.fee, Decimal)
            self.assertIsInstance(pmt.transaction.height, int)

    @patch('monero.backends.jsonrpc.wallet.requests.post')
    def test_outgoing_confirmed_and_unconfirmed(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = self.accounts_result
        self.wallet = Wallet(JSONRPCWallet())
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'id': 0,
            'jsonrpc': '2.0',
            'result': {'out': [{'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                             'amount': 70000000000,
                             'destinations': [{'address': 'BaB4Xsi9fBPDutsdNWTzNN5qgmTE2WUwnMGm5ukkb9TXUJHQLyZhQikekhHX8zhmRn3VTJeniuMXJHuCHfKyPk1XQDfk9bw',
                                               'amount': 70000000000}],
                             'double_spend_seen': False,
                             'fee': 960900000,
                             'height': 1088441,
                             'note': '',
                             'payment_id': '0000000000000000',
                             'subaddr_index': {'major': 0, 'minor': 0},
                             'timestamp': 1517342302,
                             'txid': 'e32cccd7522e760b1c8a571fd08c75e7a1d822874380edc9656f58284eeb2fe5',
                             'type': 'out',
                             'unlock_time': 0},
                            {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                             'amount': 21000000000000,
                             'destinations': [{'address': 'BczAN2ZV5MENFAqSBdJJpzW9CMqURR9XTCjihzEGHzCV58YFRZHYuhk2huFsBrbPtDN2dGWHgiY1CRTUAPeDJg1ZFCzCssT',
                                               'amount': 21000000000000}],
                             'double_spend_seen': False,
                             'fee': 960990000,
                             'height': 1088394,
                             'note': '',
                             'payment_id': '0000000000000000',
                             'subaddr_index': {'major': 0, 'minor': 0},
                             'timestamp': 1517335388,
                             'txid': 'edc7c28e7b07486be48dac0a178f25a3505114267ddaf3e62ab00d9a6e996044',
                             'type': 'out',
                             'unlock_time': 0},
                            {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                             'amount': 210000000000,
                             'destinations': [{'address': 'Bg2iRGq5f6iXf3gXYps9AJFWuhhtL74o8GE4JrBPFN3ViuyuTDcPSVqckGeNSU1brSFbdYJ5jjVerJ8Cb4aGJwJTSvzzHwf',
                                               'amount': 210000000000}],
                             'double_spend_seen': False,
                             'fee': 960810000,
                             'height': 1088479,
                             'note': '',
                             'payment_id': '0000000000000000',
                             'subaddr_index': {'major': 0, 'minor': 0},
                             'timestamp': 1517344830,
                             'txid': 'd09666238129a1e2a71a9b7c6b30564a95baef926556bb658785cb9c38d9b25a',
                             'type': 'out',
                             'unlock_time': 0},
                            {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                             'amount': 1111111111000,
                             'double_spend_seen': False,
                             'fee': 960750000,
                             'height': 1088516,
                             'note': '',
                             'payment_id': '0000000000000000',
                             'subaddr_index': {'major': 0, 'minor': 0},
                             'timestamp': 1517347450,
                             'txid': '551721b5358b02565d6a9862867e3806b9a2e0d5aa5158d4d30940251d27bbdd',
                             'type': 'out',
                             'unlock_time': 0},
                            {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                             'amount': 70000000000,
                             'destinations': [{'address': 'BaB4Xsi9fBPDutsdNWTzNN5qgmTE2WUwnMGm5ukkb9TXUJHQLyZhQikekhHX8zhmRn3VTJeniuMXJHuCHfKyPk1XQDfk9bw',
                                               'amount': 70000000000}],
                             'double_spend_seen': False,
                             'fee': 960900000,
                             'height': 1088438,
                             'note': '',
                             'payment_id': '0000000000000000',
                             'subaddr_index': {'major': 0, 'minor': 0},
                             'timestamp': 1517341824,
                             'txid': '21e7eb651e8a2bc7661975e965ac6b30a6f4033c6a02e96320e41139ad3e307c',
                             'type': 'out',
                             'unlock_time': 0},
                            {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                             'amount': 3333333333330,
                             'double_spend_seen': False,
                             'fee': 960750000,
                             'height': 1088521,
                             'note': '',
                             'payment_id': '0000000000000000',
                             'subaddr_index': {'major': 0, 'minor': 0},
                             'timestamp': 1517347785,
                             'txid': '5d15fef66fe8de715bcbf2c181f97b9932f9f843aef4724f3026fa3cd1082c68',
                             'type': 'out',
                             'unlock_time': 0},
                            {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                             'amount': 1000000000000,
                             'destinations': [{'address': 'Bg2iRGq5f6iXf3gXYps9AJFWuhhtL74o8GE4JrBPFN3ViuyuTDcPSVqckGeNSU1brSFbdYJ5jjVerJ8Cb4aGJwJTSvzzHwf',
                                               'amount': 1000000000000}],
                             'double_spend_seen': False,
                             'fee': 960990000,
                             'height': 1088394,
                             'note': '',
                             'payment_id': '6cc9350927868849',
                             'subaddr_index': {'major': 0, 'minor': 0},
                             'timestamp': 1517335388,
                             'txid': '5e8f392a42899294e6b679ddac13cfe1dfe7f034b1e347424218af06c3dfdc85',
                             'type': 'out',
                             'unlock_time': 0},
                            {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                             'amount': 2450000000000,
                             'destinations': [{'address': '9vgV48wWAPTWik5QSUSoGYicdvvsbSNHrT9Arsx1XBTz6VrWPSgfmnUKSPZDMyX4Ms8R9TkhB4uFqK9s5LUBbV6YQN2Q9ag',
                                               'amount': 2450000000000}],
                             'double_spend_seen': False,
                             'fee': 961350000,
                             'height': 1088184,
                             'note': '',
                             'payment_id': '6cc9350927868849',
                             'subaddr_index': {'major': 0, 'minor': 0},
                             'timestamp': 1517299877,
                             'txid': '2b41226d45edb875634694fccd95f3c174daa5062763eee619ed4475a7b9207a',
                             'type': 'out',
                             'unlock_time': 0},
                            {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                             'amount': 1000000000000,
                             'destinations': [{'address': 'BZHa2Fm9yn3by1CWTBruWxEuZ5TqyMLiBQAFrHM6aniLfjTBWkA4E4kif63YS7wmbFW5UBwrFSKNoiSQ2mE8SS5S6uzgvoc',
                                               'amount': 1000000000000}],
                             'double_spend_seen': False,
                             'fee': 961350000,
                             'height': 1088184,
                             'note': '',
                             'payment_id': '0000000000000000',
                             'subaddr_index': {'major': 0, 'minor': 0},
                             'timestamp': 1517299877,
                             'txid': '40de45db57eb87eb8395baf5c1dc705602938317d043f463e68ed85b7108f9f3',
                             'type': 'out',
                             'unlock_time': 0},
                            {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                             'amount': 123000000000,
                             'destinations': [{'address': 'BYeK7sZ9DhkASZpMrhGw6yFynaDy5PJ8T2CeogvGTFfT2kMQdTNJFQpDXpoHNBPTyNfrxERdRje9bBJh7LTqN4oDUVVvzAe',
                                               'amount': 123000000000}],
                             'double_spend_seen': False,
                             'fee': 3843000000,
                             'height': 1088523,
                             'note': '',
                             'payment_id': '0000000000000000',
                             'subaddr_index': {'major': 0, 'minor': 0},
                             'timestamp': 1517347908,
                             'txid': 'e291fe40c6102a6193c82ac33227c08e5b30a863dba1bc63e13043a25abbb97a',
                             'type': 'out',
                             'unlock_time': 0},
                            {'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                             'amount': 2220000000000,
                             'double_spend_seen': False,
                             'fee': 3843840000,
                             'height': 1088411,
                             'note': '',
                             'payment_id': '0000000000000000',
                             'subaddr_index': {'major': 0, 'minor': 0},
                             'timestamp': 1517339862,
                             'txid': 'a8829744952facbfdaab21ca193298edb1fa16f688cd5dbcdff3ed3968155f28',
                             'type': 'out',
                             'unlock_time': 0}],
                    'pending': [{'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                                 'amount': 3141592653589,
                                 'double_spend_seen': False,
                                 'fee': 3842880000,
                                 'height': 0,
                                 'note': '',
                                 'payment_id': '0000000000000000000000000000000079323846264338327950288419716939',
                                 'subaddr_index': {'major': 0, 'minor': 0},
                                 'timestamp': 1517348994,
                                 'txid': '34833fef78c7b7c15383a78912344ecfb3ace479d27c4bd6f3e3f136ddc1d6a9',
                                 'type': 'pending',
                                 'unlock_time': 0}]}}
        pay_out = self.wallet.outgoing(unconfirmed=True)
        self.assertEqual(len(list(pay_out)), 12)
        for pmt in pay_out:
            self.assertIsInstance(pmt, OutgoingPayment)
            self.assertIsInstance(pmt.local_address, Address)
            self.assertIsInstance(pmt.amount, Decimal)
            self.assertIsInstance(pmt.timestamp, datetime)
            self.assertIsInstance(pmt.transaction, Transaction)
            self.assertIsInstance(pmt.transaction.fee, Decimal)
            self.assertIsInstance(pmt.transaction.height, (int, type(None)))

    @patch('monero.backends.jsonrpc.wallet.requests.post')
    def test_outgoing_unconfirmed_only(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = self.accounts_result
        self.wallet = Wallet(JSONRPCWallet())
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'id': 0,
            'jsonrpc': '2.0',
            'result': {'pending': [{'address': '9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC',
                                 'amount': 3141592653589,
                                 'double_spend_seen': False,
                                 'fee': 3842880000,
                                 'height': 0,
                                 'note': '',
                                 'payment_id': '0000000000000000000000000000000079323846264338327950288419716939',
                                 'subaddr_index': {'major': 0, 'minor': 0},
                                 'timestamp': 1517348994,
                                 'txid': '34833fef78c7b7c15383a78912344ecfb3ace479d27c4bd6f3e3f136ddc1d6a9',
                                 'type': 'pending',
                                 'unlock_time': 0}]}}
        pay_out = self.wallet.outgoing(unconfirmed=True, confirmed=False)
        self.assertEqual(len(list(pay_out)), 1)
        for pmt in pay_out:
            self.assertIsInstance(pmt, OutgoingPayment)
            self.assertIsInstance(pmt.local_address, Address)
            self.assertIsInstance(pmt.amount, Decimal)
            self.assertIsInstance(pmt.timestamp, datetime)
            self.assertIsInstance(pmt.transaction, Transaction)
            self.assertIsInstance(pmt.transaction.fee, Decimal)
            self.assertIs(pmt.transaction.height, None)

    @responses.activate
    def test_multiple_destinations(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_multiple_destinations-accounts.json'),
            status=200)
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_multiple_destinations-incoming.json'),
            status=200)
        self.wallet = Wallet(JSONRPCWallet())
        out = self.wallet.outgoing()
        self.assertEqual(len(out), 1)
        pmt = out[0]
        self.assertEqual(pmt.amount, 1)
        self.assertEqual(len(pmt.destinations), 2)
        self.assertEqual(pmt.destinations[0][1] + pmt.destinations[1][1], pmt.amount)

    @patch('monero.backends.jsonrpc.wallet.requests.post')
    def test_send_transfer(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = self.accounts_result
        self.wallet = Wallet(JSONRPCWallet())
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'id': 0,
             'jsonrpc': '2.0',
             'result': {'amount_list': [3000000000000],
                        'fee_list': [3866640000],
                        'multisig_txset': '',
                        'tx_blob_list': ['020001020005a3d60be09109dfd202e617d904090789e33b02c001885d17d80101a4de34b9e76f8e9b87f50766b33a1f00f49d020002c5fc19a94f82a9cefeaebf5f9f7d8330ff28cc7b1c6dba65d5dd3bfe4693056a00028711ea3e11b97250e7563838e4ea203594c4b33784c2d9777aa738061a31946d2c020901b259965ad1f33d2d014c8cdd4a341a75cf01fef00e6b344b47150e55ae06333b5585b20eb0f4afff160380fde0b30ee3c5ebbb3bbaf11b30f4ef79ee96122175077cec9866b88aa123fdd9f55e2d06cb3815f7e8e88dbcd4f6776aafd13cdf21c86b38671bb4641dd4d696fff29a0546817024cb9f9330fe86a43c1e4088a9019a601aa80025e3f24d0ab5066fdd09254ec751d101960c3422db7657a43b764f015679b3da7221aa349d40ddcce60964af135cbef245c4a2d51bd2b8605b6ce7576f32e9f0b06d91b3840828902cd4c35a1a59fdef21441a02a78229df304f8569f259c3ec218ffe45722020fbfde6a74b0d36753d6afae377e771d454839f8e76762e23dbf35ee354716f7d15f42e7e03048d917984a814fdef3ea4556d0946b30a790e8e0739e8e9f933da61e3ddd2699df0bcf55ac1c149cfbea618830933830bd3937b1f27613cd0959b6020dda7ced635d3c41d31694a526788a7c783e8476594006e2dee7d9fd606d793618fc062ed8cc178c4e1376524a6029a618b882cbfc86f40cc0a036b11d30500290abc052823a5f3b180cb7e05e0c9316a7cbfc9e94c370e0817b3ad5c90c0d9070606883d72d6706f1b5069652a8a98c20d60774ff6dd3ba2fa09d39af8c5f7cca2e592cdd0df79482d44baba5531f24961967c43c720aa8f3d93b376c67064960baacf4c347dc243cee2b44e8194fe14e1efe785924671cf8ff3bf545ab8a05213bcce3adef4dae1988e9d33926722be5927c952f6b8f36e62a8fafdb699c8ffdc61720a6d869bfc2719a05fe9f13c72e295869955bfb88eb79d95d19285340049906d497d9d847c09b7e4009d8b0c09a535e993583270227e00c883822a32fbf1c206e5de38438c1d637fd87600f6d56b673e608625acfebbfb8c32632da3282346588078d4af03c84ef78a141af8ca92d236b7f464aad3f4e66e34689d0bb2fbed1a0b9fc342e5e8a51505b69c9cb7d401778576e36c68475ad738e35f867ad6498428d59fdf3e92d42cb91515675a0a8412a85e359c4aa9f25a684b2e5fa0d3faee9afef115113579b423f2386edf9b8961c1a37967a7718b20594421fdb537069c643f03475f2396ad61faa904c1f35ce2436f6260c51c429a58358c1f19961bb8a9b3516e2eef13551315ab586e68caae69c4c09b40ff6fff4f67fdc2f700600b5a97f280b6a94c11068065d8edf1cbb10203e559ee94ba3cbea4eee1cd36790012196284ba15b3d7427c3fd3647cb65c9230d2fafbd96c978e0545e404317805c549d2bfcb7bc68bdbce5a94f2f090487d58e2be4d011b44532d8543338c64cf91dc869021b94b5c2b7dabf666b2a57c703e4a1cbd6702fceb42cff1108e06b4412abbc5f68cae62fc01bd9ac96e36ce07d1536115d44c752b37d5d90ea44614a76a67ac7da251511a8fed42a012478f29031603da3eef2cde3d7a9e342c92fcc88f1437a50ec0bb18670ece373de05945dd05976433a32bf352715fe5c8960940a9cff86b97bf57786ccfbf7ddac06bb657ed936d6c112bdc6bf6e5f731ef0e066f554b95f530932ac950ebddd01eb04bf36073da30bf1addf137a0f5852fa8480dfc7e2962424c5d3d6f420f85217d30b481dae95db7d87d8da86cc259675b33a546c0eff502768ea78a296ca55b608dd492c2c213415c45b3167c051f45fc04c12c67a06d984f8deef6079dcd0f6d07513c735630d53ff281d9a2024e84f749164db0fe0826690c460342b5c48a4fb2f7cae80efef65cea5b733bf8624314e74efd5212c23925ab08adaa5bd78bfb24bc5e4133328e478235a42538c0d01edb065ff17ed0116d1e33864dbedc31304c04d31ae7451048979c9ca4e92d6bcdb5e4ac42caa22665729967504dd1242f95f71dcbc59cd9d62c831f774ac9ebe0619318f31229075535793924dc79874fff17954686c4463b1094d1e3f8a98c115fec2d2b1e37c11d06f7a24c1dbf7871b7510d8f5785b47a5c62203820add67f0264dfe71ac6185e457d3be8944ba5ff3d78847b21349a2a5813b79fadce4fa2f393edaa4904c7564d8036664b0191090e82bf275b552e8cd5f04ee30511a8edad21bb8041588e71296836d34e86e8f7c6edc4327b7d1122377b19fb6e8961c26a0ab1b4e3a5e0f6d2b6b4448e395985981584c78da0b7678d2a338d553d07be430c0e967c86e0859eb69422959d6eacb43ed9acc678d515466ce9bca08c03ad2a09affa136893566df52a553ca67f529fe9fa72f15b7fd60c769a5168d53c02d701937d20d79284f34e1b7094c40491df2619c03efacc3989d340d7b611c348f9098fa80e007874cd7bdb6eb67c23e17f8446ca01b6ea1fe1475b3cb5a031d50e0424f2efb010259a038d693ca1ab3bc1abf5c56880c2d14355790934617c2b260a74883c88310fa0bb0d2aa0a5778532b3bff7a80586a2fd761e2620c3bcad1006cc328cdd3a9c790d30d260e473a85ffc8200dae9bc2992cd446d55103668db0e2f85976ec87bf7bda26c4c6492f76e493beef5daf29f0b723fa8d9cb4eba4f03396c65b052fbf4521dfd7ed611fe3bbbb577ab46ff87002bad166e6a61873b0e2a8b5be203a6a0c4bd12c7a5cc82284d12b089b4cf245d38d93749383a85b202deba9fbcab44b9f343117669ccf91cf16df5af4309941c718e937228ec2ace05c3fbf708be2d079c92b1045c0167116dc2c52323b23f8514eddbe1e3d30cb005'],
                        'tx_hash_list': ['401d8021975a0fee16fe84acbfc4d8ba6312e563fa245baba2aac382e787fb60'],
                        'tx_key_list': ['7061d4d939b563a11e344c60938410e2e63ea72c43741fae81b8805cebe5570a']}}
        txns = self.wallet.transfer(
            '9wFuzNoQDck1pnS9ZhG47kDdLD1BUszSbWpGfWcSRy9m6Npq9NoHWd141KvGag8hu2gajEwzRXJ4iJwmxruv9ofc2CwnYCE',
            3)
        self.assertEqual(len(txns), 1)
        txn = txns[0]
        self.assertIsInstance(txn, Transaction)
        self.assertIsInstance(txn.fee, Decimal)
        self.assertEqual(txn.hash,
            '401d8021975a0fee16fe84acbfc4d8ba6312e563fa245baba2aac382e787fb60')
        self.assertEqual(txn.key,
            '7061d4d939b563a11e344c60938410e2e63ea72c43741fae81b8805cebe5570a')

    @responses.activate
    def test_sweep_all(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_sweep_all-00-get_accounts.json'),
            status=200)
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_sweep_all-10-getbalance.json'),
            status=200)
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_sweep_all-20-sweep_all.json'),
            status=200)
        w = Wallet(JSONRPCWallet())
        result = w.sweep_all(
            '55LTR8KniP4LQGJSPtbYDacR7dz8RBFnsfAKMaMuwUNYX6aQbBcovzDPyrQF9KXF9tVU6Xk3K8no1BywnJX6GvZX8yJsXvt',
            relay=False)
        self.assertEqual(len(result), 1)
        result = result[0]
        self.assertIsInstance(result[0], Transaction)
        self.assertEqual(Decimal('111.086545699972'), result[1])

    @patch('monero.backends.jsonrpc.wallet.requests.post')
    def test_dynamic_ring_size_deprecation(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = self.accounts_result
        self.wallet = Wallet(JSONRPCWallet())
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'id': 0,
             'jsonrpc': '2.0',
             'result': {'amount_list': [3000000000000],
                        'fee_list': [3866640000],
                        'multisig_txset': '',
                        'tx_blob_list': ['020001020005a3d60be09109dfd202e617d904090789e33b02c001885d17d80101a4de34b9e76f8e9b87f50766b33a1f00f49d020002c5fc19a94f82a9cefeaebf5f9f7d8330ff28cc7b1c6dba65d5dd3bfe4693056a00028711ea3e11b97250e7563838e4ea203594c4b33784c2d9777aa738061a31946d2c020901b259965ad1f33d2d014c8cdd4a341a75cf01fef00e6b344b47150e55ae06333b5585b20eb0f4afff160380fde0b30ee3c5ebbb3bbaf11b30f4ef79ee96122175077cec9866b88aa123fdd9f55e2d06cb3815f7e8e88dbcd4f6776aafd13cdf21c86b38671bb4641dd4d696fff29a0546817024cb9f9330fe86a43c1e4088a9019a601aa80025e3f24d0ab5066fdd09254ec751d101960c3422db7657a43b764f015679b3da7221aa349d40ddcce60964af135cbef245c4a2d51bd2b8605b6ce7576f32e9f0b06d91b3840828902cd4c35a1a59fdef21441a02a78229df304f8569f259c3ec218ffe45722020fbfde6a74b0d36753d6afae377e771d454839f8e76762e23dbf35ee354716f7d15f42e7e03048d917984a814fdef3ea4556d0946b30a790e8e0739e8e9f933da61e3ddd2699df0bcf55ac1c149cfbea618830933830bd3937b1f27613cd0959b6020dda7ced635d3c41d31694a526788a7c783e8476594006e2dee7d9fd606d793618fc062ed8cc178c4e1376524a6029a618b882cbfc86f40cc0a036b11d30500290abc052823a5f3b180cb7e05e0c9316a7cbfc9e94c370e0817b3ad5c90c0d9070606883d72d6706f1b5069652a8a98c20d60774ff6dd3ba2fa09d39af8c5f7cca2e592cdd0df79482d44baba5531f24961967c43c720aa8f3d93b376c67064960baacf4c347dc243cee2b44e8194fe14e1efe785924671cf8ff3bf545ab8a05213bcce3adef4dae1988e9d33926722be5927c952f6b8f36e62a8fafdb699c8ffdc61720a6d869bfc2719a05fe9f13c72e295869955bfb88eb79d95d19285340049906d497d9d847c09b7e4009d8b0c09a535e993583270227e00c883822a32fbf1c206e5de38438c1d637fd87600f6d56b673e608625acfebbfb8c32632da3282346588078d4af03c84ef78a141af8ca92d236b7f464aad3f4e66e34689d0bb2fbed1a0b9fc342e5e8a51505b69c9cb7d401778576e36c68475ad738e35f867ad6498428d59fdf3e92d42cb91515675a0a8412a85e359c4aa9f25a684b2e5fa0d3faee9afef115113579b423f2386edf9b8961c1a37967a7718b20594421fdb537069c643f03475f2396ad61faa904c1f35ce2436f6260c51c429a58358c1f19961bb8a9b3516e2eef13551315ab586e68caae69c4c09b40ff6fff4f67fdc2f700600b5a97f280b6a94c11068065d8edf1cbb10203e559ee94ba3cbea4eee1cd36790012196284ba15b3d7427c3fd3647cb65c9230d2fafbd96c978e0545e404317805c549d2bfcb7bc68bdbce5a94f2f090487d58e2be4d011b44532d8543338c64cf91dc869021b94b5c2b7dabf666b2a57c703e4a1cbd6702fceb42cff1108e06b4412abbc5f68cae62fc01bd9ac96e36ce07d1536115d44c752b37d5d90ea44614a76a67ac7da251511a8fed42a012478f29031603da3eef2cde3d7a9e342c92fcc88f1437a50ec0bb18670ece373de05945dd05976433a32bf352715fe5c8960940a9cff86b97bf57786ccfbf7ddac06bb657ed936d6c112bdc6bf6e5f731ef0e066f554b95f530932ac950ebddd01eb04bf36073da30bf1addf137a0f5852fa8480dfc7e2962424c5d3d6f420f85217d30b481dae95db7d87d8da86cc259675b33a546c0eff502768ea78a296ca55b608dd492c2c213415c45b3167c051f45fc04c12c67a06d984f8deef6079dcd0f6d07513c735630d53ff281d9a2024e84f749164db0fe0826690c460342b5c48a4fb2f7cae80efef65cea5b733bf8624314e74efd5212c23925ab08adaa5bd78bfb24bc5e4133328e478235a42538c0d01edb065ff17ed0116d1e33864dbedc31304c04d31ae7451048979c9ca4e92d6bcdb5e4ac42caa22665729967504dd1242f95f71dcbc59cd9d62c831f774ac9ebe0619318f31229075535793924dc79874fff17954686c4463b1094d1e3f8a98c115fec2d2b1e37c11d06f7a24c1dbf7871b7510d8f5785b47a5c62203820add67f0264dfe71ac6185e457d3be8944ba5ff3d78847b21349a2a5813b79fadce4fa2f393edaa4904c7564d8036664b0191090e82bf275b552e8cd5f04ee30511a8edad21bb8041588e71296836d34e86e8f7c6edc4327b7d1122377b19fb6e8961c26a0ab1b4e3a5e0f6d2b6b4448e395985981584c78da0b7678d2a338d553d07be430c0e967c86e0859eb69422959d6eacb43ed9acc678d515466ce9bca08c03ad2a09affa136893566df52a553ca67f529fe9fa72f15b7fd60c769a5168d53c02d701937d20d79284f34e1b7094c40491df2619c03efacc3989d340d7b611c348f9098fa80e007874cd7bdb6eb67c23e17f8446ca01b6ea1fe1475b3cb5a031d50e0424f2efb010259a038d693ca1ab3bc1abf5c56880c2d14355790934617c2b260a74883c88310fa0bb0d2aa0a5778532b3bff7a80586a2fd761e2620c3bcad1006cc328cdd3a9c790d30d260e473a85ffc8200dae9bc2992cd446d55103668db0e2f85976ec87bf7bda26c4c6492f76e493beef5daf29f0b723fa8d9cb4eba4f03396c65b052fbf4521dfd7ed611fe3bbbb577ab46ff87002bad166e6a61873b0e2a8b5be203a6a0c4bd12c7a5cc82284d12b089b4cf245d38d93749383a85b202deba9fbcab44b9f343117669ccf91cf16df5af4309941c718e937228ec2ace05c3fbf708be2d079c92b1045c0167116dc2c52323b23f8514eddbe1e3d30cb005'],
                        'tx_hash_list': ['401d8021975a0fee16fe84acbfc4d8ba6312e563fa245baba2aac382e787fb60'],
                        'tx_key_list': ['7061d4d939b563a11e344c60938410e2e63ea72c43741fae81b8805cebe5570a']}}

    @patch('monero.backends.jsonrpc.wallet.requests.post')
    def test_export_import_outputs(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = self.accounts_result
        self.wallet = Wallet(JSONRPCWallet())
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'id': 0,
            'jsonrpc': '2.0',
            'result': {'outputs_data_hex': '4d6f6e65726f206f7574707574206578706f72740393332736be3f7d08c6a00a99f3f14f933f6e9b266ee5a84738a4331a446eb9c16415cb7932dae2730bd713c58bc286fcfc257fad6349ae2346242d5f4cf0dda5c14b3acd335bd157b4f8d101ee95a169e6cf9ae8d1ef0f2fb98b23c0841889cf6017f405d3a097a8d7b3089026dcf969cba8df8140e798a9a8c6204e66ddfe22c945702c1b84fb6ecf3484070ed53622b38cd5dcae3441168219d1637a6a7bf8114c03b8ace240ca90a7dce92ee5d22fd302a623fc98d59503debdeb16f096f8f0b4fd5c5585143f7adb9d8a918ad2ff01d47cbd8c3d27b1278b28446ad3782d68a7d42dfbf7959710239eafad6476a36ed02bcd563b780572980a9ab7340d850bd489a415f71da64b7c51c9cbfcfb4556c97ad9d7617b27e0bc128995dea5b6c8b67cc160c2b001bf9750b719cbd46e1d4e9e2f7c654948ee775820501e53bea9383d16a7e8b0de60ca15eec3cc132f869f704887fa78415fd4da9d77c7592d76ddff5bc0f13c1f2dfcc4a9086e1e38d90b13b8aecb91778f3d187513ffd9c543c0551f43020c74340c6b795c84e9cc8c85b0f6e6d649201c0ba4c738afb8b984c25244e69a66b799f145cb3dd1378df1f59767a884eced4779ca9b6d3919d5b635427f2cc2db7dd064a84d4e1e31f707ce593cbeec9066dafea07e3086522a0d099e15bdc7cde66f02e352e2e5b5d493bbc8ff4a43d4ac1956cb70697793a8856428bc77d4894912871a177b275e5f1dac55becb150981205b0723ab2137549b8ae39a665a24485fae048288012b7937a032c3b617eed0b10504ea43b00fc70cb4b935cebe09adb163e9806aa22edefe7921c90dbf6db8a0541e03b73420a0615fefb11a93c608c0985a865436bc1f865a97fb6ef77d8fd4d8db202c53374f06b65ce251fd200c7323aa017b407d06c3ede254d82e39a149b74dd70a89b892704aa19b5eec9bf5610e014f3175dc3f13e79a64d1bcdf2c492494e813e5df157f40a5d796d1414e0e6c65b11e8fb9e63b26aae3f4c4367b0a6333b819e7ed4a2b2687b292c1611d7efe638033da44a4d9ecf12417beaee8c05b978c0eda0808be4cdb0ee76ed5d54dbf4c61f99e6cef60c5baecb615015036d6113890b8827d3b41f21273c3a860531cd2ea1d1ecff3656740c69702d0d6ea34160cc9cd5d3c58bd2ca53320fef77c384aaa8214a30d315c8d94174d45759fd13fdb8d0c94823964dc669ad23eb85426a6f316931c1e42c839b5b0713fffd34890165cee2656f63b7fee0949849368fc0ca2dff74340cca7dd724c06d2e7ec40195535ec43c2b8977cb0bd0955d56b540fb7eb7103d5f432edd63f9d426b464ec3f531633a86487c27660662fa5164b8402ca1535933cf2e55868a8cc3a4fd19a8a42d8878008ae6ddf1e17236e7f816da9aceb5baa381c3727604516df20557281d9ebc1bd9f27effbf1375680b910f8fcd2cf9799eb4845e0aa17653525fdcdef87278d9b069265850e39e6c6598ec370a8ac372638aa781c6d71cf4d9b65115034d01b24cdfd4d02c97aac431ccd192c25de4e4feefc119a6ea55d477566c79761113a04cdd0a5a1e161279795efc5e0f8fe3c2cebceb5dd6f6a0383a18fedd5b83d404239ce6ecab6e6265a9d4678f8ec10445d2b0e790fd414b071d3fe1076a18c6a90f4e7ba1bdbfcd363d7e3aef31a502d5f262ad54777d001d14b3a809de213b379929e4308a0b0f45e1aa0c6b3b483a4867f2827c316e85223cb191fcd546600d96f32e3ff9377cff408d475f59b385e0d78bbbf640e5f180fc64622d9536a8ab1f89309044813cc9e0840e57b1e2c5e392cca2cbd3bac1b2ac4c12ce11f2e7e48e644ebb0936002d2e2c554fb52fb7dc02b4371f87c5175af7ea0b101e2486b6331f5887604b4245c8b71c56edce095483d6fc4b3d90b642f53973e1ed0af6de3d0143a10a442668e4ac1db0c321ced61d17ac559a61000e643d62762fa41249f5d2712938e224555dfca61352e5a288db6eaa2fa2f3cbad48b45780c6fd84a772cd16e3922825125969f9ac5fa1e75a1faaea9350895ec0c5286a3d7cdfe99d6ee5d290e95bfeb7f35a28d4f6bb5996fd40bd18bbf1138b6a86ab74fa2228abd72c69646cd6fd0b53562c5e41104b5b5ac047cff45240169703282f09872f1152cffd4ad5bf13e3ee8123d8510154a7fdfa435c0ff92464db01b7fe9d41bdd63fb01178093d2f5f1f83cbff2674f509e45ed2e359faa2549259d849c74b1ca5b15ad9bd20a0121c4af360782cb260a021e4e6dc680429394eda423910105936f8d3c9ff29c6b5d48b42ad3f0e0318647d3f2d5d17cb7fe37cfe4b947a0f9ffdf84adb53dbd5b2a228f73ca79396703290f8111863dfa1de9a7c91dc42107d5cdee5c7234d25476f0b3500966a6ef2df343721fdfa57631ea3d5df939b7ff88be4f7738d829cbd0f4dc6ea5c6799ce0747da631fba84a5c0d29c905e377675171a040b4311c13940c78240b5157d4fb17b27e94ace0b29b7629955d35a3a7fbccc977f82f272253bcaaf458340b394b6263af39146ea8b20938c3259bc641d7b5f47fad1ffeb251aa40e97c54f112cd0b571dbfafe83a1776add24c8ad5c363eea5d420f869e05e32d0f926c5d8d1a0a533b0ed60f1cf3104765a27c11dd18e74a62cd329594e22d75d357f10afa56f1cd51220a5165c75d7bf1779d904d1f5715a3db1607c01bf266676db7055813db92522a49fff7ff96042c6476b7fb00487b484ed1675b390efab7d3b40221ab3d0f4c8872189644197c1e6b0b9a5a66e7fc32aeff38539a63db449a5233f8a4be230324d8ac99efa472ec4e7fde53f616efae90ad84ee88c3afe5df6a1eae471c2928692ebc896c28eb3934308d1ba01ef9d209dee589adc5ccce2ad658828080037a64656ecff5209f157cbd57f37bc25461771ca549d44ceaa2178bae4acb1dfe5367503575a8bee605f9e3ed629dbcdeee58ba732819ec818e776c9f66ebc2757c3c0c7a1afd37b8113c322e62d826169c560f5a7c9456b30307db0ec2e594b0ecb6580067fda2f5196ad8ff6b460ebbc8879fbf41559e03c109f2f610d0611899cdbd33ed3a718b0c875073d972aaf1f440702fef37983abc9845df067a52b3697ae6f722f4f743de910e68f13ecb3645a0a9a1e0ef9f71c02bfc7aa22743c8175ed767ec12d042bf7ec32edc2bc5d3c54e9969bf22c434db5bdbbba21fd827fe084963344411e61291bf1ed92432f9de0af8f68c73343bf8baf8205754bdcfe5a540cc870e45d634e3d84281ff70a3d619cd60da558d106b669f3c1a8786eb258a2816e19064418e4b410b47ca6d2f07f75acf507417d1872c4e3ccb797435a1f3dcf3877627cecbcd3d7bea19712b4ad9363363c177153a71b81e4eeb9048a4dd3531daf81e23a8a165eb20ee03d02994157fff693ed9900b67876654ec0ba974eac6c4b8d223c834a2e31d6a9e785c6ac066c4cb8291f859a4f77346dc9133d93f94abca5d9b16bf93d9c0879aa44bcbb4c29c0726db1e905823531abb9e2a8dad4a1d3eea6814530f8d4da4290a64cb83dc6c21bbdcb3665124a3fe54a93d58f64048ccca4fe832bae27747955d5b11b9e636e5a38c3f5f4d93b2b711de020c99ffa147d2e755504995a4790b4e7432a4bf33187a08179e4e3232040914be7a7b98221576f2bf05ee2a8d4a55a6788a4e44bb7c5047dcbb41b01aeff3d0604b70118ed7c74fff089b467f0059da8ebaf7ebe9afdd746eefedcd63103ce88f0fa8234e512b64e742d12a9046690a0cb7be124b4294b3249695702c57f0c7c07ad9d0ee41cef44cdea99478671fd7ebeef353082cbd93956c96deeee0c91b66e8899b8537294b30cc0b7e0d3958c4b5dc9954c7ba04fe4addc9bd3c4040a09418a9ef3dbd59a4a445f7cadbd8ff004afa75133c56692995626148c096ac74a3cdc1fbb746d0b55900df0deb466ad93b7986f1652b42cf5d0de98001709423b233eb3612f1774e54d0939ef2c7e8aefd6e0a72c00597baf85617041c3639f69f5ab628ece848d8cc183a250df634673c51e96c0b6edb232c29cb05a7b6d465e729f3a250a4dbd90aba8ed4d3a9ce783af1c755a224d583e3639ebd383eed58667461d13f19ef20a8ee9e968fbab7cdd580e1899639d1f92ada3c4332a3d561807b3b85b52436143aa97a49c177e9acb0dd4c1d2e5f8fe0c2f55c9810309e422a65cfdd9d16cc84fad5d6019c61c120c02461b512cf9a507a61b5205f431e6646f622891af9c918e841e5f64b37c2071f6f1c5a43953f2ec79cef7ca57413ef55555b256e9cb181f5b456fd45760f818abc2edccfbe3abebe2ed01439c530c79dfd1d62df609d4e1ed663f76dae50853ab121c50d2b5f55ec51ddcb1efee19722e946f049f6ba52a33986adf0bc9bdba057d94e3ebf542b6b10288d4c37c3d913bbaa8fa54972733bdec93b839adf2417f9a6d270ff793afb239086642862fa7c362f5c381263047a605674927e7fbd093e8a1d0ec66f60a89b48bab5f37f832d4643ac0c91caea78e1bc08d9255c1a569effe7a690bc4a174f6e8a4153999b83468c146007951f885fb08fa5ba68bef63b759d41b3c03a5493940793dbf414ca54b6114c39644cd667c3dd214db0dd261cb1367d1abfc4fe96ef233c43e8efbb080f89835c3c4d68754c3623d562d164a24fe48c5e38059ced6e69486661664351a7574113b686b79c9559c62452336cdd7543563213e5316407fd231cfa6dc95a1fe66ad40db5d1dc081a9fd2898b78def10dc835b189b6c7002da379336f1cadbfe04579ae0aee067b84eb7814a98224e1ece9035b4c4f35d9d1680f271182356ce57d3dd2db12f965a783af83dab107d8a2276ea8d43e38f1e842046c97ac09f4142f84c77a7bdfd9d36e3844f80209'}}
        outs_hex = self.wallet.export_outputs()
        mock_post.return_value.json.return_value = {u'id': 0, u'jsonrpc': u'2.0', u'result': {u'num_imported': 9}}
        self.assertEqual(self.wallet.import_outputs(outs_hex), 9)

    @patch('monero.backends.jsonrpc.wallet.requests.post')
    def test_export_import_key_images(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = self.accounts_result
        self.wallet = Wallet(JSONRPCWallet())
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {u'id': 0,
            u'jsonrpc': u'2.0',
            u'result': {u'signed_key_images': [{u'key_image': u'0100000000000000000000000000000000000000000000000000000000000000',
                                                 u'signature': u'ffe0d3216dc7a9f44dd997e7412ecb4a5e03641bba27119bbc0d5b6a145955048f4a8f301826c0d5999264cbc67817a6643143c49195a56fd135936667db0e08'},
                                                {u'key_image': u'0100000000000000000000000000000000000000000000000000000000000000',
                                                 u'signature': u'0ed0b9752eb5d2466985174c50453f3fc9bd271b1f95bfd50d484b958976c40e8e1a7584cde52a85d40edc4a1bf9684003436492364af0ad9e1d4add1e158108'},
                                                {u'key_image': u'0100000000000000000000000000000000000000000000000000000000000000',
                                                 u'signature': u'b54632f4e95f70eb1af6459c94694c65ff1b8c822b40a62e6ef7cc1c6a055b0bb4b3832d48330c863993bf46bf87e1ed2971bf6a5d94a9a333a59017fb83630e'},
                                                {u'key_image': u'0100000000000000000000000000000000000000000000000000000000000000',
                                                 u'signature': u'57f85fd761ecb780a877034cef57449df7c3ad492d803711d1b2a47bf192d00af2f2341388120364dba0d7496c0a5d041032602812995c11268253618713040a'},
                                                {u'key_image': u'0100000000000000000000000000000000000000000000000000000000000000',
                                                 u'signature': u'9d22b52da3b835afbf29de7ba2dd86fb805435492691799debd7d37dd932dc0e4b07e9b4744da38e2b38fac63475522112804627227756bc37dbc57ea7e59701'},
                                                {u'key_image': u'0100000000000000000000000000000000000000000000000000000000000000',
                                                 u'signature': u'664c7ac1c1f4c86e56ebc5298ef4acf46c2c154263c5dbc69b5d4d08b9f31a001db8845dbe37a81e7289e33f24ab5b0f17bbfe00612e4624c7b27ca0c27e5c0c'},
                                                {u'key_image': u'0100000000000000000000000000000000000000000000000000000000000000',
                                                 u'signature': u'a6bf6c5248b00f946ced5d21d03311fa6335b0ddf37f8e46d89d4b0a73de7b040d7ceee31da144693a8f86b1e61908014783e139061c0a4015b0ef13a967060c'},
                                                {u'key_image': u'0100000000000000000000000000000000000000000000000000000000000000',
                                                 u'signature': u'2d6792c9c438657a5a2d7068f16fe80ca7995144ec1f12f1a37c091690cf260323bbe866e88d725dc791344e6af29b0f22d0792b9f60a5020c6e54bad7fe1404'},
                                                {u'key_image': u'0100000000000000000000000000000000000000000000000000000000000000',
                                                 u'signature': u'a5fe1c57e83442856b1e3cefc67814c908f2485269adbe808c013c7ddb489c0592278fec3c7cc32b2d16135e627fe7bf42ab896e0c7a17333f176ff8bf267f04'}]}}
        kimgs = self.wallet.export_key_images()
        mock_post.return_value.json.return_value = {u'id': 0,
            u'jsonrpc': u'2.0',
            u'result': {u'height': 125578, u'spent': 322437994530000, u'unspent': 0}}
        self.assertEqual(
            self.wallet.import_key_images(kimgs),
            (125578, Decimal('322.437994530000'), Decimal('0')))

    @responses.activate
    def test_incoming_from_self__issue_71(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_incoming_from_self__issue_71-00-get_accounts.json'),
            status=200)
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_incoming_from_self__issue_71-1a75f-get_transfer_by_txid.json'),
            status=200)
        self.wallet = Wallet(JSONRPCWallet())
        pmts = self.wallet.incoming(tx_id='1a75f3aa57f7912313e90ab1188b7a102dbb619a324c3db51bb856a2f40503f1')
        self.assertEqual(len(pmts), 1)

    @responses.activate
    def test_init_default_backend(self):
        """Test default backend initialization.
        Also test for bug #88 where invalid backend value was passed to PaymentManager."""
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_incoming_from_self__issue_71-00-get_accounts.json'),
            status=200)
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_incoming_by_tx_id-7ab84-get_transfer_by_txid.json'),
            status=200)
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_incoming_from_self__issue_71-00-get_accounts.json'),
            status=200)
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_incoming_by_tx_id-7ab84-get_transfer_by_txid.json'),
            status=200)

        wallet1 = Wallet(host='127.0.0.1')
        self.assertEqual(type(wallet1._backend), JSONRPCWallet)
        pmts = wallet1.incoming(tx_id='7ab84fe2fb34467c590cde2f7d6ba7de5928a2db6c84c6ccfff8962eca0ad99c')
        self.assertEqual(len(pmts), 3)

        wallet2 = Wallet()
        self.assertEqual(type(wallet2._backend), JSONRPCWallet)
        pmts = wallet2.incoming(tx_id='7ab84fe2fb34467c590cde2f7d6ba7de5928a2db6c84c6ccfff8962eca0ad99c')
        self.assertEqual(len(pmts), 3)

        with self.assertRaises(ValueError):
            wallet3 = Wallet(backend=JSONRPCWallet(), port=18089)
