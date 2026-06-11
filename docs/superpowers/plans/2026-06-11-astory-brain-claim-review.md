# A Story Brain Claim Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a governed claim-review and promotion loop so extracted memory can safely become future `/astory` behavior without letting raw, rejected, or high-risk claims become accidental truth.

**Architecture:** Keep run claim files as evidence snapshots, keep `references/brain/ledger/events.jsonl` as the append-only lifecycle record, and compute current claim state from claim snapshot plus ledger. Raw candidate queues are review input only; future recall should use only active runtime notes and promoted canonical brain pages.

**Tech Stack:** Python standard library, existing `scripts/astory_brain/*` modules, `unittest`, Markdown brain pages, JSON/JSONL artifacts.

---

## Why This Change Exists

The current learning pipeline extracts useful claims, but the next reliability gap is lifecycle control:

- `learn --write` currently rewrites `references/brain/ledger/events.jsonl`; a memory ledger must be append-only and idempotent.
- `runs/<run_id>/memory/claim_candidates.json` is currently indexable, which risks candidate or quarantined text showing up as future recall truth.
- There is no CLI for the creator/Codex to list open claims, promote safe claims, reject false claims, defer uncertain claims, or quarantine dangerous ones.
- There is no deterministic bridge from reviewed claim to canonical brain page.

This matches the architecture direction from MemGPT-style managed memory, Reflexion-style post-run learning, and modern write/manage/read memory framing:

- MemGPT: https://arxiv.org/abs/2310.08560
- Reflexion: https://arxiv.org/abs/2303.11366
- LLM agent memory survey: https://arxiv.org/abs/2404.13501

## File Structure

- Modify `scripts/astory_brain/models.py`
  - Add `rejected` to `ClaimStatus`.
  - Add `MemoryClaimRecord` and `ClaimDecision` dataclasses if the implementation needs typed current-state rows.

- Modify `scripts/astory_brain/learning.py`
  - Make ledger writes append-only and idempotent.
  - Write `runs/<run_id>/memory/active_claims.md` for auto-apply claims only.

- Create `scripts/astory_brain/claim_store.py`
  - Load claim snapshots from `runs/*/memory/claim_candidates.json`.
  - Load ledger events from `references/brain/ledger/events.jsonl`.
  - Compute current claim status.
  - Validate lifecycle transitions.
  - Append review events without deleting prior events.

- Create `scripts/astory_brain/promotion.py`
  - Route promoted claims to the correct canonical brain page.
  - Append cited Current Truth bullets and Timeline/Evidence bullets.
  - Preserve existing frontmatter and compiled-page separators.

- Modify `scripts/astory_brain/source_scan.py`
  - Stop indexing raw `claim_candidates.json`.
  - Index `memory/active_claims.md` only for runtime auto-apply memory.
  - Let promoted claims enter recall through `references/brain/pages/*`.

- Modify `scripts/astory_brain_cli.py`
  - Add `claims list`.
  - Add `claims decide`.
  - Update `doctor` to use `claim_store` summaries instead of directly reading raw summaries.

- Modify `.agents/skills/astory/SKILL.md`
  - Require `claims list` during `MEMORY_RECALL_PREFLIGHT`.
  - Require `learn --write` plus claim review after meaningful eval/approval evidence.
  - State that raw candidate queues are not recall truth.

- Modify `references/brain/README.md`
  - Document lifecycle states, review commands, and promotion rules.

- Create `tests/test_astory_brain_claim_review.py`
  - Cover ledger idempotence, claim listing, decisions, page promotion, and recall filtering.

- Update `tests/test_astory_brain_learning.py`
  - Expect active runtime notes for auto-apply claims.
  - Stop expecting `claim_candidates.json` to be the future recall surface.

- Update `tests/test_astory_brain_synthesis.py`
  - Prove quarantined/rejected candidates are not presented as usable recall truth.

---

### Task 1: Make Ledger Writes Append-Only And Idempotent

**Files:**
- Modify: `scripts/astory_brain/learning.py`
- Test: `tests/test_astory_brain_learning.py`

- [ ] **Step 1: Write the failing ledger durability test**

Add this test to `tests/test_astory_brain_learning.py`:

