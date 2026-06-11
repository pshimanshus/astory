import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import astory_repo_qa


REPO_ROOT = Path(__file__).resolve().parents[1]
ACTIVE_RUN_ID = "2026-06-10_22-22_heart-rent"
PROMPT_REVISION_RUN_ID = "2026-06-10_22-55_couple-banter"
LOCAL_IDENTITY_RUN_ID = "2026-06-07_17-57_auto"


class AStoryRepoQATests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.active_audit = astory_repo_qa.run_repo_qa(REPO_ROOT, ACTIVE_RUN_ID)
        cls.local_identity_audit = astory_repo_qa.run_repo_qa(
            REPO_ROOT, LOCAL_IDENTITY_RUN_ID
        )

    def test_skill_contract_and_master_prompt_are_present(self):
        checks = self.active_audit["checks_by_id"]

        self.assertEqual(checks["skill_contract_present"]["status"], "pass")
        self.assertEqual(checks["master_prompt_present"]["status"], "pass")
        self.assertEqual(checks["required_templates_present"]["status"], "pass")

    def test_agent_dispatch_prompt_packets_are_structured(self):
        required_packets = [
            REPO_ROOT / ".agents/skills/astory/templates/agents/story_room_agent_prompt.md",
            REPO_ROOT
            / ".agents/skills/astory/templates/agents/visual_scene_discussion_prompt.md",
            REPO_ROOT / ".agents/skills/astory/templates/agents/review_room_agent_prompt.md",
        ]
        required_phrases = [
            "Run:",
            "Read Before Writing",
            "Output Artifacts",
            "Discussion Protocol",
            "Reference Rules",
            "Failure Codes",
        ]

        for path in required_packets:
            with self.subTest(path=path):
                self.assertTrue(path.exists(), path)
                text = path.read_text()
                for phrase in required_phrases:
                    self.assertIn(phrase, text)

    def test_required_templates_include_agent_prompt_packets(self):
        checked_paths = set(
            self.active_audit["checks_by_id"]["required_templates_present"][
                "checked_paths"
            ]
        )

        self.assertIn(
            ".agents/skills/astory/templates/agents/story_room_agent_prompt.md",
            checked_paths,
        )
        self.assertIn(
            ".agents/skills/astory/templates/agents/visual_scene_discussion_prompt.md",
            checked_paths,
        )
        self.assertIn(
            ".agents/skills/astory/templates/agents/review_room_agent_prompt.md",
            checked_paths,
        )

    def test_agent_dispatch_prompt_packets_are_specific_not_generic(self):
        prompt_dir = REPO_ROOT / ".agents/skills/astory/templates/agents"
        packet_expectations = {
            "story_room_agent_prompt.md": [
                "Minimum Specificity Bar",
                "Evidence Ledger",
                "Decision Table",
                "Do Not Return",
                "Bad Output Patterns",
                "slide_beat_contract",
                "cut_or_keep_verdict",
                "micro_action",
            ],
            "visual_scene_discussion_prompt.md": [
                "Minimum Specificity Bar",
                "Evidence Ledger",
                "Decision Table",
                "Do Not Return",
                "Bad Output Patterns",
                "camera_distance",
                "face_visibility_plan",
                "rejected_scene_memory",
            ],
            "review_room_agent_prompt.md": [
                "Minimum Specificity Bar",
                "Evidence Ledger",
                "Decision Table",
                "Do Not Return",
                "Bad Output Patterns",
                "gate_ledger",
                "blocker_owner",
                "next_command",
            ],
        }

        for filename, phrases in packet_expectations.items():
            path = prompt_dir / filename
            text = path.read_text()
            with self.subTest(filename=filename):
                self.assertGreater(len(text.split()), 900)
                for phrase in phrases:
                    self.assertIn(phrase, text)

    def test_active_run_reference_manifest_is_complete_and_hashed(self):
        checks = self.active_audit["checks_by_id"]
        summary = self.active_audit["reference_summary"]

        self.assertEqual(checks["reference_manifest_integrity"]["status"], "pass")
        self.assertFalse(checks["reference_manifest_integrity"]["missing_paths"])
        self.assertFalse(checks["reference_manifest_integrity"]["sha_mismatches"])
        self.assertGreaterEqual(summary["aachu_face_identity_count"], 4)
        self.assertGreaterEqual(summary["zuv_face_identity_count"], 4)
        self.assertGreaterEqual(summary["style_reference_count"], 1)

    def test_active_run_prompt_matches_locked_story_and_reference_gate(self):
        checks = self.active_audit["checks_by_id"]

        self.assertEqual(checks["prompt_story_contract"]["status"], "pass")
        self.assertEqual(checks["prompt_reference_gate"]["status"], "pass")
        self.assertEqual(checks["prompt_forbidden_role_reversal"]["status"], "pass")

    def test_reference_load_plan_accepts_loaded_reference_path_proof(self):
        checks = self.active_audit["checks_by_id"]

        self.assertEqual(checks["reference_visibility_proof"]["status"], "pass")
        self.assertIsNone(checks["reference_visibility_proof"]["failure_code"])
        self.assertTrue(checks["reference_visibility_proof"]["final_imagegen_allowed"])
        self.assertEqual(checks["reference_visibility_proof"]["view_image_queue_count"], 17)
        self.assertIn(
            "runs/2026-06-10_22-22_heart-rent/evals/imagegen_reference_visibility_proof.json",
            checks["reference_visibility_proof"]["expected_artifact"],
        )

    def test_reference_visibility_proof_accepts_confirmed_roles_format(self):
        audit = astory_repo_qa.run_repo_qa(REPO_ROOT, PROMPT_REVISION_RUN_ID)
        check = audit["checks_by_id"]["reference_visibility_proof"]

        self.assertEqual(check["status"], "pass")
        self.assertIsNone(check["failure_code"])
        self.assertTrue(check["final_imagegen_allowed"])

    def test_pending_image_qa_blocks_final_package(self):
        checks = self.active_audit["checks_by_id"]

        self.assertEqual(checks["image_qa_blocks_final_package"]["status"], "pass")
        self.assertEqual(
            checks["image_qa_blocks_final_package"]["hard_gate_result"],
            "pending_creator_image_qa",
        )
        self.assertEqual(
            checks["image_qa_blocks_final_package"]["failure_code"],
            "IMAGE_QA_PENDING_CREATOR_APPROVAL",
        )
        self.assertEqual(checks["final_package_not_started"]["status"], "pass")

    def test_accepted_candidate_filenames_are_not_treated_as_final(self):
        checks = self.active_audit["checks_by_id"]

        self.assertEqual(
            checks["accepted_candidate_filename_guard"]["status"], "pass"
        )
        self.assertGreaterEqual(
            len(checks["accepted_candidate_filename_guard"]["rejected_after_review"]),
            1,
        )

    def test_trace_and_approvals_record_required_hitl_order(self):
        checks = self.active_audit["checks_by_id"]

        self.assertEqual(checks["trace_jsonl_valid"]["status"], "pass")
        self.assertEqual(checks["hitl_order_before_imagegen"]["status"], "pass")
        self.assertEqual(checks["approvals_cover_required_gates"]["status"], "pass")

    def test_local_identity_cpu_stall_is_recorded_and_blocks_final_art(self):
        checks = self.local_identity_audit["checks_by_id"]

        self.assertEqual(checks["local_identity_execution_report"]["status"], "pass")
        self.assertEqual(
            checks["local_identity_execution_report"]["failure_code"],
            "LOCAL_CPU_EXECUTION_STALLED",
        )
        self.assertFalse(
            checks["local_identity_execution_report"]["identity_proof_generated"]
        )

    def test_detects_imagegen_story_run_for_heart_rent(self):
        workflow = self.active_audit["workflow"]

        self.assertEqual(workflow["type"], "imagegen_story_run")
        self.assertIn("prompts", workflow["evidence"])
        self.assertIn("reference_load_plan", workflow["evidence"])

    def test_detects_prompt_revision_run_for_couple_banter(self):
        audit = astory_repo_qa.run_repo_qa(REPO_ROOT, PROMPT_REVISION_RUN_ID)

        self.assertIn(
            audit["workflow"]["type"],
            {"prompt_revision_run", "imagegen_story_run"},
        )
        self.assertIn("prompt_files", audit["workflow"])
        self.assertGreaterEqual(len(audit["workflow"]["prompt_files"]), 1)

    def test_detects_local_identity_execution_run(self):
        workflow = self.local_identity_audit["workflow"]

        self.assertEqual(workflow["type"], "local_identity_execution_run")
        self.assertIn("local_identity_proof", workflow["evidence"])

    def test_agent_assignment_gate_is_still_required_for_prompt_locked_runs(self):
        check = self.active_audit["checks_by_id"]["agent_assignment_gate"]

        self.assertEqual(check["status"], "fail")
        self.assertEqual(check["failure_code"], "AGENT_ASSIGNMENT_MISSING")
        self.assertIn("incomplete", check["summary"])
        self.assertTrue(check["assignment_trace_present"])
        self.assertIn(
            "evals/pre_generation_eval.json.prompt_room_outputs_or_agent_outputs",
            check["missing_requirements"],
        )

    def test_agent_assignment_gate_is_present_in_every_audit(self):
        audit = astory_repo_qa.run_repo_qa(REPO_ROOT, PROMPT_REVISION_RUN_ID)

        self.assertIn("agent_assignment_gate", audit["checks_by_id"])

    def test_blocked_memory_recall_blocks_overall_status(self):
        blocked_check = {
            "id": "memory_recall",
            "status": "blocked",
            "severity": "blocker",
            "summary": "Memory recall artifact is missing for this run.",
            "failure_code": "MEMORY_RECALL_MISSING",
        }

        with patch.object(astory_repo_qa, "_check_memory_recall", return_value=blocked_check):
            audit = astory_repo_qa.run_repo_qa(REPO_ROOT, ACTIVE_RUN_ID)

        self.assertEqual(audit["overall_status"], "blocked")
        self.assertTrue(
            any(item["id"] == "memory_recall" for item in audit["blocking_findings"])
        )

    def test_memory_recall_rejects_derived_index_citation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "runs/example"
            (run_dir / "planning").mkdir(parents=True)
            (run_dir / "logs").mkdir()
            (run_dir / "planning/memory_recall.md").write_text(
                "# Memory Recall\n\n"
                "## Cited Findings\n\n"
                "- `references/brain/index/chunks.jsonl`: derived cache.\n\n"
                "## Retrieval Evidence\n\n"
                "- `references/brain/index/chunks.jsonl` evidence.\n\n"
                "## Gaps\n\n"
                "- None.\n\n"
                "## Usability For This Run\n\n"
                "Supporting context only.\n",
                encoding="utf-8",
            )
            (run_dir / "logs/trace.jsonl").write_text(
                '{"state":"MEMORY_RECALL_PREFLIGHT","status":"retrospective_backfill_complete"}\n',
                encoding="utf-8",
            )

            check = astory_repo_qa._check_memory_recall(
                root, run_dir, {"type": "imagegen_story_run"}
            )

            self.assertEqual(check["status"], "fail")
            self.assertIn("references/brain/index/chunks.jsonl", check["derived_citations"])

    def test_memory_recall_requires_trace_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "runs/example"
            (run_dir / "planning").mkdir(parents=True)
            (root / "references/identity/aachu").mkdir(parents=True)
            (root / "references/identity/aachu/README.md").write_text(
                "Aachu refs\n", encoding="utf-8"
            )
            (run_dir / "planning/memory_recall.md").write_text(
                "# Memory Recall\n\n"
                "## Cited Findings\n\n"
                "- `references/identity/aachu/README.md`: identity refs.\n\n"
                "## Retrieval Evidence\n\n"
                "- `references/identity/aachu/README.md` evidence.\n\n"
                "## Gaps\n\n"
                "- None.\n\n"
                "## Usability For This Run\n\n"
                "Supporting context only.\n",
                encoding="utf-8",
            )

            check = astory_repo_qa._check_memory_recall(
                root, run_dir, {"type": "imagegen_story_run"}
            )

            self.assertEqual(check["status"], "fail")
            self.assertEqual(check["failure_code"], "MEMORY_RECALL_TRACE_MISSING")

    def test_prompt_reference_gate_checks_every_prompt_file(self):
        audit = astory_repo_qa.run_repo_qa(REPO_ROOT, PROMPT_REVISION_RUN_ID)
        check = audit["checks_by_id"]["prompt_reference_gate"]

        self.assertIn("prompt_results", check)
        self.assertGreaterEqual(len(check["prompt_results"]), 4)
        self.assertTrue(
            all(item["status"] == "pass" for item in check["prompt_results"])
        )

    def test_prompt_role_reversal_checks_every_prompt_file(self):
        audit = astory_repo_qa.run_repo_qa(REPO_ROOT, PROMPT_REVISION_RUN_ID)
        check = audit["checks_by_id"]["prompt_forbidden_role_reversal"]

        self.assertIn("prompt_results", check)
        self.assertGreaterEqual(len(check["prompt_results"]), 4)
        self.assertTrue(
            all(item["status"] == "pass" for item in check["prompt_results"])
        )

    def test_heart_rent_story_contract_uses_run_contract_metadata(self):
        check = self.active_audit["checks_by_id"]["prompt_story_contract"]

        self.assertEqual(check["status"], "pass")
        self.assertEqual(check["contract_source"], "run_artifacts")
        self.assertIn("required_phrases", check)

    def test_couple_banter_story_contract_is_not_heart_rent_specific(self):
        audit = astory_repo_qa.run_repo_qa(REPO_ROOT, PROMPT_REVISION_RUN_ID)
        check = audit["checks_by_id"]["prompt_story_contract"]

        self.assertNotIn("pay rent for living in", json.dumps(check).lower())
        self.assertIn(check["status"], {"pass", "not_applicable"})

    def test_review_loop_reports_remaining_blockers_after_visibility_proof(self):
        result = astory_repo_qa.run_review_loop(
            REPO_ROOT,
            ACTIVE_RUN_ID,
            max_iterations=2,
            prepare_references=False,
        )

        self.assertEqual(result["status"], "blocked")
        self.assertGreaterEqual(len(result["iterations"]), 1)
        self.assertNotIn("REFERENCE_VISIBILITY_PROOF_INVALID", json.dumps(result))
        self.assertIn("AGENT_ASSIGNMENT_MISSING", json.dumps(result))

    def test_review_loop_has_bounded_iterations(self):
        result = astory_repo_qa.run_review_loop(
            REPO_ROOT,
            ACTIVE_RUN_ID,
            max_iterations=1,
            prepare_references=False,
        )

        self.assertEqual(len(result["iterations"]), 1)
        self.assertEqual(result["max_iterations"], 1)

    def test_review_loop_writes_machine_readable_artifact(self):
        astory_repo_qa.run_review_loop(
            REPO_ROOT,
            ACTIVE_RUN_ID,
            max_iterations=1,
            prepare_references=False,
        )

        path = REPO_ROOT / f"runs/{ACTIVE_RUN_ID}/evals/repo_qa_review_loop.json"
        self.assertTrue(path.exists())
        self.assertEqual(json.loads(path.read_text())["run_id"], ACTIVE_RUN_ID)

    def test_blocking_findings_have_failure_codes(self):
        audit = astory_repo_qa.run_repo_qa(REPO_ROOT, PROMPT_REVISION_RUN_ID)

        self.assertTrue(audit["blocking_findings"])
        self.assertTrue(
            all(finding["failure_code"] for finding in audit["blocking_findings"])
        )

    def test_active_run_blockers_and_loop_blockers_have_failure_codes(self):
        audit = astory_repo_qa.run_repo_qa(REPO_ROOT, ACTIVE_RUN_ID)
        loop = astory_repo_qa.run_review_loop(
            REPO_ROOT,
            ACTIVE_RUN_ID,
            max_iterations=1,
            prepare_references=False,
        )

        self.assertTrue(audit["blocking_findings"])
        self.assertTrue(
            all(finding["failure_code"] for finding in audit["blocking_findings"])
        )
        for iteration in loop["iterations"]:
            self.assertTrue(
                all(
                    finding["failure_code"]
                    for finding in iteration["blocking_findings"]
                )
            )

    def test_review_loop_cli_can_prepare_references_when_run_directly(self):
        result = subprocess.run(
            [
                sys.executable,
                "scripts/astory_repo_qa.py",
                "--run-id",
                ACTIVE_RUN_ID,
                "--loop",
                "--max-iterations",
                "1",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"run_id": "2026-06-10_22-22_heart-rent"', result.stdout)


if __name__ == "__main__":
    unittest.main()
