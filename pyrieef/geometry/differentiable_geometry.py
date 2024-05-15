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

import numpy as np
import copy
from abc import abstractmethod


class DifferentiableMap:

    @abstractmethod
    def output_dimension(self):
        raise NotImplementedError()

    @abstractmethod
    def input_dimension(self):
        raise NotImplementedError()

    def __call__(self, q):
        """ Method called when call object """
        return self.forward(q)

    @abstractmethod
    def forward(self, q):
        """ Should return an array or single value"""
        raise NotImplementedError()

    def gradient(self, q):
        """ Should return an array or single value
                n : input dimension
            Convienience function to get numpy gradients in the same shape
            as the input vector
            for addition and substraction, of course gradients are
            only availables if the output dimension is one."""
        assert self.output_dimension() == 1
        return np.array(self.jacobian(q)).reshape(self.input_dimension())

    def jacobian(self, q):
        """ Should return a matrix or single value of
                m x n : ouput x input (dimensions)
            by default the method returns the finite difference jacobian.
            WARNING the object returned by this function is a numpy matrix."""
        return finite_difference_jacobian(self, q)

    def hessian(self, q):
        """ Should return the hessian matrix
                n x n : input x input (dimensions)
            by default the method returns the finite difference hessian
            that relies on the jacobian function.
            This method would be a third order tensor
            in the case of multiple output, we exclude this case for now.
            WARNING the object returned by this function is a numpy matrix."""
        return finite_difference_hessian(self, q)

    def evaluate(self, q):
        """ Evaluates the map and jacobian simultaneously. The default
            implementation simply calls both forward and Getjacobian()
            separately but overriding this method can make the evaluation
            more efficient """
        x = self.forward(q)
        J = self.jacobian(q)
        return [x, J]


class Compose(DifferentiableMap):

    def __init__(self, f, g):
        """

            f round g : f(g(q))

            This function should be called pullback if we approxiate
            higher order (i.e., hessians) derivaties by pullback, here it's
            computing the true 1st order derivative of the composition.

            """
        # Make sure the composition makes sense
        assert g.output_dimension() == f.input_dimension()
        self._f = f
        self._g = g

    def output_dimension(self):
        return self._f.output_dimension()

    def input_dimension(self):
        return self._g.input_dimension()

    def forward(self, q):
        return self._f(self._g(q))

    def jacobian(self, q):
        """  d/dq f(g(q)), applies chain rule.

                * J_f(g(q)) J_g

         If J is the jacobian of a function f(x), J_f = d/dx f(x)
            then the jacobian of the "pullback" of f defined on the
            range space of a map g, f(g(q)) is
                    d/dq f(g(q)) = J_f(g(q)) J_g
            This method computes and
            returns this "pullback gradient" J_f (g(q)) J_g(q).
            WARNING: J_f is assumed to be a jacobian np.matrix object
        """
        [y, J] = self.evaluate(q)
        return J

    def hessian(self, q):
        """  d^2/dq^2 f(g(q)), applies chain rule.

                * J_g' H_f J_g + H_g J_f,

            so far only works if f and g are functions, not maps.
            https://en.wikipedia.org/wiki/Chain_rule (Higher derivatives)
            WARNING: J_f is assumed to be a jacobian np.matrix object
        """
        x = self._g(q)
        J_g = self._g.jacobian(q)
        H_g = self._g.hessian(q)
        J_f = self._f.jacobian(x)
        H_f = self._f.hessian(x)
        a_x = J_g.T * H_f * J_g
        b_x = J_f * np.ones(self.input_dimension()) * H_g
        return a_x + b_x

    def evaluate(self, q):
        """
            d/dq f(g(q)), applies chain rule.
        """
        x = self._g(q)
        [y, J_f] = self._f.evaluate(x)
        J = J_f * self._g.jacobian(q)
        return [y, J]


