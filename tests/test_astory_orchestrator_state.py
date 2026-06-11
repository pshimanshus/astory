import unittest

from scripts.astory_orchestrator import state as run_state_mod


class RunStateModelTests(unittest.TestCase):
    def test_new_run_state_starts_at_init_run(self):
        state = run_state_mod.new_run_state("2026-06-11_demo")
        self.assertEqual(state.current_state, "INIT_RUN")
        self.assertEqual(state.status, "running")
        self.assertEqual(state.completed, [])
        self.assertTrue(state.created_at)
        self.assertEqual(state.created_at, state.updated_at)

    def test_to_dict_from_dict_round_trip(self):
        state = run_state_mod.new_run_state("2026-06-11_demo")
        state.completed = ["INIT_RUN"]
        state.current_state = "PARSE_CREATIVE_INPUT"
        state.gates = {"agent_assignment": "pending"}
        state.retries = {"idea_room": 1}
        restored = run_state_mod.from_dict(run_state_mod.to_dict(state))
        self.assertEqual(restored.current_state, "PARSE_CREATIVE_INPUT")
        self.assertEqual(restored.completed, ["INIT_RUN"])
        self.assertEqual(restored.gates, {"agent_assignment": "pending"})
        self.assertEqual(restored.retries, {"idea_room": 1})

    def test_from_dict_rejects_unknown_current_state(self):
        bad = run_state_mod.to_dict(run_state_mod.new_run_state("x"))
        bad["current_state"] = "NOT_A_STATE"
        with self.assertRaises(ValueError):
            run_state_mod.from_dict(bad)

    def test_from_dict_rejects_invalid_status(self):
        bad = run_state_mod.to_dict(run_state_mod.new_run_state("x"))
        bad["status"] = "exploding"
        with self.assertRaises(ValueError):
            run_state_mod.from_dict(bad)

    def test_from_dict_requires_run_id(self):
        bad = run_state_mod.to_dict(run_state_mod.new_run_state("x"))
        bad["run_id"] = ""
        with self.assertRaises(ValueError):
            run_state_mod.from_dict(bad)


if __name__ == "__main__":
    unittest.main()
