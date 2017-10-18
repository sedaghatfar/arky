# -*- encoding: utf8 -*-
# © Toons

import unittest

from arky import rest
rest.use("dark")
from arky import util

class TestUtilDef(unittest.TestCase):

    def test_unlockAccount0(self):
        self.assertEqual(util.unlockAccount("D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk", "secret", "secondSecret"), True)

    def test_floatAmount0(self):
        balance = float(rest.GET.api.accounts.getBalance(address="D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk").get("balance", 0))
        self.assertEqual(util.floatAmount("100%", "D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk")*100000000+rest.cfg.fees["send"], balance)

if __name__ == '__main__':
    unittest.main()
