import dataclasses
import json
import unittest
from pathlib import Path

from scripts.instagram_corpus.providers import (
    ApifyProvider,
    BrightDataProvider,
    ManualJsonProvider,
    ProviderChild,
    ProviderPost,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "instagram_corpus"


class InstagramCorpusProviderTests(unittest.TestCase):
    def test_provider_records_are_dataclasses(self):
        self.assertTrue(dataclasses.is_dataclass(ProviderChild))
        self.assertTrue(dataclasses.is_dataclass(ProviderPost))

        child = ProviderChild(index=0, type="Photo", url="https://cdn.example.test/a.jpg")
        post = ProviderPost(
            source_url="https://www.instagram.com/p/DUtQzmaj9Rw/",
            shortcode="DUtQzmaj9Rw",
            caption="caption",
            metrics={"likes": 1, "comments": 2, "views": None, "plays": None},
            content_type="Photo",
            children=[child],
            raw={"provider": "test"},
        )

        self.assertEqual(dataclasses.asdict(post)["children"][0]["type"], "Photo")

    def test_manual_json_normalizes_brightdata_carousel_fixture(self):
        provider = ManualJsonProvider(FIXTURE_DIR / "brightdata_post_carousel.json")

        post = provider.fetch_post_by_url("https://www.instagram.com/p/DUtQzmaj9Rw/")

        self.assertEqual(post.source_url, "https://www.instagram.com/p/DUtQzmaj9Rw/")
        self.assertEqual(post.shortcode, "DUtQzmaj9Rw")
        self.assertEqual(post.caption, "Fixture caption from Bright Data.")
        self.assertEqual(
            post.metrics,
            {"likes": 163284, "comments": 528, "views": None, "plays": None},
        )
        self.assertEqual(post.content_type, "Carousel")
        self.assertEqual(
            dataclasses.asdict(post)["children"],
            [
                {
                    "index": 0,
                    "type": "Photo",
                    "url": "https://cdn.example.test/brightdata/slide-1.jpg",
                    "raw": {"provider_field": "photos"},
                },
                {
                    "index": 1,
                    "type": "Photo",
                    "url": "https://cdn.example.test/brightdata/slide-2.jpg",
                    "raw": {"provider_field": "photos"},
                },
                {
                    "index": 2,
                    "type": "Photo",
                    "url": "https://cdn.example.test/brightdata/slide-3.jpg",
                    "raw": {"provider_field": "post_content"},
                },
            ],
        )
        self.assertEqual(post.raw["provider"], "manual_json")
        self.assertEqual(post.raw["payload"]["content_type"], "Carousel")

    def test_manual_json_normalizes_apify_reel_fixture(self):
        provider = ManualJsonProvider(FIXTURE_DIR / "apify_post_reel.json")

        post = provider.fetch_post_by_url("https://www.instagram.com/reel/APIFYreel01/")

        self.assertEqual(post.source_url, "https://www.instagram.com/reel/APIFYreel01/")
        self.assertEqual(post.shortcode, "APIFYreel01")
        self.assertEqual(post.caption, "Fixture caption from Apify.")
        self.assertEqual(
            post.metrics,
            {"likes": 94210, "comments": 804, "views": 712345, "plays": 812345},
        )
        self.assertEqual(post.content_type, "Reel")
        self.assertEqual(len(post.children), 1)
        self.assertEqual(post.children[0].type, "Video")
        self.assertEqual(post.children[0].url, "https://cdn.example.test/apify/reel.mp4")

    def test_brightdata_provider_uses_injected_http_and_redacts_token(self):
        calls = []

        def fake_http_post(url, *, headers, json):
            calls.append({"url": url, "headers": headers, "json": json})
            payload = json_module_load("brightdata_post_carousel.json")
            payload["echoed_secret"] = "bd-secret-token"
            return [payload]

        provider = BrightDataProvider(token="bd-secret-token", http_post=fake_http_post)

        post = provider.fetch_post_by_url("https://www.instagram.com/p/DUtQzmaj9Rw/")

        self.assertEqual(len(calls), 1)
        self.assertIn("dataset_id=gd_lk5ns7kz21pck8jpis", calls[0]["url"])
        self.assertEqual(calls[0]["headers"]["Authorization"], "Bearer bd-secret-token")
        self.assertEqual(
            calls[0]["json"],
            {"input": [{"url": "https://www.instagram.com/p/DUtQzmaj9Rw/"}]},
        )
        self.assertEqual(post.raw["provider"], "brightdata")
        self.assertEqual(post.children[2].url, "https://cdn.example.test/brightdata/slide-3.jpg")
        self.assertNotIn("bd-secret-token", json.dumps(post.raw, sort_keys=True))

    def test_apify_provider_uses_injected_http_default_actor_and_redacts_token(self):
        calls = []

        def fake_http_post(url, *, headers, json):
            calls.append({"url": url, "headers": headers, "json": json})
            payload = json_module_load("apify_post_reel.json")
            payload["echoed_secret"] = "apify-secret-token"
            return [payload]

        provider = ApifyProvider(token="apify-secret-token", http_post=fake_http_post)

        post = provider.fetch_post_by_url("https://www.instagram.com/reel/APIFYreel01/")

        self.assertEqual(len(calls), 1)
        self.assertIn("apify~instagram-post-scraper", calls[0]["url"])
        self.assertEqual(calls[0]["headers"]["Authorization"], "Bearer apify-secret-token")
        self.assertEqual(
            calls[0]["json"]["directUrls"],
            ["https://www.instagram.com/reel/APIFYreel01/"],
        )
        self.assertEqual(post.raw["provider"], "apify")
        self.assertEqual(post.content_type, "Reel")
        self.assertEqual(post.children[0].url, "https://cdn.example.test/apify/reel.mp4")
        self.assertNotIn("apify-secret-token", json.dumps(post.raw, sort_keys=True))

    def test_apify_provider_normalizes_child_posts_when_present(self):
        calls = []

        def fake_http_post(url, *, headers, json):
            calls.append({"url": url, "headers": headers, "json": json})
            return [
                {
                    "url": "https://www.instagram.com/p/CAROUSEL01/",
                    "shortCode": "CAROUSEL01",
                    "text": "Carousel text from Apify.",
                    "likes": 100,
                    "comments": 9,
                    "type": "Sidecar",
                    "childPosts": [
                        {
                            "type": "Image",
                            "displayUrl": "https://cdn.example.test/apify/child-1.jpg",
                        },
                        {
                            "type": "Video",
                            "videoUrl": "https://cdn.example.test/apify/child-2.mp4",
                        },
                    ],
                }
            ]

        provider = ApifyProvider(
            token="apify-secret-token",
            actor="custom/instagram-reader",
            http_post=fake_http_post,
        )

        post = provider.fetch_post_by_url("https://www.instagram.com/p/CAROUSEL01/")

        self.assertIn("custom~instagram-reader", calls[0]["url"])
        self.assertEqual(post.content_type, "Carousel")
        self.assertEqual([child.type for child in post.children], ["Photo", "Video"])
        self.assertEqual(
            [child.url for child in post.children],
            [
                "https://cdn.example.test/apify/child-1.jpg",
                "https://cdn.example.test/apify/child-2.mp4",
            ],
        )


def json_module_load(name):
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
