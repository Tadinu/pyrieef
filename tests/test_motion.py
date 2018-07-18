#!/usr/bin/env python

# Copyright (c) 2015 Max Planck Institute
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
# Jim Mainprice on Sunday June 17 2018

from test_common_imports import *
from motion.trajectory import *
from motion.cost_terms import *
from motion.motion_optimization import *


def test_finite_differences():
    dim = 4
    acceleration = FiniteDifferencesAcceleration(dim, 1)
    print acceleration.jacobian(np.zeros(dim * 3))
    assert check_jacobian_against_finite_difference(acceleration)


def test_cliques():
    A = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    cliques = [A[i:3 + i] for i in range(len(A) - 2)]
    print A
    print cliques
    assert len(cliques) == (len(A) - 2)

    dimension = 10
    network = CliquesFunctionNetwork(dimension, 1)
    x_0 = np.zeros(3)
    for _ in range(network.nb_cliques()):
        network.add_function(SquaredNorm(x_0))
    cliques = network.all_cliques(A)
    print cliques
    assert len(cliques) == (len(A) - 2)


def test_trajectory():
    T = 10

    traj = Trajectory(T)
    print type(traj)
    print traj

    size = 2 * (T + 2)  # This is the formula for n = 2

    traj.set(np.ones(size))
    print type(traj)
    print str(traj)

    traj.set(np.random.rand(size))
    print type(traj)
    print str(traj)

    print "final configuration : "
    print traj.final_configuration()

    print "config 3 : "
    print traj.configuration(3)

    print "clique 3 : "
    print traj.clique(3)

    print "config 3 (ones) : "
    traj.configuration(3)[:] = np.ones(2)
    print traj.configuration(3)

    print "final configuration (ones) : "
    traj.final_configuration()[:] = np.ones(2)
    print traj.final_configuration()


def test_motion_optimimization_2d():
    motion_optimization = MotionOptimization2DCostMap(None, None)
    trajectory = Trajectory(motion_optimization.T)
    sum_acceleration = motion_optimization.cost(trajectory)
    print "sum_acceleration : ", sum_acceleration
    q_init = np.zeros(2)
    q_goal = np.ones(2)
    trajectory = linear_interpolation_trajectory(
        q_init, q_goal, motion_optimization.T)
    print trajectory
    print trajectory.final_configuration()
    sum_acceleration = motion_optimization.cost(trajectory)
    print "sum_acceleration : ", sum_acceleration
    assert check_jacobian_against_finite_difference(
        motion_optimization.objective)


if __name__ == "__main__":
    test_trajectory()
    test_cliques()
    test_finite_differences()
    test_motion_optimimization_2d()