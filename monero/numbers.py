from decimal import Decimal

PICONERO = Decimal("0.000000000001")
EMPTY_KEY = "0" * 64


def to_atomic(amount):
    """Convert Monero decimal to atomic integer of piconero."""
    if not isinstance(amount, (Decimal, int, float)):
        raise ValueError(
            "Amount '{}' doesn't have numeric type. Only Decimal, int, long and "
            "float (not recommended) are accepted as amounts.".format(amount)
        )
    return int(amount * 10**12)


def from_atomic(amount):
    """Convert atomic integer of piconero to Monero decimal."""
    return (Decimal(amount) * PICONERO).quantize(PICONERO)


def as_monero(amount):
    """Return the amount rounded to maximal Monero precision."""
    return Decimal(amount).quantize(PICONERO)


class PaymentID(object):
    """
    A class that validates Monero payment ID.

    Payment IDs can be used as str or int across the module, however this class
    offers validation as well as simple conversion and comparison to those two
    primitive types.

    :param payment_id: the payment ID as integer or hexadecimal string
    """

    _payment_id = None

    def __init__(self, payment_id):
        if isinstance(payment_id, PaymentID):
            payment_id = int(payment_id)
        if isinstance(payment_id, str):
            payment_id = int(payment_id, 16)
        elif not isinstance(payment_id, int):
            raise TypeError(
                "payment_id must be either int or hexadecimal str or bytes, "
                "is {0}".format(type(payment_id))
            )
        if payment_id.bit_length() > 256:
            raise ValueError(
                "payment_id {0} is more than 256 bits long".format(payment_id)
            )
        self._payment_id = payment_id

    def is_short(self):
        """Returns True if payment ID is short enough to be included
        in :class:`IntegratedAddress <monero.address.IntegratedAddress>`."""
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
        elif isinstance(other, int):
            return int(self) == other
        elif isinstance(other, str):
            return str(self) == other
        return super(PaymentID, self).__eq__(other)
