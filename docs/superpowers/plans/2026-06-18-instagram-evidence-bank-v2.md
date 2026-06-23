# Instagram Evidence Bank V2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a recoverable Instagram evidence-bank pipeline that turns the existing 715 winner-bank seed posts into raw-evidenced, media-backed, OCR-annotated, RAG-ready corpus records.

**Architecture:** Provider-first acquisition writes immutable raw payloads, downloaded media is content-addressed, SQLite owns the normalized catalog and job queue, and JSONL RAG exports are derived from the catalog with citations and explicit gaps. Browser capture is limited to diagnostics.

**Tech Stack:** Python 3 standard library first, SQLite, JSONL, SHA-256 media store, optional provider clients via HTTP, optional PaddleOCR/RapidOCR after fixture-backed interfaces exist.

---

## Execution Mode

Use subagent-driven development with disjoint ownership:

- Agent A: `scripts/instagram_corpus/providers/*`, provider fixtures, raw acquisition tests.
- Agent B: `scripts/instagram_corpus/schema.py`, `db.py`, `seed_import.py`, catalog tests.
- Agent C: `scripts/instagram_corpus/media.py`, `ocr.py`, media/OCR tests.
- Agent D: `scripts/instagram_corpus/export_rag.py`, `validate.py`, CLI/export tests.
- Coordinator: reviews each patch, runs integration tests, then dispatches adversarial review.

No agent should edit unrelated A Story workflow files. The worktree is already dirty; do not revert or tidy files outside this plan.

## Files

Create:

- `scripts/instagram_corpus/__init__.py`
- `scripts/instagram_corpus/ids.py`
- `scripts/instagram_corpus/schema.py`
- `scripts/instagram_corpus/db.py`
- `scripts/instagram_corpus/raw_store.py`
- `scripts/instagram_corpus/seed_import.py`
- `scripts/instagram_corpus/providers/__init__.py`
- `scripts/instagram_corpus/providers/base.py`
- `scripts/instagram_corpus/providers/brightdata.py`
- `scripts/instagram_corpus/providers/apify.py`
- `scripts/instagram_corpus/providers/manual_json.py`
- `scripts/instagram_corpus/media.py`
- `scripts/instagram_corpus/ocr.py`
- `scripts/instagram_corpus/export_rag.py`
- `scripts/instagram_corpus/validate.py`
- `scripts/instagram_corpus_cli.py`
- `tests/test_instagram_corpus_ids.py`
- `tests/test_instagram_corpus_db.py`
- `tests/test_instagram_corpus_seed_import.py`
- `tests/test_instagram_corpus_raw_store.py`
- `tests/test_instagram_corpus_providers.py`
- `tests/test_instagram_corpus_media.py`
- `tests/test_instagram_corpus_ocr.py`
- `tests/test_instagram_corpus_export_rag.py`
- `tests/test_instagram_corpus_validate.py`
- `tests/fixtures/instagram_corpus/brightdata_post_carousel.json`
- `tests/fixtures/instagram_corpus/apify_post_reel.json`
- `tests/fixtures/instagram_corpus/winner_seed_minimal.json`

Generated at runtime, not committed unless explicitly requested:

- `data/instagram-corpus/corpus.sqlite`
- `data/instagram-corpus/raw/*`
- `data/instagram-corpus/media/*`
- `data/instagram-corpus/exports/rag/*.jsonl`
- `data/instagram-corpus/manifests/*.json`

## Task 1: Stable IDs

**Files:**

- Create: `scripts/instagram_corpus/ids.py`
- Test: `tests/test_instagram_corpus_ids.py`

- [ ] **Step 1: Write the failing tests**

