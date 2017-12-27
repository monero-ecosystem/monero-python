from decimal import Decimal
import sys

PICONERO = Decimal('0.000000000001')

if sys.version_info < (3,):
    _integer_types = (int, long,)
else:
    _integer_types = (int,)


def to_atomic(amount):
    """Convert Monero decimal to atomic integer of piconero."""
    return int(amount * 10**12)

def from_atomic(amount):
    """Convert atomic integer of piconero to Monero decimal."""
    return (Decimal(amount) * PICONERO).quantize(PICONERO)

def as_monero(amount):
    """Return the amount rounded to maximal Monero precision."""
    return Decimal(amount).quantize(PICONERO)

def payment_id_as_int(payment_id):
    if isinstance(payment_id, (bytes, str)):
        payment_id = int(payment_id, 16)
    elif not isinstance(payment_id, _integer_types):
        raise TypeError("payment_id must be either int or hexadecimal str or bytes, "
            "is %r" % payment_id)
    return payment_id
