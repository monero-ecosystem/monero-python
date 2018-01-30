from datetime import datetime
from decimal import Decimal
import unittest

from monero.address import address
from monero.numbers import PaymentID
from monero.transaction import IncomingPayment, OutgoingPayment, Transaction

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

    def test_hash(self):
        self.assertIn(
            'a0b876ebcf7c1d499712d84cedec836f9d50b608bb22d6cb49fd2feae3ffed14',
            repr(self.tx1))
        self.assertIn(
            'a0b876ebcf7c1d499712d84cedec836f9d50b608bb22d6cb49fd2feae3ffed14',
            repr(self.pm1))
