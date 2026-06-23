from __future__ import annotations

import json
import re
import hashlib
from datetime import datetime, timezone
from pathlib import Path

from scripts.instagram_corpus.ids import normalize_shortcode, post_id_from_shortcode


GAP_TYPES = ("saves", "shares", "child_media_urls", "ocr", "visual_notes")


def import_winner_seed(conn, seed_path, run_id):
    seed = Path(seed_path)
    if not seed.is_absolute():
        seed = seed.resolve()
    records = _load_records(seed)
    now = _utc_now()
    raw_object_id = _insert_seed_raw_object(conn, seed, run_id, now)

    conn.execute(
        """
        INSERT OR IGNORE INTO ingest_runs(run_id, source, started_at, completed_at, metadata_json)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            run_id,
            seed.as_posix(),
            now,
            now,
            json.dumps({"importer": "winner_seed"}, sort_keys=True),
        ),
    )

    seen_accounts = set()
    seen_posts = set()
    snapshot_count = 0
    asset_count = 0
    metric_count = 0
    gap_count = 0
    chunk_count = 0

    for record in records:
        shortcode = _record_shortcode(record)
        post_id = post_id_from_shortcode(shortcode)
        account_id = _account_id(record)
        permalink = _record_url(record, shortcode)
        media_type = _text(record.get("type") or record.get("format") or "")
        product_type = _optional_text(record.get("productType") or record.get("product_type"))
        caption = _text(record.get("caption") or record.get("caption_preview_max_24_words") or "")
        child_count = _int(record.get("childCount", record.get("slide_count", 0)))

        _upsert_account(conn, account_id, record)
        seen_accounts.add(account_id)

        _upsert_post(
            conn,
            post_id=post_id,
            shortcode=shortcode,
            permalink=permalink,
            account_id=account_id,
            media_type=media_type,
            product_type=product_type,
            posted_at=_optional_text(record.get("timestamp")),
            caption=caption,
            raw_object_id=raw_object_id,
        )
        seen_posts.add(post_id)

        snapshot_id = _stable_id("snapshot", run_id, post_id)
        conn.execute(
            """
            INSERT OR REPLACE INTO post_snapshots(
                snapshot_id, post_id, run_id, captured_at, caption, media_type,
                child_count, like_count, comment_count, view_count, play_count,
                source_json, raw_object_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                snapshot_id,
                post_id,
                run_id,
                now,
                caption,
                media_type,
                child_count,
                _metric(record, "likes"),
                _metric(record, "comments"),
                _metric(record, "views"),
                _metric(record, "plays"),
                json.dumps(record, sort_keys=True, ensure_ascii=False),
                raw_object_id,
            ),
        )
        snapshot_count += 1

        asset_count += _insert_assets(conn, post_id, record, media_type, child_count)
        metric_count += _insert_metrics(conn, post_id, run_id, record, now, raw_object_id)
        gap_count += _insert_gaps(conn, post_id, run_id, now)
        chunk_count += _insert_caption_chunk(
            conn,
            post_id,
            run_id,
            _record_url(record, shortcode),
            caption,
            raw_object_id,
            now,
        )

    conn.commit()
    return {
        "run_id": run_id,
        "accounts": len(seen_accounts),
        "posts": len(seen_posts),
        "snapshots": snapshot_count,
        "raw_objects": 1,
        "assets": asset_count,
        "metric_observations": metric_count,
        "gaps": gap_count,
        "rag_chunks": chunk_count,
    }


def _insert_seed_raw_object(conn, seed_path: Path, run_id: str, captured_at: str) -> str:
    payload = seed_path.read_bytes()
    sha256 = hashlib.sha256(payload).hexdigest()
    raw_object_id = f"raw_seed_{_slug(run_id)}_seedfile_{sha256[:16]}"
    conn.execute(
        """
        INSERT OR REPLACE INTO raw_objects(
            raw_object_id, provider, run_id, object_type, source_url, request_url,
            response_status, local_path, metadata_path, sha256, captured_at,
            metadata_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            raw_object_id,
            "winner_seed",
            run_id,
            "seed_file",
            seed_path.as_posix(),
            seed_path.as_posix(),
            None,
            seed_path.as_posix(),
            None,
            sha256,
            captured_at,
            json.dumps({"source": "winner_seed_import"}, sort_keys=True),
        ),
    )
    return raw_object_id


def _load_records(seed_path):
    data = json.loads(Path(seed_path).read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("records", "posts", "winner_bank"):
            records = data.get(key)
            if isinstance(records, list):
                return records
    raise ValueError("winner seed must be a list of post records")


def _record_shortcode(record):
    value = record.get("shortCode") or record.get("shortcode")
    if not value:
        value = record.get("url") or record.get("source_url")
    return normalize_shortcode(_text(value))


def _record_url(record, shortcode):
    return _text(
        record.get("url")
        or record.get("source_url")
        or f"https://www.instagram.com/p/{shortcode}/"
    )


def _account_id(record):
    username = _text(record.get("ownerUsername") or record.get("source_account") or "unknown")
    return "acct_" + _slug(username.lower())


def _upsert_account(conn, account_id, record):
    username = _text(record.get("ownerUsername") or record.get("source_account") or "unknown")
    full_name = _optional_text(record.get("ownerFullName") or record.get("account_name"))
    profile_url = f"https://www.instagram.com/{username}/" if username != "unknown" else None
    conn.execute(
        """
        INSERT OR IGNORE INTO accounts(account_id, username, full_name, profile_url)
        VALUES (?, ?, ?, ?)
        """,
        (account_id, username, full_name, profile_url),
    )
    conn.execute(
        """
        UPDATE accounts
        SET username = ?, full_name = ?, profile_url = ?, updated_at = CURRENT_TIMESTAMP
        WHERE account_id = ?
        """,
        (username, full_name, profile_url, account_id),
    )


def _upsert_post(
    conn,
    post_id,
    shortcode,
    permalink,
    account_id,
    media_type,
    product_type,
    posted_at,
    caption,
    raw_object_id,
):
    conn.execute(
        """
        INSERT OR IGNORE INTO posts(
            post_id, shortcode, permalink, account_id, media_type,
            product_type, posted_at, caption, raw_object_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            post_id,
            shortcode,
            permalink,
            account_id,
            media_type,
            product_type,
            posted_at,
            caption,
            raw_object_id,
        ),
    )
    conn.execute(
        """
        UPDATE posts
        SET permalink = ?, account_id = ?, media_type = ?, product_type = ?,
            posted_at = ?, caption = ?, raw_object_id = ?, updated_at = CURRENT_TIMESTAMP
        WHERE post_id = ?
        """,
        (
            permalink,
            account_id,
            media_type,
            product_type,
            posted_at,
            caption,
            raw_object_id,
            post_id,
        ),
    )


