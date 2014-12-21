import inspect

from .__version__ import __version__
from contextlib import contextmanager

try:
    from flux import current_timeline as time_module
except ImportError:
    import time as time_module
from .deadlines import make_deadline as _make_deadline
from .exceptions import TimeoutExpired, IllegalArgumentError


def wait(*args, **kwargs):
    result = _Result()
    for x in iterwait(result=result, *args, **kwargs):
        pass
    return result.result

def iterwait(predicate, timeout_seconds=None, sleep_seconds=1, result=None, waiting_for=None,
             expected_exceptions=()):

    if not isinstance(expected_exceptions, tuple) and not (isinstance(expected_exceptions, type)
                                                           and issubclass(expected_exceptions, Exception)):
        raise IllegalArgumentError('expected_exceptions should be tuple or Exception subclass')
    timeout = _make_deadline(timeout_seconds)
    if result is None:
        result = _Result()
    if waiting_for is None:
        waiting_for = str(predicate)
    sleep_generator = _get_sleep_generator(timeout, sleep_seconds)
    while True:
        try:
            result.result = predicate()
        except expected_exceptions:
            pass
        if result.result:
            return
        if timeout.is_expired():
            raise TimeoutExpired(timeout_seconds, waiting_for)
        with _end_sleeping(next(sleep_generator)):
            yield

@contextmanager
def _end_sleeping(total_seconds):
    deadline = _make_deadline(total_seconds)
    yield
    time_module.sleep(max(0, deadline.get_num_seconds_remaining()))

class _Result(object):
    result = None

def _get_sleep_generator(timeout, sleep_seconds):
    if type(sleep_seconds) not in (tuple, list):
        sleep_seconds = (sleep_seconds, sleep_seconds, 1)
    if len(sleep_seconds) <= 2:
        sleep_seconds = (sleep_seconds[0], sleep_seconds[1], 2)
    elif len(sleep_seconds) < 2:
        sleep_seconds = (sleep_seconds[0], None, 2)
    current_sleep, end_sleep, multiplier = sleep_seconds
    while True:
        time_remaining = timeout.get_num_seconds_remaining()
        if time_remaining is not None:
            current_sleep = min(time_remaining, current_sleep)
        current_sleep = max(0, current_sleep)
        yield current_sleep
        current_sleep *= multiplier
        if end_sleep is not None:
            current_sleep = min(end_sleep, current_sleep)

class Aggregate(object):
    def __init__(self, predicates):
        super(Aggregate, self).__init__()
        self.predicates = list(predicates)
class ANY(Aggregate):
    def __call__(self):
        return any(p() for p in self.predicates)
class ALL(Aggregate):
    def __call__(self):
        for index in range(len(self.predicates), 0, -1):
            index -= 1
            if self.predicates[index]():
                self.predicates.pop(index)
        return not self.predicates
