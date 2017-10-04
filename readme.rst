.. image:: https://github.com/Moustikitos/arky/raw/master/arky-logo.png
   :target: https://ark.io

Copyright 2016-2017 **Toons**, Copyright 2017 **ARK**, `MIT licence`_

Install
=======

Ubuntu / OSX
^^^^^^^^^^^^

Open a terminal and type :

``sudo pip install arky``

If you work with ``python3``

``sudo pip3 install arky``

From development version

``sudo -H pip install git+https://github.com/ArkEcosystem/arky.git``

If you work with ``python3``

``sudo -H pip3 install git+https://github.com/ArkEcosystem/arky.git``

Windows 
^^^^^^^

Run a command as Administrator and type :

``pip install arky``

For development version

``pip install git+https://github.com/ArkEcosystem/arky.git``

Authors
=======

Toons <moustikitos@gmail.com>

Support this project
====================

.. image:: https://github.com/ArkEcosystem/arky/raw/master/ark-logo.png
   :height: 30

Toons Ark address: ``AUahWfkfr5J4tYakugRbfow7RWVTK35GPW``

.. image:: http://bruno.thoorens.free.fr/img/bitcoin.png
   :width: 100

Toons Bitcoin address: ``3Jgib9SQiDLYML7QKBYtJUkHq2nyG6Z63D``

**Show gratitude on Gratipay:**

.. image:: http://img.shields.io/gratipay/user/b_py.svg?style=flat-square
   :target: https://gratipay.com/~b_py

**Vote for Toons' delegate arky**

Version
=======

**1.0 ``AIP11``**

**0.3**

+ ``stick-arky`` released : bring all arky every where on your usb stick
+ ``kapu`` mainnet added
+ ``cli`` pkg:
   * arky-cli can now execute script
   * code tweak
   * ``input`` instead of ``getpass`` for secondsecret (encoding issue)
   * ``delegate`` module improvement
   * added ``network staking`` and ``network update`` command
+ ``ui`` pkg added: this is arky lite wallet
+ ``util`` pkg: ``coinmarketcap`` api update
+ ``api`` pkg: 
   * ``get`` method use different seed on each call
   * Fees values loaded from blockchain
   * Default timeout changed to 10s

**0.2.3**

+ ``core`` mod : 
   * `toonsbuf protocol`_ implemented
   * osx compatibility issue fix
+ ``cli`` can now execute arky scripts

**0.2.2**

+ pypi wheel universall fix
+ wiki updated
+ ``cli`` pkg:
   * added ``network wif`` command
   * added ``network browse`` command
   * fixed ``vote -d <delegate>`` behaviour
   * minor bugfixes and improvements
+ ``util.stats`` mod:
   * ``getHistory`` fix
   * added ``plot2D``
   * added ``getBalanceHistory``
   * added ``getVoteHistory``
+ ``api`` pkg:
   * improvement for ``postData`` and ``broadcastSerial``
   * added autoconf feature

**0.2.1**

+ ``cli`` pkg:
   * added network command set
   * added delegate command set
   * added account command set
+ ``api`` pkg:
   * only up-to-date peers selected for broadcasting

**0.2.0**

+ custom network configuration file added (``ark.net`` and ``dark.net`` available)
+ added ``cli`` pkg:
   * ``escrow`` module availabel
+ ``util`` pkg:
   * added ``stats`` module

**0.1.9**

+ ``api`` pkg:
   * minor bugfixes
   * offline mode added
   * better connection protocol

**0.1.8**

+ relative import fix for ``python 2.x``
+ updated testnet and devnet seeds
+ ``api`` pkg:
   * ``api.get`` improvement
   * ``api.use`` improvement, can now connect to a custom seed
   * ``api.broadcast`` improvement
   * multiple transaction requests enabled
+ ``core`` mod:
   * removed ``sendTransaction`` (use ``api.sendTx`` instead)

**0.1.7**

+ ``api`` pkg:
   * documentation (docstring)
   * added ``api.send_tx`` and ``api.broadcast``
   * ``api.get`` code improvement
   * bugfix on requests header ``port`` field value 
+ ``core`` mod:
   * removed ``checkStrictDER`` calls in ``core.Transaction.sign``

**0.1.6**

+ ``api`` pkg : improve peer connection

**0.1.5**

+ ``wallet`` mod : code improvement
+ ``util`` pkg : https bug fix in frozen mode
+ ``api`` pkg : update

**0.1.4**

+ first mainnet release

.. _MIT licence: http://htmlpreview.github.com/?https://github.com/Moustikitos/arky/blob/master/arky.html
.. _ARK API: https://github.com/ArkEcosystem/ark-api
.. _escrow command set: https://github.com/ArkEcosystem/arky/blob/master/wiki/escrow.md
.. _network command set: https://github.com/ArkEcosystem/arky/blob/master/wiki/network.md
.. _delegate command set: https://github.com/ArkEcosystem/arky/blob/master/wiki/delegate.md
.. _account command set: https://github.com/ArkEcosystem/arky/blob/master/wiki/account.md
.. _toonsbuf protocol: https://github.com/Moustikitos/AIPs/blob/master/AIPS/aip-8.md
