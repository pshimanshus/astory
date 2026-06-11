import json
import tempfile
import unittest
from pathlib import Path

from scripts.astory_brain.eval import run_retrieval_eval
from scripts.astory_brain.graph import extract_links_from_page
from scripts.astory_brain.indexer import build_index
from scripts.astory_brain.retrieval import recall


class AStoryBrainRetrievalTests(unittest.TestCase):
    def test_recall_heart_rent_finds_active_run_prompt(self):
        with tempfile.TemporaryDirectory() as tmp:
            index = Path(tmp) / "index"
            build_index(".", index, include_runs=["2026-06-10_22-22_heart-rent"])

            results = recall(index, "heart rent slide prompt", limit=5)

            self.assertTrue(any("heart-rent" in item.chunk.path for item in results))
            self.assertTrue(any("keyword_match" in item.evidence for item in results))

    def test_role_filter_prevents_aachu_zuv_contamination(self):
        with tempfile.TemporaryDirectory() as tmp:
            index = Path(tmp) / "index"
            build_index(".", index, include_runs=[])

            results = recall(index, "face identity references", role="aachu", limit=20)

            self.assertTrue(results)
            self.assertTrue(
                all(
                    item.chunk.role == "aachu"
                    or "references/identity/" not in item.chunk.path
                    for item in results
                )
            )
            self.assertFalse(
                any("references/identity/zuv/" in item.chunk.path for item in results)
            )
            self.assertFalse(
                any(item.chunk.path == "references/identity/README.md" for item in results)
            )

    def test_graph_extraction_reads_frontmatter_edges(self):
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "run-lessons.md"
            page.write_text(
                "---\n"
                "type: run_lesson\n"
                "uses_reference:\n"
                "  - references/identity/aachu/face-01.png\n"
                "failed_for:\n"
                "  - generic_watercolor\n"
                "---\n\n"
                "# Current Truth\n\n"
                "- Slide 1 used `references/identity/aachu/face-01.png`.\n",
                encoding="utf-8",
            )

            links = extract_links_from_page(page, repo_root=Path(tmp))
            relation_targets = {(link.relation, link.to_path or link.to_id) for link in links}

            self.assertIn(
                ("uses_reference", "references/identity/aachu/face-01.png"),
                relation_targets,
            )
            self.assertIn(("failed_for", "failure:generic_watercolor"), relation_targets)

    def test_qrels_eval_requires_expected_hits_and_forbidden_misses(self):
        with tempfile.TemporaryDirectory() as tmp:
            index = Path(tmp) / "index"
            qrels = Path(tmp) / "qrels.json"
            build_index(".", index, include_runs=["2026-06-10_22-22_heart-rent"])
            qrels.write_text(
                json.dumps(
                    [
                        {
                            "query": "Aachu face identity references",
                            "role": "aachu",
                            "expected_paths": ["references/identity/aachu/README.md"],
                            "forbidden_paths": ["references/identity/zuv/README.md"],
                        }
                    ]
                ),
                encoding="utf-8",
            )

            report = run_retrieval_eval(index, qrels, top_k=5)

            self.assertEqual(report["status"], "pass")
            self.assertEqual(report["forbidden_hit_count"], 0)

    def test_qrels_eval_requires_all_expected_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            index = Path(tmp) / "index"
            qrels = Path(tmp) / "qrels.json"
            build_index(".", index, include_runs=[])
            qrels.write_text(
                json.dumps(
                    [
                        {
                            "query": "Aachu face identity references",
                            "role": "aachu",
                            "expected_paths": [
                                "references/identity/aachu/README.md",
                                "references/identity/aachu/definitely-missing.md",
                            ],
                            "forbidden_paths": [],
                        }
                    ]
                ),
                encoding="utf-8",
            )

            report = run_retrieval_eval(index, qrels, top_k=5)

            self.assertEqual(report["status"], "fail")
            self.assertEqual(report["failures"][0]["code"], "expected_path_missing")


if __name__ == "__main__":
    unittest.main()
