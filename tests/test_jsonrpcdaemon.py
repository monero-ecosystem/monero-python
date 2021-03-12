import decimal
import json
import logging
import os
import responses
import six

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
    getheight_url = 'http://127.0.0.1:18081/get_height'
    getaltblockshashes_url = 'http://127.0.0.1:18081/get_alt_blocks_hashes'
    iskeyimagespent_url = 'http://127.0.0.1:18081/is_key_image_spent'
    startmining_url = 'http://127.0.0.1:18081/start_mining'
    stopmining_url = 'http://127.0.0.1:18081/stop_mining'
    miningstatus_url = 'http://127.0.0.1:18081/mining_status'
    savebc_url = 'http://127.0.0.1:18081/save_bc'
    getpeerlist_url = 'http://127.0.0.1:18081/get_peer_list'
    setloghashrate_url = 'http://127.0.0.1:18081/set_log_hash_rate'
    setloglevel_url = 'http://127.0.0.1:18081/set_log_level'
    setlogcategories_url = 'http://127.0.0.1:18081/set_log_categories'
    gettransactionpoolstats_url = 'http://127.0.0.1:18081/get_transaction_pool_stats'
    stopdaemon_url = 'http://127.0.0.1:18081/stop_daemon'
    getlimit_url = 'http://127.0.0.1:18081/get_limit'
    setlimit_url = 'http://127.0.0.1:18081/set_limit'
    outpeers_url = 'http://127.0.0.1:18081/out_peers'
    inpeers_url = 'http://127.0.0.1:18081/in_peers'
    getouts_url = 'http://127.0.0.1:18081/get_outs'
    update_url = 'http://127.0.0.1:18081/update'
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

        resp = self.backend.set_bans(six.ensure_text('188.165.17.204'), True, 3600)

        self.assertEqual(resp['status'], 'OK')

    @responses.activate
    def test_set_bans_multiple(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_set_bans.json'),
            status=200)


        ips = [six.ensure_text('188.165.17.204'), 1466097787, six.ensure_text('87.98.224.124')]
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

    @responses.activate
    def test_get_height(self):
        responses.add(responses.POST, self.getheight_url,
            json=self._read('test_get_height_2294632.json'),
            status=200)

        resp = self.backend.get_height()

        self.assertEqual(resp['height'], 2294632)
        self.assertEqual(resp['hash'], '228c0538b7ba7d28fdd58ed310326db61ea052038bdb42652f6e1852cf666325')

    @responses.activate
    def test_get_transactions(self):
        responses.add(responses.POST, self.transactions_url,
            json=self._read('test_get_transactions.json'),
            status=200)

        resp = self.backend.get_transactions(['c6802ca1805784c7330e71521a318c302f88625b0eab80740cfab24af7b0cb93',
            'ae476cae3ad2b44c6c2614b9435adbe304e24c59d410fe3b4dd046a9021d66b9'], decode_as_json=True, prune=False)

        self.assertEqual(resp['txs_as_hex'][0], 
            '02000102000bbdef820aa8e5f901a3cc79a337b5d601aadb01af55fb44d90b8f0c850bda856b62f04c77bf46f46954b8caa82097b9386b0a501277262'
            'c68601ed917ac020002d4871f51832c1951212b3d87395a8df5594e927588221e665a018c098968cc8b000262d52033f1a3c921f1db56eca9b5dd50f3'
            '6ecf76e22e67cc694fb7c214a609ef2c0164d167ad3d6f762414567f5812585fe7f48d3400cd51d999b020899658526567020901795c32b0b5ba9ce30'
            '580cfe81a73e3d349bd53dfa8fa66a93993f6921ff0457386671f45ef33760947513b71ec6398ff0e2ebb5edde433e452b9035112714a290806bedd15'
            'cd5293ea33be5bec57e983042840d75f66b7ca31c599f4ca0179a0ea918ad50e7e2d10784dffb56eeb39d4c92236c4904c1ecebd5b90ad6b797f9bace'
            '3566394d8a2558232b8f8262317dcc3da8038bc46119eb891371d71f940e15801c6ddf29ddf034c0e277ce87d4343cb821fece9c74b1e04ecec914c34'
            'c5b7bb518042b1ca36de80e451aca0c44d93298d4a4ec31a2a1aa8b5b437a6aab043ed66a681ba1f5f7773fa140176ddcdb2a0e7c9ae3163094671bf3'
            '48d5504bc2b168891c1a599ce00acfe3a430c9c58370fe53b96a4d64155b03b5f30ee0307f95bde576a409f86100e2bcfe81d19d2407134310dce6ff9'
            '53f668e810d48f12f3fd61b6c0f00819a18b75ae762b03dd97ba40ffc5a791318bf019f989e85f09385b4b9b74c8500321fb918e13f3bbd0a2fdf5749'
            '318f152e2a0f994f11b848e0157e0b3c44afab6653ef0815ad1e0d76ba1141d5abb61f8b078a57413d3374b3aa78fbea4de0604d470a12a21da6fea3c'
            '765e9ddec5d50b8f76f079f9c61c17b25822612418444181adf9e334a695aaabec779edf8842dbdbae99461c608dc0096113d8da040c3b5bd94dc796a'
            'a1daaa740839fd0f4363fa60b8c3e84fddc43075ae595d323dc7cff3db06df16d2eb08bdceca623de357e6cfd59deedcba29a203bbbbaadcc18bdd1ce'
            '03ba2d1bd16bc5e666b8006b473f339841199c5c183c5b78b420bd896cd50b2aa7b9f9fcba3615abe0f734c830320a8e9830976bbcae9a8e77676c4a3'
            'd944a3dca84fed10d242b12da93e9e37be272a933b45b23b8f4c20c8dc6bc3f0d56878639b7900f505e6060806939e9f7f417fd10965fc564c7f00893'
            'b920b6c32ff2e546dd40ec4414a110b052e97d3d74255190c0032f0826f87f155779e21e9b5b6a9300d6a2bde804ec0e107cde3f600ab5572cdda0964'
            '5147cbbfcbf4c3681cb6965770ebb2b298151c354e45aab0e1ab77d414a30362a0091230d667e4ac44f5448cdf319b170c92f20d8c44b620f3b451732'
            '8bf4ece003dba9db9a71d0531ddd329adbcc4f6c408caeaebabe477bc1084f1da40cc4ca03e7ecc5f173167accf433667b9d3b61fdfd8cfe3498951e8'
            '912d6ef9a79401e0913b53dc6a14a8e117d053f82020e808b45e15b85d7102d1ccc87739c22124b058b2ab71e67f71598bf2b43813fb408df5ecafb1c'
            'a6c9761256958b017d7ab00d4a0a3fdb9ed61908d6559b853d254d86bd50fd85b349a8a9c5386850e4b9ad0984eed4614a896488fcb1b63cf795a56c1'
            '2425dfbfe19ee09ac4375e6eb220e0ff2254d80d1f9fb865d5b176003779f5064ae0949aee694ac89df0fee4d1f3104d8bf76b06773b27c6ca86e69fb'
            '94146ca082a76af02d3e76c6e635fc3bb524084f89e8428a61207a4660e9c666e3e74762a62330d56753ad8fa7cf1267f5490c3ff7596b99bdda95e1b'
            'd409107ec45e09a0650f0a8c32dfddfbca2000602c705427b0fb904ef582e435fef3de34b6a3a07a67031fea098a28695cce2908f230e80cadb40036b'
            '6da75aef391ce13231674edb807af5e04f686027cae475274007b85ff58b13527f6b1125438e734ac8a1206255a332824004a1a2de925584140398089'
            'f34018fce44f334f3b283e58900ffa58f7c2a63641f7d4d946fb44e2b18f4ce36baf1b06c026e4055dadb7b06a239a003ba571528a0f16f0f1dd4cbd730')

        self.assertEqual(resp['txs'][0]['block_height'], 2295433)
        self.assertEqual(resp['txs'][0]['block_timestamp'], 1613160690)
        self.assertEqual(resp['txs'][1]['in_pool'], True)

        json.loads(resp['txs'][0]['as_json'])

    @responses.activate
    def test_get_alt_blocks_hashes(self):
        responses.add(responses.POST, self.getaltblockshashes_url,
            json=self._read('test_get_alt_blocks_hashes_doc_example.json'),
            status=200)

        resp = self.backend.get_alt_blocks_hashes()

        hashes = ["9c2277c5470234be8b32382cdf8094a103aba4fcd5e875a6fc159dc2ec00e011","637c0e0f0558e284493f38a5fcca3615db59458d90d3a5eff0a18ff59b83f46f",
        "6f3adc174a2e8082819ebb965c96a095e3e8b63929ad9be2d705ad9c086a6b1c","697cf03c89a9b118f7bdf11b1b3a6a028d7b3617d2d0ed91322c5709acf75625",
        "d99b3cf3ac6f17157ac7526782a3c3b9537f89d07e069f9ce7821d74bd9cad0e","e97b62109a6303233dcd697fa8545c9fcbc0bf8ed2268fede57ddfc36d8c939c",
        "70ff822066a53ad64b04885c89bbe5ce3e537cdc1f7fa0dc55317986f01d1788","b0d36b209bd0d4442b55ea2f66b5c633f522401f921f5a85ea6f113fd2988866"]

        self.assertEqual(resp['blks_hashes'], hashes)

    @responses.activate
    def test_is_key_image_spent(self):
        responses.add(responses.POST, self.iskeyimagespent_url,
            json=self._read('test_is_key_image_spent.json'),
            status=200)

        key_imgs = ['8d1bd8181bf7d857bdb281e0153d84cd55a3fcaa57c3e570f4a49f935850b5e3', '7319134bfc50668251f5b899c66b005805ee255c136f0e1cecbb0f3a912e09d4',
        '8d1bd8181bf7d857bdb281e0153d84cd55a3fcaa57c3e570f4a49f935850b5e2', 'fbbd6ac46dc4905c455f3b51595da6b135a5e9a64c6c181875558649be0ab183']
        resp = self.backend.is_key_image_spent(key_imgs)

        self.assertEqual(resp['spent_status'], [1, 1, 0, 2])

    @responses.activate
    def test_send_raw_transaction(self):
        pass

    @responses.activate
    def test_start_mining(self):
        responses.add(responses.POST, self.startmining_url,
            json=self._read('test_mining.json'),
            status=200)

        mining_addr = '497e4umLC7pfJ5TSSuU1QY8E1Nh5h5cWfYnvvpTrYFKiQriWfVYeVn2KH8Hpp3AeDRbCSxTvZuUZ1WYd8PGLqM4r5P5hjNQ'
        resp = self.backend.start_mining(False, True, mining_addr, 4)

        self.assertEqual(resp['status'], 'OK')

        with self.assertRaises(ValueError):
            self.backend.start_mining(False, True, mining_addr, -1)

        with self.assertRaises(ValueError):
            self.backend.start_mining(False, True, "meepmoopthisisntarealminingaddress", 2)

    @responses.activate
    def test_stop_mining(self):
        responses.add(responses.POST, self.stopmining_url,
            json=self._read('test_mining.json'),
            status=200)

        resp = self.backend.stop_mining()

        self.assertEqual(resp['status'], 'OK')

    @responses.activate
    def test_mining_status_off(self):
        responses.add(responses.POST, self.miningstatus_url,
            json=self._read('test_mining_status_off.json'),
            status=200)

        resp = self.backend.mining_status()

        self.assertEqual(resp['active'], False)
        self.assertEqual(resp['difficulty'], 250236969769)
        self.assertEqual(resp['pow_algorithm'], 'RandomX')

    @responses.activate
    def test_mining_status_on(self):
        responses.add(responses.POST, self.miningstatus_url,
            json=self._read('test_mining_status_on.json'),
            status=200)

        resp = self.backend.mining_status()

        self.assertEqual(resp['active'], True)
        self.assertEqual(resp['difficulty'], 252551179535)
        self.assertEqual(resp['pow_algorithm'], 'RandomX')
        self.assertEqual(resp['address'], "497e4umLC7pfJ5TSSuU1QY8E1Nh5h5cWfYnvvpTrYFKiQriWfVYeVn2KH8Hpp3AeDRbCSxTvZuUZ1WYd8PGLqM4r5P5hjNQ")

    @responses.activate
    def test_save_bc(self):
        responses.add(responses.POST, self.savebc_url,
            json=self._read('test_save_bc.json'),
            status=200)

        resp = self.backend.save_bc()

        self.assertEqual(resp['status'], 'OK')

    @responses.activate
    def test_get_peer_list(self):
        responses.add(responses.POST, self.getpeerlist_url,
            json=self._read('test_get_peer_list.json'),
            status=200)

        resp = self.backend.get_peer_list()
        
        white0 = resp['white_list'][0]
        gray0 = resp['gray_list'][0]

        self.assertEqual(white0['host'], '204.8.15.5')
        self.assertEqual(white0['ip'], 84871372)
        self.assertEqual(white0['port'], 18080)
        self.assertEqual(white0['id'], 702714784157243868)

        self.assertEqual(gray0['host'], '92.233.45.0')
        self.assertEqual(gray0['ip'], 3008860)
        self.assertEqual(gray0['port'], 5156)
        self.assertEqual(gray0['id'], 779474923786790553)

    @responses.activate
    def test_set_log_hashrate_mining(self):
        responses.add(responses.POST, self.setloghashrate_url,
            json=self._read('test_set_log_hash_rate_mining.json'),
            status=200)

        resp = self.backend.set_log_hash_rate(True)

        self.assertEqual(resp['status'], 'OK')

    @responses.activate
    def test_set_log_hashrate_notmining(self):
        responses.add(responses.POST, self.setloghashrate_url,
            json=self._read('test_set_log_hash_rate_notmining.json'),
            status=200)

        with self.assertRaises(RPCError):
            resp = self.backend.set_log_hash_rate(False)

    @responses.activate
    def test_set_log_level(self):
        responses.add(responses.POST, self.setloglevel_url,
            json=self._read('test_set_log_level.json'),
            status=200)

        resp = self.backend.set_log_level(1)

        with self.assertRaises(ValueError):
            resp = self.backend.set_log_level(5)

        self.assertEqual(JSONRPCDaemon.known_log_levels(), JSONRPCDaemon._KNOWN_LOG_LEVELS)

    @responses.activate
    def test_set_log_categories_default(self):
        responses.add(responses.POST, self.setlogcategories_url,
            json=self._read('test_set_log_categories_default.json'),
            status=200)

        resp = self.backend.set_log_categories('default:INFO')

        self.assertEqual(resp['status'], 'OK')
        self.assertEqual(resp['categories'], 'default:INFO')

        self.assertEqual(JSONRPCDaemon.known_log_categories(), JSONRPCDaemon._KNOWN_LOG_CATEGORIES)

    @responses.activate
    def test_set_log_categories_multiple(self):
        responses.add(responses.POST, self.setlogcategories_url,
            json=self._read('test_set_log_categories_multiple.json'),
            status=200)

        resp = self.backend.set_log_categories(['logging:INFO', 'net:FATAL']) 

        self.assertEqual(resp['categories'], 'logging:INFO,net:FATAL')
        self.assertEqual(resp['status'], 'OK')

    @responses.activate
    def test_set_log_categories_empty(self):
        responses.add(responses.POST, self.setlogcategories_url,
            json=self._read('test_set_log_categories_empty.json'),
            status=200)

        resp = self.backend.set_log_categories() 

        self.assertEqual(resp['categories'], '')
        self.assertEqual(resp['status'], 'OK')

    @responses.activate
    def test_get_transaction_pool(self):
        responses.add(responses.POST, self.mempool_url,
            json=self._read('test_get_transaction_pool.json'),
            status=200)

        resp = self.backend.get_transaction_pool()

        self.assertEqual(resp['spent_key_images'][0]['id_hash'], '1ccff101d8ee93903bde0a8ef99ebc99ccd5150f7157b93b758cd456458d4166')
        self.assertEqual(resp['spent_key_images'][0]['txs_hashes'][0], '73fe0207e25d59dce5cd6f7369edf33a04ac56409eca3b28ad837c43640ef83f')
        self.assertEqual(resp['transactions'][0]['id_hash'], 'ea020cf2595c017d5fd4d0d427b8ff02b1857e996136b041c0f7fd6dffc4c72c')

    @responses.activate
    def test_get_transaction_pool_stats(self):
        responses.add(responses.POST, self.gettransactionpoolstats_url,
            json=self._read('test_get_transaction_pool_stats.json'),
            status=200)

        resp = self.backend.get_transaction_pool_stats()

        self.assertEqual(resp['pool_stats']['bytes_total'], 75438)
        self.assertEqual(resp['pool_stats']['txs_total'], 17)
        self.assertEqual(resp['pool_stats']['histo'][0]['bytes'], 3419)
        self.assertEqual(resp['pool_stats']['histo'][0]['txs'], 2)

    @responses.activate
    def test_stop_daemon(self):
        responses.add(responses.POST, self.stopdaemon_url,
            json=self._read('test_stop_daemon.json'),
            status=200)

        resp = self.backend.stop_daemon()

        self.assertEqual(resp['status'], 'OK')

    @responses.activate
    def test_get_limit(self):
        responses.add(responses.POST, self.getlimit_url,
            json=self._read('test_get_limit.json'),
            status=200)

        resp = self.backend.get_limit()

        self.assertEqual(resp['limit_down'], 8192)
        self.assertEqual(resp['limit_up'], 2048)
        self.assertEqual(resp['status'], 'OK')

    @responses.activate
    def test_out_peers(self):
        responses.add(responses.POST, self.outpeers_url,
            json=self._read('test_out_peers.json'),
            status=200)

        resp = self.backend.out_peers(16)

        self.assertEqual(resp['out_peers'], 16)

        with self.assertRaises(ValueError):
            resp = self.backend.out_peers(2**32)

    @responses.activate
    def test_out_peers_unlimited(self):
        responses.add(responses.POST, self.outpeers_url,
            json=self._read('test_out_peers_unlimited.json'),
            status=200)

        resp = self.backend.out_peers(-1)

        self.assertEqual(resp['out_peers'], 2**32 - 1)

    @responses.activate
    def test_in_peers(self):
        responses.add(responses.POST, self.inpeers_url,
            json=self._read('test_in_peers.json'),
            status=200)

        resp = self.backend.in_peers(128)

        self.assertEqual(resp['in_peers'], 128)

        with self.assertRaises(ValueError):
            resp = self.backend.in_peers(2**32)

    @responses.activate
    def test_in_peers_unlimited(self):
        responses.add(responses.POST, self.inpeers_url,
            json=self._read('test_in_peers_unlimited.json'),
            status=200)

        resp = self.backend.in_peers(-1)

        self.assertEqual(resp['in_peers'], 2**32 - 1)

    @responses.activate
    def test_get_outs(self):
        responses.add(responses.POST, self.getouts_url,
            json=self._read('test_get_outs_multiple.json'),
            status=200)

        a = [0, decimal.Decimal('0'), decimal.Decimal('20'), int(3e12)]
        i = [20000, 20001, 50630, 232237]
        resp = self.backend.get_outs(a, i)

        self.assertEqual(resp['outs'][0]['height'], 1224094)
        self.assertEqual(resp['outs'][0]['key'], 'fc13952b8b9c193d4c875e750e88a0da8a7d348f95c019cfde93762d68298dd7')
        self.assertEqual(resp['outs'][0]['mask'], 'bf99dc047048605f6e0aeebc937477ae6e9e3143e1be1b48af225b41f809e44e')
        self.assertEqual(resp['outs'][0]['txid'], '687f9b1d6fa409a13e84c682e90127b1953e10efe679c114a01d7db77f474d50')
        self.assertEqual(resp['outs'][0]['unlocked'], True)

        self.assertEqual(resp['outs'][3]['height'], 999999)
        self.assertEqual(resp['outs'][3]['key'], 'e20315663e3d278421797c4098c828cad5220849d08c3d26fee72003d4cda698')
        self.assertEqual(resp['outs'][3]['mask'], '100c6f1342b71b73edddc5492be923182f00a683488ec3a2a1c7a949cbe57768')
        self.assertEqual(resp['outs'][3]['txid'], '2a5d456439f7ae27b5d26e493651c0e24e1d7e02b6d9d019c89d562ce0658472')
        self.assertEqual(resp['outs'][3]['unlocked'], True)

    @responses.activate
    def test_get_outs_single(self):
        responses.add(responses.POST, self.getouts_url,
            json=self._read('test_get_outs_single.json'),
            status=200)

        resp = self.backend.get_outs(0, 10000)

        self.assertEqual(resp['outs'][0]['height'], 1222460)
        self.assertEqual(resp['outs'][0]['key'], '9c7055cb5b790f1eebf10b7b8fbe01241eb736b5766d15554da7099bbcdc4b44')
        self.assertEqual(resp['outs'][0]['mask'], '42e37af85cddaeccbea6fe597037c9377045a682e66661260868877b9440af70')
        self.assertEqual(resp['outs'][0]['txid'], 'b357374ad4636f17520b6c2fdcf0fb5e6a1185fed2aef509b19b5100d04ae552')
        self.assertEqual(resp['outs'][0]['unlocked'], True)

    @responses.activate
    def test_update_check_none(self):
        responses.add(responses.POST, self.update_url,
            json=self._read('test_update_check_none.json'),
            status=200)

        resp = self.backend.update('check')

        self.assertEqual(resp['update'], False)
        self.assertEqual(resp['auto_uri'], '')
        self.assertEqual(resp['hash'], '')
        self.assertEqual(resp['path'], '')
        self.assertEqual(resp['user_uri'], '')
        self.assertEqual(resp['version'], '')
        self.assertEqual(resp['status'], 'OK')

        with self.assertRaises(ValueError):
            self.backend.update('badcommandrightherebuddyolpal')

    @responses.activate
    def test_restricted_false(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_sync_info.json'),
            status=200)

        self.assertFalse(self.backend.restricted())

    @responses.activate
    def test_restricted_true(self):
        responses.add(responses.POST, self.jsonrpc_url,
            json=self._read('test_method_not_found.json'),
            status=200)

        self.assertTrue(self.backend.restricted())
