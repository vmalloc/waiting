from .__version__ import __version__
from contextlib import contextmanager
from time import sleep as _sleep
from time import time as _time
from .deadlines import make_deadline as _make_deadline
from .exceptions import TimeoutExpired

def wait(*args, **kwargs):
    result = _Result()
    for x in iterwait(result=result, *args, **kwargs):
        pass
    return result.result

def iterwait(predicate, timeout_seconds=None, sleep_seconds=1, result=None):
    timeout = _make_deadline(timeout_seconds)
    if result is None:
        result = _Result()
    while True:
        result.result = predicate()
        if result.result:
            return
        if timeout.is_expired():
            raise TimeoutExpired()
        with _end_sleeping(_get_sleep_time(timeout, sleep_seconds)):
            yield

@contextmanager
def _end_sleeping(total_seconds):
    deadline = _make_deadline(total_seconds)
    yield
    _sleep(max(0, deadline.get_num_seconds_remaining()))

class _Result(object):
    result = None

def _get_sleep_time(timeout, sleep_seconds):
    time_remaining = timeout.get_num_seconds_remaining()
    assert time_remaining != 0
    if time_remaining is not None:
        sleep_seconds = min(time_remaining, sleep_seconds)
    return max(0, sleep_seconds)

class Aggregate(object):
    def __init__(self, predicates):
        super(Aggregate, self).__init__()
        self.predicates = list(predicates)
class ANY(Aggregate):
    def __call__(self):
        return any(p() for p in self.predicates)
class ALL(Aggregate):
    def __call__(self):
        for index in xrange(len(self.predicates), 0, -1):
            index -= 1
            if self.predicates[index]():
                self.predicates.pop(index)
        return not self.predicates
