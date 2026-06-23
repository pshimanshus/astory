# Research Bank Normalization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a normalized A Story research bank from the existing 715-post scrape, with one stable ID per post, metrics, linked assets, slide placeholders, communication analysis, visual classification, and explicit extraction gaps.

**Architecture:** Add a pure Python builder that reads the existing scraped JSON and first-party carousel exports, enriches records with local slide assets where available, and writes JSON plus Markdown reports under `references/text-style/research-bank/`. The first slice is local-data complete; a later scraper/OCR slice can fill the gaps it exposes.

**Tech Stack:** Python standard library, `PIL` when available for lightweight local-image visual classification, `unittest`.

---

## File Map

| Path | Responsibility |
| --- | --- |
| `scripts/research_bank_builder.py` | Load raw scraped posts, enrich first-party metrics/assets, normalize records, classify local visual assets, and write reports. |
| `tests/test_research_bank_builder.py` | Unit tests for stable IDs, metric availability/gaps, first-party insight enrichment, sidecar slide placeholders, local asset detection, and report writing. |
| `references/text-style/research-bank/research_bank.json` | Generated normalized post bank. |
| `references/text-style/research-bank/research_bank_summary.md` | Generated human-readable summary of counts, top posts, and extraction gaps. |

## Task 1: Builder API And Schema

**Files:**
- Create: `tests/test_research_bank_builder.py`
- Create: `scripts/research_bank_builder.py`

- [ ] **Step 1: Write failing tests for schema shape**

Create tests that build a temporary repo with:

```json
[
  {
    "ownerUsername": "wetheurban",
    "ownerFullName": "WE THE URBAN",
    "url": "https://www.instagram.com/p/AAA/",
    "shortCode": "AAA",
    "type": "Sidecar",
    "caption": "The little things are often the biggest things.",
    "likesCount": 100,
    "commentsCount": 5,
    "videoViewCount": 0,
    "videoPlayCount": 0,
    "childCount": 3,
    "childTypes": ["Image", "Image", "Image"],
    "displayUrl": "https://cdn.example/aaa.jpg",
    "mechanicTags": ["carousel", "direct_you", "first_person"],
    "winnerScore": 120
  },
  {
    "ownerUsername": "werenotreallystrangers",
    "ownerFullName": "We Are Not Really Strangers",
    "url": "https://www.instagram.com/p/BBB/",
    "shortCode": "BBB",
    "type": "Video",
    "caption": "made me think",
    "likesCount": 50,
    "commentsCount": 2,
    "videoViewCount": 1000,
    "videoPlayCount": 2000,
    "childCount": 0,
    "childTypes": [],
    "displayUrl": "https://cdn.example/bbb.jpg",
    "mechanicTags": ["reel", "first_person"],
    "winnerScore": 80
  }
]
```

Assert:
- IDs are `ig:wetheurban:AAA` and `ig:werenotreallystrangers:BBB`.
- Sidecar record has three slide entries.
- Slide 2 and slide 3 explicitly state that child URLs are missing.
- Third-party records expose `saves`, `shares`, and `reach` as unavailable gaps.
- Video record is classified as `reel_video`.

- [ ] **Step 2: Run schema tests and confirm RED**

Run:

```bash
python3 -m unittest tests/test_research_bank_builder.py -v
```

Expected: import failure for `scripts.research_bank_builder`.

- [ ] **Step 3: Implement minimal builder API**

Create:

```python
def build_research_bank(repo_root: Path, source_path: Path | None = None) -> dict:
    ...
```

Return:

```json
{
  "schema_version": "1.0",
  "source_paths": [],
  "summary": {},
  "records": []
}
```

Each record includes:

```json
{
  "id": "ig:<account>:<shortcode>",
  "source": {},
  "metrics": {},
  "metrics_gaps": [],
  "post": {},
  "communication": {},
  "slides": [],
  "record_gaps": []
}
```

- [ ] **Step 4: Run tests and confirm GREEN**

Run:

```bash
python3 -m unittest tests/test_research_bank_builder.py -v
```

Expected: all current tests pass.

## Task 2: First-Party Enrichment And Local Assets

**Files:**
- Modify: `tests/test_research_bank_builder.py`
- Modify: `scripts/research_bank_builder.py`

