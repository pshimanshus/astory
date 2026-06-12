import tempfile
import unittest
from pathlib import Path

from scripts.astory_orchestrator import gates


def _touch(repo_root, run_id, rel_path):
    path = Path(repo_root) / "runs" / run_id / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("x")


class MissingArtifactsTests(unittest.TestCase):
    def test_all_present_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            _touch(tmp, "demo", "debates/agent_assignment_matrix.md")
            self.assertEqual(
                gates.missing_artifacts(tmp, "demo", "DISCOVER_AND_ASSIGN_AGENTS"),
                [],
            )

    def test_missing_listed_run_relative(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(
                gates.missing_artifacts(tmp, "demo", "DISCOVER_AND_ASSIGN_AGENTS"),
                ["debates/agent_assignment_matrix.md"],
            )

    def test_state_with_no_produces_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(gates.missing_artifacts(tmp, "demo", "INIT_RUN"), [])

    def test_unknown_state_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(KeyError):
                gates.missing_artifacts(tmp, "demo", "NOT_A_STATE")


class CheckGateTests(unittest.TestCase):
    def test_gate_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            _touch(tmp, "demo", "debates/agent_assignment_matrix.md")
            result = gates.check_gate(tmp, "demo", "DISCOVER_AND_ASSIGN_AGENTS")
            self.assertTrue(result["ok"])
            self.assertEqual(result["missing"], [])

    def test_gate_fail_lists_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = gates.check_gate(tmp, "demo", "DISCOVER_AND_ASSIGN_AGENTS")
            self.assertFalse(result["ok"])
            self.assertEqual(result["missing"], ["debates/agent_assignment_matrix.md"])
            self.assertEqual(result["state"], "DISCOVER_AND_ASSIGN_AGENTS")

    def test_non_gate_state_is_ok_but_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = gates.check_gate(tmp, "demo", "INIT_RUN")
            self.assertTrue(result["ok"])
            self.assertFalse(result["is_gate"])


if __name__ == "__main__":
    unittest.main()
