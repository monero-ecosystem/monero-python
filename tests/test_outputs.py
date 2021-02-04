from decimal import Decimal
import json
try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock
import responses

from monero.backends.jsonrpc import JSONRPCDaemon, JSONRPCWallet
from monero.backends.offline import OfflineWallet
from monero.daemon import Daemon
from monero.transaction import Transaction
from monero.wallet import Wallet

from .base import JSONTestCase

class OutputTestCase(JSONTestCase):
    data_subdir = "test_outputs"
    daemon_transactions_url = "http://127.0.0.1:38081/get_transactions"
    wallet_jsonrpc_url = "http://127.0.0.1:38083/json_rpc"

    @responses.activate
    def test_multiple_outputs(self):
        daemon = Daemon(JSONRPCDaemon(host="127.0.0.1", port=38081))
        responses.add(responses.POST, self.wallet_jsonrpc_url,
            json=self._read("test_multiple_outputs-wallet-00-get_accounts.json"),
            status=200)
        responses.add(responses.POST, self.wallet_jsonrpc_url,
            json=self._read("test_multiple_outputs-wallet-01-query_key.json"),
            status=200)
        responses.add(responses.POST, self.wallet_jsonrpc_url,
            json=self._read("test_multiple_outputs-wallet-02-addresses-account-0.json"),
            status=200)
        responses.add(responses.POST, self.wallet_jsonrpc_url,
            json=self._read("test_multiple_outputs-wallet-02-addresses-account-1.json"),
            status=200)
        wallet = Wallet(JSONRPCWallet(host="127.0.0.1", port=38083))
        responses.add(responses.POST, self.daemon_transactions_url,
            json=self._read("test_multiple_outputs-daemon-00-get_transactions.json"),
            status=200)
        tx = daemon.transactions(
                "f79a10256859058b3961254a35a97a3d4d5d40e080c6275a3f9779acde73ca8d")[0]
        outs = tx.outputs(wallet=wallet)
        self.assertEqual(len(outs), 5)
        self.assertEqual(
                outs[0].stealth_address,
                "d3eb42322566c1d48685ee0d1ad7aed2ba6210291a785ec051d8b13ae797d202")
        self.assertEqual(
                outs[1].stealth_address,
                "5bda44d7953e27b84022399850b59ed87408facdf00bbd1a2d4fda4bf9ebf72f")
        self.assertEqual(
                outs[2].stealth_address,
                "4c79c14d5d78696e72959a28a734ec192059ebabb931040b5a0714c67b507e76")
        self.assertEqual(
                outs[3].stealth_address,
                "64de2b358cdf96d498a9688edafcc0e25c60179e813304747524c876655a8e55")
        self.assertEqual(
                outs[4].stealth_address,
                "966240954892294091a48c599c6db2b028e265c67677ed113d2263a7538f9a43")
        self.assertIsNotNone(outs[0].payment)
        self.assertIsNone(outs[1].payment)      # FIXME: isn't that change we should recognize?
        self.assertIsNotNone(outs[2].payment)
        self.assertIsNotNone(outs[3].payment)
        self.assertIsNotNone(outs[4].payment)
        self.assertEqual(outs[0].amount, outs[0].payment.amount)
        self.assertEqual(outs[2].amount, outs[2].payment.amount)
        self.assertEqual(outs[3].amount, outs[3].payment.amount)
        self.assertEqual(outs[4].amount, outs[4].payment.amount)
        self.assertEqual(outs[0].amount, Decimal(4))
        self.assertEqual(outs[2].amount, Decimal(1))
        self.assertEqual(outs[3].amount, Decimal(2))
        self.assertEqual(outs[4].amount, Decimal(8))
        self.assertEqual(
                outs[0].payment.local_address,
                "76Qt2xMZ3m7b2tagubEgkvG81pwf9P3JYdxR65H2BEv8c79A9pCBTacEFv87tfdcqXRemBsZLFVGHTWbqBpkoBJENBoJJS9")
        self.assertEqual(
                outs[2].payment.local_address,
                "78zGgzb45TEL8uvRFjCayUjHS98RFry1f7P4PE4LU7oeLh42s9AtP8fYXVzWqUW4r3Nz4g3V64w9RSiV7o3zUbPZVs5DVaU")
        self.assertEqual(
                outs[3].payment.local_address,
                "73ndji4W2bu4WED87rJDVALMvUsZLLYstZsigbcGfb5YG9SuNyCSYk7Qbttez2mXciKtWRzRN9aYGJbF9TPBidNQNZppnFw")
        self.assertEqual(
                outs[4].payment.local_address,
                "7BJxHKTa4p5USJ9Z5GY15ZARXL6Qe84qT3FnWkMbSJSoEj9ugGjnpQ1N9H1jqkjsTzLiN5VTbCP8f4MYYVPAcXhr36bHXzP")

    def test_coinbase_no_own_output(self):
        txdata = self._read("test_coinbase_no_own_output-26dcb5.json")
        tx = Transaction(
            hash="26dcb55c3c93a2176949fd9ec4e20a9d97ece7c420408d9353c390a909e9a7c1",
            height=766459,
            output_indices=txdata["output_indices"],
            json=json.loads(txdata["as_json"]))
        self.assertTrue(tx.is_coinbase)
        wallet = Wallet(OfflineWallet(
            address="56eDKfprZtQGfB4y6gVLZx5naKVHw6KEKLDoq2WWtLng9ANuBvsw67wfqyhQECoLmjQN4cKAdvMp2WsC5fnw9seKLcCSfjj",
            view_key="e507923516f52389eae889b6edc182ada82bb9354fb405abedbe0772a15aea0a"))
        outs = tx.outputs(wallet=wallet)
        self.assertEqual(len(outs), 1)
        self.assertIsNone(outs[0].payment)
        self.assertEqual(outs[0].amount, Decimal("8.415513145431"))
        self.assertEqual(outs[0].index, 3129279)

    def test_coinbase_own_output(self):
        txdata = self._read("test_coinbase_own_output-dc0861.json")
        tx = Transaction(
            hash="dc08610685b8a55dc7d64454ecbe12868e4e73c766e2d19ee092885a06fc092d",
            height=518147,
            json=txdata)
        self.assertTrue(tx.is_coinbase)
        wallet = Wallet(OfflineWallet(
            address="56eDKfprZtQGfB4y6gVLZx5naKVHw6KEKLDoq2WWtLng9ANuBvsw67wfqyhQECoLmjQN4cKAdvMp2WsC5fnw9seKLcCSfjj",
            view_key="e507923516f52389eae889b6edc182ada82bb9354fb405abedbe0772a15aea0a"))
        outs = tx.outputs(wallet=wallet)
        self.assertEqual(len(outs), 1)
        self.assertIsNotNone(outs[0].payment)
        self.assertEqual(
            outs[0].payment.local_address,
            "56eDKfprZtQGfB4y6gVLZx5naKVHw6KEKLDoq2WWtLng9ANuBvsw67wfqyhQECoLmjQN4cKAdvMp2WsC5fnw9seKLcCSfjj")
        self.assertEqual(outs[0].amount, outs[0].payment.amount)
        self.assertEqual(outs[0].payment.amount, Decimal("13.515927959357"))

    # TODO add test of v1 transaction
    # TODO add test of ExtraParser initialized with str and bytes
    # TODO add test of extra with TX_EXTRA_TAG_PADDING
    # TODO add test of extra with TX_EXTRA_TAG_EXTRA_NONCE
    # TODO add test of extra with unknown tag, e.g. 0x03
