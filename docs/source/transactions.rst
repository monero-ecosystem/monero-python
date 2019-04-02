Sending and receiving payments
==============================

Payments in Monero desire a bit of explanation even for people experienced with cryptocurrency.

The main difference from coins which use transparent blockchain is that Monero transactions do not
disclose sender or recipient's address, nor they tell what the amount is. This is a great feature
that makes Monero stand out, however at the same time it causes difficulties. In the outgoing
payments you won't see the recipient address and, in the incoming ones you won't see the sender.

For this reason, there are two classes representing those, ``IncomingPayment`` and
``OutgoingPayment``. They share most attributes from the parent ``Payment`` class but carry only
one address, depending on which end of the payment your wallet is. Your end address is present
in ``local_address`` attribute.

Retrieving payments
-------------------

Each ``Wallet`` and ``Account`` object has two methods which will return the list of incoming or
outgoing payments:

.. code-block:: python

    In [4]: wallet.incoming()
    Out[4]: 
    [in: e9a71c01875bec20812f71d155bfabf42024fde3ec82475562b817dcc8cbf8dc @ 1087530 2.120000000000 id=cb248105ea6a9189,
     in: a0b876ebcf7c1d499712d84cedec836f9d50b608bb22d6cb49fd2feae3ffed14 @ 1087606 1.000000000000 id=0166d8da6c0045c51273dd65d6f63734beb8a84e0545a185b2cfd053fced9f5d,
     in: d29264ad317e8fdb55ea04484c00420430c35be7b3fe6dd663f99aebf41a786c @ 1087858 3.140000000000 id=03f6649304ea4cb2,
     in: f349c6badfa7f6e46666db3996b569a05c6ac4e85417551ec208d96f8a37294a @ 1088400 1.000000000000 id=0000000000000000,
     in: bc8b7ef53552c2d4bce713f513418894d0e2c8dcaf72e681e1d4d5a202f1eb62 @ 1088394 8.000000000000 id=0000000000000000,
     in: 5ef7ead6a041101ed326568fbb59c128403cba46076c3f353cd110d969dac808 @ 1087601 7.000000000000 id=0000000000000000,
     in: cc44568337a186c2e1ccc080b43b4ae9db26a07b7afd7edeed60ce2fc4a6477f @ 1087530 10.000000000000 id=0000000000000000,
     in: 41304bbb514d1abdfdb0704bf70f8d2ec4e753c57aa34b6d0525631d79113b87 @ 1088400 1.000000000000 id=1f2510a597bd634bbd130cf21e63b4ad01f4565faf0d3eb21589f496bf28f7f2,
     in: f34b495cec77822a70f829ec8a5a7f1e727128d62e6b1438e9cb7799654d610e @ 1087601 3.000000000000 id=f75ad90e25d71a12,
     in: 5c3ab739346e9d98d38dc7b8d36a4b7b1e4b6a16276946485a69797dbf887cd8 @ 1087530 10.000000000000 id=f75ad90e25d71a12,
     in: 4ea70add5d0c7db33557551b15cd174972fcfc73bf0f6a6b47b7837564b708d3 @ 1087530 4.000000000000 id=f75ad90e25d71a12]

    In [5]: wallet.outgoing()
    Out[5]: 
    [out: a8829744952facbfdaab21ca193298edb1fa16f688cd5dbcdff3ed3968155f28 @ 1088411 2.220000000000 id=0000000000000000,
     out: e291fe40c6102a6193c82ac33227c08e5b30a863dba1bc63e13043a25abbb97a @ 1088523 0.123000000000 id=0000000000000000,
     out: 40de45db57eb87eb8395baf5c1dc705602938317d043f463e68ed85b7108f9f3 @ 1088184 1.000000000000 id=0000000000000000,
     out: 2b41226d45edb875634694fccd95f3c174daa5062763eee619ed4475a7b9207a @ 1088184 2.450000000000 id=6cc9350927868849,
     out: 5e8f392a42899294e6b679ddac13cfe1dfe7f034b1e347424218af06c3dfdc85 @ 1088394 1.000000000000 id=6cc9350927868849,
     out: 5d15fef66fe8de715bcbf2c181f97b9932f9f843aef4724f3026fa3cd1082c68 @ 1088521 3.333333333330 id=0000000000000000,
     out: edc7c28e7b07486be48dac0a178f25a3505114267ddaf3e62ab00d9a6e996044 @ 1088394 21.000000000000 id=0000000000000000,
     out: e32cccd7522e760b1c8a571fd08c75e7a1d822874380edc9656f58284eeb2fe5 @ 1088441 0.070000000000 id=0000000000000000,
     out: d09666238129a1e2a71a9b7c6b30564a95baef926556bb658785cb9c38d9b25a @ 1088479 0.210000000000 id=0000000000000000,
     out: 551721b5358b02565d6a9862867e3806b9a2e0d5aa5158d4d30940251d27bbdd @ 1088516 1.111111111000 id=0000000000000000,
     out: 21e7eb651e8a2bc7661975e965ac6b30a6f4033c6a02e96320e41139ad3e307c @ 1088438 0.070000000000 id=0000000000000000,
     out: 34833fef78c7b7c15383a78912344ecfb3ace479d27c4bd6f3e3f136ddc1d6a9 @ 1088538 3.141592653589 id=0000000000000000000000000000000079323846264338327950288419716939]

