# Instagram Evidence Bank V2 Design

**Date:** 2026-06-18

**Goal:** Build a complete, provenance-heavy content evidence bank for the best performing Instagram posts already identified in the winner bank, so A Story of Two can search, study, and remix proven mechanics without pretending copied competitor work is ours.

**Decision:** Browser capture is not the primary architecture. It is a diagnostic fallback. The primary path is provider/API acquisition into an immutable evidence ledger, then media download, OCR, visual annotation, and RAG exports built only from cited raw evidence.

## What We Already Have

Local files already contain the seed ranking:

- `references/text-style/winner-bank/posts_merged.json`: 715 posts from 17 accounts.
- `references/text-style/winner-bank/winner_bank.json`: 170 winners from 14 accounts.
- `references/text-style/content-dump/full-715-offline-2026-06-16/content_dump.jsonl`: 715 offline seed records.
- `references/text-style/content-dump/top-170-offline-2026-06-16/content_dump.jsonl`: 170 offline seed records.
- `data/instagram/account_inventory.json`: 87 owned A Story posts with first-party Graph insight fields including `saved` and `shares`.
- `data/instagram/carousel_posts/*`: 12 owned carousel exports with slide files and insights.

Current gap: the winner bank is not yet a complete evidence bank. The current seed records have captions, visible metrics, basic type/child counts, and first-display URLs. They do not preserve immutable provider payloads, full child carousel media, downloaded media hashes, slide-by-slide OCR, visual composition labels, comments at scale, or reliable third-party saves/shares.

## What Is Possible

Possible with high confidence:

- Build one stable ID per source post.
- Store account, shortcode, permalink, format, timestamp, caption, likes, comments, views/plays when visible/provider-supplied.
- Recover child carousel image/video URLs through a provider that returns `photos`, `videos`, or `post_content`.
- Download each child asset into a content-addressed media store.
- OCR each slide and save exact slide text, line boxes, confidence, and fallback status.
- Add visual labels such as `no_visuals_text_only`, `photo_quote`, `illustrated_scene`, `chat_screenshot_style`, `meme_panel`, `video_reel`, and `unknown_needs_review`.
- Export RAG-ready JSONL chunks with raw evidence IDs and explicit gaps.
- Merge first-party A Story data where saves/shares are available through owned-account insights.

Not reliably possible without special access:

- Competitor saves and shares. These should be marked unavailable unless a provider explicitly returns them and the raw payload is stored.
- Guaranteed full historical comments for every public post.
- Legally safe reuse of raw competitor images/captions as training material. We can store evidence for internal analysis only if approved, but the RAG should prefer sanitized notes, mechanics, and source citations over raw copied expression.
- A durable logged-in browser scraper. Instagram UI, session state, rate limits, and anti-bot behavior make it a bad primary dependency.

## Operating Model

The Anthropic-style operating loop that applies here is:

1. Explore first, then plan, then implement.
2. Fan out independent research and implementation lanes.
3. Keep each worker on a bounded file/domain ownership.
4. Test on a small batch before scale.
5. Use adversarial review before calling the pipeline ready.

Sources:

- Claude Code best practices: https://code.claude.com/docs/en/best-practices
- Claude Code agent teams: https://code.claude.com/docs/en/agent-teams
- Anthropic teams workflow examples: https://claude.com/blog/how-anthropic-teams-use-claude-code

## Architecture

Use three durable layers. Derived data can always be rebuilt from lower layers.

### 1. Immutable Raw Store

Path:

```text
data/instagram-corpus/raw/{provider}/{run_id}/
```

Every raw object stores:

- provider name
- run ID
- sanitized request URL
- request mode
- HTTP status or provider status
- response bytes path
- response SHA-256
- captured timestamp
- source URL
- object type: `post`, `profile`, `comments`, `reel`, `owned_insights`, `manual_note`, `public_html`

No normalization happens in raw files. Raw files are the evidence.

### 2. Content-Addressed Media Store

Path:

```text
data/instagram-corpus/media/sha256/{first_two_hash_chars}/{sha256}.{ext}
```

Every media file has a sidecar:

```json
{
  "sha256": "hash",
  "source_url": "https://...",
  "mime": "image/jpeg",
  "bytes": 12345,
  "width": 1080,
  "height": 1350,
  "duration_seconds": null,
  "variant": "original",
  "raw_object_id": "raw_provider_hash",
  "rights_scope": "third_party_analysis_only"
}
```

