# -*- encoding: utf8 -*-
# © Toons

import unittest
import arky.rest

class TestArkCrypto(unittest.TestCase):

    def __init__(self, *args, **kw):
        unittest.TestCase.__init__(self, *args, **kw)
        arky.rest.use("dark")

    def test_getKeys(self):
        self.assertEqual(arky.core.crypto.getKeys("secret")["publicKey"], "03a02b9d5fdd1307c2ee4652ba54d492d1fd11a7d1bb3f3a44c4a05e79f19de933")

    def test_getAddress(self):
        self.assertEqual(arky.core.crypto.getAddress(arky.core.crypto.getKeys("secret")["publicKey"]), "D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk")


class TestLskCrypto(unittest.TestCase):

    def __init__(self, *args, **kw):
        unittest.TestCase.__init__(self, *args, **kw)
        arky.rest.use("lisk")

    def test_getKeys(self):
        self.assertEqual(arky.core.crypto.getKeys("secret")["publicKey"], "5d036a858ce89f844491762eb89e2bfbd50a4a0a0da658e4b2628b25b117ae09")

    def test_getAddress(self):
        self.assertEqual(arky.core.crypto.getAddress(arky.core.crypto.getKeys("secret")["publicKey"]), "18160565574430594874L")

if __name__ == '__main__':
    unittest.main()
