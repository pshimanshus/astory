from __future__ import annotations

import hashlib
import json
import mimetypes
from pathlib import Path
from typing import Any, Dict, Union
from urllib.parse import urlparse
from urllib.request import urlopen


_MIME_EXTENSIONS = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "video/mp4": ".mp4",
}


def store_media(
    root: Union[str, Path],
    source_url: str,
    content: bytes,
    mime: str,
    raw_object_id: str,
    variant: str = "original",
    width: int | None = None,
    height: int | None = None,
    duration_seconds: float | None = None,
    rights_scope: str = "third_party_analysis_only",
) -> Dict[str, Any]:
    content_bytes = _as_bytes(content)
    sha256 = hashlib.sha256(content_bytes).hexdigest()
    media_path = _media_path(Path(root), sha256, mime)
    media_path.parent.mkdir(parents=True, exist_ok=True)

    if not media_path.exists():
        media_path.write_bytes(content_bytes)

    sidecar_path = media_path.with_suffix(media_path.suffix + ".json")
    sidecar = {
        "sha256": sha256,
        "source_url": source_url,
        "mime": mime,
        "bytes": len(content_bytes),
        "width": width,
        "height": height,
        "duration_seconds": duration_seconds,
        "rights_scope": rights_scope,
        "variant": variant,
        "raw_object_id": raw_object_id,
    }
    _write_json(sidecar_path, sidecar)

    stored = dict(sidecar)
    stored["path"] = str(media_path)
    stored["sidecar_path"] = str(sidecar_path)
    return stored


def download_media_assets(conn, root: Union[str, Path], run_id: str) -> Dict[str, int]:
    rows = conn.execute(
        """
        SELECT a.asset_id, a.source_url, a.media_type, p.raw_object_id
        FROM assets a
        LEFT JOIN posts p ON p.post_id = a.post_id
        WHERE a.source_url IS NOT NULL
          AND a.source_url != ''
          AND (a.media_file_id IS NULL OR a.media_file_id = '')
        ORDER BY a.post_id, a.asset_index
        """
    ).fetchall()
    downloaded = 0
    failed = 0
    skipped = 0
    for row in rows:
        asset_id = _row_value(row, "asset_id", 0)
        source_url = _row_value(row, "source_url", 1)
        raw_object_id = _row_value(row, "raw_object_id", 3) or f"raw_media_{run_id}"
        try:
            content, mime = _download_url(source_url)
            stored = store_media(
                root,
                source_url,
                content,
                mime,
                raw_object_id,
                variant="original",
            )
            media_file_id = f"media_{stored['sha256'][:16]}"
            conn.execute(
                """
                INSERT OR REPLACE INTO media_files(
                    media_file_id, sha256, local_path, source_url, mime_type,
                    byte_count, width, height, duration_seconds, variant,
                    raw_object_id, rights_scope, metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    media_file_id,
                    stored["sha256"],
                    stored["path"],
                    source_url,
                    stored["mime"],
                    stored["bytes"],
                    stored["width"],
                    stored["height"],
                    stored["duration_seconds"],
                    stored["variant"],
                    raw_object_id,
                    stored["rights_scope"],
                    json.dumps({"run_id": run_id, "sidecar_path": stored["sidecar_path"]}, sort_keys=True),
                ),
            )
            conn.execute(
                "UPDATE assets SET media_file_id = ?, status = ? WHERE asset_id = ?",
                (media_file_id, "downloaded", asset_id),
            )
            downloaded += 1
        except Exception as exc:
            conn.execute(
                "UPDATE assets SET status = ? WHERE asset_id = ?",
                (f"download_failed:{type(exc).__name__}", asset_id),
            )
            failed += 1
    conn.commit()
    return {"downloaded": downloaded, "failed": failed, "skipped": skipped}


def _media_path(root: Path, sha256: str, mime: str) -> Path:
    return root / "media" / "sha256" / sha256[:2] / f"{sha256}{_extension_for_mime(mime)}"


def _extension_for_mime(mime: str) -> str:
    normalized = mime.split(";", 1)[0].strip().lower()
    return _MIME_EXTENSIONS.get(normalized, ".bin")


def _as_bytes(content: bytes) -> bytes:
    if isinstance(content, bytes):
        return content
    if isinstance(content, bytearray):
        return bytes(content)
    if isinstance(content, memoryview):
        return content.tobytes()
    raise TypeError("content must be bytes-like")


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _download_url(source_url: str) -> tuple[bytes, str]:
    with urlopen(source_url, timeout=30) as response:
        content = response.read()
        mime = response.headers.get_content_type() if response.headers else None
    if not mime or mime == "text/plain":
        guessed, _encoding = mimetypes.guess_type(urlparse(source_url).path)
        if guessed:
            mime = guessed
    return content, mime or "application/octet-stream"


def _row_value(row, key: str, index: int):
    if hasattr(row, "keys"):
        return row[key]
    return row[index]
