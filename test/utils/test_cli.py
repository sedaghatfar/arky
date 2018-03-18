# -*- encoding: utf8 -*-
import io
import unittest

from collections import OrderedDict
from mock import patch

from arky.utils.cli import prettyPrint, shortAddress


class TestUtilsCLI(unittest.TestCase):

    def test_prettyPrint(self):
        # we use OrderedDict to always guarantee the same order as a result so we can assert it
        data = OrderedDict()
        data["testing"] = True
        data["transactions"] = "many"
        with patch('sys.stdout', new=io.StringIO()) as stdout:
            prettyPrint(data, log=False)
        assert stdout.getvalue() == '\t     testing: True\n\ttransactions: many\n'

    def test_shortAddress(self):
        output = shortAddress("DUGvQBxLzQqrNy68asPcU3stWQyzVq8G49")
        assert output == "DUGvQ...q8G49"


if __name__ == '__main__':
    unittest.main()
