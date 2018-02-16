Backends
========

Backends are the protocols and methods used to communicate with the Monero daemon and interact with
the wallet. As of the time of this writing, the only backend available in this library is for the
HTTP based RPC server.

JSON RPC
----------------

This backend requires a running ``monero-wallet-rpc`` process with a Monero wallet file opened.
This can be on your local system or a remote node, depending on where the wallet file lives and
where the daemon is running. Refer to the quickstart for general setup information.

The Python `requests`_ library is used in order to facilitate HTTP requests to the JSON RPC
interface. It makes POST requests and passes proper headers, parameters, and payload data as per
the official `Wallet RPC`_ documentation.

.. _`requests`: http://docs.python-requests.org/

.. _`Wallet RPC`: https://getmonero.org/resources/developer-guides/wallet-rpc.html


API reference
-------------

.. automodule:: monero.backends.jsonrpc
   :members:
