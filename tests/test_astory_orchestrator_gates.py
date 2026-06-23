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

    def test_multi_artifact_state_lists_only_missing_subset(self):
        # PRE_GENERATION_EVAL declares source-winner alignment too; with one
        # present, only the other required artifacts should be reported missing.
        with tempfile.TemporaryDirectory() as tmp:
            _touch(tmp, "demo", "evals/pre_generation_eval.json")
            self.assertEqual(
                sorted(gates.missing_artifacts(tmp, "demo", "PRE_GENERATION_EVAL")),
                [
                    "debates/prompt_room/prompt_review.md",
                    "evals/pre_generation_eval_report.md",
                    "evals/source_winner_alignment_eval.json",
                ],
            )


if __name__ == "__main__":
    unittest.main()
