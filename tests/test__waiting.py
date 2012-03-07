from forge import ForgeTestCase
import waiting

class WaitingTest(ForgeTestCase):
    def setUp(self):
        super(WaitingTest, self).setUp()
        self.virtual_time = 0
        self.sleeps_performed = []
        self.predicate_satisfied = False
        self.satisfy_at_time = None
        self.satisfy_after_time = None
        self.forge.replace_with(waiting, "_sleep", self._sleep)
        self.forge.replace_with(waiting, "_time", self._time)
        self.forge.replace_with(waiting.deadlines, "_time", self._time)
    def predicate(self):
        if self.satisfy_at_time is not None and self.satisfy_at_time == self.virtual_time:
            self.predicate_satisfied = True
        if self.satisfy_after_time is not None and self.satisfy_after_time <= self.virtual_time:
            self.predicate_satisfied = True
        return self.predicate_satisfied
    def _sleep(self, delta):
        self.sleeps_performed.append(delta)
        self.virtual_time += delta
        self.assertGreater(1000, len(self.sleeps_performed), "Infinite loop")
    def _time(self):
        return self.virtual_time
    def test__waiting_does_not_expire(self):
        num_tries = 9
        sleep_seconds = 10
        self.satisfy_at_time = num_tries * sleep_seconds
        waiting.wait(self.predicate, sleep_seconds=sleep_seconds, timeout_seconds=(sleep_seconds*num_tries)+1)
    def test__waiting_expires(self):
        with self.assertRaises(waiting.TimeoutExpired):
            waiting.wait(self.predicate, sleep_seconds=3, timeout_seconds=5) # timeout_seconds intentionally not divided by sleep
        self.assertEquals(self.virtual_time, 5)

class AggregationTest(ForgeTestCase):
    def setUp(self):
        super(AggregationTest, self).setUp()
        self.forge.replace(waiting, "_sleep")
        self.predicates = [self.forge.create_wildcard_mock() for i in range(5)]
    def test__wait_any(self):
        for p in self.predicates:
            p().and_return(False)
        waiting._sleep(1)
        self.predicates[0]().and_return(True)
        self.forge.replay()
        waiting.wait(waiting.ANY(self.predicates))
    def test__wait_all(self):
        for iteration in xrange(len(self.predicates) * 2, 0, -1):
            iteration -= 1
            for index, p in reversed(list(enumerate(self.predicates))):
                if index > iteration:
                    continue
                p().and_return(index == iteration)
            if iteration != 0:
                waiting._sleep(1)
        self.forge.replay()
        waiting.wait(waiting.ALL(self.predicates))
