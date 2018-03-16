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

	def test_unlockAcount(self):
		# function doesn't exist so we can't test it
		pass

	def test_floatAmount(self):
		# can' test because `floatAmount` function still seems to be WIP
		pass

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

if __name__ == '__main__':
    unittest.main()
