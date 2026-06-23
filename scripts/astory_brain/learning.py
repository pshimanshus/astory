from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .models import LearningReport, MemoryClaim, MemoryLedgerEvent


def extract_learning_report(repo_root: str | Path, run_id: str) -> LearningReport:
    root = Path(repo_root).resolve()
    run_root = root / "runs" / run_id
    claims: list[MemoryClaim] = []

    image_qa_path = run_root / "evals/image_quality_eval.json"
    image_qa = _read_json(image_qa_path)
    candidates = image_qa.get("candidates_reviewed", [])
    if not isinstance(candidates, list):
        candidates = []
    approvals_path = run_root / "docs/approvals.md"
    approvals = _read_text(approvals_path)
    selected_refs_path = run_root / "references-used/selected_references.json"
    selected_refs = _read_json(selected_refs_path)

    if selected_refs.get("prompt_only_allowed") is False and selected_refs.get("view_image_queue_count"):
        claims.append(
            _claim(
                run_id=run_id,
                claim_type="production_constraint",
                text=(
                    "Final Aachu/Zuv imagegen for this run requires loading the "
                    "queued local reference images with view_image; prompt-only "
                    "generation is forbidden."
                ),
                evidence_paths=[_rel(selected_refs_path, root)],
                confidence=0.96,
                scope="run",
                risk_level="medium",
                promotion_policy="auto_apply",
                status="candidate",
                applies_to=["imagegen", "reference_visibility"],
                rationale="Selected reference manifest explicitly forbids prompt-only generation.",
            )
        )

    accepted_name_rejections = [
        item
        for item in candidates
        if "accepted_candidate" in str(item.get("path", ""))
        and str(item.get("status", "")).startswith("rejected")
    ]
    if accepted_name_rejections:
        claims.append(
            _claim(
                run_id=run_id,
                claim_type="failure_mode",
                text=(
                    "A filename containing accepted_candidate is not final acceptance "
                    "proof; final status must come from explicit image QA and creator "
                    "approval evidence."
                ),
                evidence_paths=[_rel(image_qa_path, root)],
                confidence=0.98,
                scope="workflow",
                risk_level="low",
                promotion_policy="auto_apply",
                status="candidate",
                applies_to=["image_qa", "final_package"],
                rationale="Image QA records accepted_candidate files rejected after creator review.",
            )
        )

    rejected_aachu_age = image_qa.get("qa_checklist", {}).get(
        "creator_rejected_aachu_age"
    ) or _candidate_has_failure(candidates, "AACHU_AGE_DRIFT")
    if rejected_aachu_age:
        evidence = [_rel(image_qa_path, root)]
        if approvals:
            evidence.append(_rel(approvals_path, root))
        claims.append(
            _claim(
                run_id=run_id,
                claim_type="creator_preference",
                text=(
                    "Creator rejected an output where Aachu looked old; future "
                    "retries for this concept must preserve youthful Aachu face "
                    "identity from the approved anchors."
                ),
                evidence_paths=evidence,
                confidence=0.93,
                scope="aachu_identity",
                risk_level="high",
                promotion_policy="human_review",
                status="candidate",
                applies_to=["aachu", "identity", "image_qa"],
                rationale="Creator feedback and QA checklist both mark Aachu age drift as rejected.",
            )
        )

    rejected_couple_energy = image_qa.get("qa_checklist", {}).get(
        "creator_rejected_couple_energy"
    ) or _candidate_has_failure(candidates, "COUPLE_ENERGY_MISSING")
    if rejected_couple_energy:
        evidence = [_rel(image_qa_path, root)]
        if approvals:
            evidence.append(_rel(approvals_path, root))
        claims.append(
            _claim(
                run_id=run_id,
                claim_type="creator_preference",
                text=(
                    "Creator rejected a retry where couple energy was missing; "
                    "future retries for this concept need visible closeness, shared "
                    "attention, and affectionate body language."
                ),
                evidence_paths=evidence,
                confidence=0.93,
                scope="relationship_direction",
                risk_level="high",
                promotion_policy="human_review",
                status="candidate",
                applies_to=["together", "body_language", "image_qa"],
                rationale="Creator feedback and QA checklist both mark missing couple energy as rejected.",
            )
        )

    export = (
        image_qa.get("export")
        or image_qa.get("rejected_export")
        if isinstance(image_qa, dict)
        else None
    )
    if isinstance(export, dict) and str(export.get("status", "")).startswith("rejected"):
        export_path = export.get("path")
        text = "Rejected exports must not be promoted as final artwork or style anchors."
        if export_path:
            text = f"Rejected export `{export_path}` must not be promoted as final artwork or a style anchor."
        claims.append(
            _claim(
                run_id=run_id,
                claim_type="failure_mode",
                text=text,
                evidence_paths=[_rel(image_qa_path, root)],
                confidence=0.97,
                scope="asset_governance",
                risk_level="medium",
                promotion_policy="quarantine",
                status="quarantined",
                applies_to=["exports", "final_package", "style"],
                rationale="Image QA marks the export rejected after creator review.",
            )
        )

    return LearningReport(run_id=run_id, claims=_dedupe_claims(claims), summary={})


