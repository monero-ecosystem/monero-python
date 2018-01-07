import argparse
from decimal import Decimal
import operator
import logging
import random
import re

import monero
from monero.address import address
from monero.numbers import PaymentID, as_monero
from monero.wallet import Wallet
from monero.backends.jsonrpc import JSONRPCWallet

def url_data(url):
    gs = re.compile(
        r'^(?:(?P<user>[a-z0-9_-]+)?(?::(?P<password>[^@]+))?@)?(?P<host>[^:\s]+)(?::(?P<port>[0-9]+))?$'
        ).match(url).groupdict()
    return dict(filter(operator.itemgetter(1), gs.items()))

def destpair(s):
    addr, amount = s.split(':')
    return (address(addr), as_monero(amount))

argsparser = argparse.ArgumentParser(description="Transfer Monero")
argsparser.add_argument('-v', dest='verbosity', action='count', default=0,
    help="Verbosity (repeat to increase; -v for INFO, -vv for DEBUG")
argsparser.add_argument('daemon_url', nargs='?', type=url_data, default='127.0.0.1:18082',
    help="Daemon URL [user[:password]@]host[:port]")
argsparser.add_argument('-a', dest='account', default=0, type=int, help="Source account index")
argsparser.add_argument('-p', dest='prio',
    choices=['unimportant', 'normal', 'elevated', 'priority'],
    default='normal')
argsparser.add_argument('-r', dest='ring_size', type=int, default=5, help="Ring size")
argsparser.add_argument('-i', dest='payment_id', nargs='?', type=PaymentID, default=0,
    help="Payment ID")
argsparser.add_argument('destinations', metavar='address:amount', nargs='+', type=destpair,
    help="Destination address and amount (one or more pairs)")
args = argsparser.parse_args()
prio = getattr(monero.prio, args.prio.upper())
payment_id = PaymentID(random.randint(0, 2**256)) if args.payment_id is None else args.payment_id

level = logging.WARNING
if args.verbosity == 1:
    level = logging.INFO
elif args.verbosity > 1:
    level = logging.DEBUG
logging.basicConfig(level=level, format="%(asctime)-15s %(message)s")

w = Wallet(JSONRPCWallet(**args.daemon_url))
txfrs = w.accounts[args.account].transfer_multiple(
    args.destinations, priority=prio, mixin=args.ring_size, payment_id=payment_id)
for tx in txfrs:
    print(u"Transaction {hash}:\nXMR: {amount:21.12f} @ {fee:13.12f} fee\n"
       u"Payment ID: {payment_id}\nTx key:     {key}\nSize:       {size} B".format(
            hash=tx.hash, amount=tx.amount, fee=tx.fee,
            payment_id=tx.payment_id, key=tx.key, size=len(tx.blob) >> 1))