```python
    def test_learn_write_preserves_existing_ledger_events_and_dedupes_new_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_minimal_repo(root)

            ledger = root / "references/brain/ledger/events.jsonl"
            ledger.parent.mkdir(parents=True, exist_ok=True)
            preserved_event = {
                "event_id": "event:manual-review",
                "claim_id": "claim:manual",
                "run_id": RUN_ID,
                "action": "review_decision",
                "from_status": "candidate",
                "to_status": "deferred",
                "promotion_policy": "human_review",
                "evidence_paths": [f"runs/{RUN_ID}/docs/approvals.md"],
                "rationale": "Manual decision must survive later learning writes.",
            }
            ledger.write_text(json.dumps(preserved_event, sort_keys=True) + "\n", encoding="utf-8")

            report = extract_learning_report(root, RUN_ID)
            write_learning_artifacts(root, report)
            write_learning_artifacts(root, report)

            events = [
                json.loads(line)
                for line in ledger.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            event_ids = [event["event_id"] for event in events]

            self.assertIn("event:manual-review", event_ids)
            self.assertEqual(len(event_ids), len(set(event_ids)))
            self.assertEqual(
                sum(event["action"] == "candidate_created" for event in events),
                len(report.claims),
            )
```

- [ ] **Step 2: Run the failing test**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_brain_learning.AStoryBrainLearningTests.test_learn_write_preserves_existing_ledger_events_and_dedupes_new_events -v
```

Expected: fail because `write_learning_artifacts()` currently replaces the ledger file.

- [ ] **Step 3: Implement idempotent ledger merge**

In `scripts/astory_brain/learning.py`, replace the direct `ledger_jsonl.write_text(...)` call with a helper:

```python
def _write_ledger_events(ledger_jsonl: Path, events: list[MemoryLedgerEvent]) -> None:
    existing_rows = _read_jsonl_lines(ledger_jsonl)
    seen = {
        str(row.get("event_id"))
        for row in existing_rows
        if isinstance(row, dict) and row.get("event_id")
    }
    merged_rows = list(existing_rows)
    for event in events:
        row = asdict(event)
        if row["event_id"] in seen:
            continue
        merged_rows.append(row)
        seen.add(row["event_id"])
    ledger_jsonl.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in merged_rows),
        encoding="utf-8",
    )


