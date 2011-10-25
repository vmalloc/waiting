from forge import ForgeTestCase
import waiting

class SleepTest(ForgeTestCase):
    def setUp(self):
        super(SleepTest, self).setUp()
        self.forge.replace(waiting, "_sleep")
        self.predicate = self.forge.create_wildcard_mock()
    def test__sleep_between_tries_default(self):
        self._test__sleep_between_tries()
    def test__sleep_between_tries_different_sleep_value(self):
        self._test__sleep_between_tries(3.4)
    def _test__sleep_between_tries(self, sleep_seconds=None):
        for i in range(5):
            self.predicate().and_return(False)
            waiting._sleep(1 if sleep_seconds is None else sleep_seconds)
        self.predicate().and_return(True)
        self.forge.replay()
        waiting.wait(self.predicate, **(dict(sleep_seconds=sleep_seconds) if sleep_seconds is not None else {}))


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
