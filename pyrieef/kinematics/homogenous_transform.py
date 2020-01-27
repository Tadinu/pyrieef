#!/usr/bin/env python

# Copyright (c) 2018, University of Stuttgart
# All rights reserved.
#
# Permission to use, copy, modify, and distribute this software for any purpose
# with or without   fee is hereby granted, provided   that the above  copyright
# notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS  SOFTWARE INCLUDING ALL  IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR  BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR  ANY DAMAGES WHATSOEVER RESULTING  FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION,   ARISING OUT OF OR IN    CONNECTION WITH THE USE   OR
# PERFORMANCE OF THIS SOFTWARE.
#
#                                        Jim Mainprice on Sunday June 13 2018

from geometry.differentiable_geometry import *
from geometry.rotations import *


class HomogenousTransform(DifferentiableMap):
    """ HomeogenousTransform as DifferentiableMap """

    def __init__(self, p0=np.zeros(2)):
        self._n = 3
        self._p0 = p0
        assert self._p0.size == self._n - 1

    def output_dimension(self):
        return self._n - 1

    def input_dimension(self):
        return self._n

    def forward(self, q):
        T = np.eye(self.input_dimension())
        p = np.ones(self.input_dimension())
        dim = self.output_dimension()
        p[:dim] = self._p0
        T[:dim, :dim] = rotation_matrix_2d_radian(q[dim])
        T[:dim, dim] = q[:dim]
        return np.dot(T, p)[:dim]

    def jacobian(self, q):
        """ Should return a matrix or single value of
                m x n : ouput x input (dimensions)
            by default the method returns the finite difference jacobian.
            WARNING the object returned by this function is a numpy matrix."""

