from datetime import datetime
from decimal import Decimal
import unittest
try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock

from monero.wallet import Wallet
from monero.address import Address
from monero.transaction import IncomingPayment, OutgoingPayment, Transaction
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
        for pmt in pay_in:
            self.assertIsInstance(pmt, IncomingPayment)
# Once PR#3010 has been merged to Monero, update the JSON and enable the following:
#            self.assertIsInstance(pmt.received_by, Address)
            self.assertIsInstance(pmt.amount, Decimal)
            self.assertIsInstance(pmt.transaction, Transaction)
            self.assertIsInstance(pmt.transaction.fee, Decimal)
            self.assertIsInstance(pmt.transaction.height, int)

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
        for pmt in pay_out:
            self.assertIsInstance(pmt, OutgoingPayment)
# Once PR#3010 has been merged to Monero, update the JSON and enable the following:
#            self.assertIsInstance(pmt.sent_from, Address)
            self.assertIsInstance(pmt.amount, Decimal)
            self.assertIsInstance(pmt.timestamp, datetime)
            self.assertIsInstance(pmt.transaction, Transaction)
            self.assertIsInstance(pmt.transaction.fee, Decimal)
            self.assertIsInstance(pmt.transaction.height, int)

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
        for pmt in payments:
            self.assertIsInstance(pmt, IncomingPayment)
            self.assertIsInstance(pmt.received_by, Address)
            self.assertIsInstance(pmt.amount, Decimal)
            self.assertIsInstance(pmt.transaction, Transaction)
            self.assertIsInstance(pmt.transaction.height, int)

    @patch('monero.backends.jsonrpc.requests.post')
    def test_send_transfer(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = self.get_accounts_result
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
