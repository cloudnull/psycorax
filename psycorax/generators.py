import time
import random
import string


def manager_list(b_l=None):
    """
    OPTIONAL Variable :
    bl = 'Base List'

    Create a shared list using multiprocessing Managers
    If you use the "bl" variable you can specify a prebuilt list
    The default is that bl=None
    """
    import multiprocessing
    manager = multiprocessing.Manager()
    if b_l:
        managed_dictionary = manager.list(b_l)
    else:
        managed_dictionary = manager.list()
    return managed_dictionary


def manager_dict(b_d=None):
    """
    OPTIONAL Variable :
    bd = 'Base Dictionary'

    Create a shared dictionary using multiprocessing Managers
    If you use the "bd" variable you can specify a prebuilt dict
    the default is that bd=None
    """
    import multiprocessing
    manager = multiprocessing.Manager()
    if b_d:
        managed_dictionary = manager.dict(b_d)
    else:
        managed_dictionary = manager.dict()
    return managed_dictionary


def manager_queue(iters):
    """
    iters="The iterable variables"

    Uses a manager Queue, from multiprocessing.
    All jobs will be added to the queue for processing.
    """
    import multiprocessing
    manager = multiprocessing.Manager()
    worker_q = manager.Queue()
    for d_t in iters:
        worker_q.put(d_t)
    return worker_q


def worker_proc(job_action):
    """
    This method Requires the "job_action" which is a list of tuples which
    resembles something like this :

    job_action = [(method, node)]

    The Threads are all made active prior to them being joined.
    """
    import multiprocessing

    # prep the List for actions
    processes = []

    # Enable for multiprocessing Debug
    #multiprocessing.log_to_stderr(level='DEBUG')

    proc_name = 'PsycoRax-%s-Worker' % str(job_action).split()[2]
    processes = []
    for job in job_action:
        processes.append(multiprocessing.Process(name=proc_name,
                                                 target=job[0],
                                                 args=(job[1],),)
                         )

    for proc_j in processes:
        proc_j.start()

    for proc_j in processes:
        proc_j.join()


def retryloop(attempts, timeout=None, delay=None, backoff=1):
    """
    Enter the amount of retries you want to perform.
    The timeout allows the application to quit on "X".
    delay allows the loop to wait on fail. Useful for making REST calls.

    Example:
        Function for retring an action.
        for retry in retryloop(attempts=10, timeout=30, delay=1, backoff=1):
            something
            if somecondition:
                retry()
    """
    starttime = time.time()
    success = set()
    for _ in range(attempts):
        success.add(True)
        yield success.clear
        if success:
            return
        duration = time.time() - starttime
        if timeout is not None and duration > timeout:
            break
        if delay:
            time.sleep(delay)
            delay = delay * backoff
    raise RetryError


def rand_string(length=9, chr_set=string.ascii_uppercase):
    """
    Generate a Random string
    """
    output = ''
    for _ in range(length):
        output += random.choice(chr_set)
    return output


# ACTIVE STATE retry loop
# http://code.activestate.com/recipes/578163-retry-loop/
class RetryError(Exception):
    pass
