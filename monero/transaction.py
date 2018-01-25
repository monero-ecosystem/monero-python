class Payment(object):
    tx_hash = None
    payment_id = None
    amount = None
    timestamp = None
    transaction = None

    def __init__(self, **kwargs):
        self.tx_hash = kwargs.get('tx_hash', self.tx_hash)
        self.amount = kwargs.get('amount', self.amount)
        self.timestamp = kwargs.get('timestamp', self.timestamp)
        self.payment_id = kwargs.get('payment_id', self.payment_id)
        self.transaction = kwargs.get('transaction', self.transaction)


class IncomingPayment(Payment):
    received_by = None

    def __init__(self, **kwargs):
        super(IncomingPayment, self).__init__(**kwargs)
        self.received_by = kwargs.get('received_by', self.received_by)


class OutgoingPayment(Payment):
    sent_from = None
    note = ''

    def __init__(self, **kwargs):
        super(OutgoingPayment, self).__init__(**kwargs)
        self.sent_from = kwargs.get('sent_from', self.sent_from)
        self.note = kwargs.get('note', self.sent_from)


class Transaction(object):
    hash = None
    fee = None
    height = None
    timestamp = None
    key = None
    blob = None

    def __init__(self, **kwargs):
        self.hash = kwargs.get('hash', self.hash)
        self.fee = kwargs.get('fee', self.fee)
        self.height = kwargs.get('height', self.height)
        self.timestamp = kwargs.get('timestamp', self.timestamp)
        self.key = kwargs.get('key', self.key)
        self.blob = kwargs.get('blob', self.blob)