def _read_jsonl_lines(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows
```

Then call:

```python
    events = [_event_for_claim(claim) for claim in report.claims]
    _write_ledger_events(ledger_jsonl, events)
```

- [ ] **Step 4: Run the durability test again**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_brain_learning.AStoryBrainLearningTests.test_learn_write_preserves_existing_ledger_events_and_dedupes_new_events -v
```

Expected: pass.

---

### Task 2: Split Review Queue From Runtime Recall

**Files:**
- Modify: `scripts/astory_brain/learning.py`
- Modify: `scripts/astory_brain/source_scan.py`
- Test: `tests/test_astory_brain_learning.py`

- [ ] **Step 1: Write the failing active-claims test**

Replace the current `test_learning_claims_are_indexable_for_future_recall` expectation with this behavior:

```python
    def test_only_active_claims_are_indexable_for_future_recall(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_minimal_repo(root)
            report = extract_learning_report(root, RUN_ID)
            write_learning_artifacts(root, report)

            index = root / "references/brain/index"
            build_index(root, index, include_runs=[RUN_ID])
            results = recall(
                index,
                "prompt only generation forbidden view image references",
                run_id=RUN_ID,
                limit=10,
            )

            paths = {result.chunk.path for result in results}
            self.assertIn(f"runs/{RUN_ID}/memory/active_claims.md", paths)
            self.assertNotIn(f"runs/{RUN_ID}/memory/claim_candidates.json", paths)
```

Add this second test to prove quarantined/review-only text is not a runtime truth surface:

```python
    def test_quarantined_claim_candidates_are_not_runtime_recall_truth(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_minimal_repo(root)
            report = extract_learning_report(root, RUN_ID)
            write_learning_artifacts(root, report)

            index = root / "references/brain/index"
            build_index(root, index, include_runs=[RUN_ID])
            results = recall(
                index,
                "rejected export style anchor final artwork",
                run_id=RUN_ID,
                limit=10,
            )

            paths = {result.chunk.path for result in results}
            self.assertNotIn(f"runs/{RUN_ID}/memory/claim_candidates.json", paths)
```

- [ ] **Step 2: Run the failing tests**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_brain_learning.AStoryBrainLearningTests.test_only_active_claims_are_indexable_for_future_recall tests.test_astory_brain_learning.AStoryBrainLearningTests.test_quarantined_claim_candidates_are_not_runtime_recall_truth -v
```

Expected: fail because raw candidate JSON is currently indexed and `active_claims.md` is not written.

- [ ] **Step 3: Write active runtime claims**

In `scripts/astory_brain/learning.py`, add:

```python
def _render_active_claims_markdown(report: LearningReport) -> str:
    active_claims = [
        claim
        for claim in report.claims
        if claim.promotion_policy == "auto_apply" and claim.status == "candidate"
    ]
    lines = [
        "# Active Runtime Memory Claims",
        "",
        f"Run: `{report.run_id}`",
        "",
        "These claims may guide workflow behavior, but they are not canonical brain page truth.",
        "",
    ]
    if not active_claims:
        lines.append("- No active runtime claims.")
        return "\n".join(lines) + "\n"
    for claim in active_claims:
        evidence = ", ".join(f"`{path}`" for path in claim.evidence_paths)
        lines.extend(
            [
                f"- `{claim.claim_id}`: {claim.text} Evidence: {evidence}",
            ]
        )
    return "\n".join(lines) + "\n"
```

Then in `write_learning_artifacts()` write:

```python
    active_claims = run_memory_dir / "active_claims.md"
    active_claims.write_text(_render_active_claims_markdown(report), encoding="utf-8")
```

Return it in artifacts:

```python
        "active_claims_markdown": _rel(active_claims, root),
```

- [ ] **Step 4: Exclude raw queues from source scanning**

In `scripts/astory_brain/source_scan.py`, add:

```python
EXCLUDED_FILENAMES = {
    "claim_candidates.json",
    "claim_candidates.md",
}
```

Then update `_iter_text_files()`:

```python
        if path.name in EXCLUDED_FILENAMES:
            continue
```

- [ ] **Step 5: Run the active-claims tests again**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_brain_learning.AStoryBrainLearningTests.test_only_active_claims_are_indexable_for_future_recall tests.test_astory_brain_learning.AStoryBrainLearningTests.test_quarantined_claim_candidates_are_not_runtime_recall_truth -v
```

Expected: pass.

---

### Task 3: Add Claim Store And Lifecycle State Resolution

**Files:**
- Create: `scripts/astory_brain/claim_store.py`
- Modify: `scripts/astory_brain/models.py`
- Test: `tests/test_astory_brain_claim_review.py`

- [ ] **Step 1: Add claim lifecycle tests**

Create `tests/test_astory_brain_claim_review.py`:

```python
import json
import tempfile
import unittest
from pathlib import Path

from scripts.astory_brain.claim_store import (
    apply_claim_decision,
    load_claim_records,
    summarize_claim_records,
)
from scripts.astory_brain.learning import extract_learning_report, write_learning_artifacts

from tests.test_astory_brain_learning import REPO_ROOT, RUN_ID, _copy_minimal_repo


class AStoryBrainClaimReviewTests(unittest.TestCase):
    def test_load_claim_records_marks_auto_apply_as_active_runtime(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_minimal_repo(root)
            report = extract_learning_report(root, RUN_ID)
            write_learning_artifacts(root, report)

            records = load_claim_records(root)
            auto_records = [
                record
                for record in records
                if record.claim.promotion_policy == "auto_apply"
            ]

            self.assertTrue(auto_records)
            self.assertTrue(
                all(record.effective_status == "active_runtime" for record in auto_records)
            )

    def test_apply_claim_decision_appends_review_event_and_updates_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_minimal_repo(root)
            report = extract_learning_report(root, RUN_ID)
            write_learning_artifacts(root, report)
            claim_id = next(
                claim.claim_id
                for claim in report.claims
                if claim.promotion_policy == "human_review"
            )

            decision = apply_claim_decision(
                root,
                claim_id=claim_id,
                decision="defer",
                reason="Need another approved run before turning this into canonical identity memory.",
                reviewer="codex",
            )

            self.assertEqual(decision["to_status"], "deferred")
            records = load_claim_records(root)
            reviewed = next(record for record in records if record.claim.claim_id == claim_id)
            self.assertEqual(reviewed.effective_status, "deferred")

            ledger = root / "references/brain/ledger/events.jsonl"
            events = [
                json.loads(line)
                for line in ledger.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertTrue(
                any(
                    event["claim_id"] == claim_id
                    and event["action"] == "review_decision"
                    and event["to_status"] == "deferred"
                    for event in events
                )
            )

    def test_summarize_claim_records_separates_active_and_open_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_minimal_repo(root)
            report = extract_learning_report(root, RUN_ID)
            write_learning_artifacts(root, report)

            summary = summarize_claim_records(load_claim_records(root))

            self.assertGreaterEqual(summary["active_runtime"], 1)
            self.assertGreaterEqual(summary["open_human_review"], 1)
            self.assertGreaterEqual(summary["quarantined"], 1)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the failing claim-store tests**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_brain_claim_review -v
```

Expected: fail because `claim_store.py` does not exist.

- [ ] **Step 3: Add rejected status**

In `scripts/astory_brain/models.py`, change:

```python
ClaimStatus = Literal["candidate", "quarantined", "promoted", "deferred"]
```

to:

```python
ClaimStatus = Literal["candidate", "quarantined", "promoted", "deferred", "rejected"]
```

- [ ] **Step 4: Implement claim store**

Create `scripts/astory_brain/claim_store.py`:

```python
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from .models import MemoryClaim


Decision = Literal["promote", "reject", "defer", "quarantine"]


@dataclass(frozen=True)
class MemoryClaimRecord:
    claim: MemoryClaim
    effective_status: str
    latest_event: dict[str, Any] | None


def load_claim_records(repo_root: str | Path) -> list[MemoryClaimRecord]:
    root = Path(repo_root).resolve()
    claims = _load_claims(root)
    events = _load_events(root)
    latest_by_claim = _latest_events(events)
    records: list[MemoryClaimRecord] = []
    for claim in sorted(claims, key=lambda item: item.claim_id):
        latest = latest_by_claim.get(claim.claim_id)
        status = _effective_status(claim, latest)
        records.append(MemoryClaimRecord(claim=claim, effective_status=status, latest_event=latest))
    return records


def summarize_claim_records(records: list[MemoryClaimRecord]) -> dict[str, int]:
    summary = {
        "total": len(records),
        "active_runtime": 0,
        "open_human_review": 0,
        "open_quarantine_review": 0,
        "promoted": 0,
        "deferred": 0,
        "rejected": 0,
        "quarantined": 0,
    }
    for record in records:
        status = record.effective_status
        summary[status] = summary.get(status, 0) + 1
        if status == "candidate" and record.claim.promotion_policy == "human_review":
            summary["open_human_review"] += 1
        if status == "quarantined" or record.claim.promotion_policy == "quarantine":
            summary["open_quarantine_review"] += 1
    return summary


def apply_claim_decision(
    repo_root: str | Path,
    *,
    claim_id: str,
    decision: Decision,
    reason: str,
    reviewer: str = "codex",
    target_page: str | None = None,
) -> dict[str, Any]:
    if not reason.strip():
        raise ValueError("Claim review reason is required.")
    root = Path(repo_root).resolve()
    records = load_claim_records(root)
    record = next((item for item in records if item.claim.claim_id == claim_id), None)
    if record is None:
        raise ValueError(f"Unknown claim_id: {claim_id}")
    to_status = {
        "promote": "promoted",
        "reject": "rejected",
        "defer": "deferred",
        "quarantine": "quarantined",
    }[decision]
    if decision == "promote" and not target_page:
        raise ValueError("Promote decisions require --target-page.")
    if target_page and not target_page.startswith("references/brain/pages/"):
        raise ValueError("target_page must be under references/brain/pages/.")
    event = {
        "event_id": "event:" + _stable_hash("|".join([claim_id, decision, reason, target_page or ""])),
        "claim_id": claim_id,
        "run_id": record.claim.run_id,
        "action": "review_decision",
        "from_status": record.effective_status,
        "to_status": to_status,
        "promotion_policy": record.claim.promotion_policy,
        "evidence_paths": record.claim.evidence_paths,
        "rationale": reason.strip(),
        "reviewer": reviewer,
        "reviewed_at": datetime.now(timezone.utc).isoformat(),
        "target_page": target_page,
    }
    _append_event(root / "references/brain/ledger/events.jsonl", event)
    return event


def _load_claims(root: Path) -> list[MemoryClaim]:
    claims: list[MemoryClaim] = []
    for path in sorted((root / "runs").glob("*/memory/claim_candidates.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        for row in payload.get("claims") or []:
            if isinstance(row, dict):
                claims.append(MemoryClaim(**row))
    return claims


def _load_events(root: Path) -> list[dict[str, Any]]:
    path = root / "references/brain/ledger/events.jsonl"
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            events.append(row)
    return events


def _latest_events(events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for event in events:
        claim_id = str(event.get("claim_id") or "")
        if not claim_id:
            continue
        latest[claim_id] = event
    return latest


def _effective_status(claim: MemoryClaim, latest: dict[str, Any] | None) -> str:
    if latest and latest.get("action") == "review_decision":
        return str(latest.get("to_status") or claim.status)
    if claim.status == "candidate" and claim.promotion_policy == "auto_apply":
        return "active_runtime"
    return claim.status


def _append_event(path: Path, event: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    if path.exists():
        existing = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    event_line = json.dumps(event, sort_keys=True)
    if event_line not in existing:
        existing.append(event_line)
    path.write_text("\n".join(existing) + "\n", encoding="utf-8")


def _stable_hash(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:16]
```

- [ ] **Step 5: Run claim-store tests again**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_brain_claim_review -v
```

Expected: pass.

---

### Task 4: Promote Reviewed Claims Into Canonical Brain Pages

**Files:**
- Create: `scripts/astory_brain/promotion.py`
- Modify: `scripts/astory_brain/claim_store.py`
- Test: `tests/test_astory_brain_claim_review.py`

- [ ] **Step 1: Add a promotion test**

Add this test to `tests/test_astory_brain_claim_review.py`:

```python
    def test_promote_claim_writes_cited_current_truth_to_target_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_minimal_repo(root)
            report = extract_learning_report(root, RUN_ID)
            write_learning_artifacts(root, report)
            claim = next(
                claim
                for claim in report.claims
                if claim.claim_type == "creator_preference"
                and claim.scope == "aachu_identity"
            )

            event = apply_claim_decision(
                root,
                claim_id=claim.claim_id,
                decision="promote",
                reason="Creator feedback is explicit and should shape future Aachu identity QA.",
                reviewer="codex",
                target_page="references/brain/pages/characters/aachu.md",
            )

            page = root / "references/brain/pages/characters/aachu.md"
            text = page.read_text(encoding="utf-8")
            self.assertEqual(event["to_status"], "promoted")
            self.assertIn(claim.claim_id, text)
            self.assertIn("Creator rejected an output where Aachu looked old", text)
            self.assertIn(f"`runs/{RUN_ID}/evals/image_quality_eval.json`", text)
```

- [ ] **Step 2: Run the failing promotion test**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_brain_claim_review.AStoryBrainClaimReviewTests.test_promote_claim_writes_cited_current_truth_to_target_page -v
```

Expected: fail because promotion does not write to the target page.

- [ ] **Step 3: Implement page promotion**

Create `scripts/astory_brain/promotion.py`:

```python
from __future__ import annotations

from pathlib import Path

from .models import MemoryClaim
from .page_store import split_frontmatter


def promote_claim_to_page(repo_root: str | Path, claim: MemoryClaim, target_page: str) -> None:
    root = Path(repo_root).resolve()
    page_path = root / target_page
    if not page_path.exists():
        raise ValueError(f"Target page does not exist: {target_page}")
    text = page_path.read_text(encoding="utf-8")
    if claim.claim_id in text:
        return
    frontmatter, body = split_frontmatter(text)
    body = _insert_current_truth_bullet(body, claim)
    body = _insert_timeline_bullet(body, claim)
    if frontmatter:
        rendered = text[: text.find("\n---\n") + len("\n---\n")] + body
    else:
        rendered = body
    page_path.write_text(rendered.rstrip() + "\n", encoding="utf-8")


def _insert_current_truth_bullet(body: str, claim: MemoryClaim) -> str:
    evidence = ", ".join(f"`{path}`" for path in claim.evidence_paths)
    bullet = f"- `{claim.claim_id}`: {claim.text} Evidence: {evidence}."
    if "# Current Truth" not in body or "\n---\n" not in body:
        raise ValueError("Target page must be a compiled brain page.")
    current, timeline = body.split("\n---\n", 1)
    current = current.rstrip() + "\n" + bullet + "\n"
    return current + "\n---\n" + timeline


def _insert_timeline_bullet(body: str, claim: MemoryClaim) -> str:
    evidence = claim.evidence_paths[0] if claim.evidence_paths else f"runs/{claim.run_id}/memory/claim_candidates.json"
    bullet = f"- {claim.run_id[:10]} | `{evidence}` | Promoted memory claim `{claim.claim_id}`."
    current, timeline = body.split("\n---\n", 1)
    timeline = timeline.rstrip() + "\n" + bullet + "\n"
    return current + "\n---\n" + timeline
```

Then in `scripts/astory_brain/claim_store.py`, after `_append_event(...)` in `apply_claim_decision()`:

```python
    if decision == "promote" and target_page:
        from .promotion import promote_claim_to_page

        promote_claim_to_page(root, record.claim, target_page)
```

- [ ] **Step 4: Run promotion and lint tests**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_brain_claim_review.AStoryBrainClaimReviewTests.test_promote_claim_writes_cited_current_truth_to_target_page tests.test_astory_brain_lint -v
```

Expected: pass.

---

### Task 5: Add `claims list` And `claims decide` CLI

**Files:**
- Modify: `scripts/astory_brain_cli.py`
- Test: `tests/test_astory_brain_claim_review.py`

- [ ] **Step 1: Add CLI tests**

Add these tests to `tests/test_astory_brain_claim_review.py`:

```python
    def test_cli_claims_list_outputs_open_review_queue(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_minimal_repo(root)
            report = extract_learning_report(root, RUN_ID)
            write_learning_artifacts(root, report)

            output = subprocess.check_output(
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts/astory_brain_cli.py"),
                    "claims",
                    "list",
                    "--repo-root",
                    str(root),
                    "--status",
                    "open",
                    "--json",
                ],
                text=True,
            )

            payload = json.loads(output)
            self.assertEqual(payload["status"], "ok")
            self.assertGreaterEqual(payload["summary"]["open_human_review"], 1)
            self.assertTrue(payload["claims"])

    def test_cli_claims_decide_defers_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_minimal_repo(root)
            report = extract_learning_report(root, RUN_ID)
            write_learning_artifacts(root, report)
            claim_id = next(
                claim.claim_id
                for claim in report.claims
                if claim.promotion_policy == "human_review"
            )

            output = subprocess.check_output(
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts/astory_brain_cli.py"),
                    "claims",
                    "decide",
                    "--repo-root",
                    str(root),
                    "--claim-id",
                    claim_id,
                    "--decision",
                    "defer",
                    "--reason",
                    "Need one more run before promoting this preference.",
                ],
                text=True,
            )

            payload = json.loads(output)
            self.assertEqual(payload["status"], "decision_recorded")
            self.assertEqual(payload["event"]["to_status"], "deferred")
