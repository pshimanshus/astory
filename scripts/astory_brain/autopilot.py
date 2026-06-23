from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .claim_store import (
    append_claim_event,
    build_claim_event,
    load_claim_records,
    summarize_claim_records,
)
from .eval import run_retrieval_eval
from .indexer import build_index
from .learning import extract_learning_report, write_learning_artifacts
from .lint import lint_brain
from .policy import load_memory_autopilot_policy
from .promotion import promote_claim_to_page


POST_RUN_PHASES = {"post_run", "write_reports"}


def run_memory_autopilot(
    repo_root: str | Path,
    run_id: str,
    *,
    phase: str = "post_run",
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    if phase == "pre_imagegen":
        return {
            "schema_version": "1.0",
            "status": "skipped_pre_imagegen",
            "run_id": run_id,
            "phase": phase,
            "heavy_verification_ran": False,
            "human_intervention_required": False,
            "reason": "Memory autopilot does not run learning, promotion, or retrieval eval before illustration generation.",
        }
    if phase not in POST_RUN_PHASES:
        raise ValueError(f"Unsupported memory autopilot phase: {phase}")

    learning = extract_learning_report(root, run_id)
    learning_artifacts = write_learning_artifacts(root, learning)
    policy = load_memory_autopilot_policy(root)
    records = [
        record
        for record in load_claim_records(root)
        if record.claim.run_id == run_id
    ]

    decision_summary = {
        "auto_promoted": 0,
        "auto_deferred": 0,
        "auto_quarantined": 0,
        "auto_rollback": 0,
        "kept_active_runtime": 0,
        "skipped_already_decided": 0,
    }
    decisions: list[dict[str, Any]] = []
    page_backups: dict[str, str] = {}
    promoted_records: list[tuple[Any, str]] = []

    for record in records:
        if record.latest_event is not None:
            decision_summary["skipped_already_decided"] += 1
            continue
        if record.claim.promotion_policy == "auto_apply":
            if not policy["auto_promote_auto_apply"]:
                decision_summary["kept_active_runtime"] += 1
                continue
            target_page = _target_page_for_claim(record.claim)
            page_path = root / target_page
            page_backups.setdefault(target_page, page_path.read_text(encoding="utf-8"))
            promote_claim_to_page(root, record.claim, target_page)
            event = build_claim_event(
                record,
                action="auto_promoted",
                to_status="promoted",
                reason="Autopilot promoted low/medium-risk workflow memory after post-run evidence extraction.",
                target_page=target_page,
            )
            append_claim_event(root, event)
            promoted_records.append((record, target_page))
            decisions.append(event)
            decision_summary["auto_promoted"] += 1
            continue
        if record.claim.promotion_policy == "human_review":
            if not policy["auto_defer_high_risk"]:
                continue
            event = build_claim_event(
                record,
                action="auto_deferred",
                to_status="deferred",
                reason=(
                    "Autopilot deferred high-risk identity/style/creator-preference "
                    "memory until repeated evidence exists."
                ),
            )
            append_claim_event(root, event)
            decisions.append(event)
            decision_summary["auto_deferred"] += 1
            continue
        if record.claim.promotion_policy == "quarantine":
            if not policy["auto_quarantine_rejected_assets"]:
                continue
            event = build_claim_event(
                record,
                action="auto_quarantined",
                to_status="quarantined",
                reason="Autopilot quarantined rejected or unsafe memory so it cannot guide generation.",
            )
            append_claim_event(root, event)
            decisions.append(event)
            decision_summary["auto_quarantined"] += 1

    verification = _run_heavy_verification(root, run_id)
    if verification["status"] != "pass" and promoted_records:
        _restore_promoted_pages(root, page_backups)
        for record, target_page in promoted_records:
            event = build_claim_event(
                record,
                action="auto_rollback",
                to_status="deferred",
                reason="Autopilot rolled back promotion because lint or retrieval eval failed.",
                target_page=target_page,
            )
            append_claim_event(root, event)
            decisions.append(event)
            decision_summary["auto_rollback"] += 1
        verification = _run_heavy_verification(root, run_id)

    final_summary = summarize_claim_records(
        [
            record
            for record in load_claim_records(root)
            if record.claim.run_id == run_id
        ]
    )
    report = {
        "schema_version": "1.0",
        "status": "completed" if verification["status"] == "pass" else "completed_with_verification_failures",
        "run_id": run_id,
        "phase": phase,
        "heavy_verification_ran": True,
        "human_intervention_required": False,
        "learning_artifacts": learning_artifacts,
        "policy": policy,
        "decision_summary": decision_summary,
        "claim_summary": final_summary,
        "decisions": decisions,
        "verification": verification,
        "pre_imagegen_latency_contract": (
            "The heavy learn/promote/verify loop is post-run only and must not run before illustration generation."
        ),
    }
    _write_autopilot_report(root, run_id, report)
    return report


def _target_page_for_claim(claim) -> str:
    if claim.scope == "aachu_identity":
        return "references/brain/pages/characters/aachu.md"
    if claim.scope == "relationship_direction":
        return "references/brain/pages/characters/together.md"
    if "style" in claim.applies_to or claim.scope == "asset_governance":
        return "references/brain/pages/style/observational-intimacy-premium.md"
    return "references/brain/pages/run-lessons.md"


def _run_heavy_verification(root: Path, run_id: str) -> dict[str, Any]:
    lint_report = lint_brain(root)
    index_dir = root / "references/brain/index"
    build_index(root, index_dir, include_runs=[run_id])
    qrels = root / "tests/fixtures/brain/qrels.json"
    eval_report = {"status": "not_run", "reason": "qrels fixture missing"}
    if qrels.exists():
        eval_report = run_retrieval_eval(index_dir, qrels)
    return {
        "status": "pass"
        if lint_report["status"] == "pass"
        and eval_report["status"] in {"pass", "not_run"}
        else "fail",
        "lint": lint_report,
        "retrieval_eval": eval_report,
    }


def _restore_promoted_pages(root: Path, page_backups: dict[str, str]) -> None:
    for target_page, text in page_backups.items():
        (root / target_page).write_text(text, encoding="utf-8")


def _write_autopilot_report(root: Path, run_id: str, report: dict[str, Any]) -> None:
    path = root / "runs" / run_id / "memory/autopilot_report.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
