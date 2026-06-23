from __future__ import annotations

import re
from urllib.parse import urlparse


SHORTCODE_RE = re.compile(r"^[A-Za-z0-9_-]+$")
INSTAGRAM_POST_KINDS = {"p", "reel", "tv"}


def normalize_shortcode(value: str) -> str:
    raw = (value or "").strip()
    if not raw:
        raise ValueError("shortcode is required")

    if "instagram.com/" in raw and "://" not in raw:
        raw = "https://" + raw.lstrip("/")

    parsed = urlparse(raw)
    if parsed.scheme or parsed.netloc:
        shortcode = _shortcode_from_path(parsed.path)
    else:
        shortcode = raw.split("?", 1)[0].split("#", 1)[0].strip("/")
        if "/" in shortcode:
            shortcode = _shortcode_from_path(shortcode)

    if not shortcode or not SHORTCODE_RE.match(shortcode):
        raise ValueError(f"invalid Instagram shortcode: {value!r}")
    return shortcode


def post_id_from_shortcode(shortcode: str) -> str:
    return "ig_" + normalize_shortcode(shortcode)


def media_hash_path(sha256_hex: str, suffix: str) -> str:
    digest = (sha256_hex or "").strip().lower()
    if not digest:
        raise ValueError("sha256 digest is required")
    extension = (suffix or "").strip().lower()
    if extension and not extension.startswith("."):
        extension = "." + extension
    return f"sha256/{digest[:2]}/{digest}{extension}"


def _shortcode_from_path(path: str) -> str:
    parts = [part for part in path.split("/") if part]
    if len(parts) < 2 or parts[0] not in INSTAGRAM_POST_KINDS:
        raise ValueError(f"unsupported Instagram post URL path: {path!r}")
    return parts[1]
