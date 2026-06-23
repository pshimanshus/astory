from __future__ import annotations

from .base import (
    HttpPost,
    InstagramProvider,
    ProviderPost,
    default_http_post,
    first_payload,
    normalize_post,
)


DEFAULT_APIFY_ACTOR = "apify/instagram-post-scraper"


class ApifyProvider(InstagramProvider):
    provider_name = "apify"

    def __init__(
        self,
        token: str,
        actor: str = DEFAULT_APIFY_ACTOR,
        http_post: HttpPost | None = None,
    ):
        self.token = token
        self.actor = actor
        self.http_post = http_post or default_http_post

    def fetch_post_by_url(self, url: str) -> ProviderPost:
        actor_id = self.actor.replace("/", "~")
        endpoint = (
            f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items"
        )
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        body = {
            "directUrls": [url],
            "resultsType": "posts",
            "resultsLimit": 1,
        }
        response = self.http_post(endpoint, headers=headers, json=body)
        payload = first_payload(response, requested_url=url)
        return normalize_post(
            payload,
            provider_name=self.provider_name,
            requested_url=url,
            request_metadata={
                "url": endpoint,
                "headers": headers,
                "json": body,
                "actor": self.actor,
            },
            redaction_values=(self.token,),
        )