```python
import unittest

from scripts.instagram_corpus.ids import media_hash_path, normalize_shortcode, post_id_from_shortcode


class InstagramCorpusIdsTest(unittest.TestCase):
    def test_normalize_shortcode_from_url(self):
        self.assertEqual(normalize_shortcode("https://www.instagram.com/p/DUtQzmaj9Rw/"), "DUtQzmaj9Rw")

    def test_post_id_from_shortcode(self):
        self.assertEqual(post_id_from_shortcode("DUtQzmaj9Rw"), "ig_DUtQzmaj9Rw")

    def test_media_hash_path(self):
        self.assertEqual(
            media_hash_path("abc123", ".jpg"),
            "sha256/ab/abc123.jpg",
        )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test and confirm failure**

Run:

```bash
python3 -m unittest tests.test_instagram_corpus_ids -v
```

Expected: import failure because `scripts.instagram_corpus.ids` does not exist yet.

- [ ] **Step 3: Implement the module**

Implement three pure functions:

- `normalize_shortcode(value: str) -> str`
- `post_id_from_shortcode(shortcode: str) -> str`
- `media_hash_path(sha256_hex: str, suffix: str) -> str`

Rules:

- Accept direct shortcodes and Instagram `/p/`, `/reel/`, and `/tv/` URLs.
- Reject empty values with `ValueError`.
- Strip query strings and trailing slashes.
- Lowercase only the file suffix, not the shortcode.

- [ ] **Step 4: Run the test and confirm pass**

Run:

```bash
python3 -m unittest tests.test_instagram_corpus_ids -v
```

Expected: 3 tests pass.

## Task 2: SQLite Schema And Catalog Helpers

**Files:**

- Create: `scripts/instagram_corpus/schema.py`
- Create: `scripts/instagram_corpus/db.py`
- Test: `tests/test_instagram_corpus_db.py`

- [ ] **Step 1: Write schema tests**

Test an in-memory database can create all required tables and enforce uniqueness for `posts.post_id` and `raw_objects.raw_object_id`.

Required table names:

```python
REQUIRED_TABLES = {
    "ingest_runs",
    "raw_objects",
    "accounts",
    "posts",
    "post_snapshots",
    "assets",
    "media_files",
    "metric_observations",
    "comments",
    "annotations",
    "ocr_results",
    "rag_chunks",
    "gaps",
    "jobs",
}
```

- [ ] **Step 2: Run the schema test and confirm failure**

Run:

```bash
python3 -m unittest tests.test_instagram_corpus_db -v
```

Expected: import failure.

- [ ] **Step 3: Implement schema creation**

`schema.py` exposes `SCHEMA_SQL`.

`db.py` exposes:

- `connect(path: str | Path) -> sqlite3.Connection`
- `initialize(conn: sqlite3.Connection) -> None`
- `table_names(conn: sqlite3.Connection) -> set[str]`

Use `PRAGMA foreign_keys = ON`.

- [ ] **Step 4: Run schema tests**

Run:

```bash
python3 -m unittest tests.test_instagram_corpus_db -v
```

Expected: all tests pass.

## Task 3: Immutable Raw Store

**Files:**

- Create: `scripts/instagram_corpus/raw_store.py`
- Test: `tests/test_instagram_corpus_raw_store.py`

- [ ] **Step 1: Write raw-store tests**

The test writes a sample JSON payload and asserts:

- payload bytes are stored under `raw/{provider}/{run_id}/`
- SHA-256 is stable
- returned metadata includes `raw_object_id`, `local_path`, `sha256`, `captured_at`, `provider`, `source_url`
- `Authorization`, `Cookie`, `x-access-key`, and token query parameters are not written to metadata

- [ ] **Step 2: Run test and confirm failure**

Run:

```bash
python3 -m unittest tests.test_instagram_corpus_raw_store -v
```

Expected: import failure.

- [ ] **Step 3: Implement `write_raw_object`**

Signature:

```python
def write_raw_object(
    root: Path,
    provider: str,
    run_id: str,
    object_type: str,
    source_url: str,
    payload: bytes,
    request_url: str | None = None,
    response_status: int | None = None,
) -> dict:
    ...
