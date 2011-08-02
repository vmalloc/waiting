from time import time

class Deadline(object):
    def is_expired(self):
        raise NotImplementedError() # pragma: no cover
class Within(Deadline):
    def __init__(self, seconds):
        super(Within, self).__init__()
        self._deadline = time() + seconds
    def is_expired(self):
        return time() > self._deadline

class Whenever(Deadline):
    def is_expired(self):
        return False

def make_deadline(seconds):
    if seconds is None:
        return Whenever()
    return Within(seconds)
