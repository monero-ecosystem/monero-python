from binascii import hexlify, unhexlify
import struct

from . import address
from .backends.jsonrpc import JSONRPCWallet
from . import base58
from . import const
from . import ed25519
from . import numbers
from .transaction import Payment, PaymentManager
from .keccak import keccak_256


class Wallet(object):
    """
    Monero wallet.

    Provides interface to operate on a wallet.

    A wallet consists of :class:`accounts <monero.account.Account>`. Fresh wallets start
    with only one account but you may create more. Although it's possible to combine funds
    from different accounts, or even wallets, in a single transaction, this code closely
    follows the idea of separation introduced in the original wallet software.

    The list of accounts will be initialized under the `accounts` attribute.

    The wallet exposes a number of methods that operate on the default account (of index 0).

    :param backend: a wallet backend
    :param \\**kwargs: arguments to initialize a :class:`JSONRPCWallet <monero.backends.jsonrpc.JSONRPCWallet>`
                        instance if no backend is given
    """

    accounts = None

    def __init__(self, backend=None, **kwargs):
        if backend and len(kwargs):
            raise ValueError("backend already given, other arguments are extraneous")

        self._backend = backend if backend else JSONRPCWallet(**kwargs)
        self.incoming = PaymentManager(0, self._backend, "in")
        self.outgoing = PaymentManager(0, self._backend, "out")
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
            _acc.wallet = self
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
        Returns private spend key. None if wallet is view-only.

        :rtype: str or None
        """
        key = self._backend.spend_key()
        if key == numbers.EMPTY_KEY:
            return None
        return key

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

        :param label: account label as `str`
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

    def export_outputs(self):
        """
        Exports outputs in hexadecimal format.

        :rtype: str
        """
        return self._backend.export_outputs()

    def import_outputs(self, outputs_hex):
        """
        Imports outputs in hexadecimal format. Returns number of imported outputs.

        :rtype: int

        """
        return self._backend.import_outputs(outputs_hex)

    def export_key_images(self):
        """
        Exports signed key images as a list of dicts.

        :rtype: [dict, dict, ...]
        """
        return self._backend.export_key_images()

    def import_key_images(self, key_images_hex):
        """
        Imports key images from a list of dicts. Returns tuple of (height, spent, unspent).

        :rtype: (int, Decimal, Decimal)

        """
        return self._backend.import_key_images(key_images_hex)

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
        return self.accounts[0].address()

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

        :rtype: tuple of subaddress, subaddress index (minor):
                (:class:`SubAddress <monero.address.SubAddress>`, `int`)
        """
        return self.accounts[0].new_address(label=label)

    def get_address(self, major, minor):
        """
        Calculates sub-address for account index (`major`) and address index within
        the account (`minor`).

        :rtype: :class:`BaseAddress <monero.address.BaseAddress>`
        """
        # ensure indexes are within uint32
        if major < 0 or major >= 2 ** 32:
            raise ValueError("major index {} is outside uint32 range".format(major))
        if minor < 0 or minor >= 2 ** 32:
            raise ValueError("minor index {} is outside uint32 range".format(minor))
        master_address = self.address()
        if major == minor == 0:
            return master_address
        master_svk = unhexlify(self.view_key())
        master_psk = unhexlify(self.address().spend_key())
        # m = Hs("SubAddr\0" || master_svk || major || minor)
        hsdata = b"".join(
            [
                b"SubAddr\0",
                master_svk,
                struct.pack("<I", major),
                struct.pack("<I", minor),
            ]
        )
        m = keccak_256(hsdata).digest()
        # D = master_psk + m * B
        D = ed25519.edwards_add(
            master_psk, ed25519.scalarmult_B(ed25519.scalar_reduce(m))
        )
        # C = master_svk * D
        C = ed25519.scalarmult(master_svk, D)
        netbyte = bytearray(
            [const.SUBADDR_NETBYTES[const.NETS.index(master_address.net)]]
        )
        data = netbyte + D + C
        checksum = keccak_256(data).digest()[:4]
        return address.SubAddress(base58.encode(hexlify(data + checksum)))

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
        Sends a transfer from the default account. Returns a list of resulting transactions.

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
                    so they might be broadcast later
        :rtype: list of :class:`Transaction <monero.transaction.Transaction>`
        """
        return self.accounts[0].transfer(
            address,
            amount,
            priority=priority,
            payment_id=payment_id,
            unlock_time=unlock_time,
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
        Sends a batch of transfers from the default account. Returns a list of resulting
        transactions and amounts.

        :param destinations: a list of destination and amount pairs: [(address, amount), ...]
        :param priority: transaction priority, implies fee. The priority can be a number
                from 1 to 4 (unimportant, normal, elevated, priority) or a constant
                from `monero.const.PRIO_*`.
        :param payment_id: ID for the payment (must be None if
                :class:`IntegratedAddress <monero.address.IntegratedAddress>`
                is used as a destination)
        :param unlock_time: the extra unlock delay
        :param relay: if `True`, the wallet will relay the transaction(s) to the network
                immediately; when `False`, it will only return the transaction(s)
                so they might be broadcast later
        :rtype: list of transaction and amount pairs:
                [(:class:`Transaction <monero.transaction.Transaction>`, `Decimal`), ...]
        """
        return self.accounts[0].transfer_multiple(
            destinations,
            priority=priority,
            payment_id=payment_id,
            unlock_time=unlock_time,
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
        Sends all unlocked balance from the default account to an address.
        Returns a list of resulting transactions.

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
        return self.accounts[0].sweep_all(
            address,
            priority=priority,
            payment_id=payment_id,
            subaddr_indices=subaddr_indices,
            unlock_time=unlock_time,
            relay=relay,
        )
