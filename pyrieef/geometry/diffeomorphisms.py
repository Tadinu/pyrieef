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
import sys
import math
from .workspace import *
from .utils import *
from .differentiable_geometry import *
from scipy.special import lambertw
from abc import abstractmethod

# --------
# this is the scaling factor
# - gamma | x - r | ... Does not work...
# TODO look into this.


def alpha3_f(eta, r, gamma, x):
    return eta * np.exp(-gamma * (x - r))

# y = f(x) is the distance value it gives


def beta3_f(eta, r, gamma, x):
    return x - alpha_f(eta, r, gamma, x)


def beta3_inv_f(eta, r, gamma, y):
    l = lambertw(eta * gamma * np.exp(gamma * r - gamma * y)).real
    return l / gamma + y

# --------


def alpha2_f(eta, r, gamma, x):
    return eta / x

# y = f(x) is the distance value
# it gives


def beta2_f(eta, r, gamma, x):
    return x - alpha2_f(eta, r, gamma, x)


def beta2_inv_f(eta, r, gamma, y):
    return (y + np.sqrt(y ** 2 + 4. * eta)) * 0.5

# --------
# this is the scaling factor
# - gamma | x - r | ...


def alpha_f(eta, r, gamma, x):
    return eta * np.exp(-gamma * x + r)

# y = f(x) is the distance value it gives


def beta_f(eta, r, gamma, x):
    return x - alpha_f(eta, r, gamma, x)

# def beta_inv_f(eta, r, gamma, y):
#     return lambertw(gamma * eta * np.exp(-gamma * y)).real / gamma + y

# INVERSE OF BETA
# neta * exp( gamma *(x + r) )


def beta_inv_f(eta, r, gamma, y):
    l = lambertw(eta * gamma * np.exp(r - gamma * y)).real
    return l / gamma + y


class Diffeomoprhism(DifferentiableMap):

    def output_dimension(self):
        return self.input_dimension()

    @abstractmethod
    def inverse(self, y):
        raise NotImplementedError()


class PlaneDiffeomoprhism(Diffeomoprhism):

    def input_dimension(self):
        return 2


class AnalyticPlaneDiffeomoprhism(PlaneDiffeomoprhism):

    @abstractmethod
    def object(self):
        raise NotImplementedError()


class ComposeDiffeo(Compose):

    def __init__(self, f, g):
        """

            f round g : f(g(q))

            This function should be called pullback if we approxiate
            higher order (i.e., hessians) derivaties by pullback, here it's
            computing the true 1st order derivative of the composition.

            """
        Compose.__init__(self, f, g)

    def inverse(self, y):
        return self._g.inverse(self._f.inverse(y))


# The polar coordinates r and phi can be converted to the Cartesian coordinates
# x and y by using the trigonometric functions sine and cosine


class PolarCoordinateSystem(AnalyticPlaneDiffeomoprhism):

    def __init__(self):
        self.circle = Circle()
        self.circle.radius = .1
        self.circle.origin = np.array([.0, .0])
        self.eta = self.circle.radius  # for the exp

    # Access the internal object.
    def object(self):
        return self.circle

    # Converts from Euclidean to Polar
    # p[0] : x
    # p[1] : y
    def forward(self, p):
        p_0 = p - self.circle.origin
        r = np.linalg.norm(p_0)
        phi = math.atan2(p_0[1], p_0[0])
        return np.array([r, phi])

    # Converts from Polar to Euclidean
    # p[0] : r
    # p[1] : phi
    def inverse(self, p):
        x = p[0] * math.cos(p[1]) + self.circle.origin[0]
        y = p[0] * math.sin(p[1]) + self.circle.origin[1]
        return np.array([x, y])


