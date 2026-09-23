import time 

def start_timer():
    """
    Start a performance timer.
    """

    return time.perf_counter()

def elapsed_time(start_time):
    """
    Return elapsed time in seconds.
    """
    return round(
        time.perf_counter() - start_time,
        3
    )