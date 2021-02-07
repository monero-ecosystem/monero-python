from datetime import datetime
from decimal import Decimal
from operator import attrgetter
import random
import unittest

from monero.address import address
from monero.numbers import PaymentID
from monero.transaction import IncomingPayment, Transaction, Output, _ByHeight
from monero import exceptions

class FiltersTestCase(unittest.TestCase):
    def setUp(self):
        self.tx1 = Transaction(
            timestamp=datetime(2018, 1, 29, 15, 0, 25),
            height=1087606,
            hash='a0b876ebcf7c1d499712d84cedec836f9d50b608bb22d6cb49fd2feae3ffed14',
            fee=Decimal('0.00352891'))
        self.pm1 = IncomingPayment(
            amount=Decimal('1'),
            local_address=address('Bf6ngv7q2TBWup13nEm9AjZ36gLE6i4QCaZ7XScZUKDUeGbYEHmPRdegKGwLT8tBBK7P6L32RELNzCR6QzNFkmogDjvypyV'),
            payment_id=PaymentID('0166d8da6c0045c51273dd65d6f63734beb8a84e0545a185b2cfd053fced9f5d'),
            transaction=self.tx1)

        # setup for one-time output tests
        self.json1 = { # Actual as_json response from TX ee5bcb6430c39757ff27f8d607287572f3956a0ee16bb1d2378891f93746c8f9
            'version': 2, 'unlock_time': 0, 'vin': [{'key': {'amount': 0, 'key_offsets': 
            [25471133, 261981, 36602, 18967, 13096, 16260, 54279, 3105, 5403, 786, 555],
            'k_image': '4b48346e954a74be9a334b03cadf8aa020542d201fb6ae7416246d19fd04fdb7'}}],
            'vout': [{'amount': 0, 'target': {'key': 'c55e793b4d673dcf73587e5141b777ef24e255d48826c75ce110ffc23ff762b9'}},
            {'amount': 0, 'target': {'key': '93b263454cd3cc349245ad60c9c248332b885a1f2d7b5792cfc24fd87434d62a'}}],
            'extra': [1, 209, 170, 43, 245, 190, 68, 82, 131, 116, 79, 134, 175, 104, 216, 127, 99, 49, 127, 141, 255, 65, 204, 101,
            81, 244, 111, 253, 155, 75, 111, 14, 159, 2, 9, 1, 24, 56, 108, 94, 20, 88, 150, 94], 'rct_signatures': {'type': 5,
            'txnFee': 58560000, 'ecdhInfo': [{'amount': '6c13cf459cb9ed96'}, {'amount': '373bc40c7f600bf4'}], 'outPk':
            ['80521a77ebe954a5daa6f14b13cc74337f999bc68177a58e76f768c18f2fa421',
            '5997e64b90d59f7f810ddbc801f747c4fa43e2de593e4ea48531e16d776c00fd']}}
        self.outind1 = [25884175, 25884176]
        self.tx2 = Transaction(json=self.json1, output_indices=self.outind1)
        self.oto1 = Output(index=25973289, amount=Decimal('0.000000000000'))
        self.oto2 = Output(pubkey='0faff18f7149a0db5aa0dc3c9116887740ccbb5dc4d1eeff87895288e55e5052')

    def test_hash(self):
        self.assertIn(
            'a0b876ebcf7c1d499712d84cedec836f9d50b608bb22d6cb49fd2feae3ffed14',
            repr(self.tx1))
        self.assertIn(
            'a0b876ebcf7c1d499712d84cedec836f9d50b608bb22d6cb49fd2feae3ffed14',
            repr(self.pm1))

    def test_outputs(self):
        out1, out2 = self.tx2.outputs()
        self.assertEqual(out1.transaction, self.tx2)
        self.assertEqual(out2.transaction, self.tx2)
        self.assertIn(self.json1['vout'][0]['target']['key'], repr(out1))
        self.assertFalse(out2 != Output(stealth_address=self.json1['vout'][1]['target']['key']))
        self.assertIn('(index=25973289,amount=0E-12)', repr(self.oto1))
        self.assertEqual(self.oto1, Output(index=25973289, amount=Decimal('0.000000000000')))

        with self.assertRaises(exceptions.TransactionWithoutJSON):
            self.tx1.outputs()

        with self.assertRaises(TypeError):
            self.oto1 == self.oto2


class SortingTestCase(unittest.TestCase):
    def test_sorting(self):
        pmts = [
            IncomingPayment(transaction=Transaction(height=10)),
            IncomingPayment(transaction=Transaction(height=12)),
            IncomingPayment(transaction=Transaction(height=13)),
            IncomingPayment(transaction=Transaction(height=None)),
            IncomingPayment(transaction=Transaction(height=100)),
            IncomingPayment(transaction=Transaction(height=None)),
            IncomingPayment(transaction=Transaction(height=1))
        ]
        for i in range(1680):    # 1/3 of possible permutations
            sorted_pmts = sorted(pmts, key=_ByHeight)
            self.assertEqual(
                list(map(attrgetter('height'), map(attrgetter('transaction'), sorted_pmts))),
                [None, None, 100, 13, 12, 10, 1])
            random.shuffle(pmts)

