from . import address
from . import prio
from . import account
from . import transaction

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

    def get_height(self):
        """
        Returns the height of the wallet.
        """
        return self._backend.get_height()

    def get_spend_key(self):
        """
        Returns private spend key.
        """
        return self._backend.get_spend_key()

    def get_view_key(self):
        """
        Returns private view key.
        """
        return self._backend.get_view_key()

    def get_seed(self):
        """
        Returns word seed.
        """
        return self._backend.get_seed()

    def new_account(self, label=None):
        acc, addr = self._backend.new_account(label=label)
        assert acc.index == len(self.accounts)
        self.accounts.append(acc)
        return acc

    def get_transaction(self, hash):
        return self._backend.get_transaction(hash)

    def confirmations(self, txn):
        txn = self._backend.get_transaction(txn)
        if txn.height is None:
            return 0
        return max(0, self.get_height() - txn.height)

    # Following methods operate on default account (index=0)
    def get_balances(self):
        return self.accounts[0].get_balances()

    def get_balance(self, unlocked=False):
        return self.accounts[0].get_balance(unlocked=unlocked)

    def get_address(self):
        return self.accounts[0].get_addresses()[0]

    def get_addresses(self):
        return self.accounts[0].get_addresses()

    def new_address(self, label=None):
        return self.accounts[0].new_address(label=label)

    def get_payments(self, payment_id=None):
        return self.accounts[0].get_payments(payment_id=payment_id)

    def get_transactions_in(self, confirmed=True, unconfirmed=False):
        return self.accounts[0].get_transactions_in(confirmed=confirmed, unconfirmed=unconfirmed)

    def get_transactions_out(self, confirmed=True, unconfirmed=True):
        return self.accounts[0].get_transactions_out(confirmed=confirmed, unconfirmed=unconfirmed)

    def transfer(self, address, amount,
            priority=prio.NORMAL, ringsize=5, payment_id=None, unlock_time=0,
            relay=True):
        return self.accounts[0].transfer(
                address,
                amount,
                priority=priority,
                ringsize=ringsize,
                payment_id=None,
                unlock_time=unlock_time,
                relay=relay)

    def transfer_multiple(self, destinations,
            priority=prio.NORMAL, ringsize=5, payment_id=None, unlock_time=0,
            relay=True):
        """
        destinations = [(address, amount), ...]
        """
        return self.accounts[0].transfer_multiple(
                destinations,
                priority=priority,
                ringsize=ringsize,
                payment_id=None,
                unlock_time=unlock_time,
                relay=relay)
