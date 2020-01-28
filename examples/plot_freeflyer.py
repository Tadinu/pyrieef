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
#                                      Jim Mainprice on Monday January 27 2020

import demos_common_imports
from pyrieef.geometry.workspace import *
from pyrieef.kinematics.robot import *
from pyrieef.rendering.workspace_renderer import WorkspaceDrawer

robot = create_robot_from_file()
env = EnvBox()
box = Box(origin=np.array([-.5, -.5]), dim=np.array([.5, .5]))
workspace = Workspace(env)
# workspace.obstacles.append(box)
# workspace.obstacles.append(hexagon(.1))
# workspace.obstacles.append(Polygon(
#     origin=[-.5, -.5],
#     verticies=[
#         np.array([.3, .3]),
#         np.array([.0, .3]),
#         np.array([.0, .0]),
#         np.array([.3, .0])]))
workspace.obstacles.append(
    Polygon(origin=np.array([0., 0.]), verticies=robot.shape))
viewer = WorkspaceDrawer(workspace, wait_for_keyboard=True)
sdf = SignedDistanceWorkspaceMap(workspace)
viewer.draw_ws_obstacles()
for name, i in robot.keypoint_names.items():
    p = robot.keypoint_map(i)(np.zeros(3))
    viewer.draw_ws_point(p, color='r', shape='o')
viewer.background_matrix_eval = True
viewer.draw_ws_background(sdf, nb_points=200)
viewer.show_once()