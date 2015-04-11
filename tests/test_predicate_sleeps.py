import waiting

import pytest


@pytest.mark.parametrize('do_sleep', [True, False])
def test_predicate_sleeps_coelesce(timeline, do_sleep):
    timeline.predicate_sleep = 0.5 if do_sleep else 0
    sleep_seconds = 2
    expected_sleep = sleep_seconds - timeline.predicate_sleep
    timeline.satisfy_after_time = 10
    waiting.wait(timeline.predicate, sleep_seconds=2)
    assert timeline.sleeps_performed == [expected_sleep for i in range(5)]
