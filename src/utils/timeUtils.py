import time
from datetime import datetime


def get_timer(start=time.perf_counter()):
    return time.perf_counter() - start


def get_date_time():
    now = datetime.now()
    date_formatted = now.strftime("%d%m%Y")
    time_formatted = now.strftime("%H%M%S")
    return date_formatted, time_formatted


if __name__ == "__main__":
    print(get_date_time())