```

Also add imports at the top:

```python
import subprocess
import sys
```

- [ ] **Step 2: Run the failing CLI tests**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_brain_claim_review.AStoryBrainClaimReviewTests.test_cli_claims_list_outputs_open_review_queue tests.test_astory_brain_claim_review.AStoryBrainClaimReviewTests.test_cli_claims_decide_defers_claim -v
```

Expected: fail because the CLI command does not exist.

- [ ] **Step 3: Add CLI subcommands**

In `scripts/astory_brain_cli.py`, import:

```python
from astory_brain.claim_store import (
    apply_claim_decision,
    load_claim_records,
    summarize_claim_records,
)
```

and mirror it in the relative import branch.

Add parser setup:

```python
    claims_parser = subparsers.add_parser("claims")
    claims_subparsers = claims_parser.add_subparsers(dest="claims_command", required=True)

    claims_list_parser = claims_subparsers.add_parser("list")
    claims_list_parser.add_argument("--repo-root", default=".")
    claims_list_parser.add_argument("--status", default="open")
    claims_list_parser.add_argument("--json", action="store_true")

    claims_decide_parser = claims_subparsers.add_parser("decide")
    claims_decide_parser.add_argument("--repo-root", default=".")
    claims_decide_parser.add_argument("--claim-id", required=True)
    claims_decide_parser.add_argument("--decision", choices=["promote", "reject", "defer", "quarantine"], required=True)
    claims_decide_parser.add_argument("--reason", required=True)
    claims_decide_parser.add_argument("--reviewer", default="codex")
    claims_decide_parser.add_argument("--target-page")
```

Add command handling:

```python
    if args.command == "claims":
        if args.claims_command == "list":
            records = load_claim_records(args.repo_root)
            filtered = _filter_claim_records(records, args.status)
            payload = {
                "status": "ok",
                "summary": summarize_claim_records(records),
                "claims": [_claim_record_payload(record) for record in filtered],
            }
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(_render_claim_list(payload))
            return 0
        if args.claims_command == "decide":
            event = apply_claim_decision(
                args.repo_root,
                claim_id=args.claim_id,
                decision=args.decision,
                reason=args.reason,
                reviewer=args.reviewer,
                target_page=args.target_page,
            )
            print(json.dumps({"status": "decision_recorded", "event": event}, indent=2, sort_keys=True))
            return 0
```

Add helpers:

```python
def _filter_claim_records(records, status: str):
    if status == "all":
        return records
    if status == "open":
        return [
            record
            for record in records
            if record.effective_status in {"candidate", "quarantined"}
            and record.claim.promotion_policy in {"human_review", "quarantine"}
        ]
    return [record for record in records if record.effective_status == status]


def _claim_record_payload(record):
    return {
        "claim_id": record.claim.claim_id,
        "run_id": record.claim.run_id,
        "claim_type": record.claim.claim_type,
        "text": record.claim.text,
        "evidence_paths": record.claim.evidence_paths,
        "confidence": record.claim.confidence,
        "scope": record.claim.scope,
        "risk_level": record.claim.risk_level,
        "promotion_policy": record.claim.promotion_policy,
        "source_status": record.claim.status,
        "effective_status": record.effective_status,
        "applies_to": record.claim.applies_to,
        "rationale": record.claim.rationale,
    }


def _render_claim_list(payload: dict) -> str:
    lines = ["# Memory Claims", ""]
    lines.append(json.dumps(payload["summary"], indent=2, sort_keys=True))
    lines.append("")
    for claim in payload["claims"]:
        lines.extend(
            [
                f"## `{claim['claim_id']}`",
                "",
                f"- Status: `{claim['effective_status']}`",
                f"- Policy: `{claim['promotion_policy']}`",
                f"- Risk: `{claim['risk_level']}`",
                "",
                claim["text"],
                "",
            ]
        )
    return "\n".join(lines)
```

- [ ] **Step 4: Run CLI tests again**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_brain_claim_review.AStoryBrainClaimReviewTests.test_cli_claims_list_outputs_open_review_queue tests.test_astory_brain_claim_review.AStoryBrainClaimReviewTests.test_cli_claims_decide_defers_claim -v
```

Expected: pass.

---

### Task 6: Make Doctor Use The Claim Store

**Files:**
- Modify: `scripts/astory_brain_cli.py`
- Test: `tests/test_astory_brain_learning.py`

- [ ] **Step 1: Update doctor expectations**

Update `test_doctor_reports_open_claim_review_queue_after_learning` to assert the richer summary:

```python
            self.assertIn("Learning pipeline status: `operational_with_review_queue`", output)
            self.assertIn("## Memory Claim Review Queue", output)
            self.assertEqual(
                doctor_json["learning_pipeline_status"],
                "operational_with_review_queue",
            )
            self.assertGreaterEqual(doctor_json["claim_review_queue"]["active_runtime"], 1)
            self.assertGreaterEqual(doctor_json["claim_review_queue"]["open_human_review"], 1)
            self.assertGreaterEqual(doctor_json["claim_review_queue"]["open_quarantine_review"], 1)
```

- [ ] **Step 2: Run the failing doctor test**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_brain_learning.AStoryBrainLearningTests.test_doctor_reports_open_claim_review_queue_after_learning -v
```

Expected: fail until doctor uses `claim_store`.

- [ ] **Step 3: Replace raw summary loading in doctor**

In `scripts/astory_brain_cli.py`, update `_learning_pipeline_status()` to use:

```python
def _learning_pipeline_status(root: Path, required_runs: list[str]) -> dict:
    from astory_brain.claim_store import load_claim_records, summarize_claim_records

    missing_runs: list[str] = []
    for run_id in required_runs or []:
        claims_path = root / "runs" / run_id / "memory/claim_candidates.json"
        if not claims_path.exists():
            missing_runs.append(run_id)

    records = [
        record
        for record in load_claim_records(root)
        if not required_runs or record.claim.run_id in set(required_runs)
    ]
    summary = summarize_claim_records(records)

    if missing_runs:
        status = "needs_extraction"
    elif summary.get("open_human_review", 0) or summary.get("open_quarantine_review", 0):
        status = "operational_with_review_queue"
    else:
        status = "ready"
    return {
        "status": status,
        "claim_review_queue": summary,
        "missing_learning_runs": missing_runs,
    }
```

If relative imports are needed when the CLI is invoked as a module, move the `claim_store` imports to the existing import branch instead of importing inside this function.

- [ ] **Step 4: Run doctor tests again**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_brain_learning.AStoryBrainLearningTests.test_doctor_reports_open_claim_review_queue_after_learning tests.test_astory_brain_synthesis.AStoryBrainCliTests.test_doctor_reports_brain_setup_scope_not_run_gate_scope -v
```

Expected: pass.

---

### Task 7: Wire The Workflow Docs And Skill Contract

**Files:**
- Modify: `.agents/skills/astory/SKILL.md`
- Modify: `references/brain/README.md`

- [ ] **Step 1: Update the `/astory` Brain Recall Gate**

In `.agents/skills/astory/SKILL.md`, under `## Brain Recall Gate`, add these rules:

```markdown
- Raw `runs/<run_id>/memory/claim_candidates.*` files are review queues, not
  production recall truth. Runtime recall should use `memory/active_claims.md`
  for auto-apply claims and canonical `references/brain/pages/*` for promoted
  claims.
- Use `python3 scripts/astory_brain_cli.py claims list --repo-root . --status open`
  after `learn --write` to surface human-review and quarantine decisions.
- Use `python3 scripts/astory_brain_cli.py claims decide --repo-root . --claim-id <claim_id> --decision promote|reject|defer|quarantine --reason "<reason>"`
  for claim lifecycle decisions. Promotion also requires
  `--target-page references/brain/pages/<page>.md`.
- Do not promote identity, style, or creator-preference claims unless they cite
  local run evidence and the target page passes brain lint afterward.
```

- [ ] **Step 2: Update brain README lifecycle docs**

In `references/brain/README.md`, add:

```markdown
## Claim Lifecycle

Learning writes claim snapshots into `runs/<run_id>/memory/claim_candidates.*`.
Those files are evidence queues. They are not canonical truth.

Effective claim states:

- `active_runtime`: auto-apply claim available to workflow behavior through
  `runs/<run_id>/memory/active_claims.md`.
- `candidate`: human-review claim waiting for a decision.
- `promoted`: reviewed claim written into `references/brain/pages/*`.
- `deferred`: reviewed claim intentionally held for more evidence.
- `rejected`: reviewed claim rejected as false, weak, or no longer useful.
- `quarantined`: claim must not influence generation except as an explicit
  warning/failure mode.

Use:

```bash
python3 scripts/astory_brain_cli.py claims list --repo-root . --status open
python3 scripts/astory_brain_cli.py claims decide --repo-root . --claim-id claim:<id> --decision defer --reason "Need another approved run."
python3 scripts/astory_brain_cli.py claims decide --repo-root . --claim-id claim:<id> --decision promote --target-page references/brain/pages/run-lessons.md --reason "Explicit creator-approved workflow lesson."
```
```

- [ ] **Step 3: Run doc-sensitive tests**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_brain_lint tests.test_astory_brain_synthesis -v
```

Expected: pass.

---

### Task 8: Full Verification

**Files:**
- No new code files.

- [ ] **Step 1: Run the full unit suite**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

Expected: all tests pass.

- [ ] **Step 2: Run brain lint**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/astory_brain_cli.py lint --repo-root .
```

Expected:

```json
{
  "failures": [],
  "status": "pass"
}
```

- [ ] **Step 3: Run brain doctor**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/astory_brain_cli.py doctor --repo-root .
```

Expected:

```text
Brain setup status: `operational_with_review_queue`
Runtime status: `ready`
Learning pipeline status: `operational_with_review_queue`
```

- [ ] **Step 4: Prove open claims are visible**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/astory_brain_cli.py claims list --repo-root . --status open --json
```

Expected:

```json
{
  "status": "ok",
  "summary": {
    "open_human_review": 2
  }
}
```

The exact total can vary if more runs have learned claims, but open human-review claims must be visible and not hidden behind the doctor summary.

## Self-Review

- Spec coverage: The plan covers ledger durability, queue/runtime separation, lifecycle state, review CLI, canonical promotion, doctor reporting, docs, and verification.
- Placeholder scan: No `TBD`, `TODO`, or hand-wavy implementation steps remain.
- Type consistency: The plan uses `MemoryClaimRecord`, `effective_status`, `apply_claim_decision`, `load_claim_records`, and `summarize_claim_records` consistently across tests, CLI, and implementation.
- Risk check: The plan intentionally prevents raw candidate files from becoming recall truth and requires cited canonical pages for promoted high-risk claims.
