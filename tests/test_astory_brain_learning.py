import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.astory_brain.indexer import build_index
from scripts.astory_brain.learning import (
    extract_learning_report,
    write_learning_artifacts,
)
from scripts.astory_brain.retrieval import recall


REPO_ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "2026-06-10_22-22_heart-rent"


class AStoryBrainLearningTests(unittest.TestCase):
    def test_extracts_policy_scored_claims_from_run_evidence(self):
        report = extract_learning_report(REPO_ROOT, RUN_ID)

        self.assertEqual(report.run_id, RUN_ID)
        self.assertGreaterEqual(len(report.claims), 4)
        self.assertTrue(all(claim.evidence_paths for claim in report.claims))
        self.assertTrue(all(claim.confidence > 0 for claim in report.claims))

        policies = {claim.promotion_policy for claim in report.claims}
        statuses = {claim.status for claim in report.claims}
        claim_types = {claim.claim_type for claim in report.claims}

        self.assertIn("auto_apply", policies)
        self.assertIn("human_review", policies)
        self.assertIn("quarantine", policies)
        self.assertIn("candidate", statuses)
        self.assertIn("quarantined", statuses)
        self.assertIn("creator_preference", claim_types)
        self.assertIn("failure_mode", claim_types)
        self.assertIn("production_constraint", claim_types)

        creator_claims = [
            claim
            for claim in report.claims
            if claim.claim_type == "creator_preference"
        ]
        self.assertTrue(any("Aachu" in claim.text for claim in creator_claims))
        self.assertTrue(
            all(claim.risk_level == "high" for claim in creator_claims)
        )

    def test_write_learning_artifacts_records_ledger_and_claim_queue(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_minimal_repo(root)

            report = extract_learning_report(root, RUN_ID)
            artifacts = write_learning_artifacts(root, report)

            claim_path = root / artifacts["claims_json"]
            ledger_path = root / artifacts["ledger_jsonl"]
            markdown_path = root / artifacts["claims_markdown"]

            self.assertTrue(claim_path.exists())
            self.assertTrue(ledger_path.exists())
            self.assertTrue(markdown_path.exists())

            payload = json.loads(claim_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["run_id"], RUN_ID)
            self.assertEqual(payload["schema_version"], "1.0")
            self.assertGreaterEqual(payload["summary"]["human_review"], 1)
            self.assertGreaterEqual(payload["summary"]["quarantine"], 1)

            ledger_events = [
                json.loads(line)
                for line in ledger_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual(len(ledger_events), len(report.claims))
            self.assertTrue(
                all(event["action"] == "candidate_created" for event in ledger_events)
            )
            self.assertTrue(
                all(event["claim_id"].startswith("claim:") for event in ledger_events)
            )

    def test_active_learning_claims_are_indexable_for_future_recall(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_minimal_repo(root)
            report = extract_learning_report(root, RUN_ID)
            write_learning_artifacts(root, report)

            index = root / "references/brain/index"
            build_index(root, index, include_runs=[RUN_ID])
            results = recall(
                index,
                "prompt only generation forbidden view image queued local references",
                run_id=RUN_ID,
                limit=10,
            )

            paths = {result.chunk.path for result in results}
            self.assertIn(
                f"runs/{RUN_ID}/memory/active_claims.md",
                paths,
            )
            self.assertNotIn(f"runs/{RUN_ID}/memory/claim_candidates.json", paths)

    def test_cli_learn_writes_claim_queue_and_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_minimal_repo(root)

            output = subprocess.check_output(
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts/astory_brain_cli.py"),
                    "learn",
                    "--repo-root",
                    str(root),
                    "--run-id",
                    RUN_ID,
                    "--write",
                ],
                text=True,
            )

            payload = json.loads(output)
            self.assertEqual(payload["run_id"], RUN_ID)
            self.assertEqual(payload["status"], "claims_extracted")
            self.assertTrue((root / payload["artifacts"]["claims_json"]).exists())
            self.assertTrue((root / payload["artifacts"]["ledger_jsonl"]).exists())

    def test_doctor_reports_open_claim_review_queue_after_learning(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_minimal_repo(root)
            report = extract_learning_report(root, RUN_ID)
            write_learning_artifacts(root, report)

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
            doctor_json = json.loads(
                (root / "references/brain/reports/doctor.json").read_text(
                    encoding="utf-8"
                )
            )

            self.assertIn("Learning pipeline status: `operational_with_review_queue`", output)
            self.assertIn("## Memory Claim Review Queue", output)
            self.assertEqual(
                doctor_json["learning_pipeline_status"],
                "operational_with_review_queue",
            )
            self.assertGreaterEqual(doctor_json["claim_review_queue"]["active_runtime"], 1)
            self.assertGreaterEqual(doctor_json["claim_review_queue"]["open_human_review"], 1)
            self.assertGreaterEqual(doctor_json["claim_review_queue"]["open_quarantine_review"], 1)


def _copy_minimal_repo(root: Path) -> None:
    for rel in [
        "references/brain/schema/type_taxonomy.json",
        "references/brain/schema/version.json",
        "tests/fixtures/brain/qrels.json",
        "scripts/astory_repo_qa.py",
        "references/style/README.md",
        f"runs/{RUN_ID}/docs/approvals.md",
        f"runs/{RUN_ID}/evals/image_quality_eval.json",
        f"runs/{RUN_ID}/evals/pre_generation_eval.json",
        f"runs/{RUN_ID}/evals/repo_qa_review.json",
        f"runs/{RUN_ID}/references-used/selected_references.json",
        f"runs/{RUN_ID}/prompts/slide_01_4x5_prompt.txt",
    ]:
        source = REPO_ROOT / rel
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    _write_minimal_brain_pages(root)


def _write_minimal_brain_pages(root: Path) -> None:
    pages = root / "references/brain/pages"
    characters = pages / "characters"
    characters.mkdir(parents=True, exist_ok=True)
    (characters / "aachu.md").write_text(
        "---\n"
        "type: character\n"
        "role: aachu\n"
        "---\n\n"
        "# Aachu\n\n"
        "# Current Truth\n\n"
        "- Aachu face identity references are role-separated for retrieval. Evidence: `references/brain/pages/characters/aachu.md`.\n\n"
        "---\n\n"
        "# Timeline / Evidence\n\n"
        "- 2026-06-10 | `references/brain/pages/characters/aachu.md` | Minimal test fixture.\n",
        encoding="utf-8",
    )
    (characters / "zuv.md").write_text(
        "---\n"
        "type: character\n"
        "role: zuv\n"
        "---\n\n"
        "# Zuv\n\n"
        "# Current Truth\n\n"
        "- Zuv face identity references are role-separated for retrieval. Evidence: `references/brain/pages/characters/zuv.md`.\n\n"
        "---\n\n"
        "# Timeline / Evidence\n\n"
        "- 2026-06-10 | `references/brain/pages/characters/zuv.md` | Minimal test fixture.\n",
        encoding="utf-8",
    )
    (characters / "together.md").write_text(
        "---\n"
        "type: character\n"
        "role: together\n"
        "---\n\n"
        "# Together\n\n"
        "# Current Truth\n\n"
        "- Together references describe body language and couple scale. Evidence: `references/brain/pages/characters/together.md`.\n\n"
        "---\n\n"
        "# Timeline / Evidence\n\n"
        "- 2026-06-10 | `references/brain/pages/characters/together.md` | Minimal test fixture.\n",
        encoding="utf-8",
    )
    (pages / "run-lessons.md").write_text(
        "---\n"
        "type: run_lesson\n"
        "role: text\n"
        "---\n\n"
        "# Run Lessons\n\n"
        "# Current Truth\n\n"
        f"- Repo QA preserves blockers instead of manufacturing proof artifacts. Evidence: `runs/{RUN_ID}/evals/repo_qa_review.json`.\n\n"
        "---\n\n"
        "# Timeline / Evidence\n\n"
        f"- 2026-06-10 | `runs/{RUN_ID}/evals/repo_qa_review.json` | Minimal test fixture.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    unittest.main()
