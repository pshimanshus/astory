import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from scripts.research_bank_builder import build_research_bank, write_research_bank


class ResearchBankBuilderTests(unittest.TestCase):
    def test_normalizes_posts_with_stable_ids_metrics_and_slide_gaps(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_raw_posts(
                root,
                [
                    _post(
                        account="wetheurban",
                        shortcode="AAA",
                        kind="Sidecar",
                        child_count=3,
                        child_types=["Image", "Image", "Image"],
                        caption="The little things are often the biggest things.",
                        tags=["carousel", "direct_you", "first_person"],
                    ),
                    _post(
                        account="werenotreallystrangers",
                        shortcode="BBB",
                        kind="Video",
                        child_count=0,
                        child_types=[],
                        caption="made me think",
                        tags=["reel", "first_person"],
                        video_views=1000,
                        video_plays=2000,
                    ),
                ],
            )

            bank = build_research_bank(root)

            self.assertEqual(bank["schema_version"], "1.0")
            self.assertEqual(bank["summary"]["total_records"], 2)
            records = {record["id"]: record for record in bank["records"]}
            self.assertIn("ig:wetheurban:AAA", records)
            self.assertIn("ig:werenotreallystrangers:BBB", records)

            sidecar = records["ig:wetheurban:AAA"]
            self.assertEqual(sidecar["source"]["post_type"], "carousel")
            self.assertEqual(len(sidecar["slides"]), 3)
            self.assertEqual(sidecar["slides"][0]["asset_status"], "display_url_only")
            self.assertEqual(
                sidecar["slides"][1]["asset_status"],
                "missing_child_url_in_source_scrape",
            )
            self.assertEqual(
                sidecar["slides"][2]["text"]["status"],
                "ocr_not_available",
            )
            self.assertIn("saves_unavailable", sidecar["metrics_gaps"])
            self.assertIn("shares_unavailable", sidecar["metrics_gaps"])
            self.assertIn("reach_unavailable", sidecar["metrics_gaps"])

            reel = records["ig:werenotreallystrangers:BBB"]
            self.assertEqual(reel["source"]["post_type"], "reel_video")
            self.assertEqual(reel["slides"][0]["visual"]["classification"], "reel_video")

    def test_enriches_first_party_exports_and_local_slide_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_raw_posts(
                root,
                [
                    _post(
                        account="a.storyof.two",
                        shortcode="AAA",
                        kind="Sidecar",
                        child_count=2,
                        child_types=["Image", "Image"],
                        caption="Share this to the person who stayed.",
                        tags=["carousel", "direct_you"],
                    )
                ],
            )
            export_dir = root / "data/instagram/carousel_posts/AAA"
            export_dir.mkdir(parents=True)
            (export_dir / "carousel_export.json").write_text(
                json.dumps(
                    {
                        "post": {
                            "shortcode": "AAA",
                            "permalink": "https://www.instagram.com/p/AAA/",
                            "media_type": "CAROUSEL_ALBUM",
                            "media_product_type": "FEED",
                        },
                        "children": [
                            {
                                "id": "slide-1",
                                "media_type": "IMAGE",
                                "media_url": "https://cdn.example/slide-1.jpg",
                            },
                            {
                                "id": "slide-2",
                                "media_type": "IMAGE",
                                "media_url": "https://cdn.example/slide-2.jpg",
                            },
                        ],
                        "insights": {
                            "available": {
                                "shares": 44,
                                "saved": 55,
                                "reach": 1000,
                                "views": 900,
                                "follows": 6,
                                "total_interactions": 200,
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )
            asset_dir = root / ".carousel_research"
            asset_dir.mkdir()
            Image.new("RGB", (20, 20), "white").save(asset_dir / "AAA_00.jpg")

            bank = build_research_bank(root)
            record = bank["records"][0]

            self.assertEqual(record["metrics"]["metric_source"], "first_party_graph_export")
            self.assertEqual(record["metrics"]["shares"], 44)
            self.assertEqual(record["metrics"]["saves"], 55)
            self.assertEqual(record["metrics"]["reach"], 1000)
            self.assertEqual(record["metrics"]["views"], 900)
            self.assertNotIn("shares_unavailable", record["metrics_gaps"])
            self.assertEqual(
                record["slides"][0]["local_asset_path"],
                ".carousel_research/AAA_00.jpg",
            )
            self.assertEqual(
                record["slides"][0]["visual"]["classification"],
                "likely_text_only_minimal_visuals",
            )

    def test_writes_json_and_markdown_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_raw_posts(
                root,
                [
                    _post(
                        account="wetheurban",
                        shortcode="AAA",
                        kind="Sidecar",
                        child_count=2,
                        child_types=["Image", "Image"],
                        caption="The little things are often the biggest things.",
                        tags=["carousel", "direct_you"],
                    )
                ],
            )

            artifacts = write_research_bank(
                root, root / "references/text-style/research-bank"
            )

            json_path = root / artifacts["json"]
            markdown_path = root / artifacts["summary_markdown"]
            self.assertTrue(json_path.exists())
            self.assertTrue(markdown_path.exists())

            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["summary"]["total_records"], 1)
            markdown = markdown_path.read_text(encoding="utf-8")
            self.assertIn("Total records: 1", markdown)
            self.assertIn("Format counts", markdown)
            self.assertIn("Extraction gaps", markdown)
            self.assertIn("Top posts", markdown)


def _write_raw_posts(root: Path, posts: list[dict]) -> None:
    bank_dir = root / "references/text-style/winner-bank"
    bank_dir.mkdir(parents=True)
    (bank_dir / "posts_merged.json").write_text(
        json.dumps(posts), encoding="utf-8"
    )


def _post(
    *,
    account: str,
    shortcode: str,
    kind: str,
    child_count: int,
    child_types: list[str],
    caption: str,
    tags: list[str],
    video_views: int = 0,
    video_plays: int = 0,
) -> dict:
    return {
        "ownerUsername": account,
        "ownerFullName": account,
        "url": f"https://www.instagram.com/p/{shortcode}/",
        "shortCode": shortcode,
        "type": kind,
        "productType": None,
        "timestamp": "2026-06-01T00:00:00.000Z",
        "caption": caption,
        "hashtags": [],
        "commentsCount": 5,
        "likesCount": 100,
        "videoViewCount": video_views,
        "videoPlayCount": video_plays,
        "dimensionsHeight": 1350,
        "dimensionsWidth": 1080,
        "childCount": child_count,
        "childTypes": child_types,
        "displayUrl": f"https://cdn.example/{shortcode}.jpg",
        "alt": "",
        "firstComment": "",
        "latestComments": [],
        "mechanicTags": tags,
        "captionWords": len(caption.split()),
        "winnerScore": 120,
        "commentToLikeRatio": 0.05,
        "commentTagProxy": 0,
        "commentSendProxy": 0,
    }


if __name__ == "__main__":
    unittest.main()
