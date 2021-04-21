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

from demos_common_imports import *
import numpy as np
from pyrieef.geometry.workspace import *
from pyrieef.geometry.pixel_map import *
from pyrieef.geometry.geodesics import *
from pyrieef.geometry.diffeomorphisms import *
from pyrieef.geometry.utils import *
from pyrieef.motion.cost_terms import *
from pyrieef.rendering.workspace_planar import WorkspaceDrawer
import itertools

circles = []
circles.append(Circle(origin=[.1, .0], radius=0.1))
# circles.append(Circle(origin=[.1, .25], radius=0.05))
# circles.append(Circle(origin=[.2, .25], radius=0.05))
# circles.append(Circle(origin=[.0, .25], radius=0.05))

workspace = Workspace()
workspace.obstacles = circles
renderer = WorkspaceDrawer(workspace)
sdf = SignedDistanceWorkspaceMap(workspace)
cost = ObstaclePotential2D(sdf, 1., 1.7)

x_goal = np.array([0.4, 0.4])
nx, ny = (3, 3)
x = np.linspace(-.2, -.1, nx)
y = np.linspace(-.5, -.1, ny)

for i, j in itertools.product(list(range(nx)), list(range(ny))):
    x_init = np.array([x[i], y[j]])
    line = NaturalGradientGeodescis(cost, x_init, x_goal, attractor=False)
    renderer.draw_ws_line(line)
renderer.draw_ws_background(sdf)
renderer.draw_ws_obstacles()
renderer.draw_ws_point([x_goal[0], x_goal[1]], color='k', shape='o')
renderer.show()
