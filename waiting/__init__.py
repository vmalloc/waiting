from .__version__ import __version__
from time import sleep as _sleep
from .deadlines import make_deadline as _make_deadline
from .exceptions import TimeoutExpired

def wait(predicate, timeout_seconds=None, sleep_seconds=1):
    while True:
        timeout = _make_deadline(timeout_seconds)
        result = predicate()
        if result:
            return result
        if timeout.is_expired():
            raise TimeoutExpired()
        _sleep(sleep_seconds)