class Pullback(Compose):

    def __init__(self, f, g):
        """
            f round g (f pullback by g)
               with approximate hessian. True hessian when H_g = 0

            https://en.wikipedia.org/wiki/Pullback_(differential_geometry)
        """
        Compose.__init__(self, f, g)

    def hessian(self, q):
        """
            d^2/dq^2 f(g(q)), applies chain rule.

                * J_g' H_f J_g + H_g J_f,

            here we dropout the higher order term of g
            this cooresponds to the full hessian when H_g = 0
            WARNING: f still has to be a function for now.
        """
        x = self._g(q)
        J_g = self._g.jacobian(q)
        H_f = self._f.hessian(x)
        # print("H_f :", H_f.shape)
        # print("J_g :", J_g.shape)
        return J_g.T * H_f * J_g


class Scale(DifferentiableMap):
    """ Scales a function by a constant """

    def __init__(self, f, alpha):
        self._f = f
        self._alpha = alpha

    def output_dimension(self):
        return self._f.output_dimension()

    def input_dimension(self):
        return self._f.input_dimension()

    def forward(self, q):
        return self._alpha * self._f.forward(q)

    def jacobian(self, q):
        return self._alpha * self._f.jacobian(q)

    def hessian(self, q):
        return self._alpha * self._f.hessian(q)


class SumOfTerms(DifferentiableMap):
    """ Sums n differentiable maps """

    def __init__(self, functions):
        nb_functions = len(functions)
        assert nb_functions > 0
        self._functions = functions
        if nb_functions > 1:
            for f in self._functions:
                assert f.output_dimension() == self.output_dimension()
                assert f.input_dimension() == self.input_dimension()

    def output_dimension(self):
        return self._functions[0].output_dimension()

    def input_dimension(self):
        return self._functions[0].input_dimension()

    def forward(self, q):
        return sum(f(q) for f in self._functions)

    def jacobian(self, q):
        return sum(f.jacobian(q) for f in self._functions)

    def hessian(self, q):
        return sum(f.hessian(q) for f in self._functions)


class RangeSubspaceMap(DifferentiableMap):
    """ Takes only some outputs """

    def __init__(self, n, indices):
        """n is the input dimension, indices are the output"""
        self._dim = n
        self._indices = indices

    def output_dimension(self):
        return len(self._indices)

    def input_dimension(self):
        return self._dim

    def forward(self, q):
        return q[self._indices]

    def jacobian(self, q):
        return np.matrix(np.eye(self._dim))[self._indices, :]

    def hessian(self, q):
        assert self.output_dimension() == 1
        return np.matrix(np.zeros((self._dim, self._dim)))


class CombinedOutputMap(DifferentiableMap):
    """ creates a combination of the maps
        phi(x) = [phi1(x); phi2(x); ...; phiN(x)]
        TODO : Test
        """

    def __init__(self, maps):
        self._maps = maps
        self._output_dim = sum(m.output_dimension() for m in self._maps)

    def output_dimension(self):
        return self._output_dim

    def input_dimension(self):
        return self._maps[0].input_dimension()

    def forward(self, q):
        idx = 0
        phi = np.zeros(self._output_dim)
        for m in self._maps:
            v = m(q)
            phi[idx:m.output_dimension() + idx] = v
            idx += m.output_dimension()
        return phi

    def jacobian(self, q):
        idx = 0
        J_phi = np.zeros((self._output_dim, self.input_dimension()))
        for m in self._maps:
            J = m.jacobian(q)
            J_phi[idx:m.output_dimension() + idx, 0:m.input_dimension()] = J
            idx += m.output_dimension()
        return J_phi


