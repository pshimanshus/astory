from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


REDACTED = "[REDACTED]"
SENSITIVE_HEADER_NAMES = {
    "authorization",
    "cookie",
    "proxy-authorization",
    "x-access-key",
}
SENSITIVE_NAME_PARTS = ("token", "secret", "cookie", "session", "password")


def write_raw_object(
    root,
    provider,
    run_id,
    object_type,
    source_url,
    payload,
    request_url=None,
    request_headers=None,
    response_status=None,
    metadata=None,
):
    root_path = Path(root)
    payload_bytes = _ensure_bytes(payload)
    sha256_hex = hashlib.sha256(payload_bytes).hexdigest()
    captured_at = _utc_now()

    safe_provider = _slug(provider)
    safe_run_id = _slug(run_id)
    safe_object_type = _slug(object_type)
    raw_dir = root_path / "raw" / safe_provider / safe_run_id
    raw_dir.mkdir(parents=True, exist_ok=True)

    stem = f"{safe_object_type}_{sha256_hex[:16]}"
    payload_path = raw_dir / f"{stem}.json"
    metadata_path = raw_dir / f"{stem}.meta.json"
    payload_path.write_bytes(payload_bytes)

    raw_object_id = f"raw_{safe_provider}_{safe_run_id}_{safe_object_type}_{sha256_hex[:16]}"
    record = {
        "raw_object_id": raw_object_id,
        "provider": provider,
        "run_id": run_id,
        "object_type": object_type,
        "source_url": source_url,
        "request_url": _redact_url(request_url) if request_url else None,
        "request_headers": _redact_headers(request_headers or {}),
        "response_status": response_status,
        "local_path": _relative_posix(root_path, payload_path),
        "metadata_path": _relative_posix(root_path, metadata_path),
        "sha256": sha256_hex,
        "captured_at": captured_at,
        "metadata": _redact_value(metadata or {}),
    }
    metadata_path.write_text(
        json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return record


def _ensure_bytes(payload):
    if isinstance(payload, bytes):
        return payload
    if isinstance(payload, str):
        return payload.encode("utf-8")
    raise TypeError("payload must be bytes or str")


def _utc_now():
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _slug(value):
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value or "").strip())
    return slug.strip("._-") or "unknown"


def _relative_posix(root, path):
    return path.relative_to(root).as_posix()


def _redact_headers(headers):
    redacted = {}
    for name, value in headers.items():
        if _is_sensitive_name(name):
            redacted[name] = REDACTED
        else:
            redacted[name] = value
    return redacted


def _redact_url(url):
    parts = urlsplit(url)
    query = []
    for name, value in parse_qsl(parts.query, keep_blank_values=True):
        query.append((name, REDACTED if _is_sensitive_name(name) else value))
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def _redact_value(value):
    if isinstance(value, dict):
        return {
            key: (REDACTED if _is_sensitive_name(key) else _redact_value(item))
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_redact_value(item) for item in value]
    return value


def _is_sensitive_name(name):
    lowered = str(name).lower()
    return lowered in SENSITIVE_HEADER_NAMES or any(part in lowered for part in SENSITIVE_NAME_PARTS)

