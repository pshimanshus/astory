import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.astory_brain.indexer import build_index
from scripts.astory_brain.source_scan import scan_sources


class AStoryBrainIndexerTests(unittest.TestCase):
    def test_scan_sources_finds_heart_rent_prompts_and_approvals(self):
        sources = scan_sources(".", include_runs=["2026-06-10_22-22_heart-rent"])
        paths = {source.path for source in sources}

        self.assertIn("runs/2026-06-10_22-22_heart-rent/docs/approvals.md", paths)
        self.assertIn(
            "runs/2026-06-10_22-22_heart-rent/prompts/slide_01_4x5_prompt.txt",
            paths,
        )

    def test_scan_sources_assigns_roles_from_reference_paths(self):
        sources = scan_sources(".", include_runs=[])
        role_by_path = {source.path: source.role for source in sources}

        self.assertEqual(role_by_path["references/identity/aachu/README.md"], "aachu")
        self.assertEqual(role_by_path["references/identity/zuv/README.md"], "zuv")

    def test_build_index_writes_sources_pages_and_chunks(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "index"
            build_index(".", output, include_runs=["2026-06-10_22-22_heart-rent"])

            self.assertTrue((output / "sources.jsonl").exists())
            self.assertTrue((output / "pages.jsonl").exists())
            self.assertTrue((output / "chunks.jsonl").exists())

            chunks = [
                json.loads(line)
                for line in (output / "chunks.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertTrue(any("heart-rent" in chunk["path"] for chunk in chunks))

    def test_index_is_disposable_and_rebuildable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page_dir = root / "references/brain/pages/characters"
            page_dir.mkdir(parents=True)
            (page_dir / "aachu.md").write_text(
                "# Aachu\n\n"
                "# Current Truth\n\n"
                "- Use visible local references from `references/identity/aachu/`.\n\n"
                "---\n\n"
                "# Timeline / Evidence\n\n"
                "- 2026-06-10 | `references/identity/aachu/README.md` | Source root exists.\n",
                encoding="utf-8",
            )

            index = root / "references/brain/index"
            build_index(root, index, include_runs=[])
            before = (index / "chunks.jsonl").read_text(encoding="utf-8")

            shutil.rmtree(index)
            build_index(root, index, include_runs=[])
            after = (index / "chunks.jsonl").read_text(encoding="utf-8")

            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