class ProductFunction(DifferentiableMap):
    """Take the product of functions"""

    def __init__(self, g, h):
        """
        f(x) = g(x)h(x)
        n is the input dimension
        indices are the output
        """
        self._g = g
        self._h = h
        # print "self._g.input_dimension() : ", self._g.input_dimension()
        # print "self._h.input_dimension() : ", self._h.input_dimension()
        assert self._g.input_dimension() == self._h.input_dimension()
        assert self._g.output_dimension() == 1
        assert self._h.output_dimension() == 1

    def output_dimension(self):
        return 1

    def input_dimension(self):
        return self._g.input_dimension()

    def forward(self, x):
        v1 = self._g.forward(x)
        v2 = self._h.forward(x)
        return v1 * v2

    def jacobian(self, x):
        v1 = self._g.forward(x)
        v2 = self._h.forward(x)
        J1 = self._g.jacobian(x)
        J2 = self._h.jacobian(x)
        return v1 * J2 + v2 * J1

    def hessian(self, x):
        assert self.output_dimension() == 1
        v1 = self._g.forward(x)
        v2 = self._h.forward(x)

        H1 = self._g.hessian(x)
        H2 = self._h.hessian(x)

        g1 = self._g.gradient(x)
        g2 = self._h.gradient(x)

        return v1 * H2 + v2 * H1 + np.outer(g1, g2) + np.outer(g2, g1)


class AffineMap(DifferentiableMap):
    """Simple map of the form: f(x)=ax + b"""

    def __init__(self, a, b):
        self._a = np.matrix(a)  # Make sure that a is matrix
        self._b = np.matrix(b.reshape(b.size, 1))

    def output_dimension(self):
        return self._b.shape[0]

    def input_dimension(self):
        return self._a.shape[1]

    def a(self):
        return self._a

    def forward(self, x):
        x_tmp = x.reshape(self.input_dimension(), 1)
        y = self._a * x_tmp + self._b
        return np.array(y).reshape(self.output_dimension())

    def jacobian(self, x):
        return self._a

    def hessian(self, x):
        assert self.output_dimension() == 1
        return np.matrix(np.zeros((
            self.input_dimension(), self.input_dimension())))


class QuadricFunction(DifferentiableMap):
    """ Here we implement a quadric funciton of the form:
        f(x) = 1/2 x^T A x + bx + c """

    def __init__(self, a, b, c):
        assert a.shape[0] == a.shape[1]
        assert b.size == a.shape[1]
        self._a = np.matrix(a)
        self._b = np.matrix(b.reshape(b.size, 1))
        self._c = c
        self._symmetric = np.allclose(self._a, self._a.T, atol=1e-8)
        self._posdef = np.all(np.linalg.eigvals(self._a) > 0)

    def output_dimension(self):
        return 1

    def input_dimension(self):
        return self._b.size

    def forward(self, x):
        x_tmp = np.matrix(x.reshape(self._b.size, 1))
        v = np.ndarray.item(
            .5 * x_tmp.T * self._a * x_tmp + self._b.T * x_tmp + self._c)
        return v

    def jacobian(self, x):
        x_tmp = np.matrix(x.reshape(self._b.size, 1))
        return (self.hessian(x) * x_tmp + self._b).T

    def hessian(self, x):
        """ when the matrix is positive this can be simplified
            see matrix cookbook """
        if self._symmetric and self._posdef:
            return self._a.T
        else:
            return 0.5 * (self._a + self._a.T)


class ExpTestFunction(DifferentiableMap):
    """ Test function that can be evaluated on a grid """

    def output_dimension(self):
        return 1

    def input_dimension(self):
        return 2

    def forward(self, p):
        return np.exp(-(2 * p[0])**2 - (p[1] / 2)**2)


class PolynomeTestFunction(DifferentiableMap):
    """ Test function polynome """

    def output_dimension(self):
        return 1

    def input_dimension(self):
        return 2

    def forward(self, p):
        return (p[0] - 1)**2 + .5 * (p[1] - 3)**2 + 4

    def jacobian_x(self, p):
        return 2*(p[0]-1)

    def jacobian_y(self, p):
        return p[1]-3

    def jacobian(self, p):
        return np.matrix([2*(p[0]-1), p[1]-3])


