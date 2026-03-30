import unittest

from qa.smoke.exiled_prince_smoke import run_all_scenarios


class ExiledPrinceSmokeTests(unittest.TestCase):
    def test_smoke_scenarios(self) -> None:
        for result in run_all_scenarios():
            with self.subTest(scenario=result.scenario, seed=result.seed):
                self.assertTrue(result.passed, msg=f"[scenario={result.scenario} seed={result.seed}] {result.details}")


if __name__ == "__main__":
    unittest.main()
