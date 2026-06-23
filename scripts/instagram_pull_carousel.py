"""Pull token-safe data for an Instagram carousel post."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse

try:
    from scripts.instagram_check import (
        InstagramCheckError,
        fetch_json,
        load_env_file,
    )
except ModuleNotFoundError:
    from instagram_check import (  # type: ignore[no-redef]
        InstagramCheckError,
        fetch_json,
        load_env_file,
    )


API_VERSION = "v21.0"
GRAPH_BASE_URL = f"https://graph.instagram.com/{API_VERSION}"
TOKEN_ENV_KEY = "INSTAGRAM_ACCESS_TOKEN"
MEDIA_FIELDS = ",".join(
    [
        "id",
        "caption",
        "media_type",
        "media_product_type",
        "permalink",
        "shortcode",
        "timestamp",
        "username",
        "like_count",
        "comments_count",
        "is_comment_enabled",
        "media_url",
        "thumbnail_url",
        "owner",
        "children{id,media_type,media_url,permalink,timestamp,username}",
    ]
)
# Valid feed-post insight metrics. Pulled best-effort: any the token lacks
# permission for are recorded under "denied" rather than failing the export.
INSIGHT_METRICS = [
    "reach",
    "impressions",
    "saved",
    "likes",
    "comments",
    "shares",
    "total_interactions",
    "views",
    "profile_activity",
    "profile_visits",
    "follows",
    "navigation",
]
COMMENT_FIELDS = ",".join(
    [
        "id",
        "text",
        "timestamp",
        "username",
        "like_count",
        "replies{id,text,timestamp,username,like_count}",
    ]
)


def build_url(path: str, access_token: str, params: dict[str, Any] | None = None) -> str:
    query = dict(params or {})
    query["access_token"] = access_token
    return f"{GRAPH_BASE_URL}/{path.lstrip('/')}?{urlencode(query)}"


def fetch_collection(
    url: str,
    get_json: Callable[[str], dict[str, Any]] = fetch_json,
    max_items: int | None = None,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    next_url: str | None = url

    while next_url:
        response = get_json(next_url)
        items.extend(response.get("data", []))
        if max_items is not None and len(items) >= max_items:
            return items[:max_items]
        next_url = response.get("paging", {}).get("next")

    return items


def choose_carousel(
    media: list[dict[str, Any]],
    permalink: str | None = None,
) -> dict[str, Any]:
    for item in media:
        if item.get("media_type") != "CAROUSEL_ALBUM":
            continue
        if permalink and _normalize_permalink(item.get("permalink")) != _normalize_permalink(
            permalink
        ):
            continue
        return item

    if permalink:
        raise InstagramCheckError(f"No carousel post found for permalink: {permalink}")
    raise InstagramCheckError("No carousel posts found in the scanned Instagram media.")


def list_carousels(
    env: dict[str, str],
    get_json: Callable[[str], dict[str, Any]] = fetch_json,
    scan_limit: int = 50,
) -> list[dict[str, Any]]:
    access_token = _access_token(env)
    media = fetch_collection(
        build_url(
            "me/media",
            access_token,
            {"fields": MEDIA_FIELDS, "limit": min(scan_limit, 100)},
        ),
        get_json=get_json,
        max_items=scan_limit,
    )
    return [item for item in media if item.get("media_type") == "CAROUSEL_ALBUM"]


def fetch_media_insights(
    media_id: str,
    env: dict[str, str],
    get_json: Callable[[str], dict[str, Any]] = fetch_json,
    metrics: list[str] | None = None,
) -> dict[str, Any]:
    """Fetch every available insight metric for a media item.

    Metrics the token lacks permission for are listed under ``denied`` and other
    failures under ``errors`` so a missing scope never breaks the export.
    """

    access_token = _access_token(env)
    metric_list = metrics if metrics is not None else INSIGHT_METRICS
    available: dict[str, Any] = {}
    denied: list[str] = []
    errors: dict[str, str] = {}

    for metric in metric_list:
        response, failure = _fetch_metric(media_id, access_token, metric, get_json)
        if failure is not None:
            kind, message = failure
            if kind == "denied":
                denied.append(metric)
            else:
                errors[metric] = message
            continue
        data = response.get("data", [])
        available[metric] = _insight_value(data[0]) if data else None

    return {"available": available, "denied": denied, "errors": errors}


def pull_latest_carousel(
    env: dict[str, str],
    get_json: Callable[[str], dict[str, Any]] = fetch_json,
    media_id: str | None = None,
    permalink: str | None = None,
    scan_limit: int = 50,
    include_insights: bool = True,
) -> dict[str, Any]:
    access_token = _access_token(env)

    if media_id:
        post = get_json(
            build_url(
                media_id,
                access_token,
                {"fields": MEDIA_FIELDS},
            )
        )
        if post.get("media_type") != "CAROUSEL_ALBUM":
            raise InstagramCheckError(f"Media {media_id} is not a carousel album.")
    else:
        post = choose_carousel(
            list_carousels(env, get_json=get_json, scan_limit=scan_limit),
            permalink=permalink,
        )

    comments = fetch_collection(
        build_url(
            f"{post['id']}/comments",
            access_token,
            {"fields": COMMENT_FIELDS, "limit": 100},
        ),
        get_json=get_json,
    )
    children = post.get("children", {}).get("data", [])
    insights = (
        fetch_media_insights(post["id"], env, get_json=get_json)
        if include_insights
        else None
    )

    return {
        "schema_version": "1.1",
        "pulled_at": _utc_now_iso(),
        "account": {
            "user_id": env.get("INSTAGRAM_USER_ID"),
            "username": env.get("INSTAGRAM_USERNAME"),
        },
        "post": post,
        "child_count": len(children),
        "children": children,
        "post_comments_count": post.get("comments_count"),
        "comment_count": len(comments),
        "comments": comments,
        "insights": insights,
    }


def write_export(output_dir: str | Path, export: dict[str, Any]) -> Path:
    post = export["post"]
    folder_name = _shortcode_from_permalink(post.get("permalink")) or post["id"]
    post_dir = Path(output_dir) / folder_name
    post_dir.mkdir(parents=True, exist_ok=True)

    export_path = post_dir / "carousel_export.json"
    export_path.write_text(
        json.dumps(export, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (post_dir / "post.json").write_text(
        json.dumps(post, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (post_dir / "slides.json").write_text(
        json.dumps(export.get("children", []), indent=2, sort_keys=True, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    (post_dir / "comments.json").write_text(
        json.dumps(export.get("comments", []), indent=2, sort_keys=True, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    if export.get("insights") is not None:
        (post_dir / "insights.json").write_text(
            json.dumps(export["insights"], indent=2, sort_keys=True, ensure_ascii=False)
            + "\n",
            encoding="utf-8",
        )
    return export_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Pull token-safe data for the latest Instagram carousel post."
    )
    parser.add_argument("--env", default=".env.local", help="Env file path.")
    parser.add_argument(
        "--output-dir",
        default="data/instagram/carousel_posts",
        help="Directory for local JSON exports.",
    )
    parser.add_argument("--media-id", help="Pull one carousel by Instagram media ID.")
    parser.add_argument("--permalink", help="Pull one carousel by Instagram permalink.")
    parser.add_argument(
        "--scan-limit",
        type=int,
        default=50,
        help="How many recent media items to scan when no media ID is provided.",
    )
    parser.add_argument(
        "--list-carousels",
        action="store_true",
        help="List recent carousel post summaries instead of writing an export.",
    )
    args = parser.parse_args(argv)

    env = load_env_file(args.env)

    try:
        if args.list_carousels:
            carousels = list_carousels(env, scan_limit=args.scan_limit)
            print(json.dumps([_carousel_summary(item) for item in carousels], indent=2))
            return 0

        export = pull_latest_carousel(
            env,
            media_id=args.media_id,
            permalink=args.permalink,
            scan_limit=args.scan_limit,
        )
        export_path = write_export(args.output_dir, export)
    except InstagramCheckError as error:
        print(f"instagram pull failed: {error}", file=sys.stderr)
        return 2
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        print(f"instagram pull failed: HTTP {error.code}: {body}", file=sys.stderr)
        return 1
    except (URLError, TimeoutError, json.JSONDecodeError) as error:
        print(f"instagram pull failed: {error}", file=sys.stderr)
        return 1

    insights = export.get("insights") or {}
    print(
        json.dumps(
            {
                "status": "ok",
                "export_path": str(export_path),
                "post_id": export["post"]["id"],
                "permalink": export["post"].get("permalink"),
                "child_count": export["child_count"],
                "comment_count": export["comment_count"],
                "post_comments_count": export["post_comments_count"],
                "insights_available": sorted(insights.get("available", {})),
                "insights_denied": sorted(insights.get("denied", [])),
            },
            sort_keys=True,
        )
    )
    return 0


def _fetch_metric(
    media_id: str,
    access_token: str,
    metric: str,
    get_json: Callable[[str], dict[str, Any]],
) -> tuple[dict[str, Any] | None, tuple[str, str] | None]:
    """Fetch one metric. Returns (response, None) or (None, (kind, message))."""

    params_variants = [
        {"metric": metric},
        {"metric": metric, "metric_type": "total_value"},
    ]
    last_message: str | None = None
    for params in params_variants:
        url = build_url(f"{media_id}/insights", access_token, params)
        try:
            return get_json(url), None
        except HTTPError as error:
            body = error.read().decode("utf-8", errors="replace")
            message = _error_message(body) or f"HTTP {error.code}"
            last_message = message
            if "permission" in message.lower():
                return None, ("denied", message)
            if "metric_type" in body:
                continue  # retry requesting metric_type=total_value
            return None, ("error", message)
        except (URLError, TimeoutError, json.JSONDecodeError) as error:
            return None, ("error", str(error))
    return None, ("error", last_message or "unknown error")


def _insight_value(entry: dict[str, Any]) -> Any:
    total_value = entry.get("total_value")
    if isinstance(total_value, dict) and "value" in total_value:
        return total_value["value"]
    values = entry.get("values")
    if values:
        return values[0].get("value")
    return None


def _error_message(body: str) -> str | None:
    try:
        payload = json.loads(body)
    except (json.JSONDecodeError, TypeError):
        return None
    error = payload.get("error")
    if isinstance(error, dict):
        return error.get("message")
    return None


def _access_token(env: dict[str, str]) -> str:
    access_token = env.get(TOKEN_ENV_KEY)
    if not access_token:
        raise InstagramCheckError(
            f"Missing {TOKEN_ENV_KEY}. Save it in .env.local or export it first."
        )
    return access_token


def _carousel_summary(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item.get("id"),
        "permalink": item.get("permalink"),
        "timestamp": item.get("timestamp"),
        "like_count": item.get("like_count"),
        "comments_count": item.get("comments_count"),
        "child_count": len(item.get("children", {}).get("data", [])),
    }


def _shortcode_from_permalink(permalink: str | None) -> str | None:
    if not permalink:
        return None
    parts = [part for part in urlparse(permalink).path.split("/") if part]
    if len(parts) >= 2 and parts[0] in {"p", "reel", "tv"}:
        return parts[1]
    return None


def _normalize_permalink(permalink: str | None) -> str | None:
    if not permalink:
        return None
    parsed = urlparse(permalink)
    path = parsed.path.rstrip("/")
    return f"{parsed.netloc.lower()}{path}"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


if __name__ == "__main__":
    raise SystemExit(main())