class LinearTestFunction(DifferentiableMap):
    """ Test function linear function (easily testable on meshgrid) """

    def output_dimension(self):
        return 1

    def input_dimension(self):
        return 2

    def forward(self, p):
        return .25 * p[0] + .7 * p[1]

    def jacobian_x(self, p):
        return .25

    def jacobian_y(self, p):
        return .7

    def jacobian(self, p):
        return np.matrix([.25, .7])


class IdentityMap(DifferentiableMap):
    """Simple identity map : f(x)=x"""

    def __init__(self, n):
        self._dim = n

    def output_dimension(self):
        return self._dim

    def input_dimension(self):
        return self._dim

    def forward(self, q):
        return q

    def jacobian(self, q):
        return np.matrix(np.eye(self._dim))

    def hessian(self, x):
        assert self.output_dimension() == 1
        return np.matrix(np.zeros((self._dim, self._dim)))


class ZeroMap(DifferentiableMap):
    """Simple zero map : f(x)=0"""

    def __init__(self, m, n):
        self._n = n
        self._m = m

    def output_dimension(self):
        return self._m

    def input_dimension(self):
        return self._n

    def forward(self, q):
        return np.zeros(self._m)

    def jacobian(self, q):
        return np.matrix(np.zeros((self._m, self._n)))

    def hessian(self, x):
        assert self.output_dimension() == 1
        return np.matrix(np.zeros((self._n, self._n)))


class SquaredNorm(DifferentiableMap):
    """ Simple squared norm : f(x)= | x - x_0 | ^2 """

    def __init__(self, x_0):
        self.x_0 = x_0

    def output_dimension(self):
        return 1

    def input_dimension(self):
        return self.x_0.size

    def forward(self, x):
        delta_x = np.array(x).reshape(x.size) - self.x_0
        return 0.5 * np.dot(delta_x, delta_x)

    def jacobian(self, x):
        delta_x = x - self.x_0
        return np.matrix(delta_x)

    def hessian(self, x):
        assert self.output_dimension() == 1
        return np.matrix(np.eye(self.x_0.size, self.x_0.size))


class Norm(DifferentiableMap):
    """
        Simple norm f(x) = |x - x_0|
    """

    def __init__(self, x_0=None):
        self.x_0 = x_0
        self._n = 2 if x_0 is None else self.x_0.size

    def output_dimension(self):
        return 1

    def input_dimension(self):
        return self._n

    def _xd(self, x):
        return x - self.x_0 if self.x_0 is not None else x

    def forward(self, x):
        return np.linalg.norm(self._xd(x))

    def gradient(self, x):
        x_d = self._xd(x)
        return x_d / np.linalg.norm(x_d)

    def hessian(self, x):
        x_d = self._xd(x)
        d_inv = 1. / np.linalg.norm(x_d)
        return d_inv * np.eye(x.size) - d_inv**3 * np.outer(x_d, x_d)


class SoftNorm(DifferentiableMap):
    """
        Soft norm f(x; \alpha) = sqrt(x^2 + \alpha^2) - \alpha
    """

    def __init__(self, x_0=None, alpha=.05):
        self.x_0 = x_0
        self._n = 2 if x_0 is None else self.x_0.size
        self._alpha = alpha
        self._alpha_sq = self._alpha * self._alpha

    def output_dimension(self):
        return 1

    def input_dimension(self):
        return self._n

    def _xd(self, x):
        return x - self.x_0 if self.x_0 is not None else x

    def _alpha_norm(self, x):
        return np.sqrt(np.dot(self._xd(x), self._xd(x)) + self._alpha_sq)

    def forward(self, x):
        return self._alpha_norm(x) - self._alpha

    def gradient(self, x):
        return self._xd(x) / self._alpha_norm(x)


class Normalize(DifferentiableMap):
    """
        f(x) = x / |x|
    """

    def __init__(self, n):
        self._n = n

    def input_dimension(self):
        return self._n

    def output_dimension(self):
        return self._n

    def forward(self, x):
        return x / np.linalg.norm(x)

    def jacobian(self, x):
        dinv = 1. / np.linalg.norm(x)
        s = np.full((self._n, ), dinv)
        return np.diag(s) - np.outer(x, x) * (dinv ** 3)


