"""Outcome attribution: turn Instagram carousel exports into brain signal.

Likes are vanity; the flywheel ranks by send-behavior (shares per 1k reach)
and follow conversion. This module loads `carousel_export.json` files pulled
by `scripts/instagram_pull_carousel.py`, computes normalized outcome metrics,
and compiles a cited canonical brain page plus a derived JSON report.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

EXPORTS_DIR = "data/instagram/carousel_posts"
PAGE_PATH = "references/brain/pages/outcome-attribution.md"
REPORT_PATH = "references/brain/reports/outcome_attribution.json"

# Posts younger than this stay unranked: insights are still accruing.
MATURITY_WINDOW = timedelta(hours=72)

# Tier thresholds on shares per 1k reach, grounded in the 2026-05/06 cohort:
# winners clustered >= 20, flops <= 7, everything else is mid.
WINNER_SHARES_PER_1K = 20.0
FLOP_SHARES_PER_1K = 7.0


@dataclass(frozen=True)
class CarouselOutcome:
    shortcode: str
    media_id: str
    permalink: str
    timestamp: str
    export_path: str
    likes: int
    reach: int
    shares: int
    saves: int
    views: int
    follows: int
    comments: int
    shares_per_1k: float
    saves_per_1k: float
    follows_per_1k: float


def load_carousel_outcomes(repo_root: str | Path) -> list[CarouselOutcome]:
    root = Path(repo_root)
    exports_root = root / EXPORTS_DIR
    if not exports_root.is_dir():
        return []
    records: list[CarouselOutcome] = []
    for export_file in sorted(exports_root.glob("*/carousel_export.json")):
        payload = json.loads(export_file.read_text(encoding="utf-8"))
        post = payload.get("post") or {}
        available = (payload.get("insights") or {}).get("available") or {}
        permalink = post.get("permalink") or ""
        shortcode = export_file.parent.name
        reach = int(available.get("reach") or 0)
        shares = int(available.get("shares") or 0)
        saves = int(available.get("saved") or 0)
        follows = int(available.get("follows") or 0)
        records.append(
            CarouselOutcome(
                shortcode=shortcode,
                media_id=str(post.get("id") or ""),
                permalink=permalink,
                timestamp=str(post.get("timestamp") or ""),
                export_path=export_file.relative_to(root).as_posix(),
                likes=int(post.get("like_count") or available.get("likes") or 0),
                reach=reach,
                shares=shares,
                saves=saves,
                views=int(available.get("views") or 0),
                follows=follows,
                comments=int(
                    post.get("comments_count") or available.get("comments") or 0
                ),
                shares_per_1k=_per_1k(shares, reach),
                saves_per_1k=_per_1k(saves, reach),
                follows_per_1k=_per_1k(follows, reach),
            )
        )
    return records


def compute_outcome_report(
    records: list[CarouselOutcome],
    now: datetime | None = None,
) -> dict:
    now = now or datetime.now(timezone.utc)
    posts = []
    for record in sorted(records, key=lambda r: r.shares_per_1k, reverse=True):
        entry = asdict(record)
        entry["tier"] = _tier(record, now)
        posts.append(entry)
    ranking = [entry["shortcode"] for entry in posts if entry["tier"] != "immature"]
    return {
        "schema_version": 1,
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "metric": "shares_per_1k_reach",
        "maturity_window_hours": int(MATURITY_WINDOW.total_seconds() // 3600),
        "thresholds": {
            "winner_shares_per_1k": WINNER_SHARES_PER_1K,
            "flop_shares_per_1k": FLOP_SHARES_PER_1K,
        },
        "posts": posts,
        "ranking": ranking,
        "winners": [e["shortcode"] for e in posts if e["tier"] == "winner"],
        "flops": [e["shortcode"] for e in posts if e["tier"] == "flop"],
    }


def write_outcome_artifacts(repo_root: str | Path, report: dict) -> dict[str, str]:
    root = Path(repo_root)
    report_file = root / REPORT_PATH
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    page_file = root / PAGE_PATH
    page_file.parent.mkdir(parents=True, exist_ok=True)
    page_file.write_text(_render_page(report), encoding="utf-8")
    return {"page": PAGE_PATH, "report": REPORT_PATH}


def _per_1k(value: int, reach: int) -> float:
    if reach <= 0:
        return 0.0
    return round(value / reach * 1000, 2)


def _parse_timestamp(raw: str) -> datetime | None:
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S+0000"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None


def _tier(record: CarouselOutcome, now: datetime) -> str:
    posted_at = _parse_timestamp(record.timestamp)
    if posted_at is not None and now - posted_at < MATURITY_WINDOW:
        return "immature"
    if record.shares_per_1k >= WINNER_SHARES_PER_1K:
        return "winner"
    if record.shares_per_1k <= FLOP_SHARES_PER_1K:
        return "flop"
    return "mid"


def _render_page(report: dict) -> str:
    posts = report["posts"]
    winners = [e for e in posts if e["tier"] == "winner"]
    flops = [e for e in posts if e["tier"] == "flop"]
    truth_lines = [
        "- Carousel outcomes are ranked by shares per 1k reach and follow"
        " conversion, not likes; the metric pipeline lives in"
        " `scripts/astory_brain/outcomes.py` over exports from"
        " `scripts/instagram_pull_carousel.py`.",
    ]
    for entry in winners:
        truth_lines.append(
            f"- `{entry['export_path']}`: {entry['shortcode']} is a send-behavior"
            f" winner with {entry['shares_per_1k']} shares/1k reach,"
            f" {entry['saves_per_1k']} saves/1k, {entry['follows_per_1k']}"
            f" follows/1k (reach {entry['reach']}, likes {entry['likes']})."
        )
    for entry in flops:
        truth_lines.append(
            f"- `{entry['export_path']}`: {entry['shortcode']} is a flop with"
            f" {entry['shares_per_1k']} shares/1k reach despite"
            f" {entry['likes']} likes."
        )
    likes_vs_share = _likes_vs_share_divergence(posts)
    if likes_vs_share:
        truth_lines.append(likes_vs_share)

    timeline_lines = [
        f"- {entry['timestamp'][:10]} | `{entry['export_path']}` |"
        f" {entry['shortcode']} tier={entry['tier']}"
        f" shares/1k={entry['shares_per_1k']} reach={entry['reach']}"
        for entry in posts
    ]
    frontmatter = (
        "---\n"
        "type: outcome_attribution\n"
        "role: text\n"
        "mentions:\n"
        f"  - {EXPORTS_DIR}\n"
        "---\n"
    )
    return (
        frontmatter
        + "\n# Outcome Attribution\n\n# Current Truth\n\n"
        + "\n".join(truth_lines)
        + "\n\n---\n\n# Timeline / Evidence\n\n"
        + "\n".join(timeline_lines)
        + "\n"
    )


def _likes_vs_share_divergence(posts: list[dict]) -> str | None:
    mature = [e for e in posts if e["tier"] != "immature"]
    if len(mature) < 2:
        return None
    top_likes = max(mature, key=lambda e: e["likes"])
    top_share = max(mature, key=lambda e: e["shares_per_1k"])
    if top_likes["shortcode"] == top_share["shortcode"]:
        return None
    return (
        f"- Likes and shareability diverge: {top_likes['shortcode']} leads on"
        f" likes ({top_likes['likes']}) but {top_share['shortcode']} leads on"
        f" send behavior ({top_share['shares_per_1k']} shares/1k reach); rank"
        f" ideas by the latter. Evidence: `{top_share['export_path']}`."
    )
