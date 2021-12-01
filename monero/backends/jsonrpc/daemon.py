from __future__ import unicode_literals
import binascii
from datetime import datetime
from decimal import Decimal
import ipaddress
import json
import logging
import requests
import six

from ... import address
from ... import exceptions
from ...block import Block
from ...const import NET_MAIN, NET_TEST, NET_STAGE
from ...numbers import from_atomic, to_atomic
from ...transaction import Transaction
from .exceptions import RPCError, MethodNotFound, Unauthorized


_log = logging.getLogger(__name__)


RESTRICTED_MAX_TRANSACTIONS = 100


class JSONRPCDaemon(object):
    """
    JSON RPC backend for Monero daemon.
    The offical documentation for the Monero Daemon RPC Protocol can be found at the link below.
    https://www.getmonero.org/resources/developer-guides/daemon-rpc.html#on_get_block_hash
    Much of the in-code documentation of this class is derived from this document.

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

    _METHOD_NOT_FOUND_CODE = -32601
    _KNOWN_LOG_CATEGORIES = [
        "*",
        "default",
        "net",
        "net.http",
        "net.p2p",
        "logging",
        "net.throttle",
        "blockchain.db",
        "blockchain.db.lmdb",
        "bcutil",
        "checkpoints",
        "net.dns",
        "net.dl",
        "i18n",
        "perf",
        "stacktrace",
        "updates",
        "account",
        "cn",
        "difficulty",
        "hardfork",
        "miner",
        "blockchain",
        "txpool",
        "cn.block_queue",
        "net.cn",
        "daemon",
        "debugtools.deserialize",
        "debugtools.objectsizes",
        "device.ledger",
        "wallet.gen_multisig",
        "multisig",
        "bulletproofs",
        "ringct",
        "daemon.rpc",
        "wallet.simplewallet",
        "WalletAPI",
        "wallet.ringdb",
        "wallet.wallet2",
        "wallet.rpc" "tests.core",
    ]
    _KNOWN_LOG_LEVELS = ["FATAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE"]

    _net = None
    _restricted = None

    def __init__(
        self,
        protocol="http",
        host="127.0.0.1",
        port=18081,
        path="/json_rpc",
        user="",
        password="",
        timeout=30,
        verify_ssl_certs=True,
        proxy_url=None,
        prune_transactions=True,
    ):
        self.url = "{protocol}://{host}:{port}".format(
            protocol=protocol, host=host, port=port
        )
        _log.debug("JSONRPC daemon backend URL: {url}".format(url=self.url))
        self.auth = requests.auth.HTTPDigestAuth(user, password)
        self.session = requests.Session()
        self.timeout = timeout
        self.verify_ssl_certs = verify_ssl_certs
        self.proxies = {protocol: proxy_url}
        self.prune_transactions = prune_transactions

    def info(self):
        info = self.raw_jsonrpc_request("get_info")
        self._set_net(info)
        return info

    def net(self):
        if self._net:
            return self._net
        self.info()
        return self._net

    def restricted(self):
        if self._restricted is None:
            self._set_restricted()

        return self._restricted

    def send_transaction(self, blob, relay=True):
        res = self.raw_request(
            "/sendrawtransaction",
            {
                "tx_as_hex": six.ensure_text(binascii.hexlify(blob)),
                "do_not_relay": not relay,
            },
        )
        if res["status"] == "OK":
            return res
        raise exceptions.TransactionBroadcastError(
            "{status}: {reason}".format(**res), details=res
        )

    def mempool(self):
        res = self.raw_request("/get_transaction_pool", {})
        txs = []
        for tx in res.get("transactions", []):
            txs.append(
                Transaction(
                    hash=tx["id_hash"],
                    fee=from_atomic(tx["fee"]),
                    timestamp=datetime.fromtimestamp(tx["receive_time"]),
                    blob=binascii.unhexlify(tx["tx_blob"]),
                    json=json.loads(tx["tx_json"]),
                    confirmations=0,
                )
            )
        return txs

    def headers(self, start_height, end_height=None):
        end_height = end_height or start_height
        res = self.raw_jsonrpc_request(
            "get_block_headers_range",
            {"start_height": start_height, "end_height": end_height},
        )
        if res["status"] == "OK":
            return res["headers"]
        raise exceptions.BackendException(res["status"])

    def block(self, bhash=None, height=None):
        data = {}
        if bhash:
            data["hash"] = bhash
        if height:
            data["height"] = height
        res = self.raw_jsonrpc_request("get_block", data)
        if res["status"] == "OK":
            bhdr = res["block_header"]
            sub_json = json.loads(res["json"])
            data = {
                "blob": res["blob"],
                "hash": bhdr["hash"],
                "height": bhdr["height"],
                "timestamp": datetime.fromtimestamp(bhdr["timestamp"]),
                "version": (bhdr["major_version"], bhdr["minor_version"]),
                "difficulty": bhdr["difficulty"],
                "nonce": bhdr["nonce"],
                "orphan": bhdr["orphan_status"],
                "prev_hash": bhdr["prev_hash"],
                "reward": from_atomic(bhdr["reward"]),
                "transactions": self.transactions(
                    [bhdr["miner_tx_hash"]] + sub_json["tx_hashes"]
                ),
            }
            return Block(**data)
        raise exceptions.BackendException(res["status"])

    def transactions(self, hashes):
        """
        Returns a list of transactions for given hashes. Automatically chunks the request
        into amounts acceptable by a restricted RPC server.
        """

        hashes = self._validate_hashlist(hashes)
        result = []
        while len(hashes):
            result.extend(
                self._do_get_transactions(
                    hashes[:RESTRICTED_MAX_TRANSACTIONS], prune=self.prune_transactions
                )
            )
            hashes = hashes[RESTRICTED_MAX_TRANSACTIONS:]
        return result

    def raw_request(self, path, data=None):
        hdr = {"Content-Type": "application/json"}
        _log.debug(
            "Request: {path}\nData: {data}".format(
                path=path, data=json.dumps(data, indent=2, sort_keys=True)
            )
        )
        rsp = self.session.post(
            self.url + path,
            headers=hdr,
            data=json.dumps(data) if data else None,
            auth=self.auth,
            timeout=self.timeout,
            verify=self.verify_ssl_certs,
            proxies=self.proxies,
        )
        if rsp.status_code != 200:
            raise RPCError(
                "Invalid HTTP status {code} for path {path}.".format(
                    code=rsp.status_code, path=path
                )
            )
        result = rsp.json()
        _ppresult = json.dumps(result, indent=2, sort_keys=True)
        _log.debug("Result:\n{result}".format(result=_ppresult))
        return result

    def raw_jsonrpc_request(self, method, params=None):
        hdr = {"Content-Type": "application/json"}
        data = {"jsonrpc": "2.0", "id": 0, "method": method, "params": params or {}}
        _log.debug(
            "Method: {method}\nParams:\n{params}".format(
                method=method, params=json.dumps(params, indent=2, sort_keys=True)
            )
        )
        rsp = self.session.post(
            self.url + "/json_rpc",
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

        try:
            result = rsp.json()
        except ValueError as e:
            _log.error(
                "Could not parse JSON response from '{url}' during method '{method}'. Response:\n{resp}".format(
                    url=self.url, method=method, resp=rsp.text
                )
            )
            raise RPCError(
                "Daemon returned an unreadable JSON response. It may contain unparseable binary characters."
            )

        _ppresult = json.dumps(result, indent=2, sort_keys=True)
        _log.debug("Result:\n{result}".format(result=_ppresult))

        if "error" in result:
            err = result["error"]
            code = err["code"]
            msg = err["message"]

            if code == self._METHOD_NOT_FOUND_CODE:
                raise MethodNotFound('Daemon method "{}" not found'.format(method))

            _log.error("JSON RPC error:\n{result}".format(result=_ppresult))
            raise RPCError(
                "Method '{method}' failed with RPC Error of unknown code {code}, "
                "message: {msg}".format(
                    method=method, data=data, result=result, code=code, msg=msg
                )
            )
        elif "status" in result["result"] and result["result"]["status"] == "BUSY":
            raise exceptions.DaemonIsBusy(
                "In JSONRPC method '{method}': daemon at {url} is in BUSY mode. RPC command results will be unpredictable "
                "until daemon is fully synced.".format(method=method, url=self.url)
            )

        return result["result"]

    # JSON RPC Methods (https://www.getmonero.org/resources/developer-guides/daemon-rpc.html#json-rpc-methods)

    def get_block_count(self):
        """
        Look up how many blocks are in the longest chain known to the node.

        Output:
        {
        "count": unsigned int; Number of blocks in longest chain seen by the node.
        "status": str; General RPC error code. "OK" means everything looks good.
        }
        """

        return self.raw_jsonrpc_request("get_block_count")

    def on_get_block_hash(self, height):
        """
        Look up a block's hash by its height.

        :param int height: height of the block

        Output: str; block hash
        """

        height = int(height)

        if height < 0:
            raise ValueError("height < 0")

        return self.raw_jsonrpc_request("on_get_block_hash", params=[height])

    def get_block_template(self, wallet_address, reserve_size):
        """
        Get a block template on which mining a new block.

        :param str wallet_address: Address of wallet to receive coinbase transactions for successful block.
        :param int reserve_size: number of bytes to make reserved space, maximum is 127

        Output:
        {
        "blocktemplate_blob": str; Blob on which to try to mine a new block.
        "blockhashing_blob": str; Blob on which to try to find a valid nonce.
        "difficulty": unsigned int; Bottom 64 bits of difficulty of next block.
        "difficuly_top64": unsigned int; Top 64 bits of difficulty of next block.
        "wide_difficulty": str; hex str of difficulty of next block.
        "expected_reward": unsigned int; Coinbase reward expected to be received if block is successfully mined.
        "height": unsigned int; Height on which to mine.
        "prev_hash": str; Hash of the most recent block on which to mine the next block.
        "reserved_offset": unsigned int; Offset in bytes to reserved space in block blob.
        "seed_hash": str;
        "seed_height": unsigned int;
        "status": str; General RPC error code. "OK" means everything looks good.
        "untrusted": bool; True for bootstrap mode, False for full sync mode
        }
        """

        try:
            address.address(wallet_address)
        except ValueError:
            raise ValueError("wallet_address is not in a recognized address form")

        if reserve_size not in range(128):
            raise ValueError("reserve_size {} is out of bounds".format(reserve_size))

        return self.raw_jsonrpc_request(
            "get_block_template",
            params={"wallet_address": wallet_address, "reserve_size": reserve_size},
        )

    def submit_block(self, blobs):
        """
        Submit a mined block to the network.

        :param list blobs: list of block hex strs or raw bytes objects

        Output:
        {
        "status": str; Block submit status
        }
        """

        if isinstance(blobs, (six.binary_type,) + six.string_types):
            blobs = [blobs]

        blobs = [
            binascii.hexlify(b).decode()
            if isinstance(b, six.binary_type)
            else six.ensure_text(b)
            for b in blobs
        ]

        return self.raw_jsonrpc_request("submit_block", params=blobs)

    def get_last_block_header(self):
        """
        Block header information for the most recent block is easily retrieved with this method.

        Output:
        {
        "block_header": {
            "block_size": unsigned int; The block size in bytes.
            "depth": unsigned int; The number of blocks succeeding this block on the blockchain. A larger number means an older block.
            "difficulty" unsigned int; The strength of the Monero network based on mining power.
            "hash": str; The hash of this block.
            "height": unsigned int; The number of blocks preceding this block on the blockchain.
            "major_version": unsigned int; The major version of the monero protocol at this block height.
            "minor_version": unsigned int; The minor version of the monero protocol at this block height.
            "nonce": unsigned int; a cryptographic random one-time number used in mining a Monero block.
            "num_txes": unsigned int; Number of transactions in the block, not counting the coinbase tx.
            "orphan_status": bool; Usually false. If true, this block is not part of the longest chain.
            "prev_hash": str; The hash of the block immediately preceding this block in the chain.
            "reward": unsigned int; The amount of new atomic units generated in this block and rewarded to the miner. Note: 1 XMR = 1e12 atomic units.
            "timestamp": unsigned int; The unix time at which the block was recorded into the blockchain.
        }
        "status": str; General RPC error code. "OK" means everything looks good.
        "untrusted": bool; True for bootstrap mode, False for full sync mode
        }
        """

        return self.raw_jsonrpc_request("get_last_block_header")

    def get_block_header_by_hash(self, blk_hash):
        """
        Block header information can be retrieved using a block's hash

        :param str blk_hash: block hash

        Output:
        {
        "block_header": {
            "block_size": unsigned int; The block size in bytes.
            "depth": unsigned int; The number of blocks succeeding this block on the blockchain. A larger number means an older block.
            "difficulty" unsigned int; The strength of the Monero network based on mining power.
            "hash": str; The hash of this block.
            "height": unsigned int; The number of blocks preceding this block on the blockchain.
            "major_version": unsigned int; The major version of the monero protocol at this block height.
            "minor_version": unsigned int; The minor version of the monero protocol at this block height.
            "nonce": unsigned int; a cryptographic random one-time number used in mining a Monero block.
            "num_txes": unsigned int; Number of transactions in the block, not counting the coinbase tx.
            "orphan_status": bool; Usually false. If true, this block is not part of the longest chain.
            "prev_hash": str; The hash of the block immediately preceding this block in the chain.
            "reward": unsigned int; The amount of new atomic units generated in this block and rewarded to the miner. Note: 1 XMR = 1e12 atomic units.
            "timestamp": unsigned int; The unix time at which the block was recorded into the blockchain.
        }
        "status": str; General RPC error code. "OK" means everything looks good.
        "untrusted": bool; True for bootstrap mode, False for full sync mode
        }
        """

        if not self._is_valid_256_hex(blk_hash):
            raise ValueError('blk_hash "{}" is not a valid hash'.format(blk_hash))

        return self.raw_jsonrpc_request(
            "get_block_header_by_hash", params={"hash": blk_hash}
        )

    def get_block_header_by_height(self, height):
        """
        Block header information can be retrieved using a block's height

        :param int height: block height

        Output:
        {
        "block_header": {
            "block_size": unsigned int; The block size in bytes.
            "depth": unsigned int; The number of blocks succeeding this block on the blockchain. A larger number means an older block.
            "difficulty" unsigned int; The strength of the Monero network based on mining power.
            "hash": str; The hash of this block.
            "height": unsigned int; The number of blocks preceding this block on the blockchain.
            "major_version": unsigned int; The major version of the monero protocol at this block height.
            "minor_version": unsigned int; The minor version of the monero protocol at this block height.
            "nonce": unsigned int; a cryptographic random one-time number used in mining a Monero block.
            "num_txes": unsigned int; Number of transactions in the block, not counting the coinbase tx.
            "orphan_status": bool; Usually false. If true, this block is not part of the longest chain.
            "prev_hash": str; The hash of the block immediately preceding this block in the chain.
            "reward": unsigned int; The amount of new atomic units generated in this block and rewarded to the miner. Note: 1 XMR = 1e12 atomic units.
            "timestamp": unsigned int; The unix time at which the block was recorded into the blockchain.
        }
        "status": str; General RPC error code. "OK" means everything looks good.
        "untrusted": bool; True for bootstrap mode, False for full sync mode
        }
        """

        if height < 0:
            raise ValueError("height < 0")

        return self.raw_jsonrpc_request(
            "get_block_header_by_height", params={"height": height}
        )

    def get_block_headers_range(self, start_height, end_height):
        """
        Similar to get_block_header_by_height, but for a range of blocks. The range is inclusive,
        so the number of blocks returned will be equal to end_height - start_height + 1

        :param int start_height: starting height
        :param int end_height: ending height

        Output:
        {
        "headers": list; block_header structures (get_last_block_header) for the blocks in height range.
        "status": str; General RPC error code. "OK" means everything looks good.
        "untrusted": bool; True for bootstrap mode, False for full sync mode
        }
        """

        start_height = int(start_height)
        end_height = int(end_height)

        if start_height < 0:
            raise ValueError("start_height < 0")
        if end_height < start_height:
            raise ValueError("end_height < start_height")

        return self.raw_jsonrpc_request(
            "get_block_headers_range",
            params={"start_height": start_height, "end_height": end_height},
        )

    def get_block(self, height=None, hash=None):
        """
        Full block information can be retrieved by either block height or hash. Either height OR
        hash must be specified, but not both.

        :param int height: block height
        :param str hash: block hash

        Output:
        {
        "blob": str; Hexadecimal blob of block information.
        "block_header": A structure containing block header information. See get_last_block_header.
        "json": str; JSON formatted string details:
            "major_version": unsigned int; The major version of the monero protocol at this block height.
            "minor_version": unsigned int; The minor version of the monero protocol at this block height.
            "timestamp": unsigned int; The unix time at which the block was recorded into the blockchain.
            "prev_id": str; The hash of the block immediately preceding this block in the chain.
            "nonce": unsigned int; a cryptographic random one-time number used in mining a Monero block.
            "miner_tx": {
                "version": unsigned int; Transaction version number.
                "unlock_time": unsigned int; The block height when the coinbase transaction becomes spendable.
                "vin": list; List of transaction inputs with the following structure:
                    {
                        "gen": {        (note: miner txs are coinbase txs or "gen")
                            "height": This block height, a.k.a. when the coinbase is generated.
                        }
                    }
                "vout": list; List of transaction outputs with the following structures:
                    {
                        "amount"; unsigned int; The amount of the output, in atomic units.
                        "target": {
                            "key": str; public key of one-time output of miner tx.
                        }
                    }
                "extra"; list; List of integers 0-255, usually the "transaction ID" but can be used to include byte string.
                "rct_signatures" - Contain signatures of tx signers. Coinbased txs do not have signatures.
        "miner_tx_hash": str; hash of the coinbase transaction which belongs to this block.
        "tx_hashes": list; List of str hex hashes of non-coinbase transactions in the block.
        "status": str; General RPC error code. "OK" means everything looks good.
        "untrusted": bool; True for bootstrap mode, False for full sync mode.
        }
        """

        if height is None and hash is None:
            raise ValueError("height or hash must be provided")
        elif height is not None and hash is not None:
            raise ValueError("height and hash can not both be provided")

        if height is not None:
            if height < 0:
                raise ValueError("{} is not a valid height".format(height))

            params = {"height": int(height)}
        else:
            if not self._is_valid_256_hex(hash):
                raise ValueError('blk_hash "{}" is not a valid hash'.format(hash))

            params = {"hash": hash}

        return self.raw_jsonrpc_request("get_block", params=params)

    def get_connections(self):
        """
        Retrieve information about incoming and outgoing connections to your node.

        Output:
        {
        "connections": list; List of all connections and their info with the following structure:
            {
            "address": str; The peer's address, actually IPv4 & port
            "avg_download": unsigned int; Average bytes of data downloaded by node.
            "avg_upload": unsigned int; Average bytes of data uploaded by node.
            "connection_id": str; The connection ID
            "current_download": unsigned int; Current bytes downloaded by node.
            "current_upload": unsigned int; Current bytes uploaded by node.
            "height": unsigned int; The peer height
            "host": str; The peer host
            "incoming": bool; Is the node getting information from your node?
            "ip": str; The node's IP address.
            "live_time": unsigned int
            "local_ip": bool
            "localhost": bool
            "peer_id": str; The node's ID on the network.
            "port": str; The port that the node is using to connect to the network.
            "recv_count": unsigned int
            "recv_idle_time": unsigned int
            "send_count": unsigned int
            "send_idle_time": unsigned int
            "state": str
            "support_flags": unsigned int
            }
        }
        """

        return self.raw_jsonrpc_request("get_connections")

    def get_info(self):
        """
        Retrieve general information about the state of your node and the network.

        Output:
        {
        "alt_blocks_count": unsigned int; Number of alternative blocks to main chain.
        "block_size_limit": unsigned int; Maximum allowed block size
        "block_size_median": unsigned int; Median block size of latest 100 blocks
        "bootstrap_daemon_address": str; bootstrap node to give immediate usability to wallets while syncing by proxying RPC to it.
        "busy_syncing": bool; States if new blocks are being added (true) or not (false).
        "cumulative_difficulty": unsigned int; Cumulative difficulty of all blocks in the blockchain.
        "difficulty": unsigned int; Network difficulty (analogous to the strength of the network)
        "free_space": unsigned int; Available disk space on the node.
        "grey_peerlist_size": unsigned int; Grey Peerlist Size
        "height": unsigned int; Current length of longest chain known to daemon.
        "height_without_bootstrap": unsigned int; Current length of the local chain of the daemon.
        "incoming_connections_count": unsigned int; Number of peers connected to and pulling from your node.
        "mainnet": bool; States if the node is on the mainnet (true) or not (false).
        "offline": bool; States if the node is offline (true) or online (false).
        "outgoing_connections_count": unsigned int; Number of peers that you are connected to and getting information from.
        "rpc_connections_count": unsigned int; Number of RPC client connected to the daemon (Including this RPC request).
        "stagenet": bool; States if the node is on the stagenet (true) or not (false).
        "start_time": unsigned int; Start time of the daemon, as UNIX time.
        "status": str; General RPC error code. "OK" means everything looks good.
        "synchronized": bool; States if the node is synchronized (true) or not (false).
        "target": unsigned int; Current target for next proof of work.
        "target_height": unsigned int; The height of the next block in the chain.
        "testnet": bool; States if the node is on the testnet (true) or not (false).
        "top_block_hash": str; Hash of the highest block in the chain.
        "tx_count": unsigned int; Total number of non-coinbase transaction in the chain.
        "tx_pool_size": unsigned int; Number of transactions that have been broadcast but not included in a block.
        "untrusted": bool; True for bootstrap mode, False for full sync mode.
        "was_bootstrap_ever_used": bool; States if a bootstrap node has ever been used since the daemon started.
        "white_peerlist_size": unsigned int; White Peerlist Size
        }
        """

        return self.raw_jsonrpc_request("get_info")

    def hard_fork_info(self):
        """
        Look up information regarding hard fork voting and readiness.

        Output:
        {
        "earliest_height": unsigned int; Block height at which hard fork would be enabled if voted in.
        "enabled": bool; Tells if hard fork is enforced.
        "state": unsigned int; Current hard fork state: 0 (There is likely a hard fork), 1 (An update is needed to fork properly), or 2 (Everything looks good).
        "status": str; General RPC error code. "OK" means everything looks good.
        "threshold": unsigned int; Minimum percent of votes to trigger hard fork. Default is 80.
        "version": unsigned int; The major block version for the fork.
        "votes": unsigned int; Number of votes towards hard fork.
        "voting": unsigned int; Hard fork voting status.
        "window": unsigned int; Number of blocks over which current votes are cast. Default is 10080 blocks.
        }
        """

        return self.raw_jsonrpc_request("hard_fork_info")

    def set_bans(self, ip, ban, seconds=None):
        """
        Ban (or unban) other nodes by IP for a certain length of time.

        :param ip: ip address of node to ban in two forms: 'a.b.c.d' str or 32-bit unsigned integer
        :param bool ban: Whether to ban (True) or unban (False)
        :param int seconds: Number of seconds to ban. Optional if "ban" is False

        Notes:
        * Params "ip", "ban", and "seconds" can be single elements or they can be iterables of the same length. For example:

            ips =        ['229.52.8.67', 611282986]
            should_ban = [True,          False]
            seconds =    [10000,         None]
            daemon.set_bans(ips, should_ban, seconds)

        * "seconds" can be 0 or None if "ban" is False

        Output:
        {
        "status": str; General RPC error code. "OK" means everything looks good. Any other value means that something went wrong.
        }
        """

        if isinstance(
            ip, six.string_types + six.integer_types
        ):  # If single element paramters
            user_bans = [{"ip": ip, "ban": ban, "seconds": seconds}]
        else:  # If params are iterables, contrust the list of ban entries
            if not (len(ip) == len(ban) == len(seconds)):
                raise ValueError('"ip", "ban", and "seconds" are not the same length')

            user_bans = [
                {"ip": ip[i], "ban": ban[i], "seconds": seconds[i]}
                for i in range(len(ip))
            ]

        # Construct the bans parameter to be passed to the RPC command
        bans = []
        for ban_entry in user_bans:
            curr_ip = ban_entry["ip"]
            curr_ban = bool(ban_entry["ban"])
            curr_seconds = ban_entry["seconds"]

            # validate IP
            ipaddress.IPv4Address(curr_ip)

            if curr_ban and curr_seconds is None:
                raise ValueError('Whenever "ban" is True, "seconds" must not be None')
            elif curr_seconds is not None and curr_seconds < 0:
                raise ValueError('"seconds" can not be less than zero')

            ban = {}
            if isinstance(curr_ip, six.integer_types):
                ban["ip"] = curr_ip
            else:
                ban["host"] = curr_ip
            if curr_seconds is not None:
                ban["seconds"] = curr_seconds
            ban["ban"] = curr_ban

            bans.append(ban)

        return self.raw_jsonrpc_request("set_bans", params={"bans": bans})

    def get_bans(self):
        """
        Get list of ban entries. For structure of ban entires, see documentation of set_bans method.

        Output:
        {
        "bans": list; banned nodes with following structure
            {
                "host": str; Banned host (IP in A.B.C.D form).
                "ip": unsigned int; Banned IP address, in Int format.
                "seconds": unsigned int; Local Unix time that IP is banned until.
            }
        "status": str; General RPC error code. "OK" means everything looks good.
        }
        """

        resp = self.raw_jsonrpc_request("get_bans")

        # When there are no ban entries, the node returns a responses with no "bans" field.
        # This is counterintuitive for the user, so I add an empty field if it's not provided.
        if "bans" not in resp:
            resp["bans"] = []

        return resp

    def flush_txpool(self, txids=None):
        """
        Flush tx ids from transaction pool

        :param list txids: list of str; transactions IDs to flush from mempool (all tx ids flushed if empty).

        Output:
        {
        "status": str; General RPC error code. "OK" means everything looks good. Any other value means that something went wrong.
        }
        """

        txids = self._validate_hashlist(txids)

        resp = self.raw_jsonrpc_request("flush_txpool", params={"txids": txids})

        if "transactions" not in resp:
            resp["transactions"] = []

        return resp

    def get_output_histogram(
        self, amounts, min_count=None, max_count=None, unlocked=None, recent_cutoff=None
    ):
        """
        Get a histogram of output amounts. For all amounts (possibly filtered by parameters), gives the number
        of outputs on the chain for that amount. RingCT outputs counts as 0 amount.

        :param list amounts: list of unsigned ints in atomic units, or Decimals as full monero amounts
        :param int min_count: lower bound for output number
        :param int max_count: upper bound for output number
        :param bool unlocked: whether to count only unlocked
        :pramrm int recent_cutoff: unsigned int


        Output:
        {
        "histogram": list; histogram entries with the following structure
            {
            "amount": unsigned int; Output amount in atomic units.
            "total_instances": unsigned int; number of total instances for given amount.
            "unlocked_instances": unsigned int; number of unlocked instances for given amount.
            "recent_instances": unsigned int; number of recent instances for given amount.
            }
        "status - string; General RPC error code. "OK" means everything looks good.
        "untrusted": bool; True for bootstrap mode, False for full sync mode.
        }
        """

        # Coerce amounts paramter
        if isinstance(amounts, (Decimal,) + six.integer_types):
            amounts = [to_atomic(amounts) if isinstance(amounts, Decimal) else amounts]
        elif amounts is None:
            raise ValueError("amounts is None")

        # Construct RPC parameters
        params = {"amounts": amounts}
        if min_count is not None:
            params["min_count"] = int(min_count)
        if max_count is not None:
            params["max_count"] = int(max_count)
        if unlocked is not None:
            params["unlocked"] = bool(unlocked)
        if recent_cutoff is not None:
            params["recent_cutoff"] = int(recent_cutoff)

        return self.raw_jsonrpc_request("get_output_histogram", params=params)

    def get_coinbase_tx_sum(self, height, count):
        """
        Get the coinbase amount and the fees amount for n last blocks starting at particular height.

        :param int height: unsigned int; block height from which getting the amounts
        :param int count: unsigned int; number of blocks to include in the sum

        Output:
        {
        "emission_amount": unsigned int; amount of coinbase reward in atomic units
        "fee_amount": unsigned int; amount of fees in atomic units
        "status": str; General RPC error code. "OK" means everything looks good.
        }
        """

        if height < 0:
            raise ValueError("height < 0")
        elif count < 0:
            raise ValueError("count < 0")

        return self.raw_jsonrpc_request(
            "get_coinbase_tx_sum", params={"height": height, "count": count}
        )

    def get_version(self):
        """
        Get the node's current version.

        Output:
        {
        "version": unsigned int;
        "status": str; General RPC error code. "OK" means everything looks good.
        "untrusted": bool; True for bootstrap mode, False for full sync mode.
        }
        """
        return self.raw_jsonrpc_request("get_version")

    def get_fee_estimate(self, grace_blocks=None):
        """
        Gives an estimation on fees per byte.

        :param int grace_blocks: Optional; number of previous blocks to include in fee calculation

        Output:
        {
        "fee": unsigned int; Amount of fees estimated per byte in atomic units
        "quantization_mask": unsigned int; Final fee should be rounded up to an even multiple of this value
        "status": str; General RPC error code. "OK" means everything looks good.
        "untrusted": bool; True for bootstrap mode, False for full sync mode.
        }
        """

        if not isinstance(grace_blocks, (type(None),) + six.integer_types):
            raise TypeError("grace_blocks is not an int")
        elif grace_blocks is not None and grace_blocks < 0:
            raise ValueError("grace_blocks < 0")

        params = {"grace_blocks": grace_blocks} if grace_blocks else None
        return self.raw_jsonrpc_request("get_fee_estimate", params=params)

    def get_alternate_chains(self):
        """
        Display alternative chains seen by the node.


        Output:
        {
        "chains": list; chain informations with the following structure
            {
                "block_hash": str; the block hash of the first diverging block of this alternative chain.
                "difficulty": unsigned int; the cumulative difficulty of all blocks in the alternative chain.
                "height": unsigned int; the block height of the first diverging block of this alternative chain.
                "length": unsigned int; the length in blocks of this alternative chain, after divergence.
            }
        "status": str; General RPC error code. "OK" means everything looks good.
        }

        """

        return self.raw_jsonrpc_request("get_alternate_chains")

    def relay_tx(self, txids):
        """
        Relay a list of transaction IDs.

        :param list txids: list of transaction IDs to relay

        Output:
        {
        "status": str; General RPC error code. "OK" means everything looks good. Any other value means that something went wrong.
        }
        """

        txids = self._validate_hashlist(txids)

        return self.raw_jsonrpc_request("relay_tx", params={"txids": txids})

    def sync_info(self):
        """
        Get synchronisation information.

        Output:
        {
        "height": unsigned int; current height
        "peers": list; peer informations with the following structure
            {
                "info": dict; structure of connection info, as defined in get_connections
            }
        "spans": list; span informations with the follwing structure (absent if node is fully synced)
            {
                "connection_id": str; connection ID.
                "nblocks": unsigned int; number of blocks in that span.
                "rate": unsigned int; connection rate.
                "remote_address": str; peer address the node is downloading (or has downloaded) the span from.
                "size": unsigned int; total number of bytes in that span's blocks (including txes).
                "speed": unsigned int; connection speed.
                "start_block_height": unsigned int; block height of the first block in that span.
            }
        "status": str; General RPC error code. "OK" means everything looks good.
        "target_height": unsigned int; target height the node is syncing from (will be undefined if node is fully synced)
        }
        """

        return self.raw_jsonrpc_request("sync_info")

    # Other RPC Methods (https://www.getmonero.org/resources/developer-guides/daemon-rpc.html#other-daemon-rpc-calls)

    def get_height(self):
        """
        Get the node's current height.

        Outputs:
        {
        "height": unsigned int; Current length of longest chain known to daemon.
        "status": str; General RPC error code. "OK" means everything looks good.
        "untrusted": bool; True for bootstrap mode, False for full sync mode.
        }
        """

        return self.raw_request("/get_height")

    def get_transactions(self, tx_hashes, decode_as_json=False, prune=False):
        """
        Look up one or more transactions by hash.

        :param list txs_hashes: List of transaction hashes to look up.
        :param bool decode_as_json: Optional (false by default). If true, the returned tx info will be decoded into JSON.
        :param bool prune: Optional (false by default). If true, prune blob data, greatly cutting down on response size.


        Output:
        {
        "missed_tx": list; (Optional - returned if not empty) Transaction hashes that could not be found.
        "status": str; General RPC error code. "OK" means everything looks good.
        "txs": list; transaction informations with the following structure
            {
                "as_hex": stri; Full transaction information as a hex string.
                "as_json": json str; JSON formatted as follows
                    {
                        "version": unsigned int; Transaction version
                        "unlock_time": unsigned int; If not 0, this tells when a transaction output is spendable.
                        "vin": list; transaction inputs with the following structure
                            {
                                "key":
                                {
                                    "amount": unsigned int; The amount of the input, in atomic units.
                                    "key_offsets": list; integer offets to the input.
                                    "k_image": str; The key image for the given input
                                }

                            }
                        "vout": list; transaction inputs with the following structure
                            {
                                "amount": unsigned int; Amount of transaction output, in atomic units.
                                "target":
                                {
                                    "key": str; The stealth public key of the receiver.
                                }
                            }
                        "extra"; list; List of integers 0-255, usually the "transaction ID" but can be used to include byte string.
                        signatures - List of signatures used in ring signature to hide the true origin of the transaction.
                    }
                "block_height": unsigned int; block height including the transaction
                "block_timestamp": unsigned int; Unix time at chich the block has been added to the blockchain
                "double_spend_seen": boolean; States if the transaction is a double-spend (true) or not (false)
                "in_pool": bool; States if the transaction is in pool (true) or included in a block (false)
                "output_indices": list; list of the tx's output's globals indexes as unsigned ints
                "tx_hash": str; transaction hash
            }
        "txs_as_hex": str; Full transaction information as a hex string (old compatibility parameter)
        "txs_as_json": json str; (Optional - returned if set in inputs. Old compatibility parameter) List of transaction as in as_json above:
        }
        """

        tx_hashes = self._validate_hashlist(tx_hashes)

        return self.raw_request(
            "/get_transactions",
            data={
                "txs_hashes": tx_hashes,
                "decode_as_json": bool(decode_as_json),
                "prune": bool(prune),
            },
        )

    def get_alt_blocks_hashes(self):
        """
        Get the known blocks hashes which are not on the main chain.

        Output:
        {
        "blks_hashes"; list; alternative blocks hashes to main chain
        "status": str; General RPC error code. "OK" means everything looks good.
        "untrusted": bool; True for bootstrap mode, False for full sync mode.
        }
        """

        return self.raw_request("/get_alt_blocks_hashes")

    def is_key_image_spent(self, key_images):
        """
        Check if outputs have been spent using the key image associated with the output.

        :param list key_images: List of key image hex strings to check.

        Key Image Status Legend:
            0 = unspent
            1 = spent in blockchain
            2 = spent in transaction pool

        Outputs:
        {
        "spent_status": list of unsigned ints; List of statuses for each image checked.
        "status": str; General RPC error code. "OK" means everything looks good.
        "untrusted": bool; True for bootstrap mode, False for full sync mode.
        }
        """

        key_images = self._validate_hashlist(key_images)

        return self.raw_request("/is_key_image_spent", data={"key_images": key_images})

    def send_raw_transaction(self, tx_as_hex, do_not_relay=False):
        """
        Broadcast a raw transaction to the network.

        :param str tx_as_hex: Full transaction information as hexidecimal string.
        :param bool do_not_relay: Optional; Stop relaying transaction to other nodes (default is false).

        Output:
        {
        "double_spend": bool; Transaction is a double spend (true) or not (false).
        "fee_too_low": bool; Fee is too low (true) or OK (false).
        "invalid_input": bool; Input is invalid (true) or valid (false).
        "invalid_output": bool; Output is invalid (true) or valid (false).
        "low_mixin": bool; Mixin count is too low (true) or OK (false).
        "not_rct": bool; Transaction is a standard ring transaction (true) or a ring confidential transaction (false).
        "not_relayed": bool; Transaction was not relayed (true) or relayed (false).
        "overspend": bool; Transaction uses more money than available (true) or not (false).
        "reason": str; Additional information. Currently empty or "Not relayed" if transaction was accepted but not relayed.
        "too_big": bool; Transaction size is too big (true) or OK (false).
        "status": str; General RPC error code. "OK" means everything looks good.
        "untrusted": bool; True for bootstrap mode, False for full sync mode.
        }
        """

        tx_as_hex = six.ensure_text(tx_as_hex)

        return self.raw_request(
            "/send_raw_transaction",
            data={"tx_as_hex": tx_as_hex, "do_not_relay": do_not_relay},
        )

    def start_mining(
        self, do_background_mining, ignore_battery, miner_address, threads_count
    ):
        """
        Start mining on the daemon.

        :param bool do_background_mining: States if the mining should run in background (true) or foreground (false).
        :param bool ignore_battery: States if batery state (on laptop) should be ignored (true) or not (false).
        :param str miner_address: Account address to mine to.
        :param int threads_count: Number of mining thread to run.

        Output:
        {
        "status": str; General RPC error code. "OK" means everything looks good. Any other value means that something went wrong.
        }
        """

        if isinstance(miner_address, address.Address):
            miner_address = repr(miner_address)
        else:
            try:
                converted_addr = address.address(miner_address)
            except ValueError:
                raise ValueError(
                    'miner_address "{}" does not match any recognized address format'.format(
                        miner_address
                    )
                )

            if not isinstance(converted_addr, address.Address):
                raise ValueError(
                    'miner_address must be a "standard" monero address (i.e. it must start with a "4")'
                )

        if not isinstance(threads_count, int):
            raise TypeError("threads_count must be an int")

        if threads_count < 0:
            raise ValueError("threads_count < 0")

        return self.raw_request(
            "/start_mining",
            data={
                "do_background_mining": bool(do_background_mining),
                "ignore_battery": bool(ignore_battery),
                "miner_address": miner_address,
                "threads_count": threads_count,
            },
        )

    def stop_mining(self):
        """
        Stop mining on the daemon.

        Output:
        {
        "status": str; General RPC error code. "OK" means everything looks good. Any other value means that something went wrong.
        }
        """

        return self.raw_request("/stop_mining")

    def mining_status(self):
        """
        Get the mining status of the daemon.

        Output:
        {
        "active": bool; States if mining is enabled (true) or disabled (false).
        "address": str; Account address daemon is mining to. Empty if not mining.
        "is_background_mining_enabled": bool; States if the mining is running in background (true) or foreground (false).
        "speed": unsigned int; Mining power in hashes per seconds.
        "threads_count": unsigned int; Number of running mining threads.
        "status":  str; General RPC error code. "OK" means everything looks good. Any other value means that something went wrong.
        }
        """

        return self.raw_request("/mining_status")

    def save_bc(self):
        """
        Save the blockchain. The blockchain does not need saving and is always saved when modified, however it does a sync to
        flush the filesystem cache onto the disk for safety purposes against Operating System or Harware crashes.

        Output:
        {
        "status": str; General RPC error code. "OK" means everything looks good. Any other value means that something went wrong.
        }
        """

        return self.raw_request("/save_bc")

    def get_peer_list(self):
        """
        Get the known peer list.

        Outputs:
        {
        "gray_list": list; offline peer informations with the following structure
            {
                "host": unsigned int; IP address in integer format.
                "id": stri; Peer id.
                "ip": unsigned int; IP address in integer format.
                "last_seen": unsigned int; unix time at which the peer has been seen for the last time.
                "port": unsigned int; TCP port the peer is using to connect to monero network.
            }
        "white_list": list; online peer informations with the above structure ^^^
        "status": str; General RPC error code. "OK" means everything looks good. Any other value means that something went wrong.
        }
        """

        return self.raw_request("/get_peer_list")

    def set_log_hash_rate(self, visible):
        """
        Set the log hash rate display mode.

        :param bool visible: States if hash rate logs should be visible (true) or hidden (false)

        Output:
        {
        "status": str; General RPC error code. "OK" means everything looks good. Any other value means that something went wrong.
        }
        """

        resp = self.raw_request("/set_log_hash_rate", data={"visible": bool(visible)})

        if resp["status"] == "NOT MINING":
            raise RPCError(
                'The node at "{url}" is not currently mining and therefore cannot set its hash rate log visibility.'.format(
                    url=self.url
                )
            )

        return resp

    def set_log_level(self, level):
        """
        Set the daemon log level. By default, log level is set to 0.

        :param int level: daemon log level to set from 0 (less verbose) to 4 (most verbose)

        Output:
        {
        "status": str; General RPC error code. "OK" means everything looks good. Any other value means that something went wrong.
        }
        """

        if level not in range(5):
            raise ValueError(
                "level must an integer between 0 (less verbose) and 4 (more verbose), inclusive"
            )

        return self.raw_request("/set_log_level", data={"level": level})

    def set_log_categories(self, categories=None):
        """
        Set the daemon log categories. Categories are represented as a comma separated list of
        <Category>:<level> (similarly to syslog standard <Facility>:<Severity-level>).
        To get a list of all log categories known by this library, call JSONRPCDaemon.get_all_known_log_categories().
        To get a list of all log levels known by this library, call JSONRPCDaemon.get_all_known_log_levels().

        :param categories: str or list; Optional, daemon log categories to enable. Accepts list or comma-seperated string.

        Output:
        {
        "categories": str; comma-seperated string list of daemon log enabled categories
        "status": str; General RPC error code. "OK" means everything looks good. Any other value means that something went wrong.
        }
        """

        if not categories:
            return self.raw_request("/set_log_categories")
        elif isinstance(categories, six.string_types):
            categories = categories.split(",")

        # Validate categories
        for cat_str in categories:
            try:
                category, level = cat_str.split(":")

                if category not in self._KNOWN_LOG_CATEGORIES:
                    _log.warn('Unrecognized log category: "{}"'.format(category))

                if level not in self._KNOWN_LOG_LEVELS:
                    _log.warn('Unrecognized log level: "{}"'.format(level))
            except ValueError:
                raise ValueError('malformed category string: "{}"'.format(cat_str))

        final_category_str = ",".join(categories)

        return self.raw_request(
            "/set_log_categories", data={"categories": final_category_str}
        )

    def get_transaction_pool(self):
        """
        Show information about valid transactions seen by the node but not yet mined into a block,
        as well as spent key image information for the txpool in the node's memory.

        Output:
        {
        "spent_key_images": list; spent output key images with following structure
            {
                "id_hash": str; Key image.
                "txs_hashes": list; tx hashes of the txes (usually one) spending that key image.
            }
        "transactions": list; transactions in the mempool with the following structure
            {
                "blob_size": unsigned int; The size of the full transaction blob.
                "double_spend_seen": bool; States if this transaction has been seen as double spend.
                "do_not_relay": bool; States if this transaction should not be relayed
                "fee": unsigned int; The amount of the mining fee included in the transaction, in atomic units.
                "id_hash": str; The transaction ID hash.
                "kept_by_block": bool; States if the tx was included in a block at least once (true) or not (false).
                "last_failed_height": unsigned int; If the transaction validation has previously failed, this tells at what height that occured.
                "last_failed_id_hash": str; Like the previous, this tells the previous transaction ID hash.
                "last_relayed_time": unsigned int; Last unix time at which the transaction has been relayed.
                "max_used_block_height": unsigned int; Tells the height of the most recent block with an output used in this transaction.
                "max_used_block_hash": str; Tells the hash of the most recent block with an output used in this transaction.
                "receive_time": unsigned int; The Unix time that the transaction was first seen on the network by the node.
                "relayed": bool; States if this transaction has been relayed
                "tx_blob": unsigned int; Hexadecimal blob represnting the transaction.
                "tx_json": json string; JSON structure of all information in the transaction (see get_transactions() for structure information)
            }
        "status": str; General RPC error code. "OK" means everything looks good.
        }
        """

        return self.raw_request("/get_transaction_pool")

    def get_transaction_pool_stats(self):
        """
        Get the transaction pool statistics.

        Output:
        {
        "pool_stats": {
            "bytes_max": unsigned int; Max transaction size in pool.
            "bytes_med" unsigned int; Median transaction size in pool.
            "bytes_min" unsigned int; Min transaction size in pool.
            "bytes_total": unsigned int; total size of all transactions in pool.
            "histo": list; histogram of transaction sizes with the following structure
                {
                    "txs": unsigned int; number of transactions.
                    "bytes": unsigned int; size in bytes.
                }
            "histo_98pc": unsigned int; the time 98% of txes are "younger" than.
            "num_10m": unsigned int; number of transactions in pool for more than 10 minutes.
            "num_double_spends": unsigned int; number of double spend transactions.
            "num_failing": unsigned int; number of failing transactions.
            "num_not_relayed": unsigned int; number of non-relayed transactions.
            "oldest": unsigned int; unix time of the oldest transaction in the pool
            "txs_total": unsigned int; total number of transactions.
        }
        "status": str; General RPC error code. "OK" means everything looks good.
        "untrusted": bool; True for bootstrap mode, False for full sync mode.
        }
        """

        return self.raw_request("/get_transaction_pool_stats")

    def stop_daemon(self):
        """
        Send a command to the daemon to safely disconnect and shut down.

        Output:
        {
        "status": str; General RPC error code. "OK" means everything looks good. Any other value means that something went wrong.
        }
        """

        return self.raw_request("/stop_daemon")

    def get_limit(self):
        """
        Get daemon bandwidth limits.

        Outputs:
        {
        "limit_down": unsigned int; Download limit in kBytes per second
        "limit_up": unsigned int; Upload limit in kBytes per second
        "status": str; General RPC error code. "OK" means everything looks good.
        "untrusted": bool; True for bootstrap mode, False for full sync mode.
        }
        """

        return self.raw_request("/get_limit")

    def set_limit(self, limit_down=-1, limit_up=-1):
        """
        Set daemon bandwidth limits.

        :param int limit_down: Download limit in kBytes per second (-1 reset to default, 0 don't change the current limit)
        :param int limit_up: Upload limit in kBytes per second (-1 reset to default, 0 don't change the current limit)

        Output:
        {
        "limit_down": - unsigned int; Download limit in kBytes per second
        "limit_up": unsigned int; Upload limit in kBytes per second
        "status": str; General RPC error code. "OK" means everything looks good.
        }
        """

        if limit_down < -1:
            raise ValueError("invalid limit_down: {}".format(limit_down))
        elif limit_up < -1:
            raise ValueError("invalid limit_up: {}".format(limit_up))

        return self.raw_request(
            "/set_limit", data={"limit_down": limit_down, "limit_up": limit_up}
        )

    def out_peers(self, out_peers_arg):
        """
        Limit number of outgoing peers.

        :param int out_peers_arg: Max number of outgoing peers. If less than zero, allow unlimited outgoing peers

        Output:
        {
        "status": str; General RPC error code. "OK" means everything looks good. Any other value means that something went wrong.
        }
        """

        if out_peers_arg < 0:
            out_peers_arg = 2 ** 32 - 1
        elif out_peers_arg > 2 ** 32 - 1:
            raise ValueError('out_peers_arg "{}" is too large'.format(out_peers_arg))

        return self.raw_request("/out_peers", data={"out_peers": int(out_peers_arg)})

    def in_peers(self, in_peers_arg):
        """
        Limit number of incoming peers.

        :param int in_peers_arg: Max number of incoming peers. If less than zero, allow unlimited incoming peers

        Output:
        {
        "status": str; General RPC error code. "OK" means everything looks good. Any other value means that something went wrong.
        }
        """

        if in_peers_arg < 0:
            in_peers_arg = 2 ** 32 - 1
        elif in_peers_arg > 2 ** 32 - 1:
            raise ValueError('in_peers_arg "{}" is too large'.format(in_peers_arg))

        return self.raw_request("/in_peers", data={"in_peers": int(in_peers_arg)})

    def get_outs(self, amount, index, get_txid=True):
        """
        Get information about one-time outputs (stealth addresses).


        :param amount: list or single element of output amount. Decimal for full monero amounts or int for atmoic units
        :param index: list of single element of output index. int
        :param bool get_txid: Optional. If true, a txid will included for each output in the response.

        Output:
        {
        "outs": list; output informations with the following structure
            {
                "height": unsigned int; block height of the output
                "key": str; the public key of the output
                "mask": str;
                "txid": str; transaction id
                "unlocked": bool; States if output is locked (false) or not (true)
            }
        "status": str; General RPC error code. "OK" means everything looks good.
        "untrusted": bool; True for bootstrap mode, False for full sync mode.
        }
        """

        if isinstance(index, six.integer_types):  # single element
            outputs = [
                {
                    "amount": amount
                    if isinstance(amount, six.integer_types)
                    else to_atomic(amount),
                    "index": index,
                }
            ]
        else:  # multiple elements
            if len(amount) != len(index):
                raise ValueError("length of amount and index do not match")

            outputs = []
            for a, i in zip(amount, index):
                outputs.append(
                    {
                        "amount": a
                        if isinstance(a, six.integer_types)
                        else to_atomic(a),
                        "index": i,
                    }
                )

        return self.raw_request(
            "/get_outs", data={"outputs": outputs, "get_txid": get_txid}
        )

    def update(self, command, path=None):
        """
        Update daemon.


        :param str command: Command to use, either "check" or "download".
        :param str path: Optional, path where to download the update.


        Output:
        {
        "auto_uri": str;
        "hash": str;
        "path": str; path to download the update.
        "update": bool; States if an update is available to download (true) or not (false).
        "user_uri": str;
        "version": str; Version available for download.
        "status": str; General RPC error code. "OK" means everything looks good.
        }
        """

        command = six.ensure_text(command)
        path = six.ensure_text(path) if path is not None else None

        if command not in ("check", "download"):
            raise ValueError('unrecognized command: "{}"'.format(command))

        data = {"command": command}

        if path is not None:
            data["path"] = path

        return self.raw_request("/update", data=data)

    # Supporting class methods

    @classmethod
    def known_log_categories(cls):
        return cls._KNOWN_LOG_CATEGORIES

    @classmethod
    def known_log_levels(cls):
        return cls._KNOWN_LOG_LEVELS

    # private methods

    def _set_net(self, info):
        if info["mainnet"]:
            self._net = NET_MAIN
        if info["testnet"]:
            self._net = NET_TEST
        if info["stagenet"]:
            self._net = NET_STAGE

    def _set_restricted(self):
        try:
            self.sync_info()

            self._restricted = False
        except MethodNotFound:
            self._restricted = True

    def _do_get_transactions(self, hashes, prune):
        res = self.raw_request(
            "/get_transactions",
            {"txs_hashes": hashes, "decode_as_json": True, "prune": prune},
        )
        if res["status"] != "OK":
            raise exceptions.BackendException(res["status"])
        txs = []
        for tx in res.get("txs", []):
            as_json = json.loads(tx["as_json"])
            fee = as_json.get("rct_signatures", {}).get("txnFee")
            txs.append(
                Transaction(
                    hash=tx["tx_hash"],
                    fee=from_atomic(fee) if fee else None,
                    height=None if tx["in_pool"] else tx["block_height"],
                    timestamp=datetime.fromtimestamp(tx["block_timestamp"])
                    if "block_timestamp" in tx
                    else None,
                    blob=binascii.unhexlify(tx["as_hex"]) or None,
                    json=as_json,
                )
            )

        return txs

    def _is_valid_256_hex(self, hexhash):
        try:
            bytearray.fromhex(hexhash)

            return len(hexhash) == 64
        except ValueError:
            return False

    def _validate_hashlist(self, hashes):
        if not hashes:
            return []
        else:
            if isinstance(hashes, six.string_types):
                hashes = [hashes]
            else:
                coerce_compatible_str = lambda s: six.ensure_text(str(s))
                hashes = list(map(coerce_compatible_str, hashes))

            not_valid = lambda h: not self._is_valid_256_hex(h)

            if any(map(not_valid, hashes)):
                raise ValueError("hashes contains an invalid hash")

            return hashes
