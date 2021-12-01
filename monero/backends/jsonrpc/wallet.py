from __future__ import unicode_literals
import binascii
from datetime import datetime
import json
import logging
import operator
import requests

from ... import exceptions
from ...account import Account
from ...address import address, Address, SubAddress
from ...numbers import from_atomic, to_atomic, PaymentID
from ...seed import Seed
from ...transaction import Transaction, IncomingPayment, OutgoingPayment
from .exceptions import RPCError, Unauthorized, MethodNotFound

_log = logging.getLogger(__name__)


class JSONRPCWallet(object):
    """
    JSON RPC backend for Monero wallet (``monero-wallet-rpc``)

    :param protocol: `http` or `https`
    :param host: host name or IP
    :param port: port number
    :param path: path for JSON RPC requests (should not be changed)
    :param user: username to authenticate with over RPC
    :param password: password to authenticate with over RPC
    :param timeout: request timeout
    :param verify_ssl_certs: verify ssl certs for request
    :param proxy_url: a proxy to use
    """

    _master_address = None

    def __init__(
        self,
        protocol="http",
        host="127.0.0.1",
        port=18088,
        path="/json_rpc",
        user="",
        password="",
        timeout=30,
        verify_ssl_certs=True,
        proxy_url=None,
    ):
        self.url = "{protocol}://{host}:{port}/json_rpc".format(
            protocol=protocol, host=host, port=port
        )
        _log.debug("JSONRPC wallet backend URL: {url}".format(url=self.url))
        self.auth = requests.auth.HTTPDigestAuth(user, password)
        self.session = requests.Session()
        self.timeout = timeout
        self.verify_ssl_certs = verify_ssl_certs
        self.proxies = {protocol: proxy_url}
        _log.debug(
            "JSONRPC wallet backend auth: '{user}'/'{stars}'".format(
                user=user, stars=("*" * len(password)) if password else ""
            )
        )

    def height(self):
        return self.raw_request("getheight")["height"]

    def spend_key(self):
        return self.raw_request("query_key", {"key_type": "spend_key"})["key"]

    def view_key(self):
        return self.raw_request("query_key", {"key_type": "view_key"})["key"]

    def seed(self):
        return Seed(self.raw_request("query_key", {"key_type": "mnemonic"})["key"])

    def accounts(self):
        accounts = []
        _accounts = self.raw_request("get_accounts")
        idx = 0
        self._master_address = Address(
            _accounts["subaddress_accounts"][0]["base_address"]
        )
        for _acc in _accounts["subaddress_accounts"]:
            assert idx == _acc["account_index"]
            accounts.append(
                Account(self, _acc["account_index"], label=_acc.get("label"))
            )
            idx += 1
        return accounts

    def new_account(self, label=None):
        _account = self.raw_request("create_account", {"label": label})
        # NOTE: the following should re-read label by _account.get('label') but the RPC
        # doesn't return that detail here
        return Account(self, _account["account_index"], label=label), SubAddress(
            _account["address"]
        )

    def addresses(self, account=0, addr_indices=None):
        qdata = {"account_index": account}
        if addr_indices:
            qdata["address_index"] = addr_indices
        _addresses = self.raw_request("getaddress", qdata)
        addresses = [None] * (
            max(map(operator.itemgetter("address_index"), _addresses["addresses"])) + 1
        )
        for _addr in _addresses["addresses"]:
            addresses[_addr["address_index"]] = address(
                _addr["address"], label=_addr.get("label", None)
            )
        return addresses

    def new_address(self, account=0, label=None):
        _address = self.raw_request(
            "create_address", {"account_index": account, "label": label}
        )
        return SubAddress(_address["address"]), _address["address_index"]

    def balances(self, account=0):
        _balance = self.raw_request("getbalance", {"account_index": account})
        return (
            from_atomic(_balance["balance"]),
            from_atomic(_balance["unlocked_balance"]),
        )

    def transfers_in(self, account, pmtfilter):
        params = {"account_index": account, "pending": False}
        method = "get_transfers"
        if pmtfilter.tx_ids:
            method = "get_transfer_by_txid"
        if pmtfilter.unconfirmed:
            params["in"] = pmtfilter.confirmed
            params["out"] = False
            params["pool"] = True
        else:
            if pmtfilter.payment_ids:
                method = "get_bulk_payments"
                params["payment_ids"] = list(map(str, pmtfilter.payment_ids))
            else:
                params["in"] = pmtfilter.confirmed
                params["out"] = False
                params["pool"] = False
        if method == "get_transfers":
            if pmtfilter.min_height:
                # NOTE: the API uses (min, max] range which is confusing
                params["min_height"] = pmtfilter.min_height - 1
                params["filter_by_height"] = True
            if pmtfilter.max_height:
                params["max_height"] = pmtfilter.max_height
                params["filter_by_height"] = True
            _pmts = self.raw_request(method, params)
            pmts = _pmts.get("in", [])
        elif method == "get_transfer_by_txid":
            pmts = []
            for txid in pmtfilter.tx_ids:
                params["txid"] = txid
                try:
                    _pmts = self.raw_request(method, params, squelch_error_logging=True)
                except exceptions.TransactionNotFound:
                    continue
                pmts.extend(_pmts["transfers"])
                # Issue #71: incoming payments to self will have excess 'destinations' key. Remove.
                for pmt in pmts:
                    try:
                        del pmt["destinations"]
                    except KeyError:
                        pass
        else:
            # NOTE: the API uses (min, max] range which is confusing
            params["min_block_height"] = (pmtfilter.min_height or 1) - 1
            _pmts = self.raw_request(method, params)
            pmts = _pmts.get("payments", [])
        if pmtfilter.unconfirmed:
            pmts.extend(_pmts.get("pool", []))
        return list(pmtfilter.filter(map(self._inpayment, pmts)))

    def transfers_out(self, account, pmtfilter):
        if pmtfilter.tx_ids:
            pmts = []
            for txid in pmtfilter.tx_ids:
                try:
                    _pmts = self.raw_request(
                        "get_transfer_by_txid",
                        {"account_index": account, "txid": txid},
                        squelch_error_logging=True,
                    )
                except exceptions.TransactionNotFound:
                    continue
                pmts.extend(_pmts["transfers"])
        else:
            _pmts = self.raw_request(
                "get_transfers",
                {
                    "account_index": account,
                    "in": False,
                    "out": pmtfilter.confirmed,
                    "pool": False,
                    "pending": pmtfilter.unconfirmed,
                },
            )
            pmts = _pmts.get("out", [])
            if pmtfilter.unconfirmed:
                pmts.extend(_pmts.get("pending", []))
        return list(pmtfilter.filter(map(self._outpayment, pmts)))

    def _paymentdict(self, data):
        pid = data.get("payment_id", None)
        laddr = data.get("address", None)
        if laddr:
            laddr = address(laddr)
        result = {
            "payment_id": None if pid is None else PaymentID(pid),
            "amount": from_atomic(data["amount"]),
            "timestamp": datetime.fromtimestamp(data["timestamp"])
            if "timestamp" in data
            else None,
            "note": data.get("note", None),
            "transaction": self._tx(data),
            "local_address": laddr,
        }
        if "destinations" in data:
            result["destinations"] = [
                (address(x["address"]), from_atomic(x["amount"]))
                for x in data.get("destinations")
            ]
        return result

    def _inpayment(self, data):
        return IncomingPayment(**self._paymentdict(data))

    def _outpayment(self, data):
        return OutgoingPayment(**self._paymentdict(data))

    def _tx(self, data):
        return Transaction(
            **{
                "hash": data.get("txid", data.get("tx_hash")),
                "fee": from_atomic(data["fee"]) if "fee" in data else None,
                "key": data.get("key"),
                "height": data.get("height", data.get("block_height")) or None,
                "timestamp": datetime.fromtimestamp(data["timestamp"])
                if "timestamp" in data
                else None,
                "blob": binascii.unhexlify(data.get("blob", "")),
                "confirmations": data.get("confirmations", None),
            }
        )

    def export_outputs(self):
        return self.raw_request("export_outputs")["outputs_data_hex"]

    def import_outputs(self, outputs_hex):
        return self.raw_request("import_outputs", {"outputs_data_hex": outputs_hex})[
            "num_imported"
        ]

    def export_key_images(self):
        return self.raw_request("export_key_images")["signed_key_images"]

    def import_key_images(self, key_images):
        _data = self.raw_request("import_key_images", {"signed_key_images": key_images})
        return (
            _data["height"],
            from_atomic(_data["spent"]),
            from_atomic(_data["unspent"]),
        )

    def transfer(
        self,
        destinations,
        priority,
        payment_id=None,
        unlock_time=0,
        account=0,
        relay=True,
    ):
        data = {
            "account_index": account,
            "destinations": list(
                map(
                    lambda dst: {
                        "address": str(address(dst[0])),
                        "amount": to_atomic(dst[1]),
                    },
                    destinations,
                )
            ),
            "priority": priority,
            "unlock_time": 0,
            "get_tx_keys": True,
            "get_tx_hex": True,
            "new_algorithm": True,
            "do_not_relay": not relay,
        }
        if payment_id is not None:
            data["payment_id"] = str(PaymentID(payment_id))
        _transfers = self.raw_request("transfer_split", data)
        _pertx = [
            dict(_tx)
            for _tx in map(
                lambda vs: zip(
                    ("txid", "amount", "fee", "key", "blob", "payment_id"), vs
                ),
                zip(
                    *[
                        _transfers[k]
                        for k in (
                            "tx_hash_list",
                            "amount_list",
                            "fee_list",
                            "tx_key_list",
                            "tx_blob_list",
                        )
                    ]
                ),
            )
        ]
        for d in _pertx:
            d["payment_id"] = payment_id
        return [self._tx(data) for data in _pertx]

    def sweep_all(
        self,
        destination,
        priority,
        payment_id=None,
        subaddr_indices=None,
        unlock_time=0,
        account=0,
        relay=True,
    ):
        if not subaddr_indices:
            # retrieve indices of all subaddresses with positive unlocked balance
            bals = self.raw_request("get_balance", {"account_index": account})
            subaddr_indices = []
            for subaddr in bals["per_subaddress"]:
                if subaddr.get("unlocked_balance", 0):
                    subaddr_indices.append(subaddr["address_index"])
        data = {
            "account_index": account,
            "address": str(address(destination)),
            "subaddr_indices": list(subaddr_indices),
            "priority": priority,
            "unlock_time": 0,
            "get_tx_keys": True,
            "get_tx_hex": True,
            "do_not_relay": not relay,
        }
        if payment_id is not None:
            data["payment_id"] = str(PaymentID(payment_id))
        _transfers = self.raw_request("sweep_all", data)
        _pertx = [
            dict(_tx)
            for _tx in map(
                lambda vs: zip(
                    ("txid", "amount", "fee", "key", "blob", "payment_id"), vs
                ),
                zip(
                    *[
                        _transfers[k]
                        for k in (
                            "tx_hash_list",
                            "amount_list",
                            "fee_list",
                            "tx_key_list",
                            "tx_blob_list",
                        )
                    ]
                ),
            )
        ]
        for d in _pertx:
            d["payment_id"] = payment_id
        return list(
            zip(
                [self._tx(data) for data in _pertx],
                map(from_atomic, _transfers["amount_list"]),
            )
        )

    def raw_request(self, method, params=None, squelch_error_logging=False):
        hdr = {"Content-Type": "application/json"}
        data = {"jsonrpc": "2.0", "id": 0, "method": method, "params": params or {}}
        _log.debug(
            "Method: {method}\nParams:\n{params}".format(
                method=method, params=json.dumps(params, indent=2, sort_keys=True)
            )
        )
        rsp = self.session.post(
            self.url,
            headers=hdr,
            data=json.dumps(data),
            auth=self.auth,
            timeout=self.timeout,
            verify=self.verify_ssl_certs,
            proxies=self.proxies,
        )

        if rsp.status_code == 401:
            raise Unauthorized("401 Unauthorized. Invalid RPC user name or password.")
        elif rsp.status_code != 200:
            raise RPCError(
                "Invalid HTTP status {code} for method {method}.".format(
                    code=rsp.status_code, method=method
                )
            )
        result = rsp.json()
        _ppresult = json.dumps(result, indent=2, sort_keys=True)
        _log.debug("Result:\n{result}".format(result=_ppresult))

        if "error" in result:
            err = result["error"]
            if not squelch_error_logging:
                _log.error("JSON RPC error:\n{result}".format(result=_ppresult))
            if err["code"] in _err2exc:
                raise _err2exc[err["code"]](err["message"])
            else:
                raise RPCError(
                    "Method '{method}' failed with RPC Error of unknown code {code}, "
                    "message: {message}".format(
                        method=method, data=data, result=result, **err
                    )
                )
        return result["result"]


_err2exc = {
    -2: exceptions.WrongAddress,
    -4: exceptions.GenericTransferError,
    -5: exceptions.WrongPaymentId,
    -8: exceptions.TransactionNotFound,
    -9: exceptions.SignatureCheckFailed,
    -14: exceptions.AccountIndexOutOfBound,
    -15: exceptions.AddressIndexOutOfBound,
    -16: exceptions.TransactionNotPossible,
    -17: exceptions.NotEnoughMoney,
    -20: exceptions.AmountIsZero,
    -29: exceptions.WalletIsWatchOnly,
    -37: exceptions.NotEnoughUnlockedMoney,
    -38: exceptions.NoDaemonConnection,
    -43: exceptions.WalletIsNotDeterministic,  # https://github.com/monero-project/monero/pull/4653
    -32601: MethodNotFound,
}