```

The payload filename should include object type plus SHA prefix. The metadata filename should be the same stem with `.meta.json`.

- [ ] **Step 4: Run raw-store tests**

Run:

```bash
python3 -m unittest tests.test_instagram_corpus_raw_store -v
```

Expected: all tests pass.

## Task 4: Seed Importer For Existing 715/170 Records

**Files:**

- Create: `scripts/instagram_corpus/seed_import.py`
- Test: `tests/test_instagram_corpus_seed_import.py`
- Fixture: `tests/fixtures/instagram_corpus/winner_seed_minimal.json`

- [ ] **Step 1: Write fixture**

Fixture includes one sidecar and one reel seed record using existing winner-bank field names:

```json
[
  {
    "shortCode": "DUtQzmaj9Rw",
    "url": "https://www.instagram.com/p/DUtQzmaj9Rw/",
    "ownerUsername": "source_account",
    "ownerFullName": "Source Account",
    "type": "Sidecar",
    "productType": null,
    "caption": "fixture caption",
    "likesCount": 163284,
    "commentsCount": 528,
    "videoViewCount": 0,
    "videoPlayCount": 0,
    "childCount": 10,
    "displayUrl": "https://example.test/display.jpg",
    "timestamp": "2026-01-01T00:00:00.000Z",
    "winnerScore": 200000
  }
]
```

- [ ] **Step 2: Write importer tests**

Assert importer creates:

- one account
- one post
- one snapshot
- `childCount` asset slots
- one `metric_observations` row each for likes and comments
- gap rows for `saves`, `shares`, `child_media_urls`, `ocr`, and `visual_notes`

- [ ] **Step 3: Run test and confirm failure**

Run:

```bash
python3 -m unittest tests.test_instagram_corpus_seed_import -v
```

Expected: import failure.

- [ ] **Step 4: Implement importer**

Expose:

```python
def import_winner_seed(conn: sqlite3.Connection, seed_path: Path, run_id: str) -> dict:
    ...
```

Return a manifest dict:

```json
{
  "run_id": "seed_2026_06_18",
  "posts": 1,
  "accounts": 1,
  "assets": 10,
  "gaps": 5
}
```

- [ ] **Step 5: Run importer tests**

Run:

```bash
python3 -m unittest tests.test_instagram_corpus_seed_import -v
```

Expected: all tests pass.

## Task 5: Provider Adapter Contract

**Files:**

- Create: `scripts/instagram_corpus/providers/base.py`
- Create: `scripts/instagram_corpus/providers/manual_json.py`
- Test: `tests/test_instagram_corpus_providers.py`
- Fixtures: `tests/fixtures/instagram_corpus/brightdata_post_carousel.json`, `tests/fixtures/instagram_corpus/apify_post_reel.json`

- [ ] **Step 1: Write provider contract tests**

Tests should assert the normalized provider result shape:

```python
{
    "source_url": "https://www.instagram.com/p/DUtQzmaj9Rw/",
    "shortcode": "DUtQzmaj9Rw",
    "caption": "fixture caption",
    "metrics": {"likes": 163284, "comments": 528, "views": None, "plays": None},
    "content_type": "Carousel",
    "children": [
        {"index": 0, "type": "Photo", "url": "https://example.test/slide-1.jpg"}
    ],
    "raw": {"provider": "manual_json"}
}
```

- [ ] **Step 2: Run provider tests and confirm failure**

Run:

```bash
python3 -m unittest tests.test_instagram_corpus_providers -v
```

Expected: import failure.

- [ ] **Step 3: Implement base classes**

Use dataclasses:

- `ProviderChild`
- `ProviderPost`
- `ProviderError`

Use a simple abstract base class:

```python
class InstagramProvider:
    provider_name: str
    def fetch_post_by_url(self, url: str) -> ProviderPost:
        raise NotImplementedError