- [ ] **Step 1: Write failing test for first-party insights**

Create a temp `data/instagram/carousel_posts/AAA/carousel_export.json` with `insights.available.shares`, `saved`, `reach`, and `views`, plus two child media items. Create `.carousel_research/AAA_00.jpg` as a small plain white image.

Assert:
- Metrics include `shares`, `saves`, `reach`, `views`, and `metric_source == "first_party_graph_export"`.
- Slide 1 has `local_asset_path == ".carousel_research/AAA_00.jpg"`.
- Slide 1 visual classification says `likely_text_only_minimal_visuals` or an explicit local asset classification.

- [ ] **Step 2: Run test and confirm RED**

Run:

```bash
python3 -m unittest tests/test_research_bank_builder.py -v
```

Expected: failing assertion because first-party enrichment is not implemented.

- [ ] **Step 3: Implement enrichment**

Add helpers:

```python
def _load_first_party_exports(repo_root: Path) -> dict[str, dict]:
    ...

def _local_slide_assets(repo_root: Path) -> dict[str, dict[int, str]]:
    ...

def _classify_local_image(path: Path) -> dict:
    ...
```

Use first-party exports only for matching shortcodes. Do not overwrite third-party public metrics with absent values.

- [ ] **Step 4: Run tests and confirm GREEN**

Run:

```bash
python3 -m unittest tests/test_research_bank_builder.py -v
```

Expected: all tests pass.

## Task 3: Report Writing

**Files:**
- Modify: `tests/test_research_bank_builder.py`
- Modify: `scripts/research_bank_builder.py`

- [ ] **Step 1: Write failing test for output files**

Assert `write_research_bank(repo_root, output_dir)` writes:
- `research_bank.json`
- `research_bank_summary.md`

Assert the Markdown includes:
- total record count;
- format counts;
- extraction gaps;
- top posts table.

- [ ] **Step 2: Run test and confirm RED**

Run:

```bash
python3 -m unittest tests/test_research_bank_builder.py -v
```

Expected: failing import or missing function/file assertion.

- [ ] **Step 3: Implement report writing and CLI**

Add:

```python
def write_research_bank(repo_root: Path, output_dir: Path) -> dict[str, str]:
    ...
```

CLI:

```bash
python3 scripts/research_bank_builder.py --repo-root . --output-dir references/text-style/research-bank
```

- [ ] **Step 4: Run tests and confirm GREEN**

Run:

```bash
python3 -m unittest tests/test_research_bank_builder.py -v
```

Expected: all tests pass.

## Task 4: Generate Current Bank

**Files:**
- Generate: `references/text-style/research-bank/research_bank.json`
- Generate: `references/text-style/research-bank/research_bank_summary.md`

- [ ] **Step 1: Run builder on the repo**

Run:

```bash
python3 scripts/research_bank_builder.py --repo-root . --output-dir references/text-style/research-bank
```

Expected: JSON output with generated artifact paths.

- [ ] **Step 2: Verify counts**

Run:

```bash
python3 - <<'PY'
import json
from pathlib import Path
bank = json.loads(Path("references/text-style/research-bank/research_bank.json").read_text())
print(bank["summary"])
PY
```

Expected:
- `total_records` is 715.
- `format_counts` includes 297 `carousel`, 187 `reel_video`, and 231 `static_image`.
- Gap counts explicitly report missing child URLs/OCR for third-party carousels.

## Task 5: Next Scrape/OCR Contract

**Files:**
- Generate or update: `references/text-style/research-bank/research_bank_summary.md`

- [ ] **Step 1: Document what cannot be completed from current raw data**

The summary must explicitly say:
- third-party saves/shares/reach are unavailable unless the scrape/API source provides them;
- most third-party carousel child slide URLs are absent in the current raw scrape;
- OCR is not available in the local environment yet;
- full slide text requires a richer child-asset scrape plus OCR/manual transcription.

- [ ] **Step 2: Verify the summary states those gaps**

Run:

```bash
rg -n "child slide URLs|OCR|saves|shares|third-party" references/text-style/research-bank/research_bank_summary.md
```

Expected: all four gap categories are present.