Shortcodes are mappings. Hashes are truth.

### 3. Catalog Database

Use SQLite for the local transactional catalog and resume queue. DuckDB can be added later for analytics, but SQLite is enough for the first implementation.

Core tables:

- `ingest_runs`
- `raw_objects`
- `accounts`
- `posts`
- `post_snapshots`
- `assets`
- `media_files`
- `metric_observations`
- `comments`
- `annotations`
- `ocr_results`
- `rag_chunks`
- `gaps`
- `jobs`

Metric rule:

- Third-party posts may have `likes`, `comments`, `views`, and `plays`.
- Third-party `saves` and `shares` must be `unavailable` unless a provider payload explicitly supplies them.
- Owned A Story posts may use first-party insight metrics such as `saved` and `shares`, with raw Graph evidence attached.

## Acquisition Ladder

### Primary: Bright Data Instagram Scraper API

Reason: docs show structured Instagram profile, posts, reels, and comments data; sync requests handle up to 20 URLs and async up to 5,000 URLs; post-by-URL responses include fields such as shortcode, likes, comments, content type, photos, thumbnail, and `post_content`.

Sources:

- https://docs.brightdata.com/datasets/scrapers/instagram/introduction
- https://docs.brightdata.com/api-reference/scrapers/social-media-apis/instagram-posts-collect-by-url

Pilot command shape:

```bash
curl --request POST \
  --url 'https://api.brightdata.com/datasets/v3/scrape?dataset_id=gd_lk5ns7kz21pck8jpis&include_errors=true' \
  --header "Authorization: Bearer $BRIGHTDATA_TOKEN" \
  --header "Content-Type: application/json" \
  --data '{"input":[{"url":"https://www.instagram.com/p/DUtQzmaj9Rw/"}]}'
```

Acceptance gate: reject as primary if child media URLs are missing for carousels.

### Secondary: Apify Instagram Actors

Reason: Apify's Instagram scraper supports posts, profiles, locations, search, photos, comments, and API/dataset export. Its related actors include post, reel, hashtag, and comment scrapers.

Source:

- https://apify.com/apify/instagram-scraper

Acceptance gate: validate output contract on a 20-post pilot before scaling.

### Fallback API: HikerAPI

Reason: HikerAPI exposes media info by URL/code/id and comments endpoints using an `x-access-key` header.

Source:

- https://hiker-doc.readthedocs.io/en/latest/api-reference/v2/media/

Use as a validator or missing-field recovery path, not the only acquisition path.

### Audit/Media Fallback: Instaloader and Gallery-dl

Instaloader can download media, captions, comments, and metadata and supports resumable iterations, but it is unofficial and should be used at your own risk.

Sources:

- https://instaloader.github.io/
- https://github.com/instaloader/instaloader

Gallery-dl is useful as a media downloader and supports cookies/browser cookies, which also makes it risky for production. It should not be a logged-in primary pipeline.

Source:

- https://github.com/mikf/gallery-dl

### Last Resort: Browser/Playwright Capture

Use only for:

- validating one suspicious provider result
- capturing a public page manually for a top-priority missing post
- screenshot evidence where API/provider data disagrees

Browser capture is not used to produce the 700-post corpus at scale.

## OCR And Slide Segmentation

Tier 1: classic OCR.

- Preferred: PaddleOCR or RapidOCR.
- Use for text-heavy carousels, quote slides, clean white-background posts, and most Instagram graphics.
- Store line text, boxes, order, native confidence, and preprocessing variant.

Tier 2: VLM fallback.

- Preferred candidates: PaddleOCR-VL, Qwen-style VLM, Florence-2, Surya, or olmOCR depending on hardware.
- Use only when Tier 1 returns blank/low-confidence/incoherent results.
- Mark VLM confidence as uncalibrated unless verified by OCR agreement or token scores.

Sources:

- Hugging Face OCR open models: https://huggingface.co/blog/ocr-open-models
- Hugging Face OCR model listing: https://huggingface.co/models?other=ocr
- PaddleOCR-VL appears in the current OCR model list.
- Surya, olmOCR, DeepSeek-OCR, Chandra, and LightOnOCR are viable benchmark candidates, not automatic production dependencies.

Slide output shape:

