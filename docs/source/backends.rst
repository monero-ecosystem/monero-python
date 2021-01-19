Backends
========

The module comes with possibility of replacing the underlying backend. Backends are the protocols
and methods used to communicate with the Monero daemon or wallet. As of the time of this writing,
the module offers the following options:

 * ``jsonrpc`` for the HTTP based RPC server,
 * ``offline`` for running the wallet without Internet connection and even without the wallet file.

JSON RPC
----------------

This backend requires a running ``monero-wallet-rpc`` process with a Monero wallet file opened.
This can be on your local system or a remote node, depending on where the wallet file lives and
where the daemon is running. Refer to the quickstart for general setup information.

The Python `requests`_ library is used in order to facilitate HTTP requests to the JSON RPC
interface. It makes POST requests and passes proper headers, parameters, and payload data as per
the official `Wallet RPC`_ documentation.

Also, ``jsonrpc`` backend is the default choice and both ``Wallet`` and ``Daemon`` classes
can be invoked in a simple form with no ``backend`` argument given. They will assume connection to
the default *mainnet* port on *localhost*, like below:

.. code-block:: python

    In [1]: wallet = Wallet()   # is equivalent to: wallet = Wallet(JSONRPCWallet(host='localhost', port=18081)

.. _`requests`: http://docs.python-requests.org/

.. _`Wallet RPC`: https://getmonero.org/resources/developer-guides/wallet-rpc.html

.. automodule:: monero.backends.jsonrpc
   :members:

Offline
----------------

This backend allows creating a `Wallet` instance without network connection or even without the
wallet itself. In version 0.5 the only practical use is to cold-generate
:doc:`subaddresses <address>` like in the example below:

.. code-block:: python

   In [8]: w = Wallet(OfflineWallet('47ewoP19TN7JEEnFKUJHAYhGxkeTRH82sf36giEp9AcNfDBfkAtRLX7A6rZz18bbNHPNV7ex6WYbMN3aKisFRJZ8Ebsmgef', view_key='6d9056aa2c096bfcd2f272759555e5764ba204dd362604a983fa3e0aafd35901'))

   In [9]: w.get_address(100,37847)
   Out[9]: 883Gcsq65iqh4UL3fJTWLxY45skXyFVNQJZ4bdw4TJcqd8vafvtpX4p6HNmawqFMQ6TwJP7adzyLT1fbU6z1n9dqB9bJrfn

.. automodule:: monero.backends.offline
   :members:
