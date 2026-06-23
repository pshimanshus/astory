import json
import unittest
from pathlib import Path

from scripts.instagram_corpus import db
from scripts.instagram_corpus.seed_import import import_winner_seed


FIXTURE = Path(__file__).parent / "fixtures" / "instagram_corpus" / "winner_seed_minimal.json"


class InstagramCorpusSeedImportTest(unittest.TestCase):
    def setUp(self):
        self.conn = db.connect(":memory:")
        db.initialize(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_imports_winner_seed_catalog_rows_and_gaps(self):
        manifest = import_winner_seed(self.conn, FIXTURE, run_id="seed_test")

        self.assertEqual(
            manifest,
            {
                "run_id": "seed_test",
                "accounts": 1,
                "posts": 1,
                "snapshots": 1,
                "raw_objects": 1,
                "assets": 3,
                "metric_observations": 4,
                "gaps": 5,
                "rag_chunks": 1,
            },
        )

        counts = {
            name: self.conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
            for name in [
                "accounts",
                "posts",
                "post_snapshots",
                "raw_objects",
                "assets",
                "metric_observations",
                "gaps",
                "rag_chunks",
            ]
        }
        self.assertEqual(counts["accounts"], 1)
        self.assertEqual(counts["posts"], 1)
        self.assertEqual(counts["post_snapshots"], 1)
        self.assertEqual(counts["raw_objects"], 1)
        self.assertEqual(counts["assets"], 3)
        self.assertEqual(counts["metric_observations"], 4)
        self.assertEqual(counts["gaps"], 5)
        self.assertEqual(counts["rag_chunks"], 1)

        post = self.conn.execute(
            """
            SELECT post_id, shortcode, permalink, account_id, media_type, caption, raw_object_id
            FROM posts
            """
        ).fetchone()
        self.assertEqual(post["post_id"], "ig_DUtQzmaj9Rw")
        self.assertEqual(post["shortcode"], "DUtQzmaj9Rw")
        self.assertEqual(post["account_id"], "acct_wetheurban")
        self.assertEqual(post["media_type"], "Sidecar")
        self.assertTrue(post["raw_object_id"].startswith("raw_seed_seed_test_seedfile_"))
        self.assertIn("intimacy becomes an anchor", post["caption"])

        snapshot = self.conn.execute(
            "SELECT raw_object_id FROM post_snapshots WHERE post_id = ?",
            ("ig_DUtQzmaj9Rw",),
        ).fetchone()
        self.assertEqual(snapshot["raw_object_id"], post["raw_object_id"])

        metrics = {
            row["metric_name"]: (row["metric_value"], row["raw_object_id"])
            for row in self.conn.execute(
                "SELECT metric_name, metric_value, raw_object_id FROM metric_observations"
            )
        }
        self.assertEqual(
            {name: value for name, (value, _raw_id) in metrics.items()},
            {
                "likes": 615337,
                "comments": 1417,
                "views": 0,
                "plays": 0,
            },
        )
        self.assertTrue(all(raw_id == post["raw_object_id"] for _value, raw_id in metrics.values()))

        raw = self.conn.execute(
            "SELECT sha256, local_path FROM raw_objects WHERE raw_object_id = ?",
            (post["raw_object_id"],),
        ).fetchone()
        self.assertEqual(len(raw["sha256"]), 64)
        self.assertEqual(Path(raw["local_path"]), FIXTURE)

        chunk = self.conn.execute(
            "SELECT evidence_json FROM rag_chunks WHERE post_id = ?",
            ("ig_DUtQzmaj9Rw",),
        ).fetchone()
        self.assertEqual(json.loads(chunk["evidence_json"]), [post["raw_object_id"]])

        gap_types = {
            row["gap_type"]
            for row in self.conn.execute("SELECT gap_type FROM gaps ORDER BY gap_type")
        }
        self.assertEqual(
            gap_types,
            {"saves", "shares", "child_media_urls", "ocr", "visual_notes"},
        )

    def test_fixture_is_winner_bank_style_json(self):
        data = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.assertIsInstance(data, list)
        first = data[0]
        for key in [
            "shortCode",
            "url",
            "ownerUsername",
            "type",
            "caption",
            "likesCount",
            "commentsCount",
            "childCount",
            "displayUrl",
        ]:
            self.assertIn(key, first)


if __name__ == "__main__":
    unittest.main()
