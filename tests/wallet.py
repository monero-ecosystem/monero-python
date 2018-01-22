from datetime import datetime
from decimal import Decimal
import unittest
try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock

from monero.wallet import Wallet
from monero.address import Address
from monero.transaction import Transaction, Payment, Transfer
from monero.backends.jsonrpc import JSONRPCWallet

class SubaddrWalletTestCase(unittest.TestCase):
    get_accounts_result = {'id': 0,
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
    def test_get_balance(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = self.get_accounts_result
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
        locked = self.wallet.get_balance()
        unlocked = self.wallet.get_balance(unlocked=True)
        balances = self.wallet.get_balances()
        self.assertEqual(balances[0], locked)
        self.assertEqual(balances[1], unlocked)
        self.assertIsInstance(locked, Decimal)
        self.assertIsInstance(unlocked, Decimal)
        self.assertIsInstance(balances[0], Decimal)
        self.assertIsInstance(balances[1], Decimal)
        self.assertEqual(locked, Decimal('224.916129245183'))

    @patch('monero.backends.jsonrpc.requests.post')
    def test_get_address(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = self.get_accounts_result
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
        waddr = self.wallet.get_address()
        a0addr = self.wallet.accounts[0].get_address()
        self.assertEqual(waddr, a0addr)
        self.assertEqual(
            waddr,
            '9vgV48wWAPTWik5QSUSoGYicdvvsbSNHrT9Arsx1XBTz6VrWPSgfmnUKSPZDMyX4Ms8R9TkhB4uFqK9s5LUBbV6YQN2Q9ag')
        self.assertEqual(a0addr.label, 'Primary account')
        self.assertEqual(len(self.wallet.accounts[0].get_addresses()), 8)

    @patch('monero.backends.jsonrpc.requests.post')
    def test_get_transactions_in(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = self.get_accounts_result
        self.wallet = Wallet(JSONRPCWallet())
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value ={'id': 0,
            'jsonrpc': '2.0',
            'result': {'in': [{'amount': 2470000000000,
                            'double_spend_seen': False,
                            'fee': 0,
                            'height': 1049947,
                            'note': '',
                            'payment_id': '0000000000000000',
                            'subaddr_index': {'major': 0, 'minor': 0},
                            'timestamp': 1511926250,
                            'txid': '0cdde0eb934c44b523f6e966a5e19b131ed68c3c08600bc087f48ae13015b704',
                            'type': 'in',
                            'unlock_time': 0},
                           {'amount': 6123000000000,
                            'double_spend_seen': False,
                            'fee': 0,
                            'height': 1049947,
                            'note': '',
                            'payment_id': '0000000000000000',
                            'subaddr_index': {'major': 0, 'minor': 0},
                            'timestamp': 1511926250,
                            'txid': '8b4154681c48a873550818ecaa6408a7c987a882b80917d6c902befd6ee57109',
                            'type': 'in',
                            'unlock_time': 0},
                           {'amount': 9767000000000,
                            'double_spend_seen': False,
                            'fee': 0,
                            'height': 1049947,
                            'note': '',
                            'payment_id': '0000000000000000',
                            'subaddr_index': {'major': 0, 'minor': 0},
                            'timestamp': 1511926250,
                            'txid': 'd23a7d086e70df7aa0ca002361c4b35e35a272345b0a513ece4f21b773941f5e',
                            'type': 'in',
                            'unlock_time': 0}]}}
        pay_in = self.wallet.get_transactions_in()
        self.assertEqual(len(list(pay_in)), 3)
        for tx in pay_in:
            self.assertIsInstance(tx, Payment)
# Once PR#3010 has been merged to Monero, update the JSON and enable the following:
#            self.assertIsInstance(tx.local_address, Address)
            self.assertIsInstance(tx.amount, Decimal)
            self.assertIsInstance(tx.fee, Decimal)

    @patch('monero.backends.jsonrpc.requests.post')
    def test_get_transactions_out(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = self.get_accounts_result
        self.wallet = Wallet(JSONRPCWallet())
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'id': 0,
            'jsonrpc': '2.0',
            'result': {'out': [{'amount': 484257334653,
                             'destinations': [{'address': 'BeUtm39sgTWfehPwwdrWWCAyUVfRQ512TTU5R1cm4SVmPVFxcqDz2zo5YGiyHtdav2RnDFdNvVnTANgsKtYTqo7kUCPvkqK',
                                               'amount': 484257334653}],
                             'double_spend_seen': False,
                             'fee': 19254480000,
                             'height': 1051266,
                             'note': '',
                             'payment_id': '0000000000000000',
                             'subaddr_index': {'major': 2, 'minor': 0},
                             'timestamp': 1512095241,
                             'txid': 'eadca0f956a2a60cb3497a7dff1bd80153140a111d2f7db257a264bd9b76f0b3',
                             'type': 'out',
                             'unlock_time': 0},
                            {'amount': 791221885761,
                             'destinations': [{'address': 'Bd2RQrySgNaBghRZimDu54iTeJPQFZqPKc36Mb8gWiiU3ripWBv7zZZYkGDBCd5uC1efzh88V3PhyeRhMEYiMSLPN2KLFAj',
                                               'amount': 791221885761}],
                             'double_spend_seen': False,
                             'fee': 19304320000,
                             'height': 1049917,
                             'note': '',
                             'payment_id': '0000000000000000',
                             'subaddr_index': {'major': 2, 'minor': 0},
                             'timestamp': 1511922110,
                             'txid': '5486ae9e6867ceb6e5aa478b32cba5c11d28e6d905c8479565c78e3933163ab6',
                             'type': 'out',
                             'unlock_time': 0},
                            {'amount': 98047029154,
                             'destinations': [{'address': '9xJAXRqfKJVgFcqAQPk6bThkjAhAdJ18tSTcpfpiSD634t74RqhzC3kAtHMNbScqkJCDhnvv5iCeuATuNS3r5y51RktPsoZ',
                                               'amount': 98047029154}],
                             'double_spend_seen': False,
                             'fee': 19253920000,
                             'height': 1051282,
                             'note': '',
                             'payment_id': '0000000000000000',
                             'subaddr_index': {'major': 2, 'minor': 0},
                             'timestamp': 1512098498,
                             'txid': '9591c8f6832cc3b7908c2447b2feef58c44e7774a5c05cea617ad2f3b3866c18',
                             'type': 'out',
                             'unlock_time': 0},
                            {'amount': 536269959084,
                             'destinations': [{'address': 'Bfiu2Zm5uoV8RkjGJVWtp2Wkzct15mdKcdM6P6CZsLkPfttjPqvXWR2GkdkG2ai91KNvyro8zKygygMcTf6feyUA8nJmyNT',
                                               'amount': 536269959084}],
                             'double_spend_seen': False,
                             'fee': 19303200000,
                             'height': 1049947,
                             'note': '',
                             'payment_id': '0000000000000000',
                             'subaddr_index': {'major': 2, 'minor': 0},
                             'timestamp': 1511926250,
                             'txid': 'af669b99162d9b514a0e8d3bd1d905e3b8778e6fcb88d172e5e049e909c4cc87',
                             'type': 'out',
                             'unlock_time': 0},
                            {'amount': 179693868346,
                             'destinations': [{'address': '9wFuzNoQDck1pnS9ZhG47kDdLD1BUszSbWpGfWcSRy9m6Npq9NoHWd141KvGag8hu2gajEwzRXJ4iJwmxruv9ofc2CwnYCE',
                                               'amount': 179693868346}],
                             'double_spend_seen': False,
                             'fee': 17927000000,
                             'height': 1049870,
                             'note': '',
                             'payment_id': '0000000000000000',
                             'subaddr_index': {'major': 2, 'minor': 0},
                             'timestamp': 1511914391,
                             'txid': '2fa2de7fbf009093c5319d0421d3e8c684b8351a066c48d51369aedbbfd1d9af',
                             'type': 'out',
                             'unlock_time': 0},
                            {'amount': 540005123047,
                             'destinations': [{'address': 'BYo9Bf1FXxBdM655QkQsxs25HZ78EehDmJWZfLAts8LFcym4k8LbEywJcWnoCBHVXQb5ZJ6JXrF2MFtNrVnswGXsAxWNBgh',
                                               'amount': 540005123047}],
                             'double_spend_seen': False,
                             'fee': 19302640000,
                             'height': 1049963,
                             'note': '',
                             'payment_id': '0000000000000000',
                             'subaddr_index': {'major': 2, 'minor': 0},
                             'timestamp': 1511928624,
                             'txid': '7e3db6c59c02d870f18b37a37cfc5857eeb5412df4ea00bb1971f3095f72b0d8',
                             'type': 'out',
                             'unlock_time': 0}]}}
        pay_out = self.wallet.get_transactions_out()
        self.assertEqual(len(list(pay_out)), 6)
        for tx in pay_out:
            self.assertIsInstance(tx, Transfer)
# Once PR#3010 has been merged to Monero, update the JSON and enable the following:
#            self.assertIsInstance(tx.local_address, Address)
            self.assertIsInstance(tx.amount, Decimal)
            self.assertIsInstance(tx.fee, Decimal)
            self.assertIsInstance(tx.timestamp, datetime)

    @patch('monero.backends.jsonrpc.requests.post')
    def test_get_payments(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = self.get_accounts_result
        self.wallet = Wallet(JSONRPCWallet())
        mock_post.return_value.status_code = 200 
        mock_post.return_value.json.return_value = {'id': 0,
            'jsonrpc': '2.0',
            'result': {'payments': [{'address': 'BZ9V9tfTDgHYsnAxgeMLaGCUb6yMaGNiZJwiBWQrE23MXcRqSde9DKa9LnPw31o2G8QrdKdUNM7VWhd3dr22ivk54QGqZ6u',
                          'amount': 2313370000000,
                          'block_height': 1048268,
                          'payment_id': 'feedbadbeef12345',
                          'subaddr_index': {'major': 1, 'minor': 1},
                          'tx_hash': 'e84343c2ebba4d4d94764e0cd275adee07cf7b4718565513be453d3724f6174b',
                          'unlock_time': 0}]}}
        payments = self.wallet.get_payments(payment_id=0xfeedbadbeef12345)
        self.assertEqual(len(list(payments)), 1)
        for payment in payments:
            self.assertIsInstance(payment, Payment)
            self.assertIsInstance(payment.local_address, Address)
            self.assertIsInstance(payment.amount, Decimal)
            self.assertIsInstance(payment.height, int)
