Release Notes
=============

0.99
----

This is a test release before 1.0. The reference library for Ed25519 cryptography has been dropped
and replaced with `pynacl`_ which is a wrapper over `libsodium`_, the industry standard
lightning-fast C library.

There are no backward-incompatible changes in the API. The aim is to have the software tested
thoroughly before the first stable release.

.. _`pynacl`: https://github.com/pyca/pynacl/
.. _`libsodium`: https://github.com/jedisct1/libsodium/

0.9
---

The hashing library ``sha3`` has been replaced by ``pycryptodomex`` which is a more actively
maintained project. However, the code still may work with the old ``sha3`` module. Just ignore
the new dependency and run as usual.

0.8
---

Backward-incompatible changes:

 1. The ``monero.prio`` submodule has been removed. Switch to ``monero.const``.
 2. Methods ``.is_mainnet()``, ``.is_testnet()``, ``.is_stagenet()`` have been removed from
    ``monero.address.Address`` instances. Use ``.net`` attribute instead.

0.7
---

Backward-incompatible changes:

 1. The ``Transaction.blob`` changes from hexadecimal to raw binary data (``bytes`` in Python 3,
    ``str`` in Python 2).

Deprecations:

 1. ``monero.const`` has been introduced. Transaction priority consts will move to
    ``monero.const.PRIO_*``. The ``monero.prio`` submodule has been deprecated and will be gone
    in 0.8.
 2. Methods ``.is_mainnet()``, ``.is_testnet()``, ``.is_stagenet()`` have been deprecated and
    new ``.net`` property has been added to all ``monero.address.Address`` instances. The values
    are from among ``monero.const.NET_*`` and have string representation of ``"main"``, ``"test"``
    and ``"stage"`` respectively. Likewise, ``monero.seed.Seed.public_address()`` accepts those
    new values.
    All deprecated uses will raise proper warnings in 0.7.x and will be gone with 0.8.

0.6
---

With version 0.6 the package name on PyPi has changed from `monero-python` to just `monero`.

Backward-incompatible changes:

 1. The ``.new_address()`` method of both ``Wallet`` and ``Account`` returns a 2-element tuple of
    (`subaddress`, `index`) where the additional element is the index of the subaddress within
    current account.

0.5
---

Backward-incompatible changes:

 1. The ``ringsize`` parameter is gone from ``.transfer()`` and ``.transfer_multiple()`` methods of
    both ``Wallet`` and ``Account``. Since Monero 0.13 the ring size is of constant value 11.
 2. The class hierarchy in ``monero.address`` has been reordered. ``Address`` now represents only
    master address of a wallet. ``SubAddress`` doesn't inherit after it anymore, but all classes
    share the common base of ``BaseAddress``.
    
    In particular, make sure that your code doesn't check a presence of Monero address by checking
    ``isinstance(x, monero.address.Address)``. That will not work for sub-addresses anymore.
    Replace it by ``isinstance(x, monero.address.BaseAddress)``.
