import re
import sys
import warnings
from .address import address
from .numbers import PaymentID

class Payment(object):
    """
    A payment base class, representing payment not associated with any
    :class:`Account <monero.account.Account>`.

    This class is not intended to be turned into objects by the user,
    it is used by backends.
    """
    payment_id = None
    amount = None
    timestamp = None
    transaction = None
    local_address = None
    note = ''

    _reprstr = "{} @ {} {:.12f} id={}"

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
        return self._reprstr.format(
            self.transaction.hash, self.transaction.height or 'pool', self.amount, self.payment_id)


class IncomingPayment(Payment):
    """
    An incoming payment (one that increases the balance of an
    :class:`Account <monero.account.Account>`)
    """
    _reprstr = "in: {} @ {} {:.12f} id={}"


class OutgoingPayment(Payment):
    """
    An outgoing payment (one that decreases the balance of an
    :class:`Account <monero.account.Account>`)
    """
    destinations = None

    def __init__(self, **kwargs):
        self.destinations = kwargs.pop('destinations', [])
        super(OutgoingPayment, self).__init__(**kwargs)

    _reprstr = "out: {} @ {} {:.12f} id={}"


class Transaction(object):
    """
    A Monero transaction. Identified by `hash`, it can be a part of a block of some `height`
    or not yet mined (`height` is `None` then).

    This class is not intended to be turned into objects by the user,
    it is used by backends.
    """
    hash = None
    fee = None
    height = None
    timestamp = None
    key = None
    blob = None
    confirmations = None

    def __init__(self, **kwargs):
        self.hash = kwargs.get('hash', self.hash)
        self.fee = kwargs.get('fee', self.fee)
        self.height = kwargs.get('height', self.height)
        self.timestamp = kwargs.get('timestamp', self.timestamp)
        self.key = kwargs.get('key', self.key)
        self.blob = kwargs.get('blob', self.blob)
        self.confirmations = kwargs.get('confirmations', self.confirmations)

    def __repr__(self):
        return self.hash


if sys.version_info < (3,): # pragma: no cover
    _str_types = (str, bytes, unicode)
else:                       # pragma: no cover
    _str_types = (str, bytes)


class PaymentManager(object):
    """
    A payment query manager, handling either incoming or outgoing payments of
    an :class:`Account <monero.account.Account>`.

    This class is not intended to be turned into objects by the user,
    it is used by backends.
    """
    account_idx = 0
    backend = None

    def __init__(self, account_idx, backend, direction):
        self.account_idx = account_idx
        self.backend = backend
        self.direction = direction

    def __call__(self, **filterparams):
        fetch = self.backend.transfers_in if self.direction == 'in' else self.backend.transfers_out
        return fetch(self.account_idx, PaymentFilter(**filterparams))


def _validate_tx_id(txid):
    if not bool(re.compile('^[0-9a-f]{64}$').match(txid)):
        raise ValueError("Transaction ID must be a 64-character hexadecimal string, not "
            "'{}'".format(txid))
    return txid


class _ByHeight(object):
    """A helper class used as key in sorting of payments by height.
    Mempool goes on top, blockchain payments are ordered with descending block numbers.

    **WARNING:** Integer sorting is reversed here.
    """
    def __init__(self, pmt):
        self.pmt = pmt
    def _cmp(self, other):
        sh = self.pmt.transaction.height
        oh = other.pmt.transaction.height
        if sh is oh is None:
            return 0
        if sh is None:
            return 1
        if oh is None:
            return -1
        return (sh > oh) - (sh < oh)
    def __lt__(self, other):
        return self._cmp(other) > 0
    def __le__(self, other):
        return self._cmp(other) >= 0
    def __eq__(self, other):
        return self._cmp(other) == 0
    def __ge__(self, other):
        return self._cmp(other) <= 0
    def __gt__(self, other):
        return self._cmp(other) < 0
    def __ne__(self, other):
        return self._cmp(other) != 0


class PaymentFilter(object):
    """
    A helper class that filters payments retrieved by the backend.

    This class is not intended to be turned into objects by the user,
    it is used by backends.
    """
    def __init__(self, **filterparams):
        self.min_height = filterparams.pop('min_height', None)
        self.max_height = filterparams.pop('max_height', None)
        self.unconfirmed = filterparams.pop('unconfirmed', False)
        self.confirmed = filterparams.pop('confirmed', True)
        _local_address = filterparams.pop('local_address', None)
        _tx_id = filterparams.pop('tx_id', None)
        _payment_id = filterparams.pop('payment_id', None)
        if len(filterparams) > 0:
            raise ValueError("Excessive arguments for payment query: {}".format(filterparams))
        if self.unconfirmed and (self.min_height is not None or self.max_height is not None):
            warnings.warn("Height filtering (min_height/max_height) has been requested while "
                    "also asking for unconfirmed transactions. These are mutually exclusive. "
                    "As mempool transactions have no height at all, they will be excluded "
                    "from the result.",
                    RuntimeWarning)
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
        if _tx_id is None:
            self.tx_ids = []
        else:
            if isinstance(_tx_id, _str_types):
                tx_ids = [_tx_id]
            else:
                try:
                    iter(_tx_id)
                    tx_ids = _tx_id
                except TypeError:
                    tx_ids = [_tx_id]
            self.tx_ids = list(map(_validate_tx_id, tx_ids))
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
        if self.tx_ids and payment.transaction.hash not in self.tx_ids:
            return False
        if self.local_addresses and payment.local_address not in self.local_addresses:
            return False
        return True

    def filter(self, payments):
        return sorted(
            filter(self.check, payments),
            key=_ByHeight)
