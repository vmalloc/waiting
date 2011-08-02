Overview
--------
*waiting* is a small library for waiting for stuff to happen. It basically waits for a function to return **True**, in various modes.

Usage
-----

The most basic usage is when you have a function you want to wait for::

 >>> predicate = lambda : True

Waiting forever is very simple::

 >>> from waiting import wait
 >>> wait(predicate)

A *timeout* parameter can also be specified::

 >>> wait(predicate, timeout_seconds=10.5)

When a timeout expires without the predicate being fullfilled, an exception is thrown::

 >>> wait(lambda : False, timeout_seconds=0) # doctest: +IGNORE_EXCEPTION_DETAIL
 Traceback (most recent call last):
  ...
 TimeoutExpired
 
 
Sleeping polls the predicate at a certain interval (by default 1 second). The interval can be changed with the *sleep_seconds* argument::

 >>> wait(predicate, sleep_seconds=20)