```

- [ ] **Step 4: Implement manual JSON adapter**

It reads fixture/provider JSON from disk and converts Bright Data-like or Apify-like fields into the normalized result.

- [ ] **Step 5: Run provider tests**

Run:

```bash
python3 -m unittest tests.test_instagram_corpus_providers -v
```

Expected: all tests pass.

## Task 6: Bright Data Adapter

**Files:**

- Create: `scripts/instagram_corpus/providers/brightdata.py`
- Modify: `tests/test_instagram_corpus_providers.py`

- [ ] **Step 1: Add no-network tests**

Tests must use a fake HTTP callable and assert:

- request uses `BRIGHTDATA_TOKEN`
- request URL contains dataset ID `gd_lk5ns7kz21pck8jpis`
- token value is not present in returned raw metadata
- response fields `photos`, `videos`, `post_content`, `likes`, `num_comments`, `shortcode`, `content_type` are normalized

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
python3 -m unittest tests.test_instagram_corpus_providers -v
```

Expected: Bright Data tests fail because adapter is missing.

- [ ] **Step 3: Implement adapter**

Expose:

```python
class BrightDataProvider(InstagramProvider):
    def __init__(self, token: str, http_post=None):
        ...
```

Do not read `.env` inside the provider. The CLI injects the token.

- [ ] **Step 4: Run provider tests**

Run:

```bash
python3 -m unittest tests.test_instagram_corpus_providers -v
```

Expected: all tests pass.

## Task 7: Apify Adapter

**Files:**

- Create: `scripts/instagram_corpus/providers/apify.py`
- Modify: `tests/test_instagram_corpus_providers.py`

- [ ] **Step 1: Add no-network tests**

Tests must use a fake HTTP callable and assert:

- request uses `APIFY_TOKEN`
- actor name is configurable and defaults to `apify/instagram-post-scraper`
- token value is not present in returned raw metadata
- post/reel fields normalize into `ProviderPost`

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
python3 -m unittest tests.test_instagram_corpus_providers -v
```

Expected: Apify tests fail because adapter is missing.

- [ ] **Step 3: Implement adapter**

Expose:

```python
class ApifyProvider(InstagramProvider):
    def __init__(self, token: str, actor: str = "apify/instagram-post-scraper", http_post=None):
        ...
```

- [ ] **Step 4: Run provider tests**

Run:

```bash
python3 -m unittest tests.test_instagram_corpus_providers -v
```

Expected: all tests pass.

## Task 8: Media Download And Hash Store

**Files:**

- Create: `scripts/instagram_corpus/media.py`
- Test: `tests/test_instagram_corpus_media.py`

- [ ] **Step 1: Write media tests**

Use a fake downloader that returns bytes and headers. Assert:

- file path is content-addressed under `media/sha256/{aa}/`
- sidecar JSON includes source URL, SHA-256, MIME, bytes, variant, and raw object ID
- duplicate content returns same path without duplicate bytes

- [ ] **Step 2: Run media tests and confirm failure**

Run:

```bash
python3 -m unittest tests.test_instagram_corpus_media -v
```

Expected: import failure.

- [ ] **Step 3: Implement media store**

Expose:

```python
def store_media(
    root: Path,
    source_url: str,
    content: bytes,
    mime: str,
    raw_object_id: str,
    variant: str = "original",
) -> dict:
    ...
