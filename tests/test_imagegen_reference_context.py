import unittest
import tempfile
from pathlib import Path

from PIL import Image

from scripts.prepare_imagegen_reference_context import (
    build_reference_context,
    write_reference_context,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class ImagegenReferenceContextTests(unittest.TestCase):
    def setUp(self):
        self.repo_root = REPO_ROOT

    def test_builds_local_view_image_queue_without_manual_attachments(self):
        context = build_reference_context(
            self.repo_root, "2026-06-10_22-22_heart-rent"
        )

        self.assertEqual(context["status"], "ready_to_load_with_view_image")
        self.assertFalse(context["manual_user_attachments_required"])
        self.assertFalse(context["prompt_only_allowed"])
        self.assertGreaterEqual(context["raw_reference_queue_count"], 10)
        self.assertGreaterEqual(context["view_image_queue_count"], 4)
        self.assertIn(
            "references/identity/aachu/aachu-face-side-bridal-glance-2026-06-18-01.jpg",
            context["view_image_queue"],
        )
        self.assertIn(
            "references/identity/zuv/zuv-face-front-blue-overshirt-selfie-2026-06-18-01.jpg",
            context["view_image_queue"],
        )

    def test_face_visible_queue_has_required_aachu_and_zuv_face_anchors(self):
        context = build_reference_context(
            self.repo_root, "2026-06-10_22-22_heart-rent"
        )

        self.assertGreaterEqual(
            len(context["reference_groups"]["aachu_face_identity"]), 4
        )
        self.assertGreaterEqual(
            len(context["reference_groups"]["zuv_face_identity"]), 4
        )
        for group in (
            "aachu_face_identity",
            "zuv_face_identity",
            "expression_support",
            "together_body_language",
            "style",
        ):
            for reference in context["reference_groups"][group]:
                self.assertEqual(
                    reference["delivery_mode"], "view_image_before_imagegen"
                )
                self.assertTrue((self.repo_root / reference["path"]).exists())

    def test_face_identity_records_are_identity_only_not_pose_templates(self):
        context = build_reference_context(
            self.repo_root, "2026-06-10_22-22_heart-rent"
        )

        for group_name in ("aachu_face_identity", "zuv_face_identity"):
            with self.subTest(group_name=group_name):
                records = context["reference_groups"][group_name]
                self.assertGreaterEqual(len(records), 4)
                for reference in records:
                    self.assertIn("face_identity", reference["use_for"])
                    self.assertIn(
                        "identity_structure_not_pose_template",
                        reference["usage_contract"]["mode"],
                    )
                    self.assertIn("head_angle", reference["do_not_use_for"])
                    self.assertIn("expression_lock", reference["do_not_use_for"])
                    self.assertIn("pose", reference["do_not_use_for"])
                    self.assertIn("wardrobe", reference["do_not_use_for"])

        summary = context["identity_reference_summary"]
        self.assertGreaterEqual(summary["aachu"]["view_bucket_count"], 2)
        self.assertGreaterEqual(summary["zuv"]["view_bucket_count"], 2)

    def test_selects_multi_angle_face_anchors_before_same_angle_duplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            run_id = "2099-01-01_identity-diversity"
            (repo_root / "runs" / run_id).mkdir(parents=True)
            self._write_minimal_reference_repo(repo_root)
            for subject in ("aachu", "zuv"):
                for filename in [
                    f"{subject}-face-front-01.jpg",
                    f"{subject}-face-front-02.jpg",
                    f"{subject}-face-three-quarter-left-01.jpg",
                    f"{subject}-face-side-01.jpg",
                    f"{subject}-face-smile-front-01.jpg",
                ]:
                    self._write_image(repo_root / "references" / "identity" / subject / filename)

            context = build_reference_context(repo_root, run_id)

        for group_name in ("aachu_face_identity", "zuv_face_identity"):
            selected = context["reference_groups"][group_name]
            buckets = {reference["view_bucket"] for reference in selected}
            self.assertGreaterEqual(len(buckets), 2)
            self.assertIn("front", buckets)
            self.assertTrue({"three_quarter", "side"} & buckets)

    def test_face_anchors_are_discovered_from_flat_identity_folders(self):
        context = build_reference_context(REPO_ROOT, "2026-06-10_22-22_heart-rent")

        for reference in context["reference_groups"]["aachu_face_identity"]:
            self.assertTrue(reference["path"].startswith("references/identity/aachu/"))
            self.assertEqual(reference["subject"], "aachu")
        for reference in context["reference_groups"]["zuv_face_identity"]:
            self.assertTrue(reference["path"].startswith("references/identity/zuv/"))
            self.assertEqual(reference["subject"], "zuv")

    def test_couple_banter_includes_current_request_images(self):
        context = build_reference_context(
            REPO_ROOT, "2026-06-10_22-55_couple-banter"
        )
        current_request = context["reference_groups"]["current_request"]

        self.assertGreaterEqual(len(current_request), 1)
        self.assertTrue(
            all(item["role"] == "current_request" for item in current_request)
        )
        self.assertFalse(context["manual_user_attachments_required"])
        self.assertFalse(context["prompt_only_allowed"])

    def test_current_request_images_are_analysis_only_not_active_inputs(self):
        context = build_reference_context(
            REPO_ROOT, "2026-06-10_22-55_couple-banter"
        )
        current_request_paths = [
            item["path"] for item in context["reference_groups"]["current_request"]
        ]

        self.assertGreaterEqual(len(current_request_paths), 1)
        for path in current_request_paths:
            self.assertIn(path, context["raw_reference_queue"])
            self.assertNotIn(path, context["active_view_image_queue"])
            self.assertNotIn(path, context["view_image_queue"])

        current_request_packets = [
            packet
            for packet in context["generation_reference_packet_queue"]
            if packet["role"] == "current_request_binder"
        ]
        self.assertEqual(len(current_request_packets), 1)
        self.assertEqual(
            current_request_packets[0]["source_paths"],
            current_request_paths,
        )

    def test_style_references_come_from_best_illustration_as_loadable_images(self):
        context = build_reference_context(REPO_ROOT, "2026-06-10_22-22_heart-rent")
        style_refs = context["reference_groups"]["style"]

        self.assertGreaterEqual(len(style_refs), 1)
        self.assertTrue(
            all(item["input_kind"] == "local_image_file" for item in style_refs)
        )
        self.assertTrue(
            all(
                item["path"].startswith("references/style/best-illustration/")
                for item in style_refs
            )
        )
        self.assertTrue(
            all(
                item["delivery_mode"] == "view_image_before_imagegen"
                for item in style_refs
            )
        )

    def test_active_queue_uses_raw_face_anchors_not_binders(self):
        context = build_reference_context(
            REPO_ROOT, "2026-06-10_22-55_couple-banter"
        )

        self.assertEqual(
            context["reference_delivery_strategy"], "raw_identity_first_v1"
        )
        self.assertIn("load_plan_sha256", context)
        self.assertGreater(len(context["load_plan_sha256"]), 20)
        self.assertEqual(
            context["raw_reference_queue_count"], len(context["raw_reference_queue"])
        )
        self.assertEqual(
            context["generation_reference_packet_queue_count"],
            len(context["generation_reference_packet_queue"]),
        )
        self.assertEqual(context["view_image_queue"], context["active_view_image_queue"])
        self.assertTrue(
            all(
                "runs/" not in path or "/reference-binder/" not in path
                for path in context["active_view_image_queue"]
            )
        )
        aachu_identity = [
            reference["path"]
            for reference in context["reference_groups"]["aachu_face_identity"]
        ]
        zuv_identity = [
            reference["path"]
            for reference in context["reference_groups"]["zuv_face_identity"]
        ]
        self.assertEqual(
            context["active_view_image_queue"][: len(aachu_identity)],
            aachu_identity,
        )
        self.assertEqual(
            context["active_view_image_queue"][
                len(aachu_identity) : len(aachu_identity) + len(zuv_identity)
            ],
            zuv_identity,
        )
        self.assertGreaterEqual(
            len(aachu_identity),
            4,
        )
        self.assertGreaterEqual(
            len(zuv_identity),
            4,
        )
        self.assertGreaterEqual(
            sum(
                path.startswith("references/identity/aachu/")
                for path in context["active_view_image_queue"]
            ),
            4,
        )
        self.assertGreaterEqual(
            sum(
                path.startswith("references/identity/zuv/")
                for path in context["active_view_image_queue"]
            ),
            4,
        )
        roles = {
            packet["role"]
            for packet in context["generation_reference_packet_queue"]
        }
        self.assertIn("aachu_identity_binder", roles)
        self.assertIn("zuv_identity_binder", roles)
        self.assertIn("style_binder", roles)
        self.assertIn("current_request_binder", roles)

    def test_write_reference_context_preserves_raw_active_queue_after_binder_write(self):
        context = build_reference_context(
            REPO_ROOT, "2026-06-10_22-55_couple-banter"
        )
        expected_queue = list(context["active_view_image_queue"])

        write_reference_context(REPO_ROOT, context)

        self.assertEqual(context["active_view_image_queue"], expected_queue)
        self.assertEqual(context["view_image_queue"], expected_queue)
        self.assertTrue(
            all(
                "runs/" not in path or "/reference-binder/" not in path
                for path in context["view_image_queue"]
            )
        )

    def test_write_reference_context_creates_hashed_binder_images(self):
        context = build_reference_context(
            REPO_ROOT, "2026-06-10_22-55_couple-banter"
        )

        write_reference_context(REPO_ROOT, context)

        for packet in context["generation_reference_packet_queue"]:
            path = REPO_ROOT / packet["path"]
            with self.subTest(path=packet["path"]):
                self.assertTrue(path.exists())
                self.assertEqual(path.suffix.lower(), ".png")
                self.assertEqual(packet["input_kind"], "generated_reference_binder")
                self.assertGreater(packet["size_bytes"], 0)
                self.assertGreater(len(packet["sha256"]), 20)

    def test_full_scene_cafe_identity_ref_is_demoted_for_cafe_prompt(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            run_id = "2099-01-01_cafe-loneliness"
            run_root = repo_root / "runs" / run_id
            (run_root / "prompts").mkdir(parents=True)
            self._write_minimal_reference_repo(repo_root)
            self._write_identity_fixture(repo_root)
            (run_root / "prompts/slide_01_prompt.txt").write_text(
                "SCENE:\n"
                "Aachu sits at a crowded cafe friends table, lost and unsmiling.\n",
                encoding="utf-8",
            )

            context = build_reference_context(repo_root, run_id)

        unsafe_ref = "references/identity/aachu/aachu-face-cafe-neutral-01.jpg"
        self.assertNotIn(unsafe_ref, context["active_view_image_queue"])
        self.assertIn(
            unsafe_ref,
            context["reference_policy_summary"]["analysis_only_refs"],
        )
        self.assertIn(
            "scene_overlap:cafe",
            context["reference_policy_summary"]["exclusion_reasons"][unsafe_ref],
        )

    def test_reference_policy_excludes_emotion_forbidden_smile_anchor(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            run_id = "2099-01-01_no-smile"
            run_root = repo_root / "runs" / run_id
            (run_root / "references-used").mkdir(parents=True)
            self._write_minimal_reference_repo(repo_root)
            self._write_identity_fixture(repo_root)
            (run_root / "references-used/reference_policy.json").write_text(
                """{
  "schema_version": "1.0",
  "blocked_active_refs": [],
  "analysis_only_refs": [],
  "emotion_forbidden_refs": [
    "references/identity/aachu/aachu-face-crop-lavender-smile-01.jpg"
  ],
  "reason": "Slide 1 is a no-smile missing-person ache beat."
}
""",
                encoding="utf-8",
            )

            context = build_reference_context(repo_root, run_id)

        smile_ref = "references/identity/aachu/aachu-face-crop-lavender-smile-01.jpg"
        self.assertNotIn(smile_ref, context["active_view_image_queue"])
        self.assertIn(
            smile_ref,
            context["reference_policy_summary"]["emotion_forbidden_refs"],
        )

    def test_policy_filtered_active_queue_keeps_minimum_face_anchors(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            run_id = "2099-01-01_policy-keeps-anchors"
            run_root = repo_root / "runs" / run_id
            (run_root / "references-used").mkdir(parents=True)
            self._write_minimal_reference_repo(repo_root)
            self._write_identity_fixture(repo_root)
            (run_root / "references-used/reference_policy.json").write_text(
                """{
  "schema_version": "1.0",
  "blocked_active_refs": [
    "references/identity/aachu/aachu-face-cafe-neutral-01.jpg"
  ],
  "analysis_only_refs": [],
  "emotion_forbidden_refs": [
    "references/identity/aachu/aachu-face-crop-lavender-smile-01.jpg"
  ],
  "reason": "Unsafe pose and smile anchors stay out of active imagegen."
}
""",
                encoding="utf-8",
            )

            context = build_reference_context(repo_root, run_id)

        aachu_active = [
            path
            for path in context["active_view_image_queue"]
            if path.startswith("references/identity/aachu/")
        ]
        zuv_active = [
            path
            for path in context["active_view_image_queue"]
            if path.startswith("references/identity/zuv/")
        ]
        self.assertGreaterEqual(len(aachu_active), 4)
        self.assertGreaterEqual(len(zuv_active), 4)
        self.assertNotIn(
            "references/identity/aachu/aachu-face-cafe-neutral-01.jpg",
            aachu_active,
        )
        self.assertNotIn(
            "references/identity/aachu/aachu-face-crop-lavender-smile-01.jpg",
            aachu_active,
        )

    def _write_minimal_reference_repo(self, repo_root):
        for rel_path in [
            "references/text-style/README.md",
            "references/brand/README.md",
            ".agents/skills/astory/references/house-style-contract.md",
            ".agents/skills/astory/references/imagegen-contract.md",
        ]:
            path = repo_root / rel_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("test reference\n", encoding="utf-8")
        for index in range(1, 4):
            self._write_image(
                repo_root
                / "references"
                / "style"
                / "best-illustration"
                / f"slide-{index:02d}.png"
            )
        self._write_image(
            repo_root
            / "references"
            / "identity"
            / "together"
            / "together-body-language-01.jpg"
        )

    def _write_identity_fixture(self, repo_root):
        for filename in [
            "aachu-face-cafe-neutral-01.jpg",
            "aachu-face-crop-cafe-neutral-01.jpg",
            "aachu-face-crop-home-black-01.jpg",
            "aachu-face-crop-kitchen-neutral-01.jpg",
            "aachu-face-crop-lavender-smile-01.jpg",
            "aachu-face-front-close-selfie-2026-06-18-01.jpg",
            "aachu-face-side-bridal-glance-2026-06-18-01.jpg",
        ]:
            self._write_image(
                repo_root / "references" / "identity" / "aachu" / filename
            )
        for filename in [
            "zuv-face-front-blue-overshirt-selfie-2026-06-18-01.jpg",
            "zuv-face-three-quarter-blue-overshirt-selfie-2026-06-18-01.jpg",
            "zuv-face-side-indoor-white-tee-2026-06-18-01.jpg",
            "zuv-face-front-hand-hair-blue-overshirt-2026-06-18-01.jpg",
            "zuv-face-crop-balcony-neutral-01.jpg",
        ]:
            self._write_image(
                repo_root / "references" / "identity" / "zuv" / filename
            )

    def _write_image(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (32, 32), (240, 240, 238)).save(path)


if __name__ == "__main__":
    unittest.main()
