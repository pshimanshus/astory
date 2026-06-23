import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.instagram_corpus import db
from scripts.instagram_corpus.seed_import import import_winner_seed
from scripts.instagram_corpus.validate import validate_catalog

FIXTURE = Path(__file__).parent / "fixtures" / "instagram_corpus" / "winner_seed_minimal.json"


class InstagramCorpusValidateTests(unittest.TestCase):
    def test_validate_catalog_accepts_complete_minimal_catalog(self):
        conn = sqlite3.connect(":memory:")
        _create_validation_schema(conn)
        _insert_complete_catalog(conn)

        with tempfile.TemporaryDirectory() as tmp:
            findings = validate_catalog(conn, Path(tmp))

        self.assertEqual(findings, [])

    def test_validate_catalog_reports_provenance_and_coverage_findings(self):
        conn = sqlite3.connect(":memory:")
        _create_validation_schema(conn)
        _insert_broken_catalog(conn)

        with tempfile.TemporaryDirectory() as tmp:
            findings = validate_catalog(conn, Path(tmp))

        codes = {finding["code"] for finding in findings}
        self.assertEqual(
            codes,
            {
                "raw_missing_sha256",
                "post_missing_evidence",
                "metric_missing_raw_evidence",
                "chunk_missing_evidence",
                "carousel_child_missing",
            },
        )
        for finding in findings:
            self.assertEqual(finding["severity"], "error")
            self.assertIn("gate", finding)
            self.assertIn("target", finding)
            self.assertIn("message", finding)

    def test_validate_catalog_reports_child_asset_row_with_missing_media_and_no_gap(self):
        conn = sqlite3.connect(":memory:")
        _create_validation_schema(conn)
        _insert_carousel_with_missing_child_media_row(conn)

        with tempfile.TemporaryDirectory() as tmp:
            findings = validate_catalog(conn, Path(tmp))

        self.assertIn("carousel_child_missing", {finding["code"] for finding in findings})
        self.assertIn("ig_CHILDLESS:1", {finding["target"] for finding in findings})

    def test_validate_catalog_accepts_canonical_seed_import_with_raw_evidence(self):
        conn = db.connect(":memory:")
        db.initialize(conn)
        import_winner_seed(conn, FIXTURE, run_id="seed_test")

        findings = validate_catalog(conn, Path("/"))

        self.assertEqual(findings, [])
        conn.close()

    def test_validate_catalog_checks_raw_file_digest_against_corpus_root(self):
        conn = sqlite3.connect(":memory:")
        _create_validation_schema(conn)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw_path = root / "raw/provider/run/post.json"
            raw_path.parent.mkdir(parents=True)
            raw_path.write_text("payload", encoding="utf-8")
            conn.execute(
                "INSERT INTO raw_objects VALUES (?, ?, ?, ?, ?)",
                (
                    "raw_bad_digest",
                    "provider",
                    "f" * 64,
                    "raw/provider/run/post.json",
                    "https://www.instagram.com/p/BAD/",
                ),
            )

            findings = validate_catalog(conn, root)

        codes = {finding["code"] for finding in findings}
        self.assertIn("raw_sha256_mismatch", codes)

    def test_validate_catalog_reports_unresolved_raw_evidence_references(self):
        conn = sqlite3.connect(":memory:")
        _create_validation_schema(conn)
        conn.execute(
            "INSERT INTO posts VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                "ig_TYPO",
                "TYPO",
                "https://www.instagram.com/p/TYPO/",
                "image",
                "third_party_analysis_only",
                "raw_typo",
                1,
            ),
        )
        conn.execute(
            "INSERT INTO metric_observations VALUES (?, ?, ?, ?, ?, ?)",
            ("metric_likes", "ig_TYPO", "likes", 10, "raw_typo", "provider"),
        )
        conn.execute(
            "INSERT INTO rag_chunks VALUES (?, ?, ?, ?)",
            ("chunk_typo", "ig_TYPO", json.dumps(["raw_typo"]), json.dumps([])),
        )

        with tempfile.TemporaryDirectory() as tmp:
            findings = validate_catalog(conn, Path(tmp))

        codes = {finding["code"] for finding in findings}
        self.assertIn("raw_evidence_missing", codes)
        targets = {finding["target"] for finding in findings}
        self.assertIn("ig_TYPO:raw_typo", targets)
        self.assertIn("metric_likes:raw_typo", targets)
        self.assertIn("chunk_typo:raw_typo", targets)


