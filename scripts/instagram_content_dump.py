#!/usr/bin/env python3
"""Build a RAG-friendly evidence dump for ranked Instagram posts.

This is intentionally boring infrastructure: seed from the known winner-bank
URLs, fetch the public Instagram page where possible, preserve source evidence,
and write one normalized document per post. Public HTML usually exposes caption
preview, metrics, canonical image, and owner metadata; it usually does not expose
all carousel child slides without an authenticated browser/provider pass.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_SOURCE = Path("references/text-style/winner-bank/posts_merged.json")
DEFAULT_OUTPUT = Path("references/text-style/content-dump")
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36"
)


class _MetaParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.meta: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "meta":
            return
        payload = {key: value or "" for key, value in attrs}
        key = payload.get("property") or payload.get("name")
        value = payload.get("content")
        if key and value is not None:
            self.meta[key] = html.unescape(value)


def parse_instagram_public_html(page_html: str) -> dict[str, Any]:
    """Extract the stable public meta layer from an Instagram post page."""

    parser = _MetaParser()
    parser.feed(page_html)
    meta = parser.meta
    description = meta.get("og:description") or meta.get("description") or ""
    parsed_description = _parse_description(description)

    return {
        "status": "public_meta_found" if description else "public_meta_missing",
        "likes": parsed_description.get("likes"),
        "comments": parsed_description.get("comments"),
        "account_username": parsed_description.get("account_username")
        or _username_from_title(meta.get("twitter:title")),
        "published_label": parsed_description.get("published_label"),
        "caption_preview": parsed_description.get("caption_preview"),
        "primary_image_url": meta.get("og:image") or meta.get("twitter:image"),
        "canonical_url": meta.get("og:url"),
        "instagram_media_id": _media_id(meta.get("al:ios:url")),
        "owner_user_id": meta.get("instapp:owner_user_id"),
        "raw_description": description,
    }


def select_top_posts(
    posts: list[dict[str, Any]],
    limit: int,
    sort_by: str = "winnerScore",
) -> list[dict[str, Any]]:
    def score(post: dict[str, Any]) -> tuple[float, int, int]:
        primary = post.get(sort_by)
        if primary is None:
            primary = post.get("winnerScore")
        if primary is None:
            primary = post.get("likesCount")
        return (
            float(primary or 0),
            int(post.get("likesCount") or 0),
            int(post.get("commentsCount") or 0),
        )

    return sorted(posts, key=score, reverse=True)[:limit]


def build_content_dump(
    repo_root: str | Path,
    output_dir: str | Path,
    source_path: str | Path = DEFAULT_SOURCE,
    limit: int = 170,
    sort_by: str = "winnerScore",
    fetch_html: Callable[[str], str] | None = None,
    fetch_public_pages: bool = True,
    download_media: bool = False,
) -> dict[str, str]:
    root = Path(repo_root)
    source = Path(source_path)
    if not source.is_absolute():
        source = root / source
    out = Path(output_dir)
    if not out.is_absolute():
        out = root / out
    out.mkdir(parents=True, exist_ok=True)
    posts_dir = out / "posts"
    posts_dir.mkdir(exist_ok=True)

    raw_posts = _read_json(source)
    if not isinstance(raw_posts, list):
        raise ValueError(f"Expected list in {source}")
    selected = select_top_posts(raw_posts, limit=limit, sort_by=sort_by)
    fetcher = fetch_html or fetch_public_html

    records: list[dict[str, Any]] = []
    for index, post in enumerate(selected, start=1):
        record = _build_record(
            index,
            post,
            root,
            posts_dir,
            fetcher,
            fetch_public_pages,
            download_media,
        )
        records.append(record)

    manifest = {
        "schema_version": "instagram_content_dump.v1",
        "built_at": _now(),
        "source_file": _rel(root, source),
        "sort_by": sort_by,
        "post_count": len(records),
        "posts": [
            {
                "id": record["id"],
                "rank": record["rank"],
                "account": record["account"]["username"],
                "shortcode": record["shortcode"],
                "post_type": record["post_type"],
                "source_url": record["source_url"],
                "likes": record["metrics"].get("likes"),
                "comments": record["metrics"].get("comments"),
                "asset_slots": len(record["assets"]),
                "public_html": record["public_html"],
                "gaps": record["gaps"],
            }
            for record in records
        ],
    }

    manifest_path = out / "manifest.json"
    jsonl_path = out / "content_dump.jsonl"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True, ensure_ascii=True) + "\n")

    return {
        "manifest": _rel(root, manifest_path),
        "jsonl": _rel(root, jsonl_path),
        "posts_dir": _rel(root, posts_dir),
    }


def fetch_public_html(url: str) -> str:
    result = subprocess.run(
        [
            "curl",
            "-L",
            "--fail",
            "-sS",
            "--connect-timeout",
            "10",
            "--max-time",
            "30",
            "--retry",
            "1",
            "-A",
            USER_AGENT,
            url,
        ],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise OSError(message or f"curl failed with exit {result.returncode}")
    return result.stdout.decode("utf-8", errors="replace")


def _build_record(
    rank: int,
    post: dict[str, Any],
    root: Path,
    posts_dir: Path,
    fetcher: Callable[[str], str],
    fetch_public_pages: bool,
    download_media: bool,
) -> dict[str, Any]:
    shortcode = str(post.get("shortCode") or _shortcode_from_url(post.get("url")) or "")
    source_url = str(post.get("url") or f"https://www.instagram.com/p/{shortcode}/")
    post_id = f"ig:{shortcode}"
    post_dir = posts_dir / post_id.replace(":", "_")
    assets_dir = post_dir / "assets"
    post_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(exist_ok=True)

    public_html: dict[str, Any]
    page_html = ""
    if not fetch_public_pages:
        public_html = {
            "status": "not_attempted",
            "likes": None,
            "comments": None,
            "caption_preview": None,
            "primary_image_url": None,
        }
    else:
        try:
            page_html = fetcher(source_url)
            public_html = parse_instagram_public_html(page_html)
            (post_dir / "public_page.html").write_text(page_html, encoding="utf-8")
        except (HTTPError, URLError, TimeoutError, OSError) as error:
            public_html = {
                "status": "fetch_failed",
                "error": str(error),
                "likes": None,
                "comments": None,
                "caption_preview": None,
                "primary_image_url": None,
            }

    assets = _assets(post, public_html, root, assets_dir, download_media)
    record = {
        "schema_version": "instagram_content_dump.post.v1",
        "rank": rank,
        "id": post_id,
        "shortcode": shortcode,
        "source_url": source_url,
        "account": {
            "username": post.get("ownerUsername") or public_html.get("account_username"),
            "full_name": post.get("ownerFullName"),
            "instagram_user_id": public_html.get("owner_user_id"),
        },
        "post_type": _post_type(post),
        "raw_type": post.get("type"),
        "published_at": post.get("timestamp"),
        "published_label": public_html.get("published_label"),
        "metrics": {
            "likes": post.get("likesCount") or public_html.get("likes"),
            "comments": post.get("commentsCount") or public_html.get("comments"),
            "views": post.get("videoViewCount"),
            "plays": post.get("videoPlayCount"),
            "winner_score": post.get("winnerScore"),
            "public_html_likes": public_html.get("likes"),
            "public_html_comments": public_html.get("comments"),
        },
        "caption": {
            "text": post.get("caption") or "",
            "word_count": post.get("captionWords"),
            "hashtags": post.get("hashtags") or [],
            "public_preview": public_html.get("caption_preview"),
        },
        "assets": assets,
        "public_html": public_html,
        "communication_seed": {
            "mechanic_tags": post.get("mechanicTags") or [],
            "first_comment": post.get("firstComment") or "",
            "latest_comments": post.get("latestComments") or [],
        },
        "gaps": _gaps(post, assets, public_html),
        "evidence_paths": {
            "folder": _rel(root, post_dir),
            "public_html": _rel(root, post_dir / "public_page.html") if page_html else None,
            "record_json": _rel(root, post_dir / "record.json"),
        },
    }
    (post_dir / "record.json").write_text(
        json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return record


def _assets(
    post: dict[str, Any],
    public_html: dict[str, Any],
    root: Path,
    assets_dir: Path,
    download_media: bool,
) -> list[dict[str, Any]]:
    post_type = _post_type(post)
    child_count = int(post.get("childCount") or 0)
    slot_count = child_count if post_type == "carousel" and child_count > 0 else 1
    primary_url = public_html.get("primary_image_url") or post.get("displayUrl")
    assets: list[dict[str, Any]] = []
    for index in range(slot_count):
        remote_url = primary_url if index == 0 else None
        local_path = None
        status = "remote_url_present" if remote_url else "missing_child_asset_url"
        if remote_url and download_media:
            local_file = assets_dir / f"{index:02d}.jpg"
            try:
                _download(remote_url, local_file)
                local_path = _rel(root, local_file)
                status = "downloaded"
            except (HTTPError, URLError, TimeoutError, OSError) as error:
                status = f"download_failed: {error}"
        assets.append(
            {
                "asset_id": f"ig:{post.get('shortCode')}:asset:{index:02d}",
                "index": index,
                "role": "slide" if post_type == "carousel" else "primary",
                "media_type": "video_thumbnail" if post_type == "reel" else "image",
                "remote_url": remote_url,
                "local_path": local_path,
                "status": status,
                "ocr_text": None,
                "visual_notes": None,
                "style_notes": None,
            }
        )
    return assets


def _gaps(
    post: dict[str, Any],
    assets: list[dict[str, Any]],
    public_html: dict[str, Any],
) -> list[dict[str, str]]:
    gaps = [
        {
            "field": "assets[].ocr_text",
            "status": "not_attempted",
            "reason": "OCR is a separate pass over downloaded images/screenshots.",
        },
        {
            "field": "assets[].visual_notes",
            "status": "not_attempted",
            "reason": "Visual/style analysis should run after assets are downloaded.",
        },
    ]
    if any(asset["remote_url"] is None for asset in assets):
        gaps.append(
            {
                "field": "assets[].remote_url",
                "status": "not_scraped",
                "reason": "Public unauthenticated Instagram HTML did not expose every carousel child URL.",
            }
        )
    if public_html.get("status") == "not_attempted":
        gaps.append(
            {
                "field": "public_html",
                "status": "not_attempted",
                "reason": "Offline mode skipped public Instagram page fetches.",
            }
        )
    elif public_html.get("status") != "public_meta_found":
        gaps.append(
            {
                "field": "public_html",
                "status": "not_scraped",
                "reason": "Public page fetch did not return parseable Instagram meta tags.",
            }
        )
    if _post_type(post) == "reel":
        gaps.append(
            {
                "field": "reel_transcript",
                "status": "not_attempted",
                "reason": "Transcript extraction needs a video/audio pass.",
            }
        )
    gaps.extend(
        [
            {
                "field": "metrics.saves",
                "status": "not_scraped",
                "reason": "Third-party saves are not public Instagram metrics.",
            },
            {
                "field": "metrics.shares",
                "status": "not_scraped",
                "reason": "Third-party shares are not public Instagram metrics.",
            },
        ]
    )
    return gaps


def _parse_description(description: str) -> dict[str, Any]:
    match = re.search(
        r"(?P<likes>[\d,.]+[KMB]?)\s+likes,\s+"
        r"(?P<comments>[\d,.]+[KMB]?)\s+comments\s+-\s+"
        r"(?P<account>[\w.]+)\s+on\s+"
        r"(?P<date>.*?):\s+\"(?P<caption>.*?)\"",
        description,
        re.S,
    )
    if not match:
        return {}
    return {
        "likes": _parse_count(match.group("likes")),
        "comments": _parse_count(match.group("comments")),
        "account_username": match.group("account"),
        "published_label": match.group("date").strip(),
        "caption_preview": match.group("caption").strip(),
    }


def _parse_count(value: str) -> int:
    value = value.strip().upper()
    multiplier = 1
    if value.endswith("K"):
        multiplier = 1_000
        value = value[:-1]
    elif value.endswith("M"):
        multiplier = 1_000_000
        value = value[:-1]
    elif value.endswith("B"):
        multiplier = 1_000_000_000
        value = value[:-1]
    return int(float(value.replace(",", "")) * multiplier)


def _post_type(post: dict[str, Any]) -> str:
    raw_type = str(post.get("type") or "").lower()
    product_type = str(post.get("productType") or "").lower()
    if raw_type == "sidecar":
        return "carousel"
    if raw_type == "video" or product_type == "clips":
        return "reel"
    return "image"


def _download(url: str, path: Path) -> None:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30) as response:
        path.write_bytes(response.read())


def _username_from_title(title: str | None) -> str | None:
    if not title:
        return None
    match = re.search(r"\(@([^)]+)\)", title)
    return match.group(1) if match else None


def _media_id(url: str | None) -> str | None:
    if not url:
        return None
    match = re.search(r"media\?id=(\d+)", url)
    return match.group(1) if match else None


def _shortcode_from_url(url: str | None) -> str | None:
    if not url:
        return None
    match = re.search(r"/(?:p|reel)/([^/?#]+)/?", url)
    return match.group(1) if match else None


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dump top Instagram winner content for RAG.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--limit", type=int, default=170)
    parser.add_argument("--sort-by", default="winnerScore")
    parser.add_argument("--download-media", action="store_true")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip public Instagram page fetches and dump only the seed corpus.",
    )
    args = parser.parse_args(argv)

    try:
        artifacts = build_content_dump(
            args.repo_root,
            args.output_dir,
            source_path=args.source,
            limit=args.limit,
            sort_by=args.sort_by,
            fetch_public_pages=not args.offline,
            download_media=args.download_media,
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"instagram content dump failed: {error}", file=sys.stderr)
        return 1

    print(json.dumps({"status": "ok", "artifacts": artifacts}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
