import operator
from .transaction import Transaction


class Block(object):
    """
    A Monero block. Identified by `hash` (optionaly by `height`).

    This class is not intended to be turned into objects by the user,
    it is used by backends.
    """

    hash = None
    height = None
    timestamp = None
    version = None
    difficulty = None
    nonce = None
    orphan = False
    prev_hash = None
    reward = None
    blob = None

    transactions = None

    def __init__(self, **kwargs):
        for k in (
            "hash",
            "height",
            "timestamp",
            "version",
            "difficulty",
            "nonce",
            "prev_hash",
            "reward",
        ):
            setattr(self, k, kwargs.get(k, getattr(self, k)))
        self.orphan = kwargs.get("orphan", self.orphan)
        self.transactions = kwargs.get("transactions", self.transactions or [])
        self.blob = kwargs.get("blob", self.blob)

    def __eq__(self, other):
        if isinstance(other, Block):
            return self.hash == other.hash
        elif isinstance(other, str):
            return self.hash == other
        return super(Block, self).__eq__(other)

    def __contains__(self, tx):
        if isinstance(tx, str):
            txid = tx
        elif isinstance(tx, Transaction):
            txid = tx.hash
        else:
            raise ValueError(
                "Only Transaction or hash strings may be used to test existence in Blocks, "
                "got '{:s}'".format(tx)
            )
        return txid in map(operator.attrgetter("hash"), self.transactions)
