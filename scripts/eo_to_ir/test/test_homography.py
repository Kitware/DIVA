#!/usr/bin/env python3

import unittest
import os
import sys

import numpy as np
from numpy.testing import assert_array_equal

lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../lib")
sys.path.append(lib_path)

from homography import apply_homography  # noqa


class TestHomography(unittest.TestCase):
    def setUp(self):
        super(TestHomography, self).setUp()

        self.homography_i = np.array([[1.0, 0.0, 0.0],
                                      [0.0, 1.0, 0.0],
                                      [0.0, 0.0, 1.0]])

        self.homography_i2 = np.array([[2.0, 0.0, 0.0],
                                       [0.0, 2.0, 0.0],
                                       [0.0, 0.0, 2.0]])

        self.homography_1 = np.array([[2.0, 0.0, 0.0],
                                      [0.0, 2.0, 0.0],
                                      [0.0, 0.0, 1.0]])

        self.homography_2 = np.array([[1.0, 0.0, 3.0],
                                      [0.0, 1.0, 4.0],
                                      [0.0, 0.0, 1.0]])

        self.bounds_1 = (10.0, 10.0, 20.0, 20.0)

        self.result_bounds_1 = (20.0, 20.0, 40.0, 40.0)
        self.result_bounds_2 = (13.0, 14.0, 23.0, 24.0)

    def test_apply_homography(self):
        assert_array_equal(
            apply_homography(self.homography_i,
                             self.bounds_1),
            self.bounds_1)

        assert_array_equal(
            apply_homography(self.homography_i2,
                             self.bounds_1),
            self.bounds_1)

        assert_array_equal(
            apply_homography(self.homography_1,
                             self.bounds_1),
            self.result_bounds_1)

        assert_array_equal(
            apply_homography(self.homography_2,
                             self.bounds_1),
            self.result_bounds_2)


if __name__ == '__main__':
    unittest.main()
