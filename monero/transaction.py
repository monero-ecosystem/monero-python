class Transaction(object):
    hash = None
    height = None
    timestamp = None
    payment_id = '0000000000000000'
    amount = None
    fee = None
    local_address = None

    def __init__(self, hash=None, **kwargs):
        self.hash = hash
        self.height = kwargs.get('height', self.height)
        self.timestamp = kwargs.get('timestamp', self.timestamp)
        self.payment_id = kwargs.get('payment_id', self.payment_id)
        self.amount = kwargs.get('amount', self.amount)
        self.fee = kwargs.get('fee', self.fee)
        self.local_address = kwargs.get('local_address', self.local_address)

    def __repr__(self):
        return self.hash


class Payment(Transaction):
    """Incoming Transaction"""
    pass


class Transfer(Transaction):
    """Outgoing Transaction"""
    key = None
    blob = None
    note = ''

    def __init__(self, **kwargs):
        super(Transfer, self).__init__(**kwargs)
        self.key = kwargs.get('key', self.key)
        self.note = kwargs.get('note', self.note)
        self.blob = kwargs.get('blob', self.blob)
