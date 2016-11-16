Overview
--------
*waiting* is a small library for waiting for stuff to happen. It basically waits for a function to return **True**, in various modes.

*Waiting* is compatible with `flux <http://flux.readthedocs.org>`_ for simulated timelines.

Usage
-----

The most basic usage is when you have a function you want to wait for::

 >>> predicate = lambda : True

Waiting forever is very simple::

 >>> from waiting import wait, TimeoutExpired
 >>> wait(predicate)
 True

If your predicate returns a value, it will be returned as the result of wait()::

 >>> result = object()
 >>> wait(lambda: result) is result
 True

A *timeout* parameter can also be specified::

 >>> wait(predicate, timeout_seconds=10.5)
 True

When a timeout expires without the predicate being fullfilled, an exception is thrown::


 >>> try:
 ...     wait(lambda : False, timeout_seconds=0)
 ... except TimeoutExpired:
 ...     # expired!
 ...     pass
 ... else:
 ...     assert False


Sleeping polls the predicate at a certain interval (by default 1 second). The interval can be changed with the *sleep_seconds* argument::

 >>> wait(predicate, sleep_seconds=20)
 True

When waiting for multiple predicates, *waiting* provides two simple facilities to help aggregate them: **ANY** and **ALL**. They resemble Python's built-in *any()* and *all()*, except that they don't call a predicate once it has been satisfied (this is useful when the predicates are inefficient and take time to complete)::

 >>> from waiting import wait, ANY, ALL
 >>> wait(ANY([predicate, predicate]))
 True
 >>> wait(ALL([predicate, predicate]))
 True

TimeoutExpired exceptions, by default, don't tell you much about what didn't happen that you were expecting. To fix that, use the *waiting_for* argument::

 >>> try:
 ...     wait(lambda : False, timeout_seconds=0, waiting_for="something that will never happen") #doctest: +ELLIPSIS
 ... except TimeoutExpired as e:
 ...     print(e)
 Timeout of 0 seconds expired waiting for something that will never happen

Exponential backoff is supported for the sleep interval::

 >>> from waiting import wait
 >>> wait(predicate, sleep_seconds=(1, 100)) # sleep 1, 2, 4, 8, 16, 32, 64, 100, 100, ....
 True
 >>> wait(predicate, sleep_seconds=(1, 100, 3)) # sleep 1, 3, 9, 27, 81, 100, 100, 100 ....
 True
 >>> wait(predicate, sleep_seconds=(1, None)) # sleep 1, 2, 4, 6, .... (infinity)
 True
 >>> wait(predicate, sleep_seconds=(1, None, 4)) # sleep 1, 4, 16, 64, ... (infinity)
 True

If your predicate might raise certain exceptions you wish to ignore, you may use ``expected_exceptions`` to ignore them::

 >>> from waiting import wait
 >>> wait(predicate, expected_exceptions=ValueError)
 True
 >>> wait(predicate, expected_exceptions=(ValueError, AttributeError))
 True

If you'd like to maintain updates while waiting for a predicate to complete, you may use ``on_poll`` to pass a function to perform some behavior after every sleep. By default, this is a no-op.

 >>> import logging
 >>> from waiting import wait
 >>> try:
 ...    wait(lambda: False, timeout_seconds=5,               # Timeout after 5 seconds
 ...          on_poll=lambda: logging.warn("Waiting...")) # Log "Waiting..." six times.
 ... except TimeoutExpired:
 ...    pass
 ... else:
 ...    assert False
