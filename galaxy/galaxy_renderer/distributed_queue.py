from __future__ import print_function

from multiprocessing import JoinableQueue, Queue
from multiprocessing.managers import SyncManager

from connection_config import PORT


class TaskManager(SyncManager):
    pass


if __name__ == '__main__':
    from sys import argv, exit
    master_socket = int(PORT)
    task_queue = JoinableQueue()
    result_queue = Queue()
    TaskManager.register('get_job_queue', callable=lambda: task_queue)
    TaskManager.register('get_result_queue', callable=lambda: result_queue)
    m = TaskManager(address=('', master_socket), authkey=b'secret')
    print('starting queue server, socket', master_socket)
    m.get_server().serve_forever()
