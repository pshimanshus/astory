import io
import json
import tempfile
import unittest
from pathlib import Path
from urllib.error import HTTPError

from scripts import instagram_pull_carousel


class InstagramPullCarouselTests(unittest.TestCase):
    def test_choose_latest_carousel_uses_first_carousel_album(self):
        media = [
            {"id": "reel-1", "media_type": "VIDEO"},
            {
                "id": "carousel-1",
                "media_type": "CAROUSEL_ALBUM",
                "permalink": "https://www.instagram.com/p/new/",
            },
            {
                "id": "carousel-2",
                "media_type": "CAROUSEL_ALBUM",
                "permalink": "https://www.instagram.com/p/old/",
            },
        ]

        selected = instagram_pull_carousel.choose_carousel(media)

        self.assertEqual(selected["id"], "carousel-1")

    def test_choose_carousel_can_match_permalink(self):
        media = [
            {
                "id": "carousel-1",
                "media_type": "CAROUSEL_ALBUM",
                "permalink": "https://www.instagram.com/p/new/",
            },
            {
                "id": "carousel-2",
                "media_type": "CAROUSEL_ALBUM",
                "permalink": "https://www.instagram.com/p/old/",
            },
        ]

        selected = instagram_pull_carousel.choose_carousel(
            media, permalink="https://www.instagram.com/p/old/"
        )

        self.assertEqual(selected["id"], "carousel-2")

    def test_pull_carousel_export_omits_access_token_and_includes_comments(self):
        requested_urls = []

        def fake_get_json(url):
            requested_urls.append(url)
            if url.startswith("https://graph.instagram.com/v21.0/me/media"):
                return {
                    "data": [
                        {
                            "id": "carousel-1",
                            "media_type": "CAROUSEL_ALBUM",
                            "permalink": "https://www.instagram.com/p/new/",
                            "children": {
                                "data": [
                                    {
                                        "id": "child-1",
                                        "media_type": "IMAGE",
                                        "media_url": "https://cdn.example/slide.jpg",
                                    }
                                ]
                            },
                        }
                    ],
                    "paging": {
                        "next": "https://graph.instagram.com/v21.0/me/media?access_token=secret-token"
                    },
                }
            if url.startswith(
                "https://graph.instagram.com/v21.0/carousel-1/comments"
            ):
                return {
                    "data": [
                        {
                            "id": "comment-1",
                            "text": "beautiful",
                            "username": "reader",
                        }
                    ]
                }
            self.fail(f"Unexpected URL: {url}")

        export = instagram_pull_carousel.pull_latest_carousel(
            {
                "INSTAGRAM_ACCESS_TOKEN": "secret-token",
                "INSTAGRAM_USER_ID": "17841442026478504",
                "INSTAGRAM_USERNAME": "a.storyof.two",
            },
            get_json=fake_get_json,
            scan_limit=1,
            include_insights=False,
        )

        export_text = json.dumps(export)
        self.assertEqual(export["post"]["id"], "carousel-1")
        self.assertEqual(export["child_count"], 1)
        self.assertEqual(export["comment_count"], 1)
        self.assertEqual(export["comments"][0]["text"], "beautiful")
        self.assertNotIn("secret-token", export_text)
        self.assertTrue(any("access_token=secret-token" in url for url in requested_urls))

    def test_fetch_media_insights_records_available_and_permission_denied(self):
        def fake_get_json(url):
            if "metric=reach" in url:
                return {"data": [{"name": "reach", "total_value": {"value": 12345}}]}
            if "metric=saved" in url:
                return {"data": [{"name": "saved", "total_value": {"value": 678}}]}
            raise HTTPError(
                url,
                403,
                "Forbidden",
                {},
                io.BytesIO(
                    b'{"error":{"message":"Application does not have '
                    b'permission for this action"}}'
                ),
            )

        result = instagram_pull_carousel.fetch_media_insights(
            "carousel-1",
            {"INSTAGRAM_ACCESS_TOKEN": "secret-token"},
            get_json=fake_get_json,
            metrics=["reach", "saved", "shares"],
        )

        self.assertEqual(result["available"]["reach"], 12345)
        self.assertEqual(result["available"]["saved"], 678)
        self.assertIn("shares", result["denied"])
        self.assertEqual(result["errors"], {})

    def test_fetch_media_insights_retries_with_metric_type_total_value(self):
        seen = []

        def fake_get_json(url):
            seen.append(url)
            if "metric_type=total_value" in url:
                return {"data": [{"name": "views", "total_value": {"value": 99}}]}
            raise HTTPError(
                url,
                400,
                "Bad Request",
                {},
                io.BytesIO(
                    b'{"error":{"message":"metric_type must be specified"}}'
                ),
            )

        result = instagram_pull_carousel.fetch_media_insights(
            "carousel-1",
            {"INSTAGRAM_ACCESS_TOKEN": "secret-token"},
            get_json=fake_get_json,
            metrics=["views"],
        )

        self.assertEqual(result["available"]["views"], 99)
        self.assertTrue(any("metric_type=total_value" in url for url in seen))

    def test_write_export_uses_post_shortcode_folder_when_available(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_path = instagram_pull_carousel.write_export(
                Path(tmp),
                {
                    "post": {
                        "id": "carousel-1",
                        "permalink": "https://www.instagram.com/p/DZc_HnOiR0W/",
                    },
                    "comments": [],
                },
            )

            self.assertEqual(output_path.name, "carousel_export.json")
            self.assertEqual(output_path.parent.name, "DZc_HnOiR0W")
            self.assertTrue(output_path.exists())


if __name__ == "__main__":
    unittest.main()
