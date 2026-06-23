from __future__ import annotations

import json
from pathlib import Path

from .base import InstagramProvider, ProviderPost, first_payload, normalize_post


class ManualJsonProvider(InstagramProvider):
    provider_name = "manual_json"

    def __init__(self, payload_path: str | Path):
        self.payload_path = Path(payload_path)

    def fetch_post_by_url(self, url: str) -> ProviderPost:
        payload = json.loads(self.payload_path.read_text(encoding="utf-8"))
        item = first_payload(payload, requested_url=url)
        return normalize_post(
            item,
            provider_name=self.provider_name,
            requested_url=url,
            request_metadata={"path": str(self.payload_path)},
        )
