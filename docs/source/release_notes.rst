Release Notes
=============

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
