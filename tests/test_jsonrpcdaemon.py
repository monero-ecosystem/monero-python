import decimal
import json
import logging
import os
import responses

from monero.const import NET_STAGE
from monero.daemon import Daemon
from monero.backends.jsonrpc import JSONRPCDaemon, RPCError
from monero.exceptions import TransactionWithoutBlob, DaemonIsBusy
from monero.transaction import Transaction

from .base import JSONTestCase

class JSONRPCDaemonTestCase(JSONTestCase):
    jsonrpc_url = 'http://127.0.0.1:18081/json_rpc'
    mempool_url = 'http://127.0.0.1:18081/get_transaction_pool'
    transactions_url = 'http://127.0.0.1:18081/get_transactions'
    sendrawtransaction_url = 'http://127.0.0.1:18081/sendrawtransaction'
    data_subdir = 'test_jsonrpcdaemon'

    def setUp(self):
        self.daemon = Daemon(JSONRPCDaemon())
        self.backend = self.daemon._backend

        # this is disabled b/c raw_request logs errors
        logging.getLogger('monero.backends.jsonrpc.daemon').disabled = True

    @responses.activate
    def test_basic_info(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_basic_info-get_info.json'),
            status=200)
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_basic_info-get_info.json'),
            status=200)
        self.assertTrue(self.daemon.info())
        self.assertEqual(self.daemon.height(), 294993)

    @responses.activate
    def test_net(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_basic_info-get_info.json'),
            status=200)
        self.assertEqual(self.daemon.net, NET_STAGE)
        self.daemon.net
        self.assertEqual(len(responses.calls), 1, "net value has not been cached?")

    @responses.activate
    def test_info_then_net(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_basic_info-get_info.json'),
            status=200)
        self.daemon.info()
        self.assertEqual(self.daemon.net, NET_STAGE)
        self.assertEqual(len(responses.calls), 1, "net value has not been cached?")

    @responses.activate
    def test_mempool(self):
        responses.add(responses.POST, self.mempool_url,
            json=self._read('test_mempool-transactions.json'),
            status=200)
        txs = self.daemon.mempool()
        self.assertEqual(len(txs), 2)
        self.assertEqual(txs[0].confirmations, 0)
        self.assertEqual(txs[1].confirmations, 0)
        self.assertGreater(txs[0].fee, 0)
        self.assertGreater(txs[1].fee, 0)

    @responses.activate
    def test_block(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read("test_block-423cd4d170c53729cf25b4243ea576d1e901d86e26c06d6a7f79815f3fcb9a89.json"),
            status=200)
        responses.add(responses.POST, self.transactions_url,
            json=self._read("test_block-423cd4d170c53729cf25b4243ea576d1e901d86e26c06d6a7f79815f3fcb9a89-txns.json"),
            status=200)
        blk = self.daemon.block("423cd4d170c53729cf25b4243ea576d1e901d86e26c06d6a7f79815f3fcb9a89")
        self.assertEqual(
            blk.hash,
            "423cd4d170c53729cf25b4243ea576d1e901d86e26c06d6a7f79815f3fcb9a89")
        self.assertEqual(blk.height, 451992)
        self.assertIsInstance(blk.reward, decimal.Decimal)

        self.assertIn("24fb42f9f324082658524b29b4cf946a9f5fcfa82194070e2f17c1875e15d5d0", blk)
        for tx in blk.transactions:
            self.assertIn(tx, blk)

        # tx not in block
        self.assertNotIn("e3a3b8361777c8f4f1fd423b86655b5c775de0230b44aa5b82f506135a96c53a", blk)
        # wrong arg type
        self.assertRaises(ValueError, lambda txid: txid in blk, 1245)

        # block or hash not specified
        with self.assertRaises(ValueError):
            self.daemon.block()

    @responses.activate
    def test_transactions(self):
        responses.add(responses.POST, self.transactions_url,
            json=self._read('test_transactions_pruned.json'),
            status=200)
        txs = self.daemon.transactions([
            "050679bd5717cd4c3d0ed1db7dac4aa7e8a222ffc7661b249e5a595a3af37d3c",     # @471570
            "e3a3b8361777c8f4f1fd423b86655b5c775de0230b44aa5b82f506135a96c53a",     # @451993
            "e2871c4203e29433257219bc20fa58c68dc12efed8f05a86d59921969a2b97cc",     # @472279
            "035a1cfadd2f80124998f5af8c7bb6703743a4f322d0a20b7f7b502956ada59d",     # mempool
            "feed00000000000face00000000000bad00000000000beef00000000000acab0",     # doesn't exist
        ])
        self.assertEqual(len(txs), 4)
        self.assertEqual(txs[0].hash,
                "050679bd5717cd4c3d0ed1db7dac4aa7e8a222ffc7661b249e5a595a3af37d3c")
        self.assertEqual(txs[0].height, 471570)
        with self.assertRaises(TransactionWithoutBlob):
            txs[0].size
        self.assertEqual(txs[0].fee, decimal.Decimal('0.000331130000'))
        self.assertIsNone(txs[0].blob)
        self.assertEqual(txs[1].hash,
                "e3a3b8361777c8f4f1fd423b86655b5c775de0230b44aa5b82f506135a96c53a")
        self.assertEqual(txs[1].height, 451993)
        with self.assertRaises(TransactionWithoutBlob):
            txs[1].size
        self.assertEqual(txs[1].fee, decimal.Decimal('0.000265330000'))
        self.assertIsNone(txs[1].blob)
        self.assertEqual(txs[2].hash,
                "e2871c4203e29433257219bc20fa58c68dc12efed8f05a86d59921969a2b97cc")
        self.assertEqual(txs[2].height, 472279)
        with self.assertRaises(TransactionWithoutBlob):
            txs[2].size
        self.assertEqual(txs[2].fee, decimal.Decimal('0.000327730000'))
        self.assertIsNone(txs[2].blob)
        self.assertEqual(txs[3].hash,
                "035a1cfadd2f80124998f5af8c7bb6703743a4f322d0a20b7f7b502956ada59d")
        self.assertIsNone(txs[3].height)
        with self.assertRaises(TransactionWithoutBlob):
            txs[3].size
        self.assertEqual(txs[3].fee, decimal.Decimal('0.000320650000'))
        self.assertIsNone(txs[3].blob)

    @responses.activate
    def test_transactions_single(self):
        responses.add(responses.POST, self.transactions_url,
            json=self._read('test_transactions_single_pruned.json'),
            status=200)

        tx = self.daemon.transactions('bbc10f5944cc3e88be576d2ab9f4f5ab5a2b46d95a7cab1027bc15c17393102c')[0]

        self.assertEqual(tx.height, 2279770)
        self.assertIsNone(tx.blob)

    @responses.activate
    def test_transaction_not_pruned(self):
        daemon_no_prune = Daemon(JSONRPCDaemon(prune_transactions=False))
        responses.add(responses.POST, self.transactions_url,
            json=self._read('test_transactions_single.json'),
            status=200)

        tx = daemon_no_prune.transactions('bbc10f5944cc3e88be576d2ab9f4f5ab5a2b46d95a7cab1027bc15c17393102c')[0]
        self.assertIsNotNone(tx.blob)
        self.assertIs(type(tx.blob), bytes)

    @responses.activate
    def test_send_transaction(self):
        path = os.path.join(
            os.path.dirname(__file__),
            "data",
            self.data_subdir,
            "0e8fa9202e0773333360e5b9e8fb8e94272c16a8a58b6fe7cf3b4327158e3a44.tx")
        responses.add(responses.POST, self.sendrawtransaction_url,
            json=self._read('test_send_transaction.json'),
            status=200)

        with open(path, "rb") as blob_file:
            tx = Transaction(blob=blob_file.read())
            rsp = self.daemon.send_transaction(tx)
            self.assertEqual(rsp["status"], "OK")

    @responses.activate
    def test_chunking(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_chunking-10-block-693324.json'),
            status=200)
        responses.add(responses.POST, self.transactions_url,
            json=self._read('test_chunking-20-get_transactions_1of2.json'),
            status=200)
        responses.add(responses.POST, self.transactions_url,
            json=self._read('test_chunking-20-get_transactions_2of2.json'),
            status=200)
        blk = self.daemon.block(height=693324)
        self.assertEqual(len(blk.transactions), 105)
        self.assertEqual(len(set(blk.transactions)), 105)

    @responses.activate
    def test_headers(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_headers_2279790_2279799.json'),
            status=200)
        headers = self.daemon.headers(2279790, 2279799)
        self.assertEqual(len(headers), 10)
        self.assertEqual(headers[0]['hash'], '2763e0b9738c46317602a8e338b6b3ece893be4b9e1c4586824beb4f33286992')
        self.assertEqual(headers[9]['nonce'], 275623)

    @responses.activate
    def test_invalid_param(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_invalid_param.json'),
            status=200)
        with self.assertRaises(RPCError):
            blk = self.daemon.block(height=-1)

    def test_init_default_backend(self):
        daemon1 = Daemon(host='localhost')
        daemon2 = Daemon()

        with self.assertRaises(ValueError):
            daemon3 = Daemon(backend=JSONRPCDaemon(), port=18089)

    @responses.activate
    def test_busy_daemon(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_get_last_block_header_BUSY.json'),
            status=200)

        with self.assertRaises(DaemonIsBusy):
            self.backend.get_last_block_header()

    # Start testing all JSONRPC commands
    @responses.activate
    def test_get_block_count(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_get_block_count_2287024.json'),
            status=200)

        resp = self.backend.get_block_count()

        self.assertEqual(resp['status'], 'OK')
        self.assertEqual(resp['count'], 2287024)

    @responses.activate
    def test_on_get_block_hash(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_on_get_block_hash_2000000.json'),
            status=200)

        self.assertEqual(
            self.backend.on_get_block_hash(2000000),
            'dc2ef85b049311814742f543469e3ec1b8d589e68434d9f220ce41072c69c39e')

        with self.assertRaises(ValueError):
            self.backend.on_get_block_hash(-2023)

    @responses.activate
    def test_get_block_template(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_get_block_template_481SgRxo_64.json'),
            status=200)

        resp = self.backend.get_block_template(
            '481SgRxo8hwBCY4z6r88JrN5X8JFCJYuJUDuJXGybTwaVKyoJPKoGj3hQRAEGgQTdmV1xH1URdnHkJv6He5WkEbq6iKhr94',
            reserve_size=64)

        self.assertTrue(resp['blocktemplate_blob'].startswith(
            '0e0ec890de8006fbe94dbaf09e5fc4431460ede46c0e7c3db4adf1f0a6f34c5a0f5144e6d9dd27'))
        self.assertTrue(resp['blockhashing_blob'].startswith(
            '0e0ec890de8006fbe94dbaf09e5fc4431460ede46c0e7c3db4adf1f0a6f34c5a0f5144e6d9dd27'))
        self.assertEqual(resp['difficulty'], 232871166515)
        self.assertEqual(resp['difficulty_top64'], 0)
        self.assertEqual(resp['expected_reward'], 1180703555413)
        self.assertEqual(resp['height'], 2287042)
        self.assertEqual(resp['prev_hash'], 'fbe94dbaf09e5fc4431460ede46c0e7c3db4adf1f0a6f34c5a0f5144e6d9dd27')
        self.assertEqual(resp['reserved_offset'], 130)
        self.assertEqual(resp['seed_hash'], 'd432f499205150873b2572b5f033c9c6e4b7c6f3394bd2dd93822cd7085e7307')
        self.assertEqual(resp['seed_height'], 2285568)
        self.assertEqual(resp['status'], 'OK')
        self.assertEqual(resp['untrusted'], False)
        self.assertEqual(resp['wide_difficulty'], '0x3638340233')

        with self.assertRaises(ValueError):
            self.backend.get_block_template(
                '481SgRxo8hwBCY4z6r88JrN5X8JFCJYuJUDuJXGybTwaVKyoJPKoGj3hQRAEGgQTdmV1xH1URdnHkJv6He5WkEbq6iKhr94',
                -49)

        with self.assertRaises(ValueError):
            self.backend.get_block_template(
                'ThisIsAnInvalidWalletAddressSoThisShouldThrowAnError',
                30)

    @responses.activate
    def test_submit_block(self):
        # @TODO I need a more thorough test for this routine, but I do have have an example of a response for a successfully
        # mined block, sadly. Maybe we can use the project donations to purchase an AMD EPYC 7742 for "research" ;)
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_submit_block_failure.json'),
            status=200)

        with self.assertRaises(RPCError):
            self.backend.submit_block(b'this is not a block and should not work')

    @responses.activate
    def test_get_last_block_header(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_get_last_block_header_success.json'),
            status=200)

        resp = self.backend.get_last_block_header()

        self.assertEqual(resp['status'], 'OK')

        block_header = resp['block_header']

        self.assertEqual(block_header['block_size'], 65605)
        self.assertEqual(block_header['block_weight'], 65605)
        self.assertEqual(block_header['cumulative_difficulty'], 86426998743673801)
        self.assertEqual(block_header['cumulative_difficulty_top64'], 0)
        self.assertEqual(block_header['wide_cumulative_difficulty'], "0x1330ce5bf1eabc9")
        self.assertEqual(block_header['depth'], 0)
        self.assertEqual(block_header['difficulty'], 253652891944)
        self.assertEqual(block_header['difficulty_top64'], 0)
        self.assertEqual(block_header['wide_difficulty'], "0x3b0ee3f928")
        self.assertEqual(block_header['hash'], "a55ec867052340715c4b8b4dcd2de53bc2a195e666058d10a224037932ccdc40")
        self.assertEqual(block_header['height'], 2287573)
        self.assertEqual(block_header['long_term_weight'], 65605)
        self.assertEqual(block_header['major_version'], 14)
        self.assertEqual(block_header['minor_version'], 14)
        self.assertEqual(block_header['miner_tx_hash'], "42219818a7f30910a89e0d0d9fc479950137b93820e5955fc071fa8f4e3c2400")
        self.assertEqual(block_header['nonce'], 37920)
        self.assertEqual(block_header['num_txes'], 34)
        self.assertEqual(block_header['orphan_status'], False)
        self.assertEqual(block_header['pow_hash'], "")
        self.assertEqual(block_header['prev_hash'], "7ca630666d7040f0cadbaaf9da92db4797ef67b60ca8f15324b94236ffe0b3a8")
        self.assertEqual(block_header['reward'], 1181081601887)
        self.assertEqual(block_header['timestamp'], 1612215053)

    @responses.activate
    def test_get_block_header_by_hash(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_get_block_header_by_hash_90f6fd3f.json'),
            status=200)

        resp = self.backend.get_block_header_by_hash('90f6fd3fe29c7518f15afd2da31734e890cc24247b5da10dc9ac2ea215ae844b')

        self.assertIn('block_header', resp)
        self.assertIn('status', resp)
        self.assertIn('untrusted', resp)

        block_header = resp['block_header']

        self.assertEqual(block_header['block_size'], 17130)
        self.assertEqual(block_header['block_weight'], 17130)
        self.assertEqual(block_header['cumulative_difficulty'], 86641187797059581)
        self.assertEqual(block_header['cumulative_difficulty_top64'], 0)
        self.assertEqual(block_header['wide_cumulative_difficulty'], "0x133cfb3858fc7fd")
        self.assertEqual(block_header['depth'], 4)
        self.assertEqual(block_header['difficulty'], 239025076303)
        self.assertEqual(block_header['difficulty_top64'], 0)
        self.assertEqual(block_header['wide_difficulty'], "0x37a701384f")
        self.assertEqual(block_header['hash'], "90f6fd3fe29c7518f15afd2da31734e890cc24247b5da10dc9ac2ea215ae844b")
        self.assertEqual(block_header['height'], 2288453)
        self.assertEqual(block_header['long_term_weight'], 17130)
        self.assertEqual(block_header['major_version'], 14)
        self.assertEqual(block_header['minor_version'], 14)
        self.assertEqual(block_header['miner_tx_hash'], "5e8d9531ae078ef5630e3c9950eb768b87b31481652c2b8dafca25d57e9c0c3f")
        self.assertEqual(block_header['nonce'], 1040830456)
        self.assertEqual(block_header['num_txes'], 11)
        self.assertEqual(block_header['orphan_status'], False)
        self.assertEqual(block_header['pow_hash'], "")
        self.assertEqual(block_header['prev_hash'], "a78d9e631f743806b0b8d3a70bb85758db466633eb3b4620737dd29b0548eb21")
        self.assertEqual(block_header['reward'], 1176972120146)
        self.assertEqual(block_header['timestamp'], 1612323209)

        with self.assertRaises(ValueError):
            self.backend.get_block_header_by_hash('HeyWaitAMinuteThisIsntAHashYouLiedToMeHowCouldYouDoThisToMeITrustedYou')

    @responses.activate
    def test_get_block_header_by_height(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_get_block_header_by_height_2288495.json'),
            status=200)

        resp = self.backend.get_block_header_by_height(2288495)

        self.assertIn('block_header', resp)
        self.assertIn('status', resp)
        self.assertIn('untrusted', resp)

        block_header = resp['block_header']

        self.assertEqual(block_header['block_size'], 8415)
        self.assertEqual(block_header['block_weight'], 8415)
        self.assertEqual(block_header['cumulative_difficulty'], 86651164421641270)
        self.assertEqual(block_header['cumulative_difficulty_top64'], 0)
        self.assertEqual(block_header['wide_cumulative_difficulty'], "0x133d8c662b9d436")
        self.assertEqual(block_header['depth'], 3)
        self.assertEqual(block_header['difficulty'], 238154836806)
        self.assertEqual(block_header['difficulty_top64'], 0)
        self.assertEqual(block_header['wide_difficulty'], "0x3773226b46")
        self.assertEqual(block_header['hash'], "966c1a70358ce998e7d5fb243b155971f9bffe06030c92dbd70486d398c40c05")
        self.assertEqual(block_header['height'], 2288495)
        self.assertEqual(block_header['long_term_weight'], 8415)
        self.assertEqual(block_header['major_version'], 14)
        self.assertEqual(block_header['minor_version'], 14)
        self.assertEqual(block_header['miner_tx_hash'], "408dd52531cab37e51db5a9a581bf25691b5534d8d0037b38e68061691b976e1")
        self.assertEqual(block_header['nonce'], 1275098057)
        self.assertEqual(block_header['num_txes'], 5)
        self.assertEqual(block_header['orphan_status'], False)
        self.assertEqual(block_header['pow_hash'], "")
        self.assertEqual(block_header['prev_hash'], "47751e6eb31230e92a5ee98242aa34d79bfd48657f2727c9a9b3cbad6aee88bb")
        self.assertEqual(block_header['reward'], 1176760892780)
        self.assertEqual(block_header['timestamp'], 1612328193)

        with self.assertRaises(ValueError):
            self.backend.get_block_header_by_height(-69420)

    @responses.activate
    def test_get_block_headers_range(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_get_block_headers_range_2288491_2288500.json'),
            status=200)

        resp = self.backend.get_block_header_by_height(2288495)

        self.assertIn('headers', resp)
        self.assertIn('status', resp)
        self.assertIn('untrusted', resp)

        headers = resp['headers']

        self.assertEqual(len(headers), 10)

        block_header_0 = headers[0]

        self.assertEqual(block_header_0['block_size'], 49559)
        self.assertEqual(block_header_0['block_weight'], 49559)
        self.assertEqual(block_header_0['cumulative_difficulty'], 86650214633914049)
        self.assertEqual(block_header_0['cumulative_difficulty_top64'], 0)
        self.assertEqual(block_header_0['wide_cumulative_difficulty'], "0x133d7e93ef73ec1")
        self.assertEqual(block_header_0['depth'], 19)
        self.assertEqual(block_header_0['difficulty'], 236253710852)
        self.assertEqual(block_header_0['difficulty_top64'], 0)
        self.assertEqual(block_header_0['wide_difficulty'], "0x3701d18a04")
        self.assertEqual(block_header_0['hash'], "01a5a129515e752055af9883ac98cdbd9eb90db16ab69ea187a1eb24eb7d0c66")
        self.assertEqual(block_header_0['height'], 2288491)
        self.assertEqual(block_header_0['long_term_weight'], 49559)
        self.assertEqual(block_header_0['major_version'], 14)
        self.assertEqual(block_header_0['minor_version'], 14)
        self.assertEqual(block_header_0['miner_tx_hash'], "22c3dd706931fe0606e086147dcb8a984b504a5bd0eabd1cf7dabb9456154cd4")
        self.assertEqual(block_header_0['nonce'], 922780730)
        self.assertEqual(block_header_0['num_txes'], 26)
        self.assertEqual(block_header_0['orphan_status'], False)
        self.assertEqual(block_header_0['pow_hash'], "")
        self.assertEqual(block_header_0['prev_hash'], "6bd071b487be697128142b9b132be8d2c3e4ee9660f73d811c3d23e4526e56ac")
        self.assertEqual(block_header_0['reward'], 1178084560299)
        self.assertEqual(block_header_0['timestamp'], 1612327847)

        with self.assertRaises(ValueError):
            self.backend.get_block_headers_range(-1, 10)

        with self.assertRaises(ValueError):
            self.backend.get_block_headers_range(70, 25)

    @responses.activate
    def test_get_block_with_height(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_get_block_2288515.json'),
            status=200)

        resp = self.backend.get_block(height=2288515)

        resp_fields = ['blob', 'block_header', 'credits', 'json', 'miner_tx_hash', 'status', 'tx_hashes', 'untrusted']
        for field in resp_fields:
            self.assertIn(field, resp)

        self.assertTrue(resp['blob'].startswith('0e0efef0e880066d78ace422007a2cefb423553b3'))
        self.assertEqual(len(resp['tx_hashes']), 17)
        self.assertEqual(resp['status'], 'OK')
        self.assertTrue(type(resp['block_header']), dict)

        json.loads(resp['json'])

        with self.assertRaises(ValueError):
            self.backend.get_block()

        with self.assertRaises(ValueError):
            self.backend.get_block(height=2288515, hash='1c68300646dda11a89cc9ca4001100745fcbd192e0e6efb6b06bd4d25851662b')

        with self.assertRaises(ValueError):
            self.backend.get_block(height=-5)

    @responses.activate
    def test_get_block_with_hash(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_get_block_2288515.json'),
            status=200)

        resp = self.backend.get_block(hash='1c68300646dda11a89cc9ca4001100745fcbd192e0e6efb6b06bd4d25851662b')

        resp_fields = ['blob', 'block_header', 'credits', 'json', 'miner_tx_hash', 'status', 'tx_hashes', 'untrusted']

        for field in resp_fields:
            self.assertIn(field, resp)

        self.assertTrue(resp['blob'].startswith('0e0efef0e880066d78ace422007a2cefb423553b3'))
        self.assertEqual(len(resp['tx_hashes']), 17)
        self.assertEqual(resp['status'], 'OK')
        self.assertTrue(type(resp['block_header']), dict)

        json.loads(resp['json'])

        with self.assertRaises(ValueError):
            self.backend.get_block(hash='STUPIDHECKINGBADHASH')

    @responses.activate
    def test_get_connections(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_get_connections.json'),
            status=200)

        resp = self.backend.get_connections()

        self.assertIn('connections', resp)

        connections = resp['connections']

        self.assertNotEqual(len(connections), 0)

        connection0 = connections[0]

        for conn_field in ['address', 'address_type', 'avg_download', 'avg_upload', 'connection_id', 'current_download', 'current_upload',
        'height', 'host', 'incoming', 'ip', 'live_time', 'local_ip', 'localhost', 'peer_id', 'port', 'pruning_seed', 'recv_count', 'recv_idle_time',
        'rpc_credits_per_hash', 'rpc_port', 'send_count', 'send_idle_time', 'state', 'support_flags']:
            self.assertIn(conn_field, connection0)

    @responses.activate
    def test_get_info(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_get_info.json'),
            status=200)

        resp = self.backend.get_info()

        for info_field in ['adjusted_time', 'alt_blocks_count', 'block_size_limit', 'block_size_median', 'block_weight_limit', 'block_weight_median',
        'bootstrap_daemon_address', 'busy_syncing', 'credits', 'cumulative_difficulty', 'cumulative_difficulty_top64', 'database_size', 'difficulty',
        'difficulty_top64', 'free_space', 'grey_peerlist_size', 'height', 'height_without_bootstrap', 'incoming_connections_count', 'mainnet', 'nettype',
        'offline', 'outgoing_connections_count', 'rpc_connections_count', 'stagenet', 'start_time', 'status', 'synchronized', 'target', 'target_height',
        'testnet', 'top_block_hash', 'top_hash', 'tx_count', 'tx_pool_size', 'untrusted', 'update_available', 'version', 'was_bootstrap_ever_used',
        'white_peerlist_size', 'wide_cumulative_difficulty', 'wide_difficulty']:
            self.assertIn(info_field, resp)

    @responses.activate
    def test_hard_fork_info(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_hard_fork_info.json'),
            status=200)

        resp = self.backend.hard_fork_info()

        for fork_field in ["earliest_height", "enabled", "state", "status", "threshold", "version", "votes", "voting", "window"]:
            self.assertIn(fork_field, resp)

    @responses.activate
    def test_set_bans_single(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_set_bans.json'),
            status=200)

        resp = self.backend.set_bans('188.165.17.204', True, 3600)

        self.assertEqual(resp['status'], 'OK')

    @responses.activate
    def test_set_bans_multiple(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_set_bans.json'),
            status=200)


        ips = ['188.165.17.204', 1466097787, '87.98.224.124']
        bans = [True, True, False]
        seconds = [3600, 500, 7200]

        self.backend.set_bans(ips, bans, seconds)

    def test_set_bans_errors(self):
        bad_ips =     [-1,    99999999999, 69420, '300.1.1.1', '125.124.123', '8.8.8.8']
        bad_bans =    [False, False,       True,  False,        True,         True]
        bad_seconds = [0,     None,        None,  60,           4000,         None]

        for i in range(len(bad_ips)):
            with self.assertRaises(ValueError):
                self.backend.set_bans(bad_ips[i], bad_bans[i], bad_seconds[i])

    @responses.activate
    def test_get_bans(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_get_bans.json'),
            status=200)

        resp = self.backend.get_bans()

        self.assertIn('bans', resp) # Should always be true bc I insert bans field when not given
        bans = resp['bans']
        ban0 = bans[0]

        self.assertEqual(ban0['host'], '145.239.118.5')
        self.assertEqual(ban0['ip'], 91680657)
        self.assertEqual(ban0['seconds'], 72260)

    @responses.activate
    def test_flush_txpool_all(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_flush_txpool.json'),
            status=200)


        self.backend.flush_txpool()

    @responses.activate
    def test_flush_txpool_single(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_flush_txpool.json'),
            status=200)


        self.backend.flush_txpool('65971f85ee13782f1f664cc8034a10b361b8b71ef821b323405ee0f698adb702')

    @responses.activate
    def test_flush_txpool_multiple(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_flush_txpool.json'),
            status=200)

        txs_to_flush = ['51bd0eebbb32392d4b4646e8b398432b9f42dee0e41f4939305e13e9f9a28e08',
        'ae9f8cbfdbae825e61c2745dc77c533fb9811e42ab9b3810d9529794c5bc9404']

        self.backend.flush_txpool(txs_to_flush)

    @responses.activate
    def test_get_output_histogram(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_get_output_histogram_1and5.json'),
            status=200)

        resp = self.backend.get_output_histogram([1e12, 5e12], 10, 100000000, True, 10)

        histogram = resp['histogram']

        self.assertEqual(histogram[0]['amount'], 1e12)
        self.assertEqual(histogram[0]['recent_instances'], 874619)
        self.assertEqual(histogram[0]['total_instances'], 874619)
        self.assertEqual(histogram[0]['unlocked_instances'], 874619)

    @responses.activate
    def test_get_coinbase_tx_sum(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_get_coinbase_tx_sum_2200000.json'),
            status=200)

        resp = self.backend.get_coinbase_tx_sum(2200000, 100)

        self.assertEqual(resp['emission_amount'], 139291580971286)
        self.assertEqual(resp['emission_amount_top64'], 0)
        self.assertEqual(resp['wide_emission_amount'], '0x7eaf59343916')
        self.assertEqual(resp['fee_amount'], 505668215000)
        self.assertEqual(resp['fee_amount_top64'], 0)
        self.assertEqual(resp['wide_fee_amount'], '0x75bc2ca0d8')

    @responses.activate
    def test_get_version(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_get_version.json'),
            status=200)

        resp = self.backend.get_version()

        self.assertEqual(resp['release'], True)
        self.assertEqual(resp['status'], 'OK')
        self.assertEqual(resp['untrusted'], False)
        self.assertEqual(resp['version'], 196613)

    @responses.activate
    def test_get_fee_estimate(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_get_fee_estimate.json'),
            status=200)

        resp = self.backend.get_fee_estimate()

        self.assertEqual(resp['fee'], 7790)
        self.assertEqual(resp['quantization_mask'], 10000)
        self.assertEqual(resp['status'], 'OK')
        self.assertEqual(resp['untrusted'], False)

    @responses.activate
    def test_get_fee_estimate_with_grace(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_get_fee_estimate.json'),
            status=200)

        resp = self.backend.get_fee_estimate(grace_blocks=10)

        self.assertEqual(resp['fee'], 7790)
        self.assertEqual(resp['quantization_mask'], 10000)
        self.assertEqual(resp['status'], 'OK')
        self.assertEqual(resp['untrusted'], False)

    def test_get_fee_estimate_errors(self):
        with self.assertRaises(TypeError):
            self.backend.get_fee_estimate(5.5)

        with self.assertRaises(ValueError):
            self.backend.get_fee_estimate(-100)

    @responses.activate
    def test_get_alternate_chains(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_get_alternate_chains.json'),
            status=200)

        resp = self.backend.get_alternate_chains()

        chains = resp['chains']
        chain0 = chains[0]

        self.assertEqual(chain0['block_hash'], '697cf03c89a9b118f7bdf11b1b3a6a028d7b3617d2d0ed91322c5709acf75625')
        self.assertEqual(chain0['difficulty'], 14114729638300280)
        self.assertEqual(chain0['height'], 1562062)
        self.assertEqual(chain0['length'], 2)

    @responses.activate
    def test_relay_tx_single(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_relay_tx.json'),
            status=200)

        resp = self.backend.relay_tx('9fd75c429cbe52da9a52f2ffc5fbd107fe7fd2099c0d8de274dc8a67e0c98613')

        self.assertEqual(resp['status'], 'OK')

    @responses.activate
    def test_relay_tx_multiple(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_relay_tx.json'),
            status=200)

        txs = ['70ee3df366870d8ca2099b273c1ae1c909a964b053077ead5c186c8b160c9d00',
        '018476f726efb2d2b5a4a3ba6c29fb4f00549b0dcef6183b2bfa38a7acb1a804']
        resp = self.backend.relay_tx(txs)

        self.assertEqual(resp['status'], 'OK')

    @responses.activate
    def test_sync_info(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_sync_info.json'),
            status=200)

        resp = self.backend.sync_info()

        height = resp['height']
        peers = resp['peers']
        spans = resp['spans']

        pinfo0 = peers[0]['info']

        self.assertEqual(height, 2292442)
        self.assertEqual(pinfo0['address'], '54.39.75.54:59545')
        self.assertEqual(pinfo0['connection_id'], '9bded655ad3d44eaa8b51917bdb8edbb')
        self.assertEqual(pinfo0['host'], '54.39.75.54')
        self.assertEqual(pinfo0['port'], '59545')
        self.assertEqual(pinfo0['recv_count'], 277)
        self.assertEqual(pinfo0['incoming'], True)

        span0 = spans[0]

        self.assertEqual(span0, {
        "connection_id": "e8076d15669c431d90b290a712760359",
        "nblocks": 13,
        "rate": 982529,
        "remote_address": "178.63.100.197:18080",
        "size": 998309,
        "speed": 100,
        "start_block_height": 2292442
        })

    @responses.activate
    def test_get_txpool_backlog(self):
        pass

    @responses.activate
    def test_get_output_distribution(self):
        pass