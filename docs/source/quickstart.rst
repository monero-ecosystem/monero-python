Quick start
===========

This quick start tutorial will guide you through the first steps of connecting
to the Monero wallet. We assume you:

 * have basic knowledge of Monero concepts of the wallet and daemon,
 * know how to use CLI (*command line interface*),
 * have experience with Python.

Connect to testnet for your own safety
--------------------------------------

The testnet is another Monero network where worthless coins circulate and
where, as the name suggests, all tests are supposed to be run. It's also a
place for early deployment of future features of the currency itself. You may
read `a brief explanation at stackexchange`_.

.. warning:: **Please run all tests on testnet.** The code presented in these docs will
    perform the requested operations right away, without asking for confirmation.
    This is live code, not a wallet application that makes sure the user has not
    made a mistake. **Running on the live net, if you make a mistake, you may lose
    money.**

.. _a brief explanation at stackexchange: https://monero.stackexchange.com/questions/1591/what-is-the-monero-testnet-how-can-i-participate-in-it

Start the daemon and create a wallet
------------------------------------

In order to connect to the testnet network you need to start the daemon:

.. code-block:: shell

    $ monerod --testnet


If you haven't used testnet before, it will begin downloading the blockchain,
exactly like it does on the live network. In January 2018 the testnet
blockchain was slightly over 2 GiB. It may take some time to get it.

You may however create a wallet in the meantime:

.. code-block:: shell

    $ monero-wallet-cli --testnet --generate-new-wallet testwallet

For now you may leave the password empty (testnet coins are worthless).

Start the RPC server
--------------------

The RPC server is a small utility that will operate on the wallet, exposing
a JSON RPC interface. Start it by typing:

.. code-block:: shell

    $ monero-wallet-rpc --testnet --wallet-file testwallet --password "" --rpc-bind-port 28088 --disable-rpc-login

Now you're almost ready to start using Python.

Install Dependencies
---------------------

Before you can use the library, you first must download the Python library dependencies with ``pip``. It is recommended to use a `virtual environment`_ to isolate library versions. Assuming you have ``virtualenv`` installed to your system, set up a new env, activate it, and install the dependencies.

.. _`virtual environment`: https://averlytics.com/2017/08/06/virtual-environment-a-python-best-practice/

.. code-block:: shell

    $ virtualenv .venv
    $ source .venv/bin/activate
    $ pip install -r requirements.txt
    $ python

Now you can proceed.

Connect to the wallet
---------------------

.. code-block:: python

    In [1]: from monero.wallet import Wallet

    In [2]: from monero.backends.jsonrpc import JSONRPCWallet

    In [3]: w = Wallet(JSONRPCWallet(port=28088))

    In [4]: w.address()
    Out[4]: A2GmyHHJ9jtUhPiwoAbR2tXU9LJu2U6fJjcsv3rxgkVRWU6tEYcn6C1NBc7wqCv5V7NW3zeYuzKf6RGGgZTFTpVC4QxAiAX

    In [5]: w.balance()
    Out[5]: Decimal('0E-12')

Congratulations! You have connected to the wallet. You may now proceed to the
next part, which will tell you about :doc:`interaction with wallet and accounts <wallet>`.
