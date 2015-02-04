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