def _insert_assets(conn, post_id, record, media_type, child_count):
    asset_total = child_count if child_count > 0 else 1
    child_types = record.get("childTypes") or []
    display_url = _optional_text(record.get("displayUrl") or record.get("display_url"))
    inserted = 0
    for index in range(asset_total):
        asset_id = f"{post_id}_asset_{index:02d}"
        child_type = child_types[index] if index < len(child_types) else media_type
        source_url = display_url if index == 0 else None
        conn.execute(
            """
            INSERT OR REPLACE INTO assets(
                asset_id, post_id, asset_index, media_type, source_url,
                display_url, status, metadata_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                asset_id,
                post_id,
                index,
                _optional_text(child_type),
                source_url,
                display_url if index == 0 else None,
                "display_url_only" if source_url else "missing_child_media_url",
                "{}",
            ),
        )
        inserted += 1
    return inserted


def _insert_metrics(conn, post_id, run_id, record, observed_at, raw_object_id):
    metrics = {
        "likes": _metric(record, "likes"),
        "comments": _metric(record, "comments"),
        "views": _metric(record, "views"),
        "plays": _metric(record, "plays"),
    }
    inserted = 0
    for name, value in metrics.items():
        if value is None:
            continue
        conn.execute(
            """
            INSERT INTO metric_observations(
                post_id, metric_name, metric_value, status, source, run_id, observed_at
                , raw_object_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                post_id,
                name,
                value,
                "available",
                "winner_seed_public_scrape",
                run_id,
                observed_at,
                raw_object_id,
            ),
        )
        inserted += 1
    return inserted


def _insert_caption_chunk(conn, post_id, run_id, source_url, caption, raw_object_id, created_at):
    if not caption:
        return 0
    conn.execute(
        """
        INSERT OR REPLACE INTO rag_chunks(
            chunk_id, post_id, asset_id, chunk_type, source_url, text, rights_scope,
            raw_object_ids, gap_ids, evidence_json, created_at, metadata_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            _stable_id("chunk", run_id, post_id, "caption"),
            post_id,
            None,
            "caption",
            source_url,
            caption,
            "third_party_analysis_only",
            json.dumps([raw_object_id]),
            json.dumps([]),
            json.dumps([raw_object_id]),
            created_at,
            "{}",
        ),
    )
    return 1


def _insert_gaps(conn, post_id, run_id, created_at):
    reasons = {
        "saves": "Third-party saves are unavailable in public winner-bank seed data.",
        "shares": "Third-party shares are unavailable in public winner-bank seed data.",
        "child_media_urls": "Winner-bank seed has only first-display media, not complete child media URLs.",
        "ocr": "OCR has not been run for this seed asset.",
        "visual_notes": "Human or model visual notes have not been added.",
    }
    inserted = 0
    for gap_type in GAP_TYPES:
        conn.execute(
            """
            INSERT OR REPLACE INTO gaps(
                gap_id, post_id, gap_type, status, reason, source, created_at, metadata_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                _stable_id("gap", run_id, post_id, gap_type),
                post_id,
                gap_type,
                "open",
                reasons[gap_type],
                "winner_seed_import",
                created_at,
                "{}",
            ),
        )
        inserted += 1
    return inserted


def _metric(record, metric_name):
    field_names = {
        "likes": ("likesCount", "likes"),
        "comments": ("commentsCount", "comments"),
        "views": ("videoViewCount", "views", "views_or_plays"),
        "plays": ("videoPlayCount", "plays"),
    }[metric_name]
    for field_name in field_names:
        if field_name in record and record[field_name] is not None:
            return _int(record[field_name])
    return None


def _stable_id(*parts):
    return "_".join(_slug(part) for part in parts)


def _slug(value):
    return re.sub(r"[^A-Za-z0-9_]+", "_", str(value)).strip("_") or "unknown"


def _text(value):
    return "" if value is None else str(value)


def _optional_text(value):
    if value is None:
        return None
    return str(value)


def _int(value):
    if value is None or value == "":
        return 0
    return int(value)


def _utc_now():
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )
