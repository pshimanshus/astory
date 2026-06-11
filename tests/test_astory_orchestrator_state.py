import tempfile
import unittest
from pathlib import Path

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


class RunStatePersistenceTests(unittest.TestCase):
    def test_save_then_load_round_trips(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_id = "2026-06-11_demo"
            state = run_state_mod.new_run_state(run_id)
            path = run_state_mod.save_state(tmp, run_id, state)
            self.assertTrue(path.exists())
            self.assertEqual(
                path,
                Path(tmp).resolve() / "runs" / run_id / "state" / "run_state.json",
            )
            loaded = run_state_mod.load_state(tmp, run_id)
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded.current_state, "INIT_RUN")
            self.assertEqual(loaded.run_id, run_id)

    def test_save_state_writes_sorted_json_with_trailing_newline(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_id = "2026-06-11_demo"
            path = run_state_mod.save_state(
                tmp, run_id, run_state_mod.new_run_state(run_id)
            )
            text = path.read_text()
            self.assertTrue(text.endswith("\n"))
            self.assertLess(text.index('"completed"'), text.index('"current_state"'))

    def test_load_state_returns_none_when_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(run_state_mod.load_state(tmp, "missing_run"))


if __name__ == "__main__":
    unittest.main()
