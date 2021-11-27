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

    def height(self):
        raise WalletIsOffline()

    def spend_key(self):
        return self._ssk

    def view_key(self):
        return self._svk

    def seed(self):
        return Seed(self._ssk)

    def accounts(self):
        return [Account(self, 0)]

    def new_account(self, label=None):
        raise WalletIsOffline()

    def addresses(self, account=0, addr_indices=None):
        if account == 0 and (addr_indices == [0] or addr_indices is None):
            return [self._address]
        raise WalletIsOffline()  # pragma: no cover (this should never happen)

    def new_address(self, account=0, label=None):
        raise WalletIsOffline()

    def balances(self, account=0):
        raise WalletIsOffline()

    def transfers_in(self, account, pmtfilter):
        raise WalletIsOffline()

    def transfers_out(self, account, pmtfilter):
        raise WalletIsOffline()

    def export_outputs(self):
        raise WalletIsOffline()

    def import_outputs(self, outputs_hex):
        raise WalletIsOffline()

    def export_key_images(self):
        raise WalletIsOffline()

    def import_key_images(self, key_images):
        raise WalletIsOffline()

    def transfer(self, *args, **kwargs):
        raise WalletIsOffline()
