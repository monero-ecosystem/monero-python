import binascii
from datetime import datetime
import operator
import json
import logging
import pprint
import requests

from .. import exceptions
from ..account import Account
from ..address import address, Address, SubAddress
from ..numbers import from_atomic, to_atomic, PaymentID
from ..transaction import Transaction, Payment, Transfer

_log = logging.getLogger(__name__)


class JSONRPCDaemon(object):
    def __init__(self, protocol='http', host='127.0.0.1', port=18081, path='/json_rpc'):
        self.url = '{protocol}://{host}:{port}'.format(
                protocol=protocol,
                host=host,
                port=port)
        _log.debug("JSONRPC daemon backend URL: {url}".format(url=self.url))

    def get_info(self):
        info = self.raw_jsonrpc_request('get_info')
        return info

    def send_transaction(self, blob):
        res = self.raw_request('/sendrawtransaction', {
            'tx_as_hex': blob,
            'do_not_relay': False})
        if res['status'] == 'OK':
            return res
        raise exceptions.TransactionBroadcastError(
                "{status}: {reason}".format(**res),
                details=res)

    def raw_request(self, path, data):
        hdr = {'Content-Type': 'application/json'}
        _log.debug(u"Request: {path}\nData: {data}".format(
            path=path,
            data=pprint.pformat(data)))
        rsp = requests.post(self.url + path, headers=hdr, data=json.dumps(data))
        if rsp.status_code != 200:
            raise RPCError("Invalid HTTP status {code} for path {path}.".format(
                code=rsp.status_code,
                path=path))
        result = rsp.json()
        _ppresult = pprint.pformat(result)
        _log.debug(u"Result:\n{result}".format(result=_ppresult))
        return result


    def raw_jsonrpc_request(self, method, params=None):
        hdr = {'Content-Type': 'application/json'}
        data = {'jsonrpc': '2.0', 'id': 0, 'method': method, 'params': params or {}}
        _log.debug(u"Method: {method}\nParams:\n{params}".format(
            method=method,
            params=pprint.pformat(params)))
        rsp = requests.post(self.url + '/json_rpc', headers=hdr, data=json.dumps(data))
        if rsp.status_code != 200:
            raise RPCError("Invalid HTTP status {code} for method {method}.".format(
                code=rsp.status_code,
                method=method))
        result = rsp.json()
        _ppresult = pprint.pformat(result)
        _log.debug(u"Result:\n{result}".format(result=_ppresult))

        if 'error' in result:
            err = result['error']
            _log.error(u"JSON RPC error:\n{result}".format(result=_ppresult))
#            if err['code'] in _err2exc:
#                raise _err2exc[err['code']](err['message'])
#            else:
#                raise RPCError(
#                    "Method '{method}' failed with RPC Error of unknown code {code}, "
#                    "message: {message}".format(method=method, data=data, result=result, **err))
            raise RPCError(
                "Method '{method}' failed with RPC Error of unknown code {code}, "
                "message: {message}".format(method=method, data=data, result=result, **err))
#
#
#
        return result['result']




