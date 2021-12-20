Python Monero module
====================

|travis|_ |coveralls|_


.. |travis| image:: https://travis-ci.org/monero-ecosystem/monero-python.svg
.. _travis: https://travis-ci.org/monero-ecosystem/monero-python


.. |coveralls| image:: https://coveralls.io/repos/github/monero-ecosystem/monero-python/badge.svg
.. _coveralls: https://coveralls.io/github/monero-ecosystem/monero-python


A comprehensive Python module for handling Monero cryptocurrency.

* release 0.99
* open source: https://github.com/monero-ecosystem/monero-python
* works with Monero 0.13.x and `the latest source`_ (at least we try to keep up)
* Python 2.x and 3.x compatible
* available on PyPi: https://pypi.org/project/monero/
* comes with `documentation`_
* generously funded by `Monero FFS`_ donors

.. warning:: With release 0.6 the project name at PyPi has changed from `monero-python` to `monero`.
    Please update your dependency files.

.. _`the latest source`: https://github.com/monero-project/monero
.. _`documentation`: http://monero-python.readthedocs.io/en/latest/
.. _`Monero FFS`: https://forum.getmonero.org/9/work-in-progress

Copyrights
----------

Released under the BSD 3-Clause License. See `LICENSE.txt`_.

Copyright (c) 2017-2018 Michał Sałaban <michal@salaban.info> and Contributors:
`lalanza808`_, `cryptochangements34`_, `atward`_, `rooterkyberian`_, `brucexiu`_,
`lialsoftlab`_, `moneroexamples`_, `massanchik`_, `MrClottom`_, `jeffro256`_,
`sometato`_.

Copyright (c) 2016 The MoneroPy Developers (``monero/base58.py`` taken from `MoneroPy`_)

Copyright (c) 2011 thomasv@gitorious (``monero/seed.py`` based on `Electrum`_)

.. _`LICENSE.txt`: LICENSE.txt
.. _`MoneroPy`: https://github.com/bigreddmachine/MoneroPy
.. _`Electrum`: https://github.com/spesmilo/electrum

.. _`lalanza808`: https://github.com/lalanza808
.. _`cryptochangements34`: https://github.com/cryptochangements34
.. _`atward`: https://github.com/atward
.. _`rooterkyberian`: https://github.com/rooterkyberian
.. _`brucexiu`: https://github.com/brucexiu
.. _`lialsoftlab`: https://github.com/lialsoftlab
.. _`moneroexamples`: https://github.com/moneroexamples
.. _`massanchik`: https://github.com/massanchik
.. _`MrClottom`: https://github.com/MrClottom
.. _`jeffro256`: https://github.com/jeffro256
.. _`sometato`: https://github.com/sometato

Want to help?
-------------

If you find this project useful, please consider a donation to the following address:
``481SgRxo8hwBCY4z6r88JrN5X8JFCJYuJUDuJXGybTwaVKyoJPKoGj3hQRAEGgQTdmV1xH1URdnHkJv6He5WkEbq6iKhr94``


Development
-----------

1. Clone the repo
2. Create virtualenv & activate it

.. code-block:: bash

    python3 -m venv .venv
    source .venv/bin/activate

3. Install dependencies

.. code-block:: bash

    .venv/bin/pip install -r requirements.txt -r test_requirements.txt

4. Do your thing

5. Run tests

.. code-block:: bash

    .venv/bin/pytest

6. Format your code with black

.. code-block:: bash

    .venv/bin/black .
