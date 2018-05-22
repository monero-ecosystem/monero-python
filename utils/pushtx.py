#!/usr/bin/python
import argparse
import logging
import operator
import re
import sys

from monero.backends.jsonrpc import JSONRPCDaemon
from monero.daemon import Daemon
from monero.transaction import Transaction
from monero import exceptions

def url_data(url):
    gs = re.compile(
        r'^(?P<host>[^:\s]+)(?::(?P<port>[0-9]+))?$'
        ).match(url).groupdict()
    return dict(filter(operator.itemgetter(1), gs.items()))

argsparser = argparse.ArgumentParser(description="Push transaction to network")
argsparser.add_argument('daemon_rpc_url', nargs='?', type=url_data, default='127.0.0.1:18081',
    help="Daemon RPC URL [host[:port]]")
argsparser.add_argument('-v', dest='verbosity', action='count', default=0,
    help="Verbosity (repeat to increase; -v for INFO, -vv for DEBUG")
argsparser.add_argument('-i', dest='tx_filenames', nargs='+', default=None,
    help="Files with transaction data. Will read from stdin if not given.")
argsparser.add_argument('--no-relay', dest='relay', action='store_false',
    help="Do not relay the transaction (it will stay at the node unless mined or expired)")
args = argsparser.parse_args()
level = logging.WARNING
if args.verbosity == 1:
    level = logging.INFO
elif args.verbosity > 1:
    level = logging.DEBUG
logging.basicConfig(level=level, format="%(asctime)-15s %(message)s")
if args.tx_filenames:
    blobs = [(f, open(f, 'r').read()) for f in args.tx_filenames]
else:
    blobs = [('transaction', sys.stdin.read())]
d = Daemon(JSONRPCDaemon(**args.daemon_rpc_url))
for name, blob in blobs:
    logging.debug("Sending {}".format(name))
    tx = Transaction(blob=blob)
    try:
        res = d.send_transaction(tx, relay=args.relay)
    except exceptions.TransactionBroadcastError as e:
        print("{} not sent, reason: {}".format(name, e.details['reason']))
        logging.debug(e.details)
        continue
    if res['not_relayed']:
        print("{} not relayed".format(name))
    else:
        print("{} successfully sent".format(name))
