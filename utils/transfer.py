#!/usr/bin/python
import argparse
from decimal import Decimal
import operator
import logging
import os
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
argsparser.add_argument('wallet_rpc_url', nargs='?', type=url_data, default='127.0.0.1:18082',
    help="Wallet RPC URL [user[:password]@]host[:port]")
argsparser.add_argument('-t', dest='timeout', type=int, default=30, help="Request timeout")
argsparser.add_argument('-a', dest='account', default=0, type=int, help="Source account index")
argsparser.add_argument('-p', dest='prio',
    choices=['unimportant', 'normal', 'elevated', 'priority'],
    default='normal')
argsparser.add_argument('-i', dest='payment_id', nargs='?', type=PaymentID,
    const=PaymentID(random.randint(0, 2**256)),
    help="Payment ID")
argsparser.add_argument('--save', dest='outdir', nargs='?', default=None, const='.',
    help="Save to file, optionally follow by destination directory (default is .)\n"
        "Transaction will be not relayed to the network.")
argsparser.add_argument('destinations', metavar='address:amount', nargs='+', type=destpair,
    help="Destination address and amount (one or more pairs)")
args = argsparser.parse_args()
prio = getattr(monero.const, "PRIO_{:s}".format(args.prio.upper()))

level = logging.WARNING
if args.verbosity == 1:
    level = logging.INFO
elif args.verbosity > 1:
    level = logging.DEBUG
logging.basicConfig(level=level, format="%(asctime)-15s %(message)s")

w = Wallet(JSONRPCWallet(timeout=args.timeout, **args.wallet_rpc_url))
txns = w.accounts[args.account].transfer_multiple(
    args.destinations, priority=prio, payment_id=args.payment_id,
    relay=args.outdir is None)
for tx in txns:
    print(u"Transaction {hash}:\nfee: {fee:21.12f}\n"
       u"Tx key:     {key}\nSize:       {size} B".format(
            hash=tx.hash, fee=tx.fee,
            key=tx.key, size=len(tx.blob) >> 1))
    if args.outdir:
        outname = os.path.join(args.outdir, tx.hash + '.tx')
        outfile = open(outname, 'wb')
        outfile.write(tx.blob)
        outfile.close()
        print(u"Transaction saved to {}".format(outname))
