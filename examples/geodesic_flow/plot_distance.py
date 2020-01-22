#!/usr/bin/env python

# Copyright (c) 2019, University of Stuttgart
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
#                                         Jim Mainprice on Wed January 22 2019

from demos_common_imports import *
import numpy as np
from pyrieef.geometry.workspace import *
from pyrieef.geometry.pixel_map import *
from pyrieef.geometry.geodesics import *
from pyrieef.rendering.workspace_renderer import WorkspaceDrawer
from pyrieef.utils.misc import *
import itertools
import matplotlib.pyplot as plt


NB_POINTS = 20
VERBOSE = False
ROWS = 3
COLS = 3


def heat_diffusion(workspace, source, iterations):
    """
    Diffuses heat from a source point on a 2D grid defined
    over a workspace populated by obstacles.

        The function was implemented by following
        https://people.eecs.berkeley.edu/~demmel/\
            cs267/lecture17/lecture17.html#link_1.5

    TODO test it agains the heat kernel
    """
    extent = workspace.box.extent()
    dx = (extent.x_max - extent.x_min) / NB_POINTS
    dy = (extent.y_max - extent.y_min) / NB_POINTS
    occupancy = occupancy_map(NB_POINTS, workspace).T
    grid = PixelMap(dx, extent)
    print("Max t size : ", (dx ** 2))
    assert dx == dy
    dim = NB_POINTS ** 2
    M = np.zeros((dim, dim))
    h = dx
    t = .0003  # (dx ** 2) (ideal)
    d = 1. / (h ** 2)

    # Euler
    c = t * d
    a = 4. * c

    #  Crank-Nicholson
    # c = -t / (2. * (h ** 2))
    # a = 2. * t / (h ** 2)
    if VERBOSE:
        print("a : ", a)
        print("c : ", c)
    print("fill matrix...")
    # U(i,j,m+1) = U(i,j,m) + k*Discrete-2D-Laplacian(U)(i,j,m)
    #                  k
    #            = (1 - 4*---) * U(i,j,m) +
    #                 h^2
    #           k
    #          ---*(U(i-1,j,m) + U(i+1,j,m) + U(i,j-1,m) + U(i,j+1,m))
    #          h^2
    # we use a row major representation of the matrix
    for p, q in itertools.product(range(dim), range(dim)):
        i0, j0 = row_major(p, NB_POINTS)
        i1, j1 = row_major(q, NB_POINTS)
        if p == q:
            M[p, q] = a
        elif (
                i0 == i1 - 1) and (j0 == j1) or (
                i0 == i1 + 1) and (j0 == j1) or (
                i0 == i1) and (j0 == j1 - 1) or (
                i0 == i1) and (j0 == j1 + 1):
            M[p, q] = c
        if occupancy[i0, j0] == 1. or occupancy[i1, j1] == 1.:
            M[p, q] = 0.
    if VERBOSE:
        with np.printoptions(
                formatter={'float': '{: 0.1f}'.format},
                linewidth=200):
            print("M : \n", M)
    u_0 = np.zeros((dim))
    source_grid = grid.world_to_grid(source)
    u_0[source_grid[0] + source_grid[1] * NB_POINTS] = 1.
    if VERBOSE:
        print(" - I.shape : ", I.shape)
        print(" - M.shape : ", M.shape)
        print(" - u_0.shape : ", u_0.shape)
    print("solve...")
    costs = []
    u_t = u_0
    for i in range(iterations):
        u_t = np.linalg.solve(np.eye(dim) - M, u_t)
        costs.append(np.reshape(u_t, (-1, NB_POINTS)).copy())
    print("solved!")
    return costs


circles = []
circles.append(Circle(origin=[.1, .0], radius=0.1))
circles.append(Circle(origin=[.1, .25], radius=0.05))
circles.append(Circle(origin=[.2, .25], radius=0.05))
circles.append(Circle(origin=[.0, .25], radius=0.05))

workspace = Workspace()
workspace.obstacles = circles
renderer = WorkspaceDrawer(workspace, rows=ROWS, cols=COLS)
x_source = np.array([0.2, 0.15])

# ------------------------------------------------------------------------------
iterations = ROWS * COLS
U = heat_diffusion(workspace, x_source, iterations)
for i in range(iterations):
    renderer.set_drawing_axis(i)
    renderer.draw_ws_obstacles()
    renderer.draw_ws_point([x_source[0], x_source[1]], color='r', shape='o')
    renderer.background_matrix_eval = False
    renderer.draw_ws_img(U[i], interpolate="bicubic",
                         color_style=plt.cm.hsv)
renderer.show()