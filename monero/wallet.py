from . import address
from . import prio
from . import account

class Wallet(object):
    accounts = None

    def __init__(self, backend):
        self._backend = backend
        self.refresh()

    def refresh(self):
        self.accounts = self.accounts or []
        idx = 0
        for _acc in self._backend.get_accounts():
            try:
                if self.accounts[idx]:
                    continue
            except IndexError:
                pass
            self.accounts.append(_acc)
            idx += 1

    def new_account(self, label=None):
        acc, addr = self._backend.new_account(label=label)
        assert acc.index == len(self.accounts)
        self.accounts.append(acc)
        return acc

    # Following methods operate on default account (index=0)
    def get_balances(self):
        return self.accounts[0].get_balances()

    def get_balance(self, unlocked=False):
        return self.accounts[0].get_balance(unlocked=unlocked)

    def get_address(self, index=0):
        return self.accounts[0].get_addresses()[0]

    def new_address(self, label=None):
        return self.accounts[0].new_address(label=label)

    def get_payments(self, payment_id=None):
        return self.accounts[0].get_payments(payment_id=payment_id)

    def get_transactions_in(self):
        return self.accounts[0].get_transactions_in()

    def get_transactions_out(self):
        return self.accounts[0].get_transactions_out()

    def transfer(self, address, amount, priority=prio.NORMAL, mixin=5, payment_id=None, unlock_time=0):
        return self.accounts[0].transfer(
                address,
                amount,
                priority=priority,
                mixin=mixin,
                payment_id=None,
                unlock_time=unlock_time)

    def transfer_multiple(self, destinations, priority=prio.NORMAL, mixin=5, payment_id=None, unlock_time=0):
        """
        destinations = [(address, amount), ...]
        """
        return self.accounts[0].transfer_multiple(
                destinations,
                priority=priority,
                mixin=mixin,
                payment_id=None,
                unlock_time=unlock_time)
