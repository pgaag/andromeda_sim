import sys

import numpy as np
import scipy.constants
import numba
from numba import prange, jit, types
from numba.typed import List, Dict
from multiprocessing import cpu_count, Process

from connection_config import PORT, IP_WORKER
from distributed_queue import TaskManager

"""
Port: 34705
##### Laeuft im Cluster und ist der Arbeiter(engl. worker) der die Berechnung durchfuehrt.#####

Der Worker muss die IP-Adresse und den Port kennen, unter dem er den TaskManager und somit die beiden Queues 
erreichen kann. Auf jedem Rechner im Cluster sollte ein Worker gestartet werden. """


@jit(parallel=True, nopython=True)
def calc_acc(index, keys, values):
    force = np.zeros(3, dtype=np.float64)
    n = len(keys)
    for i in prange(n):
        # keys = [1,2,3,4,5]
        # index = 5
        # values = [1 : (np.array(pos_x, pos_y, pos_z, mass), 2 : (np.array(pos_x, pos_y, pos_z, mass), ..............]
        if i != index:
            pos_idx = np.asarray(values[index][:3], dtype=np.float64)
            target_idx = np.asarray(values[i][:3], dtype=np.float64)
            distance = target_idx - pos_idx
            distance_abs = np.linalg.norm(distance)
            temp = 6.672e-11 * ((values[index][3] * values[i][3]) / distance_abs ** 3) * distance
            force += temp
    res = force / values[index][3]
    return res


def __worker_function(job_queue, result_queue):
    while True:
        job = job_queue.get()
        job_items = dict(job.items())
        job_keys = list(job.keys())
        all_planets = job_items[job_keys[0]]
        planet_indexes = List(all_planets.keys())
        keys_as_array = [x.split('-') for x in job_keys]
        planets_numba_dict = Dict.empty(key_type=types.int64, value_type=types.float64[::])
        for key, value in all_planets.items():
            planets_numba_dict[key] = all_planets[key]
        from_index = int(keys_as_array[0][0])
        to_index = int(keys_as_array[0][1])
        for i in range(from_index, min_num(to_index, len(planet_indexes))):
            res = calc_acc(i, planet_indexes, planets_numba_dict)
            result_queue.put((i, res))
        job_queue.task_done()


def min_num(a, b):
    if a < b:
        return a
    return b


def __start_workers(m):
    job_queue = m.get_job_queue()
    result_queue = m.get_result_queue()
    nr_of_processes = cpu_count()
    processes = [Process(target=__worker_function,
                         args=(job_queue, result_queue))
                 for i in range(nr_of_processes)]
    for p in processes:
        p.start()
    return nr_of_processes


if __name__ == '__main__':
    server_ip = IP_WORKER
    server_socket = int(PORT)
    print(IP_WORKER, PORT)
    TaskManager.register('get_job_queue')
    TaskManager.register('get_result_queue')
    m = TaskManager(address=(server_ip, server_socket), authkey=b'secret')
    m.connect()
    nr_of_processes = __start_workers(m)
    print(nr_of_processes, 'workers started')
