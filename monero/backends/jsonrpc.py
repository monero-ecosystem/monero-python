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
from ..seed import Seed
from ..transaction import Transaction, IncomingPayment, OutgoingPayment

_log = logging.getLogger(__name__)


class JSONRPCDaemon(object):
    """
    JSON RPC backend for Monero daemon

    :param protocol: `http` or `https`
    :param host: host name or IP
    :param port: port number
    :param path: path for JSON RPC requests (should not be changed)
    """
    def __init__(self, protocol='http', host='127.0.0.1', port=18081, path='/json_rpc'):
        self.url = '{protocol}://{host}:{port}'.format(
                protocol=protocol,
                host=host,
                port=port)
        _log.debug("JSONRPC daemon backend URL: {url}".format(url=self.url))

    def info(self):
        info = self.raw_jsonrpc_request('get_info')
        return info

    def send_transaction(self, blob, relay=True):
        res = self.raw_request('/sendrawtransaction', {
            'tx_as_hex': blob,
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
                timestamp=datetime.fromtimestamp(tx['receive_time'])))
        return txs

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
            raise RPCError(
                "Method '{method}' failed with RPC Error of unknown code {code}, "
                "message: {message}".format(method=method, data=data, result=result, **err))
        return result['result']




class JSONRPCWallet(object):
    """
    JSON RPC backend for Monero wallet (``monero-wallet-rpc``)

    :param protocol: `http` or `https`
    :param host: host name or IP
    :param port: port number
    :param path: path for JSON RPC requests (should not be changed)
    :param user: username to authenticate with over RPC
    :param password: password to authenticate with over RPC
    """
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

    def height(self):
        return self.raw_request('getheight')['height']

    def spend_key(self):
        # NOTE: This will fail on 0.11.x, the method was missing
        return self.raw_request('query_key', {'key_type': 'spend_key'})['key']

    def view_key(self):
        return self.raw_request('query_key', {'key_type': 'view_key'})['key']

    def seed(self):
        return Seed(self.raw_request('query_key', {'key_type': 'mnemonic'})['key'])

    def accounts(self):
        accounts = []
        try:
            _accounts = self.raw_request('get_accounts', squelch_error_logging=True)
        except MethodNotFound:
            # monero <= 0.11 : there's only one account and one address
            _log.debug('Monero <= 0.11 found, no accounts')
            self._master_address = self.addresses()[0]
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

    def addresses(self, account=0):
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

    def balances(self, account=0):
        _balance = self.raw_request('getbalance', {'account_index': account})
        return (from_atomic(_balance['balance']), from_atomic(_balance['unlocked_balance']))

    def transfers_in(self, account, pmtfilter):
        params = {'account_index': account, 'pending': False}
        method = 'get_transfers'
        if pmtfilter.unconfirmed:
            params['in'] = pmtfilter.confirmed
            params['out'] = False
            params['pool'] = True
        else:
            if pmtfilter.payment_ids:
                method = 'get_bulk_payments'
                params['payment_ids'] = list(map(str, pmtfilter.payment_ids))
            else:
                params['in'] = pmtfilter.confirmed
                params['out'] = False
                params['pool'] = False
        if method == 'get_transfers':
            arg = 'in'
            if pmtfilter.min_height:
                # NOTE: the API uses (min, max] range which is confusing
                params['min_height'] = pmtfilter.min_height - 1
                params['filter_by_height'] = True
            if pmtfilter.max_height:
                params['max_height'] = pmtfilter.max_height
                params['filter_by_height'] = True
            # PR#3235 makes the following obsolete
            # CRYPTONOTE_MAX_BLOCK_NUMBER = 500000000
            params['max_height'] = params.get('max_height', 500000000)
        else:
            arg = 'payments'
            # NOTE: the API uses (min, max] range which is confusing
            params['min_block_height'] = (pmtfilter.min_height or 1) - 1
        _pmts = self.raw_request(method, params)
        pmts = _pmts.get(arg, [])
        if pmtfilter.unconfirmed:
            pmts.extend(_pmts.get('pool', []))
        return list(pmtfilter.filter(map(self._inpayment, pmts)))

    def transfers_out(self, account, pmtfilter):
        _pmts = self.raw_request('get_transfers', {
            'account_index': account,
            'in': False,
            'out': pmtfilter.confirmed,
            'pool': False,
            'pending': pmtfilter.unconfirmed})
        pmts = _pmts.get('out', [])
        if pmtfilter.unconfirmed:
            pmts.extend(_pmts.get('pending', []))
        return list(pmtfilter.filter(map(self._outpayment, pmts)))

    def _paymentdict(self, data):
        pid = data.get('payment_id', None)
        laddr = data.get('address', None)
        if laddr:
            laddr = address(laddr)
        return {
            'payment_id': None if pid is None else PaymentID(pid),
            'amount': from_atomic(data['amount']),
            'timestamp': datetime.fromtimestamp(data['timestamp']) if 'timestamp' in data else None,
            'note': data.get('note', None),
            'transaction': self._tx(data),
            'local_address': laddr,
        }

    def _inpayment(self, data):
        return IncomingPayment(**self._paymentdict(data))

    def _outpayment(self, data):
        return OutgoingPayment(**self._paymentdict(data))

    def _tx(self, data):
        return Transaction(**{
            'hash': data.get('txid', data.get('tx_hash')),
            'fee': from_atomic(data['fee']) if 'fee' in data else None,
            'key': data.get('key'),
            'height': data.get('height', data.get('block_height')) or None,
            'timestamp': datetime.fromtimestamp(data['timestamp']) if 'timestamp' in data else None,
            'blob': data.get('blob', None),
        })

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
        return [self._tx(data) for data in _pertx]

    def raw_request(self, method, params=None, squelch_error_logging=False):
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
            if not squelch_error_logging:
                _log.error(u"JSON RPC error:\n{result}".format(result=_ppresult))
            # XXX: workaround for 0.11 bug throwing a wrong error code
            if err['code'] == -4 and 'not enough money' in err['message']:
                raise exceptions.NotEnoughMoney(err['message'])
            #
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
    -5: exceptions.WrongPaymentId,
    -8: exceptions.TransactionNotFound,
    -16: exceptions.TransactionNotPossible,
    -17: exceptions.NotEnoughMoney,
    -20: exceptions.AmountIsZero,
    -37: exceptions.NotEnoughUnlockedMoney, # PR pending: https://github.com/monero-project/monero/pull/3197
    -38: exceptions.NoDaemonConnection, # PR 3197
    -32601: MethodNotFound,
}
