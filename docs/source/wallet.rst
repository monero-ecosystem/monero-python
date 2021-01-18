Using wallet and accounts
=========================

The Wallet class provides an abstraction layer to retrieve wallet information, manage accounts and
subaddresses, and of course send transfers.

The wallet
----------

The following example shows how to create and retrieve wallet's accounts and
addresses via the default JSON RPC backend:

.. code-block:: python

    In [1]: from monero.wallet import Wallet

    In [2]: w = Wallet(port=28088)

    In [3]: w.address()
    Out[3]: A2GmyHHJ9jtUhPiwoAbR2tXU9LJu2U6fJjcsv3rxgkVRWU6tEYcn6C1NBc7wqCv5V7NW3zeYuzKf6RGGgZTFTpVC4QxAiAX

Accounts and subaddresses
-------------------------

The accounts are stored in wallet's ``accounts`` attribute, which is a list.

Regardless of the version, **the wallet by default operates on its account of
index 0**, which makes it consistent with the behavior of the CLI wallet
client.

.. code-block:: python

    In [4]: len(w.accounts)
    Out[4]: 1

    In [5]: w.accounts[0]
    Out[5]: <monero.account.Account at 0x7f78992d6898>

    In [6]: w.accounts[0].address()
    Out[6]: A2GmyHHJ9jtUhPiwoAbR2tXU9LJu2U6fJjcsv3rxgkVRWU6tEYcn6C1NBc7wqCv5V7NW3zeYuzKf6RGGgZTFTpVC4QxAiAX

    In [7]: w.addresses()
    Out[7]: [A2GmyHHJ9jtUhPiwoAbR2tXU9LJu2U6fJjcsv3rxgkVRWU6tEYcn6C1NBc7wqCv5V7NW3zeYuzKf6RGGgZTFTpVC4QxAiAX]


Creating accounts and addresses
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Every wallet can have separate accounts and each account can have numerous
addresses. The ``Wallet.new_account()`` and ``Account.new_address()`` will
create new instances, then return a tuple consisting of the subaddress itself,
and the subaddress index within the account.

.. code-block:: python

    In [8]: w.new_address()
    Out[8]: (BenuGf8eyVhjZwdcxEJY1MHrUfqHjPvE3d7Pi4XY5vQz53VnVpB38bCBsf8AS5rJuZhuYrqdG9URc2eFoCNPwLXtLENT4R7, 1)

    In [9]: w.addresses()
    Out[9]:
    [A2GmyHHJ9jtUhPiwoAbR2tXU9LJu2U6fJjcsv3rxgkVRWU6tEYcn6C1NBc7wqCv5V7NW3zeYuzKf6RGGgZTFTpVC4QxAiAX,
     BenuGf8eyVhjZwdcxEJY1MHrUfqHjPvE3d7Pi4XY5vQz53VnVpB38bCBsf8AS5rJuZhuYrqdG9URc2eFoCNPwLXtLENT4R7]

    In [10]: w.new_account()
    Out[10]: <monero.account.Account at 0x7f7894dffbe0>

    In [11]: len(w.accounts)
    Out[11]: 2

    In [12]: w.accounts[1].address()
    Out[12]: Bhd3PRVCnq5T5jjNey2hDSM8DxUgFpNjLUrKAa2iYVhYX71RuCGTekDKZKXoJPAGL763kEXaDSAsvDYb8bV77YT7Jo19GKY

    In [13]: w.accounts[1].new_address()
    Out[13]: (Bbz5uCtnn3Gaj1YAizaHw1FPeJ6T7kk7uQoeY48SWjezEAyrWScozLxYbqGxsV5L6VJkvw5VwECAuLVJKQtHpA3GFXJNPYu, 1)

    In [14]: w.accounts[1].addresses()
    Out[14]:
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
