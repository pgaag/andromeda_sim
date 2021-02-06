import multiprocessing
import sys
import time
import math

import numpy as np

from galaxy.galaxy_renderer.connection_config import IP_MASTER, PORT
from galaxy.galaxy_renderer.distributed_queue import TaskManager
from galaxy.galaxy_renderer.simulation_constants import END_MESSAGE
import galaxy.galaxy_calc as galaxy


__FPS = 60


def _move_bodies(bodies, andromeda, manager, delta_t, speed):
    for i in range(speed):
        update_all_accelerations(andromeda, manager)
        andromeda.calc_all_next_positions_and_velocities(delta_t)
    for j in range(len(bodies)):
        for i in range(3):
            bodies[j][i] = (andromeda.planets[j].position[i] / galaxy.DISTANCE_SUN) - 1
    time.sleep(1 / __FPS)
    return bodies


def update_all_accelerations(andromeda, manager):
    result_list = _calculate_accelerations_distributed(andromeda, manager)
    for acceleration_data in result_list:
        andromeda.update_acceleration_for_plaent_with_index(acceleration_data[0], acceleration_data[1])


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


def create_argument_list_for_acc_calc(andromeda, in_list):
    planet_list = andromeda.extract_all_planets_as_position_and_mass_dictionary()
    num_of_planets = len(planet_list.keys())
    cores = multiprocessing.cpu_count()
    portion_size = math.ceil(num_of_planets / cores)
    to_index = portion_size
    from_index = 0
    for i in range(cores + 5):
        if i+1 >= cores:
            to_index = num_of_planets - 1
        planet_dict = dict()
        job_key = ""
        job_key += str(from_index)
        job_key += "-"
        job_key += str(to_index)
        planet_dict[job_key] = planet_list
        from_index += portion_size
        to_index += portion_size
        in_list.append(planet_dict)


def min_num(a, b):
    if a < b:
        return a
    return b


def _calculate_accelerations_distributed(andromeda, master):
    # get queues
    job_queue = master.get_job_queue()
    result_queue = master.get_result_queue()

    # create list of tasks
    in_list = []
    result_list = []
    create_argument_list_for_acc_calc(andromeda, in_list)

    # put tasks in job queue
    for task in in_list:
        job_queue.put(task)

    # wait for tasks to finish
    job_queue.join()

    # get the new planets from the queue and collect them in a new list
    while not result_queue.empty():
        result_list.append(result_queue.get())

    return result_list


def startup(sim_pipe, nr_of_bodies, delta_t, speed):
    server_ip = IP_MASTER
    server_socket = int(PORT)
    TaskManager.register('get_job_queue')
    TaskManager.register('get_result_queue')
    m = TaskManager(address=(server_ip, server_socket), authkey=b'secret')
    m.connect()

    bodies = _initialise_bodies(nr_of_bodies, True)
    andromeda = galaxy.Galaxy(len(bodies))
    mass_to_size_scale_factor = 0.000000000000002
    for i in range(nr_of_bodies - 1):
        bodies[i][3] = andromeda.planets[i].mass * mass_to_size_scale_factor  # Scale size with mass
    bodies[0][3] = 0.005

    while True:
        if sim_pipe.poll():
            message = sim_pipe.recv()
            if isinstance(message, str) and message == END_MESSAGE:
                print('simulation exiting ...')
                sys.exit(0)

        bodies = _move_bodies(bodies, andromeda, m, delta_t, speed)
        sim_pipe.send(bodies)
