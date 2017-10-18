.. image:: https://github.com/Moustikitos/arky/raw/master/arky-logo.png
   :target: https://ark.io

Copyright 2016-2017 **Toons**, Copyright 2017 **ARK**, `MIT licence`_

Install
=======

Ubuntu / OSX
^^^^^^^^^^^^

From development version

``sudo -H pip install https://github.com/ArkEcosystem/arky/archive/aip11.zip``

If you work with ``python3``

``sudo -H pip3 install https://github.com/ArkEcosystem/arky/archive/aip11.zip``

Windows 
^^^^^^^

From development version

``pip install https://github.com/ArkEcosystem/arky/archive/aip11.zip``

REST API
========

``rest`` module allows developpers to send requests to the blockchain.

>>> from arky import rest
>>> rest.use("ark")

It loads the ``ark.net`` file and create associated REST API endpoinds.
All endpoinds can be reached using this syntax :

``rest.[METHOD].[endpoinds with "/" replaced by "."](param=value, ...[returnKey=name])``

>>> # http equivalent [PEER ADDRESS]/api/delegates/get?username=arky
>>> rest.GET.api.delegates.get(username="arky")
{'delegate': {'productivity': 99.22, 'producedblocks': 42283, 'approval': 1.06, 
'rate': 19, 'publicKey': '030da05984d579395ce276c0dd6ca0a60140a3c3d964423a04e7ab
e110d60a15e9', 'username': 'arky', 'vote': '137484978342696', 'address': 'ARfDVW
Z7Zwkox3ZXtMQQY1HYSANMB88vWE', 'missedblocks': 334}, 'success': True}

It returns a python dictionary transposed from server json response. You can
provide a ``returnKey`` option value to get the field you want from server response :

>>> rest.use("oxy")
>>> rest.GET.api.delegates.get(username="toons", returnKey="delegate")
{'rate': 20, 'producedblocks': 1354, 'approval': 14.36, 'username': 'toons', 'ra
nk': 20, 'publicKey': 'c0f4e7fb7555fd19de2b6a9de92f02b44cef56c782ca0f6983607b7f4
e508ef9', 'productivity': 99.63, 'missedblocks': 5, 'vote': '1476176009882003', 
'address': '15981732227677853647X'}

Blockchain ``core``
===================

``rest.use`` loads a blockchain package find in  ``*.net`` file as ``arky.core``.
Blockchain package define the current interface :

* ``arky.core.crypto.getKeys(secret)``
* ``arky.core.crypto.getAddress(publicKey)``
* ``arky.core.crypto.getSignature(tx, privateKey)``
* ``arky.core.crypto.getId(tx)``
* ``arky.core.crypto.getBytes(tx)``
* ``arky.core.sendToken(amount, recipientId, vendorField, secret, secondSecret=None)``
* ``arky.core.registerSecondPublicKey(secondPublicKey, secret, secondSecret=None)``
* ``arky.core.registerSecondPassphrase(secondPassphrase, secret, secondSecret=None)``
* ``arky.core.registerDelegate(username, secret, secondSecret=None)``
* ``arky.core.upVoteDelegate(usernames, secret, secondSecret=None)``
* ``arky.core.downVoteDelegate(usernames, secret, secondSecret=None)``

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

**1.0 - AIP11**


.. _MIT licence: http://htmlpreview.github.com/?https://github.com/Moustikitos/arky/blob/master/arky.html
.. _toonsbuf protocol: https://github.com/Moustikitos/AIPs/blob/master/AIPS/aip-8.md
