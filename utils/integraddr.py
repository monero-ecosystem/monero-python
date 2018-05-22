#!/usr/bin/python
import sys
from monero.address import address
from monero.numbers import PaymentID

USAGE = "{0} <address> <payment_id>"

try:
    addr = address(sys.argv[1])
    pid = PaymentID(sys.argv[2])
except IndexError:
    print(USAGE.format(*sys.argv), file=sys.stderr)
    sys.exit(-1)

print(addr.with_payment_id(pid))
