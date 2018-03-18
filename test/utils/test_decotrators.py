# -*- encoding: utf8 -*-
import unittest
from arky.utils.decorators import setInterval
from threading import Event


class TestUtilsDecorators(unittest.TestCase):

    def test_setInterval(self):
        @setInterval(30)
        def testfn():
            print("tick")

        event = testfn()
        assert event.is_set() is False
        assert isinstance(event, Event)
        event.set()
        assert event.is_set() is True


if __name__ == '__main__':
    unittest.main()