class SoftMax(DifferentiableMap):
    """ Softmax

            f(x) = exp(x_i) / sum_j exp(x_j)
    """

    def __init__(self, n, gamma):
        self._n = n
        self._gamma = gamma

    def output_dimension(self):
        return self._n

    def input_dimension(self):
        return self._n

    def forward(self, x):
        z = np.exp(self._gamma * x)
        return z / np.sum(z)

    def jacobian(self, q):
        s = self.forward(q)
        return self._gamma * (np.diag(s) - np.outer(s, s))


class LogSumExp(SoftMax):
    """ Log of softmax (smooth max)

            f(x) = (1 / gamma) * log[ sum_j exp(gamma * x_j) ]

        A normalized version can be defined when all the monoids
        are positive f(x) =  log( sum(z) - (1-n))
    """

    def __init__(self, n, gamma):
        SoftMax.__init__(self, n, gamma)

    def output_dimension(self):
        return 1

    def forward(self, x):
        z = np.exp(self._gamma * x)
        return (1. / self._gamma) * np.log(np.sum(z))

    def jacobian(self, x):
        return SoftMax.forward(self, x)

    def hessian(self, x):
        z = np.exp(self._gamma * x)
        p_inv = 1 / np.sum(z)
        M = p_inv * np.diag(z) - (p_inv ** 2) * np.outer(z, z)
        return self._gamma * M


class Sigmoid(DifferentiableMap):
    """
        f(x) = 1 / (1 + e^-x)
    """

    def __init__(self, n):
        self._n = n

    def input_dimension(self):
        return self._n

    def output_dimension(self):
        return self._n

    def forward(self, x):
        y = np.zeros(self._n)
        for i in range(self._n):
            if x[i] > 0:
                y[i] = 1. / (1. + np.exp(-x[i]))
            else:
                expx = np.exp(x)
                y[i] = expx / (1. + expx)
        return y

    def jacobian(self, x):
        J = np.matrix(np.zeros((self._n, self._n)))
        s = self.forward(x)
        for i in range(self._n):
            J[i, i] = s[i] * (1 - s[i])
        return J

    def hessian(self, x):
        assert self.output_dimension() == 1
        H = np.matrix(np.zeros((self._n, self._n)))
        s = self.forward(x)[0]
        H[0, 0] = s * (1 - s) * (1 - 2 * s)
        return H


class Tanh(DifferentiableMap):
    """
        f(x) = (1 - e^-2x) / (1 + e^-2x)
    """

    def __init__(self, n):
        self._n = n

    def input_dimension(self):
        return self._n

    def output_dimension(self):
        return self._n

    def forward(self, x):
        y = np.zeros(self._n)
        for i in range(self._n):
            exp2x = np.exp(-2. * x[i])
            y[i] = (1. - exp2x) / (1. + exp2x)
        return y

    def jacobian(self, x):
        J = np.matrix(np.zeros((self._n, self._n)))
        tanh = self.forward(x)
        for i in range(self._n):
            J[i, i] = 1 - tanh[i] ** 2
        return J

    def hessian(self, x):
        """ TODO """
        assert self.output_dimension() == 1


class Arccos(DifferentiableMap):
    """
        f(x) = arccos(x)
    """

    def __init__(self):
        return

    def input_dimension(self):
        return 1

    def output_dimension(self):
        return 1

    def forward(self, x):
        return np.arccos(x)

    def jacobian(self, x):
        J = np.matrix([0.])
        J[0, 0] = -1 / np.sqrt(1 - x ** 2)
        return J

    def hessian(self, x):
        H = np.matrix([0.])
        H[0, 0] = -x / np.power(1 - x ** 2, 1.5)
        return H


