from time import time as _time

class Deadline(object):
    def is_expired(self):
        raise NotImplementedError() # pragma: no cover
    def get_num_seconds_remaining(self):
        return None
class Within(Deadline):
    def __init__(self, seconds):
        super(Within, self).__init__()
        self._deadline = _time() + seconds
    def is_expired(self):
        return _time() >= self._deadline
    def get_num_seconds_remaining(self):
        return self._deadline - _time()

class Whenever(Deadline):
    def is_expired(self):
        return False

def make_deadline(seconds):
    if seconds is None:
        return Whenever()
    return Within(seconds)
