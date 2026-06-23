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

    def test_astory_skill_requires_session_learning_capture(self):
        text = (REPO_ROOT / ".agents/skills/astory/SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Session Learning Capture Gate", text)
        self.assertIn("creator correction", text.lower())
        self.assertIn("planning/creator_direction_notes.md", text)
        self.assertIn("before continuing", text.lower())

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

    def test_story_room_prompt_packets_require_creator_direction_notes(self):
        prompt_dir = REPO_ROOT / ".agents/skills/astory/templates/agents"
        for filename in [
            "story_room_agent_prompt.md",
            "visual_scene_discussion_prompt.md",
        ]:
            text = (prompt_dir / filename).read_text(encoding="utf-8")
            with self.subTest(filename=filename):
                self.assertIn(
                    "runs/{{run_id}}/planning/creator_direction_notes.md",
                    text,
                )
                self.assertIn("creator corrections", text.lower())

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

    def test_reference_load_plan_rejects_stale_loaded_reference_path_proof(self):
        checks = self.active_audit["checks_by_id"]

        self.assertEqual(checks["reference_visibility_proof"]["status"], "fail")
        self.assertEqual(
            checks["reference_visibility_proof"]["failure_code"],
            "REFERENCE_VISIBILITY_PROOF_STALE",
        )
        self.assertFalse(checks["reference_visibility_proof"]["final_imagegen_allowed"])
        self.assertGreaterEqual(
            checks["reference_visibility_proof"]["view_image_queue_count"], 4
        )
        self.assertIn(
            "runs/2026-06-10_22-22_heart-rent/evals/imagegen_reference_visibility_proof.json",
            checks["reference_visibility_proof"]["expected_artifact"],
        )

    def test_reference_visibility_proof_accepts_confirmed_roles_format(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "runs/legacy"
            (run_dir / "references-used").mkdir(parents=True)
            (run_dir / "evals").mkdir()
            queue = self._raw_identity_queue()
            aachu_refs = [
                {
                    "path": queue[0],
                    "role": "aachu_face_identity",
                    "subject": "aachu",
                    "quality": "identity",
                    "input_kind": "local_image_file",
                    "delivery_mode": "view_image_before_imagegen",
                    "view_bucket": "three_quarter",
                },
                {
                    "path": queue[1],
                    "role": "aachu_face_identity",
                    "subject": "aachu",
                    "quality": "identity",
                    "input_kind": "local_image_file",
                    "delivery_mode": "view_image_before_imagegen",
                    "view_bucket": "front",
                },
                {
                    "path": queue[2],
                    "role": "aachu_face_identity",
                    "subject": "aachu",
                    "quality": "identity",
                    "input_kind": "local_image_file",
                    "delivery_mode": "view_image_before_imagegen",
                    "view_bucket": "front",
                },
                {
                    "path": queue[3],
                    "role": "aachu_face_identity",
                    "subject": "aachu",
                    "quality": "identity",
                    "input_kind": "local_image_file",
                    "delivery_mode": "view_image_before_imagegen",
                    "view_bucket": "front",
                },
            ]
            zuv_refs = [
                {
                    "path": queue[4],
                    "role": "zuv_face_identity",
                    "subject": "zuv",
                    "quality": "identity",
                    "input_kind": "local_image_file",
                    "delivery_mode": "view_image_before_imagegen",
                    "view_bucket": "front",
                },
                {
                    "path": queue[5],
                    "role": "zuv_face_identity",
                    "subject": "zuv",
                    "quality": "identity",
                    "input_kind": "local_image_file",
                    "delivery_mode": "view_image_before_imagegen",
                    "view_bucket": "three_quarter",
                },
                {
                    "path": queue[6],
                    "role": "zuv_face_identity",
                    "subject": "zuv",
                    "quality": "identity",
                    "input_kind": "local_image_file",
                    "delivery_mode": "view_image_before_imagegen",
                    "view_bucket": "side",
                },
                {
                    "path": queue[7],
                    "role": "zuv_face_identity",
                    "subject": "zuv",
                    "quality": "identity",
                    "input_kind": "local_image_file",
                    "delivery_mode": "view_image_before_imagegen",
                    "view_bucket": "front",
                },
            ]
            manifest = {
                "schema_version": "1.0",
                "run_id": "legacy",
                "reference_groups": {
                    "aachu_face_identity": aachu_refs,
                    "zuv_face_identity": zuv_refs,
                },
                "view_image_queue": queue,
                "view_image_queue_count": len(queue),
                "load_state": {
                    "proof_artifact": "runs/legacy/evals/imagegen_reference_visibility_proof.json"
                },
            }
            proof = {
                "schema_version": "1.0",
                "run_id": "legacy",
                "status": "loaded",
                "loaded_in_current_conversation": True,
                "loading_method": "functions.view_image",
                "loaded_paths": queue,
                "loaded_count": len(queue),
                "expected_count": len(queue),
                "reference_roles_confirmed": [
                    "aachu_face_identity",
                    "zuv_face_identity",
                ],
            }
            (run_dir / "references-used/selected_references.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )
            (run_dir / "evals/imagegen_reference_visibility_proof.json").write_text(
                json.dumps(proof), encoding="utf-8"
            )

            check = astory_repo_qa._check_reference_visibility_proof(root, run_dir)

        self.assertEqual(check["status"], "pass")
        self.assertIsNone(check["failure_code"])
        self.assertTrue(check["final_imagegen_allowed"])

    def test_reference_visibility_proof_rejects_stale_load_plan_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, run_dir = self._write_minimal_visibility_run(tmp)
            proof_path = run_dir / "evals/imagegen_reference_visibility_proof.json"
            proof = json.loads(proof_path.read_text())
            proof["load_plan_sha256"] = "stale"
            proof_path.write_text(json.dumps(proof), encoding="utf-8")

            check = astory_repo_qa._check_reference_visibility_proof(root, run_dir)

            self.assertEqual(check["status"], "fail")
            self.assertEqual(
                check["failure_code"], "REFERENCE_VISIBILITY_PROOF_STALE"
            )
            self.assertFalse(check["final_imagegen_allowed"])

    def test_reference_visibility_proof_rejects_missing_active_queue_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, run_dir = self._write_minimal_visibility_run(tmp)
            proof_path = run_dir / "evals/imagegen_reference_visibility_proof.json"
            proof = json.loads(proof_path.read_text())
            proof["loaded_paths"] = ["runs/example/references-used/reference-binder/aachu.png"]
            proof_path.write_text(json.dumps(proof), encoding="utf-8")

            check = astory_repo_qa._check_reference_visibility_proof(root, run_dir)

            self.assertEqual(check["status"], "fail")
            self.assertEqual(
                check["failure_code"], "REFERENCE_VISIBILITY_PROOF_INCOMPLETE"
            )
            self.assertFalse(check["final_imagegen_allowed"])

    def test_reference_visibility_proof_rejects_binder_only_identity_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, run_dir = self._write_minimal_visibility_run(tmp)

            check = astory_repo_qa._check_reference_visibility_proof(root, run_dir)

        self.assertEqual(check["status"], "fail")
        self.assertEqual(
            check["failure_code"],
            "IDENTITY_REFERENCE_INPUT_UNPROVEN",
        )
        self.assertIn("active_queue_missing_raw_aachu_face_anchors", check["validation_errors"])
        self.assertIn("active_queue_missing_raw_zuv_face_anchors", check["validation_errors"])
        self.assertFalse(check["final_imagegen_allowed"])

    def test_missing_reference_visibility_proof_before_imagegen_is_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, run_dir = self._write_minimal_visibility_run(
                tmp, write_proof=False
            )
            (run_dir / "logs").mkdir(parents=True, exist_ok=True)
            (run_dir / "logs/trace.jsonl").write_text(
                '{"state":"GENERATE_IMAGES_WITH_IMAGEGEN","status":"complete"}\n',
                encoding="utf-8",
            )

            check = astory_repo_qa._check_reference_visibility_proof(root, run_dir)

            self.assertEqual(check["status"], "fail")
            self.assertEqual(
                check["failure_code"],
                "REFERENCE_VISIBILITY_PROOF_REQUIRED_BEFORE_FINAL_IMAGEGEN",
            )
            self.assertFalse(check["final_imagegen_allowed"])

    def test_reference_active_identity_inputs_rejects_binder_only_queue(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, run_dir = self._write_minimal_visibility_run(tmp)

            check = astory_repo_qa._check_reference_active_identity_inputs(root, run_dir)

        self.assertEqual(check["status"], "fail")
        self.assertEqual(check["failure_code"], "IDENTITY_REFERENCE_INPUT_UNPROVEN")
        self.assertIn("active_queue_missing_raw_aachu_face_anchors", check["identity_input_errors"])
        self.assertIn("active_queue_missing_raw_zuv_face_anchors", check["identity_input_errors"])

    def test_reference_active_identity_inputs_rejects_single_view_anchor_sets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "runs/example"
            (run_dir / "references-used").mkdir(parents=True)
            aachu_paths = [
                f"references/identity/aachu/aachu-face-side-{index:02d}.jpg"
                for index in range(1, 5)
            ]
            zuv_paths = [
                f"references/identity/zuv/zuv-face-side-{index:02d}.jpg"
                for index in range(1, 5)
            ]
            manifest = {
                "schema_version": "1.0",
                "run_id": "example",
                "reference_groups": {
                    "aachu_face_identity": [
                        {
                            "path": path,
                            "role": "aachu_face_identity",
                            "subject": "aachu",
                            "quality": "identity",
                            "input_kind": "local_image_file",
                            "delivery_mode": "view_image_before_imagegen",
                            "view_bucket": "side",
                            "use_for": ["face_identity"],
                            "do_not_use_for": ["pose", "head_angle", "expression_lock"],
                        }
                        for path in aachu_paths
                    ],
                    "zuv_face_identity": [
                        {
                            "path": path,
                            "role": "zuv_face_identity",
                            "subject": "zuv",
                            "quality": "identity",
                            "input_kind": "local_image_file",
                            "delivery_mode": "view_image_before_imagegen",
                            "view_bucket": "side",
                            "use_for": ["face_identity"],
                            "do_not_use_for": ["pose", "head_angle", "expression_lock"],
                        }
                        for path in zuv_paths
                    ],
                },
                "active_view_image_queue": aachu_paths + zuv_paths,
                "view_image_queue": aachu_paths + zuv_paths,
                "view_image_queue_count": 8,
            }
            (run_dir / "references-used/selected_references.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )

            check = astory_repo_qa._check_reference_active_identity_inputs(root, run_dir)

        self.assertEqual(check["status"], "fail")
        self.assertEqual(check["failure_code"], "IDENTITY_REFERENCE_DIVERSITY_MISSING")
        self.assertIn("aachu_face_identity_view_bucket_lt_2", check["identity_input_errors"])
        self.assertIn("zuv_face_identity_view_bucket_lt_2", check["identity_input_errors"])

    def test_reference_role_errors_accept_flat_face_anchor_layout(self):
        groups = {
            "aachu_face_identity": [
                {
                    "path": "references/identity/aachu/aachu-face-crop-cafe-neutral-01.jpg",
                    "role": "aachu_face_identity",
                    "subject": "aachu",
                    "quality": "identity",
                    "input_kind": "local_image_file",
                    "delivery_mode": "view_image_before_imagegen",
                }
            ],
            "zuv_face_identity": [
                {
                    "path": "references/identity/zuv/zuv-face-crop-balcony-neutral-01.jpg",
                    "role": "zuv_face_identity",
                    "subject": "zuv",
                    "quality": "identity",
                    "input_kind": "local_image_file",
                    "delivery_mode": "view_image_before_imagegen",
                }
            ],
        }

        self.assertEqual(astory_repo_qa._reference_role_errors(groups), [])

    def test_raw_identity_input_errors_accept_flat_face_anchor_layout(self):
        paths = [
            "references/identity/aachu/aachu-face-crop-cafe-neutral-01.jpg",
            "references/identity/aachu/aachu-face-crop-car-purple-01.jpg",
            "references/identity/aachu/aachu-face-crop-home-black-01.jpg",
            "references/identity/aachu/aachu-face-crop-kitchen-neutral-01.jpg",
            "references/identity/zuv/zuv-face-crop-balcony-neutral-01.jpg",
            "references/identity/zuv/zuv-face-crop-balcony-neutral-02.jpg",
            "references/identity/zuv/zuv-face-crop-balcony-neutral-03.jpg",
            "references/identity/zuv/zuv-face-crop-dinner-smile-02.jpg",
        ]

        self.assertEqual(astory_repo_qa._raw_identity_input_errors(paths), [])

    def test_prompt_palette_conflict_blocks_yellow_prone_positive_language(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "runs/example"
            (run_dir / "prompts").mkdir(parents=True)
            (run_dir / "prompts/slide_01_4x5_prompt.txt").write_text(
                "SCENE: warm lamplight and warm glow across warm ivory paper. "
                "Use terracotta red, tan pants, camel accents, cream paper, "
                "and a vintage palette. No yellow, no parchment.",
                encoding="utf-8",
            )

            check = astory_repo_qa._check_prompt_palette_conflict(
                root, run_dir, {"type": "imagegen_story_run"}
            )

        self.assertEqual(check["status"], "fail")
        self.assertEqual(check["failure_code"], "PROMPT_PALETTE_CONFLICT")
        self.assertEqual(len(check["prompt_results"]), 1)
        self.assertIn("warm lamplight", check["prompt_results"][0]["yellow_prone_terms"])

    def test_prompt_canvas_size_blocks_missing_1080x1350_portrait_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "runs/example"
            (run_dir / "prompts").mkdir(parents=True)
            (run_dir / "prompts/slide_01_prompt.txt").write_text(
                "GENERATION PRIORITY:\n"
                "Create a native 1080x1080 px @a.storyof.two illustration for slide 1.\n",
                encoding="utf-8",
            )

            check = astory_repo_qa._check_prompt_canvas_size(
                root, run_dir, {"type": "imagegen_story_run"}
            )

        self.assertEqual(check["status"], "fail")
        self.assertEqual(check["failure_code"], "PROMPT_CANVAS_SIZE_MISSING")
        self.assertIn(
            "missing_1080x1350_px",
            check["prompt_results"][0]["canvas_size_errors"],
        )
        self.assertIn(
            "non_portrait_surface_language",
            check["prompt_results"][0]["canvas_size_errors"],
        )

    def test_prompt_canvas_size_accepts_explicit_1080x1350_portrait_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "runs/example"
            (run_dir / "prompts").mkdir(parents=True)
            (run_dir / "prompts/slide_01_prompt.txt").write_text(
                "GENERATION PRIORITY:\n"
                "Create a native 1080x1350 px @a.storyof.two illustration for slide 1.\n",
                encoding="utf-8",
            )

            check = astory_repo_qa._check_prompt_canvas_size(
                root, run_dir, {"type": "imagegen_story_run"}
            )

        self.assertEqual(check["status"], "pass")
        self.assertIsNone(check["failure_code"])
        self.assertEqual(check["prompt_results"][0]["canvas_size_errors"], [])

    def test_prompt_brandmark_gate_blocks_missing_brandmark(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "runs/example"
            (run_dir / "prompts").mkdir(parents=True)
            (run_dir / "prompts/slide_01_prompt.txt").write_text(
                "Create a native 1080x1350 px illustration.\n",
                encoding="utf-8",
            )

            check = astory_repo_qa._check_prompt_brandmark_gate(
                root, run_dir, {"type": "imagegen_story_run"}
            )

        self.assertEqual(check["status"], "fail")
        self.assertEqual(check["failure_code"], "PROMPT_BRANDMARK_MISSING")
        self.assertIn("missing_at_storyof_two", check["prompt_results"][0]["brandmark_errors"])

    def test_prompt_brandmark_gate_accepts_top_right_brandmark(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "runs/example"
            (run_dir / "prompts").mkdir(parents=True)
            (run_dir / "prompts/slide_01_prompt.txt").write_text(
                "Add tiny low-contrast handwritten @a.storyof.two at top-right.\n",
                encoding="utf-8",
            )

            check = astory_repo_qa._check_prompt_brandmark_gate(
                root, run_dir, {"type": "imagegen_story_run"}
            )

        self.assertEqual(check["status"], "pass")
        self.assertIsNone(check["failure_code"])
        self.assertEqual(check["prompt_results"][0]["brandmark_errors"], [])

    def test_pre_imagegen_blocker_check_is_required_before_imagegen(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, run_dir = self._write_pre_imagegen_gate_run(tmp)

            check = astory_repo_qa._check_pre_imagegen_blocker_check(
                root, run_dir, {"type": "imagegen_story_run"}
            )

        self.assertEqual(check["status"], "fail")
        self.assertEqual(check["failure_code"], "PRE_IMAGEGEN_BLOCKER_CHECK_MISSING")
        self.assertFalse(check["final_imagegen_allowed"])

    def test_pre_imagegen_blocker_check_blocks_fallback_after_creator_correction(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, run_dir = self._write_pre_imagegen_gate_run(
                tmp,
                write_blocker_artifact=True,
                agent_assignment_status="fallback_local_passes_with_limitation_recorded",
                creator_correction=True,
            )

            check = astory_repo_qa._check_pre_imagegen_blocker_check(
                root, run_dir, {"type": "imagegen_story_run"}
            )

        self.assertEqual(check["status"], "fail")
        self.assertIn(
            "FALLBACK_REVIEW_AFTER_CREATOR_CORRECTION",
            check["computed_failure_codes"],
        )
        self.assertFalse(check["final_imagegen_allowed"])

    def test_pre_imagegen_blocker_check_blocks_smile_in_ache_prompt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, run_dir = self._write_pre_imagegen_gate_run(
                tmp,
                write_blocker_artifact=True,
                prompt_text=(
                    "GENERATION PRIORITY:\n"
                    "Create a native 1080x1350 px @a.storyof.two illustration.\n\n"
                    "ON-IMAGE TEXT:\n"
                    "Khaali hai jo tere bina,\nmain woh ghar hoon tera.\n\n"
                    "SCENE:\n"
                    "Aachu sits alone inside a crowded cafe and smiles softly, "
                    "missing him in the familiar corner.\n"
                ),
            )

            check = astory_repo_qa._check_pre_imagegen_blocker_check(
                root, run_dir, {"type": "imagegen_story_run"}
            )

        self.assertEqual(check["status"], "fail")
        self.assertIn("EMOTIONAL_STATE_CONTRADICTION", check["computed_failure_codes"])

    def test_pre_imagegen_blocker_check_blocks_broad_proceed_prompt_lock(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, run_dir = self._write_pre_imagegen_gate_run(
                tmp,
                write_blocker_artifact=True,
                creator_correction=True,
                approvals_text=(
                    "## Prompt Lock\n\n"
                    "Status: approved\n\n"
                    "Creator decision: proceed\n"
                ),
            )

            check = astory_repo_qa._check_pre_imagegen_blocker_check(
                root, run_dir, {"type": "imagegen_story_run"}
            )

        self.assertEqual(check["status"], "fail")
        self.assertIn("PROMPT_LOCK_NOT_CREATOR_VISIBLE", check["computed_failure_codes"])

    def test_pre_imagegen_blocker_check_blocks_active_cafe_reference_collision(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, run_dir = self._write_pre_imagegen_gate_run(
                tmp,
                write_blocker_artifact=True,
                manifest_paths=[
                    "references/identity/aachu/aachu-face-cafe-neutral-01.jpg",
                    "references/identity/aachu/aachu-face-crop-home-black-01.jpg",
                    "references/identity/aachu/aachu-face-crop-kitchen-neutral-01.jpg",
                    "references/identity/aachu/aachu-face-side-bridal-glance-2026-06-18-01.jpg",
                    "references/identity/zuv/zuv-face-front-blue-overshirt-selfie-2026-06-18-01.jpg",
                    "references/identity/zuv/zuv-face-three-quarter-blue-overshirt-selfie-2026-06-18-01.jpg",
                    "references/identity/zuv/zuv-face-side-indoor-white-tee-2026-06-18-01.jpg",
                    "references/identity/zuv/zuv-face-crop-balcony-neutral-01.jpg",
                    "references/style/best-illustration/slide-01.png",
                    "references/style/best-illustration/slide-02.png",
                    "references/style/best-illustration/slide-03.png",
                ],
            )

            check = astory_repo_qa._check_pre_imagegen_blocker_check(
                root, run_dir, {"type": "imagegen_story_run"}
            )

        self.assertEqual(check["status"], "fail")
        self.assertIn("IDENTITY_REFERENCE_POSE_COPY", check["computed_failure_codes"])
        self.assertIn(
            "references/identity/aachu/aachu-face-cafe-neutral-01.jpg",
            check["identity_reference_collision_check"]["unsafe_active_refs"],
        )

    def test_astory_contracts_require_1080x1350_top_right_brandmark_and_setting_gates(self):
        skill_text = (REPO_ROOT / ".agents/skills/astory/SKILL.md").read_text(
            encoding="utf-8"
        )
        master_prompt = (
            REPO_ROOT / ".agents/skills/astory/references/master-prompt.md"
        ).read_text(encoding="utf-8")
        imagegen_contract = (
            REPO_ROOT / ".agents/skills/astory/references/imagegen-contract.md"
        ).read_text(encoding="utf-8")
        visual_prompt = (
            REPO_ROOT
            / ".agents/skills/astory/templates/agents/visual_scene_discussion_prompt.md"
        ).read_text(encoding="utf-8")
        review_prompt = (
            REPO_ROOT
            / ".agents/skills/astory/templates/agents/review_room_agent_prompt.md"
        ).read_text(encoding="utf-8")
        slide_template = (
            REPO_ROOT / ".agents/skills/astory/templates/prompts/slide_prompt.txt"
        ).read_text(encoding="utf-8")

        for label, text in {
            "skill": skill_text,
            "master_prompt": master_prompt,
            "imagegen_contract": imagegen_contract,
            "slide_template": slide_template,
        }.items():
            with self.subTest(label=label):
                self.assertIn("1080x1350 px", text)
                self.assertIn("@a.storyof.two", text)
                self.assertIn("top-right", text)

        self.assertIn("visual_setting_logic", visual_prompt)
        self.assertIn("VISUAL_SETTING_CONTRADICTION", visual_prompt)
        self.assertIn("prompt_canvas_size", review_prompt)

    def test_prompt_overload_blocks_too_many_major_instruction_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "runs/example"
            (run_dir / "prompts").mkdir(parents=True)
            overloaded_prompt = "\n\n".join(
                [
                    f"SECTION {index}:\n"
                    "Instruction line one.\n"
                    "Instruction line two.\n"
                    "Instruction line three."
                    for index in range(1, 13)
                ]
            )
            (run_dir / "prompts/slide_01_4x5_prompt.txt").write_text(
                overloaded_prompt,
                encoding="utf-8",
            )

            check = astory_repo_qa._check_prompt_overload(
                root, run_dir, {"type": "imagegen_story_run"}
            )

        self.assertEqual(check["status"], "fail")
        self.assertEqual(check["failure_code"], "PROMPT_OVERLOAD")
        self.assertIn(
            "too_many_major_sections",
            check["prompt_results"][0]["overload_reasons"],
        )

    def test_prompt_overload_accepts_compact_priority_stack(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "runs/example"
            (run_dir / "prompts").mkdir(parents=True)
            compact_prompt = """GENERATION PRIORITY:
Use raw Aachu/Zuv face anchors first.

ON-IMAGE TEXT:
exact text

SCENE:
clear scene

STYLE AND COLOR:
neutral off-white watercolor-and-ink

HARD NO:
no yellow, no anime
"""
            (run_dir / "prompts/slide_01_4x5_prompt.txt").write_text(
                compact_prompt,
                encoding="utf-8",
            )

            check = astory_repo_qa._check_prompt_overload(
                root, run_dir, {"type": "imagegen_story_run"}
            )

        self.assertEqual(check["status"], "pass")
        self.assertIsNone(check["failure_code"])
        self.assertEqual(check["prompt_results"][0]["overload_reasons"], [])

    def test_gold_standard_identity_route_gate_accepts_complete_route(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "runs/example"
            self._write_gold_standard_identity_route_run(run_dir)

            audit = astory_repo_qa.run_repo_qa(root, "example")
            check = audit["checks_by_id"].get("gold_standard_identity_route_gate")

        self.assertIsNotNone(check)
        self.assertEqual(check["status"], "pass")
        self.assertEqual(check["missing_requirements"], [])

    def test_gold_standard_identity_route_gate_blocks_prompt_without_identity_priority(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "runs/example"
            self._write_gold_standard_identity_route_run(
                run_dir,
                prompt_text=(
                    "GENERATION PRIORITY:\n"
                    "Create a native 1080x1350 px @a.storyof.two illustration.\n\n"
                    "SCENE:\n"
                    "Make a cute couple scene with both faces readable in a medium-wide front three-quarter composition.\n\n"
                    "COMPOSITION AND TEXT:\n"
                    "Add tiny low-contrast handwritten @a.storyof.two at top-right.\n"
                ),
            )

            audit = astory_repo_qa.run_repo_qa(root, "example")
            check = audit["checks_by_id"].get("gold_standard_identity_route_gate")

        self.assertIsNotNone(check)
        self.assertEqual(check["status"], "fail")
        self.assertEqual(check["failure_code"], "GOLD_STANDARD_IDENTITY_ROUTE_MISSING")
        self.assertIn("prompt_raw_identity_priority", check["missing_requirements"])
        self.assertIn("prompt_blocks_binder_text_replacement", check["missing_requirements"])

    def test_gold_standard_identity_route_gate_blocks_single_anchor_pose_copy_risk(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "runs/example"
            self._write_gold_standard_identity_route_run(
                run_dir,
                prompt_text=(
                    "GENERATION PRIORITY:\n"
                    "Create a native 1080x1350 px @a.storyof.two illustration. "
                    "Use the loaded raw Aachu and Zuv face-anchor images as the highest-priority visual inputs. "
                    "Do not let style images, binders, or text descriptions replace raw face anchors.\n\n"
                    "SCENE:\n"
                    "Keep both faces readable in a medium-wide front three-quarter composition.\n\n"
                    "COMPOSITION AND TEXT:\n"
                    "Add tiny low-contrast handwritten @a.storyof.two at top-right.\n"
                ),
            )

            audit = astory_repo_qa.run_repo_qa(root, "example")
            check = audit["checks_by_id"].get("gold_standard_identity_route_gate")

        self.assertIsNotNone(check)
        self.assertEqual(check["status"], "fail")
        self.assertEqual(check["failure_code"], "GOLD_STANDARD_IDENTITY_ROUTE_MISSING")
        self.assertIn(
            "prompt_blocks_single_anchor_pose_copy",
            check["missing_requirements"],
        )


    def test_generation_attempts_block_continuing_after_hard_reject(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "runs/example"
            (run_dir / "images").mkdir(parents=True)
            attempts = {
                "schema_version": "1.0",
                "run_id": "example",
                "attempts": [
                    {
                        "slide": 1,
                        "attempt": 1,
                        "status": "rejected_after_creator_review",
                        "failure_codes": ["YELLOW_PAPER_CAST", "IDENTITY_DRIFT"],
                    },
                    {
                        "slide": 2,
                        "attempt": 1,
                        "status": "generated",
                        "failure_codes": [],
                    },
                ],
            }
            (run_dir / "images/generation_attempts.json").write_text(
                json.dumps(attempts), encoding="utf-8"
            )

            check = astory_repo_qa._check_generation_stops_after_hard_reject(run_dir)

        self.assertEqual(check["status"], "fail")
        self.assertEqual(
            check["failure_code"], "GENERATION_CONTINUED_AFTER_HARD_REJECT"
        )
        self.assertEqual(check["continued_after_hard_reject"][0]["slide"], 2)

    def test_generation_attempts_accept_acknowledged_historical_hard_reject_after_repair(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "runs/example"
            (run_dir / "images").mkdir(parents=True)
            (run_dir / "logs").mkdir()
            attempts = {
                "schema_version": "1.0",
                "run_id": "example",
                "attempts": [
                    {
                        "slide": 1,
                        "attempt": 1,
                        "status": "rejected_after_creator_review",
                        "failure_codes": ["YELLOW_PAPER_CAST", "IDENTITY_DRIFT"],
                    },
                    {
                        "slide": 2,
                        "attempt": 1,
                        "status": "rejected_after_creator_review",
                        "failure_codes": ["YELLOW_PAPER_CAST", "IDENTITY_DRIFT"],
                    },
                ],
            }
            (run_dir / "images/generation_attempts.json").write_text(
                json.dumps(attempts), encoding="utf-8"
            )
            events = [
                {
                    "state": "RETRY_OR_REVISE_IF_NEEDED",
                    "status": "repair_recorded",
                    "failure": ["GENERATION_CONTINUED_AFTER_HARD_REJECT"],
                },
                {
                    "state": "HITL_PROMPT_LOCK",
                    "status": "reapproval_required",
                    "decision": "pending_reapproval",
                },
            ]
            (run_dir / "logs/trace.jsonl").write_text(
                "".join(json.dumps(event) + "\n" for event in events),
                encoding="utf-8",
            )

            check = astory_repo_qa._check_generation_stops_after_hard_reject(run_dir)

        self.assertEqual(check["status"], "pass")
        self.assertIsNone(check["failure_code"])
        self.assertTrue(check["historical_violation_acknowledged"])
        self.assertEqual(check["continued_after_hard_reject"][0]["slide"], 2)

    def test_prompt_repair_reapproval_blocks_until_creator_approves_again(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "runs/example"
            (run_dir / "logs").mkdir(parents=True)
            events = [
                {
                    "state": "HITL_PROMPT_LOCK",
                    "status": "approved",
                    "decision": "approved",
                },
                {
                    "state": "HITL_PROMPT_LOCK",
                    "status": "reapproval_required",
                    "decision": "pending_reapproval",
                },
            ]
            (run_dir / "logs/trace.jsonl").write_text(
                "".join(json.dumps(event) + "\n" for event in events),
                encoding="utf-8",
            )

            check = astory_repo_qa._check_prompt_repair_reapproval(run_dir)

        self.assertEqual(check["status"], "fail")
        self.assertEqual(check["failure_code"], "HITL_NOT_APPROVED")
        self.assertTrue(check["reapproval_required"])
        self.assertFalse(check["reapproved_after_repair"])

    def test_prompt_repair_reapproval_passes_after_later_creator_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "runs/example"
            (run_dir / "logs").mkdir(parents=True)
            events = [
                {
                    "state": "HITL_PROMPT_LOCK",
                    "status": "reapproval_required",
                    "decision": "pending_reapproval",
                },
                {
                    "state": "HITL_PROMPT_LOCK",
                    "status": "approved",
                    "decision": "approved",
                },
            ]
            (run_dir / "logs/trace.jsonl").write_text(
                "".join(json.dumps(event) + "\n" for event in events),
                encoding="utf-8",
            )

            check = astory_repo_qa._check_prompt_repair_reapproval(run_dir)

        self.assertEqual(check["status"], "pass")
        self.assertIsNone(check["failure_code"])
        self.assertTrue(check["reapproval_required"])
        self.assertTrue(check["reapproved_after_repair"])

    def test_scene_landing_preview_blocks_approved_idea_lock_when_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "runs/example"
            (run_dir / "logs").mkdir(parents=True)
            (run_dir / "docs").mkdir()
            (run_dir / "docs/approvals.md").write_text(
                "## Idea Lock\n\nStatus: approved\n",
                encoding="utf-8",
            )
            (run_dir / "logs/trace.jsonl").write_text(
                json.dumps(
                    {
                        "state": "HITL_IDEA_LOCK",
                        "status": "approved",
                        "decision": "approved",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            check = astory_repo_qa._check_scene_landing_preview(run_dir)

        self.assertEqual(check["status"], "fail")
        self.assertEqual(check["failure_code"], "SCENE_LANDING_MISSING")
        self.assertIn("planning/scene_landing_preview.md", check["missing_requirements"])

    def test_scene_landing_preview_rejects_placeholder_or_abstract_preview(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "runs/example"
            (run_dir / "planning").mkdir(parents=True)
            (run_dir / "logs").mkdir()
            (run_dir / "docs").mkdir()
            (run_dir / "docs/approvals.md").write_text(
                "## Idea Lock\n\nStatus: approved\n",
                encoding="utf-8",
            )
            (run_dir / "logs/trace.jsonl").write_text(
                '{"state":"HITL_IDEA_LOCK","status":"approved"}\n',
                encoding="utf-8",
            )
            (run_dir / "planning/scene_landing_preview.md").write_text(
                "# Scene Landing Preview\n\n"
                "### {{title}}\n\n"
                "Score: `4.8 / 5`\n\n"
                "Rationale: highly shareable and emotionally warm.\n",
                encoding="utf-8",
            )

            check = astory_repo_qa._check_scene_landing_preview(run_dir)

        self.assertEqual(check["status"], "fail")
        self.assertEqual(check["failure_code"], "SCENE_LANDING_MISSING")
        self.assertIn("template_placeholders", check["missing_requirements"])
        self.assertIn("first_frame_visual", check["missing_requirements"])
        self.assertIn("payoff_frame", check["missing_requirements"])

    def test_scene_landing_preview_passes_for_concrete_preview_before_approved_lock(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "runs/example"
            (run_dir / "planning").mkdir(parents=True)
            (run_dir / "logs").mkdir()
            (run_dir / "docs").mkdir()
            (run_dir / "docs/approvals.md").write_text(
                "## Idea Lock\n\n"
                "Status: approved\n\n"
                "Scene landing preview: `runs/example/planning/scene_landing_preview.md`\n",
                encoding="utf-8",
            )
            (run_dir / "logs/trace.jsonl").write_text(
                '{"state":"CREATE_SCENE_LANDING_PREVIEW","status":"complete"}\n'
                '{"state":"HITL_IDEA_LOCK","status":"approved"}\n',
                encoding="utf-8",
            )
            (run_dir / "planning/scene_landing_preview.md").write_text(
                "# Scene Landing Preview\n\n"
                "Exact first-slide text: `do not open that packet. i am on a call.`\n\n"
                "First-frame visual:\n"
                "Aachu freezes mid-snack-packet tear while Zuv is on a laptop call.\n\n"
                "Why the first swipe happens:\n"
                "The viewer recognizes the tiny panic of making one loud household sound.\n\n"
                "Mini slide arc:\n"
                "1. Call begins.\n2. Packet crackles.\n3. Roles reverse with a spoon clink.\n4. They eat together after the call.\n\n"
                "Payoff frame:\n"
                "The packet is finally open between them and both are laughing.\n\n"
                "Why someone sends it:\n"
                "Send to the partner who freezes during your meetings.\n\n"
                "What could make it land flat/generic:\n"
                "If it becomes generic work-call humor.\n\n"
                "Correction if it feels flat:\n"
                "Keep the role reversal and the guilty body language.\n",
                encoding="utf-8",
            )

            check = astory_repo_qa._check_scene_landing_preview(run_dir)

        self.assertEqual(check["status"], "pass")
        self.assertIsNone(check["failure_code"])
        self.assertFalse(check["missing_requirements"])

    def test_source_winner_novelty_model_blocks_when_contract_exists_but_model_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "runs/example"
            (run_dir / "planning").mkdir(parents=True)
            (run_dir / "planning/source_winner_remix_contract.json").write_text(
                json.dumps(
                    {
                        "remix_mode": "permissioned_source_preserving_remix",
                        "source_winner": {
                            "source_url": "https://www.instagram.com/p/example/"
                        },
                    }
                ),
                encoding="utf-8",
            )

            check = astory_repo_qa._check_source_winner_novelty_model(run_dir)

        self.assertEqual(check["status"], "fail")
        self.assertEqual(
            check["failure_code"], "SOURCE_WINNER_NOVELTY_MODEL_MISSING"
        )
        self.assertIn(
            "planning/source_winner_novelty_model.json",
            check["missing_requirements"],
        )

    def test_source_winner_novelty_model_rejects_placeholder_modeling(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "runs/example"
            (run_dir / "planning").mkdir(parents=True)
            (run_dir / "planning/source_winner_remix_contract.json").write_text(
                json.dumps({"remix_mode": "permissioned_source_preserving_remix"}),
                encoding="utf-8",
            )
            (run_dir / "planning/source_winner_novelty_model.json").write_text(
                json.dumps(
                    {
                        "framework_reference": "{{framework_reference}}",
                        "source_winner": {"source_url": ""},
                        "illusion_of_novelty_model": {
                            "new_reveal": "",
                            "viewer_outcome": "send",
                            "contrast_frame": "",
                            "urgency": {"used": False, "reason": ""},
                            "bullseye_proof": "",
                            "protect_the_illusion": "",
                        },
                        "a_story_translation": {
                            "what_stays_from_source": "",
                            "what_changes_for_aachu_zuv": "",
                            "lived_scene_wrapper": "",
                            "lines_to_remove_because_they_explain_the_lesson": [],
                        },
                    }
                ),
                encoding="utf-8",
            )

            check = astory_repo_qa._check_source_winner_novelty_model(run_dir)

        self.assertEqual(check["status"], "fail")
        self.assertIn("template_placeholders", check["missing_requirements"])
        self.assertIn("illusion_of_novelty_model.new_reveal", check["missing_requirements"])
        self.assertIn("a_story_translation.lived_scene_wrapper", check["missing_requirements"])

    def test_source_winner_novelty_model_passes_for_complete_modeling(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "runs/example"
            (run_dir / "planning").mkdir(parents=True)
            (run_dir / "planning/source_winner_remix_contract.json").write_text(
                json.dumps(
                    {
                        "remix_mode": "permissioned_source_preserving_remix",
                        "source_winner": {
                            "source_url": "https://www.instagram.com/p/example/"
                        },
                    }
                ),
                encoding="utf-8",
            )
            (run_dir / "planning/source_winner_novelty_model.json").write_text(
                json.dumps(
                    {
                        "framework_reference": "references/text-style/illusion-of-novelty-storytelling-2026-06-18.md",
                        "source_winner": {
                            "source_url": "https://www.instagram.com/p/example/",
                            "old_familiar_topic": "after-fight care",
                        },
                        "illusion_of_novelty_model": {
                            "new_reveal": "the apology starts before sorry",
                            "viewer_outcome": "send it without speaking first",
                            "contrast_frame": "people notice apologies, not the plate served during silence",
                            "urgency": {
                                "used": True,
                                "reason": "few minutes after a fight before pride hardens",
                            },
                            "bullseye_proof": "a plate is still placed on the table",
                            "protect_the_illusion": "do not explain this as communication",
                        },
                        "a_story_translation": {
                            "what_stays_from_source": "the after-fight care engine",
                            "what_changes_for_aachu_zuv": "Aachu and Zuv carry it through a dinner table scene",
                            "lived_scene_wrapper": "one plate arrives while both pretend not to look",
                            "lines_to_remove_because_they_explain_the_lesson": [
                                "communication matters"
                            ],
                        },
                    }
                ),
                encoding="utf-8",
            )

            check = astory_repo_qa._check_source_winner_novelty_model(run_dir)

        self.assertEqual(check["status"], "pass")
        self.assertIsNone(check["failure_code"])
        self.assertFalse(check["missing_requirements"])

    def test_novelty_candidate_ledger_not_applicable_before_idea_lock_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "runs/example"
            (run_dir / "planning").mkdir(parents=True)

            check = astory_repo_qa._check_novelty_candidate_ledger(run_dir)

        self.assertEqual(check["status"], "not_applicable")
        self.assertEqual(check["severity"], "info")

    def test_novelty_candidate_ledger_blocks_approved_idea_lock_when_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "runs/example"
            (run_dir / "logs").mkdir(parents=True)
            (run_dir / "docs").mkdir()
            (run_dir / "docs/approvals.md").write_text(
                "## Idea Lock\n\nStatus: approved\n",
                encoding="utf-8",
            )
            (run_dir / "logs/trace.jsonl").write_text(
                '{"state":"HITL_IDEA_LOCK","status":"approved"}\n',
                encoding="utf-8",
            )

            check = astory_repo_qa._check_novelty_candidate_ledger(run_dir)

        self.assertEqual(check["status"], "fail")
        self.assertEqual(
            check["failure_code"], "NOVELTY_CANDIDATE_LEDGER_MISSING"
        )
        self.assertIn(
            "planning/novelty_candidate_ledger.json",
            check["missing_requirements"],
        )

    def test_novelty_candidate_ledger_rejects_placeholder_or_empty_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "runs/example"
            (run_dir / "planning").mkdir(parents=True)
            (run_dir / "logs").mkdir()
            (run_dir / "logs/trace.jsonl").write_text(
                '{"state":"SCORE_IDEAS","status":"complete"}\n',
                encoding="utf-8",
            )
            (run_dir / "planning/novelty_candidate_ledger.json").write_text(
                json.dumps(
                    {
                        "run_id": "{{run_id}}",
                        "source_bank_search": {"used_winner_bank": True},
                        "candidates": [],
                        "selected_candidate_id": "",
                        "gate": "pass",
                    }
                ),
                encoding="utf-8",
            )

            check = astory_repo_qa._check_novelty_candidate_ledger(run_dir)

        self.assertEqual(check["status"], "fail")
        self.assertIn("template_placeholders", check["missing_requirements"])
        self.assertIn("candidates", check["missing_requirements"])
        self.assertIn("selected_candidate_id", check["missing_requirements"])

    def test_novelty_candidate_ledger_passes_for_complete_selected_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "runs/example"
            (run_dir / "planning").mkdir(parents=True)
            (run_dir / "logs").mkdir()
            (run_dir / "logs/trace.jsonl").write_text(
                '{"state":"SCORE_IDEAS","status":"complete"}\n',
                encoding="utf-8",
            )
            (run_dir / "planning/novelty_candidate_ledger.json").write_text(
                json.dumps(
                    {
                        "run_id": "example",
                        "status": "draft",
                        "source_bank_search": {
                            "used_winner_bank": True,
                            "bank_paths": [
                                "references/text-style/winner-bank/winner_bank.json"
                            ],
                            "evidence_gap": "",
                        },
                        "candidates": [
                            {
                                "candidate_id": "idea_001",
                                "title": "The plate arrives before sorry",
                                "source_winner": {
                                    "source_url": "https://www.instagram.com/p/example/",
                                    "source_account": "source_account",
                                    "source_shortcode": "example",
                                    "metric_signal": "high saves per reach",
                                },
                                "source_engine": {
                                    "old_familiar_topic": "after-fight care",
                                    "first_frame_stop": "silent dinner table",
                                    "swipe_reason": "see who softens first",
                                    "send_or_save_trigger": "send after a fight",
                                    "what_must_stay": "care before apology",
                                },
                                "novelty_model": {
                                    "new_reveal": "the apology starts before sorry",
                                    "viewer_outcome": "send without speaking first",
                                    "contrast_frame": "people notice words, not the plate",
                                    "urgency": {
                                        "used": False,
                                        "reason": "emotional timing, not news",
                                    },
                                    "bullseye_proof": "one plate placed during silence",
                                    "protect_the_illusion": "do not call it communication",
                                },
                                "a_story_wrappers": [
                                    {
                                        "wrapper_id": "wrapper_001",
                                        "wrapper_type": "scene",
                                        "what_changes_for_aachu_zuv": "Aachu and Zuv carry it through dinner",
                                        "lived_scene_wrapper": "one plate arrives while both avoid eye contact",
                                        "visual_proof": "plate set down without looking",
                                        "send_or_comment_trigger": "send to the stubborn one",
                                        "flat_or_generic_risk": "explaining the moral",
                                    }
                                ],
                                "selection_scores": {
                                    "winner_fit": 5,
                                    "source_preservation": 5,
                                    "novelty_strength": 4,
                                    "aachu_zuv_specificity": 4,
                                    "send_save_trigger": 5,
                                    "anti_slop_risk": 2,
                                    "visual_proof_potential": 5,
                                    "total": 30,
                                },
                                "decision": "selected",
                                "rejection_reason": "",
                            }
                        ],
                        "selected_candidate_id": "idea_001",
                        "rejected_generic_versions": ["small gestures matter"],
                        "gate": "pass",
                    }
                ),
                encoding="utf-8",
            )

            check = astory_repo_qa._check_novelty_candidate_ledger(run_dir)

        self.assertEqual(check["status"], "pass")
        self.assertIsNone(check["failure_code"])
        self.assertFalse(check["missing_requirements"])

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

    def test_rejected_image_qa_blocks_final_package_with_failure_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "runs/example"
            (run_dir / "evals").mkdir(parents=True)
            (run_dir / "evals/image_quality_eval.json").write_text(
                json.dumps(
                    {
                        "status": "blocked",
                        "hard_gate_result": "rejected_after_creator_review",
                        "candidates_reviewed": [
                            {
                                "path": "runs/example/images/slide_01.png",
                                "status": "rejected_after_creator_review",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            check = astory_repo_qa._check_image_qa_blocks_final_package(run_dir)

        self.assertEqual(check["status"], "pass")
        self.assertEqual(check["failure_code"], "IMAGE_QA_FAILED")
        self.assertEqual(check["hard_gate_result"], "rejected_after_creator_review")

    def test_final_package_without_illustration_proof_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "runs/example"
            (run_dir / "evals").mkdir(parents=True)
            (run_dir / "corrected-exact-source-carousel").mkdir()
            (run_dir / "corrected-exact-source-carousel/slide-01.png").write_bytes(
                b"not-a-real-png-for-this-check"
            )
            (run_dir / "evals/final_qa_exact_source_carousel.json").write_text(
                json.dumps({"decision": "ready_for_creator_review"}),
                encoding="utf-8",
            )

            check = astory_repo_qa._check_final_package_has_illustration_proof(
                run_dir
            )

        self.assertEqual(check["status"], "fail")
        self.assertEqual(check["failure_code"], "QUOTE_CARD_NOT_ILLUSTRATION")
        self.assertFalse(check["imagegen_attempted"])
        self.assertFalse(check["scene_artifacts_present"])

    def _raw_identity_queue(self):
        return [
            "references/identity/aachu/face/aachu-face-crop-car-purple-01.jpg",
            "references/identity/aachu/face/aachu-face-crop-cafe-neutral-01.jpg",
            "references/identity/aachu/face/aachu-face-crop-home-black-01.jpg",
            "references/identity/aachu/face/aachu-face-crop-kitchen-neutral-01.jpg",
            "references/identity/zuv/face/zuv-face-crop-balcony-neutral-01.jpg",
            "references/identity/zuv/face/zuv-face-crop-balcony-neutral-02.jpg",
            "references/identity/zuv/face/zuv-face-crop-balcony-neutral-03.jpg",
            "references/identity/zuv/face/zuv-face-crop-dinner-smile-02.jpg",
        ]

    def _write_minimal_visibility_run(self, tmp, write_proof=True):
        root = Path(tmp)
        run_dir = root / "runs/example"
        (run_dir / "references-used").mkdir(parents=True)
        (run_dir / "evals").mkdir()
        queue = [
            "runs/example/references-used/reference-binder/aachu.png",
            "runs/example/references-used/reference-binder/zuv.png",
        ]
        manifest = {
            "schema_version": "1.0",
            "run_id": "example",
            "reference_groups": {"aachu_face_identity": [], "zuv_face_identity": []},
            "load_plan_sha256": "current-load-plan",
            "view_image_queue": queue,
            "view_image_queue_count": len(queue),
            "active_view_image_queue": queue,
            "generation_reference_packet_queue": [
                {"path": queue[0], "role": "aachu_identity_binder"},
                {"path": queue[1], "role": "zuv_identity_binder"},
            ],
            "load_state": {
                "proof_artifact": "runs/example/evals/imagegen_reference_visibility_proof.json"
            },
        }
        (run_dir / "references-used/selected_references.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
        if write_proof:
            proof = {
                "schema_version": "1.0",
                "run_id": "example",
                "status": "loaded",
                "loaded_in_current_conversation": True,
                "loading_method": "functions.view_image",
                "load_plan_sha256": "current-load-plan",
                "loaded_paths": queue,
                "loaded_count": len(queue),
                "expected_count": len(queue),
                "references": [
                    {"path": queue[0], "role": "aachu_identity_binder"},
                    {"path": queue[1], "role": "zuv_identity_binder"},
                ],
            }
            (run_dir / "evals/imagegen_reference_visibility_proof.json").write_text(
                json.dumps(proof), encoding="utf-8"
            )
        return root, run_dir

    def _write_gold_standard_identity_route_run(self, run_dir, prompt_text=None):
        (run_dir / "references-used").mkdir(parents=True)
        (run_dir / "evals").mkdir()
        (run_dir / "prompts").mkdir()
        (run_dir / "debates/prompt_room").mkdir(parents=True)
        (run_dir / "planning").mkdir()
        (run_dir / "logs").mkdir()

        queue = [
            "references/identity/aachu/aachu-face-cafe-neutral-01.jpg",
            "references/identity/aachu/aachu-face-crop-cafe-neutral-01.jpg",
            "references/identity/aachu/aachu-face-crop-car-purple-01.jpg",
            "references/identity/aachu/aachu-face-crop-home-black-01.jpg",
            "references/identity/zuv/face-01.png",
            "references/identity/zuv/face-03.png",
            "references/identity/zuv/zuv-face-crop-balcony-laugh-01.jpg",
            "references/identity/zuv/zuv-face-crop-balcony-neutral-01.jpg",
            "references/style/best-illustration/encoded-check-000.png",
            "references/style/best-illustration/road-trip-best-reduced-tan-50-4x5.png",
            "references/style/best-illustration/slide-01.png",
        ]
        manifest = {
            "schema_version": "1.0",
            "run_id": "example",
            "load_plan_sha256": "gold-route",
            "reference_groups": {
                "aachu_face_identity": [{"path": path} for path in queue[:4]],
                "zuv_face_identity": [{"path": path} for path in queue[4:8]],
                "style_reference": [{"path": path} for path in queue[8:]],
            },
            "view_image_queue": queue,
            "view_image_queue_count": len(queue),
            "active_view_image_queue": queue,
            "load_state": {
                "proof_artifact": "runs/example/evals/imagegen_reference_visibility_proof.json"
            },
        }
        proof = {
            "schema_version": "1.0",
            "run_id": "example",
            "status": "loaded",
            "loaded_in_current_conversation": True,
            "loading_method": "view_image",
            "load_plan_sha256": "gold-route",
            "loaded_paths": queue,
            "loaded_count": len(queue),
            "expected_count": len(queue),
            "reference_roles_confirmed": [
                "aachu_face_identity",
                "zuv_face_identity",
                "style_reference",
            ],
        }
        pregen = {
            "run_id": "example",
            "status": "pass",
            "agent_assignment_status": "fallback_local_passes_with_limitation_recorded",
            "prompt_room_outputs": [
                "runs/example/debates/prompt_room/prompt_review.md"
            ],
        }
        if prompt_text is None:
            prompt_text = (
                "GENERATION PRIORITY:\n"
                "Create a native 1080x1350 px @a.storyof.two illustration. "
                "Use the loaded raw Aachu and Zuv face-anchor images as the highest-priority visual inputs. "
                "Do not let style images, binders, or text descriptions replace raw face anchors. "
                "Use multiple face anchors for identity structure only; do not copy any single anchor's pose, head angle, eye state, expression, wardrobe, lighting, background, or camera position.\n\n"
                "SCENE:\n"
                "Keep both faces readable in a medium-wide, slightly high front three-quarter composition.\n\n"
                "COMPOSITION AND TEXT:\n"
                "Add tiny low-contrast handwritten @a.storyof.two at top-right.\n"
            )

        (run_dir / "references-used/selected_references.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
        (run_dir / "evals/imagegen_reference_visibility_proof.json").write_text(
            json.dumps(proof), encoding="utf-8"
        )
        (run_dir / "evals/pre_generation_eval.json").write_text(
            json.dumps(pregen), encoding="utf-8"
        )
        (run_dir / "prompts/slide_01_prompt.txt").write_text(
            prompt_text, encoding="utf-8"
        )
        (run_dir / "debates/agent_assignment_matrix.md").write_text(
            "fallback_local_passes_with_limitation_recorded\n", encoding="utf-8"
        )
        (run_dir / "debates/prompt_room/prompt_review.md").write_text(
            "Identity Guardian pass: raw face anchors are highest priority.\n",
            encoding="utf-8",
        )
        for rel in [
            "planning/scene_landing_preview.md",
            "planning/scene_options.json",
            "planning/selected_idea.json",
            "planning/slide_beat_map.json",
            "planning/slide_count_decision.md",
        ]:
            (run_dir / rel).write_text("{}\n", encoding="utf-8")
        events = [
            {"state": "CREATE_SCENE_LANDING_PREVIEW", "status": "complete"},
            {"state": "DISCOVER_AND_ASSIGN_AGENTS", "status": "fallback_local_passes"},
            {"state": "LOAD_REFERENCE_IMAGES_IN_CONTEXT", "status": "complete"},
            {"state": "PRE_GENERATION_EVAL", "status": "pass"},
        ]
        (run_dir / "logs/trace.jsonl").write_text(
            "".join(json.dumps(event) + "\n" for event in events),
            encoding="utf-8",
        )

    def _write_pre_imagegen_gate_run(
        self,
        tmp,
        *,
        write_blocker_artifact=False,
        agent_assignment_status="actual_multi_agent",
        creator_correction=False,
        approvals_text=None,
        prompt_text=None,
        manifest_paths=None,
    ):
        root = Path(tmp)
        run_dir = root / "runs/example"
        (run_dir / "evals").mkdir(parents=True)
        (run_dir / "prompts").mkdir()
        (run_dir / "references-used").mkdir()
        (run_dir / "logs").mkdir()
        (run_dir / "docs").mkdir()
        if prompt_text is None:
            prompt_text = (
                "GENERATION PRIORITY:\n"
                "Create a native 1080x1350 px @a.storyof.two illustration.\n\n"
                "ON-IMAGE TEXT:\n"
                "Khaali hai jo tere bina,\nmain woh ghar hoon tera.\n\n"
                "SCENE:\n"
                "Aachu sits at a crowded cafe friends table, lips relaxed and unsmiling.\n"
            )
        (run_dir / "prompts/slide_01_prompt.txt").write_text(
            prompt_text, encoding="utf-8"
        )
        if manifest_paths is None:
            manifest_paths = [
                "references/identity/aachu/aachu-face-crop-cafe-neutral-01.jpg",
                "references/identity/aachu/aachu-face-crop-home-black-01.jpg",
                "references/identity/aachu/aachu-face-crop-kitchen-neutral-01.jpg",
                "references/identity/aachu/aachu-face-side-bridal-glance-2026-06-18-01.jpg",
                "references/identity/zuv/zuv-face-front-blue-overshirt-selfie-2026-06-18-01.jpg",
                "references/identity/zuv/zuv-face-three-quarter-blue-overshirt-selfie-2026-06-18-01.jpg",
                "references/identity/zuv/zuv-face-side-indoor-white-tee-2026-06-18-01.jpg",
                "references/identity/zuv/zuv-face-crop-balcony-neutral-01.jpg",
                "references/style/best-illustration/slide-01.png",
                "references/style/best-illustration/slide-02.png",
                "references/style/best-illustration/slide-03.png",
            ]
        manifest = {
            "schema_version": "1.0",
            "run_id": "example",
            "reference_groups": {},
            "active_view_image_queue": manifest_paths,
            "view_image_queue": manifest_paths,
            "view_image_queue_count": len(manifest_paths),
        }
        (run_dir / "references-used/selected_references.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
        (run_dir / "evals/pre_generation_eval.json").write_text(
            json.dumps(
                {
                    "run_id": "example",
                    "status": "pass",
                    "agent_assignment_status": agent_assignment_status,
                    "prompt_room_outputs": [
                        "runs/example/debates/prompt_room/prompt_review.md"
                    ],
                }
            ),
            encoding="utf-8",
        )
        approvals = approvals_text
        if approvals is None:
            approvals = (
                "## Prompt Lock\n\n"
                "Status: approved\n\n"
                "Prompt summary: slide 1 is visible and reviewed.\n"
                "Prompt files: `runs/example/prompts/slide_01_prompt.txt`\n"
            )
        (run_dir / "docs/approvals.md").write_text(approvals, encoding="utf-8")
        events = []
        if creator_correction:
            (run_dir / "planning").mkdir()
            (run_dir / "planning/creator_direction_notes.md").write_text(
                "Major creator correction: no smile, no copied cafe identity photo.\n",
                encoding="utf-8",
            )
            events.append(
                {
                    "state": "SESSION_LEARNING_CAPTURE",
                    "status": "complete",
                    "correction_type": "major_visual_correction",
                }
            )
        events.append({"state": "LOAD_REFERENCE_IMAGES_IN_CONTEXT", "status": "complete"})
        (run_dir / "logs/trace.jsonl").write_text(
            "".join(json.dumps(event) + "\n" for event in events),
            encoding="utf-8",
        )
        if write_blocker_artifact:
            (run_dir / "evals/pre_imagegen_blocker_check.json").write_text(
                json.dumps(
                    {
                        "schema_version": "1.0",
                        "run_id": "example",
                        "status": "pass",
                        "emotional_state_check": {"status": "pass"},
                        "identity_reference_collision_check": {"status": "pass"},
                        "fallback_review_check": {"status": "pass"},
                        "creator_prompt_lock_check": {"status": "pass"},
                        "canvas_output_expectation": {"status": "pass"},
                        "imagegen_allowed": True,
                    }
                ),
                encoding="utf-8",
            )
        return root, run_dir

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

    def test_hitl_order_passes_for_pre_imagegen_ready_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "runs/example"
            (run_dir / "logs").mkdir(parents=True)
            events = [
                {"state": "HITL_IDEA_LOCK", "status": "approved_with_revision"},
                {"state": "HITL_STORY_LOCK", "status": "approved"},
                {"state": "HITL_PROMPT_LOCK", "status": "approved"},
                {"state": "LOAD_REFERENCE_IMAGES_IN_CONTEXT", "status": "complete"},
            ]
            (run_dir / "logs/trace.jsonl").write_text(
                "".join(json.dumps(event) + "\n" for event in events),
                encoding="utf-8",
            )

            check = astory_repo_qa._check_hitl_order_before_imagegen(run_dir)

        self.assertEqual(check["status"], "pass")
        self.assertEqual(check["event_indices"]["imagegen"], None)
        self.assertEqual(check["order_state"], "pre_imagegen_ready")
        self.assertIsNone(check["failure_code"])

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
