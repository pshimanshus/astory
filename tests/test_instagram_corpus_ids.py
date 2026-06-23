import unittest

from scripts.instagram_corpus.ids import (
    media_hash_path,
    normalize_shortcode,
    post_id_from_shortcode,
)


class InstagramCorpusIdsTest(unittest.TestCase):
    def test_normalizes_raw_shortcode_without_changing_case(self):
        self.assertEqual(normalize_shortcode("  DUtQzmaj9Rw  "), "DUtQzmaj9Rw")

    def test_normalizes_shortcode_from_instagram_post_url(self):
        self.assertEqual(
            normalize_shortcode("https://www.instagram.com/p/DUtQzmaj9Rw/?utm_source=ig_web_copy_link"),
            "DUtQzmaj9Rw",
        )

    def test_normalizes_shortcode_from_schemeless_instagram_url(self):
        self.assertEqual(
            normalize_shortcode("www.instagram.com/p/DUtQzmaj9Rw/?img_index=1"),
            "DUtQzmaj9Rw",
        )

    def test_normalizes_shortcode_from_reel_and_tv_urls(self):
        self.assertEqual(
            normalize_shortcode("https://instagram.com/reel/DWmIMotjuZf/"),
            "DWmIMotjuZf",
        )
        self.assertEqual(
            normalize_shortcode("https://www.instagram.com/tv/CBa1_b-cD2e/?igsh=abc"),
            "CBa1_b-cD2e",
        )

    def test_rejects_missing_shortcode(self):
        with self.assertRaises(ValueError):
            normalize_shortcode("https://www.instagram.com/p/")

    def test_builds_stable_post_id(self):
        self.assertEqual(post_id_from_shortcode("DUtQzmaj9Rw"), "ig_DUtQzmaj9Rw")

    def test_builds_content_addressed_media_hash_path(self):
        self.assertEqual(
            media_hash_path("abcdef123456", ".JPG"),
            "sha256/ab/abcdef123456.jpg",
        )


if __name__ == "__main__":
    unittest.main()
