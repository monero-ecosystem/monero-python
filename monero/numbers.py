from decimal import Decimal

PICONERO = Decimal('0.000000000001')

def to_atomic(amount):
    """Convert Monero decimal to atomic integer of piconero."""
    return int(amount * 10**12)

def from_atomic(amount):
    """Convert atomic integer of piconero to Monero decimal."""
    return (Decimal(amount) * PICONERO).quantize(PICONERO)

def as_monero(amount):
    """Return the amount rounded to maximal Monero precision."""
    return Decimal(amount).quantize(PICONERO)
