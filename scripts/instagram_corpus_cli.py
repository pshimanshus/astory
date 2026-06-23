#!/usr/bin/env python3
"""CLI shell for the Instagram Evidence Bank V2 corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.instagram_corpus.export_rag import export_rag
from scripts.instagram_corpus.ids import post_id_from_shortcode
from scripts.instagram_corpus.media import download_media_assets
from scripts.instagram_corpus.ocr import run_ocr_for_media_files
from scripts.instagram_corpus.raw_store import write_raw_object
from scripts.instagram_corpus.validate import validate_catalog
from scripts.instagram_corpus.providers.apify import ApifyProvider
from scripts.instagram_corpus.providers.brightdata import BrightDataProvider
from scripts.instagram_corpus.providers.manual_json import ManualJsonProvider


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS raw_objects (
    raw_object_id TEXT PRIMARY KEY,
    provider TEXT,
    run_id TEXT,
    object_type TEXT,
    source_url TEXT,
    local_path TEXT,
    sha256 TEXT,
    captured_at TEXT
);
CREATE TABLE IF NOT EXISTS posts (
    post_id TEXT PRIMARY KEY,
    shortcode TEXT,
    source_url TEXT,
    account_username TEXT,
    media_type TEXT,
    rights_scope TEXT,
    raw_object_id TEXT,
    caption_text TEXT,
    expected_child_count INTEGER
);
CREATE TABLE IF NOT EXISTS assets (
    asset_id TEXT PRIMARY KEY,
    post_id TEXT,
    asset_index INTEGER,
    source_url TEXT,
    media_type TEXT,
    media_sha256 TEXT,
    rights_scope TEXT,
    raw_object_id TEXT
);
CREATE TABLE IF NOT EXISTS metric_observations (
    metric_id TEXT PRIMARY KEY,
    post_id TEXT,
    metric_name TEXT,
    value INTEGER,
    raw_object_id TEXT,
    provider TEXT
);
CREATE TABLE IF NOT EXISTS rag_chunks (
    chunk_id TEXT PRIMARY KEY,
    post_id TEXT,
    asset_id TEXT,
    source_url TEXT,
    text TEXT,
    rights_scope TEXT,
    raw_object_ids TEXT,
    gap_ids TEXT
);
CREATE TABLE IF NOT EXISTS gaps (
    gap_id TEXT PRIMARY KEY,
    post_id TEXT,
    asset_id TEXT,
    field TEXT,
    status TEXT,
    reason TEXT,
    missing_index INTEGER
);
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Instagram Evidence Bank V2 corpus CLI.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Initialize the SQLite catalog.")
    p_init.add_argument("--db", required=True)

    p_import = sub.add_parser("import-seed", help="Import seed winner-bank JSON into the catalog.")
    p_import.add_argument("--db", required=True)
    p_import.add_argument("--seed", required=True)
    p_import.add_argument("--run-id", required=True)

    p_export = sub.add_parser("export-rag", help="Export RAG-ready JSONL files.")
    p_export.add_argument("--db", required=True)
    p_export.add_argument("--out", required=True)

    p_validate = sub.add_parser("validate", help="Validate catalog provenance and coverage.")
    p_validate.add_argument("--db", required=True)
    p_validate.add_argument("--root", required=True)

    for name in ("ingest-url", "download-media", "run-ocr"):
        p_shell = sub.add_parser(name, help=f"{name} command shell; no provider requests are made.")
        p_shell.add_argument("--db", required=True)
        p_shell.add_argument("--root", required=True)
        p_shell.add_argument("--run-id", required=True)
        if name == "ingest-url":
            p_shell.add_argument("--provider", required=True)
            p_shell.add_argument("--url", required=True)
            p_shell.add_argument("--input-json")

    args = parser.parse_args(argv)
    if args.command == "init":
        return _cmd_init(args)
    if args.command == "import-seed":
        return _cmd_import_seed(args)
    if args.command == "export-rag":
        return _cmd_export_rag(args)
    if args.command == "validate":
        return _cmd_validate(args)
    if args.command == "ingest-url":
        return _cmd_ingest_url(args)
    if args.command == "download-media":
        return _cmd_download_media(args)
    if args.command == "run-ocr":
        return _cmd_run_ocr(args)
    if args.command in {"download-media", "run-ocr"}:
        return _cmd_shell(args)
    parser.error(f"unknown command {args.command}")
    return 2


def _cmd_init(args: argparse.Namespace) -> int:
    conn = _connect(args.db)
    try:
        _initialize(conn)
    finally:
        conn.close()
    _print({"status": "initialized", "db": str(args.db)})
    return 0


def _cmd_import_seed(args: argparse.Namespace) -> int:
    conn = _connect(args.db)
    try:
        _initialize(conn)
        result = _external_seed_import(conn, Path(args.seed), args.run_id)
        if result is None:
            result = {"posts": _import_seed(conn, Path(args.seed), args.run_id)}
    finally:
        conn.close()
    _print({"status": "imported", "result": result, "run_id": args.run_id})
    return 0


def _cmd_export_rag(args: argparse.Namespace) -> int:
    conn = _connect(args.db)
    try:
        counts = export_rag(conn, Path(args.out))
    finally:
        conn.close()
    _print({"status": "exported", "counts": counts, "out": str(args.out)})
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    conn = _connect(args.db)
    try:
        findings = validate_catalog(conn, Path(args.root))
    finally:
        conn.close()
    _print({"status": "validated", "findings": findings, "count": len(findings)})
    return 1 if findings else 0


def _cmd_ingest_url(args: argparse.Namespace) -> int:
    provider_name = args.provider.lower().replace("_", "-")
    conn = _connect(args.db)
    try:
        _initialize(conn)
        if args.input_json:
            provider = ManualJsonProvider(args.input_json)
            payload = Path(args.input_json).read_bytes()
        elif provider_name in {"brightdata", "bright-data"}:
            token = os.environ.get("BRIGHTDATA_TOKEN") or os.environ.get("BRIGHT_DATA_TOKEN")
            if not token:
                _print({"status": "missing_token", "provider": "brightdata", "env": "BRIGHTDATA_TOKEN"})
                return 2
            provider = BrightDataProvider(token)
            payload = None
        elif provider_name == "apify":
            token = os.environ.get("APIFY_TOKEN") or os.environ.get("APIFY_API_TOKEN")
            if not token:
                _print({"status": "missing_token", "provider": "apify", "env": "APIFY_TOKEN"})
                return 2
            provider = ApifyProvider(token)
            payload = None
        else:
            _print({"status": "unsupported_provider", "provider": args.provider})
            return 2
        post = provider.fetch_post_by_url(args.url)
        if payload is None:
            payload = json.dumps(post.raw.get("payload", {}), sort_keys=True).encode("utf-8")
        raw = write_raw_object(
            Path(args.root),
            args.provider,
            args.run_id,
            "post",
            args.url,
            payload,
            request_url=args.url,
            metadata={"input_json": str(args.input_json), "provider": args.provider},
        )
        _insert_provider_post(conn, post, raw, args.run_id)
    finally:
        conn.close()
    _print(
        {
            "status": "ingested",
            "run_id": args.run_id,
            "provider": args.provider,
            "post": {
                "shortcode": post.shortcode,
                "source_url": post.source_url,
                "children": len(post.children),
            },
            "raw_object_id": raw["raw_object_id"],
            "network_calls": 0,
        }
    )
    return 0


def _cmd_download_media(args: argparse.Namespace) -> int:
    conn = _connect(args.db)
    try:
        _initialize(conn)
        counts = download_media_assets(conn, Path(args.root), args.run_id)
    finally:
        conn.close()
    _print({"status": "downloaded", "run_id": args.run_id, "counts": counts})
    return 1 if counts.get("failed") else 0


def _cmd_run_ocr(args: argparse.Namespace) -> int:
    conn = _connect(args.db)
    try:
        _initialize(conn)
        try:
            counts = run_ocr_for_media_files(conn)
        except RuntimeError as exc:
            _print({"status": "ocr_unavailable", "error": str(exc), "run_id": args.run_id})
            return 2
    finally:
        conn.close()
    _print({"status": "ocr_complete", "run_id": args.run_id, "counts": counts})
    return 1 if counts.get("failed") else 0


def _cmd_shell(args: argparse.Namespace) -> int:
    _print(
        {
            "status": "not_implemented",
            "command": args.command,
            "run_id": args.run_id,
            "network_calls": 0,
        }
    )
    return 2


def _insert_provider_post(conn: sqlite3.Connection, provider_post, raw: dict[str, Any], run_id: str) -> None:
    now = _now()
    raw_object_id = raw["raw_object_id"]
    post_id = post_id_from_shortcode(provider_post.shortcode)
    source_url = provider_post.source_url or f"https://www.instagram.com/p/{provider_post.shortcode}/"
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
            raw["provider"],
            raw["run_id"],
            raw["object_type"],
            raw["source_url"],
            raw.get("request_url"),
            raw.get("response_status"),
            raw["local_path"],
            raw.get("metadata_path"),
            raw["sha256"],
            raw["captured_at"],
            json.dumps(raw.get("metadata", {}), sort_keys=True),
        ),
    )
    conn.execute(
        """
        INSERT OR REPLACE INTO posts(
            post_id, shortcode, permalink, account_id, media_type, product_type,
            posted_at, caption, raw_object_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            post_id,
            provider_post.shortcode,
            source_url,
            None,
            provider_post.content_type,
            None,
            None,
            provider_post.caption,
            raw_object_id,
        ),
    )
    conn.execute(
        """
        INSERT OR REPLACE INTO post_snapshots(
            snapshot_id, post_id, run_id, raw_object_id, captured_at, caption,
            media_type, child_count, like_count, comment_count, view_count,
            play_count, source_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            f"{post_id}_snapshot_{run_id}",
            post_id,
            run_id,
            raw_object_id,
            now,
            provider_post.caption,
            provider_post.content_type,
            len(provider_post.children),
            provider_post.metrics.get("likes"),
            provider_post.metrics.get("comments"),
            provider_post.metrics.get("views"),
            provider_post.metrics.get("plays"),
            json.dumps(provider_post.raw, sort_keys=True),
        ),
    )
    for child in provider_post.children:
        conn.execute(
            """
            INSERT OR REPLACE INTO assets(
                asset_id, post_id, asset_index, media_type, source_url, display_url,
                media_file_id, status, metadata_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"{post_id}_asset_{child.index:02d}",
                post_id,
                child.index,
                child.type,
                child.url,
                child.url,
                None,
                "provider_child_url",
                json.dumps(child.raw, sort_keys=True),
            ),
        )
    for name, value in provider_post.metrics.items():
        if value is None:
            continue
        conn.execute(
            """
            INSERT INTO metric_observations(
                post_id, metric_name, metric_value, status, source, run_id,
                raw_object_id, observed_at, metadata_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                post_id,
                name,
                value,
                "available",
                "manual_json_provider",
                run_id,
                raw_object_id,
                now,
                "{}",
            ),
        )
    for gap_type in ("saves", "shares", "ocr", "visual_notes"):
        conn.execute(
            """
            INSERT OR REPLACE INTO gaps(
                gap_id, post_id, asset_id, gap_type, status, reason, source,
                created_at, metadata_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"{post_id}_gap_{gap_type}",
                post_id,
                None,
                gap_type,
                "open",
                f"{gap_type} not present in manual JSON provider payload.",
                "manual_json_provider",
                now,
                "{}",
            ),
        )
    if provider_post.caption:
        conn.execute(
            """
            INSERT OR REPLACE INTO rag_chunks(
                chunk_id, post_id, asset_id, chunk_type, source_url, text,
                rights_scope, raw_object_ids, gap_ids, evidence_json, created_at,
                metadata_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"{post_id}_caption_{run_id}",
                post_id,
                None,
                "caption",
                source_url,
                provider_post.caption,
                "third_party_analysis_only",
                json.dumps([raw_object_id]),
                json.dumps([]),
                json.dumps([raw_object_id]),
                now,
                "{}",
            ),
        )
    conn.commit()


def _connect(db_path: str | Path) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _initialize(conn: sqlite3.Connection) -> None:
    external = _external_initializer()
    if external is not None:
        external(conn)
    conn.executescript(SCHEMA_SQL)
    conn.commit()


def _external_initializer() -> Any:
    try:
        from scripts.instagram_corpus import db as corpus_db
    except ImportError:
        return None
    initializer = getattr(corpus_db, "initialize", None)
    return initializer if callable(initializer) else None


def _external_seed_import(conn: sqlite3.Connection, seed_path: Path, run_id: str) -> Any:
    try:
        from scripts.instagram_corpus import seed_import
    except ImportError:
        return None
    importer = getattr(seed_import, "import_winner_seed", None)
    if not callable(importer):
        return None
    return importer(conn, seed_path, run_id)


def _import_seed(conn: sqlite3.Connection, seed_path: Path, run_id: str) -> int:
    data = json.loads(seed_path.read_text(encoding="utf-8"))
    posts = _seed_posts(data)
    now = _now()
    for post in posts:
        shortcode = _shortcode(post)
        if not shortcode:
            continue
        post_id = f"ig_{shortcode}"
        source_url = str(post.get("url") or f"https://www.instagram.com/p/{shortcode}/")
        raw_object_id = f"seed_{run_id}_{shortcode}"
        payload = json.dumps(post, ensure_ascii=True, sort_keys=True).encode("utf-8")
        sha256 = hashlib.sha256(payload).hexdigest()
        media_type = _media_type(post)
        expected_children = _expected_child_count(post)
        rights_scope = "third_party_analysis_only"

        conn.execute(
            """
            INSERT OR REPLACE INTO raw_objects (
                raw_object_id, provider, run_id, object_type, source_url, local_path, sha256, captured_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (raw_object_id, "seed", run_id, "post", source_url, str(seed_path), sha256, now),
        )
        conn.execute(
            """
            INSERT OR REPLACE INTO posts (
                post_id, shortcode, source_url, account_username, media_type,
                rights_scope, raw_object_id, caption_text, expected_child_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                post_id,
                shortcode,
                source_url,
                post.get("ownerUsername") or post.get("account_username"),
                media_type,
                rights_scope,
                raw_object_id,
                post.get("caption") or "",
                expected_children,
            ),
        )
        _insert_seed_asset(conn, post, post_id, raw_object_id, rights_scope)
        _insert_seed_metrics(conn, post, post_id, raw_object_id)
        _insert_seed_gaps(conn, post_id, expected_children, bool(post.get("displayUrl")))
        _insert_seed_chunk(conn, post, post_id, source_url, raw_object_id, rights_scope)
    conn.commit()
    return len(posts)


def _seed_posts(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [post for post in data if isinstance(post, dict)]
    if isinstance(data, dict):
        for key in ("posts", "items", "records"):
            value = data.get(key)
            if isinstance(value, list):
                return [post for post in value if isinstance(post, dict)]
    raise ValueError("seed JSON must be a list or an object with posts/items/records")


def _insert_seed_asset(
    conn: sqlite3.Connection,
    post: dict[str, Any],
    post_id: str,
    raw_object_id: str,
    rights_scope: str,
) -> None:
    display_url = post.get("displayUrl") or post.get("display_url")
    if not display_url:
        return
    conn.execute(
        """
        INSERT OR REPLACE INTO assets (
            asset_id, post_id, asset_index, source_url, media_type, media_sha256, rights_scope, raw_object_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            f"{post_id}_asset_0",
            post_id,
            0,
            str(display_url),
            _asset_media_type(post),
            None,
            rights_scope,
            raw_object_id,
        ),
    )


def _insert_seed_metrics(
    conn: sqlite3.Connection,
    post: dict[str, Any],
    post_id: str,
    raw_object_id: str,
) -> None:
    metrics = {
        "likes": post.get("likesCount"),
        "comments": post.get("commentsCount"),
        "views": post.get("videoViewCount"),
        "plays": post.get("videoPlayCount"),
    }
    for name, value in metrics.items():
        if value is None:
            continue
        conn.execute(
            """
            INSERT OR REPLACE INTO metric_observations (
                metric_id, post_id, metric_name, value, raw_object_id, provider
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (f"{post_id}_{name}", post_id, name, int(value), raw_object_id, "seed"),
        )


def _insert_seed_gaps(
    conn: sqlite3.Connection,
    post_id: str,
    expected_children: int,
    has_first_asset: bool,
) -> None:
    first_missing = 0 if not has_first_asset else 1
    for index in range(first_missing, expected_children):
        conn.execute(
            """
            INSERT OR REPLACE INTO gaps (
                gap_id, post_id, asset_id, field, status, reason, missing_index
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"{post_id}_gap_child_{index}",
                post_id,
                f"{post_id}_asset_{index}",
                "carousel_child_media",
                "unavailable",
                "seed import did not include this child media URL",
                index,
            ),
        )


def _insert_seed_chunk(
    conn: sqlite3.Connection,
    post: dict[str, Any],
    post_id: str,
    source_url: str,
    raw_object_id: str,
    rights_scope: str,
) -> None:
    caption = post.get("caption")
    if not caption:
        return
    conn.execute(
        """
        INSERT OR REPLACE INTO rag_chunks (
            chunk_id, post_id, asset_id, source_url, text, rights_scope, raw_object_ids, gap_ids
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            f"{post_id}_caption",
            post_id,
            None,
            source_url,
            str(caption),
            rights_scope,
            json.dumps([raw_object_id]),
            json.dumps([]),
        ),
    )


def _shortcode(post: dict[str, Any]) -> str:
    value = post.get("shortCode") or post.get("shortcode")
    if value:
        return str(value)
    url = str(post.get("url") or "")
    parts = [part for part in url.split("/") if part]
    for marker in ("p", "reel", "tv"):
        if marker in parts:
            index = parts.index(marker)
            if index + 1 < len(parts):
                return parts[index + 1].split("?")[0]
    return ""


def _media_type(post: dict[str, Any]) -> str:
    kind = str(post.get("type") or post.get("media_type") or "").lower()
    product = str(post.get("productType") or "").lower()
    child_count = _expected_child_count(post)
    if "sidecar" in kind or "carousel" in kind or child_count > 1:
        return "carousel"
    if "video" in kind or "reel" in kind or product == "clips":
        return "reel"
    return "image"


def _asset_media_type(post: dict[str, Any]) -> str:
    kind = str(post.get("type") or "").lower()
    return "video" if "video" in kind else "image"


def _expected_child_count(post: dict[str, Any]) -> int:
    value = post.get("childCount") or post.get("child_count") or 1
    try:
        return max(1, int(value))
    except (TypeError, ValueError):
        return 1


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _print(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
