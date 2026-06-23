from __future__ import annotations

from .base import (
    HttpPost,
    InstagramProvider,
    ProviderPost,
    default_http_post,
    first_payload,
    normalize_post,
)


BRIGHTDATA_DATASET_ID = "gd_lk5ns7kz21pck8jpis"


class BrightDataProvider(InstagramProvider):
    provider_name = "brightdata"

    def __init__(
        self,
        token: str,
        http_post: HttpPost | None = None,
        dataset_id: str = BRIGHTDATA_DATASET_ID,
    ):
        self.token = token
        self.http_post = http_post or default_http_post
        self.dataset_id = dataset_id

    def fetch_post_by_url(self, url: str) -> ProviderPost:
        endpoint = (
            "https://api.brightdata.com/datasets/v3/scrape"
            f"?dataset_id={self.dataset_id}&include_errors=true"
        )
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        body = {"input": [{"url": url}]}
        response = self.http_post(endpoint, headers=headers, json=body)
        payload = first_payload(response, requested_url=url)
        return normalize_post(
            payload,
            provider_name=self.provider_name,
            requested_url=url,
            request_metadata={"url": endpoint, "headers": headers, "json": body},
            redaction_values=(self.token,),
        )
