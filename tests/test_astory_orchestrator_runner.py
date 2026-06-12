import tempfile
import unittest

from scripts.astory_orchestrator import runner
from scripts.astory_orchestrator import state as run_state_mod
from scripts.astory_orchestrator import validate  # noqa: F401


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


PASS_SCOREBOARD = {
    "minimum_required_overall_score": 4.0,
    "candidates": [{"title": "Win", "overall_score": 4.6, "selection_status": "selected"}],
}
FAIL_SCOREBOARD = {
    "minimum_required_overall_score": 4.0,
    "candidates": [{"title": "Weak", "overall_score": 3.4, "selection_status": "selected"}],
}


class IdeaRoomLoopTests(unittest.TestCase):
    def test_passing_scoreboard_proceeds(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "SCORE_IDEAS"
            result = runner.record_idea_round(tmp, state, PASS_SCOREBOARD)
            self.assertEqual(result["decision"], "proceed")
            self.assertEqual(result["round"], 1)
            self.assertEqual(state.retries["idea_room"], 1)

    def test_first_fail_reruns_second_fail_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "SCORE_IDEAS"

            first = runner.record_idea_round(tmp, state, FAIL_SCOREBOARD)
            self.assertEqual(first["decision"], "rerun")
            self.assertEqual(state.retries["idea_room"], 1)

            second = runner.record_idea_round(tmp, state, FAIL_SCOREBOARD)
            self.assertEqual(second["decision"], "blocked")
            self.assertEqual(state.retries["idea_room"], 2)
            self.assertEqual(state.status, "blocked")

    def test_counter_survives_reload(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "SCORE_IDEAS"
            runner.record_idea_round(tmp, state, FAIL_SCOREBOARD)
            reloaded = run_state_mod.load_state(tmp, state.run_id)
            self.assertEqual(reloaded.retries["idea_room"], 1)


class GuardTests(unittest.TestCase):
    def test_idea_round_outside_idea_states_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "INIT_RUN"
            with self.assertRaises(ValueError):
                runner.record_idea_round(tmp, state, PASS_SCOREBOARD)
            self.assertNotIn(runner.IDEA_ROOM_KEY, state.retries)

    def test_idea_round_allowed_in_each_idea_state(self):
        for state_name in runner.IDEA_ROUND_STATES:
            with tempfile.TemporaryDirectory() as tmp:
                state = _fresh(tmp)
                state.current_state = state_name
                result = runner.record_idea_round(tmp, state, FAIL_SCOREBOARD)
                self.assertEqual(result["decision"], "rerun")

    def test_unknown_hitl_decision_raises_and_records_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "HITL_IDEA_LOCK"
            with self.assertRaises(ValueError):
                runner.record_hitl(tmp, state, "maybe")
            self.assertNotIn("HITL_IDEA_LOCK", state.hitl)
            self.assertEqual(state.status, "running")

    def test_rejection_decisions_block(self):
        for decision in ("rejected", "revision_requested"):
            with tempfile.TemporaryDirectory() as tmp:
                state = _fresh(tmp)
                state.current_state = "HITL_IDEA_LOCK"
                result = runner.record_hitl(tmp, state, decision)
                self.assertEqual(result.status, "blocked")


class ProceedAdvancesTests(unittest.TestCase):
    def test_proceed_advances_cursor(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "SCORE_IDEAS"
            result = runner.record_idea_round(tmp, state, PASS_SCOREBOARD)
            self.assertEqual(result["decision"], "proceed")
            self.assertEqual(state.current_state, "SELECT_BEST_IDEA")
            self.assertIn("SCORE_IDEAS", state.completed)

    def test_rerun_keeps_cursor(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "SCORE_IDEAS"
            runner.record_idea_round(tmp, state, FAIL_SCOREBOARD)
            self.assertEqual(state.current_state, "SCORE_IDEAS")

    def test_proceed_persists_advanced_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "SCORE_IDEAS"
            runner.record_idea_round(tmp, state, PASS_SCOREBOARD)
            reloaded = run_state_mod.load_state(tmp, state.run_id)
            self.assertEqual(reloaded.current_state, "SELECT_BEST_IDEA")

    def test_proceed_at_select_best_idea_lands_on_hitl(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "SELECT_BEST_IDEA"
            result = runner.record_idea_round(tmp, state, PASS_SCOREBOARD)
            self.assertEqual(result["decision"], "proceed")
            self.assertEqual(state.current_state, "HITL_IDEA_LOCK")
            self.assertEqual(state.status, "awaiting_hitl")


if __name__ == "__main__":
    unittest.main()
