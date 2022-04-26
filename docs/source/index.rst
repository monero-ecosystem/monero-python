.. image:: https://getmonero.org/press-kit/logos/monero-logo-symbol-on-white-480.png

Python module for Monero
========================

.. warning:: **URGENT SECURITY UPDATE**
   The version 1.0.2 contains an urgent security update in the output recognition code. If you're
   using the module for scanning transactions and identifying outputs using the secret view key,
   UPDATE THE SOFTWARE IMMEDIATELY.
   Otherwise you're safe. Standard wallet operations like receiving payments, spending, address
   generation etc. are NOT AFFECTED.

Welcome to the documentation for the ``monero`` Python module.

The aim of this project is to offer a set of tools for interacting with Monero
cryptocurrency in Python. It provides higher level classes representing objects
from the Monero environment, like wallets, accounts, addresses, transactions.

Currently it operates over JSON RPC protocol, however other backends are
planned as well.

Project homepage: https://github.com/monero-ecosystem/monero-python

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quickstart
   wallet
   address
   transactions
   daemon
   outputs
   backends
   seed
   misc
   exceptions
   release_notes
   license
   authors

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
