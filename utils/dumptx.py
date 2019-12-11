#!/usr/bin/python
import argparse
import json
import logging
import operator
import re
import sys

from monero.backends.jsonrpc import JSONRPCDaemon
from monero.daemon import Daemon


def url_data(url):
    gs = re.compile(r"^(?P<host>[^:\s]+)(?::(?P<port>[0-9]+))?$").match(url).groupdict()
    return dict(filter(operator.itemgetter(1), gs.items()))


argsparser = argparse.ArgumentParser(
    description="Retrieve transaction(s) from daemon and print them"
)
argsparser.add_argument("tx_id", nargs="+", type=str, help="Transaction id (hash)")
argsparser.add_argument(
    "-d",
    dest="daemon_rpc_url",
    type=url_data,
    default="127.0.0.1:18081",
    help="Daemon RPC URL [host[:port]]",
)
argsparser.add_argument(
    "-t", dest="timeout", type=int, default=30, help="Request timeout"
)
argsparser.add_argument(
    "-v",
    dest="verbosity",
    action="count",
    default=0,
    help="Verbosity (repeat to increase; -v for INFO, -vv for DEBUG",
)
args = argsparser.parse_args()
level = logging.WARNING
if args.verbosity == 1:
    level = logging.INFO
elif args.verbosity > 1:
    level = logging.DEBUG
logging.basicConfig(level=level, format="%(asctime)-15s %(message)s")

d = Daemon(JSONRPCDaemon(timeout=args.timeout, **args.daemon_rpc_url))

txs = list(d.transactions(args.tx_id))
print("Found {:d} transaction(s)".format(len(txs)))
if len(txs) > 0:
    print("-" * 79)
for tx in txs:
    print("id: {:s}".format(tx.hash))
    print(
        "height: {:s}".format("None" if tx.height is None else "{:d}".format(tx.height))
    )
    print("size: {:d}".format(tx.size))
    print("JSON:")
    print(json.dumps(tx.json, indent=2))
    print("-" * 79)
