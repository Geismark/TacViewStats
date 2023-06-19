import time


def get_timer(start=time.perf_counter()):
    return time.perf_counter() - start
