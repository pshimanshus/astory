import tempfile
import unittest
from pathlib import Path

from scripts.astory_brain.page_store import CompiledPageFormatError, parse_compiled_page


class AStoryBrainPageStoreTests(unittest.TestCase):
    def test_parse_compiled_page_splits_truth_and_timeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "aachu.md"
            page.write_text(
                "# Aachu\n\n"
                "# Current Truth\n"
                "- Use only visible local identity references.\n\n"
                "---\n\n"
                "# Timeline / Evidence\n"
                "- 2026-06-10 | `runs/example/docs/approvals.md` | approval recorded.\n",
                encoding="utf-8",
            )

            parsed = parse_compiled_page(page)

            self.assertIn("visible local identity references", parsed.current_truth)
            self.assertIn("runs/example/docs/approvals.md", parsed.timeline)

    def test_missing_separator_is_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "bad.md"
            page.write_text("# Current Truth\nNo separator\n", encoding="utf-8")

            with self.assertRaises(CompiledPageFormatError):
                parse_compiled_page(page)


if __name__ == "__main__":
    unittest.main()