def ellipse_polygon(a, b,
                    focus=[0., 0.],
                    translation=[0., 0.],
                    orientation=0.):
    ellipse = Ellipse(a, b)
    ellipse.nb_points = 50
    points = ellipse.sampled_points()
    R = rotation_matrix_2d(180 * orientation / np.pi)
    for i, p in enumerate(points):
        points[i] = np.dot(R, p) + np.array(translation)
    focus = np.dot(R, focus) + np.array(translation)
    return ConvexPolygon(
        ellipse.origin + focus,
        verticies=points[:-1])


class ConvexPolygon(Polygon):

    def __init__(self,
                 origin=np.array([0., 0.]),
                 verticies=[
                     np.array([.5, .5]),
                     np.array([-.5, .5]),
                     np.array([-.5, -.5]),
                     np.array([.5, -.5])
                 ]):
        Polygon.__init__(self, origin, verticies)
        self._focus = self.origin
        self._vertex_coordinates()

    def focus(self):
        return self._focus

    def _vertex_coordinates(self):
        """ associates an angle for each vertex """
        v0 = self._verticies[0] - self._focus
        self._coordinates = [None] * len(self._verticies)
        for i, v in enumerate(self._verticies):
            self._coordinates[i] = vectors_angle(v0, v - self._focus)

    def intersection_point(self, x):
        """ point on the boundary that intersects the
            line between the focus and a given point
            TODO : test this function """
        v0 = self._verticies[0] - self._focus
        alpha = vectors_angle(v0, x - self._focus)
        j = 0
        for i, theta in enumerate(self._coordinates):
            if theta > alpha:
                if i == 0:
                    j = len(self._coordinates) - 1
                else:
                    j = i - 1
                break
        return line_line_intersection_det(
            self._focus, x,
            self._verticies[i],
            self._verticies[j])


class AnalyticConvexPolygon(AnalyticPlaneDiffeomoprhism):

    def __init__(self, origin=[.1, -.1], polygon=None):
        self._object = polygon
        # self.eta = self.circle.radius  # for the exp
        # self.eta = .1  # for the 1/x
        self.gamma = 1.
        self.set_alpha(alpha_f, beta_inv_f)

    def object(self):
        """ Access the internal object. """
        return self._object

    def set_alpha(self, a, b):
        """ To recover the distance scaling one should
            pass the alpha and beta inverse functions."""
        self.alpha_ = a
        self.beta_inv_ = b

    def Deformationforward(self, x):
        """ squishes points inside the circle """
        x_center = x - self._object.origin
        r = self.radius(x)
        d_1 = np.linalg.norm(x_center)
        alpha = self.alpha_(r, r, self.gamma, d_1)
        return alpha * normalize(x_center)

    def Deformationinverse(self, y):
        """ maps them back outside of the circle """
        y_center = y - self._object.origin
        r = self.radius(y)
        d_2 = np.linalg.norm(y_center)
        d_1 = self.distance_before_contraction(y, d_2)
        alpha = d_1 - d_2
        return alpha * normalize(y_center)

    def radius(self, x):
        return np.linalg.norm(
            self._object.intersection_point(x) - self._object.origin)

    def distance_before_contraction(self, x, d_2):
        r = self.radius(x)
        return self.beta_inv_(r, r, self.gamma, d_2)

    def forward(self, x):
        """ squishes points inside the circle """
        y = x - self.Deformationforward(x)
        return y

    def inverse(self, y):
        """ maps them back outside of the circle """
        x = y + self.Deformationinverse(y)
        return x


class ElectricCircle(AnalyticPlaneDiffeomoprhism):

    def __init__(self):
        self.circle = Circle()
        self.circle.radius = .1
        self.circle.origin = np.array([.1, -.1])
        self.eta = self.circle.radius  # for the exp

    # Access the internal object.
    def object(self):
        return self.circle

    # squishes points inside the circle
    def forward(self, x):
        # print "origin : ", self.origin
        x_center = x - self.circle.origin
        d_1 = np.linalg.norm(x_center)
        y = np.array([0., 0.])
        y[0] = math.pow(d_1, self.eta)
        y[1] = math.atan2(x_center[1], x_center[0])
        return y

    # maps them back outside of the circle
    def inverse(self, y):
        # print "origin : ", self.origin
        x = np.array([0., 0.])
        x_center = np.array([0., 0.])
        d_1 = math.pow(y[0], 1 / self.eta)
        x_center[0] = math.cos(y[1]) * d_1
        x_center[1] = math.sin(y[1]) * d_1
        x = x_center + self.circle.origin
        return x


