import argparse
from decimal import Decimal
import logging
import operator
import random
import re

from monero.backends.jsonrpc import JSONRPCWallet
from monero import exceptions
from monero import Address, Wallet, as_monero

def url_data(url):
    gs = re.compile(
        r'^(?:(?P<user>[a-z0-9_-]+)?(?::(?P<password>[^@]+))?@)?(?P<host>[^:\s]+)(?::(?P<port>[0-9]+))?$'
        ).match(url).groupdict()
    return dict(filter(operator.itemgetter(1), gs.items()))

def get_wallet():
    argsparser = argparse.ArgumentParser(description="Display wallet contents")
    argsparser.add_argument('daemon_url', nargs='?', type=url_data, default='127.0.0.1:18082',
        help="Daemon URL [user[:password]@]host[:port]")
    argsparser.add_argument('-v', dest='verbosity', action='count', default=0,
        help="Verbosity (repeat to increase; -v for INFO, -vv for DEBUG")
    args = argsparser.parse_args()
    level = logging.WARNING
    if args.verbosity == 1:
        level = logging.INFO
    elif args.verbosity > 1:
        level = logging.DEBUG
    logging.basicConfig(level=level, format="%(asctime)-15s %(message)s")
    return Wallet(JSONRPCWallet(**args.daemon_url))

_TXHDR = "timestamp         height  id/hash                                                     " \
    "         amount         fee           payment_id       {dir}"

def tx2str(tx):
    return "{time} {height} {hash} {amount:17.12f} {fee:13.12f} {payment_id} {addr}".format(
        time=tx.timestamp.strftime("%d-%m-%y %H:%M:%S") if getattr(tx, 'timestamp', None) else None,
        height=tx.height,
        hash=tx.hash,
        amount=tx.amount,
        fee=tx.fee or 0,
        payment_id=tx.payment_id,
        addr=getattr(tx, 'local_address', None) or '')

w = get_wallet()
print(
    "Master address: {addr}\n" \
    "Balance: {total:16.12f} ({unlocked:16.12f} unlocked)".format(
        addr=w.get_address(),
        total=w.get_balance(),
        unlocked=w.get_balance(unlocked=True)))

if len(w.accounts) > 1:
    print("\nWallet has {num} account(s):".format(num=len(w.accounts)))
    for acc in w.accounts:
        print("\nAccount {idx:02d}:".format(idx=acc.index))
        print("Balance: {total:16.12f} ({unlocked:16.12f} unlocked)".format(
            total=acc.get_balance(),
            unlocked=acc.get_balance(unlocked=True)))
        addresses = acc.get_addresses()
        print("{num:2d} address(es):".format(num=len(addresses)))
        print("\n".join(map(str, addresses)))
        ins = acc.get_transactions_in()
        if ins:
            print("\nIncoming transactions:")
            print(_TXHDR.format(dir='received by'))
            for tx in ins:
                print(tx2str(tx))
        outs = acc.get_transactions_out()
        if outs:
            print("\nOutgoing transactions:")
            print(_TXHDR.format(dir='sent from'))
            for tx in outs:
                print(tx2str(tx))
else:
    ins = w.get_transactions_in()
    if ins:
        print("\nIncoming transactions:")
        print(_TXHDR.format(dir='received by'))
        for tx in ins:
            print(tx2str(tx))
    outs = w.get_transactions_out()
    if outs:
        print("\nOutgoing transactions:")
        print(_TXHDR.format(dir='sent from'))
        for tx in outs:
            print(tx2str(tx))
