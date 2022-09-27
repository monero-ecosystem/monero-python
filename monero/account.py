from . import const
from .transaction import PaymentManager


class Account(object):
    """Monero account.

    Provides interface to operate on a wallet's account.

    Accounts belong to a :class:`Wallet <monero.wallet.Wallet>` and act like
    separate sub-wallets. No funds can be moved between accounts off-chain
    (without a transaction).

    :param backend: a wallet backend
    :param index: the account's index within the wallet
    :param label: optional account label as `str`
    """

    index = None
    wallet = None
    label = None

    def __init__(self, backend, index, label=None):
        self.index = index
        self.label = label
        self._backend = backend
        self.incoming = PaymentManager(index, backend, "in")
        self.outgoing = PaymentManager(index, backend, "out")

    def balances(self):
        """
        Returns a tuple of balance and unlocked balance.

        :rtype: (Decimal, Decimal)
        """
        return self._backend.balances(account=self.index)

    def balance(self, unlocked=False):
        """
        Returns specified balance.

        :param unlocked: if `True`, return the unlocked balance, otherwise return total balance
        :rtype: Decimal
        """
        return self._backend.balances(account=self.index)[1 if unlocked else 0]

    def address(self):
        """
        Return account's main address.

        :rtype: :class:`SubAddress <monero.address.SubAddress>`
        """
        return self._backend.addresses(account=self.index, addr_indices=[0])[0]

    def addresses(self):
        """
        Returns all addresses of the account.

        :rtype: list
        """
        return self._backend.addresses(account=self.index)

    def new_address(self, label=None):
        """
        Creates a new address.

        :param label: address label as `str`
        :rtype: tuple of subaddress, subaddress index (minor):
                (:class:`SubAddress <monero.address.SubAddress>`, `int`)
        """
        return self._backend.new_address(account=self.index, label=label)

    def address_balance(self, addresses=None):
        """
        Returns balances of given addresses, or all addresses if none given.

        :param addresses: a sequence of address as :class:`Address <monero.address.Addresss>`
                    or their indexes within the account as `int`s
        :rtype: list of index, subaddress, balance, num_UTXOs:
                    (`int`, :class:`Address <monero.address.Address>`, `Decimal`, `int`)
        """
        indices = None
        _addresses = self.addresses()
        if addresses is not None:
            indices = []
            for addr in addresses:
                if isinstance(addr, int):
                    indices.append(addr)
                else:
                    indices.append(_addresses.index(addr))
        return self._backend.address_balance(account=self.index, indices=indices)

    def transfer(
        self,
        address,
        amount,
        priority=const.PRIO_NORMAL,
        payment_id=None,
        unlock_time=0,
        relay=True,
    ):
        """
        Sends a transfer. Returns a list of resulting transactions.

        :param address: destination :class:`Address <monero.address.Address>` or subtype
        :param amount: amount to send
        :param priority: transaction priority, implies fee. The priority can be a number
                    from 1 to 4 (unimportant, normal, elevated, priority) or a constant
                    from `monero.const.PRIO_*`.
        :param payment_id: ID for the payment (must be None if
                        :class:`IntegratedAddress <monero.address.IntegratedAddress>`
                        is used as the destination)
        :param unlock_time: the extra unlock delay
        :param relay: if `True`, the wallet will relay the transaction(s) to the network
                        immediately; when `False`, it will only return the transaction(s)
                        so they might be broadcasted later
        :rtype: list of :class:`Transaction <monero.transaction.Transaction>`
        """
        return self._backend.transfer(
            [(address, amount)],
            priority,
            payment_id,
            unlock_time,
            account=self.index,
            relay=relay,
        )

    def transfer_multiple(
        self,
        destinations,
        priority=const.PRIO_NORMAL,
        payment_id=None,
        unlock_time=0,
        relay=True,
    ):
        """
        Sends a batch of transfers. Returns a list of resulting transactions.

        :param destinations: a list of destination and amount pairs:
                    [(:class:`Address <monero.address.Address>`, `Decimal`), ...]
        :param priority: transaction priority, implies fee. The priority can be a number
                    from 1 to 4 (unimportant, normal, elevated, priority) or a constant
                    from `monero.const.PRIO_*`.
        :param payment_id: ID for the payment (must be None if
                    :class:`IntegratedAddress <monero.address.IntegratedAddress>`
                    is used as the destination)
        :param unlock_time: the extra unlock delay
        :param relay: if `True`, the wallet will relay the transaction(s) to the network
                    immediately; when `False`, it will only return the transaction(s)
                    so they might be broadcast later
        :rtype: list of transaction and amount pairs:
                [(:class:`Transaction <monero.transaction.Transaction>`, `Decimal`), ...]
        """
        return self._backend.transfer(
            destinations,
            priority,
            payment_id,
            unlock_time,
            account=self.index,
            relay=relay,
        )

    def sweep_all(
        self,
        address,
        priority=const.PRIO_NORMAL,
        payment_id=None,
        subaddr_indices=None,
        unlock_time=0,
        relay=True,
    ):
        """
        Sends all unlocked balance to an address. Returns a list of resulting transactions.

        :param address: destination :class:`Address <monero.address.Address>` or subtype
        :param priority: transaction priority, implies fee. The priority can be a number
                    from 1 to 4 (unimportant, normal, elevated, priority) or a constant
                    from `monero.const.PRIO_*`.
        :param payment_id: ID for the payment (must be None if
                    :class:`IntegratedAddress <monero.address.IntegratedAddress>`
                    is used as the destination)
        :param subaddr_indices: a sequence of subaddress indices to sweep from. Empty sequence
                    or `None` means sweep all positive balances.
        :param unlock_time: the extra unlock delay
        :param relay: if `True`, the wallet will relay the transaction(s) to the network
                    immediately; when `False`, it will only return the transaction(s)
                    so they might be broadcast later
        :rtype: list of :class:`Transaction <monero.transaction.Transaction>`
        """
        return self._backend.sweep_all(
            address,
            priority,
            payment_id,
            subaddr_indices,
            unlock_time,
            account=self.index,
            relay=relay,
        )
