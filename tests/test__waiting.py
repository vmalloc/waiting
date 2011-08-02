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
