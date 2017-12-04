from datetime import datetime
import operator
import json
import logging
import pprint
import requests

from .. import exceptions
from ..account import Account
from ..address import address, Address
from ..numbers import from_atomic, to_atomic

_log = logging.getLogger(__name__)


class JSONRPC(object):
    def __init__(self, protocol='http', host='127.0.0.1', port=18082, path='/json_rpc', user='', password=''):
        self.url = '{protocol}://{host}:{port}/json_rpc'.format(
                protocol=protocol,
                host=host,
                port=port)
        _log.debug("JSONRPC backend URL: {url}".format(url=self.url))
        self.user = user
        self.password = password
        _log.debug("JSONRPC backend auth: '{user}'/'{stars}'".format(
            user=user, stars=('*' * len(password)) if password else ''))

    def get_accounts(self):
        accounts = []
        try:
            _accounts = self.raw_request('get_accounts')
        except MethodNotFound:
            # monero <= 0.11
            return [Account(self, 0)]
        idx = 0
        for _acc in _accounts['subaddress_accounts']:
            assert idx == _acc['account_index']
            accounts.append(Account(self, _acc['account_index']))
            idx += 1
        return accounts

    def get_addresses(self, account=0):
        _addresses = self.raw_request('getaddress', {'account_index': account})
        if 'addresses' not in _addresses:
            # monero <= 0.11
            return [Address(_addresses['address'])]
        addresses = [None] * (max(map(operator.itemgetter('address_index'), _addresses['addresses'])) + 1)
        for _addr in _addresses['addresses']:
            addresses[_addr['address_index']] = address(_addr['address'])
        return addresses

    def get_balances(self, account=0):
        _balance = self.raw_request('getbalance', {'account_index': account})
        return (from_atomic(_balance['balance']), from_atomic(_balance['unlocked_balance']))

    def get_payments_in(self, account=0):
        _payments = self.raw_request('get_transfers',
                {'account_index': account, 'in': True, 'out': False, 'pool': False})
        return map(self._pythonify_payment, _payments.get('in', []))

    def get_payments_out(self, account=0):
        _payments = self.raw_request('get_transfers',
                {'account_index': account, 'in': False, 'out': True, 'pool': False})
        return map(self._pythonify_payment, _payments.get('out', ''))

    def _pythonify_payment(self, pm):
        return {
            'id': pm['txid'],
            'timestamp': datetime.fromtimestamp(pm['timestamp']),
            'amount': from_atomic(pm['amount']),
            'fee': from_atomic(pm['fee']),
            'height': pm['height'],
            'payment_id': pm['payment_id'],
            'note': pm['note']
        }

    def transfer(self, destinations, priority, mixin, unlock_time, account=0):
        data = {
            'account_index': account,
            'destinations': list(map(
                lambda dst: {'address': str(address(dst[0])), 'amount': to_atomic(dst[1])},
                destinations)),
            'mixin': mixin,
            'priority': priority,
            'unlock_time': 0,
            'get_tx_keys': True,
            'get_tx_hex': True,
            'new_algorithm': True,
        }
        _transfers = self.raw_request('transfer_split', data)
        keys = ('hash', 'amount', 'fee', 'key', 'blob')
        return list(map(
            self._pythonify_tx,
            [ dict(_tx) for _tx in map(
                lambda vs: zip(keys,vs),
                zip(
                    *[_transfers[k] for k in (
                        'tx_hash_list', 'amount_list', 'fee_list', 'tx_key_list', 'tx_blob_list')
                    ]
                ))
            ]))

    def _pythonify_tx(self, tx):
        return {
            'id': tx['hash'],
            'amount': from_atomic(tx['amount']),
            'fee': from_atomic(tx['fee']),
            'key': tx['key'],
            'blob': tx.get('blob', None),
        }

    def raw_request(self, method, params=None):
        hdr = {'Content-Type': 'application/json'}
        data = {'jsonrpc': '2.0', 'id': 0, 'method': method, 'params': params or {}}
        _log.debug(u"Method: {method}\nParams:\n{params}".format(
            method=method,
            params=pprint.pformat(params)))
        auth = requests.auth.HTTPDigestAuth(self.user, self.password)
        rsp = requests.post(self.url, headers=hdr, data=json.dumps(data), auth=auth)
        if rsp.status_code == 401:
            raise Unauthorized("401 Unauthorized. Invalid RPC user name or password.")
        elif rsp.status_code != 200:
            raise RPCError("Invalid HTTP status {code} for method {method}.".format(
                code=rsp.status_code,
                method=method))
        result = rsp.json()
        _ppresult = pprint.pformat(result)
        _log.debug(u"Result:\n{result}".format(result=_ppresult))

        if 'error' in result:
            err = result['error']
            _log.error(u"JSON RPC error:\n{result}".format(result=_ppresult))
            if err['code'] in _err2exc:
                raise _err2exc[err['code']](err['message'])
            else:
                raise RPCError(
                    "Method '{method}' failed with RPC Error of unknown code {code}, "
                    "message: {message}".format(method=method, data=data, result=result, **err))
        return result['result']


class RPCError(exceptions.BackendException):
    pass


class Unauthorized(RPCError):
    pass


class MethodNotFound(RPCError):
    pass


_err2exc = {
    -2: exceptions.WrongAddress,
    -4: exceptions.NotEnoughUnlockedMoney,
    -20: exceptions.AmountIsZero,
    -32601: MethodNotFound,
}
