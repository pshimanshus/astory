#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from PIL import Image
except ImportError:  # pragma: no cover - optional local-image enrichment
    Image = None  # type: ignore[assignment]


RAW_POSTS = Path("references/text-style/winner-bank/posts_merged.json")
OUTPUT_JSON = "research_bank.json"
OUTPUT_SUMMARY = "research_bank_summary.md"


def build_research_bank(
    repo_root: str | Path,
    source_path: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    raw_path = Path(source_path) if source_path else root / RAW_POSTS
    posts = _read_json(raw_path)
    if not isinstance(posts, list):
        raise ValueError(f"Expected a list of posts in {raw_path}")

    first_party = _load_first_party_exports(root)
    local_assets = _local_slide_assets(root)
    records = [
        _normalize_post(post, root, first_party, local_assets)
        for post in posts
    ]

    return {
        "schema_version": "1.0",
        "source_paths": [_rel(root, raw_path)],
        "summary": _summary(records),
        "records": records,
    }


def write_research_bank(
    repo_root: str | Path,
    output_dir: str | Path,
    source_path: str | Path | None = None,
) -> dict[str, str]:
    root = Path(repo_root)
    out_dir = Path(output_dir)
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    bank = build_research_bank(root, source_path=source_path)
    json_path = out_dir / OUTPUT_JSON
    summary_path = out_dir / OUTPUT_SUMMARY
    json_path.write_text(
        json.dumps(bank, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    summary_path.write_text(_render_summary(bank), encoding="utf-8")
    return {
        "json": _rel(root, json_path),
        "summary_markdown": _rel(root, summary_path),
    }


def _normalize_post(
    post: dict[str, Any],
    root: Path,
    first_party: dict[str, dict[str, Any]],
    local_assets: dict[str, dict[int, str]],
) -> dict[str, Any]:
    shortcode = str(post.get("shortCode") or "")
    account = str(post.get("ownerUsername") or "unknown")
    post_type = _post_type(post)
    export = first_party.get(shortcode)
    metrics, metric_gaps = _metrics(post, export)
    slides = _slides(post, root, export, local_assets.get(shortcode, {}), post_type)
    record_gaps = _record_gaps(post, export, slides, post_type)
    tags = list(post.get("mechanicTags") or [])

    return {
        "id": f"ig:{account}:{shortcode}",
        "source": {
            "account": account,
            "account_name": post.get("ownerFullName"),
            "shortcode": shortcode,
            "url": post.get("url"),
            "post_type": post_type,
            "raw_type": post.get("type"),
            "product_type": post.get("productType"),
            "timestamp": post.get("timestamp"),
        },
        "metrics": metrics,
        "metrics_gaps": metric_gaps,
        "post": {
            "caption": post.get("caption") or "",
            "caption_word_count": post.get("captionWords"),
            "hashtags": post.get("hashtags") or [],
            "first_comment": post.get("firstComment") or "",
            "latest_comments": post.get("latestComments") or [],
        },
        "communication": _communication(post.get("caption") or "", tags),
        "slides": slides,
        "record_gaps": record_gaps,
    }


def _metrics(
    post: dict[str, Any],
    export: dict[str, Any] | None,
) -> tuple[dict[str, Any], list[str]]:
    metrics = {
        "likes": post.get("likesCount"),
        "comments": post.get("commentsCount"),
        "views": post.get("videoViewCount") or None,
        "plays": post.get("videoPlayCount") or None,
        "winner_score": post.get("winnerScore"),
        "comment_to_like_ratio": post.get("commentToLikeRatio"),
        "metric_source": "public_scrape",
    }
    gaps: list[str] = []

    available = ((export or {}).get("insights") or {}).get("available") or {}
    if available:
        metrics.update(
            {
                "shares": available.get("shares"),
                "saves": available.get("saved"),
                "reach": available.get("reach"),
                "views": available.get("views", metrics["views"]),
                "follows": available.get("follows"),
                "total_interactions": available.get("total_interactions"),
                "metric_source": "first_party_graph_export",
            }
        )
    else:
        metrics.update(
            {
                "shares": None,
                "saves": None,
                "reach": None,
                "follows": None,
                "total_interactions": None,
            }
        )
        gaps.extend(
            [
                "shares_unavailable",
                "saves_unavailable",
                "reach_unavailable",
            ]
        )
    return metrics, gaps


def _slides(
    post: dict[str, Any],
    root: Path,
    export: dict[str, Any] | None,
    local_assets: dict[int, str],
    post_type: str,
) -> list[dict[str, Any]]:
    children = _export_children(export)
    child_count = len(children) or int(post.get("childCount") or 0)

    if post_type in {"static_image", "reel_video"}:
        return [
            _slide(
                1,
                post_type,
                post.get("displayUrl"),
                local_assets.get(0),
                root,
                "display_url_only" if post.get("displayUrl") else "asset_missing",
            )
        ]

    if child_count <= 0:
        child_count = 1

    slides: list[dict[str, Any]] = []
    for index in range(child_count):
        child = children[index] if index < len(children) else {}
        source_url = child.get("media_url")
        if not source_url and index == 0:
            source_url = post.get("displayUrl")
        if source_url:
            asset_status = (
                "local_asset_available"
                if index in local_assets
                else "display_url_only"
            )
        else:
            asset_status = "missing_child_url_in_source_scrape"
        slides.append(
            _slide(
                index + 1,
                child.get("media_type") or "IMAGE",
                source_url,
                local_assets.get(index),
                root,
                asset_status,
            )
        )
    return slides


def _slide(
    slide_number: int,
    media_type: str,
    source_url: str | None,
    local_asset: str | None,
    root: Path,
    asset_status: str,
) -> dict[str, Any]:
    visual = _visual(media_type, root / local_asset if local_asset else None, asset_status)
    return {
        "slide_number": slide_number,
        "media_type": media_type,
        "source_media_url": source_url,
        "local_asset_path": local_asset,
        "asset_status": asset_status,
        "text": {
            "text": None,
            "status": "ocr_not_available",
            "source": None,
        },
        "visual": visual,
    }


def _visual(media_type: str, local_asset: Path | None, asset_status: str) -> dict[str, Any]:
    if str(media_type).upper() == "VIDEO" or media_type == "reel_video":
        return {
            "classification": "reel_video",
            "notes": "Video/reel visual analysis requires video asset extraction.",
        }
    if not local_asset:
        return {
            "classification": "unknown_pending_asset_download",
            "notes": asset_status,
        }
    return _classify_local_image(local_asset)


def _classify_local_image(path: Path) -> dict[str, Any]:
    if Image is None:
        return {
            "classification": "local_asset_unclassified",
            "notes": "PIL is not installed.",
        }
    try:
        with Image.open(path) as image:
            rgb = image.convert("RGB").resize((32, 32))
            pixels = list(rgb.getdata())
    except OSError:
        return {
            "classification": "local_asset_unreadable",
            "notes": "Local asset exists but could not be opened.",
        }

    total = len(pixels)
    white = sum(1 for r, g, b in pixels if r > 240 and g > 240 and b > 240)
    avg_range = sum(max(px) - min(px) for px in pixels) / total
    white_ratio = white / total
    if white_ratio > 0.85 and avg_range < 12:
        classification = "likely_text_only_minimal_visuals"
    elif avg_range > 35:
        classification = "image_or_illustration"
    else:
        classification = "graphic_or_text_slide"
    return {
        "classification": classification,
        "white_background_ratio": round(white_ratio, 3),
        "average_channel_range": round(avg_range, 2),
    }


def _communication(caption: str, tags: list[str]) -> dict[str, Any]:
    lower = caption.lower()
    if "send this" in lower or "share this" in lower:
        prompt_type = "send_or_share_prompt"
    elif "leave a" in lower or "drop a" in lower or "comment" in lower:
        prompt_type = "comment_or_affirm_prompt"
    else:
        prompt_type = "caption_statement"

    if "first_person" in tags:
        voice = "first_person"
    elif "direct_you" in tags:
        voice = "direct_address"
    else:
        voice = "caption_voice"

    first_line = next((line.strip() for line in caption.splitlines() if line.strip()), "")
    return {
        "mechanic_tags": tags,
        "prompt_type": prompt_type,
        "voice": voice,
        "hook": first_line[:240],
        "communication_notes": _communication_notes(tags, prompt_type),
    }


def _communication_notes(tags: list[str], prompt_type: str) -> str:
    notes = []
    if "domestic" in tags:
        notes.append("domestic/lived-life frame")
    if "message_native" in tags:
        notes.append("message-native delivery")
    if "heartbreak" in tags:
        notes.append("emotional recovery or ache")
    if "reel" in tags:
        notes.append("reel-native")
    notes.append(prompt_type.replace("_", " "))
    return "; ".join(notes)


def _record_gaps(
    post: dict[str, Any],
    export: dict[str, Any] | None,
    slides: list[dict[str, Any]],
    post_type: str,
) -> list[str]:
    gaps = []
    if export is None:
        gaps.append("first_party_insights_unavailable_for_source")
    if any(slide["asset_status"] == "missing_child_url_in_source_scrape" for slide in slides):
        gaps.append("child_slide_urls_missing_from_current_scrape")
    if any(slide["text"]["status"] == "ocr_not_available" for slide in slides):
        gaps.append("slide_text_ocr_not_available")
    if post_type == "reel_video":
        gaps.append("video_transcript_not_available")
    return gaps


def _summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    format_counts = Counter(record["source"]["post_type"] for record in records)
    account_counts = Counter(record["source"]["account"] for record in records)
    gap_counts: Counter[str] = Counter()
    for record in records:
        gap_counts.update(record["record_gaps"])
        gap_counts.update(record["metrics_gaps"])
    return {
        "total_records": len(records),
        "format_counts": dict(sorted(format_counts.items())),
        "account_counts": dict(sorted(account_counts.items())),
        "gap_counts": dict(sorted(gap_counts.items())),
        "records_with_first_party_metrics": sum(
            1
            for record in records
            if record["metrics"]["metric_source"] == "first_party_graph_export"
        ),
        "local_slide_assets": sum(
            1
            for record in records
            for slide in record["slides"]
            if slide["local_asset_path"]
        ),
        "slide_slots": sum(len(record["slides"]) for record in records),
    }


def _render_summary(bank: dict[str, Any]) -> str:
    summary = bank["summary"]
    records = sorted(
        bank["records"],
        key=lambda record: record["metrics"].get("winner_score") or 0,
        reverse=True,
    )
    lines = [
        "# Research Bank Summary",
        "",
        f"Total records: {summary['total_records']}",
        f"Total slide slots: {summary['slide_slots']}",
        f"Local slide assets linked: {summary['local_slide_assets']}",
        f"Records with first-party metrics: {summary['records_with_first_party_metrics']}",
        "",
        "## Format counts",
        "",
    ]
    for key, value in summary["format_counts"].items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Extraction gaps", ""])
    for key, value in summary["gap_counts"].items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(
        [
            "",
            "Third-party saves, shares, and reach are unavailable unless a scrape/API source provides them.",
            "Most third-party carousel child slide URLs are absent from the current raw scrape, so those slides are represented as explicit placeholders.",
            "OCR is not available in the local environment; slide text remains `ocr_not_available` until a richer asset/OCR pass runs.",
            "",
            "## Top posts",
            "",
            "| Rank | ID | Account | Type | Likes | Comments | Views | Plays | Winner Score | Gaps |",
            "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for rank, record in enumerate(records[:50], start=1):
        metrics = record["metrics"]
        gaps = ", ".join(record["record_gaps"][:3])
        lines.append(
            "| {rank} | `{id}` | {account} | {post_type} | {likes} | {comments} | {views} | {plays} | {score} | {gaps} |".format(
                rank=rank,
                id=record["id"],
                account=record["source"]["account"],
                post_type=record["source"]["post_type"],
                likes=metrics.get("likes") or "",
                comments=metrics.get("comments") or "",
                views=metrics.get("views") or "",
                plays=metrics.get("plays") or "",
                score=metrics.get("winner_score") or "",
                gaps=gaps,
            )
        )
    lines.append("")
    return "\n".join(lines)


def _post_type(post: dict[str, Any]) -> str:
    raw_type = str(post.get("type") or "").lower()
    tags = set(post.get("mechanicTags") or [])
    if raw_type == "video" or "reel" in tags:
        return "reel_video"
    if raw_type == "sidecar":
        return "carousel"
    return "static_image"


def _load_first_party_exports(root: Path) -> dict[str, dict[str, Any]]:
    exports: dict[str, dict[str, Any]] = {}
    base = root / "data/instagram/carousel_posts"
    if not base.exists():
        return exports
    for path in sorted(base.glob("*/carousel_export.json")):
        try:
            payload = _read_json(path)
        except (OSError, json.JSONDecodeError):
            continue
        shortcode = path.parent.name
        post_shortcode = ((payload.get("post") or {}).get("shortcode"))
        exports[str(post_shortcode or shortcode)] = payload
    return exports


def _local_slide_assets(root: Path) -> dict[str, dict[int, str]]:
    assets: dict[str, dict[int, str]] = {}
    base = root / ".carousel_research"
    if not base.exists():
        return assets
    pattern = re.compile(r"(?P<shortcode>.+)_(?P<index>\d+)\.(?:jpg|jpeg|png|webp)$", re.I)
    for path in sorted(base.iterdir()):
        if not path.is_file():
            continue
        match = pattern.match(path.name)
        if not match:
            continue
        shortcode = match.group("shortcode")
        index = int(match.group("index"))
        assets.setdefault(shortcode, {})[index] = _rel(root, path)
    return assets


def _export_children(export: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not export:
        return []
    children = export.get("children")
    if isinstance(children, list):
        return children
    post_children = ((export.get("post") or {}).get("children") or {}).get("data")
    if isinstance(post_children, list):
        return post_children
    return []


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build normalized A Story research bank.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--source",
        default=None,
        help="Optional raw posts JSON. Defaults to references/text-style/winner-bank/posts_merged.json.",
    )
    parser.add_argument(
        "--output-dir",
        default="references/text-style/research-bank",
    )
    args = parser.parse_args(argv)
    artifacts = write_research_bank(args.repo_root, args.output_dir, args.source)
    print(json.dumps({"status": "ok", "artifacts": artifacts}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
