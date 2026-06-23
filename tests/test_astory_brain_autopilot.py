import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.astory_brain.autopilot import run_memory_autopilot
from scripts.astory_brain.claim_store import load_claim_records, summarize_claim_records
from scripts.astory_brain.indexer import build_index
from scripts.astory_brain.learning import extract_learning_report, write_learning_artifacts
from scripts.astory_brain.retrieval import recall

from tests.test_astory_brain_learning import REPO_ROOT, RUN_ID, _copy_minimal_repo


class AStoryBrainAutopilotTests(unittest.TestCase):
    def test_pre_imagegen_autopilot_is_lightweight_and_does_not_learn_or_promote(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_minimal_repo(root)
            page = root / "references/brain/pages/run-lessons.md"
            before_page = page.read_text(encoding="utf-8")

            report = run_memory_autopilot(root, RUN_ID, phase="pre_imagegen")

            self.assertEqual(report["status"], "skipped_pre_imagegen")
            self.assertFalse((root / f"runs/{RUN_ID}/memory/claim_candidates.json").exists())
            self.assertFalse((root / "references/brain/ledger/events.jsonl").exists())
            self.assertEqual(before_page, page.read_text(encoding="utf-8"))
            self.assertFalse(report["heavy_verification_ran"])

    def test_post_run_autopilot_learns_and_decides_without_human_intervention(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_minimal_repo(root)

            report = run_memory_autopilot(root, RUN_ID, phase="post_run")

            self.assertEqual(report["status"], "completed")
            self.assertFalse(report["human_intervention_required"])
            self.assertTrue(report["heavy_verification_ran"])
            self.assertTrue((root / f"runs/{RUN_ID}/memory/autopilot_report.json").exists())
            self.assertTrue((root / f"runs/{RUN_ID}/memory/active_claims.md").exists())
            self.assertGreaterEqual(report["decision_summary"]["auto_promoted"], 1)
            self.assertGreaterEqual(report["decision_summary"]["auto_deferred"], 1)
            self.assertGreaterEqual(report["decision_summary"]["auto_quarantined"], 1)

            records = load_claim_records(root)
            summary = summarize_claim_records(records)
            self.assertEqual(summary["open_human_review"], 0)
            self.assertEqual(summary["open_quarantine_review"], 0)
            self.assertGreaterEqual(summary["promoted"], 1)
            self.assertGreaterEqual(summary["deferred"], 1)
            self.assertGreaterEqual(summary["quarantined"], 1)

    def test_autopilot_cli_runs_post_run_loop(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_minimal_repo(root)

            output = subprocess.check_output(
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts/astory_brain_cli.py"),
                    "autopilot",
                    "--repo-root",
                    str(root),
                    "--run-id",
                    RUN_ID,
                    "--phase",
                    "post_run",
                ],
                text=True,
            )

            payload = json.loads(output)
            self.assertEqual(payload["status"], "completed")
            self.assertFalse(payload["human_intervention_required"])

    def test_doctor_has_no_required_human_decisions_after_autopilot_clears_queue(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_minimal_repo(root)
            run_memory_autopilot(root, RUN_ID, phase="post_run")

            output = subprocess.check_output(
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts/astory_brain_cli.py"),
                    "doctor",
                    "--repo-root",
                    str(root),
                ],
                text=True,
            )
            payload = json.loads(
                (root / "references/brain/reports/doctor.json").read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(payload["required_human_decisions"], [])
            self.assertIn("- None.", output)

    def test_policy_can_disable_auto_promotion_without_requiring_human_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_minimal_repo(root)
            policy = root / "references/brain/policies/memory_autopilot.json"
            policy.parent.mkdir(parents=True, exist_ok=True)
            policy.write_text(
                json.dumps(
                    {
                        "auto_promote_auto_apply": False,
                        "auto_defer_high_risk": True,
                        "auto_quarantine_rejected_assets": True,
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            report = run_memory_autopilot(root, RUN_ID, phase="post_run")
            summary = summarize_claim_records(load_claim_records(root))

            self.assertEqual(report["decision_summary"]["auto_promoted"], 0)
            self.assertGreaterEqual(summary["active_runtime"], 1)
            self.assertEqual(summary["open_human_review"], 0)
            self.assertEqual(summary["open_quarantine_review"], 0)
            self.assertFalse(report["human_intervention_required"])

    def test_raw_claim_candidates_are_not_indexed_as_runtime_truth(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_minimal_repo(root)
            learning = extract_learning_report(root, RUN_ID)
            write_learning_artifacts(root, learning)

            index = root / "references/brain/index"
            build_index(root, index, include_runs=[RUN_ID])
            results = recall(
                index,
                "prompt only generation forbidden view image references",
                run_id=RUN_ID,
                limit=10,
            )

            paths = {result.chunk.path for result in results}
            self.assertIn(f"runs/{RUN_ID}/memory/active_claims.md", paths)
            self.assertNotIn(f"runs/{RUN_ID}/memory/claim_candidates.json", paths)
            self.assertNotIn(f"runs/{RUN_ID}/memory/claim_candidates.md", paths)


if __name__ == "__main__":
    unittest.main()
