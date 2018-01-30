import sys
from .address import address
from .numbers import PaymentID

class Payment(object):
    payment_id = None
    amount = None
    timestamp = None
    transaction = None
    local_address = None
    note = ''

    def __init__(self, **kwargs):
        self.amount = kwargs.pop('amount', self.amount)
        self.timestamp = kwargs.pop('timestamp', self.timestamp)
        self.payment_id = kwargs.pop('payment_id', self.payment_id)
        self.transaction = kwargs.pop('transaction', self.transaction)
        self.local_address = kwargs.pop('local_address', self.local_address)
        self.note = kwargs.pop('note', self.note)
        if len(kwargs):
            raise ValueError("Excessive arguments for {}: {}".format(type(self), kwargs))

    def __repr__(self):
        return "{} {:.12f} id={}".format(self.transaction.hash, self.amount, self.payment_id)


class IncomingPayment(Payment):
    def __repr__(self):
        return "in: {} {:.12f} id={}".format(self.transaction.hash, self.amount, self.payment_id)


class OutgoingPayment(Payment):
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
        _local_address = filterparams.pop('local_address', None)
        _payment_id = filterparams.pop('payment_id', None)
        if len(filterparams) > 0:
            raise ValueError("Excessive arguments for payment query: {}".format(filterparams))

        if _local_address is None:
            self.local_addresses = []
        else:
            if isinstance(_local_address, _str_types):
                local_addresses = [_local_address]
            else:
                try:
                    iter(_local_address)
                    local_addresses = _local_address
                except TypeError:
                    local_addresses = [_local_address]
            self.local_addresses = list(map(address, local_addresses))
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
        if self.local_addresses and payment.local_address not in self.local_addresses:
            return False
        return True

    def filter(self, payments):
        return filter(self.check, payments)
