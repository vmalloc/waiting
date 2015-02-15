try:
    from flux import current_timeline as time_module
except ImportError:
    import time as time_module


class Deadline(object):

    def is_expired(self):
        raise NotImplementedError()  # pragma: no cover

    def get_num_seconds_remaining(self):
        return None


class Within(Deadline):

    def __init__(self, seconds):
        super(Within, self).__init__()
        self._deadline = time_module.time() + seconds

    def is_expired(self):
        return time_module.time() >= self._deadline

    def get_num_seconds_remaining(self):
        return self._deadline - time_module.time()


class Whenever(Deadline):

    def is_expired(self):
        return False


def make_deadline(seconds):
    if seconds is None:
        return Whenever()
    return Within(seconds)
