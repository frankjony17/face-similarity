
import os


def get_workers():
    """
    Get values from operating system environment.
    Returns:
        (int) Value of the environment variable.
    """
    try:
        worker = os.environ["WORKERS"]
    except KeyError:
        worker = 3
    return worker


def get_threads():
    """
    Get values from operating system environment.
    Returns:
        (int) Value of the environment variable.
    """
    try:
        thread = os.environ["THREADS"]
    except KeyError:
        thread = 2
    return thread


bind = "0.0.0.0:9000"
workers = get_workers()
timeout = 3 * 60  # 3 minutes
keepalive = 24 * 60 * 60  # 1 day
capture_output = True
worker_class = 'gthread'
threads = get_threads()
