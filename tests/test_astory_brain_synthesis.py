import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.astory_brain.indexer import build_index
from scripts.astory_brain.retrieval import recall
from scripts.astory_brain.synthesis import synthesize_recall


class AStoryBrainSynthesisTests(unittest.TestCase):
    def test_synthesis_contains_citations_and_gaps(self):
        with tempfile.TemporaryDirectory() as tmp:
            index = Path(tmp) / "index"
            build_index(".", index, include_runs=["2026-06-10_22-22_heart-rent"])
            results = recall(index, "heart rent prompt identity", limit=5)

            synthesis = synthesize_recall("heart rent prompt identity", results)

            self.assertIn("## Cited Findings", synthesis.answer_markdown)
            self.assertIn("## Gaps", synthesis.answer_markdown)
            self.assertTrue(synthesis.cited_paths)


class AStoryBrainCliTests(unittest.TestCase):
    def test_cli_index_and_recall(self):
        with tempfile.TemporaryDirectory() as tmp:
            index = Path(tmp) / "index"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/astory_brain_cli.py",
                    "index",
                    "--repo-root",
                    ".",
                    "--output",
                    str(index),
                    "--include-run",
                    "2026-06-10_22-22_heart-rent",
                ],
                check=True,
            )
            output = subprocess.check_output(
                [
                    sys.executable,
                    "scripts/astory_brain_cli.py",
                    "recall",
                    "--index",
                    str(index),
                    "--query",
                    "heart rent prompt identity",
                ],
                text=True,
            )

            self.assertIn("## Cited Findings", output)

    def test_cli_runs_as_module(self):
        output = subprocess.check_output(
            [
                sys.executable,
                "-m",
                "scripts.astory_brain_cli",
                "lint",
                "--repo-root",
                ".",
            ],
            text=True,
        )

        self.assertIn('"status": "pass"', output)

    def test_doctor_reports_brain_setup_scope_not_run_gate_scope(self):
        output = subprocess.check_output(
            [
                sys.executable,
                "scripts/astory_brain_cli.py",
                "doctor",
                "--repo-root",
                ".",
            ],
            text=True,
        )

        self.assertIn("Scope: `brain_setup`", output)
        self.assertIn("Runtime status: `ready`", output)
        self.assertIn("Learning pipeline status:", output)
        self.assertIn("## Creative Run Gates Excluded", output)
        self.assertIn("`reference_visibility_proof`", output)
        self.assertIn("`agent_assignment_gate`", output)
        self.assertIn("## Memory Claim Review Queue", output)
        self.assertNotIn("## Stale Runs", output)


if __name__ == "__main__":
    unittest.main()
