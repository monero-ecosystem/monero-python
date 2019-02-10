import unittest
from monero import ed25519

class Ed25519TestCase(unittest.TestCase):
    def test_comp_decomp(self):
        pts = [(0,0), (1,1), (3,5), (5,3), (7,11), (11,7)]
        for p in pts:
            self.assertEqual(p, ed25519.compress(ed25519.decompress(p)))
