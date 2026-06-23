import json
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path

from scripts.instagram_content_dump import (
    build_content_dump,
    fetch_public_html,
    parse_instagram_public_html,
    select_top_posts,
)


PUBLIC_HTML = """
<!doctype html>
<html>
<head>
  <meta property="og:image" content="https://cdn.example/slide0.jpg" />
  <meta property="og:description" content="616K likes, 1,418 comments - wetheurban on February 13, 2026: &quot;Leave a 💛 below if any of these resonated. Words: @writer&quot;. " />
  <meta property="og:url" content="https://www.instagram.com/wetheurban/p/DUtQzmaj9Rw/" />
  <meta name="twitter:title" content="WE THE URBAN (@wetheurban) • Instagram photos and videos" />
  <meta property="al:ios:url" content="instagram://media?id=3831792772647474288" />
  <meta property="instapp:owner_user_id" content="13737750" />
</head>
<body>Login shell</body>
</html>
"""


class InstagramContentDumpTests(unittest.TestCase):
    def test_parses_public_instagram_meta_description(self):
        parsed = parse_instagram_public_html(PUBLIC_HTML)

        self.assertEqual(parsed["status"], "public_meta_found")
        self.assertEqual(parsed["likes"], 616000)
        self.assertEqual(parsed["comments"], 1418)
        self.assertEqual(parsed["account_username"], "wetheurban")
        self.assertEqual(parsed["published_label"], "February 13, 2026")
        self.assertEqual(parsed["caption_preview"], "Leave a 💛 below if any of these resonated. Words: @writer")
        self.assertEqual(parsed["primary_image_url"], "https://cdn.example/slide0.jpg")
        self.assertEqual(parsed["instagram_media_id"], "3831792772647474288")
        self.assertEqual(parsed["owner_user_id"], "13737750")

    def test_selects_top_posts_from_seed_file(self):
        posts = [
            _post("low", likes=50, score=10),
            _post("high-score", likes=100, score=999),
            _post("high-likes", likes=900, score=20),
        ]

        selected = select_top_posts(posts, limit=2, sort_by="winnerScore")

        self.assertEqual([post["shortCode"] for post in selected], ["high-score", "high-likes"])

    def test_fetch_public_html_uses_curl_backend(self):
        with patch("scripts.instagram_content_dump.subprocess.run") as run:
            run.return_value = SimpleNamespace(
                returncode=0,
                stdout=PUBLIC_HTML.encode("utf-8"),
                stderr=b"",
            )

            page = fetch_public_html("https://www.instagram.com/p/DUtQzmaj9Rw/")

        self.assertIn("og:description", page)
        command = run.call_args.args[0]
        self.assertEqual(command[:4], ["curl", "-L", "--fail", "-sS"])
        self.assertEqual(command[-1], "https://www.instagram.com/p/DUtQzmaj9Rw/")

    def test_builds_rag_ready_dump_from_seed_and_live_fetcher(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            seed_path = root / "references/text-style/winner-bank/posts_merged.json"
            seed_path.parent.mkdir(parents=True)
            seed_path.write_text(
                json.dumps(
                    [
                        _post(
                            "DUtQzmaj9Rw",
                            account="wetheurban",
                            likes=615337,
                            comments=1417,
                            score=123,
                            caption="Full local caption from the earlier scrape.",
                            kind="Sidecar",
                            child_count=19,
                        )
                    ]
                ),
                encoding="utf-8",
            )

            def fetcher(url: str) -> str:
                self.assertEqual(url, "https://www.instagram.com/p/DUtQzmaj9Rw/")
                return PUBLIC_HTML

            result = build_content_dump(
                root,
                output_dir=root / "content-dump",
                source_path=seed_path,
                limit=1,
                fetch_html=fetcher,
                download_media=False,
            )

            manifest = json.loads((root / result["manifest"]).read_text(encoding="utf-8"))
            self.assertEqual(manifest["post_count"], 1)
            self.assertEqual(manifest["posts"][0]["id"], "ig:DUtQzmaj9Rw")
            self.assertEqual(manifest["posts"][0]["post_type"], "carousel")
            self.assertEqual(manifest["posts"][0]["asset_slots"], 19)
            self.assertEqual(manifest["posts"][0]["public_html"]["likes"], 616000)

            jsonl = (root / result["jsonl"]).read_text(encoding="utf-8").strip()
            record = json.loads(jsonl)
            self.assertEqual(record["source_url"], "https://www.instagram.com/p/DUtQzmaj9Rw/")
            self.assertEqual(record["caption"]["text"], "Full local caption from the earlier scrape.")
            self.assertEqual(record["assets"][0]["remote_url"], "https://cdn.example/slide0.jpg")
            self.assertEqual(record["gaps"][0]["status"], "not_attempted")

    def test_builds_offline_dump_without_fetching_public_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            seed_path = root / "references/text-style/winner-bank/posts_merged.json"
            seed_path.parent.mkdir(parents=True)
            seed_path.write_text(
                json.dumps(
                    [
                        _post(
                            "AAA",
                            likes=12,
                            score=12,
                            caption="Stored caption.",
                            kind="Image",
                        )
                    ]
                ),
                encoding="utf-8",
            )

            def fetcher(url: str) -> str:
                raise AssertionError("fetcher should not run in offline mode")

            result = build_content_dump(
                root,
                output_dir=root / "offline-dump",
                source_path=seed_path,
                limit=1,
                fetch_html=fetcher,
                fetch_public_pages=False,
            )

            record = json.loads((root / result["jsonl"]).read_text(encoding="utf-8"))
            self.assertEqual(record["public_html"]["status"], "not_attempted")
            self.assertIsNone(record["evidence_paths"]["public_html"])
            public_gap = next(gap for gap in record["gaps"] if gap["field"] == "public_html")
            self.assertEqual(public_gap["status"], "not_attempted")

    def test_jsonl_escapes_unicode_line_separators_for_one_record_per_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            seed_path = root / "references/text-style/winner-bank/posts_merged.json"
            seed_path.parent.mkdir(parents=True)
            seed_path.write_text(
                json.dumps(
                    [
                        _post(
                            "AAA",
                            likes=12,
                            score=12,
                            caption="first\u2028second",
                        )
                    ]
                ),
                encoding="utf-8",
            )

            result = build_content_dump(
                root,
                output_dir=root / "jsonl-dump",
                source_path=seed_path,
                limit=1,
                fetch_public_pages=False,
            )

            lines = (root / result["jsonl"]).read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)
            self.assertEqual(json.loads(lines[0])["caption"]["text"], "first\u2028second")


def _post(
    shortcode: str,
    *,
    account: str = "account",
    likes: int,
    comments: int = 0,
    score: int,
    caption: str = "",
    kind: str = "Image",
    child_count: int = 0,
) -> dict:
    return {
        "shortCode": shortcode,
        "ownerUsername": account,
        "ownerFullName": account,
        "url": f"https://www.instagram.com/p/{shortcode}/",
        "type": kind,
        "productType": "clips" if kind == "Video" else None,
        "caption": caption,
        "captionWords": len(caption.split()),
        "hashtags": [],
        "likesCount": likes,
        "commentsCount": comments,
        "videoViewCount": None,
        "videoPlayCount": None,
        "winnerScore": score,
        "childCount": child_count,
        "displayUrl": "https://seed.example/display.jpg",
        "timestamp": "2026-06-01T00:00:00.000Z",
        "mechanicTags": [],
    }


if __name__ == "__main__":
    unittest.main()
