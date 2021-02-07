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
from monero.transaction.extra import ExtraParser
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
        self.assertIsNone(outs[1].amount)
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
        self.assertEqual(
                repr(outs[0]),
                "d3eb42322566c1d48685ee0d1ad7aed2ba6210291a785ec051d8b13ae797d202, 4.000000000000 "
                "to [76Qt2x]")

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

    def test_v1_tx(self):
        tx1 = Transaction(
            hash="2634445086cc48b89f1cd241e89e6f37195008807264684d8fad4a16f479c45a",
            height=2022660,
            json=self._read("test_v1_tx-263444.json"))
        tx2 = Transaction(
            hash="3586a81f051bcb265a45c99f11b19fc4b55bb2abb3332c515a8b88a559cd9f7b",
            height=2022660,
            json=self._read("test_v1_tx-3586a8.json"))
        outs1 = tx1.outputs()
        self.assertEqual(len(outs1), 14)
        self.assertEqual(outs1[0].stealth_address, "b1ef76960fe245f73131be22e9b548e861f93b727ab8a2a3ff64d86521512382")
        self.assertEqual(outs1[0].amount, Decimal("0.000000000300"))
        self.assertEqual(outs1[1].stealth_address, "dcd66bbcb6e72602dd876e1dad65a3464a2bd831f09ec7c8131147315152e29b")
        self.assertEqual(outs1[1].amount, Decimal("0.000008000000"))
        self.assertEqual(outs1[2].stealth_address, "71efdb68dfd33f5c89a5fa8312ec6e346681f6f60fb406e9426231a5f230351a")
        self.assertEqual(outs1[2].amount, Decimal("0.007000000000"))
        self.assertEqual(outs1[3].stealth_address, "499fb727f61f2ce0fbc3419b309601f2cbf672eeef2cc827aef423b0b70e2529")
        self.assertEqual(outs1[3].amount, Decimal("0.000000010000"))
        self.assertEqual(outs1[4].stealth_address, "297ef9bb654dd6e26472a4f07f037eddb3f8b458cf4315e2cc40d9fd725e28b9")
        self.assertEqual(outs1[4].amount, Decimal("0.000000500000"))
        self.assertEqual(outs1[5].stealth_address, "b2bf18a500afe1775305b19d16d0d5afec0f72096b9f15cca6604d7f5ad6e5f8")
        self.assertEqual(outs1[5].amount, Decimal("0.300000000000"))
        self.assertEqual(outs1[6].stealth_address, "f7a95b33912077e3aca425270f76be13af503919b6230368a591e1053b3c7436")
        self.assertEqual(outs1[6].amount, Decimal("5.000000000000"))
        self.assertEqual(outs1[7].stealth_address, "1e93e243a865b71e14fe4df6de0902ca634749b48002c52adc7f046053c2b921")
        self.assertEqual(outs1[7].amount, Decimal("0.000200000000"))
        self.assertEqual(outs1[8].stealth_address, "513822bad9697e8494ff82cb4b58a5a693aa433c16f0aafdaaf4a27b026a32e4")
        self.assertEqual(outs1[8].amount, Decimal("0.000000000009"))
        self.assertEqual(outs1[9].stealth_address, "6e1ace4cfdf3f5363d72c241382e3b9927af1093b549a62f2902f56137d153bc")
        self.assertEqual(outs1[9].amount, Decimal("0.000000000070"))
        self.assertEqual(outs1[10].stealth_address, "1df18bd04f42c9da8f6b49afe418aabc8ab973448a941d365534b5d0862a3d46")
        self.assertEqual(outs1[10].amount, Decimal("0.000000002000"))
        self.assertEqual(outs1[11].stealth_address, "caf3e6c07f8172fc31a56ba7f541ba8d6cc601f2c7da1a135126f8f3455e3ffc")
        self.assertEqual(outs1[11].amount, Decimal("20.000000000000"))
        self.assertEqual(outs1[12].stealth_address, "1ce506bc1ee041dfe36df3e085156023be26e133fb14f5e529b60a2d769a7c7c")
        self.assertEqual(outs1[12].amount, Decimal("0.000030000000"))
        self.assertEqual(outs1[13].stealth_address, "ee1a22b1f49db4df0df56161801974326cda4ceacbbf2a17c795ebe945790281")
        self.assertEqual(outs1[13].amount, Decimal("0.030000000000"))
        outs2 = tx2.outputs()
        self.assertEqual(len(outs2), 10)
        self.assertEqual(outs2[0].stealth_address, "ddd1d47e5d419cf5e2298e4d9e828364b929976912dfc1bbed25fb20cc681f9f")
        self.assertEqual(outs2[0].amount, Decimal("3.000000000000"))
        self.assertEqual(outs2[1].stealth_address, "a0c0edc478a3448a0d371755bd614854505d2f158499d9881bfffa8b05c5b3e8")
        self.assertEqual(outs2[1].amount, Decimal("0.600000000000"))
        self.assertEqual(outs2[2].stealth_address, "f9aeb5f16117f363adcd22f6b73d6e35eda64c25fee2f59208bd68d411b6d0c6")
        self.assertEqual(outs2[2].amount, Decimal("0.000000000700"))
        self.assertEqual(outs2[3].stealth_address, "17e36384cf11a4d85be1320c0e221505818edbb2d6634dd54db24e25570d0f75")
        self.assertEqual(outs2[3].amount, Decimal("0.000000500000"))
        self.assertEqual(outs2[4].stealth_address, "8b7e5dac3e0e45f9e7213ec3d4a465c5301b20f8ef30a5b2b5baba80867952b3")
        self.assertEqual(outs2[4].amount, Decimal("0.000000000070"))
        self.assertEqual(outs2[5].stealth_address, "d1e24eeaa62232cb0e4be536fc785e03075416457dd2b704437bced16da52500")
        self.assertEqual(outs2[5].amount, Decimal("0.000000001000"))
        self.assertEqual(outs2[6].stealth_address, "52c26fcce9d0a41f91ec57074e2cbfe301ca96b556e861deba51cd54e3e5b3e3")
        self.assertEqual(outs2[6].amount, Decimal("0.000010000000"))
        self.assertEqual(outs2[7].stealth_address, "c5859574278889dede61d5aa341e14d2fb2acf45941486276f61dd286e7f8895")
        self.assertEqual(outs2[7].amount, Decimal("0.000000010000"))
        self.assertEqual(outs2[8].stealth_address, "a3556072b7c8f77abdd16fe762fe1099c10c5ab071e16075ce0c667a3eacf1cc")
        self.assertEqual(outs2[8].amount, Decimal("0.090000000000"))
        self.assertEqual(outs2[9].stealth_address, "d72affedd142c6a459c42318169447f22042dba0d93c0f7ade42ddb222de8914")
        self.assertEqual(outs2[9].amount, Decimal("0.009000000000"))

    def test_extra_unknown_tag(self):
        # try initializing as string
        ep = ExtraParser(
            "0169858d0d6de79c2dfd94b3f97745a12c9a7a61ffbae16b7a34bbf5b36b75084302086003c919"
            "1772d1f90300786a796a227d07e9ae41ff9248a6b2e55adb3f6a42eb4c7ccc1c1b3d0f42c524")
        with self.assertRaises(ValueError):
            pdata = ep.parse()

        # also try initializing as bytes
        ep = ExtraParser(
            b"015894c0e5a8d376e931df4b4ae45b753d9442de52ec8d94036253fba5aeff9782020901cb0e5e"
            b"5a80a4e135ff301ea13334dfbe1508dafcaa32762a86cf12cd4fd193ee9807edcb91bc87f6ccb6"
            b"02384b54dff4664b232a058b8d28ad7d")
        with self.assertRaises(ValueError):
            pdata = ep.parse()
