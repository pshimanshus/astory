import tempfile
import unittest

from scripts.astory_orchestrator import runner
from scripts.astory_orchestrator import state as run_state_mod


def _fresh(tmp, run_id="2026-06-11_demo"):
    state = run_state_mod.new_run_state(run_id)
    run_state_mod.save_state(tmp, run_id, state)
    return state


class AdvanceTests(unittest.TestCase):
    def test_advance_moves_to_next_and_records_completed(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            advanced = runner.advance(tmp, state)
            self.assertEqual(advanced.current_state, "PARSE_CREATIVE_INPUT")
            self.assertIn("INIT_RUN", advanced.completed)
            self.assertEqual(advanced.status, "running")

    def test_advancing_into_hitl_state_sets_awaiting_hitl(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "SELECT_BEST_IDEA"
            advanced = runner.advance(tmp, state)
            self.assertEqual(advanced.current_state, "HITL_IDEA_LOCK")
            self.assertEqual(advanced.status, "awaiting_hitl")

    def test_advance_past_terminal_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "COMPLETE_OR_BLOCKED"
            with self.assertRaises(ValueError):
                runner.advance(tmp, state)


class NextActionTests(unittest.TestCase):
    def test_next_action_for_creative_state(self):
        state = run_state_mod.new_run_state("x")
        state.current_state = "GENERATE_OR_REFINE_IDEAS"
        action = runner.next_action(state)
        self.assertEqual(action["state"], "GENERATE_OR_REFINE_IDEAS")
        self.assertEqual(action["kind"], "creative")
        self.assertFalse(action["halt"])
        self.assertIn("planning/idea_candidates.json", action["produces"])

    def test_next_action_for_hitl_state_halts(self):
        state = run_state_mod.new_run_state("x")
        state.current_state = "HITL_IDEA_LOCK"
        action = runner.next_action(state)
        self.assertTrue(action["halt"])


class HitlTests(unittest.TestCase):
    def test_approved_advances_past_hitl(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "HITL_IDEA_LOCK"
            run_state_mod.save_state(tmp, "2026-06-11_demo", state)
            result = runner.record_hitl(tmp, state, "approved")
            self.assertEqual(result.hitl["HITL_IDEA_LOCK"], "approved")
            self.assertEqual(result.current_state, "GENERATE_STORY_CONCEPT")
            self.assertEqual(result.status, "running")

    def test_rejected_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "HITL_IDEA_LOCK"
            result = runner.record_hitl(tmp, state, "rejected")
            self.assertEqual(result.status, "blocked")
            self.assertEqual(result.current_state, "HITL_IDEA_LOCK")

    def test_record_hitl_on_non_hitl_state_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "GENERATE_OR_REFINE_IDEAS"
            with self.assertRaises(ValueError):
                runner.record_hitl(tmp, state, "approved")


if __name__ == "__main__":
    unittest.main()
