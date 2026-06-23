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
    decision_events = _decision_events_by_claim(_load_events(root))
    records: list[MemoryClaimRecord] = []
    for claim in sorted(_load_claims(root), key=lambda item: item.claim_id):
        latest = decision_events.get(claim.claim_id)
        records.append(
            MemoryClaimRecord(
                claim=claim,
                effective_status=_effective_status(claim, latest),
                latest_event=latest,
            )
        )
    return records


def summarize_claim_records(records: list[MemoryClaimRecord]) -> dict[str, int]:
    summary = {
        "total": len(records),
        "active_runtime": 0,
        "open_human_review": 0,
        "open_quarantine_review": 0,
        "candidate": 0,
        "promoted": 0,
        "deferred": 0,
        "rejected": 0,
        "quarantined": 0,
    }
    for record in records:
        status = record.effective_status
        summary[status] = summary.get(status, 0) + 1
        if (
            record.claim.promotion_policy == "human_review"
            and status == "candidate"
            and record.latest_event is None
        ):
            summary["open_human_review"] += 1
        if (
            record.claim.promotion_policy == "quarantine"
            and status == "quarantined"
            and record.latest_event is None
        ):
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
    record = _record_for_claim(root, claim_id)
    to_status = {
        "promote": "promoted",
        "reject": "rejected",
        "defer": "deferred",
        "quarantine": "quarantined",
    }[decision]
    if decision == "promote":
        if not target_page:
            raise ValueError("Promote decisions require --target-page.")
        if not target_page.startswith("references/brain/pages/"):
            raise ValueError("target_page must be under references/brain/pages/.")
        from .promotion import promote_claim_to_page

        promote_claim_to_page(root, record.claim, target_page)
    event = build_claim_event(
        record,
        action="review_decision",
        to_status=to_status,
        reason=reason,
        reviewer=reviewer,
        target_page=target_page,
    )
    append_claim_event(root, event)
    return event


def append_claim_event(repo_root: str | Path, event: dict[str, Any]) -> None:
    root = Path(repo_root).resolve()
    path = root / "references/brain/ledger/events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = _load_events(root)
    event_ids = {str(row.get("event_id")) for row in rows if row.get("event_id")}
    if event["event_id"] not in event_ids:
        rows.append(event)
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def build_claim_event(
    record: MemoryClaimRecord,
    *,
    action: str,
    to_status: str,
    reason: str,
    reviewer: str = "codex-autopilot",
    target_page: str | None = None,
) -> dict[str, Any]:
    return {
        "event_id": "event:"
        + _stable_hash(
            "|".join(
                [
                    record.claim.claim_id,
                    action,
                    to_status,
                    reason.strip(),
                    target_page or "",
                ]
            )
        ),
        "claim_id": record.claim.claim_id,
        "run_id": record.claim.run_id,
        "action": action,
        "from_status": record.effective_status,
        "to_status": to_status,
        "promotion_policy": record.claim.promotion_policy,
        "evidence_paths": record.claim.evidence_paths,
        "rationale": reason.strip(),
        "reviewer": reviewer,
        "reviewed_at": datetime.now(timezone.utc).isoformat(),
        "target_page": target_page,
    }


def _record_for_claim(root: Path, claim_id: str) -> MemoryClaimRecord:
    record = next(
        (item for item in load_claim_records(root) if item.claim.claim_id == claim_id),
        None,
    )
    if record is None:
        raise ValueError(f"Unknown claim_id: {claim_id}")
    return record


def _load_claims(root: Path) -> list[MemoryClaim]:
    claims: list[MemoryClaim] = []
    runs_root = root / "runs"
    if not runs_root.exists():
        return claims
    for path in sorted(runs_root.glob("*/memory/claim_candidates.json")):
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


def _decision_events_by_claim(events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    decisions: dict[str, dict[str, Any]] = {}
    for event in events:
        action = str(event.get("action") or "")
        if action == "candidate_created":
            continue
        claim_id = str(event.get("claim_id") or "")
        if claim_id:
            decisions[claim_id] = event
    return decisions


def _effective_status(claim: MemoryClaim, decision_event: dict[str, Any] | None) -> str:
    if decision_event:
        return str(decision_event.get("to_status") or claim.status)
    if claim.status == "candidate" and claim.promotion_policy == "auto_apply":
        return "active_runtime"
    return claim.status


def _stable_hash(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:16]
