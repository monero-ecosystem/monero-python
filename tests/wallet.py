from decimal import Decimal
import unittest
from unittest.mock import patch, Mock

from monero.wallet import Wallet
from monero.backends.jsonrpc import JSONRPC

class SubaddrWalletTestCase(unittest.TestCase):
    @patch('monero.backends.jsonrpc.requests.post')
    def test_get_balance(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'id': 0,
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
        self.wallet = Wallet(JSONRPC())
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
        self.assertEqual(locked, Decimal('224.916129245183'))

    @patch('monero.backends.jsonrpc.requests.post')
    def test_get_address(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'id': 0,
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
        self.wallet = Wallet(JSONRPC())
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
        self.assertEqual(len(self.wallet.accounts[0].get_addresses()), 8)
