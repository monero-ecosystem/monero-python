from datetime import datetime
import six
import unittest

from monero.block import Block
from monero.numbers import from_atomic
from monero.transaction import Transaction


class BlockTestCase(unittest.TestCase):
    def setUp(self):
        self.tx1 = Transaction(
            hash="7e5fea8470c5771315bab4b3c77493d2ff534f5201c7c6b2bab069cb7d21ce7b")
        self.tx2 = Transaction(
            hash="3a2f859dea9d2ad5ecec167719302d4e14e21beef9b74f9583183d8e965d9106")
        self.tx3 = Transaction(
            hash="bde2b5344b63cbe58ce1a724d0a2276aaa4266be5235d5e5fde969446c3e8de1")
        self.tx4 = Transaction(
            hash="24fb42f9f324082658524b29b4cf946a9f5fcfa82194070e2f17c1875e15d5d0")
        self.block1 = Block(
            hash="423cd4d170c53729cf25b4243ea576d1e901d86e26c06d6a7f79815f3fcb9a89",
            height=451992,
            difficulty=3590,
            version= (11,12),
            nonce=140046906,
            orphan=False,
            prev_hash="51f6816891b6a7adedd0f1ad57a846eada1baac476421aa9d32d0630ce3dce41",
            reward=from_atomic(15331952645334),
            timestamp=datetime.fromtimestamp(1573646422),
            transactions=[self.tx1, self.tx2, self.tx3, self.tx4])
        self.block1_duplicate = Block(
            hash="423cd4d170c53729cf25b4243ea576d1e901d86e26c06d6a7f79815f3fcb9a89",
            height=451992,
            difficulty=3590,
            version= (11,12),
            nonce=140046906,
            orphan=False,
            prev_hash="51f6816891b6a7adedd0f1ad57a846eada1baac476421aa9d32d0630ce3dce41",
            reward=from_atomic(15331952645334),
            timestamp=datetime.fromtimestamp(1573646422),
            transactions=[self.tx1, self.tx2, self.tx3, self.tx4])

    def test_basic_ops(self):
        self.assertIsNot(self.block1, self.block1_duplicate)
        self.assertEqual(self.block1, self.block1_duplicate)
        self.assertEqual(self.block1, self.block1.hash)
        self.assertEqual(self.block1, self.block1.hash)
        self.assertNotEqual(self.block1, 1)

    def test_tx_membership(self):
        self.assertIn(self.tx1, self.block1)
        self.assertIn(self.tx2, self.block1)
        self.assertIn(self.tx3, self.block1)
        self.assertIn(self.tx4, self.block1)
        self.assertIn(self.tx1, self.block1_duplicate)
        self.assertIn(self.tx2, self.block1_duplicate)
        self.assertIn(self.tx3, self.block1_duplicate)
        self.assertIn(self.tx4, self.block1_duplicate)

    def test_tx_hash_membership(self):
        self.assertIn(self.tx1.hash, self.block1)
        self.assertIn(self.tx2.hash, self.block1)
        self.assertIn(self.tx3.hash, self.block1)
        self.assertIn(self.tx4.hash, self.block1)
        self.assertIn(self.tx1.hash, self.block1_duplicate)
        self.assertIn(self.tx2.hash, self.block1_duplicate)
        self.assertIn(self.tx3.hash, self.block1_duplicate)
        self.assertIn(self.tx4.hash, self.block1_duplicate)
