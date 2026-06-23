import sqlite3
import unittest

from scripts.instagram_corpus import db


REQUIRED_TABLES = {
    "ingest_runs",
    "raw_objects",
    "accounts",
    "posts",
    "post_snapshots",
    "assets",
    "media_files",
    "metric_observations",
    "comments",
    "annotations",
    "ocr_results",
    "rag_chunks",
    "gaps",
    "jobs",
}


class InstagramCorpusDatabaseTest(unittest.TestCase):
    def setUp(self):
        self.conn = db.connect(":memory:")
        db.initialize(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_schema_creates_required_tables(self):
        self.assertTrue(REQUIRED_TABLES.issubset(db.table_names(self.conn)))

    def test_foreign_keys_are_enabled(self):
        enabled = self.conn.execute("PRAGMA foreign_keys").fetchone()[0]
        self.assertEqual(enabled, 1)

    def test_posts_have_stable_unique_ids(self):
        self.conn.execute(
            """
            INSERT INTO accounts(account_id, username, full_name)
            VALUES (?, ?, ?)
            """,
            ("acct_wetheurban", "wetheurban", "WE THE URBAN"),
        )
        self.conn.execute(
            """
            INSERT INTO posts(post_id, shortcode, permalink, account_id, media_type)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                "ig_DUtQzmaj9Rw",
                "DUtQzmaj9Rw",
                "https://www.instagram.com/p/DUtQzmaj9Rw/",
                "acct_wetheurban",
                "Sidecar",
            ),
        )

        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                """
                INSERT INTO posts(post_id, shortcode, permalink, account_id, media_type)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    "ig_DUtQzmaj9Rw",
                    "DUtQzmaj9Rw",
                    "https://www.instagram.com/p/DUtQzmaj9Rw/",
                    "acct_wetheurban",
                    "Sidecar",
                ),
            )

    def test_raw_objects_have_stable_unique_ids(self):
        self.conn.execute(
            """
            INSERT INTO raw_objects(
                raw_object_id, provider, run_id, object_type, source_url,
                local_path, sha256, captured_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "raw_seed_abc123",
                "seed",
                "seed_run",
                "post",
                "https://www.instagram.com/p/DUtQzmaj9Rw/",
                "raw/seed/seed_run/post_abc123.json",
                "abc123",
                "2026-06-18T00:00:00Z",
            ),
        )

        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                """
                INSERT INTO raw_objects(
                    raw_object_id, provider, run_id, object_type, source_url,
                    local_path, sha256, captured_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "raw_seed_abc123",
                    "seed",
                    "seed_run",
                    "post",
                    "https://www.instagram.com/p/DUtQzmaj9Rw/",
                    "raw/seed/seed_run/post_abc123.json",
                    "abc123",
                    "2026-06-18T00:00:00Z",
                ),
            )


if __name__ == "__main__":
    unittest.main()