def write_learning_artifacts(repo_root: str | Path, report: LearningReport) -> dict[str, str]:
    root = Path(repo_root).resolve()
    run_memory_dir = root / "runs" / report.run_id / "memory"
    ledger_dir = root / "references/brain/ledger"
    run_memory_dir.mkdir(parents=True, exist_ok=True)
    ledger_dir.mkdir(parents=True, exist_ok=True)

    claims_json = run_memory_dir / "claim_candidates.json"
    claims_markdown = run_memory_dir / "claim_candidates.md"
    active_claims = run_memory_dir / "active_claims.md"
    ledger_jsonl = ledger_dir / "events.jsonl"

    payload = {
        "schema_version": "1.0",
        "run_id": report.run_id,
        "summary": _summary(report.claims),
        "claims": [asdict(claim) for claim in report.claims],
    }
    claims_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    claims_markdown.write_text(_render_claims_markdown(report), encoding="utf-8")
    active_claims.write_text(_render_active_claims_markdown(report), encoding="utf-8")

    events = [_event_for_claim(claim) for claim in report.claims]
    _write_ledger_events(ledger_jsonl, events)
    return {
        "claims_json": _rel(claims_json, root),
        "claims_markdown": _rel(claims_markdown, root),
        "active_claims_markdown": _rel(active_claims, root),
        "ledger_jsonl": _rel(ledger_jsonl, root),
    }


def _claim(
    *,
    run_id: str,
    claim_type,
    text: str,
    evidence_paths: list[str],
    confidence: float,
    scope: str,
    risk_level,
    promotion_policy,
    status,
    applies_to: list[str],
    rationale: str,
) -> MemoryClaim:
    normalized_evidence = sorted(dict.fromkeys(evidence_paths))
    claim_id = "claim:" + _stable_hash(
        "|".join([run_id, claim_type, text, *normalized_evidence])
    )
    return MemoryClaim(
        claim_id=claim_id,
        run_id=run_id,
        claim_type=claim_type,
        text=text,
        evidence_paths=normalized_evidence,
        confidence=confidence,
        scope=scope,
        risk_level=risk_level,
        promotion_policy=promotion_policy,
        status=status,
        applies_to=applies_to,
        rationale=rationale,
    )


def _event_for_claim(claim: MemoryClaim) -> MemoryLedgerEvent:
    event_id = "event:" + _stable_hash(
        "|".join([claim.claim_id, claim.status, claim.promotion_policy])
    )
    return MemoryLedgerEvent(
        event_id=event_id,
        claim_id=claim.claim_id,
        run_id=claim.run_id,
        action="candidate_created",
        from_status=None,
        to_status=claim.status,
        promotion_policy=claim.promotion_policy,
        evidence_paths=claim.evidence_paths,
        rationale=claim.rationale,
    )


def _summary(claims: list[MemoryClaim]) -> dict[str, int]:
    summary = {
        "total": len(claims),
        "auto_apply": 0,
        "human_review": 0,
        "quarantine": 0,
        "quarantined": 0,
    }
    for claim in claims:
        summary[claim.promotion_policy] = summary.get(claim.promotion_policy, 0) + 1
        summary[claim.status] = summary.get(claim.status, 0) + 1
    return summary


def _candidate_has_failure(candidates: list[Any], failure_code: str) -> bool:
    for item in candidates:
        if not isinstance(item, dict):
            continue
        codes = item.get("failure_codes") or []
        if isinstance(codes, list) and failure_code in codes:
            return True
    return False


def _render_claims_markdown(report: LearningReport) -> str:
    lines = [
        "# Memory Claim Candidates",
        "",
        f"Run: `{report.run_id}`",
        "",
    ]
    for claim in report.claims:
        evidence = ", ".join(f"`{path}`" for path in claim.evidence_paths)
        lines.extend(
            [
                f"## `{claim.claim_id}`",
                "",
                f"- Type: `{claim.claim_type}`",
                f"- Status: `{claim.status}`",
                f"- Promotion policy: `{claim.promotion_policy}`",
                f"- Risk: `{claim.risk_level}`",
                f"- Confidence: `{claim.confidence:.2f}`",
                f"- Evidence: {evidence}",
                "",
                claim.text,
                "",
            ]
        )
    return "\n".join(lines)


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
        lines.append(f"- `{claim.claim_id}`: {claim.text} Evidence: {evidence}.")
    return "\n".join(lines) + "\n"


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


def _dedupe_claims(claims: list[MemoryClaim]) -> list[MemoryClaim]:
    by_id = {claim.claim_id: claim for claim in claims}
    return [by_id[key] for key in sorted(by_id)]


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _stable_hash(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:16]


def _rel(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root).as_posix()
