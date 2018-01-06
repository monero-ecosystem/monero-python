from decimal import Decimal
import sys

PICONERO = Decimal('0.000000000001')

if sys.version_info < (3,):
    _integer_types = (int, long,)
    _str_types = (str, bytes, unicode)
else:
    _integer_types = (int,)
    _str_types = (str, bytes)


def to_atomic(amount):
    """Convert Monero decimal to atomic integer of piconero."""
    return int(amount * 10**12)

def from_atomic(amount):
    """Convert atomic integer of piconero to Monero decimal."""
    return (Decimal(amount) * PICONERO).quantize(PICONERO)

def as_monero(amount):
    """Return the amount rounded to maximal Monero precision."""
    return Decimal(amount).quantize(PICONERO)


class PaymentID(object):
    _payment_id = None

    def __init__(self, payment_id):
        if isinstance(payment_id, PaymentID):
            payment_id = int(payment_id)
        if isinstance(payment_id, _str_types):
            payment_id = int(payment_id, 16)
        elif not isinstance(payment_id, _integer_types):
            raise TypeError("payment_id must be either int or hexadecimal str or bytes, "
                "is %r" % payment_id)
        self._payment_id = payment_id

    def is_short(self):
        """Returns True if payment ID is short enough to be included
        in Integrated Address."""
        return self._payment_id.bit_length() <= 64

    def __repr__(self):
        if self.is_short():
            return "{:016x}".format(self._payment_id)
        return "{:064x}".format(self._payment_id)

    def __int__(self):
        return self._payment_id

    def __eq__(self, other):
        if isinstance(other, PaymentID):
            return int(self) == int(other)
        elif isinstance(other, _integer_types):
            return int(self) == other
        elif isinstance(other, _str_types):
            return str(self) == other
        return super()
