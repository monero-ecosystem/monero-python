Interacting with daemon
=======================

The module offers an interface to interact with Monero daemon. For the time being, like with
wallet, the only available backend is JSON RPC.

.. code-block:: python

    In [1]: from monero.daemon import Daemon

    In [2]: from monero.backends.jsonrpc import JSONRPCDaemon

    In [3]: daemon = Daemon(JSONRPCDaemon(port=28081))

    In [4]: daemon.height()
    Out[4]: 1099108

Also, the ``info()`` method will return a dictionary with details about the current daemon status.

Sending prepared transactions
-----------------------------

The daemon connection may be used for two-step sending of transactions. For example, you may want
to check the fee before broadcasting the transaction to the network.

To prepare a transaction, use ``transfer()`` or ``transfer_multiple()`` method of the wallet or
account, as described in :ref:`the section about sending payments <sending-payments>`.
The only difference is that now you want to add the ``relay=False`` argument.

.. code-block:: python

    In [5]: from monero.wallet import Wallet

    In [6]: from monero.backends.jsonrpc import JSONRPCWallet

    In [7]: wallet = Wallet(JSONRPCWallet(port=28088))

    In [8]: wallet.balance()
    Out[8]: Decimal('17.642325205670')

    In [9]: txs = wallet.transfer('Bg1nUjsEx6UUByxr68o6gXcQRF58BpQyKauoZSo2HwubGErEnz9x6AS9o5ybmk3QmgeUpX3Msgm74QkwZKx2CeVWFrrZZqt', 10, relay=False)

Now the return value is a list of resulting transactions (usually just one) which may be inspected
and validated.

.. code-block:: python

    In [10]: txs
    Out[10]: [38964a0c8c3be041051464b413996ad8d696223dc34925d98156848ed76a3ae3]

    In [11]: txs[0].fee
    Out[11]: Decimal('0.003766080000')

If anything is not OK, just discard the transaction and create a new one. There's no need to clean
up anything in the wallet.

Once you have the transaction accepted, it's time to post it to the daemon:

.. code-block:: python

    In [12]: result = daemon.send_transaction(txs[0])

    In [13]: result
    Out[13]: 
    {'double_spend': False,
     'fee_too_low': False,
     'invalid_input': False,
     'invalid_output': False,
     'low_mixin': False,
     'not_rct': False,
     'not_relayed': False,
     'overspend': False,
     'reason': '',
     'status': 'OK',
     'too_big': False}

No batching due to double spends
--------------------------------

.. warning:: The workflow described above should not be used for preparing a batch of transactions
    to be sent later. The wallet doesn't remember which inputs have been spent and will very likely
    use the same in the next transaction, resulting in a double spend and broadcast failure.

The following example shows such behavior:

.. code-block:: python

    In [14]: txs1 = wallet.transfer('BYSXsmmK44xdjNVMGprUW5Yau9tsc9SAMJrQsANjGgpk2RB83cvVhWjZAgYNwLgmhdPawATh5q1CTEoLGKZSeZqtThefV7D', 1, relay=False)

    In [15]: txs2 = wallet.transfer('Bd5m5wTjWdYSaLBKe4i2avJjuFLYMEUKpiiE86F83NFiDXKE7QseSRvS7efTtJu5xHiHm5XmxgB2mfLu7NFrG7e3UTYRzEf', 2, relay=False)

    In [16]: txs1, txs2
    Out[16]: 
    ([315901f250a1018e89e1fc2b3953bd5acfdfa759f843cf5a38306a2255de6d54],
     [2bd978172226b486badc8a9dcbafb04acb4760c3f2a5794c694fee8575739c6e])

    In [17]: daemon.send_transaction(txs1[0])
    Out[17]: 
    {'double_spend': False,
     'fee_too_low': False,
     'invalid_input': False,
     'invalid_output': False,
     'low_mixin': False,
     'not_rct': False,
     'not_relayed': False,
     'overspend': False,
     'reason': '',
     'status': 'OK',
     'too_big': False}

    In [18]: daemon.send_transaction(txs2[0])
    ---------------------------------------------------------------------------
    TransactionBroadcastError                 Traceback (most recent call last)
    <ipython-input-22-f24dc5d51c78> in <module>()
    ----> 1 daemon.send_transaction(txs2[0])

    ~/devel/monero-python/monero/daemon.py in send_transaction(self, tx, relay)
         10 
         11     def send_transaction(self, tx, relay=True):
    ---> 12         return self._backend.send_transaction(tx.blob, relay=relay)
         13 
         14     def mempool(self):

    ~/devel/monero-python/monero/backends/jsonrpc.py in send_transaction(self, blob, relay)
         36         raise exceptions.TransactionBroadcastError(
         37                 "{status}: {reason}".format(**res),
    ---> 38                 details=res)
         39 
         40     def mempool(self):

    TransactionBroadcastError: Failed: double spend

The second transaction failed because it used the same inputs as the previous one. The daemon
checks all incoming transactions for possible double-spends and rejects them if such conflict
is discovered.

API reference
-------------

.. automodule:: monero.daemon
   :members:
