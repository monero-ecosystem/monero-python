from binascii import hexlify
import responses

from monero.daemon import Daemon
from monero.backends.jsonrpc import JSONRPCDaemon
from monero.transaction import Transaction

from .base import JSONTestCase

class JSONRPCDaemonTestCase(JSONTestCase):
    jsonrpc_url = 'http://127.0.0.1:18081/json_rpc'
    mempool_url = 'http://127.0.0.1:18081/get_transaction_pool'
    data_subdir = 'test_jsonrpcdaemon'

    def setUp(self):
        self.daemon = Daemon(JSONRPCDaemon())

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
