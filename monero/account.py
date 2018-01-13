from . import address
from . import prio


class Account(object):
    index = None

    def __init__(self, backend, index):
        self.index = index
        self._backend = backend

    def get_balances(self):
        return self._backend.get_balances(account=self.index)

    def get_balance(self, unlocked=False):
        return self._backend.get_balances(account=self.index)[1 if unlocked else 0]

    def get_address(self):
        """
        Return account's main address.
        """
        return self._backend.get_addresses(account=self.index)[0]

    def get_addresses(self):
        return self._backend.get_addresses(account=self.index)

    def new_address(self, label=None):
        return self._backend.new_address(account=self.index, label=label)

    def get_payments(self, payment_id=None):
        return self._backend.get_payments(account=self.index, payment_id=payment_id)

    def get_transactions_in(self):
        return self._backend.get_transactions_in(account=self.index)

    def get_transactions_out(self):
        return self._backend.get_transactions_out(account=self.index)

    def transfer(self, address, amount, priority=prio.NORMAL, ringsize=5, payment_id=None, unlock_time=0):
        return self._backend.transfer(
            [(address, amount)],
            priority,
            ringsize,
            payment_id,
            unlock_time,
            account=self.index)

    def transfer_multiple(self, destinations, priority=prio.NORMAL, ringsize=5, payment_id=None, unlock_time=0):
        """
        destinations = [(address, amount), ...]
        """
        return self._backend.transfer(
            destinations,
            priority,
            ringsize,
            payment_id,
            unlock_time,
            account=self.index)
