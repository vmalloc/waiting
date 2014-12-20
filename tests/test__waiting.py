from forge import ForgeTestCase
from nose.tools import assert_raises, eq_
import waiting
from waiting.exceptions import IllegalArgumentError


class VirtualTimeTest(ForgeTestCase):
    def setUp(self):
        super(VirtualTimeTest, self).setUp()
        self.virtual_time = 0
        self.sleeps_performed = []
        self.predicate_satisfied = False
        self.satisfy_at_time = None
        self.satisfy_after_time = None
        self.forge.replace_with(waiting.time_module, "sleep", self._sleep)
        self.forge.replace_with(waiting.time_module, "time", self._time)
        self.forge.replace_with(waiting.deadlines.time_module, "time", self._time)
    def _sleep(self, delta):
        self.sleeps_performed.append(delta)
        self.virtual_time += delta
        self.assertGreater(1000, len(self.sleeps_performed), "Infinite loop")
    def _time(self):
        return self.virtual_time
    def predicate(self):
        if self.satisfy_at_time is not None and self.satisfy_at_time == self.virtual_time:
            self.predicate_satisfied = True
        if self.satisfy_after_time is not None and self.satisfy_after_time <= self.virtual_time:
            self.predicate_satisfied = True
        return self.predicate_satisfied

class ExponentialSleepTest(VirtualTimeTest):
    def test__exponential_sleep_start_end_multiplier(self):
        self._test__exponential_sleep([1, 2, 4, 8, 16, 32, 64, 100, 100], (1, 100, 2))
    def test__exponential_sleep_start_end_multiplier_3(self):
        self._test__exponential_sleep([1, 3, 9, 27, 81, 101, 101, 101], (1, 101, 3))
    def test__exponential_sleep_start_end_no_multiplier(self):
        self._test__exponential_sleep([1, 2, 4, 8, 16, 32, 64, 128, 201], (1, 201))
    def test__exponential_sleep_start_end_no_end_with_multiplier(self):
        self._test__exponential_sleep([1, 3, 9, 27, 81], (1, None, 3))
    def test__exponential_sleep_start_end_no_end_no_multiplier(self):
        self._test__exponential_sleep([1, 2, 4, 8, 16, 32, 64, 128, 256, 512], (1, None))
    def _test__exponential_sleep(self, sleeps, sleep_seconds_arg):
        self.satisfy_after_time = sum(sleeps)
        waiting.wait(self.predicate, sleep_seconds=sleep_seconds_arg)
        self.assertEquals(sleeps, self.sleeps_performed)

class WaitingTest(VirtualTimeTest):
    def test__waiting_does_not_expire(self):
        num_tries = 9
        sleep_seconds = 10
        self.satisfy_at_time = num_tries * sleep_seconds
        waiting.wait(self.predicate, sleep_seconds=sleep_seconds, timeout_seconds=(sleep_seconds*num_tries)+1)
    def test__waiting_expires(self):
        with self.assertRaises(waiting.TimeoutExpired):
            waiting.wait(self.predicate, sleep_seconds=3, timeout_seconds=5) # timeout_seconds intentionally not divided by sleep
        self.assertEquals(self.virtual_time, 5)
    def test__iterwait_sleep_time(self):
        sleep_seconds = 5
        num_sleeps = 7
        self.satisfy_at_time = sleep_seconds * num_sleeps
        previous_time = self.virtual_time
        for retry in waiting.iterwait(self.predicate, sleep_seconds=sleep_seconds):
            self.assertEquals(self.virtual_time, previous_time)
            previous_time = self.virtual_time + sleep_seconds
            self._sleep(1.5) # shouldn't affect the sleep
        self.assertEquals(self.virtual_time, num_sleeps * sleep_seconds)

class AggregationTest(VirtualTimeTest):
    def setUp(self):
        super(AggregationTest, self).setUp()
        self.predicates = [self.forge.create_wildcard_mock() for i in range(5)]
    def test__wait_any(self):
        for p in self.predicates:
            p().and_return(False)
        self.predicates[0]().and_return(True)
        self.forge.replay()
        waiting.wait(waiting.ANY(self.predicates))
    def test__wait_any_satisfied_on_start(self):
        for index, p in enumerate(self.predicates):
            works = (index == 2)
            p().and_return(works)
            if works:
                break
        self.forge.replay()
        waiting.wait(waiting.ANY(self.predicates))
        self.assertEquals(self.virtual_time, 0)
    def test__wait_all(self):
        for iteration in range(len(self.predicates) * 2, 0, -1):
            iteration -= 1
            for index, p in reversed(list(enumerate(self.predicates))):
                if index > iteration:
                    continue
                p().and_return(index == iteration)
        self.forge.replay()
        waiting.wait(waiting.ALL(self.predicates))
        self.assertEquals(self.virtual_time, len(self.predicates) * 2 - 1)


class FirstTestException(Exception):
    pass


class SecondTestException(Exception):
    pass


class ExpectedExceptionsTest(VirtualTimeTest):
    def raising_predicate(self):
        if self.virtual_time == 0:
            raise FirstTestException()
        return self.predicate()

    def raising_two_exceptions_predicate(self):
        if self.virtual_time == 1:
            raise SecondTestException()
        return self.raising_predicate()

    def test_no_handled_exceptions(self):
        assert_raises(FirstTestException, waiting.wait, self.raising_predicate)

    def test_another_handled_exceptions(self):
        assert_raises(SecondTestException, waiting.wait, self.raising_two_exceptions_predicate,
                      expected_exceptions=FirstTestException)

    def test_one_class(self):
        self.satisfy_at_time = 3
        waiting.wait(self.raising_predicate, expected_exceptions=FirstTestException)
        eq_(self.virtual_time, 3)

    def test_correct_tuple(self):
        self.satisfy_at_time = 3
        waiting.wait(self.raising_two_exceptions_predicate,
                     expected_exceptions=(FirstTestException, SecondTestException))
        eq_(self.virtual_time, 3)

    def test_none(self):
        assert_raises(IllegalArgumentError, waiting.wait, self.raising_predicate, expected_exceptions=None)

    def test_non_tuple(self):
        assert_raises(IllegalArgumentError, waiting.wait, self.raising_predicate, expected_exceptions='Not a tuple')
