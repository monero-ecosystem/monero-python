from decimal import Decimal

PICONERO = Decimal('0.000000000001')

def to_atomic(amount):
    return int(amount * 10**12)

def from_atomic(amount):
    return (Decimal(amount) * PICONERO).quantize(PICONERO)
