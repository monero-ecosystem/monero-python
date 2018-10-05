from datetime import datetime
from decimal import Decimal
import unittest
try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock
import warnings

from monero.wallet import Wallet
from monero.address import Address
from monero.seed import Seed
from monero.transaction import IncomingPayment, OutgoingPayment, Transaction
from monero.backends.jsonrpc import JSONRPCWallet

class SubaddrWalletTestCase(unittest.TestCase):
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

    @patch('monero.backends.jsonrpc.requests.post')
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

    @patch('monero.backends.jsonrpc.requests.post')
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

    @patch('monero.backends.jsonrpc.requests.post')
    def test_address(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = self.accounts_result
        self.wallet = Wallet(JSONRPCWallet())
        mock_post.return_value.json.return_value = {'id': 0,
            'jsonrpc': '2.0',
            'result': {'address': '9vgV48wWAPTWik5QSUSoGYicdvvsbSNHrT9Arsx1XBTz6VrWPSgfmnUKSPZDMyX4Ms8R9TkhB4uFqK9s5LUBbV6YQN2Q9ag',
                    'addresses': [{'address': '9vgV48wWAPTWik5QSUSoGYicdvvsbSNHrT9Arsx1XBTz6VrWPSgfmnUKSPZDMyX4Ms8R9TkhB4uFqK9s5LUBbV6YQN2Q9ag',
                                   'address_index': 0,
                                   'label': 'Primary account',
                                   'used': True},
                                  {'address': 'BbBjyYoYNNwFfL8RRVRTMiZUofBLpjRxdNnd5E4LyGcAK5CEsnL3gmE5QkrDRta7RPficGHcFdR6rUwWcjnwZVvCE3tLxhJ',
                                   'address_index': 1,
                                   'label': '',
                                   'used': True},
                                  {'address': 'BgzZVoJP6Vx5WP87r7NRCCRcFwiUha8uTgnjGGitHYTJEmRuz6Jq2oE9icDCGYMHXZcnR8T35Z8NoVXkfMnF9ikJNfcwwsy',
                                   'address_index': 2,
                                   'label': '(Untitled address)',
                                   'used': False},
                                  {'address': 'Bck7sYz1vvUghNNTR6rrpxfRDegswezggB9mWQkXgjwxKRTo1feiJopStdJAHtMJoSEdsYppWvQ6vbGbArWxP32xCG2TsVZ',
                                   'address_index': 3,
                                   'label': '(Untitled address)',
                                   'used': True},
                                  {'address': 'BYCcWM1gZHdCnh3Cb1KfWrAU1SjBWMV3KhUoeRy7V2Lw2F2hHeuzouP2NECBaTUgnyYAzEe8s5vpA7qmWYfjVfxeHoHWPnb',
                                   'address_index': 4,
                                   'label': '(Untitled address)',
                                   'used': False},
                                  {'address': 'BfJ5W7dZGaYih6J63YvhiDSKpVUUZbVrEhLRCY6L6TdnEfzJmwP6aUJZQQnzLQ2NMTKMAC8hiJsoiNC7jbEUZ8tmBoJcnN1',
                                   'address_index': 5,
                                   'label': '(Untitled address)',
                                   'used': True},
                                  {'address': 'BaJwiPYwnN6DV8yBeh4FjjCqRoPfdkWppSzVXTPBJo35fDyU8caxLchATGJg7TKB24Q8nM8P1iWSt4DMwec8Pg7bSbFDAir',
                                   'address_index': 6,
                                   'label': '(Untitled address)',
                                   'used': False},
                                  {'address': 'BbkS4mn6gcgUidn2znLa2J6eSBkbGjGX4doeDCKAzT2A3t1cjbquQGjhYgiMHiKTrY8ojk6Zjqi1ufvfuPwyKv4hNnMruro',
                                   'address_index': 7,
                                   'label': '(Untitled address)',
                                   'used': True}]}}
        waddr = self.wallet.address()
        a0addr = self.wallet.accounts[0].address()
        self.assertEqual(waddr, a0addr)
        self.assertEqual(
            waddr,
            '9vgV48wWAPTWik5QSUSoGYicdvvsbSNHrT9Arsx1XBTz6VrWPSgfmnUKSPZDMyX4Ms8R9TkhB4uFqK9s5LUBbV6YQN2Q9ag')
        self.assertEqual(a0addr.label, 'Primary account')
        self.assertEqual(len(self.wallet.accounts[0].addresses()), 8)

    @patch('monero.backends.jsonrpc.requests.post')
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
            self.assertIsInstance(pmt.local_address, Address)
            self.assertIsInstance(pmt.amount, Decimal)
            self.assertIsInstance(pmt.transaction, Transaction)
            self.assertIsInstance(pmt.transaction.fee, Decimal)
            self.assertIsInstance(pmt.transaction.height, int)

    @patch('monero.backends.jsonrpc.requests.post')
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
            self.assertIsInstance(pmt.local_address, Address)
            self.assertIsInstance(pmt.amount, Decimal)
            self.assertIsInstance(pmt.transaction, Transaction)
            self.assertIsInstance(pmt.transaction.fee, Decimal)
            self.assertIsInstance(pmt.transaction.height, (int, type(None)))

    @patch('monero.backends.jsonrpc.requests.post')
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
            self.assertIsInstance(pmt.local_address, Address)
            self.assertIsInstance(pmt.amount, Decimal)
            self.assertIsInstance(pmt.transaction, Transaction)
            self.assertIsInstance(pmt.transaction.fee, Decimal)
            self.assertIs(pmt.transaction.height, None)

    @patch('monero.backends.jsonrpc.requests.post')
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
            self.assertIsInstance(pmt.local_address, Address)
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
            self.assertIsInstance(pmt.local_address, Address)
            self.assertIsInstance(pmt.amount, Decimal)
            self.assertIsInstance(pmt.transaction, Transaction)
# Fee is not returned by this RPC method!
#            self.assertIsInstance(pmt.transaction.fee, Decimal)
            self.assertIsInstance(pmt.transaction.height, int)
            self.assertIn(pmt.payment_id, ids)

    @patch('monero.backends.jsonrpc.requests.post')
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

    @patch('monero.backends.jsonrpc.requests.post')
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

    @patch('monero.backends.jsonrpc.requests.post')
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

    @patch('monero.backends.jsonrpc.requests.post')
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

    @patch('monero.backends.jsonrpc.requests.post')
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
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            self.wallet.transfer(
                '9wFuzNoQDck1pnS9ZhG47kDdLD1BUszSbWpGfWcSRy9m6Npq9NoHWd141KvGag8hu2gajEwzRXJ4iJwmxruv9ofc2CwnYCE',
                3,
                ringsize=10)
            self.assertEqual(len(w), 1)
            self.assertIs(w[0].category, DeprecationWarning)
            self.wallet.transfer(
                '9wFuzNoQDck1pnS9ZhG47kDdLD1BUszSbWpGfWcSRy9m6Npq9NoHWd141KvGag8hu2gajEwzRXJ4iJwmxruv9ofc2CwnYCE',
                3,
                ringsize=12)
            self.assertEqual(len(w), 2)
            self.assertIs(w[1].category, DeprecationWarning)
            self.wallet.transfer(
                '9wFuzNoQDck1pnS9ZhG47kDdLD1BUszSbWpGfWcSRy9m6Npq9NoHWd141KvGag8hu2gajEwzRXJ4iJwmxruv9ofc2CwnYCE',
                3,
                ringsize=11)
            self.assertEqual(len(w), 2)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            self.wallet.transfer_multiple(
                [('9wFuzNoQDck1pnS9ZhG47kDdLD1BUszSbWpGfWcSRy9m6Npq9NoHWd141KvGag8hu2gajEwzRXJ4iJwmxruv9ofc2CwnYCE',
                3)],
                ringsize=10)
            self.assertEqual(len(w), 1)
            self.assertIs(w[0].category, DeprecationWarning)
            self.wallet.transfer_multiple(
                [('9wFuzNoQDck1pnS9ZhG47kDdLD1BUszSbWpGfWcSRy9m6Npq9NoHWd141KvGag8hu2gajEwzRXJ4iJwmxruv9ofc2CwnYCE',
                3)],
                ringsize=12)
            self.assertEqual(len(w), 2)
            self.assertIs(w[1].category, DeprecationWarning)
            self.wallet.transfer_multiple(
                [('9wFuzNoQDck1pnS9ZhG47kDdLD1BUszSbWpGfWcSRy9m6Npq9NoHWd141KvGag8hu2gajEwzRXJ4iJwmxruv9ofc2CwnYCE',
                3)],
                ringsize=11)
            self.assertEqual(len(w), 2)