Filtering payments
^^^^^^^^^^^^^^^^^^

Retrieving all payments and processing them each time sounds uncomfortable, especially in old
wallets which have seen a lot of transfers. To make it easier, you may use filtering on payment
queries.

For example, you may ask for payments from a recent period, limiting the blockchain height:

.. code-block:: python

    In [1]: wallet.incoming(min_height=1088000)
    Out[1]: 
    [in: f349c6badfa7f6e46666db3996b569a05c6ac4e85417551ec208d96f8a37294a @ 1088400 1.000000000000 id=0000000000000000,
     in: bc8b7ef53552c2d4bce713f513418894d0e2c8dcaf72e681e1d4d5a202f1eb62 @ 1088394 8.000000000000 id=0000000000000000,
     in: 41304bbb514d1abdfdb0704bf70f8d2ec4e753c57aa34b6d0525631d79113b87 @ 1088400 1.000000000000 id=1f2510a597bd634bbd130cf21e63b4ad01f4565faf0d3eb21589f496bf28f7f2]

Or ask for specific payment ID:

.. code-block:: python

    In [2]: wallet.incoming(payment_id='f75ad90e25d71a12')
    Out[2]: 
    [in: f34b495cec77822a70f829ec8a5a7f1e727128d62e6b1438e9cb7799654d610e @ 1087601 3.000000000000 id=f75ad90e25d71a12,
     in: 5c3ab739346e9d98d38dc7b8d36a4b7b1e4b6a16276946485a69797dbf887cd8 @ 1087530 10.000000000000 id=f75ad90e25d71a12,
     in: 4ea70add5d0c7db33557551b15cd174972fcfc73bf0f6a6b47b7837564b708d3 @ 1087530 4.000000000000 id=f75ad90e25d71a12]

Or limit by both criteria at the same time:

.. code-block:: python

    In [3]: wallet.incoming(payment_id='f75ad90e25d71a12', min_height=1087601)
    Out[3]: [in: f34b495cec77822a70f829ec8a5a7f1e727128d62e6b1438e9cb7799654d610e @ 1087601 3.000000000000 id=f75ad90e25d71a12]

You may also filter payments by the address:

.. code-block:: python

    In [4]: wallet.incoming(local_address='BhE3cQvB7VF2uuXcpXp28Wbadez6GgjypdRS1F1Mzqn8Advd6q8VfaX8ZoEDobjejrMfpHeNXoX8MjY8q8prW1PEALgr1En')
    Out[4]: 
    [in: 5ef7ead6a041101ed326568fbb59c128403cba46076c3f353cd110d969dac808 @ 1087601 7.000000000000 id=0000000000000000,
     in: 41304bbb514d1abdfdb0704bf70f8d2ec4e753c57aa34b6d0525631d79113b87 @ 1088400 1.000000000000 id=1f2510a597bd634bbd130cf21e63b4ad01f4565faf0d3eb21589f496bf28f7f2,
     in: f34b495cec77822a70f829ec8a5a7f1e727128d62e6b1438e9cb7799654d610e @ 1087601 3.000000000000 id=f75ad90e25d71a12]

The same criteria may be used for filtering outgoing payments.

.. note:: In outgoing payments the `local_address` is always set to the account's main address,
          making such filtering useless.

Payment and Transaction objects
-------------------------------

Each of the payments returned by the wallet carries all essential data:

.. code-block:: python

    In [5]: incoming = wallet.incoming()

    In [6]: incoming[0].amount
    Out[6]: Decimal('2.120000000000')

    In [7]: incoming[0].local_address
    Out[7]: 9tQoHWyZ4yXUgbz9nvMcFZUfDy5hxcdZabQCxmNCUukKYicXegsDL7nQpcUa3A1pF6K3fhq3scsyY88tdB1MqucULcKzWZC

    In [8]: incoming[0].payment_id
    Out[8]: cb248105ea6a9189


It also has a related ``Transaction`` object which offers additional information:

.. code-block:: python

    In [9]: incoming[0].transaction.height
    Out[9]: 1087530

    In [10]: incoming[0].transaction.hash
    Out[10]: 'e9a71c01875bec20812f71d155bfabf42024fde3ec82475562b817dcc8cbf8dc'


Having a running instance of the wallet you may always check the number of confirmations for each
payment object:

.. code-block:: python

    In [11]: wallet.confirmations(incoming[0])
    Out[11]: 5132

Mempool: Unconfirmed payments
-----------------------------

New transactions, before they are mined in the blocks, land in place called mempool. Each network
node updates the mempool contents with new transactions coming from their peers, while offering
them the transactions they do not have.

