# -*- encoding: utf8 -*-
# © Toons

import unittest
import arky.rest

class TestArkCrypto(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		arky.rest.use("dark")

	def test_get_address(self):
		keys = arky.core.crypto.getKeys("secret")
		address = arky.core.crypto.getAddress(keys["publicKey"])
		self.assertEqual(address, "D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk")

	def test_signature(self):
		keys = arky.core.crypto.getKeys("secret")
		message = "test message".encode("utf-8")
		signature = arky.core.crypto.getSignatureFromBytes(message, keys["privateKey"])
		self.assertEqual(
			True,
			arky.core.crypto.verifySignatureFromBytes(message, keys["publicKey"], signature)
		)


class TestLskCrypto(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		arky.rest.use("lisk")

	def test_get_keys(self):
		keys = arky.core.crypto.getKeys("secret")
		self.assertEqual(
			keys["publicKey"],
			"5d036a858ce89f844491762eb89e2bfbd50a4a0a0da658e4b2628b25b117ae09"
		)

	def test_get_address(self):
		keys = arky.core.crypto.getKeys("secret")
		address = arky.core.crypto.getAddress(keys["publicKey"])
		self.assertEqual(address, "18160565574430594874L")


if __name__ == '__main__':
	unittest.main()
