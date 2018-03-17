# -*- encoding: utf8 -*-
import os
import io
import unittest
from collections import OrderedDict
from mock import patch
from arky import rest, util


class TestUtilDef(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		rest.use("dark")

	def test_json(self):
		"""
		When calling `dumpJson` a file with a json dump should be created and we should be able to
		get its contents with `loadJson`. Our `popJson` fn should remove the file.
		"""
		data = {"testing": True}
		filename = "test.txt"
		util.dumpJson(data, filename)
		data = util.loadJson(filename)
		assert data["testing"] is True

		# test if file will be removed
		util.popJson(filename)
		assert not os.path.exists(filename)

	def test_prettyPrint(self):
		# we use OrderedDict to always guarantee the same order as a result so we can assert it
		data = OrderedDict()
		data["testing"] = True
		data["transactions"] = "many"
		with patch('sys.stdout', new=io.StringIO()) as stdout:
			util.prettyPrint(data, log=False)
		assert stdout.getvalue() == '\t     testing: True\n\ttransactions: many\n'

	def test_createBase(self):
		pins = [str('abc123'), b'abc123', u'abc123']
		for pin in pins:
			output = util.createBase(pin)
			assert output == 'e9a18c42b3d5f607'

	def test_scramble_and_unscramble(self):
		# set test data
		pin = "abc123"
		address = "DUGvQBxLzQqrNy68asPcU3stWQyzVq8G49".encode()
		scrambled_result = (
			b"\x06\x06\x0b\x0b\x06\x0f\x0f\r\x0b\x03\x06\x07\x0f\x04\x06\x05\x0f\x02\x0b\x03\x0f"
			b"\x03\x0f\x07\x06\x00\x0f\x01\t\r\t\x04\r\x03\x0f\t\x0b\x0e\r\t\x0b\x0b\t\t\x0f\t"
			b"\x0f\x06\x0b\x0f\x0b\x03\x0f\x01\x0f\x02\x0b\r\x0f\x03\t\x04\x06\x0f\t\x06\t\x01"
		)

		# run test
		base = util.createBase(pin)
		hexa = util.hexlify(address)
		scrambled = util.scramble(base, hexa)
		assert scrambled == scrambled_result

		unscrambled = util.unScramble(base, scrambled)
		assert hexa == unscrambled


	def test_dumpAccount_and_loadAccount(self):
		pin = "abc123"
		address = "DUGvQBxLzQqrNy68asPcU3stWQyzVq8G49".encode()
		privateKey = "123123123"
		base = util.createBase(pin)

		util.dumpAccount(base, address, privateKey)

		output = util.loadAccount(base)
		assert output["address"] == address
		assert output["privateKey"] == privateKey

	def test_findNetworks(self):
		networks = util.findNetworks()
		assert len(networks) == 11

	def test_shortAddress(self):
		output = util.shortAddress("DUGvQBxLzQqrNy68asPcU3stWQyzVq8G49")
		assert output == "DUGvQ...q8G49"


if __name__ == '__main__':
    unittest.main()
