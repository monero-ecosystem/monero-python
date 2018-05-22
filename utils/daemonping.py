#!/usr/bin/python
import argparse
import logging
import operator
import re

from monero.backends.jsonrpc import JSONRPCDaemon
from monero.daemon import Daemon

def url_data(url):
    gs = re.compile(
        r'^(?P<host>[^:\s]+)(?::(?P<port>[0-9]+))?$'
        ).match(url).groupdict()
    return dict(filter(operator.itemgetter(1), gs.items()))

def get_daemon():
    argsparser = argparse.ArgumentParser(description="Display daemon info")
    argsparser.add_argument('daemon_rpc_url', nargs='?', type=url_data, default='127.0.0.1:18081',
        help="Daemon RPC URL [host[:port]]")
    argsparser.add_argument('-v', dest='verbosity', action='count', default=0,
        help="Verbosity (repeat to increase; -v for INFO, -vv for DEBUG")
    args = argsparser.parse_args()
    level = logging.WARNING
    if args.verbosity == 1:
        level = logging.INFO
    elif args.verbosity > 1:
        level = logging.DEBUG
    logging.basicConfig(level=level, format="%(asctime)-15s %(message)s")
    return Daemon(JSONRPCDaemon(**args.daemon_rpc_url))

d = get_daemon()
info = d.info()
print("Net: {net:>18s}\n"
    "Height:      {height:10d}\n"
    "Difficulty:  {difficulty:10d}".format(
        net='test' if info['testnet'] else 'live',
        **info))