class RadialBasisFunction(DifferentiableMap):
    """
    Implements an unnormalized Gaussian

    f(x) = exp( -1/2 |x - x0|^2_H )

        phi(x) = 1/2 (x - x0)^T H (x - x0)
               = 1/2 [ x^T H (x - x0)  - x0^T H (x - x0) ]
               = 1/2 [ x^T H x - x^T H x0  -  x0^T H x + x0^T H x0 ]
               = 1/2 [ x^T H x - 2 x0^T H x - x0^T H x0 ]


    Create a Gaussian function centered at x0 with
    Hessian (inverse covariance) H

    TODO:
        * implement as pullback for derivatives...
        * tod check the math...
    """

    def __init__(self, x0, H):
        self._x0 = x0
        self._H = H
        Hx0 = np.dot(H, x0)
        self._phi = QuadricFunction(H, -Hx0, .5 * np.dot(x0.T, Hx0))

    def forward(self, x):
        # return np.exp(-self._phi.forward(x))
        d = x - self._x0
        return np.exp(-.5 * np.dot(np.dot(d.T, self._H), d))

    def input_dimension(self):
        return 2

    def output_dimension(self):
        return 1


class MakeDifferentiableMap(DifferentiableMap):
    """ Make a function a differentiable map """

    def __init__(self, f, g, m, n):
        self._f = f
        self._g = g
        self._n = n
        self._m = m

    def output_dimension(self):
        return self._m

    def input_dimension(self):
        return self._n

    def forward(self, x):
        return np.array(self._f(x))

    def jacobian(self, x):
        return np.array(self._g(x))


def finite_difference_jacobian(f, q):
    """ Takes an object f that has a forward method returning
    a numpy array when querried. """
    assert q.size == f.input_dimension()
    dt = 1e-4
    dt_half = dt / 2.
    J = np.zeros((
        f.output_dimension(), f.input_dimension()))
    for j in range(q.size):
        q_up = copy.deepcopy(q)
        q_up[j] += dt_half
        x_up = f.forward(q_up)
        q_down = copy.deepcopy(q)
        q_down[j] -= dt_half
        x_down = f.forward(q_down)
        J[:, j] = (x_up - x_down) / dt
    return np.matrix(J)


def finite_difference_hessian(f, q):
    """ Takes an object f that has a forward method returning
    a numpy array when querried. """
    assert q.size == f.input_dimension()
    assert f.output_dimension() == 1
    dt = 1e-4
    dt_half = dt / 2.
    H = np.zeros((
        f.input_dimension(), f.input_dimension()))
    for j in range(q.size):
        q_up = copy.deepcopy(q)
        q_up[j] += dt_half
        g_up = f.gradient(q_up)
        q_down = copy.deepcopy(q)
        q_down[j] -= dt_half
        g_down = f.gradient(q_down)
        H[:, j] = (g_up - g_down) / dt
    return np.matrix(H)


def check_is_close(a, b, tolerance=1e-10):
    """ Returns True of all variable are close."""
    results = np.isclose(
        np.array(a),
        np.array(b),
        atol=tolerance)
    return results.all()


def check_jacobian_against_finite_difference(phi, verbose=True,
                                             tolerance=1e-4):
    """ Makes sure the jacobian is close to the finite difference """
    q = np.random.rand(phi.input_dimension())
    J = phi.jacobian(q)
    J_diff = finite_difference_jacobian(phi, q)
    if verbose:
        print("J : ")
        print(J)
        print("J_diff : ")
        print(J_diff)
    return check_is_close(J, J_diff, tolerance)


def check_hessian_against_finite_difference(phi, verbose=True,
                                            tolerance=1e-4):
    """ Makes sure the hessuaian is close to the finite difference """
    q = np.random.rand(phi.input_dimension())
    H = phi.hessian(q)
    H_diff = finite_difference_hessian(phi, q)
    if verbose:
        print("H : ")
        print(H)
        print("H_diff : ")
        print(H_diff)
    return check_is_close(H, H_diff, tolerance)
