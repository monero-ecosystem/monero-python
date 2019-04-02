Using wallet and accounts
=========================

Since Monero 'Helium Hydra' (0.11.x) the wallet handles accounts and deterministically
generated addresses, known as *subaddresses*.

The wallet
----------

The following example shows how to create and retrieve wallet's accounts and
addresses:

.. code-block:: python

    In [1]: from monero.wallet import Wallet

    In [2]: from monero.backends.jsonrpc import JSONRPCWallet

    In [3]: w = Wallet(JSONRPCWallet(port=28088))

    In [4]: w.get_address()
    Out[4]: A2GmyHHJ9jtUhPiwoAbR2tXU9LJu2U6fJjcsv3rxgkVRWU6tEYcn6C1NBc7wqCv5V7NW3zeYuzKf6RGGgZTFTpVC4QxAiAX

Accounts and subaddresses
-------------------------

The accounts are stored in wallet's ``accounts`` attribute, which is a list.

Regardless of the version, **the wallet by default operates on its account of
index 0**, which makes it consistent with the behavior of the CLI wallet
client.

.. code-block:: python

    In [5]: len(w.accounts)
    Out[5]: 1

    In [6]: w.accounts[0]
    Out[6]: <monero.account.Account at 0x7f78992d6898>

    In [7]: w.accounts[0].get_address()
    Out[7]: A2GmyHHJ9jtUhPiwoAbR2tXU9LJu2U6fJjcsv3rxgkVRWU6tEYcn6C1NBc7wqCv5V7NW3zeYuzKf6RGGgZTFTpVC4QxAiAX

    In [8]: w.get_addresses()
    Out[8]: [A2GmyHHJ9jtUhPiwoAbR2tXU9LJu2U6fJjcsv3rxgkVRWU6tEYcn6C1NBc7wqCv5V7NW3zeYuzKf6RGGgZTFTpVC4QxAiAX]


Creating accounts and addresses
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Every wallet can have separate accounts and each account can have numerous
addresses. The ``Wallet.new_account()`` and ``Account.new_address()`` will
create new instances.

.. code-block:: python

    In [9]: w.new_address()
    Out[9]: BenuGf8eyVhjZwdcxEJY1MHrUfqHjPvE3d7Pi4XY5vQz53VnVpB38bCBsf8AS5rJuZhuYrqdG9URc2eFoCNPwLXtLENT4R7

    In [10]: w.get_addresses()
    Out[10]:
    [A2GmyHHJ9jtUhPiwoAbR2tXU9LJu2U6fJjcsv3rxgkVRWU6tEYcn6C1NBc7wqCv5V7NW3zeYuzKf6RGGgZTFTpVC4QxAiAX,
     BenuGf8eyVhjZwdcxEJY1MHrUfqHjPvE3d7Pi4XY5vQz53VnVpB38bCBsf8AS5rJuZhuYrqdG9URc2eFoCNPwLXtLENT4R7]

    In [11]: w.new_account()
    Out[11]: <monero.account.Account at 0x7f7894dffbe0>

    In [12]: len(w.accounts)
    Out[12]: 2

    In [13]: w.accounts[1].get_address()
    Out[13]: Bhd3PRVCnq5T5jjNey2hDSM8DxUgFpNjLUrKAa2iYVhYX71RuCGTekDKZKXoJPAGL763kEXaDSAsvDYb8bV77YT7Jo19GKY

    In [14]: w.accounts[1].new_address()
    Out[14]: Bbz5uCtnn3Gaj1YAizaHw1FPeJ6T7kk7uQoeY48SWjezEAyrWScozLxYbqGxsV5L6VJkvw5VwECAuLVJKQtHpA3GFXJNPYu

    In [15]: w.accounts[1].get_addresses()
    Out[15]:
    [Bhd3PRVCnq5T5jjNey2hDSM8DxUgFpNjLUrKAa2iYVhYX71RuCGTekDKZKXoJPAGL763kEXaDSAsvDYb8bV77YT7Jo19GKY,
     Bbz5uCtnn3Gaj1YAizaHw1FPeJ6T7kk7uQoeY48SWjezEAyrWScozLxYbqGxsV5L6VJkvw5VwECAuLVJKQtHpA3GFXJNPYu]


As mentioned above, the wallet by default operates on the first account, so
``w.new_address()`` is equivalent to ``w.accounts[0].new_address()``.

In the next chapter we will :doc:`learn about addresses <address>`.

API reference
-------------

.. automodule:: monero.wallet
   :members:

.. automodule:: monero.account
   :members:
