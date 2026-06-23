# Instagram Evidence Bank V2 Ultracode Operating Plan

**Date:** 2026-06-18

**Purpose:** Execute the Instagram Evidence Bank V2 build with an Anthropic-style multi-agent operating loop: explore, plan, implement in bounded lanes, verify with runnable tests, and use fresh-context adversarial review before calling any slice complete.

## Source Operating Principles

Anthropic's Claude Code guidance maps cleanly onto this repo:

- Give the agent runnable verification, not vibes. The gate here is `python3 -m unittest ...` plus corpus validation.
- Explore first, then plan, then code. The design and implementation plan already exist under `docs/superpowers/`.
- Use subagents where parallel exploration or bounded ownership adds value.
- Test on a small pilot before scaling to the full corpus.
- Add an adversarial review step before completion.

References:

- https://code.claude.com/docs/en/best-practices
- https://code.claude.com/docs/en/agent-teams
- https://claude.com/blog/how-anthropic-teams-use-claude-code

## In-House Agent Roles

All agents act as Idris, the Principal Engineer: skeptical, evidence-first, allergic to generic implementation, and unwilling to claim success without tests.

### Coordinator

Owns:

- plan integrity
- file ownership boundaries
- integration
- final verification
- adversarial review prompt

Refuses:

- raw browser-first scraping as the primary path
- uncited RAG chunks
- unverified "done"
- touching unrelated dirty worktree files

### Acquisition Worker

Owns:

- `scripts/instagram_corpus/providers/*`
- provider fixtures
- token redaction tests

Method:

- test provider normalization first
- no real network in unit tests
- Bright Data and Apify adapters accept injectable HTTP callables

### Catalog Worker

Owns:

- `scripts/instagram_corpus/schema.py`
- `scripts/instagram_corpus/db.py`
- `scripts/instagram_corpus/seed_import.py`
- catalog tests

Method:

- SQLite schema first
- seed import from existing 715/170 winner bank
- explicit gaps for unavailable saves/shares, child media, OCR, visual notes

### Media/OCR Worker

Owns:

- `scripts/instagram_corpus/media.py`
- `scripts/instagram_corpus/ocr.py`
- media and OCR tests

Method:

- content-addressed media store
- fixture OCR interface first
- no heavy OCR dependency until the interface and tests are stable

### Export/Validation Worker

Owns:

- `scripts/instagram_corpus/export_rag.py`
- `scripts/instagram_corpus/validate.py`
- `scripts/instagram_corpus_cli.py`
- export and validation tests

Method:

- derive RAG exports from SQLite only
- enforce evidence IDs or explicit gap IDs
- fail third-party saves/shares without provider evidence

### Adversarial Reviewer

Owns:

- fresh-context review after implementation

Review scope:

- correctness
- provenance
- security/token leakage
- compliance boundaries
- test coverage
- whether `DUtQzmaj9Rw` pilot is actually supported

## Execution Slice 1

Build the local, no-network core:

1. Stable IDs.
2. SQLite schema.
3. Immutable raw store.
4. Seed importer.
5. Provider contracts with fake HTTP.
6. Media hash store.
7. OCR interface with fixture engine.
8. RAG exporter.
9. Validator.
10. CLI shell.

This slice deliberately does not run real Bright Data/Apify requests. As of
2026-06-18, real Bright Data/Apify token-backed ingestion is unavailable for this
project; the adapters are normalization code paths with fixtures, not an active
acquisition channel. Use local winner-bank dumps, owned-account Instagram Graph
API pulls, and explicit gaps for missing third-party fields until a fresh auth
probe and pilot scrape prove otherwise.

## Verification Gates

Targeted unit gate:

```bash
python3 -m unittest tests.test_instagram_corpus_ids tests.test_instagram_corpus_db tests.test_instagram_corpus_raw_store tests.test_instagram_corpus_seed_import tests.test_instagram_corpus_providers tests.test_instagram_corpus_media tests.test_instagram_corpus_ocr tests.test_instagram_corpus_export_rag tests.test_instagram_corpus_validate tests.test_instagram_corpus_cli -v
```

Existing related regression gate:

```bash
python3 -m unittest tests.test_instagram_content_dump tests.test_research_bank_builder tests.test_instagram_winner_bank_artifacts -v
```

Full suite gate before broad completion:

```bash
python3 -m unittest discover -s tests -v
```

## Scale Gate

Only after Slice 1 is green:

1. Import the existing `winner_bank.json`.
2. Build 20-post pilot list, force-including `DUtQzmaj9Rw`.
3. Use local winner-bank dumps plus owned-account Instagram Graph API. Treat
   Bright Data/Apify as unavailable unless a fresh token auth probe and pilot
   scrape pass in the current session.
4. Validate raw evidence and child media coverage.
5. Scale to top 170.
6. Scale to full 715.

## Non-Negotiables

- No token value in raw metadata, logs, JSONL, tests, or failure output.
- No third-party saves/shares unless provider-supplied and evidenced.
- No RAG chunk without evidence IDs or explicit gaps.
- No browser automation as primary acquisition.
- No claim of completion without fresh command output.
