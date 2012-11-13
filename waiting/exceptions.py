class TimeoutExpired(Exception):
    def __init__(self, timeout_seconds, msg):
        super(TimeoutExpired, self).__init__(timeout_seconds, msg)
        self._timeout_seconds = timeout_seconds
        self._msg = msg
    def __str__(self):
        return "Timeout of {0} seconds expired waiting for {1}".format(*self.args)
    def __repr__(self):
        return "{0}: {1}".format(type(self).__name__, self)

