import unittest

from scripts.astory_brain.models import BrainChunk, BrainSource, RecallResult


class AStoryBrainModelTests(unittest.TestCase):
    def test_source_requires_local_path_and_kind(self):
        source = BrainSource(
            source_id="source:run:2026-06-10_22-22_heart-rent:approvals",
            path="runs/2026-06-10_22-22_heart-rent/docs/approvals.md",
            kind="approval",
            scope="run",
            run_id="2026-06-10_22-22_heart-rent",
            role=None,
            sha256="abc123",
            modified_at="2026-06-10T22:22:00+05:30",
        )

        self.assertEqual(source.kind, "approval")
        self.assertEqual(source.run_id, "2026-06-10_22-22_heart-rent")
        self.assertTrue(source.path.endswith("approvals.md"))

    def test_recall_result_carries_evidence_and_safety(self):
        chunk = BrainChunk(
            chunk_id="chunk:1",
            source_id="source:1",
            page_id="page:characters/aachu",
            path="references/brain/pages/characters/aachu.md",
            text="Aachu identity must cite visible local references.",
            kind="compiled_truth",
            role="aachu",
            tags=["identity"],
        )
        result = RecallResult(
            chunk=chunk,
            score=1.0,
            evidence=["exact_role_match", "keyword_match"],
            safety="exists",
        )

        self.assertIn("exact_role_match", result.evidence)
        self.assertEqual(result.safety, "exists")


if __name__ == "__main__":
    unittest.main()
