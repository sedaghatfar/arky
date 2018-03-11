# -*- encoding: utf8 -*-
import unittest
import mock
from importlib import import_module
from parameterized import parameterized
from arky.cli import CLI
from arky.exceptions import ParserException


class TestCLI(unittest.TestCase):

    @parameterized.expand([
        (["network"], (True, False)),
        (["account"], (True, False)),
        (["delegate"], (True, False)),
        (["ledger"], (True, False)),
    ])
    def test_parse(self, command, expected):
        cli = CLI()
        result = cli.parse(command)
        assert result == expected
        assert cli.module == import_module("arky.cli.{0}".format(command[0]))

    def test_parse_network(self):
        cli = CLI()
        cmd, arg = cli.parse(["network", "use", "dark"])
        assert cmd.__module__ == "arky.cli.network"
        assert cmd.__name__ == "use"
        assert arg["<name>"] == "dark"

    def test_parse_ledger_wrong_network(self):
        cli = CLI()
        result = cli.parse(["ledger"])
        assert result == (True, False)
        assert cli.module == import_module("arky.cli.ledger")
        with self.assertRaises(ParserException):
            cli.prompt
            assert cli.module == import_module("arky.cli")

    def test_parse_ledger_good_network(self):
        cli = CLI()
        cli.parse(["network", "use", "ark"])
        cmd, arg = cli.parse(["ledger", "link"])
        assert cmd.__name__ == "link"
        assert cli.module == import_module("arky.cli.ledger")

    @parameterized.expand(["..", "exit"])
    def test_parse_back(self, command):
        cli = CLI()
        cli.parse(["network"])
        assert cli.module == import_module("arky.cli.network")
        result = cli.parse([command])
        assert result == (True, False)
        assert cli.module == import_module("arky.cli")

    @parameterized.expand(["help", "?"])
    def test_parse_help(self, command):
        cli = CLI()
        with mock.patch('arky.cli.sys') as sysmock:
            result = cli.parse([command])
            assert sysmock.stdout.write.call_count == 1
        assert result == (True, False)

    @parameterized.expand(["exit", "EXIT"])
    def test_parse_exit(self, command):
        cli = CLI()
        result = cli.parse([command])
        assert result == (False, False)

if __name__ == '__main__':
    unittest.main()
