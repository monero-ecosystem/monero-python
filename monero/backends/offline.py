from .. import exceptions
from ..account import Account
from ..address import Address
from ..numbers import EMPTY_KEY
from ..seed import Seed


class WalletIsOffline(exceptions.BackendException):
    pass


class OfflineWallet(object):
    """
    Offline backend for Monero wallet. Provides support for address generation.
    """

    _address = None
    _svk = None
    _ssk = EMPTY_KEY

    def __init__(self, address, view_key=None, spend_key=None):
        self._address = Address(address)
        self._svk = view_key or self._svk
        self._ssk = spend_key or self._ssk

    def spend_key(self):
        return self._ssk

    def view_key(self):
        return self._svk

    def seed(self):
        return Seed(self._ssk)

    def accounts(self):
        return [Account(self, 0)]

    def addresses(self, account=0, addr_indices=None):
        if account == 0 and (addr_indices == [0] or addr_indices is None):
            return [self._address]
        raise WalletIsOffline()  # pragma: no cover (this should never happen)

    def is_offline(self, *_, **__):
        raise WalletIsOffline()

    address_balance = (
        balances
    ) = (
        export_key_images
    ) = (
        export_outputs
    ) = (
        height
    ) = (
        import_key_images
    ) = (
        import_outputs
    ) = (
        new_account
    ) = new_address = transfer = transfers_in = transfers_out = sweep_all = is_offline