```

Infer extension from MIME for `image/jpeg`, `image/png`, `video/mp4`; otherwise use `.bin`.

- [ ] **Step 4: Run media tests**

Run:

```bash
python3 -m unittest tests.test_instagram_corpus_media -v
```

Expected: all tests pass.

## Task 9: OCR Interface With Fixture-First Results

**Files:**

- Create: `scripts/instagram_corpus/ocr.py`
- Test: `tests/test_instagram_corpus_ocr.py`

- [ ] **Step 1: Write OCR tests**

Tests should cover:

- accepted OCR output with lines, boxes, and mean confidence
- `needs_review` when mean confidence is below threshold
- `failed` when engine returns no text for an asset marked likely text
- VLM fallback result is marked `confidence_calibrated=False`

- [ ] **Step 2: Run OCR tests and confirm failure**

Run:

```bash
python3 -m unittest tests.test_instagram_corpus_ocr -v
```

Expected: import failure.

- [ ] **Step 3: Implement engine-agnostic result model**

Use dataclasses:

- `OcrLine`
- `OcrResult`
- `OcrEngine`
- `FixtureOcrEngine`

Do not add PaddleOCR/RapidOCR dependency in this task. Add only the interface and fixture engine.

- [ ] **Step 4: Run OCR tests**

Run:

```bash
python3 -m unittest tests.test_instagram_corpus_ocr -v
```

Expected: all tests pass.

## Task 10: RAG Exporter

**Files:**

- Create: `scripts/instagram_corpus/export_rag.py`
- Test: `tests/test_instagram_corpus_export_rag.py`

- [ ] **Step 1: Write exporter tests**

Given an in-memory catalog with one post, two assets, one OCR result, and explicit gaps, exporter writes:

- `posts.jsonl`
- `assets.jsonl`
- `chunks.jsonl`
- `gaps.jsonl`

Assert every JSON line has:

- stable ID
- source URL
- evidence raw object IDs or gap IDs
- rights scope
- no missing required fields

- [ ] **Step 2: Run exporter tests and confirm failure**

Run:

```bash
python3 -m unittest tests.test_instagram_corpus_export_rag -v
```

Expected: import failure.

- [ ] **Step 3: Implement exporter**

Expose:

```python
def export_rag(conn: sqlite3.Connection, output_dir: Path) -> dict:
    ...
```

Return counts:

```json
{"posts": 1, "assets": 2, "chunks": 3, "gaps": 4}
```

- [ ] **Step 4: Run exporter tests**

Run:

```bash
python3 -m unittest tests.test_instagram_corpus_export_rag -v
```

Expected: all tests pass.

## Task 11: Validation Gates

**Files:**

- Create: `scripts/instagram_corpus/validate.py`
- Test: `tests/test_instagram_corpus_validate.py`

- [ ] **Step 1: Write validation tests**

Tests should fail fixtures for:

- raw object without SHA-256
- post without raw evidence or explicit gap
- third-party `shares` metric without provider evidence
- RAG chunk with no evidence IDs
- missing carousel child with no gap row

Tests should pass a complete minimal catalog.

- [ ] **Step 2: Run validation tests and confirm failure**

Run:

```bash
python3 -m unittest tests.test_instagram_corpus_validate -v
```

Expected: import failure.

- [ ] **Step 3: Implement validator**

Expose:

```python
def validate_catalog(conn: sqlite3.Connection, corpus_root: Path) -> list[dict]:
    ...
```

Each finding shape:

```json
{
  "severity": "error",
  "gate": "metric",
  "message": "third-party shares metric requires provider evidence",
  "target": "ig_DUtQzmaj9Rw"
}
```

- [ ] **Step 4: Run validation tests**

Run:

```bash
python3 -m unittest tests.test_instagram_corpus_validate -v
```

Expected: all tests pass.

## Task 12: CLI

**Files:**

- Create: `scripts/instagram_corpus_cli.py`
- Modify tests as needed with subprocess-free direct function tests if the repo prefers direct imports.

- [ ] **Step 1: Add CLI tests**

Test these commands through a `main(argv)` function:

```bash
init --db /tmp/corpus.sqlite
import-seed --db /tmp/corpus.sqlite --seed references/text-style/winner-bank/winner_bank.json --run-id seed_top_170
export-rag --db /tmp/corpus.sqlite --out /tmp/rag
validate --db /tmp/corpus.sqlite --root /tmp/corpus
```

- [ ] **Step 2: Run CLI tests and confirm failure**

Run:

```bash
python3 -m unittest tests.test_instagram_corpus_cli -v
```

Expected: CLI test fails because module is missing.

- [ ] **Step 3: Implement CLI**

Commands:

- `init`
- `import-seed`
- `ingest-url`
- `download-media`
- `run-ocr`
- `export-rag`
- `validate`

Provider tokens are read only in CLI command handlers:

- `BRIGHTDATA_TOKEN`
- `APIFY_TOKEN`
- `HIKER_TOKEN` when a Hiker adapter is added later

Never print token values.

- [ ] **Step 4: Run CLI tests**

Run:

```bash
python3 -m unittest tests.test_instagram_corpus_cli -v
```

Expected: all tests pass.

## Task 13: Integration Pilot

**Files:**

- Create runtime files under `data/instagram-corpus/`
- Do not commit runtime payloads unless the user explicitly asks.

- [ ] **Step 1: Build a 20 URL pilot list**

Include:

```text
https://www.instagram.com/p/DUtQzmaj9Rw/
```

Add 19 top-ranked URLs from `references/text-style/winner-bank/winner_bank.json` with this mix:

- at least 10 carousels
- at least 5 reels/videos
- at least 3 single images

- [ ] **Step 2: Run seed import**

Run:

```bash
python3 scripts/instagram_corpus_cli.py init --db data/instagram-corpus/corpus.sqlite
python3 scripts/instagram_corpus_cli.py import-seed \
  --db data/instagram-corpus/corpus.sqlite \
  --seed references/text-style/winner-bank/winner_bank.json \
  --run-id seed_top_170
