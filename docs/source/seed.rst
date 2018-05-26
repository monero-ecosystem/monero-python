Mnemonic seeds
==============

You can utilize the ``Seed`` class in order to generate or supply a 25 word mnemonic seed. From this mnemonic seed you can derive public and private spend keys, public and private view keys, and public wallet address. Read more about mnemonic seeds `here`_.

The class also reads 12 or 13 word seeds, also known as *MyMonero style*.

.. _here: https://getmonero.org/resources/moneropedia/mnemonicseed.html

.. warning:: This class deals with highly sensitive strings in both inputs and outputs.
            The mnemonic seed and it's hexadecimal representation are essentially full
            access keys to your Monero funds and should be handled with the utmost care.


Generating a new seed
-----------------------

By default, constructing the ``Seed`` class without any parameters will generate a new 25 word mnemonic seed from a 32 byte hexadecimal string using ``os.urandom(32)``. Class construction sets the attributes ``phrase`` and ``hex`` - the 25 word mnemonic seed and it's hexadecimal representation.


.. code-block:: python

    In  [1]: from monero.seed import Seed

    In  [2]: s = Seed()

    In  [3]: s.phrase
    Out [3]: 'fewest lipstick auburn cocoa macro circle hurried impel macro hatchet jeopardy swung aloof spiders gags jaws abducts buying alpine athlete junk patio academy loudly academy'

    In  [4]: s.hex
    Out [4]: u'73192a945d7400a3a76a941be451a9623f37dd834006d02140a6a762b9142d80'


Supplying your own seed
------------------------

If you have an existing mnemonic word or hexadecimal seed that you would like to derive keys for, simply pass the seed as a string to the ``Seed`` class. Class construction will automatically detect the seed type and encode or decode to set both ``phrase`` and ``hex`` attributes.

.. code-block:: python

    In  [1]: from monero.seed import Seed

    In  [2]: s = Seed("73192a945d7400a3a76a941be451a9623f37dd834006d02140a6a762b9142d80")

    In  [3]: s.phrase
    Out [3]: 'fewest lipstick auburn cocoa macro circle hurried impel macro hatchet jeopardy swung aloof spiders gags jaws abducts buying alpine athlete junk patio academy loudly academy'

    In  [4]: s.hex
    Out [4]: u'73192a945d7400a3a76a941be451a9623f37dd834006d02140a6a762b9142d80'


    In  [5]: p = Seed("fewest lipstick auburn cocoa macro circle hurried impel macro hatchet jeopardy swung aloof spiders gags jaws abducts buying alpine athlete junk patio academy loudly academy")

    In  [6]: p.phrase
    Out [6]: 'fewest lipstick auburn cocoa macro circle hurried impel macro hatchet jeopardy swung aloof spiders gags jaws abducts buying alpine athlete junk patio academy loudly academy'

    In  [7]: p.hex
    Out [7]: u'73192a945d7400a3a76a941be451a9623f37dd834006d02140a6a762b9142d80'


Deriving account keys
----------------------

Once the ``Seed`` class is constructed, you can derive `all of the keys`_ associated with the account.

.. _all of the keys: https://getmonero.org/resources/moneropedia/account.html

.. code-block:: python

    In  [1]: from monero.seed import Seed

    In  [2]: s = Seed("fewest lipstick auburn cocoa macro circle hurried impel macro hatchet jeopardy swung aloof spiders gags jaws abducts buying alpine athlete junk patio academy loudly academy")

    In  [3]: s.secret_spend_key()
    Out [3]: '0b7a7bac8a5b6de2f483d703ef82b1bb3e37dd834006d02140a6a762b9142d00'

    In  [4]: s.secret_view_key()
    Out [4]: '75ec665f4912cec813ff7f20bc75b1f375ee2f8d4bb7631ae8d1af302732a609'

    In  [5]: s.public_spend_key()
    Out [5]: 'd5db200426637399f0076090dea01394afc2b157f94d287516911dbbcf8b2275'

    In  [6]: s.public_view_key()
    Out [6]: 'cd235f236224b8a5f1e12568927e01a2879bfd49cec2517b0717adb97fe8ae39'

    In  [7]: s.public_address()
    Out [7]: '49j9ikUyGfkSkPV8TY66p2RsSs6xL7NR5LauJTt7y6LZLhpakUnjcddUksdDgccVPEUBk2obnM1YUMaXKsGsCnow7WYjktm'




API reference
-------------

.. automodule:: monero.seed
   :members:
