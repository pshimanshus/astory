import tempfile
import unittest
from pathlib import Path

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
            state.current_state = "CREATE_SCENE_LANDING_PREVIEW"
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


class InvalidScoreboardTests(unittest.TestCase):
    def test_malformed_scoreboard_is_invalid_not_low_score(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "SCORE_IDEAS"
            result = runner.record_idea_round(tmp, state, {})
            self.assertEqual(result["decision"], "invalid")
            self.assertTrue(result["problems"])

    def test_invalid_round_consumes_no_retry_and_does_not_mutate(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "SCORE_IDEAS"
            runner.record_idea_round(tmp, state, FAIL_SCOREBOARD)  # round 1
            result = runner.record_idea_round(tmp, state, {"candidates": []})
            self.assertEqual(result["decision"], "invalid")
            self.assertEqual(result["round"], 1)
            self.assertEqual(state.retries["idea_room"], 1)
            self.assertEqual(state.current_state, "SCORE_IDEAS")
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

    def test_proceed_at_select_best_idea_advances_to_scene_preview(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "SELECT_BEST_IDEA"
            result = runner.record_idea_round(tmp, state, PASS_SCOREBOARD)
            self.assertEqual(result["decision"], "proceed")
            self.assertEqual(state.current_state, "CREATE_SCENE_LANDING_PREVIEW")
            self.assertEqual(state.status, "running")


class AdvanceCheckedTests(unittest.TestCase):
    def _touch(self, tmp, run_id, rel_path):
        path = Path(tmp) / "runs" / run_id / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x")

    def test_gate_state_with_missing_artifacts_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "DISCOVER_AND_ASSIGN_AGENTS"
            result = runner.advance_checked(tmp, state)
            self.assertFalse(result["advanced"])
            self.assertEqual(
                result["missing"], ["debates/agent_assignment_matrix.md"]
            )
            self.assertEqual(state.current_state, "DISCOVER_AND_ASSIGN_AGENTS")
            self.assertEqual(state.gates["DISCOVER_AND_ASSIGN_AGENTS"], "fail")

    def test_gate_state_with_artifacts_advances(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "DISCOVER_AND_ASSIGN_AGENTS"
            self._touch(tmp, state.run_id, "debates/agent_assignment_matrix.md")
            result = runner.advance_checked(tmp, state)
            self.assertTrue(result["advanced"])
            self.assertEqual(state.current_state, "GENERATE_OR_REFINE_IDEAS")
            self.assertEqual(state.gates["DISCOVER_AND_ASSIGN_AGENTS"], "pass")

    def test_non_gate_state_advances_without_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            result = runner.advance_checked(tmp, state)
            self.assertTrue(result["advanced"])
            self.assertEqual(state.current_state, "PARSE_CREATIVE_INPUT")

    def test_gate_refusal_persists(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "DISCOVER_AND_ASSIGN_AGENTS"
            runner.advance_checked(tmp, state)
            reloaded = run_state_mod.load_state(tmp, state.run_id)
            self.assertEqual(reloaded.gates["DISCOVER_AND_ASSIGN_AGENTS"], "fail")

    def test_gate_record_flips_fail_to_pass_after_fix(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "DISCOVER_AND_ASSIGN_AGENTS"
            runner.advance_checked(tmp, state)
            self.assertEqual(state.gates["DISCOVER_AND_ASSIGN_AGENTS"], "fail")
            self._touch(tmp, state.run_id, "debates/agent_assignment_matrix.md")
            result = runner.advance_checked(tmp, state)
            self.assertTrue(result["advanced"])
            reloaded = run_state_mod.load_state(tmp, state.run_id)
            self.assertEqual(reloaded.gates["DISCOVER_AND_ASSIGN_AGENTS"], "pass")


class VerifyStateTests(unittest.TestCase):
    def _write_json(self, tmp, run_id, rel_path, payload):
        import json as _json
        path = Path(tmp) / "runs" / run_id / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_json.dumps(payload))

    def test_registered_state_ok_when_artifact_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            self._write_json(
                tmp, state.run_id, "planning/story_concept.json",
                {"title": "T", "one_line_summary": "s", "setup": "a",
                 "escalation": "b", "payoff": "c"},
            )
            result = runner.verify_state(tmp, state.run_id, "GENERATE_STORY_CONCEPT")
            self.assertTrue(result["enforced"])
            self.assertTrue(result["ok"])
            self.assertEqual(result["problems"], [])

    def test_registered_state_reports_content_problems(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            self._write_json(tmp, state.run_id, "planning/story_concept.json", {"setup": "a"})
            result = runner.verify_state(tmp, state.run_id, "GENERATE_STORY_CONCEPT")
            self.assertFalse(result["ok"])
            self.assertIn("missing_title", result["problems"])

    def test_registered_state_missing_file_is_not_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            result = runner.verify_state(tmp, state.run_id, "GENERATE_SLIDE_BEATS")
            self.assertFalse(result["ok"])
            self.assertIn("slide_beat_map_not_object", result["problems"])

    def test_registered_state_corrupt_json_is_not_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            path = Path(tmp) / "runs" / state.run_id / "planning/story_concept.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("{not valid json")
            result = runner.verify_state(tmp, state.run_id, "GENERATE_STORY_CONCEPT")
            self.assertFalse(result["ok"])
            self.assertIn("story_concept_not_object", result["problems"])

    def test_unregistered_non_gate_state_is_not_enforced_and_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            result = runner.verify_state(tmp, state.run_id, "DECIDE_SLIDE_COUNT")
            self.assertFalse(result["enforced"])
            self.assertTrue(result["ok"])

    def test_gate_state_presence_still_enforced(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            result = runner.verify_state(tmp, state.run_id, "DISCOVER_AND_ASSIGN_AGENTS")
            self.assertTrue(result["enforced"])
            self.assertFalse(result["ok"])
            self.assertEqual(result["missing"], ["debates/agent_assignment_matrix.md"])


if __name__ == "__main__":
    unittest.main()
