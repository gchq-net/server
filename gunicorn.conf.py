import multiprocessing

from prometheus_client import multiprocess

preload_app = True
max_requests = 1000
max_requests_jitter = 50
workers = multiprocessing.cpu_count() * 2 + 1

def child_exit(server, worker):  # type: ignore  # noqa
    multiprocess.mark_process_dead(worker.pid)
