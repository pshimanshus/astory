"""Pull a full first-party inventory of the account's media (reels, carousels,
photos) with best-effort per-post insights.

Reuses the token-safe helpers in ``instagram_pull_carousel`` /
``instagram_check`` so it never prints the access token. Two modes:

* ``--list-only`` — one fast pass over ``me/media`` (no insight calls). Maps the
  whole account: media type, product type, permalink, caption, like/comment
  counts, posting cadence.
* default — the list pass plus a best-effort insights pull per post
  (reach, views, shares, saved, total_interactions). ``like_count`` and
  ``comments_count`` already come from the media list, so they are not re-fetched.

Output: a single consolidated ``account_inventory.json`` (full records) under the
output dir, plus a printed summary.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError

try:
    from scripts.instagram_check import InstagramCheckError, fetch_json, load_env_file
    from scripts.instagram_pull_carousel import (
        MEDIA_FIELDS,
        _access_token,
        _shortcode_from_permalink,
        _utc_now_iso,
        build_url,
        fetch_collection,
        fetch_media_insights,
    )
except ModuleNotFoundError:  # pragma: no cover - import shim for direct runs
    from instagram_check import InstagramCheckError, fetch_json, load_env_file  # type: ignore
    from instagram_pull_carousel import (  # type: ignore
        MEDIA_FIELDS,
        _access_token,
        _shortcode_from_permalink,
        _utc_now_iso,
        build_url,
        fetch_collection,
        fetch_media_insights,
    )


# The insight metrics that matter for the study and that the website's "proof"
# leans on. like_count / comments_count come free with the media list.
STUDY_METRICS = ["reach", "views", "shares", "saved", "total_interactions"]


def list_all_media(
    env: dict[str, str],
    get_json: Callable[[str], dict[str, Any]] = fetch_json,
    scan_limit: int = 200,
) -> list[dict[str, Any]]:
    """Return every media item visible to the token (newest first)."""

    access_token = _access_token(env)
    return fetch_collection(
        build_url(
            "me/media",
            access_token,
            {"fields": MEDIA_FIELDS, "limit": min(scan_limit, 100)},
        ),
        get_json=get_json,
        max_items=scan_limit,
    )


def summarize_media(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item.get("id"),
        "shortcode": _shortcode_from_permalink(item.get("permalink")),
        "permalink": item.get("permalink"),
        "media_type": item.get("media_type"),
        "media_product_type": item.get("media_product_type"),
        "timestamp": item.get("timestamp"),
        "like_count": item.get("like_count"),
        "comments_count": item.get("comments_count"),
        "child_count": len(item.get("children", {}).get("data", [])),
        "thumbnail_url": item.get("thumbnail_url"),
        "media_url": item.get("media_url"),
        "caption": item.get("caption"),
    }


def build_inventory(
    env: dict[str, str],
    get_json: Callable[[str], dict[str, Any]] = fetch_json,
    scan_limit: int = 200,
    include_insights: bool = True,
) -> dict[str, Any]:
    media = list_all_media(env, get_json=get_json, scan_limit=scan_limit)
    records: list[dict[str, Any]] = []
    for item in media:
        record = summarize_media(item)
        if include_insights and record["id"]:
            insights = fetch_media_insights(
                record["id"], env, get_json=get_json, metrics=STUDY_METRICS
            )
            record["insights"] = insights.get("available", {})
            record["insights_denied"] = insights.get("denied", [])
        records.append(record)

    return {
        "schema_version": "1.0",
        "pulled_at": _utc_now_iso(),
        "account": {
            "user_id": env.get("INSTAGRAM_USER_ID"),
            "username": env.get("INSTAGRAM_USERNAME"),
        },
        "media_count": len(records),
        "media": records,
    }


def _type_breakdown(records: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        key = f"{record.get('media_type')}/{record.get('media_product_type')}"
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: kv[1], reverse=True))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pull a full first-party account inventory.")
    parser.add_argument("--env", default=".env.local", help="Env file path.")
    parser.add_argument(
        "--output-dir",
        default="data/instagram",
        help="Directory for the consolidated inventory JSON.",
    )
    parser.add_argument("--scan-limit", type=int, default=200, help="Max media to scan.")
    parser.add_argument(
        "--list-only",
        action="store_true",
        help="Fast pass: skip the per-post insight calls.",
    )
    args = parser.parse_args(argv)

    env = load_env_file(args.env)

    try:
        inventory = build_inventory(
            env,
            scan_limit=args.scan_limit,
            include_insights=not args.list_only,
        )
    except InstagramCheckError as error:
        print(f"instagram account pull failed: {error}", file=sys.stderr)
        return 2
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        print(f"instagram account pull failed: HTTP {error.code}: {body}", file=sys.stderr)
        return 1
    except (URLError, TimeoutError, json.JSONDecodeError) as error:
        print(f"instagram account pull failed: {error}", file=sys.stderr)
        return 1

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    name = "account_inventory.json" if not args.list_only else "account_inventory_list.json"
    out_path = out_dir / name
    out_path.write_text(
        json.dumps(inventory, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "status": "ok",
                "output": str(out_path),
                "media_count": inventory["media_count"],
                "type_breakdown": _type_breakdown(inventory["media"]),
                "insights": "skipped" if args.list_only else "pulled",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
