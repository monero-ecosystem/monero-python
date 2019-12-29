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
    argsparser.add_argument('-p', dest='proxy_url', nargs='?', type=str, default=None, help="Proxy URL")
    argsparser.add_argument('-t', dest='timeout', type=int, default=30, help="Request timeout")
    argsparser.add_argument('-v', dest='verbosity', action='count', default=0,
        help="Verbosity (repeat to increase; -v for INFO, -vv for DEBUG")
    args = argsparser.parse_args()
    level = logging.WARNING
    if args.verbosity == 1:
        level = logging.INFO
    elif args.verbosity > 1:
        level = logging.DEBUG
    logging.basicConfig(level=level, format="%(asctime)-15s %(message)s")
    return Daemon(JSONRPCDaemon(timeout=args.timeout, proxy_url=args.proxy_url, **args.daemon_rpc_url))

d = get_daemon()
info = d.info()
print("Net: {net:>15s}net\n"
    "Height:      {height:10d}\n"
    "Difficulty:  {difficulty:10d}\n"
    "Alt blocks:  {alt_blocks_count:10d}\n".format(
        net='test' if info['testnet'] \
            else 'stage' if info['stagenet'] \
            else 'main' if info['mainnet'] else 'unknown',
        **info))
print("Last 6 blocks:")
for hdr in reversed(d.headers(info['height']-6, info['height']-1)):
    print("{height:10d} {hash} {block_size_kb:6.2f} kB {num_txes:3d} txn(s) "
        "v{major_version:d}".format(
            block_size_kb=hdr['block_size']/1024.0, **hdr))
mempool = d.mempool()
if mempool:
    print("\n{:d} txn(s) in mempool:".format(len(mempool)))
    for tx in d.mempool():
        print("{:>10s} {:s}".format(tx.timestamp.strftime("%H:%M:%S"), tx.hash))
else:
    print("\nMempool is empty")
