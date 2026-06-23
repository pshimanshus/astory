import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.instagram_corpus.export_rag import export_rag


class InstagramCorpusExportRagTests(unittest.TestCase):
    def test_exports_posts_assets_chunks_and_gaps_jsonl(self):
        conn = sqlite3.connect(":memory:")
        _create_export_catalog(conn)

        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "rag"
            counts = export_rag(conn, output_dir)

            self.assertEqual(
                counts,
                {"posts": 1, "assets": 2, "chunks": 3, "comments": 1, "gaps": 1},
            )
            self.assertEqual(_jsonl_count(output_dir / "posts.jsonl"), 1)
            self.assertEqual(_jsonl_count(output_dir / "assets.jsonl"), 2)
            self.assertEqual(_jsonl_count(output_dir / "chunks.jsonl"), 3)
            self.assertEqual(_jsonl_count(output_dir / "comments.jsonl"), 1)
            self.assertEqual(_jsonl_count(output_dir / "gaps.jsonl"), 1)

            post = _read_jsonl(output_dir / "posts.jsonl")[0]
            self.assertEqual(post["post_id"], "ig_ALPHA")
            self.assertEqual(post["source_url"], "https://www.instagram.com/p/ALPHA/")
            self.assertEqual(post["rights_scope"], "third_party_analysis_only")
            self.assertEqual(post["evidence_raw_object_ids"], ["raw_post"])
            self.assertEqual(post["gap_ids"], ["gap_child_1"])

            assets = _read_jsonl(output_dir / "assets.jsonl")
            self.assertEqual([asset["asset_id"] for asset in assets], ["asset_0", "asset_1"])
            self.assertEqual(assets[0]["evidence_raw_object_ids"], ["raw_asset_0"])
            self.assertEqual(assets[1]["evidence_raw_object_ids"], [])
            self.assertEqual(assets[1]["gap_ids"], ["gap_child_1"])

            chunks = _read_jsonl(output_dir / "chunks.jsonl")
            self.assertEqual([chunk["chunk_id"] for chunk in chunks], ["chunk_caption", "chunk_slide_0", "chunk_gap"])
            for chunk in chunks:
                self.assertEqual(chunk["source_url"], "https://www.instagram.com/p/ALPHA/")
                self.assertEqual(chunk["rights_scope"], "third_party_analysis_only")
                self.assertEqual(chunk["metric_context"]["likes"], 100)
                self.assertIn("shares", chunk["explicit_unavailable_fields"])
                self.assertTrue(chunk["evidence_raw_object_ids"] or chunk["gap_ids"])

            comment = _read_jsonl(output_dir / "comments.jsonl")[0]
            self.assertEqual(comment["comment_id"], "comment_1")
            self.assertEqual(comment["post_id"], "ig_ALPHA")
            self.assertEqual(comment["evidence_raw_object_ids"], ["raw_post"])


def _create_export_catalog(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE raw_objects (
            raw_object_id TEXT PRIMARY KEY,
            provider TEXT,
            sha256 TEXT,
            source_url TEXT
        );
        CREATE TABLE posts (
            post_id TEXT PRIMARY KEY,
            shortcode TEXT,
            source_url TEXT,
            account_username TEXT,
            media_type TEXT,
            rights_scope TEXT,
            raw_object_id TEXT,
            caption_text TEXT
        );
        CREATE TABLE assets (
            asset_id TEXT PRIMARY KEY,
            post_id TEXT,
            asset_index INTEGER,
            source_url TEXT,
            media_type TEXT,
            media_sha256 TEXT,
            rights_scope TEXT,
            raw_object_id TEXT
        );
        CREATE TABLE gaps (
            gap_id TEXT PRIMARY KEY,
            post_id TEXT,
            asset_id TEXT,
            field TEXT,
            status TEXT,
            reason TEXT
        );
        CREATE TABLE rag_chunks (
            chunk_id TEXT PRIMARY KEY,
            post_id TEXT,
            asset_id TEXT,
            source_url TEXT,
            text TEXT,
            rights_scope TEXT,
            raw_object_ids TEXT,
            gap_ids TEXT
        );
        CREATE TABLE metric_observations (
            metric_id TEXT PRIMARY KEY,
            post_id TEXT,
            metric_name TEXT,
            value INTEGER,
            raw_object_id TEXT,
            provider TEXT
        );
        CREATE TABLE comments (
            comment_id TEXT PRIMARY KEY,
            post_id TEXT,
            author_username TEXT,
            text TEXT,
            like_count INTEGER,
            raw_object_id TEXT
        );
        """
    )
    conn.executemany(
        "INSERT INTO raw_objects VALUES (?, ?, ?, ?)",
        [
            ("raw_post", "seed", "a" * 64, "https://www.instagram.com/p/ALPHA/"),
            ("raw_asset_0", "provider", "b" * 64, "https://cdn.example/0.jpg"),
        ],
    )
    conn.execute(
        """
        INSERT INTO posts VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "ig_ALPHA",
            "ALPHA",
            "https://www.instagram.com/p/ALPHA/",
            "example",
            "carousel",
            "third_party_analysis_only",
            "raw_post",
            "A saved caption for retrieval.",
        ),
    )
    conn.executemany(
        "INSERT INTO assets VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (
                "asset_0",
                "ig_ALPHA",
                0,
                "https://cdn.example/0.jpg",
                "image",
                "b" * 64,
                "third_party_analysis_only",
                "raw_asset_0",
            ),
            (
                "asset_1",
                "ig_ALPHA",
                1,
                None,
                "image",
                None,
                "third_party_analysis_only",
                None,
            ),
        ],
    )
    conn.execute(
        "INSERT INTO gaps VALUES (?, ?, ?, ?, ?, ?)",
        (
            "gap_child_1",
            "ig_ALPHA",
            "asset_1",
            "carousel_child_media",
            "unavailable",
            "provider did not return child media",
        ),
    )
    conn.execute(
        "INSERT INTO metric_observations VALUES (?, ?, ?, ?, ?, ?)",
        ("metric_likes", "ig_ALPHA", "likes", 100, "raw_post", "provider"),
    )
    conn.execute(
        "INSERT INTO metric_observations VALUES (?, ?, ?, ?, ?, ?)",
        ("metric_shares_gap", "ig_ALPHA", "shares", None, None, "gap"),
    )
    conn.execute(
        "INSERT INTO comments VALUES (?, ?, ?, ?, ?, ?)",
        ("comment_1", "ig_ALPHA", "reader", "This made me send it.", 3, "raw_post"),
    )
    conn.executemany(
        "INSERT INTO rag_chunks VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (
                "chunk_caption",
                "ig_ALPHA",
                None,
                "https://www.instagram.com/p/ALPHA/",
                "caption mechanics",
                "third_party_analysis_only",
                json.dumps(["raw_post"]),
                json.dumps([]),
            ),
            (
                "chunk_slide_0",
                "ig_ALPHA",
                "asset_0",
                "https://www.instagram.com/p/ALPHA/",
                "slide text",
                "third_party_analysis_only",
                json.dumps(["raw_asset_0"]),
                json.dumps([]),
            ),
            (
                "chunk_gap",
                "ig_ALPHA",
                "asset_1",
                "https://www.instagram.com/p/ALPHA/",
                "missing second carousel child",
                "third_party_analysis_only",
                json.dumps([]),
                json.dumps(["gap_child_1"]),
            ),
        ],
    )
    conn.commit()


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _jsonl_count(path: Path) -> int:
    return len(_read_jsonl(path))


if __name__ == "__main__":
    unittest.main()
