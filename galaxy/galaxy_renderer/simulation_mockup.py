"""
    Module to send changing object positions through a pipe. Note that
    this is not a simulation, but a mockup.
"""
#
# Copyright (C) 2017  "Peter Roesch" <Peter.Roesch@fh-augsburg.de>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
# or open http://www.fsf.org/licensing/licenses/gpl.html
#
import multiprocessing
import sys
import time

import numpy as np

from Semesterprojekt.galaxy.galaxy_renderer.simulation_constants import END_MESSAGE
import Semesterprojekt.galaxy.galaxy_calc as galaxy

__FPS = 60
__DELTA_ALPHA = 0.01
# speed = simulation_speed
GALAXY_ONE = None
NR_OF_CORES = multiprocessing.cpu_count()
TIMER = 0

argumentQueue = multiprocessing.JoinableQueue()
resultQueue = multiprocessing.Queue()
nrOfProcesses = multiprocessing.cpu_count()


def _move_bodies(bodies, delta_t, speed):
    for i in range(speed):
        GALAXY_ONE.update(delta_t)

    for j in range(len(bodies)):
        for i in range(3):
            bodies[j][i] = (GALAXY_ONE.planets[j].position[i] / galaxy.DISTANCE_SUN) - 1
    time.sleep(1 / __FPS)


def _initialise_bodies(nr_of_bodies, color=False):
    if color:
        body_array = np.zeros((nr_of_bodies, 8), dtype=np.float64)
    else:
        body_array = np.zeros((nr_of_bodies, 4), dtype=np.float64)
    for body_index in range(nr_of_bodies):
        body_array[body_index][0] = 0.9 / (nr_of_bodies - body_index)
        if color:
            body_array[body_index][4:7] = np.random.uniform(size=3)
            body_array[body_index][7] = 1.0
    return body_array


def startup(sim_pipe, nr_of_bodies, delta_t, speed):
    """
        Initialise and continuously update a position list.

        Results are sent through a pipe after each update step

        Args:
            sim_pipe (multiprocessing.Pipe): Pipe to send results
            nr_of_bodies (int): Number of bodies to be created and updated.
            delta_t (float): Simulation step width.
            speed (int) : speed of simulation
    """
    bodies = _initialise_bodies(nr_of_bodies, True)
    galaxy.NR_OF_BODIES_FOR_CALC = bodies
    global GALAXY_ONE
    GALAXY_ONE = galaxy.Galaxy()

    for i in range(len(GALAXY_ONE.planets) - 1):
        bodies[i][3] = GALAXY_ONE.planets[i].mass * 0.000000000000002
    bodies[0][3] = 0.05
    while True:
        if sim_pipe.poll():
            message = sim_pipe.recv()
            if isinstance(message, str) and message == END_MESSAGE:
                print('simulation exiting ...')
                sys.exit(0)

        _move_bodies(bodies, delta_t, speed)
        sim_pipe.send(bodies)
