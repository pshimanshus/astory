import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CLI = REPO_ROOT / "scripts" / "astory_orchestrator_cli.py"


def _run(*args, cwd=REPO_ROOT):
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )


class OrchestratorCliTests(unittest.TestCase):
    def test_spine_command_prints_33_states(self):
        result = _run("spine")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(len(payload), 33)
        self.assertEqual(payload[0]["name"], "INIT_RUN")

    def test_validate_spine_command_ok(self):
        result = _run("validate-spine")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["ok"])

    def test_init_then_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            init = _run("--repo-root", tmp, "init", "--run-id", "demo")
            self.assertEqual(init.returncode, 0, init.stderr)
            self.assertEqual(json.loads(init.stdout)["status"], "created")

            status = _run("--repo-root", tmp, "status", "--run-id", "demo")
            self.assertEqual(status.returncode, 0, status.stderr)
            body = json.loads(status.stdout)
            self.assertEqual(body["current_state"], "INIT_RUN")
            self.assertEqual(body["next_state"], "PARSE_CREATIVE_INPUT")

    def test_init_refuses_existing_without_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(
                _run("--repo-root", tmp, "init", "--run-id", "demo").returncode, 0
            )
            second = _run("--repo-root", tmp, "init", "--run-id", "demo")
            self.assertEqual(second.returncode, 1)
            self.assertEqual(json.loads(second.stdout)["status"], "exists")

    def test_status_without_state_returns_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _run("--repo-root", tmp, "status", "--run-id", "demo")
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)["status"], "no_state")


class IdeaLegWalkTests(unittest.TestCase):
    def _write_scoreboard(self, tmp, overall):
        import json as _json
        path = Path(tmp) / "scoreboard.json"
        path.write_text(
            _json.dumps(
                {
                    "minimum_required_overall_score": 4.0,
                    "candidates": [
                        {"title": "X", "overall_score": overall, "selection_status": "selected"}
                    ],
                }
            )
        )
        return path

    def _set_state(self, tmp, run_id, current_state):
        from scripts.astory_orchestrator import state as run_state_mod
        st = run_state_mod.new_run_state(run_id)
        st.current_state = current_state
        run_state_mod.save_state(tmp, run_id, st)

    def test_idea_round_rerun_then_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._set_state(tmp, "demo", "SCORE_IDEAS")
            board = self._write_scoreboard(tmp, 3.4)

            first = _run("--repo-root", tmp, "idea-round", "--run-id", "demo",
                         "--scoreboard", str(board))
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(json.loads(first.stdout)["decision"], "rerun")

            second = _run("--repo-root", tmp, "idea-round", "--run-id", "demo",
                          "--scoreboard", str(board))
            self.assertEqual(json.loads(second.stdout)["decision"], "blocked")
            self.assertEqual(second.returncode, 1)

    def test_bad_scoreboard_returns_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._set_state(tmp, "demo", "SCORE_IDEAS")
            result = _run("--repo-root", tmp, "idea-round", "--run-id", "demo",
                          "--scoreboard", "/nonexistent/nope.json")
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)["status"], "bad_scoreboard")

    def test_malformed_scoreboard_is_invalid_and_returns_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._set_state(tmp, "demo", "SCORE_IDEAS")
            board = Path(tmp) / "empty.json"
            board.write_text('{"candidates": []}')
            result = _run("--repo-root", tmp, "idea-round", "--run-id", "demo",
                          "--scoreboard", str(board))
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)["decision"], "invalid")

    def test_idea_round_proceed_then_next_halts_then_approve(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._set_state(tmp, "demo", "SCORE_IDEAS")
            board = self._write_scoreboard(tmp, 4.6)

            proceed = _run("--repo-root", tmp, "idea-round", "--run-id", "demo",
                           "--scoreboard", str(board))
            self.assertEqual(json.loads(proceed.stdout)["decision"], "proceed")

            self._set_state(tmp, "demo", "HITL_IDEA_LOCK")
            nxt = _run("--repo-root", tmp, "next", "--run-id", "demo")
            self.assertEqual(nxt.returncode, 0, nxt.stderr)
            self.assertTrue(json.loads(nxt.stdout)["halt"])

            approve = _run("--repo-root", tmp, "approve", "--run-id", "demo")
            self.assertEqual(approve.returncode, 0, approve.stderr)
            self.assertEqual(json.loads(approve.stdout)["current_state"],
                             "GENERATE_STORY_CONCEPT")

    def test_advance_blocked_at_gate_then_passes_with_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._set_state(tmp, "demo", "DISCOVER_AND_ASSIGN_AGENTS")

            refused = _run("--repo-root", tmp, "advance", "--run-id", "demo")
            self.assertEqual(refused.returncode, 1)
            body = json.loads(refused.stdout)
            self.assertFalse(body["advanced"])
            self.assertIn("debates/agent_assignment_matrix.md", body["missing"])

            artifact = Path(tmp) / "runs" / "demo" / "debates" / "agent_assignment_matrix.md"
            artifact.parent.mkdir(parents=True, exist_ok=True)
            artifact.write_text("matrix")

            ok = _run("--repo-root", tmp, "advance", "--run-id", "demo")
            self.assertEqual(ok.returncode, 0, ok.stderr)
            self.assertTrue(json.loads(ok.stdout)["advanced"])

    def test_advance_at_terminal_state_returns_clean_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._set_state(tmp, "demo", "COMPLETE_OR_BLOCKED")
            result = _run("--repo-root", tmp, "advance", "--run-id", "demo")
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)["status"], "terminal")


if __name__ == "__main__":
    unittest.main()
