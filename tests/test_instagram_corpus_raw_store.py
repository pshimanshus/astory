import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.instagram_corpus.raw_store import write_raw_object


class InstagramCorpusRawStoreTest(unittest.TestCase):
    def test_writes_payload_and_sanitized_metadata_under_data_root(self):
        payload = b'{"shortcode":"DUtQzmaj9Rw","ok":true}'
        expected_sha = hashlib.sha256(payload).hexdigest()

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            metadata = write_raw_object(
                root=root,
                provider="brightdata",
                run_id="run_001",
                object_type="post",
                source_url="https://www.instagram.com/p/DUtQzmaj9Rw/",
                payload=payload,
                request_url="https://api.example.test/scrape?token=secret-token&url=https%3A%2F%2Finstagram.com%2Fp%2FDUtQzmaj9Rw%2F",
                request_headers={
                    "Authorization": "Bearer secret-token",
                    "Cookie": "sessionid=secret-cookie",
                    "x-access-key": "secret-key",
                    "User-Agent": "instagram-corpus-tests",
                },
                response_status=200,
            )

            payload_path = root / metadata["local_path"]
            metadata_path = root / metadata["metadata_path"]

            self.assertTrue(payload_path.exists())
            self.assertTrue(metadata_path.exists())
            self.assertEqual(payload_path.read_bytes(), payload)
            self.assertEqual(metadata["sha256"], expected_sha)
            self.assertEqual(metadata["provider"], "brightdata")
            self.assertEqual(metadata["source_url"], "https://www.instagram.com/p/DUtQzmaj9Rw/")
            self.assertIn("captured_at", metadata)
            self.assertTrue(metadata["raw_object_id"].startswith("raw_brightdata_run_001_post_"))

            saved_metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            serialized = json.dumps(saved_metadata, sort_keys=True)
            self.assertNotIn("secret-token", serialized)
            self.assertNotIn("secret-cookie", serialized)
            self.assertNotIn("secret-key", serialized)
            self.assertEqual(saved_metadata["request_headers"]["Authorization"], "[REDACTED]")
            self.assertEqual(saved_metadata["request_headers"]["Cookie"], "[REDACTED]")
            self.assertEqual(saved_metadata["request_headers"]["x-access-key"], "[REDACTED]")
            self.assertIn("token=%5BREDACTED%5D", saved_metadata["request_url"])


if __name__ == "__main__":
    unittest.main()
