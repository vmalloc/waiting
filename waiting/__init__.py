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
