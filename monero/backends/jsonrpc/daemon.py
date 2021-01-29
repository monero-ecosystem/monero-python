from __future__ import unicode_literals
import binascii
from datetime import datetime
import json
import logging
import requests
import six

from ... import exceptions
from ...block import Block
from ...const import NET_MAIN, NET_TEST, NET_STAGE
from ...numbers import from_atomic
from ...transaction import Transaction
from .exceptions import RPCError, Unauthorized


_log = logging.getLogger(__name__)


RESTRICTED_MAX_TRANSACTIONS = 100


class JSONRPCDaemon(object):
    """
    JSON RPC backend for Monero daemon

    :param protocol: `http` or `https`
    :param host: host name or IP
    :param port: port number
    :param path: path for JSON RPC requests (should not be changed)
    :param timeout: request timeout
    :param verify_ssl_certs: verify SSL certificates when connecting
    :param proxy_url: a proxy to use
    :param prune_transactions: whether to prune transaction data. Saves bandwidth but you may want
                            to enable it when you need to retrieve transaction binary blobs.
    """

    _net = None

    def __init__(self, protocol='http', host='127.0.0.1', port=18081, path='/json_rpc',
            user='', password='', timeout=30, verify_ssl_certs=True, proxy_url=None,
            prune_transactions=True):
        self.url = '{protocol}://{host}:{port}'.format(
                protocol=protocol,
                host=host,
                port=port)
        _log.debug("JSONRPC daemon backend URL: {url}".format(url=self.url))
        self.user = user
        self.password = password
        self.timeout = timeout
        self.verify_ssl_certs = verify_ssl_certs
        self.proxies = {protocol: proxy_url}
        self.prune_transactions = prune_transactions

    def _set_net(self, info):
        if info['mainnet']:
            self._net = NET_MAIN
        if info['testnet']:
            self._net = NET_TEST
        if info['stagenet']:
            self._net = NET_STAGE

    def info(self):
        info = self.raw_jsonrpc_request('get_info')
        self._set_net(info)
        return info

    def net(self):
        if self._net:
            return self._net
        self.info()
        return self._net

    def send_transaction(self, blob, relay=True):
        res = self.raw_request('/sendrawtransaction', {
            'tx_as_hex': six.ensure_text(binascii.hexlify(blob)),
            'do_not_relay': not relay})
        if res['status'] == 'OK':
            return res
        raise exceptions.TransactionBroadcastError(
                "{status}: {reason}".format(**res),
                details=res)

    def mempool(self):
        res = self.raw_request('/get_transaction_pool', {})
        txs = []
        for tx in res.get('transactions', []):
            txs.append(Transaction(
                hash=tx['id_hash'],
                fee=from_atomic(tx['fee']),
                timestamp=datetime.fromtimestamp(tx['receive_time']),
                blob=binascii.unhexlify(tx['tx_blob']),
                json=json.loads(tx['tx_json']),
                confirmations=0))
        return txs

    def headers(self, start_height, end_height=None):
        end_height = end_height or start_height
        res = self.raw_jsonrpc_request('get_block_headers_range', {
                'start_height': start_height,
                'end_height': end_height})
        if res['status'] == 'OK':
            return res['headers']
        raise exceptions.BackendException(res['status'])

    def block(self, bhash=None, height=None):
        data = {}
        if bhash:
            data['hash'] = bhash
        if height:
            data['height'] = height
        res = self.raw_jsonrpc_request('get_block', data)
        if res['status'] == 'OK':
            bhdr = res['block_header']
            sub_json = json.loads(res['json'])
            data = {
                'blob': res['blob'],
                'hash': bhdr['hash'],
                'height': bhdr['height'],
                'timestamp': datetime.fromtimestamp(bhdr['timestamp']),
                'version': (bhdr['major_version'], bhdr['minor_version']),
                'difficulty': bhdr['difficulty'],
                'nonce': bhdr['nonce'],
                'orphan': bhdr['orphan_status'],
                'prev_hash': bhdr['prev_hash'],
                'reward': from_atomic(bhdr['reward']),
                'transactions': self.transactions(
                    [bhdr['miner_tx_hash']] + sub_json['tx_hashes']),
            }
            return Block(**data)
        raise exceptions.BackendException(res['status'])

    def transactions(self, hashes):
        """
        Returns a list of transactions for given hashes. Automatically chunks the request
        into amounts acceptable by a restricted RPC server.
        """
        hashes = list(hashes)
        result = []
        while len(hashes):
            result.extend(
                self._do_get_transactions(
                    hashes[:RESTRICTED_MAX_TRANSACTIONS],
                    prune=self.prune_transactions))
            hashes = hashes[RESTRICTED_MAX_TRANSACTIONS:]
        return result

    def _do_get_transactions(self, hashes, prune):
        res = self.raw_request('/get_transactions', {
                'txs_hashes': hashes,
                'decode_as_json': True,
                'prune': prune})
        if res['status'] != 'OK':
            raise exceptions.BackendException(res['status'])
        txs = []
        for tx in res.get('txs', []):
            as_json = json.loads(tx['as_json'])
            fee = as_json.get('rct_signatures', {}).get('txnFee')
            txs.append(Transaction(
                hash=tx['tx_hash'],
                fee=from_atomic(fee) if fee else None,
                height=None if tx['in_pool'] else tx['block_height'],
                timestamp=datetime.fromtimestamp(
                    tx['block_timestamp']) if 'block_timestamp' in tx else None,
                blob=binascii.unhexlify(tx['as_hex']) or None,
                output_indices=None if tx['in_pool'] else tx['output_indices'],
                json=as_json))
        return txs

    def raw_request(self, path, data):
        hdr = {'Content-Type': 'application/json'}
        _log.debug(u"Request: {path}\nData: {data}".format(
            path=path,
            data=json.dumps(data, indent=2, sort_keys=True)))
        auth = requests.auth.HTTPDigestAuth(self.user, self.password)
        rsp = requests.post(
            self.url + path, headers=hdr, data=json.dumps(data), auth=auth,
            timeout=self.timeout, verify=self.verify_ssl_certs, proxies=self.proxies)
        if rsp.status_code != 200:
            raise RPCError("Invalid HTTP status {code} for path {path}.".format(
                code=rsp.status_code,
                path=path))
        result = rsp.json()
        _ppresult = json.dumps(result, indent=2, sort_keys=True)
        _log.debug(u"Result:\n{result}".format(result=_ppresult))
        return result

    def raw_jsonrpc_request(self, method, params=None):
        hdr = {'Content-Type': 'application/json'}
        data = {'jsonrpc': '2.0', 'id': 0, 'method': method, 'params': params or {}}
        _log.debug(u"Method: {method}\nParams:\n{params}".format(
            method=method,
            params=json.dumps(params, indent=2, sort_keys=True)))
        auth = requests.auth.HTTPDigestAuth(self.user, self.password)
        rsp = requests.post(
            self.url + '/json_rpc', headers=hdr, data=json.dumps(data), auth=auth,
            timeout=self.timeout, verify=self.verify_ssl_certs, proxies=self.proxies)

        if rsp.status_code == 401:
            raise Unauthorized("401 Unauthorized. Invalid RPC user name or password.")
        elif rsp.status_code != 200:
            raise RPCError("Invalid HTTP status {code} for method {method}.".format(
                code=rsp.status_code,
                method=method))
        result = rsp.json()
        _ppresult = json.dumps(result, indent=2, sort_keys=True)
        _log.debug(u"Result:\n{result}".format(result=_ppresult))

        if 'error' in result:
            err = result['error']
            _log.error(u"JSON RPC error:\n{result}".format(result=_ppresult))
            raise RPCError(
                "Method '{method}' failed with RPC Error of unknown code {code}, "
                "message: {message}".format(method=method, data=data, result=result, **err))
        return result['result']