class AnalyticEllipse(AnalyticPlaneDiffeomoprhism):

    def __init__(self, a = 0., b = 0.):
        self.ellipse = Ellipse(a, b)
        self.radius = .1
        self.eta = self.radius  # for the exp
        # self.eta = .01 # for the 1/x
        self.gamma = 1.
        self.origin = np.array([.1, -.1])

    # Access the internal object.
    def object(self):
        return self.ellipse

    # To recover the distance scaling one should
    # pass the alpha and beta inverse functions.
    def set_alpha(self, a, b):
        self.alpha_ = a
        self.beta_inv_ = b

    # squishes points inside the circle
    def Deformationforward(self, x):
        x_center = x - self.origin
        d_1 = np.linalg.norm(x_center)
        alpha = self.alpha_(self.eta, self.radius, self.gamma, d_1)
        return alpha * normalize(x_center)

    # maps them back outside of the circle
    def Deformationinverse(self, y):
        # print "origin : ", self.origin
        y_center = y - self.origin
        d_2 = np.linalg.norm(y_center)
        d_1 = self.beta_inv_(self.eta, self.radius, self.gamma, d_2)
        alpha = d_1 - d_2
        return alpha * normalize(y_center)

    # squishes points inside the circle
    def forward(self, x):
        y = x - self.Deformationforward(x)
        return y

    # maps them back outside of the circle
    def inverse(self, y):
        x = y + self.Deformationinverse(y)
        return x


class AnalyticCircle(AnalyticPlaneDiffeomoprhism):

    def __init__(self, origin=[.1, -.1], radius=.1):
        self.circle = Circle(origin, radius)
        self.eta = self.circle.radius  # for the exp
        # self.eta = .01 # for the 1/x
        self.gamma = 1.
        # self.set_alpha(alpha_f, beta_inv_f)

    def object(self):
        """ Access the internal object. """
        return self.circle

    def set_alpha(self, a, b):
        """
        To recover the distance scaling one should pass
        the alpha and beta inverse functions.
        """
        self.alpha_ = a
        self.beta_inv_ = b

    def radius(self, x):
        return self.circle.radius

    def Deformationforward(self, x):
        """ squishes points inside the circle """
        x_center = x - self.circle.origin
        d_1 = np.linalg.norm(x_center)
        # alpha = self.alpha_(self.eta, self.circle.radius, self.gamma, d_1)
        alpha = self.eta * np.exp(
            -self.gamma * d_1 + self.circle.radius)
        return alpha * normalize(x_center)

    def distance_before_contraction(self, x, d_2):
        # d_1 = self.beta_inv_(self.eta, self.circle.radius, self.gamma, d_2)
        l = lambertw(
            self.eta * self.gamma *
            np.exp(self.circle.radius - self.gamma * d_2)).real
        d_1 = l / self.gamma + d_2
        return d_1

    def Deformationinverse(self, y):
        """  maps them back outside of the circle """
        y_center = y - self.circle.origin
        d_2 = np.linalg.norm(y_center)
        d_1 = self.distance_before_contraction(y, d_2)
        alpha = d_1 - d_2
        return alpha * normalize(y_center)

    def forward(self, x):
        """ squishes points inside the circle """
        y = x - self.Deformationforward(x)
        return y

    def inverse(self, y):
        """ maps them back outside of the circle """
        x = y + self.Deformationinverse(y)
        return x


