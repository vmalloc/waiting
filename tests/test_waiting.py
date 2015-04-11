# coding=utf-8
import pytest
import waiting
from waiting.exceptions import IllegalArgumentError, TimeoutExpired


@pytest.mark.parametrize('arg', [
    ([1, 2, 4, 8, 16, 32, 64, 100, 100], (1, 100, 2)),
    ([1, 3, 9, 27, 81, 101, 101, 101], (1, 101, 3)),
    ([1, 2, 4, 8, 16, 32, 64, 128, 201], (1, 201)),
    ([1, 3, 9, 27, 81], (1, None, 3)),
    ([1, 2, 4, 8, 16, 32, 64, 128, 256, 512], (1, None)),
])
def test_exponential_sleep(timeline, arg):
    sleeps, sleep_seconds_arg = arg
    timeline.satisfy_after_time = sum(sleeps)
    waiting.wait(timeline.predicate, sleep_seconds=sleep_seconds_arg)
    assert sleeps == timeline.sleeps_performed

def test_waiting_does_not_expire(timeline):
    num_tries = 9
    sleep_seconds = 10
    timeline.satisfy_at_time = num_tries * sleep_seconds
    waiting.wait(timeline.predicate, sleep_seconds=sleep_seconds, timeout_seconds=(sleep_seconds*num_tries)+1)

def test_waiting_expires(timeline):
    with pytest.raises(waiting.TimeoutExpired):
        waiting.wait(timeline.predicate, sleep_seconds=3, timeout_seconds=5) # timeout_seconds intentionally not divided by sleep
    assert timeline.virtual_time == 5

def test_iterwait_sleep_time(timeline):
    sleep_seconds = 5
    num_sleeps = 7
    timeline.satisfy_at_time = sleep_seconds * num_sleeps
    previous_time = timeline.virtual_time
    for retry in waiting.iterwait(timeline.predicate, sleep_seconds=sleep_seconds):
        assert timeline.virtual_time == previous_time
        previous_time = timeline.virtual_time + sleep_seconds
        timeline.sleep(1.5) # shouldn't affect the sleep
    assert timeline.virtual_time == (num_sleeps * sleep_seconds)

def test__wait_any(predicates, forge, timeline):
    for p in predicates:
        p().and_return(False)
    predicates[0]().and_return(True)
    forge.replay()
    waiting.wait(waiting.ANY(predicates))

def test_wait_any_satisfied_on_start(predicates, forge, timeline):
    for index, p in enumerate(predicates):
        works = (index == 2)
        p().and_return(works)
        if works:
            break
    forge.replay()
    waiting.wait(waiting.ANY(predicates))
    assert timeline.virtual_time == 0

def test_wait_all(predicates, forge, timeline):
    for iteration in range(len(predicates) * 2, 0, -1):
        iteration -= 1
        for index, p in reversed(list(enumerate(predicates))):
            if index > iteration:
                continue
            p().and_return(index == iteration)
    forge.replay()
    waiting.wait(waiting.ALL(predicates))
    assert timeline.virtual_time == ((len(predicates) * 2) - 1)


def test_no_handled_exceptions(timeline):
    with pytest.raises(timeline.FirstTestException):
        waiting.wait(timeline.raising_predicate)

def test_another_handled_exceptions(timeline):
    with pytest.raises(timeline.SecondTestException):
        waiting.wait(timeline.raising_two_exceptions_predicate,
                     expected_exceptions=timeline.FirstTestException)

def test_one_class(timeline):
    timeline.satisfy_at_time = 3
    waiting.wait(timeline.raising_predicate, expected_exceptions=timeline.FirstTestException)
    assert timeline.virtual_time == 3

def test_correct_tuple(timeline):
    timeline.satisfy_at_time = 3
    waiting.wait(timeline.raising_two_exceptions_predicate,
                 expected_exceptions=(timeline.FirstTestException, timeline.SecondTestException))
    assert timeline.virtual_time == 3

def test_none(timeline):
    with pytest.raises(IllegalArgumentError):
        waiting.wait(timeline.raising_predicate, expected_exceptions=None)

def test_non_tuple(timeline):
    with pytest.raises(IllegalArgumentError):
        waiting.wait(timeline.raising_predicate, expected_exceptions='Not a tuple')


def test_unicode_logging():
    unicode_string = u'symbols 올 д'
    timeout = 3
    instance = TimeoutExpired(timeout, unicode_string)
    assert u'{0}'.format(instance) == u'Timeout of {0} seconds expired waiting for {1}'.format(timeout, unicode_string)
