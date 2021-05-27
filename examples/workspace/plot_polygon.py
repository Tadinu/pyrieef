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

env = EnvBox(
    origin=np.array([.0, .0]),
    dim=np.array([2., 2.]))

# polygon = ConvexPolygon(origin=env.origin + np.array([-.2, -.2]))
polygon = ellipse_polygon(.7, .3, [-.2, .0], [-.1, -.1], .7)

workspace = Workspace(env)
workspace.obstacles.append(polygon)
viewer = WorkspaceDrawer(workspace, wait_for_keyboard=True)
sdf = SignedDistanceWorkspaceMap(workspace)

viewer.draw_ws_obstacles()
viewer.draw_ws_circle(origin=env.origin, radius=1.)
# viewer.background_matrix_eval = False
viewer.draw_ws_background(sdf, nb_points=200)

for theta in np.linspace(0, 2 * math.pi, 20, endpoint=False):
    p1 = np.array([np.cos(theta), np.sin(theta)])
    p2 = polygon.intersection_point(p1)
    viewer.draw_ws_line_fill([polygon.focus(), p1], color='k')
    viewer.draw_ws_point(p2, color='r', shape='o')

viewer.show_once()