.. warning:: The presence of a transaction in the mempool is an indication that someone has already
    attempted a payment, but **should never be used as a proof the payment has been done**. A
    transaction in mempool might be replaced by another one spending the same funds, it might
    expire before being included in a block due to competition of other transactions with higher
    fees. It might also be a result of a sophisticated attack.

    **With significant amounts you should also wait for a few confirmations to appear.** The top
    of the blockchain sometimes gets replaced by a competing block. It is a popular practice to
    wait for at least 6 confirmations to appear, which is also the standard in Monero before funds
    get unlocked and can be used in subsequent transactions.

However, it is possible to query the wallet for transactions in the mempool. You may use them as
proofs of payment for less significant amounts where time of acceptance is more important than
limiting the risk of a fraud.

By default, the queries check only the blockchain. This behavior can be changed by ``confirmed``
and ``unconfirmed`` query parameters that accept boolean values:

.. code-block:: python

    In [12]: wallet.incoming(unconfirmed=True, confirmed=False)
    Out[12]: [in: 21fd4c0b2671bfc32d7c968fdf3cab1001042128d9429d4a26d4f3dc76bcecb8 @ pool 3.141592653589 id=0000000000000000]

    In [13]: incoming[0].transaction.height is None
    Out[13]: True

    In [14]: wallet.confirmations(incoming[0])
    Out[14]: 0


You may as well query for both confirmed and unconfirmed transactions using
``wallet.incoming(unconfirmed=True)`` (the default value for ``confirmed`` is ``True``).

.. note:: Mempool transactions don't belong to the blockchain (yet), therefore they have no height.
    Setting ``min_height`` or ``max_height`` arguments will **always exclude mempool
    transactions**. If ``unconfirmed`` is also set to ``True``, a warning will be issued.

.. _sending-payments:

Sending payments
----------------

There are two methods for sending Monero. For a single payment use the ``transfer`` method of
``Wallet`` or ``Account`` object.

It returns a list of resulting transactions. In most cases it will contain only one element, but
sometimes, for example when many small inputs are used, it might become necessary to split the
payment into multiple transactions.

.. code-block:: python

    In [15]: from decimal import Decimal

    In [16]: txs = wallet.transfer(
        'BdYguH2fVo3G37o8bKp8RbTRuRsTpvBaUdxeo9fj6LFrE2XqNMYKytvBLXvNtnbmXtDUwrKLcpeH4NCuhFL2cXikDV4Rzq6',
        Decimal('2.54'))

    In [17]: txs
    Out[17]: [f6e7532322f2cab837e668e7ee7be38f0ca4c0cb8c6cff7aa1cfaaf764735acb]

    In [18]: txs[0].height is None
    Out[18]: True

    In [19]: wallet.confirmations(txs[0])
    Out[19]: 0

    In [20]: wallet.outgoing(unconfirmed=True, confirmed=False)
    Out[20]: [out: f6e7532322f2cab837e668e7ee7be38f0ca4c0cb8c6cff7aa1cfaaf764735acb @ pool 2.540000000000 id=0000000000000000]


When sending multiple payments at once, it is more convenient and cheaper in terms of network fees
to use ``transfer_multiple``:

.. code-block:: python

    In [25]: txs = wallet.transfer_multiple([
        ('Ba8xvGs5qw1JfiQVJDj8D28NuyL7MuKsB59jtnx2q1ydH4CazTWfJo9iKvTyeYEoYYQ6RT6A1DfoSj1UiwssKfdjUNumu2K', Decimal('0.11')),
        ('BcVT4P2r1Md1DftWBDKHdK38Md6NtFPu4Heof8atNpxx7zbKfhMtRmUUMooU4cJuH4EKXrpke5A77XVbPhekWuiCSTaDFjw', Decimal('1.22')),
        ('Bf2xXxMLdH9gyh35o6LEyKCz6ZsPRmcujBU9rFK81Brd8HmynFj16KFHAYCETU625hY2x7XBH7CvjCHAC6bxQfsjN77Jv7e', Decimal('2.33'))])

    In [26]: txs
    Out[26]: [2785a1ad7f6d794802ea27a00e679f8c9706be0ec0b78b73d3182c551c6d69d2]

    In [28]: wallet.outgoing(unconfirmed=True, confirmed=False)
    Out[28]: [out: 2785a1ad7f6d794802ea27a00e679f8c9706be0ec0b78b73d3182c551c6d69d2 @ pool 3.660000000000 id=0000000000000000]

    In [29]: txs[0].fee
    Out[29]: Decimal('0.006282400000')

The fee is something you might like to verify before sending the transaction to the network.
In such case you'd probably be interested in the chapter about :doc:`interaction with daemon
<daemon>`.

There are some additional options you may set when sending transfer, like payment ID, priority,
ring size or unlock time. See API reference below for details.

.. note:: Be aware that transactions sent from another instance of the same wallet will not appear
    in mempool queries. They will, of course, become visible once mined.

API reference
-------------

.. automodule:: monero.transaction
   :members:
