import unittest
from run_interface import ARMS, oracle, scenarios, step


def facts(**changes):
    return {"permission": "GRANTED", "permit_object": "A", "fresh": True,
            "recovery": "RECOVERY_ONLY", "recovery_object": "A", "version": 1, **changes}


class ExecutionTests(unittest.TestCase):
    def event(self, kind="move", dx=0.1, latest=None):
        return {"tick": 0, "action": {"kind": kind, "object": "A", "dx": dx},
                "decision": facts(), "execution": latest or facts()}

    def test_revocation_after_selection(self):
        event = self.event(latest=facts(permission="DENIED", version=2))
        start, out = step("start_only", {"A": 0.2, "B": 0.0}, event)
        self.assertAlmostEqual(start["A"], 0.3)
        self.assertIn("task_permission", out["execution_errors"])
        full, out = step("full_typed", {"A": 0.2, "B": 0.0}, event)
        self.assertEqual(full["A"], 0.2)
        self.assertFalse(out["executed"])

    def test_recovery_authority_and_freshness_races(self):
        for changed in (facts(recovery="UNKNOWN"), facts(fresh=False), facts(recovery_object="B")):
            event = self.event("recover", -0.1, changed)
            _, start = step("start_only", {"A": 0.6, "B": 0.0}, event)
            after, full = step("full_typed", {"A": 0.6, "B": 0.0}, event)
            self.assertTrue(start["execution_errors"])
            self.assertFalse(full["executed"])
            self.assertEqual(after["A"], 0.6)

    def test_oracle_uses_true_state_for_completion(self):
        action = {"kind": "complete", "object": "B", "dx": 0}
        self.assertEqual(oracle(action, facts(), {"A": 1.1, "B": 0}), ["false_completion"])
        self.assertEqual(oracle(action, facts(), {"A": 0, "B": 1.0}), [])

    def test_legal_actions_are_not_all_stopped(self):
        state = {"A": 0.7, "B": 0.0}
        for event in next(scenarios("dev"))["events"][:3]:
            state, outcome = step("full_typed", state, event)
            self.assertTrue(outcome["executed"])
            self.assertTrue(outcome["legal_opportunity"])
        self.assertGreaterEqual(state["A"], 1.0 - 1e-9)

    def test_same_version_observation_change(self):
        event = self.event(latest=facts(fresh=False))
        self.assertEqual(event["decision"]["version"], event["execution"]["version"])
        _, outcome = step("full_typed", {"A": 0.2, "B": 0.0}, event)
        self.assertFalse(outcome["executed"])


if __name__ == "__main__":
    unittest.main()
