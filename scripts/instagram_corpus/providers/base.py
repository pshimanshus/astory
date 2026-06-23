from __future__ import annotations

from dataclasses import dataclass, field
import json as json_module
import re
from typing import Any, Callable, Dict, Iterable, List, Optional
from urllib import request as urlrequest

try:
    from scripts.instagram_corpus.ids import normalize_shortcode as _repo_normalize_shortcode
except ModuleNotFoundError:  # pragma: no cover - exercised only when ids.py exists.
    _repo_normalize_shortcode = None


JsonDict = Dict[str, Any]
HttpPost = Callable[..., Any]


@dataclass
class ProviderChild:
    index: int
    type: str
    url: str
    raw: JsonDict = field(default_factory=dict)


@dataclass
class ProviderPost:
    source_url: str
    shortcode: str
    caption: str
    metrics: JsonDict
    content_type: str
    children: List[ProviderChild]
    raw: JsonDict = field(default_factory=dict)


class ProviderError(RuntimeError):
    pass


class InstagramProvider:
    provider_name: str

    def fetch_post_by_url(self, url: str) -> ProviderPost:
        raise NotImplementedError


def default_http_post(url: str, *, headers: JsonDict, json: JsonDict) -> Any:
    body = json_module.dumps(json).encode("utf-8")
    request = urlrequest.Request(url, data=body, headers=headers, method="POST")
    with urlrequest.urlopen(request) as response:
        text = response.read().decode("utf-8")
    return json_module.loads(text)


def first_payload(response: Any, requested_url: Optional[str] = None) -> JsonDict:
    if isinstance(response, list):
        if not response:
            raise ProviderError("provider response contained no items")
        if requested_url:
            requested_shortcode = shortcode_from_url(requested_url)
            for item in response:
                if not isinstance(item, dict):
                    continue
                item_url = first_value(item, ("url", "input_url", "permalink"))
                item_shortcode = first_value(item, ("shortcode", "shortCode", "code"))
                if item_url == requested_url or (
                    requested_shortcode
                    and normalize_shortcode(str(item_shortcode or "")) == requested_shortcode
                ):
                    return item
        first = response[0]
        if not isinstance(first, dict):
            raise ProviderError("provider response item is not an object")
        return first

    if isinstance(response, dict):
        for key in ("data", "items", "result", "results"):
            value = response.get(key)
            if isinstance(value, list):
                return first_payload(value, requested_url=requested_url)
        return response

    raise ProviderError("provider response is not JSON object or array")


def normalize_post(
    payload: JsonDict,
    *,
    provider_name: str,
    requested_url: Optional[str] = None,
    request_metadata: Optional[JsonDict] = None,
    redaction_values: Iterable[str] = (),
) -> ProviderPost:
    source_url = str(
        first_value(payload, ("url", "input_url", "permalink", "postUrl"))
        or requested_url
        or ""
    )
    shortcode = normalize_shortcode(
        str(
            first_value(payload, ("shortcode", "shortCode", "code"))
            or shortcode_from_url(source_url)
            or shortcode_from_url(requested_url or "")
            or ""
        )
    )
    children = normalize_children(payload)
    content_type = normalize_content_type(payload, source_url=source_url, children=children)

    raw = {
        "provider": provider_name,
        "payload": redact(payload, redaction_values),
    }
    if request_metadata is not None:
        raw["request"] = redact(request_metadata, redaction_values)

    return ProviderPost(
        source_url=source_url,
        shortcode=shortcode,
        caption=normalize_caption(payload),
        metrics={
            "likes": coerce_int(first_value(payload, ("likes", "likesCount", "likes_count"))),
            "comments": coerce_int(
                first_value(
                    payload,
                    ("num_comments", "comments", "commentsCount", "comments_count"),
                )
            ),
            "views": coerce_int(
                first_value(
                    payload,
                    ("views", "view_count", "videoViewCount", "video_view_count"),
                )
            ),
            "plays": coerce_int(
                first_value(
                    payload,
                    ("plays", "play_count", "videoPlayCount", "video_play_count"),
                )
            ),
        },
        content_type=content_type,
        children=children,
        raw=raw,
    )


def normalize_caption(payload: JsonDict) -> str:
    value = first_value(payload, ("description", "caption", "text"))
    if isinstance(value, dict):
        value = first_value(value, ("text", "caption", "description"))
    return str(value or "")


def normalize_children(payload: JsonDict) -> List[ProviderChild]:
    collected: List[tuple[str, str, str]] = []
    seen_urls = set()

    def add(raw_type: str, url: Optional[str], provider_field: str) -> None:
        if not url or url in seen_urls:
            return
        seen_urls.add(url)
        collected.append((normalize_child_type(raw_type), url, provider_field))

    for item in as_list(payload.get("photos")):
        add("Photo", media_url(item, prefer_video=False), "photos")

    for item in as_list(payload.get("videos")):
        add("Video", media_url(item, prefer_video=True), "videos")

    for item in as_list(payload.get("post_content")):
        raw_type = child_raw_type(item)
        add(raw_type, media_url(item, prefer_video=raw_type.lower() == "video"), "post_content")

    for item in as_list(payload.get("childPosts")) + as_list(payload.get("child_posts")):
        raw_type = child_raw_type(item)
        add(raw_type, media_url(item, prefer_video=raw_type.lower() == "video"), "childPosts")

    if not collected:
        raw_type = str(first_value(payload, ("type", "content_type", "productType")) or "")
        prefer_video = "video" in raw_type.lower() or "clip" in raw_type.lower()
        add(raw_type or "Photo", media_url(payload, prefer_video=prefer_video), "display")

    return [
        ProviderChild(
            index=index,
            type=child_type,
            url=url,
            raw={"provider_field": provider_field},
        )
        for index, (child_type, url, provider_field) in enumerate(collected)
    ]


def normalize_content_type(
    payload: JsonDict,
    *,
    source_url: str,
    children: List[ProviderChild],
) -> str:
    raw_values = [
        str(value).lower()
        for value in (
            first_value(payload, ("content_type", "type", "productType", "product_type")),
            source_url,
        )
        if value
    ]
    raw = " ".join(raw_values)

    if "sidecar" in raw or "carousel" in raw or len(children) > 1:
        return "Carousel"
    if "reel" in raw or "clips" in raw:
        return "Reel"
    if "video" in raw or (children and children[0].type == "Video"):
        return "Video"
    return "Photo"


def normalize_child_type(value: str) -> str:
    raw = str(value or "").lower()
    if "video" in raw or "clip" in raw:
        return "Video"
    return "Photo"


def child_raw_type(item: Any) -> str:
    if isinstance(item, dict):
        return str(
            first_value(item, ("type", "content_type", "media_type", "mediaType"))
            or ""
        )
    return ""


def media_url(item: Any, *, prefer_video: bool) -> Optional[str]:
    if isinstance(item, str):
        return item
    if not isinstance(item, dict):
        return None

    video_fields = ("videoUrl", "video_url", "video", "video_src", "video_url_original")
    image_fields = (
        "url",
        "src",
        "displayUrl",
        "display_url",
        "imageUrl",
        "image_url",
        "media_url",
        "thumbnailUrl",
        "thumbnail_url",
    )
    field_order = video_fields + image_fields if prefer_video else image_fields + video_fields
    value = first_value(item, field_order)
    return str(value) if value else None


def as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def first_value(payload: JsonDict, keys: Iterable[str]) -> Any:
    for key in keys:
        if key in payload and payload[key] is not None:
            return payload[key]
    return None


def coerce_int(value: Any) -> Optional[int]:
    if value is None or isinstance(value, bool) or isinstance(value, (list, dict)):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)

    text = str(value).strip().lower().replace(",", "")
    if not text:
        return None
    match = re.search(r"([-+]?\d+(?:\.\d+)?)\s*([kmb])?", text)
    if not match:
        return None
    number = float(match.group(1))
    multiplier = {"k": 1_000, "m": 1_000_000, "b": 1_000_000_000}.get(
        match.group(2),
        1,
    )
    return int(number * multiplier)


def normalize_shortcode(value: str) -> str:
    shortcode = str(value or "").strip().strip("/")
    if _repo_normalize_shortcode is not None:
        return _repo_normalize_shortcode(shortcode)
    return shortcode


def shortcode_from_url(url: str) -> str:
    match = re.search(r"instagram\.com/(?:p|reel|tv)/([^/?#]+)/?", str(url or ""))
    return normalize_shortcode(match.group(1)) if match else ""


def redact(value: Any, redaction_values: Iterable[str]) -> Any:
    tokens = [str(token) for token in redaction_values if token]
    if isinstance(value, dict):
        return {key: redact(item, tokens) for key, item in value.items()}
    if isinstance(value, list):
        return [redact(item, tokens) for item in value]
    if isinstance(value, tuple):
        return tuple(redact(item, tokens) for item in value)
    if isinstance(value, str):
        redacted = value
        for token in tokens:
            redacted = redacted.replace(token, "<redacted>")
        return redacted
    return value
