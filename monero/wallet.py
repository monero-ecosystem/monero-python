from . import prio
from .transaction import Payment, PaymentManager


class Wallet(object):
    """
    Monero wallet.

    Provides interface to operate on a wallet.

    Wallet consists of :class:`accounts <monero.account.Account>`. In Monero 0.11 and earlier the wallet has only a single account
    with index 0. In later versions there might be multiple accounts, but a fresh wallet starts
    with only one.

    The list of accounts will be initialized under the `accounts` attribute.

    The wallet exposes a number of methods that operate on the default account (of index 0).

    :param backend: a wallet backend
    """
    accounts = None

    def __init__(self, backend):
        self._backend = backend
        self.incoming = PaymentManager(0, backend, 'in')
        self.outgoing = PaymentManager(0, backend, 'out')
        self.refresh()

    def refresh(self):
        """
        Reloads the wallet and its accounts. By default, this method is called only once,
        on :class:`Wallet` initialization. When the wallet is accessed by multiple clients or
        exists in multiple instances, calling `refresh()` will be necessary to update
        the list of accounts.
        """
        self.accounts = self.accounts or []
        idx = 0
        for _acc in self._backend.accounts():
            try:
                if self.accounts[idx]:
                    continue
            except IndexError:
                pass
            self.accounts.append(_acc)
            idx += 1

    def height(self):
        """
        Returns the height of the wallet.

        :rtype: int
        """
        return self._backend.height()

    def spend_key(self):
        """
        Returns private spend key.

        :rtype: str
        """
        return self._backend.spend_key()

    def view_key(self):
        """
        Returns private view key.

        :rtype: str
        """
        return self._backend.view_key()

    def seed(self):
        """
        Returns word seed.

        :rtype: str
        """
        return self._backend.seed()

    def new_account(self, label=None):
        """
        Creates new account, appends it to the :class:`Wallet`'s account list and returns it.

        :rtype: :class:`Account`
        """
        acc, addr = self._backend.new_account(label=label)
        assert acc.index == len(self.accounts)
        self.accounts.append(acc)
        return acc

    def confirmations(self, txn_or_pmt):
        """
        Returns the number of confirmations for given
        :class:`Transaction <monero.transaction.Transaction>` or
        :class:`Payment <monero.transaction.Payment>` object.

        :rtype: int
        """
        if isinstance(txn_or_pmt, Payment):
            txn = txn_or_pmt.transaction
        else:
            txn = txn_or_pmt
        try:
            return max(0, self.height() - txn.height)
        except TypeError:
            return 0

    # Following methods operate on default account (index=0)
    def balances(self):
        """
        Returns a tuple of balance and unlocked balance.

        :rtype: (Decimal, Decimal)
        """
        return self.accounts[0].balances()

    def balance(self, unlocked=False):
        """
        Returns specified balance.

        :param unlocked: if `True`, return the unlocked balance, otherwise return total balance
        :rtype: Decimal
        """
        return self.accounts[0].balance(unlocked=unlocked)

    def address(self):
        """
        Returns wallet's master address.

        :rtype: :class:`Address <monero.address.Address>`
        """
        return self.accounts[0].addresses()[0]

    def addresses(self):
        """
        Returns all addresses of the default account.

        :rtype: list of :class:`Address <monero.address.Address>` and
                :class:`SubAddress <monero.address.SubAddress>`
        """
        return self.accounts[0].addresses()

    def new_address(self, label=None):
        """
        Creates a new address in the default account.

        :rtype: :class:`SubAddress <monero.address.SubAddress>`
        """
        return self.accounts[0].new_address(label=label)

    def transfer(self, address, amount,
            priority=prio.NORMAL, ringsize=7, payment_id=None, unlock_time=0,
            relay=True):
        """
        Sends a transfer from the default account. Returns a list of resulting transactions.

        :param address: destination :class:`Address <monero.address.Address>` or subtype
        :param amount: amount to send
        :param priority: transaction priority, implies fee. The priority can be a number
                    from 1 to 4 (unimportant, normal, elevated, priority) or a constant
                    from `monero.prio`.
        :param ringsize: the ring size (mixin + 1)
        :param payment_id: ID for the payment (must be None if
                        :class:`IntegratedAddress <monero.address.IntegratedAddress>`
                        is used as the destination)
        :param unlock_time: the extra unlock delay
        :param relay: if `True`, the wallet will relay the transaction(s) to the network
                        immediately; when `False`, it will only return the transaction(s)
                        so they might be broadcasted later
        :rtype: list of :class:`Transaction <monero.transaction.Transaction>`
        """
        return self.accounts[0].transfer(
                address,
                amount,
                priority=priority,
                ringsize=ringsize,
                payment_id=payment_id,
                unlock_time=unlock_time,
                relay=relay)

    def transfer_multiple(self, destinations,
            priority=prio.NORMAL, ringsize=7, payment_id=None, unlock_time=0,
            relay=True):
        """
        Sends a batch of transfers from the default account. Returns a list of resulting
        transactions.

        :param destinations: a list of destination and amount pairs: [(address, amount), ...]
        :param priority: transaction priority, implies fee. The priority can be a number
                    from 1 to 4 (unimportant, normal, elevated, priority) or a constant
                    from `monero.prio`.
        :param ringsize: the ring size (mixin + 1)
        :param payment_id: ID for the payment (must be None if
                        :class:`IntegratedAddress <monero.address.IntegratedAddress>`
                        is used as a destination)
        :param unlock_time: the extra unlock delay
        :param relay: if `True`, the wallet will relay the transaction(s) to the network
                        immediately; when `False`, it will only return the transaction(s)
                        so they might be broadcasted later
        :rtype: list of :class:`Transaction <monero.transaction.Transaction>`
        """
        return self.accounts[0].transfer_multiple(
                destinations,
                priority=priority,
                ringsize=ringsize,
                payment_id=payment_id,
                unlock_time=unlock_time,
                relay=relay)