class SoftmaxWithInverse(Diffeomoprhism):
    """ 
    Maps a vector to the softmax value:

            f_i (x) = exp(x_i) / sum_j exp(x_j)
    """

    def __init__(self, gamma):
        self._gamma = gamma
        self._partition = 1.

    def forward(self, x):
        """ Compute the softmax of vector x."""
        exps = np.exp(self._gamma * x)
        self._partition = np.sum(exps)
        return exps / self._partition
        # return np.ones(x.shape)

    def inverse(self, y):
        """ Inverse of softmax for vector y."""
        return np.log(y) / self._gamma + np.log(self._partition)


class AnalyticMultiDiffeo(AnalyticPlaneDiffeomoprhism):

    def __init__(self, diffeomorphisms):
        self._diffeomorphisms = diffeomorphisms
        self._softmax = SoftmaxWithInverse(gamma=-14)

    def object(self):
        objects = [phi.object() for phi in self._diffeomorphisms]
        return Complex(np.array([0., 0.]), objects)

    def activations(self, x):
        """
         This activation function is implemented through
         a softmax function.
        """
        part = 0.
        distances = np.array([0.] * len(self._diffeomorphisms))
        for j, phi in enumerate(self._diffeomorphisms):
            distances[j] = phi.object().dist_from_border(x)
        return self._softmax.forward(distances)

    def activations_inv(self, y):
        """
         This activation function is implemented through
         a softmax function.
        """
        part = 0.
        distances = np.array([0.] * len(self._diffeomorphisms))
        for j, phi in enumerate(self._diffeomorphisms):
            o = phi.object()
            distances[j] = phi.distance_before_contraction(
                y, np.linalg.norm(y - phi.object().origin)) - phi.radius(y)
        return self._softmax.forward(distances)

    def forward(self, x):
        dx = np.array([0., 0.])
        alpha = self.activations(x)
        for i, phi in enumerate(self._diffeomorphisms):
            dx += alpha[i] * phi.Deformationforward(x)
        return x - dx

    def inverse(self, y):
        """ This is not really the inverse, it is an approximation """
        dy = np.array([0., 0.])
        alpha = self.activations_inv(y)
        for i, phi in enumerate(self._diffeomorphisms):
            dy += alpha[i] * phi.Deformationinverse(y)
        x = y + dy
        return x


def InterpolationGeodescis(obj, x_1, x_2):
    line = []
    line_inter = []
    line.append(x_1)
    p_init = obj.forward(x_1)
    p_goal = obj.forward(x_2)
    for s in np.linspace(0., 1., 100):
        p = (1. - s) * p_init + s * p_goal
        x_new = obj.inverse(p)
        line.append(x_new)
        line_inter.append(p)
        if np.linalg.norm(x_new - x_2) <= 0.001:
            break
    return [np.array(line), np.array(line_inter)]


def NaturalGradientGeodescis(obj, x_1, x_2, attractor=True):
    x_init = np.matrix(x_1).T
    x_goal = np.matrix(x_2).T
    x_tmp = x_init
    eta = 0.01
    line = []
    line.append([x_init.item(0), x_init.item(1)])
    for i in range(500):
        # Compute tensor.
        J = obj.jacobian(np.array(x_tmp.T)[0])
        # Implement the attractor derivative here directly
        # suposes that it's of the form |phi(q) - phi(q_goal)|^2
        # hence the addition of the J^T
        B = J.T if attractor else np.eye(2)
        ridge = 0.0
        g_inv = np.linalg.inv(J.T * J + ridge * np.eye(2))
        x_new = x_tmp + eta * g_inv * B * normalize(x_goal - x_tmp)
        line.append(np.array([x_new.item(0), x_new.item(1)]))
        if np.linalg.norm(x_new - x_goal) <= eta:
            line.append([x_goal.item(0), x_goal.item(1)])
            print(("End at : ", i))
            break
        x_tmp = x_new
    return np.array(line)
