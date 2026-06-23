"""Validation gates for the Instagram corpus catalog."""

from __future__ import annotations

import json
import hashlib
import sqlite3
from pathlib import Path
from typing import Any


def validate_catalog(conn: sqlite3.Connection, corpus_root: str | Path) -> list[dict[str, str]]:
    """Return provenance and coverage findings for a SQLite corpus catalog."""

    root = Path(corpus_root)
    findings: list[dict[str, str]] = []
    findings.extend(_raw_sha_findings(conn, root))
    findings.extend(_raw_reference_findings(conn))
    findings.extend(_post_evidence_findings(conn))
    findings.extend(_metric_findings(conn))
    findings.extend(_chunk_findings(conn))
    findings.extend(_carousel_child_findings(conn))
    return findings


def _raw_reference_findings(conn: sqlite3.Connection) -> list[dict[str, str]]:
    known_raw_ids = {
        str(_first(row, ("raw_object_id", "id")))
        for row in _rows(conn, "raw_objects", ("raw_object_id", "id"))
        if _first(row, ("raw_object_id", "id"))
    }
    findings: list[dict[str, str]] = []
    checks = (
        ("posts", ("post_id", "id")),
        ("assets", ("asset_id", "id")),
        ("metric_observations", ("metric_id", "id", "observation_id")),
        ("comments", ("comment_id", "id")),
        ("rag_chunks", ("chunk_id", "id")),
    )
    for table, target_names in checks:
        for row in _rows(conn, table, target_names):
            target = str(_first(row, target_names, table))
            for raw_id in _raw_ids(row):
                if raw_id not in known_raw_ids:
                    findings.append(
                        _finding(
                            "raw",
                            "raw_evidence_missing",
                            "raw evidence ID does not resolve to a raw object",
                            f"{target}:{raw_id}",
                        )
                    )
    return findings


def _raw_sha_findings(conn: sqlite3.Connection, corpus_root: Path) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for row in _rows(conn, "raw_objects", ("raw_object_id", "id")):
        raw_id = _first(row, ("raw_object_id", "id"))
        sha = _first(row, ("sha256", "response_sha256", "payload_sha256"))
        if raw_id and not sha:
            findings.append(
                _finding(
                    "raw",
                    "raw_missing_sha256",
                    "raw object is missing a SHA-256 digest",
                    str(raw_id),
                )
            )
            continue
        local_path = _first(row, ("local_path", "path"))
        if raw_id and sha and local_path:
            path = Path(str(local_path))
            if not path.is_absolute():
                path = corpus_root / path
            if not path.exists():
                findings.append(
                    _finding(
                        "raw",
                        "raw_file_missing",
                        "raw object local file is missing",
                        str(raw_id),
                    )
                )
                continue
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            if actual != str(sha):
                findings.append(
                    _finding(
                        "raw",
                        "raw_sha256_mismatch",
                        "raw object SHA-256 does not match local file bytes",
                        str(raw_id),
                    )
                )
    return findings


def _post_evidence_findings(conn: sqlite3.Connection) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for row in _rows(conn, "posts", ("post_id", "id")):
        post_id = _first(row, ("post_id", "id"))
        if not post_id:
            continue
        if not _raw_ids(row):
            findings.append(
                _finding(
                    "provenance",
                    "post_missing_evidence",
                    "post requires raw evidence or an explicit gap",
                    str(post_id),
                )
            )
    return findings


def _metric_findings(conn: sqlite3.Connection) -> list[dict[str, str]]:
    posts = {str(_first(row, ("post_id", "id"))): row for row in _rows(conn, "posts", ("post_id", "id"))}
    raw_quality = _raw_quality(conn)
    findings: list[dict[str, str]] = []
    for row in _rows(conn, "metric_observations", ("post_id", "metric_name", "id", "metric_id")):
        metric = str(_first(row, ("metric_name", "name", "metric"), "")).lower()
        post_id = str(_first(row, ("post_id",), ""))
        value = _first(row, ("metric_value", "value"))
        status = str(_first(row, ("status",), "available")).lower()
        if value is not None and status == "available" and not _raw_ids(row):
            findings.append(
                _finding(
                    "metric",
                    "metric_missing_raw_evidence",
                    f"{metric} metric requires raw evidence",
                    post_id or str(_first(row, ("metric_id", "id", "observation_id"), "unknown_metric")),
                )
            )
            continue
        if metric not in {"saves", "shares", "saved"}:
            continue
        if _is_owned_post(posts.get(post_id, {})):
            continue
        raw_ids = _raw_ids(row)
        has_provider_evidence = any(raw_quality.get(raw_id, False) for raw_id in raw_ids)
        if not has_provider_evidence:
            findings.append(
                _finding(
                    "metric",
                    "third_party_metric_missing_provider_evidence",
                    f"third-party {metric} metric requires provider evidence",
                    post_id or str(_first(row, ("metric_id", "id"), "unknown_metric")),
                )
            )
    return findings


def _chunk_findings(conn: sqlite3.Connection) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for row in _rows(conn, "rag_chunks", ("post_id", "chunk_id", "id")):
        chunk_id = _first(row, ("chunk_id", "id"))
        if chunk_id and not _raw_ids(row) and not _gap_ids(row):
            findings.append(
                _finding(
                    "rag",
                    "chunk_missing_evidence",
                    "RAG chunk requires raw evidence IDs or explicit gap IDs",
                    str(chunk_id),
                )
            )
    return findings


