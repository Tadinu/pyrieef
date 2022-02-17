#!/usr/bin/env python

# Copyright (c) 2022
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
#                                    Jim Mainprice on Thursday February 13 2022

import demos_common_imports

# pyrieef
from pyrieef.geometry.differentiable_geometry import *

# External
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import matplotlib.transforms as transforms
from numpy.testing import assert_allclose


def confidence_ellipse(ax,
                       cov=None, x=None, y=None,
                       n_std=3.0, facecolor='none', **kwargs):
    """
    Create a plot of the covariance confidence ellipse of *x* and *y*.

    Parameters
    ----------

    cov : array
        The covariance matrix

    ax : matplotlib.axes.Axes
        The axes object to draw the ellipse into.

    n_std : float
        The number of standard deviations to determine the ellipse's radiuses.

    **kwargs
        Forwarded to `~matplotlib.patches.Ellipse`

    Returns
    -------
    matplotlib.patches.Ellipse
    """
    if cov is None:

        if x.size != y.size:
            raise ValueError("x and y must be the same size")

        cov = np.cov(x, y)

        mean_x = np.mean(x)
        mean_y = np.mean(y)

    else:

        mean_x = 0
        mean_y = 0

    pearson = cov[0, 1]/np.sqrt(cov[0, 0] * cov[1, 1])
    # Using a special case to obtain the eigenvalues of this
    # two-dimensionl dataset.
    ell_radius_x = np.sqrt(1 + pearson)
    ell_radius_y = np.sqrt(1 - pearson)
    ellipse = Ellipse((0, 0), width=ell_radius_x * 2, height=ell_radius_y * 2,
                      facecolor=facecolor, **kwargs)

    # Calculating the stdandard deviation of x from
    # the squareroot of the variance and multiplying
    # with the given number of standard deviations.
    scale_x = np.sqrt(cov[0, 0]) * n_std

    # calculating the stdandard deviation of y ...
    scale_y = np.sqrt(cov[1, 1]) * n_std

    transf = transforms.Affine2D() \
        .rotate_deg(45) \
        .scale(scale_x, scale_y) \
        .translate(mean_x, mean_y)

    ellipse.set_transform(transf + ax.transData)
    return ax.add_patch(ellipse)


def sample_data():

    np.random.seed(4)

    nb_samples = 10

    # mean
    mu = np.zeros(2)

    # covariance
    # A = np.random.rand(2, 2)
    A = np.array([[1., .1], [.1, .2]])
    Sigma = A.transpose() @ A

    M = np.random.multivariate_normal(mu, Sigma, nb_samples).T

    return (Sigma, M)


class EmpiricalCovariance(DifferentiableMap):
    """ Calculates the empirical covariance of a zero mean distribution """

    def __init__(self, m, n):
        self._m = m             # nb of samples
        self._n = n             # nb of random variables

    def output_dimension(self):
        return 1

    def input_dimension(self):
        return n

    def forward(self, x):
        X = x.reshape(self._m, self._n)
        covariance = X.T @ X
        covariance /= float(self._m)
        print("cov 2 : ", covariance)
        return covariance.flatten()


(Sigma, M) = sample_data()

print(M.shape)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 6))

x = M[0, :]
y = M[1, :]

x0 = np.mean(x)
y0 = np.mean(y)

x = x - x0
y = y - y0

M0 = np.array([x, y])

cov1 = np.cov(M0)
cov2 = EmpiricalCovariance(x.size, 2)

print("cov1 : ", cov1)
print("mean0 (x) : ", np.mean(M0[0, :]))
print("mean0 (y) : ", np.mean(M0[1, :]))

assert_allclose(cov1.flatten(), cov2(M0.flatten()))


# ax1.plot(x, y, 'x', c='r')
# confidence_ellipse(ax1, cov=Sigma, edgecolor='red')
# confidence_ellipse(ax1, x=x, y=y, edgecolor='blue')
# ax1.axis('equal')
# ax1.set_title('Original Samples')

# ax2.plot(x, y, 'x', c='b')
# ax2.axis('equal')
# ax2.set_title('Optmized Samples')

# plt.show()