```

Expected: manifest reports 170 posts imported and explicit gaps for missing child URLs/OCR/visual notes.

- [ ] **Step 3: Run provider acquisition on pilot**

Bright Data path:

```bash
python3 scripts/instagram_corpus_cli.py ingest-url \
  --db data/instagram-corpus/corpus.sqlite \
  --root data/instagram-corpus \
  --provider brightdata \
  --run-id brightdata_pilot_001 \
  --url https://www.instagram.com/p/DUtQzmaj9Rw/
```

Expected: raw payload stored, normalized provider post attached, and no token appears in raw metadata.

- [ ] **Step 4: Validate pilot**

Run:

```bash
python3 scripts/instagram_corpus_cli.py validate \
  --db data/instagram-corpus/corpus.sqlite \
  --root data/instagram-corpus
```

Expected: no critical raw/provenance errors; known gaps remain for unavailable third-party saves/shares.

## Task 14: Scale Run

**Files:**

- Runtime only unless user asks to commit artifacts.

- [ ] **Step 1: Scale to top 170**

Run provider ingestion for all top-170 URLs only after the pilot child-media gate passes.

Acceptance:

- 170 normalized posts.
- 100 percent raw payload hash coverage.
- 90 percent or better child media coverage for carousel assets, or explicit provider gap rows.
- RAG export line counts match DB counts.

- [ ] **Step 2: Scale to full 715**

Run after top 170 passes.

Acceptance:

- 715 normalized posts.
- no orphan assets
- no orphan RAG chunks
- no third-party saves/shares unless provider-supplied
- validation output has zero `error` findings

## Task 15: Adversarial Review

**Files:**

- No direct edits required.

- [ ] **Step 1: Spawn reviewer**

Prompt a fresh reviewer with:

```text
Review the Instagram Evidence Bank V2 implementation against docs/superpowers/specs/2026-06-18-instagram-evidence-bank-v2-design.md and docs/superpowers/plans/2026-06-18-instagram-evidence-bank-v2.md. Report only correctness, provenance, security, compliance, data-loss, and test-coverage gaps. Ignore style preferences.
```

- [ ] **Step 2: Fix valid findings**

Only fix findings that affect correctness, requirements, provenance, security, compliance, or tests.

- [ ] **Step 3: Final verification**

Run:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/instagram_corpus_cli.py validate --db data/instagram-corpus/corpus.sqlite --root data/instagram-corpus
```

Expected: unit tests pass and validator returns zero `error` findings.

## Completion Criteria

The project is ready only when:

- A pilot has run against `DUtQzmaj9Rw` and 19 mixed winner-bank posts.
- Raw payloads are stored and hashed.
- Carousel child media is either downloaded or explicitly gapped.
- Each slide has OCR status.
- RAG exports are generated from SQLite, not handwritten loose files.
- Validation finds no provenance or metric errors.
- A fresh adversarial review has no unresolved correctness findings.
