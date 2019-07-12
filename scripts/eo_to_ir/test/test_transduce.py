#!/usr/bin/env python3

import unittest
import os
import sys
from functools import reduce

lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../lib")
sys.path.append(lib_path)

from transduce import (xd_map,
                       xd_filter,
                       appender,
                       xd)  # noqa


class TestTransduce(unittest.TestCase):
    def setUp(self):
        super(TestTransduce, self).setUp()

        id_ = xd_map(lambda x: x)
        plus1 = xd_map(lambda x: x + 1)
        sqr = xd_map(lambda x: x ** 2)
        ne3 = xd_filter(lambda x: x != 3)

        self.inputs = [1, 2, 3, 4, 5]

        self.pipelines = {}

        self.pipelines[0] = xd(id_)

        self.pipelines[1] = xd(sqr,
                               plus1,
                               ne3)

        self.pipelines[2] = xd(ne3,
                               plus1)

        self.pipelines[3] = xd(self.pipelines[2],
                               self.pipelines[1])

        self.expecteds = {}

        self.expecteds[0] = self.inputs

        self.expecteds[1] = [2, 5, 10, 17, 26]

        self.expecteds[2] = [2, 3, 5, 6]

        self.expecteds[3] = [5, 10, 26, 37]

    def test_transduce(self):
        for i in range(0, 4):
            with self.subTest(i=i):
                self.assertCountEqual(
                    reduce(self.pipelines[i](appender), self.inputs, []),
                    self.expecteds[i])


if __name__ == '__main__':
    unittest.main()
