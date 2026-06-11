import json
import tempfile
import unittest
from pathlib import Path

from scripts.astory_brain.indexer import build_index
from scripts.astory_brain.lint import lint_brain


class AStoryBrainLintTests(unittest.TestCase):
    def test_lint_flags_missing_citation_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_schema(root)
            page_dir = root / "references/brain/pages"
            page_dir.mkdir(parents=True, exist_ok=True)
            (page_dir / "bad.md").write_text(
                "# Current Truth\n\n"
                "- This claim has no citation.\n\n"
                "---\n\n"
                "# Timeline / Evidence\n\n",
                encoding="utf-8",
            )

            report = lint_brain(root)

            self.assertEqual(report["status"], "fail")
            self.assertIn("missing_citation", report["failures"][0]["code"])

    def test_lint_flags_unknown_page_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_schema(root)
            page_dir = root / "references/brain/pages"
            page_dir.mkdir(parents=True, exist_ok=True)
            (page_dir / "bad.md").write_text(
                "---\n"
                "type: random_note\n"
                "---\n\n"
                "# Current Truth\n\n"
                "- Cited claim from `docs/setup_status.md`.\n\n"
                "---\n\n"
                "# Timeline / Evidence\n\n"
                "- 2026-06-10 | `docs/setup_status.md` | Setup checked.\n",
                encoding="utf-8",
            )

            report = lint_brain(root)

            self.assertEqual(report["status"], "fail")
            self.assertTrue(
                any(failure["code"] == "unknown_page_type" for failure in report["failures"])
            )

    def test_lint_flags_derived_index_citation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_schema(root)
            page_dir = root / "references/brain/pages"
            page_dir.mkdir(parents=True, exist_ok=True)
            (page_dir / "bad.md").write_text(
                "# Current Truth\n\n"
                "- Cites derived cache `references/brain/index/chunks.jsonl`.\n\n"
                "---\n\n"
                "# Timeline / Evidence\n\n"
                "- 2026-06-10 | `references/brain/index/chunks.jsonl` | Bad evidence.\n",
                encoding="utf-8",
            )

            report = lint_brain(root)

            self.assertEqual(report["status"], "fail")
            self.assertTrue(
                any(
                    failure["code"] == "derived_index_citation"
                    for failure in report["failures"]
                )
            )

    def test_lint_flags_http_only_current_truth_citation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_schema(root)
            page_dir = root / "references/brain/pages"
            page_dir.mkdir(parents=True, exist_ok=True)
            (page_dir / "bad.md").write_text(
                "# Current Truth\n\n"
                "- This claim only cites `https://example.com/source`.\n\n"
                "---\n\n"
                "# Timeline / Evidence\n\n"
                "- 2026-06-10 | `docs/setup_status.md` | Setup checked.\n",
                encoding="utf-8",
            )
            (root / "docs").mkdir()
            (root / "docs/setup_status.md").write_text("ready\n", encoding="utf-8")

            report = lint_brain(root)

            self.assertEqual(report["status"], "fail")
            self.assertTrue(
                any(
                    failure["code"] == "missing_local_citation"
                    for failure in report["failures"]
                )
            )

    def test_lint_allows_missing_run_retro_because_doctor_tracks_writeback_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_schema(root)
            page_dir = root / "references/brain/pages"
            page_dir.mkdir(parents=True, exist_ok=True)
            (page_dir / "run-lessons.md").write_text(
                "# Current Truth\n\n"
                "- Uses setup source `docs/setup_status.md`.\n\n"
                "---\n\n"
                "# Timeline / Evidence\n\n"
                "- 2026-06-10 | `docs/setup_status.md` | Setup checked.\n",
                encoding="utf-8",
            )
            (root / "docs").mkdir()
            (root / "docs/setup_status.md").write_text("ready\n", encoding="utf-8")
            (root / "runs/example/docs").mkdir(parents=True)
            build_index(root, root / "references/brain/index", include_runs=["example"])

            report = lint_brain(root)

            self.assertEqual(report["status"], "pass")


def _write_schema(root: Path) -> None:
    schema_dir = root / "references/brain/schema"
    schema_dir.mkdir(parents=True, exist_ok=True)
    (schema_dir / "type_taxonomy.json").write_text(
        json.dumps(
            {
                "version": 1,
                "page_types": [
                    "character",
                    "relationship",
                    "style",
                    "prompt_pattern",
                    "run_lesson",
                    "failure_mode",
                    "reference",
                    "procedure",
                ],
                "roles": [
                    "aachu",
                    "zuv",
                    "together",
                    "style",
                    "wardrobe",
                    "place",
                    "brand",
                    "text",
                ],
                "source_kinds": [
                    "approval",
                    "prompt",
                    "eval",
                    "reference",
                    "skill_reference",
                    "compiled_page",
                    "retro",
                    "trace",
                ],
            }
        ),
        encoding="utf-8",
    )
    (schema_dir / "version.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "compatible_cli_min": 1,
                "canonical_root": "references/brain/pages",
                "derived_roots": ["references/brain/index", "references/brain/reports"],
            }
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    unittest.main()