class JSONRPCWallet(object):
    _master_address = None
    _addresses = None

    def __init__(self, protocol='http', host='127.0.0.1', port=18088, path='/json_rpc', user='', password=''):
        self.url = '{protocol}://{host}:{port}/json_rpc'.format(
                protocol=protocol,
                host=host,
                port=port)
        _log.debug("JSONRPC wallet backend URL: {url}".format(url=self.url))
        self.user = user
        self.password = password
        _log.debug("JSONRPC wallet backend auth: '{user}'/'{stars}'".format(
            user=user, stars=('*' * len(password)) if password else ''))

    def get_view_key(self):
        return self.raw_request('query_key', {'key_type': 'view_key'})['key']

    def get_seed(self):
        return self.raw_request('query_key', {'key_type': 'mnemonic'})['key']

    def get_accounts(self):
        accounts = []
        try:
            _accounts = self.raw_request('get_accounts')
        except MethodNotFound:
            # monero <= 0.11 : there's only one account and one address
            _log.debug('Monero <= 0.11 found, no accounts')
            self._master_address = self.get_addresses()[0]
            return [Account(self, 0)]
        idx = 0
        self._master_address = Address(_accounts['subaddress_accounts'][0]['base_address'])
        for _acc in _accounts['subaddress_accounts']:
            assert idx == _acc['account_index']
            accounts.append(Account(self, _acc['account_index']))
            idx += 1
        return accounts

    def new_account(self, label=None):
        _account = self.raw_request('create_account', {'label': label})
        return Account(self, _account['account_index']), SubAddress(_account['address'])

    def get_addresses(self, account=0):
        _addresses = self.raw_request('getaddress', {'account_index': account})
        if 'addresses' not in _addresses:
            # monero <= 0.11
            _log.debug('Monero <= 0.11 found, assuming single address')
            return [Address(_addresses['address'])]
        addresses = [None] * (max(map(operator.itemgetter('address_index'), _addresses['addresses'])) + 1)
        for _addr in _addresses['addresses']:
            addresses[_addr['address_index']] = address(
                _addr['address'],
                label=_addr.get('label', None))
        return addresses

    def new_address(self, account=0, label=None):
        _address = self.raw_request(
            'create_address', {'account_index': account, 'label': label})
        return SubAddress(_address['address'])

    def get_balances(self, account=0):
        _balance = self.raw_request('getbalance', {'account_index': account})
        return (from_atomic(_balance['balance']), from_atomic(_balance['unlocked_balance']))

    def get_payments(self, account=0, payment_id=0):
        payment_id = PaymentID(payment_id)
        _log.debug("Getting payments for account {acc}, payment_id {pid}".format(
            acc=account, pid=payment_id))
        _payments = self.raw_request('get_payments', {
            'account_index': account,
            'payment_id': str(payment_id)})
        pmts = []
        for tx in _payments['payments']:
            data = self._tx2dict(tx)
            # Monero <= 0.11 : no address is passed because there's only one
            data['local_address'] = data['local_address'] or self._master_address
            pmts.append(Payment(**data))
        return pmts

    def get_transactions_in(self, account=0):
        _transfers = self.raw_request('get_transfers',
                {'account_index': account, 'in': True, 'out': False, 'pool': False})
        return [Payment(**self._tx2dict(tx)) for tx in
            sorted(_transfers.get('in', []), key=operator.itemgetter('timestamp'))]

    def get_transactions_out(self, account=0):
        _transfers = self.raw_request('get_transfers',
                {'account_index': account, 'in': False, 'out': True, 'pool': False})
        return [Transfer(**self._tx2dict(tx)) for tx in
            sorted(_transfers.get('out', []), key=operator.itemgetter('timestamp'))]

    def _tx2dict(self, tx):
        pid = tx.get('payment_id', None)
        return {
            'hash': tx.get('txid', tx.get('tx_hash')),
            'timestamp': datetime.fromtimestamp(tx['timestamp']) if 'timestamp' in tx else None,
            'amount': from_atomic(tx['amount']),
            'fee': from_atomic(tx['fee']) if 'fee' in tx else None,
            'height': tx.get('height', tx.get('block_height')),
            'payment_id': None if pid is None else PaymentID(pid),
            'note': tx.get('note'),
            # NOTE: address will be resolved only after PR#3010 has been merged to Monero
            'local_address': address(tx['address']) if 'address' in tx else None,
            'key': tx.get('key'),
            'blob': tx.get('blob', None),
        }

    def transfer(self, destinations, priority, ringsize,
            payment_id=None, unlock_time=0, account=0,
            relay=True):
        data = {
            'account_index': account,
            'destinations': list(map(
                lambda dst: {'address': str(address(dst[0])), 'amount': to_atomic(dst[1])},
                destinations)),
            'mixin': ringsize - 1,
            'priority': priority,
            'unlock_time': 0,
            'get_tx_keys': True,
            'get_tx_hex': True,
            'new_algorithm': True,
            'do_not_relay': not relay,
        }
        if payment_id is not None:
            data['payment_id'] = str(PaymentID(payment_id))
        _transfers = self.raw_request('transfer_split', data)
        _pertx = [dict(_tx) for _tx in map(
            lambda vs: zip(('txid', 'amount', 'fee', 'key', 'blob', 'payment_id'), vs),
            zip(*[_transfers[k] for k in (
                'tx_hash_list', 'amount_list', 'fee_list', 'tx_key_list', 'tx_blob_list')]))]
        for d in _pertx:
            d['payment_id'] = payment_id
        return [Transfer(**self._tx2dict(tx)) for tx in _pertx]

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
    -5: exceptions.WrongPaymentId,
    -16: exceptions.TransactionNotPossible,
    -17: exceptions.NotEnoughMoney,
    -20: exceptions.AmountIsZero,
    -32601: MethodNotFound,
}
