import unittest
from pathlib import Path

from scripts.prepare_imagegen_reference_context import build_reference_context


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
        self.assertGreaterEqual(context["view_image_queue_count"], 10)
        self.assertIn(
            "references/identity/aachu/face/aachu-face-crop-car-purple-01.jpg",
            context["view_image_queue"],
        )
        self.assertIn(
            "references/identity/zuv/face/zuv-face-crop-balcony-neutral-01.jpg",
            context["view_image_queue"],
        )

    def test_face_visible_queue_has_required_aachu_and_zuv_face_anchors(self):
        context = build_reference_context(
            self.repo_root, "2026-06-10_22-22_heart-rent"
        )

        self.assertEqual(
            len(context["reference_groups"]["aachu_face_identity"]), 4
        )
        self.assertEqual(
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

    def test_style_references_are_recorded_as_loadable_local_images(self):
        context = build_reference_context(REPO_ROOT, "2026-06-10_22-22_heart-rent")
        style_refs = context["reference_groups"]["style"]

        self.assertGreaterEqual(len(style_refs), 1)
        self.assertTrue(
            all(item["input_kind"] == "local_image_file" for item in style_refs)
        )
        self.assertTrue(
            all(
                item["delivery_mode"] == "view_image_before_imagegen"
                for item in style_refs
            )
        )


if __name__ == "__main__":
    unittest.main()
