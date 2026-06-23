"""Export the Instagram corpus catalog into RAG-ready JSONL files."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


def export_rag(conn: sqlite3.Connection, output_dir: str | Path) -> dict[str, int]:
    """Write posts/assets/chunks/gaps JSONL exports from a SQLite catalog."""

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    posts = _post_records(conn)
    assets = _asset_records(conn, posts)
    comments = _comment_records(conn, posts)
    gaps = _gap_records(conn)
    chunks = _chunk_records(conn, posts)

    _write_jsonl(out / "posts.jsonl", posts)
    _write_jsonl(out / "assets.jsonl", assets)
    _write_jsonl(out / "comments.jsonl", comments)
    _write_jsonl(out / "chunks.jsonl", chunks)
    _write_jsonl(out / "gaps.jsonl", gaps)

    return {
        "posts": len(posts),
        "assets": len(assets),
        "chunks": len(chunks),
        "comments": len(comments),
        "gaps": len(gaps),
    }


def _post_records(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    gap_ids = _gap_ids_by_post(conn)
    metric_map = _metrics_by_post(conn)
    records: list[dict[str, Any]] = []
    for row in _rows(conn, "posts", ("post_id", "id")):
        post_id = _first(row, ("post_id", "id"))
        if not post_id:
            continue
        raw_ids = _raw_ids(row)
        metrics = metric_map.get(str(post_id), {})
        records.append(
            {
                "post_id": str(post_id),
                "shortcode": _first(row, ("shortcode", "code")),
                "source_url": _first(row, ("source_url", "permalink", "url")),
                "account_username": _first(row, ("account_username", "owner_username", "username")),
                "media_type": _first(row, ("media_type", "post_type", "type")),
                "rights_scope": _rights_scope(row),
                "caption_text": _first(row, ("caption_text", "caption", "text")),
                "metrics": metrics,
                "evidence_raw_object_ids": raw_ids,
                "gap_ids": sorted(gap_ids.get(str(post_id), [])),
            }
        )
    return records


def _asset_records(conn: sqlite3.Connection, posts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    post_map = {post["post_id"]: post for post in posts}
    gap_ids = _gap_ids_by_asset(conn)
    records: list[dict[str, Any]] = []
    for row in _rows(conn, "assets", ("post_id", "asset_index", "id", "asset_id")):
        asset_id = _first(row, ("asset_id", "id"))
        post_id = _first(row, ("post_id",))
        if not asset_id or not post_id:
            continue
        post = post_map.get(str(post_id), {})
        records.append(
            {
                "asset_id": str(asset_id),
                "post_id": str(post_id),
                "asset_index": _first(row, ("asset_index", "position", "index")),
                "source_url": _first(row, ("source_url", "remote_url", "url")),
                "media_type": _first(row, ("media_type", "asset_type", "type")),
                "media_sha256": _first(row, ("media_sha256", "sha256")),
                "rights_scope": _rights_scope(row, post.get("rights_scope")),
                "evidence_raw_object_ids": _raw_ids(row),
                "gap_ids": sorted(gap_ids.get(str(asset_id), [])),
            }
        )
    return records


def _gap_records(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for row in _rows(conn, "gaps", ("post_id", "asset_id", "missing_index", "gap_id", "id")):
        gap_id = _first(row, ("gap_id", "id"))
        if not gap_id:
            continue
        records.append(
            {
                "gap_id": str(gap_id),
                "post_id": _first(row, ("post_id",)),
                "asset_id": _first(row, ("asset_id",)),
                "field": _first(row, ("field", "gap_type", "kind")),
                "status": _first(row, ("status",)),
                "reason": _first(row, ("reason", "message")),
                "missing_index": _first(row, ("missing_index", "asset_index")),
            }
        )
    return records


def _chunk_records(conn: sqlite3.Connection, posts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    post_map = {post["post_id"]: post for post in posts}
    unavailable = _unavailable_fields_by_post(conn)
    records: list[dict[str, Any]] = []
    for row in _rows(conn, "rag_chunks", ("post_id", "asset_id", "chunk_id", "id")):
        chunk_id = _first(row, ("chunk_id", "id"))
        post_id = _first(row, ("post_id",))
        if not chunk_id or not post_id:
            continue
        post = post_map.get(str(post_id), {})
        records.append(
            {
                "chunk_id": str(chunk_id),
                "post_id": str(post_id),
                "asset_id": _first(row, ("asset_id",)),
                "source_url": _first(row, ("source_url", "url"), post.get("source_url")),
                "text": _first(row, ("text", "chunk_text", "content"), ""),
                "rights_scope": _rights_scope(row, post.get("rights_scope")),
                "evidence_raw_object_ids": _raw_ids(row),
                "gap_ids": _gap_ids(row),
                "metric_context": post.get("metrics", {}),
                "explicit_unavailable_fields": sorted(unavailable.get(str(post_id), set())),
            }
        )
    return records


def _comment_records(conn: sqlite3.Connection, posts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    post_map = {post["post_id"]: post for post in posts}
    records: list[dict[str, Any]] = []
    for row in _rows(conn, "comments", ("post_id", "comment_id", "id")):
        comment_id = _first(row, ("comment_id", "id"))
        post_id = _first(row, ("post_id",))
        if not comment_id or not post_id:
            continue
        post = post_map.get(str(post_id), {})
        records.append(
            {
                "comment_id": str(comment_id),
                "post_id": str(post_id),
                "source_url": post.get("source_url"),
                "author_username": _first(row, ("author_username", "username", "owner_username")),
                "text": _first(row, ("text", "comment_text", "body"), ""),
                "like_count": _first(row, ("like_count", "likes")),
                "rights_scope": _rights_scope(row, post.get("rights_scope")),
                "evidence_raw_object_ids": _raw_ids(row),
            }
        )
    return records


def _metrics_by_post(conn: sqlite3.Connection) -> dict[str, dict[str, Any]]:
    metrics: dict[str, dict[str, Any]] = {}
    for row in _rows(conn, "metric_observations", ("post_id", "metric_name", "id", "metric_id")):
        post_id = _first(row, ("post_id",))
        name = _first(row, ("metric_name", "name", "metric"))
        if not post_id or not name:
            continue
        metrics.setdefault(str(post_id), {})[str(name)] = _first(row, ("value", "metric_value"))
    return metrics


def _unavailable_fields_by_post(conn: sqlite3.Connection) -> dict[str, set[str]]:
    unavailable: dict[str, set[str]] = {}
    for row in _rows(conn, "gaps", ("post_id", "gap_id", "id")):
        post_id = _first(row, ("post_id",))
        field = _first(row, ("field", "gap_type", "kind"))
        if post_id and field:
            unavailable.setdefault(str(post_id), set()).add(str(field))
    for row in _rows(conn, "metric_observations", ("post_id", "metric_name", "id", "metric_id")):
        post_id = _first(row, ("post_id",))
        name = _first(row, ("metric_name", "name", "metric"))
        value = _first(row, ("value", "metric_value"))
        status = str(_first(row, ("status",), "")).lower()
        if post_id and name and (value is None or status in {"unavailable", "gap", "open"}):
            unavailable.setdefault(str(post_id), set()).add(str(name))
    return unavailable


def _gap_ids_by_post(conn: sqlite3.Connection) -> dict[str, set[str]]:
    gaps: dict[str, set[str]] = {}
    for row in _rows(conn, "gaps", ("post_id", "gap_id", "id")):
        post_id = _first(row, ("post_id",))
        gap_id = _first(row, ("gap_id", "id"))
        if post_id and gap_id:
            gaps.setdefault(str(post_id), set()).add(str(gap_id))
    return gaps


def _gap_ids_by_asset(conn: sqlite3.Connection) -> dict[str, set[str]]:
    gaps: dict[str, set[str]] = {}
    for row in _rows(conn, "gaps", ("asset_id", "gap_id", "id")):
        asset_id = _first(row, ("asset_id",))
        gap_id = _first(row, ("gap_id", "id"))
        if asset_id and gap_id:
            gaps.setdefault(str(asset_id), set()).add(str(gap_id))
    return gaps


def _raw_ids(row: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for name in ("evidence_raw_object_ids", "raw_object_ids", "evidence_json"):
        values.extend(_json_list(row.get(name)))
    singular = row.get("raw_object_id")
    if singular:
        values.append(str(singular))
    return _dedupe(values)


def _gap_ids(row: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for name in ("gap_ids", "explicit_gap_ids"):
        values.extend(_json_list(row.get(name)))
    singular = row.get("gap_id")
    if singular:
        values.append(str(singular))
    return _dedupe(values)


def _rights_scope(row: dict[str, Any], default: Any = None) -> str:
    value = _first(row, ("rights_scope",), default)
    return str(value or "third_party_analysis_only")


def _rows(conn: sqlite3.Connection, table: str, order_columns: tuple[str, ...]) -> list[dict[str, Any]]:
    columns = _columns(conn, table)
    if not columns:
        return []
    order = [column for column in order_columns if column in columns]
    sql = f"SELECT * FROM {table}"
    if order:
        sql += " ORDER BY " + ", ".join(order)
    cursor = conn.execute(sql)
    names = [description[0] for description in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]


def _columns(conn: sqlite3.Connection, table: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {str(row[1]) for row in rows}


def _first(row: dict[str, Any], names: tuple[str, ...], default: Any = None) -> Any:
    for name in names:
        value = row.get(name)
        if value is not None:
            return value
    return default


def _json_list(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item]
    if isinstance(value, tuple):
        return [str(item) for item in value if item]
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, list):
            return [str(item) for item in parsed if item]
        return [value]
    return [str(value)]


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=True, sort_keys=True) + "\n")