def _create_validation_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE raw_objects (
            raw_object_id TEXT PRIMARY KEY,
            provider TEXT,
            sha256 TEXT,
            local_path TEXT,
            source_url TEXT
        );
        CREATE TABLE posts (
            post_id TEXT PRIMARY KEY,
            shortcode TEXT,
            source_url TEXT,
            media_type TEXT,
            rights_scope TEXT,
            raw_object_id TEXT,
            expected_child_count INTEGER
        );
        CREATE TABLE assets (
            asset_id TEXT PRIMARY KEY,
            post_id TEXT,
            asset_index INTEGER,
            source_url TEXT,
            media_sha256 TEXT,
            raw_object_id TEXT
        );
        CREATE TABLE metric_observations (
            metric_id TEXT PRIMARY KEY,
            post_id TEXT,
            metric_name TEXT,
            value INTEGER,
            raw_object_id TEXT,
            provider TEXT
        );
        CREATE TABLE rag_chunks (
            chunk_id TEXT PRIMARY KEY,
            post_id TEXT,
            raw_object_ids TEXT,
            gap_ids TEXT
        );
        CREATE TABLE gaps (
            gap_id TEXT PRIMARY KEY,
            post_id TEXT,
            asset_id TEXT,
            field TEXT,
            status TEXT,
            reason TEXT,
            missing_index INTEGER
        );
        """
    )


def _insert_complete_catalog(conn: sqlite3.Connection) -> None:
    raw_root = Path(tempfile.gettempdir()) / "instagram-corpus-validate-complete"
    raw_file = raw_root / "raw/provider/run/post.json"
    raw_file.parent.mkdir(parents=True, exist_ok=True)
    raw_file.write_text("ok", encoding="utf-8")
    conn.execute(
        "INSERT INTO raw_objects VALUES (?, ?, ?, ?, ?)",
        (
            "raw_post",
            "provider",
            "2689367b205c16ce32ed4200942b8b8b1e262dfc70d9bc9fbc77c49699a4f1df",
            str(raw_file),
            "https://www.instagram.com/p/OK/",
        ),
    )
    conn.execute(
        "INSERT INTO posts VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            "ig_OK",
            "OK",
            "https://www.instagram.com/p/OK/",
            "image",
            "third_party_analysis_only",
            "raw_post",
            1,
        ),
    )
    conn.execute(
        "INSERT INTO assets VALUES (?, ?, ?, ?, ?, ?)",
        ("asset_0", "ig_OK", 0, "https://cdn.example/ok.jpg", "b" * 64, "raw_post"),
    )
    conn.execute(
        "INSERT INTO metric_observations VALUES (?, ?, ?, ?, ?, ?)",
        ("metric_likes", "ig_OK", "likes", 100, "raw_post", "provider"),
    )
    conn.execute(
        "INSERT INTO rag_chunks VALUES (?, ?, ?, ?)",
        ("chunk_ok", "ig_OK", json.dumps(["raw_post"]), json.dumps([])),
    )
    conn.commit()


def _insert_broken_catalog(conn: sqlite3.Connection) -> None:
    conn.execute(
        "INSERT INTO raw_objects VALUES (?, ?, ?, ?, ?)",
        ("raw_bad", "provider", "", "raw/provider/run/bad.json", "https://www.instagram.com/p/BAD/"),
    )
    conn.execute(
        "INSERT INTO posts VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            "ig_BAD",
            "BAD",
            "https://www.instagram.com/p/BAD/",
            "carousel",
            "third_party_analysis_only",
            None,
            2,
        ),
    )
    conn.execute(
        "INSERT INTO assets VALUES (?, ?, ?, ?, ?, ?)",
        ("asset_0", "ig_BAD", 0, "https://cdn.example/bad.jpg", "c" * 64, "raw_bad"),
    )
    conn.execute(
        "INSERT INTO metric_observations VALUES (?, ?, ?, ?, ?, ?)",
        ("metric_shares", "ig_BAD", "shares", 12, None, "seed"),
    )
    conn.execute(
        "INSERT INTO rag_chunks VALUES (?, ?, ?, ?)",
        ("chunk_bad", "ig_BAD", json.dumps([]), json.dumps([])),
    )
    conn.commit()


def _insert_carousel_with_missing_child_media_row(conn: sqlite3.Connection) -> None:
    conn.execute(
        "INSERT INTO raw_objects VALUES (?, ?, ?, ?, ?)",
        (
            "raw_childless",
            "provider",
            "d" * 64,
            "raw/provider/run/childless.json",
            "https://www.instagram.com/p/CHILDLESS/",
        ),
    )
    conn.execute(
        "INSERT INTO posts VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            "ig_CHILDLESS",
            "CHILDLESS",
            "https://www.instagram.com/p/CHILDLESS/",
            "carousel",
            "third_party_analysis_only",
            "raw_childless",
            2,
        ),
    )
    conn.executemany(
        "INSERT INTO assets VALUES (?, ?, ?, ?, ?, ?)",
        [
            (
                "childless_asset_0",
                "ig_CHILDLESS",
                0,
                "https://cdn.example/childless-0.jpg",
                "e" * 64,
                "raw_childless",
            ),
            ("childless_asset_1", "ig_CHILDLESS", 1, None, None, None),
        ],
    )
    conn.execute(
        "INSERT INTO metric_observations VALUES (?, ?, ?, ?, ?, ?)",
        ("metric_likes", "ig_CHILDLESS", "likes", 100, "raw_childless", "provider"),
    )
    conn.execute(
        "INSERT INTO rag_chunks VALUES (?, ?, ?, ?)",
        ("childless_chunk", "ig_CHILDLESS", json.dumps(["raw_childless"]), json.dumps([])),
    )
    conn.commit()


if __name__ == "__main__":
    unittest.main()
