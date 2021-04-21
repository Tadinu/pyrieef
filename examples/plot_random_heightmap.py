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
from pyrieef.rendering.workspace_planar import WorkspaceHeightmap
from pyrieef.geometry.workspace import *
from pyrieef.motion.cost_terms import *

np.random.seed(1)

workspace = sample_circle_workspaces(nb_circles=4)
viewer = WorkspaceHeightmap(workspace)
cost = SimplePotential2D(SignedDistanceWorkspaceMap(workspace))
# extent = workspace.box.extent()
# p_lower = np.array([extent.x_min, extent.y_min])
# p_upper = np.array([extent.x_max, extent.y_max])
# sdf = SumOfTerms([sdf, BoundBarrier(p_lower, p_upper, alpha=20.)])
viewer.draw_ws_background(cost)
for i, o in enumerate(workspace.obstacles):
    p = o.origin
    viewer.draw_ws_sphere(p, height=viewer.normalize_height(cost(p)))
while True:
    viewer.show()
