import contextlib
import io
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts import instagram_corpus_cli


class InstagramCorpusCliTests(unittest.TestCase):
    def test_init_import_export_and_validate_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db_path = root / "corpus.sqlite"
            seed_path = root / "seed.json"
            export_dir = root / "rag"
            seed_path.write_text(json.dumps([_seed_post()]), encoding="utf-8")

            init = _run_cli(["init", "--db", str(db_path)])
            self.assertEqual(init.return_code, 0)
            self.assertTrue(db_path.exists())

            imported = _run_cli(
                [
                    "import-seed",
                    "--db",
                    str(db_path),
                    "--seed",
                    str(seed_path),
                    "--run-id",
                    "seed_test",
                ]
            )
            self.assertEqual(imported.return_code, 0)
            self.assertEqual(_table_count(db_path, "posts"), 1)

            exported = _run_cli(["export-rag", "--db", str(db_path), "--out", str(export_dir)])
            self.assertEqual(exported.return_code, 0)
            self.assertTrue((export_dir / "posts.jsonl").exists())
            self.assertTrue((export_dir / "assets.jsonl").exists())
            self.assertTrue((export_dir / "chunks.jsonl").exists())
            self.assertTrue((export_dir / "gaps.jsonl").exists())

            validated = _run_cli(["validate", "--db", str(db_path), "--root", str(root)])
            self.assertEqual(validated.return_code, 0)
            self.assertEqual(json.loads(validated.stdout)["findings"], [])

    def test_ingest_url_can_use_manual_json_provider_without_network_or_token_leak(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db_path = root / "corpus.sqlite"
            fixture = (
                Path(__file__).parent
                / "fixtures"
                / "instagram_corpus"
                / "brightdata_post_carousel.json"
            )
            _run_cli(["init", "--db", str(db_path)])

            result = _run_cli(
                [
                    "ingest-url",
                    "--db",
                    str(db_path),
                    "--root", str(root),
                    "--provider",
                    "manual-json",
                    "--input-json",
                    str(fixture),
                    "--run-id",
                    "manual_pilot",
                    "--url",
                    "https://www.instagram.com/p/DUtQzmaj9Rw/",
                ]
            )

            self.assertEqual(result.return_code, 0)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "ingested")
            self.assertEqual(payload["post"]["shortcode"], "DUtQzmaj9Rw")
            self.assertEqual(_table_count(db_path, "raw_objects"), 1)
            self.assertEqual(_table_count(db_path, "posts"), 1)
            self.assertEqual(_table_count(db_path, "assets"), 3)
            self.assertEqual(_table_count(db_path, "rag_chunks"), 1)
            self.assertNotIn("secret-token", result.stdout)

    def test_ingest_url_requires_token_for_live_providers_without_printing_secret(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "corpus.sqlite"
            _run_cli(["init", "--db", str(db_path)])

            result = _run_cli(
                [
                    "ingest-url",
                    "--db",
                    str(db_path),
                    "--root",
                    tmp,
                    "--provider",
                    "brightdata",
                    "--run-id",
                    "live_missing_token",
                    "--url",
                    "https://www.instagram.com/p/DUtQzmaj9Rw/",
                ]
            )

            self.assertEqual(result.return_code, 2)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "missing_token")
            self.assertNotIn("BRIGHTDATA_TOKEN=", result.stdout)

    def test_download_media_fetches_asset_urls_and_updates_catalog(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db_path = root / "corpus.sqlite"
            media_source = root / "slide.jpg"
            media_source.write_bytes(b"fake jpg bytes")
            _run_cli(["init", "--db", str(db_path)])
            conn = sqlite3.connect(db_path)
            try:
                conn.execute(
                    """
                    INSERT INTO raw_objects(
                        raw_object_id, provider, run_id, object_type, source_url,
                        local_path, sha256, captured_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        "raw_asset",
                        "manual",
                        "download_test",
                        "asset",
                        media_source.as_uri(),
                        str(media_source),
                        "0" * 64,
                        "2026-06-18T00:00:00Z",
                    ),
                )
                conn.execute(
                    """
                    INSERT INTO posts(post_id, shortcode, permalink, media_type, caption, raw_object_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        "ig_MEDIA",
                        "MEDIA",
                        "https://www.instagram.com/p/MEDIA/",
                        "Image",
                        "",
                        "raw_asset",
                    ),
                )
                conn.execute(
                    """
                    INSERT INTO assets(asset_id, post_id, asset_index, media_type, source_url, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    ("ig_MEDIA_asset_00", "ig_MEDIA", 0, "Image", media_source.as_uri(), "provider_child_url"),
                )
                conn.commit()
            finally:
                conn.close()

            result = _run_cli(
                [
                    "download-media",
                    "--db",
                    str(db_path),
                    "--root",
                    str(root),
                    "--run-id",
                    "download_test",
                ]
            )

            self.assertEqual(result.return_code, 0)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "downloaded")
            self.assertEqual(payload["counts"]["downloaded"], 1)
            self.assertEqual(_table_count(db_path, "media_files"), 1)


class _CliResult:
    def __init__(self, return_code: int, stdout: str) -> None:
        self.return_code = return_code
        self.stdout = stdout


def _run_cli(argv: list[str]) -> _CliResult:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        return_code = instagram_corpus_cli.main(argv)
    return _CliResult(return_code, buffer.getvalue())


def _table_count(db_path: Path, table: str) -> int:
    conn = sqlite3.connect(db_path)
    try:
        return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    finally:
        conn.close()


def _seed_post() -> dict:
    return {
        "shortCode": "ALPHA",
        "ownerUsername": "source_account",
        "url": "https://www.instagram.com/p/ALPHA/",
        "type": "Image",
        "caption": "A seed caption with a retrievable mechanic.",
        "likesCount": 1234,
        "commentsCount": 56,
        "childCount": 1,
        "displayUrl": "https://cdn.example/alpha.jpg",
        "timestamp": "2026-06-01T00:00:00.000Z",
    }


if __name__ == "__main__":
    unittest.main()
