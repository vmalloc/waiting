import sys

class TimeoutExpired(Exception):
    def __init__(self, timeout_seconds, what):
        super(TimeoutExpired, self).__init__(timeout_seconds, what)
        self._timeout_seconds = timeout_seconds
        self._what = what
    def __str__(self):
        return "Timeout of {0} seconds expired waiting for {1}".format(self._timeout_seconds, self._what)
    def __repr__(self):
        return "{0}: {1}".format(type(self).__name__, self)
    def __unicode__(self):
        return u"Timeout of {0} seconds expired waiting for {1}".format(self._timeout_seconds, self._what)


class IllegalArgumentError(ValueError):
    pass


class NestedStopIteration(Exception):

    def __init__(self, exc_info):
        self.exc_info = exc_info

    def reraise(self):
        if sys.version_info[0] == 3:
            self._reraise3()
        else:
            self._reraise2()

    def _reraise2(self):
        exec("raise self.exc_info[0], self.exc_info[1], self.exc_info[2]")

    def _reraise3(self):
        _, exc_value, tb = self.exc_info
        raise exc_value.with_traceback(tb)
