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

import demos_common_imports
from pyrieef.geometry.workspace import *
from pyrieef.geometry.diffeomorphisms import *
from pyrieef.rendering.workspace_planar import WorkspaceDrawer

env = EnvBox(dim=np.array([2., 2.]))
box = Box(origin=np.array([-.5, -.5]), dim=np.array([.5, .5]))
segment = Segment(origin=np.array([.4, -.5]), orientation=0.2)
circle = Circle(origin=np.array([.5, .5]), radius=0.2)
ellipse = Ellipse(a=0.5, b=0.3)
polygon = hexagon(.33)
# polygon = ConvexPolygon()
workspace = Workspace(env)
workspace.obstacles.append(box)
workspace.obstacles.append(segment)
workspace.obstacles.append(circle)
workspace.obstacles.append(polygon)
# workspace.obstacles.append(ellipse)
viewer = WorkspaceDrawer(workspace, wait_for_keyboard=True)
sdf = SignedDistanceWorkspaceMap(workspace)
viewer.draw_ws_obstacles()
viewer.background_matrix_eval = True
viewer.draw_ws_background(sdf, nb_points=200)
viewer.show_once()
