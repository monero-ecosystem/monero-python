import argparse
from decimal import Decimal
import logging
import operator
import random
import re

from monero.backends.jsonrpc import JSONRPCWallet
from monero import exceptions
from monero.address import Address
from monero.numbers import as_monero
from monero.wallet import Wallet

def url_data(url):
    gs = re.compile(
        r'^(?:(?P<user>[a-z0-9_-]+)?(?::(?P<password>[^@]+))?@)?(?P<host>[^:\s]+)(?::(?P<port>[0-9]+))?$'
        ).match(url).groupdict()
    return dict(filter(operator.itemgetter(1), gs.items()))

def get_wallet():
    argsparser = argparse.ArgumentParser(description="Display wallet contents")
    argsparser.add_argument('wallet_rpc_url', nargs='?', type=url_data, default='127.0.0.1:18082',
        help="Wallet RPC URL [user[:password]@]host[:port]")
    argsparser.add_argument('-v', dest='verbosity', action='count', default=0,
        help="Verbosity (repeat to increase; -v for INFO, -vv for DEBUG")
    args = argsparser.parse_args()
    level = logging.WARNING
    if args.verbosity == 1:
        level = logging.INFO
    elif args.verbosity > 1:
        level = logging.DEBUG
    logging.basicConfig(level=level, format="%(asctime)-15s %(message)s")
    return Wallet(JSONRPCWallet(**args.wallet_rpc_url))

_TXHDR = "timestamp         height  id/hash                                                     " \
        "         amount         fee           {dir:95s} payment_id"

def pmt2str(pmt):
    return "{time} {height:7d} {hash} {amount:17.12f} {fee:13.12f} {addr} {payment_id}".format(
        time=pmt.timestamp.strftime("%d-%m-%y %H:%M:%S") if getattr(pmt, 'timestamp', None) else None,
        height=pmt.transaction.height or 0,
        hash=pmt.transaction.hash,
        amount=pmt.amount,
        fee=pmt.transaction.fee or 0,
        payment_id=pmt.payment_id,
        addr=getattr(pmt, 'local_address', None) or '')

def a2str(a):
    return "{addr} {label}".format(
        addr=a,
        label=a.label or "")

w = get_wallet()
masteraddr = w.get_address()
print(
    "Master address: {addr}\n" \
    "Balance: {total:16.12f} ({unlocked:16.12f} unlocked)".format(
        addr=a2str(masteraddr),
        total=w.get_balance(),
        unlocked=w.get_balance(unlocked=True)))
print(
    "Keys:\n" \
    "  private view:  {svk}\n" \
    "  public spend:  {psk}\n" \
    "  public view:   {pvk}\n\n" \
    "Seed:\n{seed}".format(
        svk=w.get_view_key(),
        psk=masteraddr.get_spend_key(),
        pvk=masteraddr.get_view_key(),
        seed=w.get_seed()
        ))

if len(w.accounts) > 1:
    print("\nWallet has {num} account(s):".format(num=len(w.accounts)))
    for acc in w.accounts:
        print("\nAccount {idx:02d}:".format(idx=acc.index))
        print("Balance: {total:16.12f} ({unlocked:16.12f} unlocked)".format(
            total=acc.get_balance(),
            unlocked=acc.get_balance(unlocked=True)))
        addresses = acc.get_addresses()
        print("{num:2d} address(es):".format(num=len(addresses)))
        print("\n".join(map(a2str, addresses)))
        ins = acc.get_transactions_in(unconfirmed=True)
        if ins:
            print("\nIncoming transactions:")
            print(_TXHDR.format(dir='received by'))
            for tx in ins:
                print(pmt2str(tx))
        outs = acc.get_transactions_out(unconfirmed=True)
        if outs:
            print("\nOutgoing transactions:")
            print(_TXHDR.format(dir='sent from'))
            for tx in outs:
                print(pmt2str(tx))
else:
    ins = w.get_transactions_in(unconfirmed=True)
    if ins:
        print("\nIncoming transactions:")
        print(_TXHDR.format(dir='received by'))
        for tx in ins:
            print(pmt2str(tx))
    outs = w.get_transactions_out(unconfirmed=True)
    if outs:
        print("\nOutgoing transactions:")
        print(_TXHDR.format(dir='sent from'))
        for tx in outs:
            print(pmt2str(tx))
