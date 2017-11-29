from . import address
from . import prio


class Account(object):
    index = None

    def __init__(self, backend, index):
        self.index = index
        self._backend = backend

    def get_balance(self):
        return self._backend.get_balance(account=self.index)

    def get_address(self):
        """
        Return account's main address.
        """
        return self._backend.get_address(account=self.index)[0]

    def get_addresses(self):
        return self._backend.get_addresses(account=self.index)

    def get_payments_in(self):
        return self._backend.get_payments_in(account=self.index)

    def get_payments_out(self):
        return self._backend.get_payments_out(account=self.index)

    def transfer(self, address, amount, priority=prio.NORMAL, mixin=5, unlock_time=0):
        return self._backend.transfer(
            [(address, amount)],
            priority,
            mixin,
            unlock_time,
            account=self.index)

    def transfer_multiple(self, destinations, priority=prio.NORMAL, mixin=5, unlock_time=0):
        """
        destinations = [(address, amount), ...]
        """
        return self._backend.transfer(
            destinations,
            priority,
            mixin,
            unlock_time,
            account=self.index)