```json
{
  "slide_id": "ig_DUtQzmaj9Rw_03",
  "post_id": "ig_DUtQzmaj9Rw",
  "asset_index": 3,
  "media_sha256": "hash",
  "visual_type": "no_visuals_text_only",
  "visual_summary": "plain white background with centered black text",
  "ocr": {
    "engine": "paddleocr",
    "fallback_engine": null,
    "status": "accepted",
    "full_text": "slide text",
    "mean_confidence": 0.94,
    "lines": [
      {
        "order": 0,
        "text": "line text",
        "bbox": [120, 410, 960, 468],
        "confidence": 0.94
      }
    ]
  }
}
```

## RAG Export Contract

RAG reads derived JSONL, not loose raw dumps.

Exports:

- `data/instagram-corpus/exports/rag/posts.jsonl`
- `data/instagram-corpus/exports/rag/assets.jsonl`
- `data/instagram-corpus/exports/rag/comments.jsonl`
- `data/instagram-corpus/exports/rag/chunks.jsonl`
- `data/instagram-corpus/exports/rag/gaps.jsonl`

Each chunk must include:

- stable `chunk_id`
- source `post_id`
- source URL
- evidence raw object IDs
- rights scope
- metric context
- explicit unavailable fields
- text safe for retrieval

The RAG can learn mechanics such as "plain text confession carousel", "first slide high-friction hook", "last slide brand wrapper", "comments cluster around tagging partners". It must not treat raw competitor captions as ready-to-publish A Story copy.

## Validation Gates

Raw gate:

- Every fetched object has bytes, SHA-256, provider, capture time, source URL, and no leaked token.

Count gate:

- Manifest counts match DB counts and JSONL line counts.

Media gate:

- Each downloaded file hash matches the catalog.
- Missing carousel children create `gaps` rows.

Metric gate:

- No third-party saves/shares unless provider-supplied and evidenced.
- Owned insights must cite owned Graph raw evidence.

OCR gate:

- OCR status is `accepted`, `needs_review`, or `failed`.
- Blank/low-confidence text slides are never silently accepted.

RAG gate:

- Every retrieval chunk has evidence IDs or explicit gap IDs.
- No orphan chunks.
- No uncited derived claims.

Rebuild gate:

- Derived exports can be deleted and regenerated from raw store plus SQLite.

## First Pilot

Pilot input:

- Force include `https://www.instagram.com/p/DUtQzmaj9Rw/`.
- Add 19 top-ranked winner-bank URLs with a mix of carousels, reels, and single images.

Pilot success criteria:

- 20 post records ingested.
- 90 percent or better child asset coverage for carousels, or clear provider gap reasons.
- 100 percent of raw payloads stored with hash and provider.
- 100 percent of normalized posts cite raw evidence.
- OCR attempted on every downloaded image asset.
- RAG export validates with no orphan chunks.

Scale criteria:

- Run top 170 after pilot passes.
- Run full 715 after top 170 passes.

## Agent Work Split

Coordinator:

- Owns spec, schema boundaries, merge/review, and validation gates.

Acquisition agent:

- Provider adapters and raw object persistence.

Corpus agent:

- SQLite schema, seed import, jobs, gaps, and normalization.

Media/OCR agent:

- Download, hash, media sidecars, OCR output, and visual labels.

RAG agent:

- Derived JSONL exports and RAG chunk validation.

Adversarial reviewer:

- Reviews plan/diff against requirements, compliance boundaries, data provenance, and untested claims.

## Sources Consulted

- Anthropic Claude Code best practices: https://code.claude.com/docs/en/best-practices
- Anthropic Claude Code agent teams: https://code.claude.com/docs/en/agent-teams
- Anthropic teams usage examples: https://claude.com/blog/how-anthropic-teams-use-claude-code
- Bright Data Instagram Scraper API: https://docs.brightdata.com/datasets/scrapers/instagram/introduction
- Bright Data Instagram posts by URL: https://docs.brightdata.com/api-reference/scrapers/social-media-apis/instagram-posts-collect-by-url
- Apify Instagram Scraper: https://apify.com/apify/instagram-scraper
- HikerAPI media endpoints: https://hiker-doc.readthedocs.io/en/latest/api-reference/v2/media/
- Instaloader docs: https://instaloader.github.io/
- Instaloader GitHub: https://github.com/instaloader/instaloader
- Gallery-dl GitHub: https://github.com/mikf/gallery-dl
- Hugging Face OCR open models: https://huggingface.co/blog/ocr-open-models
- Hugging Face OCR model listing: https://huggingface.co/models?other=ocr
- Meta Instagram media insights reference: https://developers.facebook.com/docs/instagram-platform/reference/instagram-media/insights/
