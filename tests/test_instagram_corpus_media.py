import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.instagram_corpus.media import store_media


class InstagramCorpusMediaTests(unittest.TestCase):
    def test_stores_content_addressed_media_with_sidecar(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            content = b"image bytes from provider"
            sha256 = hashlib.sha256(content).hexdigest()

            stored = store_media(
                root,
                "https://cdn.example/slide-01.jpg",
                content,
                "image/jpeg",
                "raw_brightdata_01",
            )

            expected_path = root / "media" / "sha256" / sha256[:2] / f"{sha256}.jpg"
            self.assertEqual(stored["path"], str(expected_path))
            self.assertEqual(stored["sha256"], sha256)
            self.assertTrue(expected_path.exists())
            self.assertEqual(expected_path.read_bytes(), content)

            sidecar_path = Path(stored["sidecar_path"])
            sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
            self.assertEqual(sidecar["sha256"], sha256)
            self.assertEqual(sidecar["source_url"], "https://cdn.example/slide-01.jpg")
            self.assertEqual(sidecar["mime"], "image/jpeg")
            self.assertEqual(sidecar["bytes"], len(content))
            self.assertIsNone(sidecar["width"])
            self.assertIsNone(sidecar["height"])
            self.assertIsNone(sidecar["duration_seconds"])
            self.assertEqual(sidecar["rights_scope"], "third_party_analysis_only")
            self.assertEqual(sidecar["variant"], "original")
            self.assertEqual(sidecar["raw_object_id"], "raw_brightdata_01")

    def test_duplicate_content_resolves_to_same_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            content = b"same bytes"

            first = store_media(
                root,
                "https://cdn.example/a.png",
                content,
                "image/png",
                "raw_1",
                variant="display",
            )
            second = store_media(
                root,
                "https://cdn.example/a.png",
                content,
                "image/png",
                "raw_1",
                variant="display",
            )

            self.assertEqual(second["path"], first["path"])
            media_files = list((root / "media" / "sha256").rglob("*.png"))
            self.assertEqual(media_files, [Path(first["path"])])

    def test_unknown_mime_uses_bin_extension_without_losing_mime(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stored = store_media(
                root,
                "https://cdn.example/blob",
                b"raw blob",
                "application/octet-stream",
                "raw_blob",
            )

            self.assertTrue(stored["path"].endswith(".bin"))
            sidecar = json.loads(Path(stored["sidecar_path"]).read_text(encoding="utf-8"))
            self.assertEqual(sidecar["mime"], "application/octet-stream")


if __name__ == "__main__":
    unittest.main()
