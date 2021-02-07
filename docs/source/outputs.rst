Output recognition
==================

The module provides means to obtain output information from transactions as well as recognize and
decrypt those destined to user's own wallet.

That functionality is a part of ``Transaction.outputs(wallet=None)`` method which may take a wallet
as optional keyword, which will make it analyze outputs against all wallet's addresses.
The wallet **must have the secret view key** while secret spend key is not required (which means
a view-only wallet is enough).

.. note:: Be aware that ed25519 cryptography used there is written in pure Python. Don't expect
        high efficiency there. If you plan a massive analysis of transactions, please check if
        using Monero source code wouldn't be better for you.

.. note:: Please make sure the wallet you provide has all existing subaddresses generated.
        If you run another copy of the wallet and use subaddresses, the wallet you pass to
        ``.outputs()`` **must have the same or bigger set of subaddressses present**. For those
        missing from the wallet, no recognition will happen.

Output data
-----------

The method will return a set of ``Output`` objects. Each of them contains the following attributes:

    * ``stealth_address`` — the stealth address of the output as hexadecimal string,
    * ``amount`` — the amount of the output, ``None`` if unknown,
    * ``index`` — the index of the output,
    * ``transaction`` — the ``Transaction`` the output is a part of,
    * ``payment`` — a ``Payment`` object if the output is destined to provided wallet,
        otherwise ``None``,

An example usage:

.. code-block:: python

    In [1]: from monero.daemon import Daemon

    In [2]: from monero.wallet import Wallet

    In [3]: daemon = Daemon(port=28081)

    In [4]: tx = daemon.transactions("f79a10256859058b3961254a35a97a3d4d5d40e080c6275a3f9779acde73ca8d")[0]

    In [5]: wallet = Wallet(port=28088)

    In [6]: outs = tx.outputs(wallet=wallet)

    In [7]: outs[0].payment.local_address
    Out [7]: 76Qt2xMZ3m7b2tagubEgkvG81pwf9P3JYdxR65H2BEv8c79A9pCBTacEFv87tfdcqXRemBsZLFVGHTWbqBpkoBJENBoJJS9

    In [8]: outs[0].payment.amount
    Out [8]: Decimal('4.000000000000')
