import sys
from .address import address
from .numbers import PaymentID

class Payment(object):
    payment_id = None
    amount = None
    timestamp = None
    transaction = None
    address = None

    def __init__(self, **kwargs):
        self.amount = kwargs.get('amount', self.amount)
        self.timestamp = kwargs.get('timestamp', self.timestamp)
        self.payment_id = kwargs.get('payment_id', self.payment_id)
        self.transaction = kwargs.get('transaction', self.transaction)
        self.address = kwargs.get('address', self.address)

    def __repr__(self):
        return "{} {:.12f} id={}".format(self.transaction.hash, self.amount, self.payment_id)


class IncomingPayment(Payment):
    def __repr__(self):
        return "in: {} {:.12f} id={}".format(self.transaction.hash, self.amount, self.payment_id)


class OutgoingPayment(Payment):
    note = ''

    def __init__(self, **kwargs):
        super(OutgoingPayment, self).__init__(**kwargs)
        self.note = kwargs.get('note', self.note)

    def __repr__(self):
        return "out: {} {:.12f} id={}".format(self.transaction.hash, self.amount, self.payment_id)


class Transaction(object):
    hash = None
    fee = None
    height = None
    timestamp = None
    key = None
    blob = None

    def __init__(self, **kwargs):
        self.hash = kwargs.get('hash', self.hash)
        self.fee = kwargs.get('fee', self.fee)
        self.height = kwargs.get('height', self.height)
        self.timestamp = kwargs.get('timestamp', self.timestamp)
        self.key = kwargs.get('key', self.key)
        self.blob = kwargs.get('blob', self.blob)

    def __repr__(self):
        return self.hash


if sys.version_info < (3,):
    _str_types = (str, bytes, unicode)
else:
    _str_types = (str, bytes)


class PaymentManager(object):
    account_idx = 0
    backend = None

    def __init__(self, account_idx, backend, direction):
        self.account_idx = account_idx
        self.backend = backend
        self.direction = direction

    def __call__(self, **filterparams):
        fetch = self.backend.transfers_in if self.direction == 'in' else self.backend.transfers_out
        return fetch(self.account_idx, PaymentFilter(**filterparams))


class PaymentFilter(object):
    def __init__(self, **filterparams):
        self.min_height = filterparams.pop('min_height', None)
        self.max_height = filterparams.pop('max_height', None)
        self.unconfirmed = filterparams.pop('unconfirmed', False)
        self.confirmed = filterparams.pop('confirmed', True)
        _address = filterparams.pop('address', None)
        _payment_id = filterparams.pop('payment_id', None)
        if len(filterparams) > 0:
            raise ValueError("Excessive arguments for payment query: {:r}".format(filterparams))

        if _address is None:
            self.addresses = []
        else:
            if isinstance(_address, _str_types):
                addresses = [_address]
            else:
                try:
                    iter(_address)
                    addresses = _address
                except TypeError:
                    addresses = [_address]
            self.addresses = list(map(address, addresses))
        if _payment_id is None:
            self.payment_ids = []
        else:
            if isinstance(_payment_id, _str_types):
                payment_ids = [_payment_id]
            else:
                try:
                    iter(_payment_id)
                    payment_ids = _payment_id
                except TypeError:
                    payment_ids = [_payment_id]
            self.payment_ids = list(map(PaymentID, payment_ids))

    def check(self, payment):
        ht = payment.transaction.height
        if ht is None:
            if not self.unconfirmed:
                return False
            if self.min_height is not None or self.max_height is not None:
                # mempool txns are filtered out if any height range check is present
                return False
        else:
            if not self.confirmed:
                return False
            if self.min_height is not None and ht < self.min_height:
                return False
            if self.max_height is not None and ht > self.max_height:
                return False
        if self.payment_ids and payment.payment_id not in self.payment_ids:
            return False
        if self.addresses and payment.address not in self.addresses:
            return False
        return True

    def filter(self, payments):
        return filter(self.check, payments)
