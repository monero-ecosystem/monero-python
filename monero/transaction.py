class Transaction(object):
    hash = None
    height = None
    timestamp = None
    fee = None
    blob = None

    def __init__(self, hash=None, **kwargs):
        self.hash = hash
        self.height = kwargs.get('height', self.height)
        self.timestamp = kwargs.get('timestamp', self.timestamp)
        self.fee = kwargs.get('fee', self.fee)
        self.blob = kwargs.get('blob', self.blob)

    def __repr__(self):
        return self.hash


class LocalTransaction(Transaction):
    """A transaction that concerns local wallet, either incoming or outgoing."""
    payment_id = None
    amount = None
    local_address = None

    def __init__(self, **kwargs):
        super(LocalTransaction, self).__init__(**kwargs)
        self.payment_id = kwargs.get('payment_id', self.payment_id)
        self.amount = kwargs.get('amount', self.amount)
        self.local_address = kwargs.get('local_address', self.local_address)


class Payment(LocalTransaction):
    """Incoming Transaction"""
    pass


class Transfer(LocalTransaction):
    """Outgoing Transaction"""
    key = None
    note = ''

    def __init__(self, **kwargs):
        super(Transfer, self).__init__(**kwargs)
        self.key = kwargs.get('key', self.key)
        self.note = kwargs.get('note', self.note)
