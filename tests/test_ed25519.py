from binascii import hexlify, unhexlify
import json
import os
import unittest

from monero import ed25519


class TestEd25519(unittest.TestCase):
    base_path = os.path.join(os.path.dirname(__file__), "data", "test_ed25519")

    def modulo_python(self, v):
        return v % ed25519.l

    def test_scalar_reduce(self):
        with open(os.path.join(self.base_path, "scalar_reduce.json"), "rb") as jsonfile:
            suite = json.load(jsonfile)
        for input_, data in suite.items():
            input_bin = ed25519.pad_to_64B(unhexlify(input_))
            integer = ed25519.decodeint(input_bin)
            print(integer)
            print(ed25519.l)
            self.assertEqual(data["integer"], integer)
            modulo_bin = ed25519.scalar_reduce(input_bin)
            print(hexlify(modulo_bin).decode())
            print(hexlify(ed25519.encodeint(self.modulo_python(integer))).decode())
            print(ed25519.decodeint(modulo_bin))
            print(data["modulo"])
            self.assertEqual(data["modulo"], ed25519.decodeint(modulo_bin))
            modulo_hex = hexlify(modulo_bin).decode()
            self.assertEqual(data["result"], modulo_hex)