def _carousel_child_findings(conn: sqlite3.Connection) -> list[dict[str, str]]:
    asset_media_by_post: dict[str, dict[int, bool]] = {}
    for row in _rows(conn, "assets", ("post_id", "asset_index", "id", "asset_id")):
        post_id = _first(row, ("post_id",))
        index = _int_or_none(_first(row, ("asset_index", "position", "index")))
        if post_id is not None and index is not None:
            asset_media_by_post.setdefault(str(post_id), {})[index] = _asset_has_media(row)

    gap_indexes, general_gap_posts = _carousel_gap_coverage(conn)
    findings: list[dict[str, str]] = []
    expected_by_post = _expected_children_by_post(conn)
    for row in _rows(conn, "posts", ("post_id", "id")):
        post_id = _first(row, ("post_id", "id"))
        if not post_id:
            continue
        expected = expected_by_post.get(str(post_id))
        if expected is None:
            expected = _int_or_none(_first(row, ("expected_child_count", "child_count", "asset_count")))
        media_type = str(_first(row, ("media_type", "post_type", "type"), "")).lower()
        if expected is None:
            continue
        if expected <= 1 and "carousel" not in media_type and "sidecar" not in media_type:
            continue
        if str(post_id) in general_gap_posts:
            continue
        asset_media = asset_media_by_post.get(str(post_id), {})
        covered_gaps = gap_indexes.get(str(post_id), set())
        start_index = min(asset_media) if asset_media else 0
        for index in range(start_index, start_index + expected):
            if asset_media.get(index) or index in covered_gaps:
                continue
            findings.append(
                _finding(
                    "media",
                    "carousel_child_missing",
                    "missing carousel child media requires an explicit gap",
                    f"{post_id}:{index}",
                )
            )
    return findings


def _expected_children_by_post(conn: sqlite3.Connection) -> dict[str, int]:
    expected: dict[str, int] = {}
    for row in _rows(conn, "post_snapshots", ("post_id", "captured_at", "snapshot_id", "id")):
        post_id = _first(row, ("post_id",))
        child_count = _int_or_none(_first(row, ("child_count", "expected_child_count", "asset_count")))
        if post_id and child_count is not None:
            expected[str(post_id)] = child_count
    return expected


def _carousel_gap_coverage(conn: sqlite3.Connection) -> tuple[dict[str, set[int]], set[str]]:
    indexes: dict[str, set[int]] = {}
    general_posts: set[str] = set()
    for row in _rows(conn, "gaps", ("post_id", "missing_index", "gap_id", "id")):
        post_id = _first(row, ("post_id",))
        if not post_id:
            continue
        field = str(_first(row, ("field", "gap_type", "kind"), "")).lower()
        if not _is_child_media_gap(field):
            continue
        index = _int_or_none(_first(row, ("missing_index", "asset_index", "index")))
        if index is not None:
            indexes.setdefault(str(post_id), set()).add(index)
        else:
            general_posts.add(str(post_id))
    return indexes, general_posts


def _asset_has_media(row: dict[str, Any]) -> bool:
    for name in ("source_url", "display_url", "media_sha256", "sha256", "media_file_id", "local_path"):
        if row.get(name):
            return True
    return False


def _is_child_media_gap(field: str) -> bool:
    return (
        ("carousel" in field and ("child" in field or "media" in field))
        or "child_media" in field
        or "child_media_urls" in field
    )


def _raw_quality(conn: sqlite3.Connection) -> dict[str, bool]:
    quality: dict[str, bool] = {}
    for row in _rows(conn, "raw_objects", ("raw_object_id", "id")):
        raw_id = _first(row, ("raw_object_id", "id"))
        sha = _first(row, ("sha256", "response_sha256", "payload_sha256"))
        if raw_id:
            quality[str(raw_id)] = bool(sha)
    return quality


def _is_owned_post(row: dict[str, Any]) -> bool:
    if not row:
        return False
    owned = _first(row, ("is_owned", "owned", "first_party"))
    if isinstance(owned, str):
        if owned.lower() in {"1", "true", "yes"}:
            return True
    elif owned:
        return True
    rights = str(_first(row, ("rights_scope",), "")).lower()
    return "owned" in rights or "first_party" in rights


def _gap_ids_by_post(conn: sqlite3.Connection) -> dict[str, set[str]]:
    gaps: dict[str, set[str]] = {}
    for row in _rows(conn, "gaps", ("post_id", "gap_id", "id")):
        post_id = _first(row, ("post_id",))
        gap_id = _first(row, ("gap_id", "id"))
        if post_id and gap_id:
            gaps.setdefault(str(post_id), set()).add(str(gap_id))
    return gaps


def _raw_ids(row: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for name in ("evidence_raw_object_ids", "raw_object_ids"):
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


def _int_or_none(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _finding(gate: str, code: str, message: str, target: str) -> dict[str, str]:
    return {
        "severity": "error",
        "gate": gate,
        "code": code,
        "message": message,
        "target": target,
    }
