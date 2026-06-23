#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

try:
    from .astory_brain.autopilot import run_memory_autopilot
    from .astory_brain.claim_store import (
        apply_claim_decision,
        load_claim_records,
        summarize_claim_records,
    )
    from .astory_brain.eval import run_retrieval_eval
    from .astory_brain.indexer import build_index
    from .astory_brain.learning import extract_learning_report, write_learning_artifacts
    from .astory_brain.lint import lint_brain
    from .astory_brain.outcomes import (
        compute_outcome_report,
        load_carousel_outcomes,
        write_outcome_artifacts,
    )
    from .astory_brain.retrieval import recall
    from .astory_brain.synthesis import synthesize_recall
except ImportError:
    from astory_brain.autopilot import run_memory_autopilot
    from astory_brain.claim_store import (
        apply_claim_decision,
        load_claim_records,
        summarize_claim_records,
    )
    from astory_brain.eval import run_retrieval_eval
    from astory_brain.indexer import build_index
    from astory_brain.learning import extract_learning_report, write_learning_artifacts
    from astory_brain.lint import lint_brain
    from astory_brain.outcomes import (
        compute_outcome_report,
        load_carousel_outcomes,
        write_outcome_artifacts,
    )
    from astory_brain.retrieval import recall
    from astory_brain.synthesis import synthesize_recall


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="A Story brain utilities")
    subparsers = parser.add_subparsers(dest="command", required=True)

    index_parser = subparsers.add_parser("index")
    index_parser.add_argument("--repo-root", default=".")
    index_parser.add_argument("--output", required=True)
    index_parser.add_argument("--include-run", action="append", default=[])

    recall_parser = subparsers.add_parser("recall")
    recall_parser.add_argument("--index", required=True)
    recall_parser.add_argument("--query", required=True)
    recall_parser.add_argument("--role")
    recall_parser.add_argument("--run-id")
    recall_parser.add_argument("--limit", type=int, default=10)
    recall_parser.add_argument("--output")

    lint_parser = subparsers.add_parser("lint")
    lint_parser.add_argument("--repo-root", default=".")

    eval_parser = subparsers.add_parser("eval")
    eval_parser.add_argument("--index", required=True)
    eval_parser.add_argument("--qrels", required=True)
    eval_parser.add_argument("--top-k", type=int, default=5)

    learn_parser = subparsers.add_parser("learn")
    learn_parser.add_argument("--repo-root", default=".")
    learn_parser.add_argument("--run-id", required=True)
    learn_parser.add_argument("--write", action="store_true")

    autopilot_parser = subparsers.add_parser("autopilot")
    autopilot_parser.add_argument("--repo-root", default=".")
    autopilot_parser.add_argument("--run-id", required=True)
    autopilot_parser.add_argument(
        "--phase",
        choices=["pre_imagegen", "post_run", "write_reports"],
        default="post_run",
    )

    claims_parser = subparsers.add_parser("claims")
    claims_subparsers = claims_parser.add_subparsers(dest="claims_command", required=True)
    claims_list_parser = claims_subparsers.add_parser("list")
    claims_list_parser.add_argument("--repo-root", default=".")
    claims_list_parser.add_argument("--status", default="open")
    claims_list_parser.add_argument("--json", action="store_true")
    claims_decide_parser = claims_subparsers.add_parser("decide")
    claims_decide_parser.add_argument("--repo-root", default=".")
    claims_decide_parser.add_argument("--claim-id", required=True)
    claims_decide_parser.add_argument(
        "--decision",
        choices=["promote", "reject", "defer", "quarantine"],
        required=True,
    )
    claims_decide_parser.add_argument("--reason", required=True)
    claims_decide_parser.add_argument("--reviewer", default="codex")
    claims_decide_parser.add_argument("--target-page")

    outcomes_parser = subparsers.add_parser("outcomes")
    outcomes_parser.add_argument("--repo-root", default=".")
    outcomes_parser.add_argument("--write", action="store_true")

    doctor_parser = subparsers.add_parser("doctor")
    doctor_parser.add_argument("--repo-root", default=".")

    args = parser.parse_args(argv)
    if args.command == "index":
        build_index(args.repo_root, args.output, args.include_run)
        return 0
    if args.command == "recall":
        results = recall(args.index, args.query, args.role, args.run_id, args.limit)
        synthesis = synthesize_recall(args.query, results)
        if args.output:
            output = Path(args.output)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(synthesis.answer_markdown, encoding="utf-8")
        else:
            print(synthesis.answer_markdown)
        return 0
    if args.command == "lint":
        report = lint_brain(args.repo_root)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report["status"] == "pass" else 1
    if args.command == "eval":
        report = run_retrieval_eval(args.index, args.qrels, args.top_k)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report["status"] == "pass" else 1
    if args.command == "learn":
        report = extract_learning_report(args.repo_root, args.run_id)
        artifacts = (
            write_learning_artifacts(args.repo_root, report)
            if args.write
            else {}
        )
        payload = {
            "status": "claims_extracted",
            "run_id": report.run_id,
            "summary": report.summary or _claim_summary(report.claims),
            "claims": [asdict(claim) for claim in report.claims],
            "artifacts": artifacts,
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    if args.command == "autopilot":
        report = run_memory_autopilot(args.repo_root, args.run_id, phase=args.phase)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
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
            print(
                json.dumps(
                    {"status": "decision_recorded", "event": event},
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0
    if args.command == "outcomes":
        records = load_carousel_outcomes(args.repo_root)
        report = compute_outcome_report(records)
        artifacts = (
            write_outcome_artifacts(args.repo_root, report) if args.write else {}
        )
        print(
            json.dumps(
                {"status": "ok", "artifacts": artifacts, "report": report},
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    if args.command == "doctor":
        report = _doctor(Path(args.repo_root).resolve())
        print(report)
        return 0
    return 2


def _doctor(root: Path) -> str:
    reports = root / "references/brain/reports"
    reports.mkdir(parents=True, exist_ok=True)
    lint_report = lint_brain(root)
    qrels = root / "tests/fixtures/brain/qrels.json"
    eval_report = {"status": "not_run", "reason": "qrels fixture missing"}
    index_dir = root / "references/brain/index"
    required_learning_runs: list[str] = []
    if qrels.exists():
        required_learning_runs = _qrels_include_runs(qrels)
        build_index(root, index_dir, required_learning_runs)
        eval_report = run_retrieval_eval(index_dir, qrels)
    runtime_status = (
        "ready"
        if lint_report["status"] == "pass" and eval_report["status"] == "pass"
        else "needs_eval"
        if lint_report["status"] == "pass" and eval_report["status"] == "not_run"
        else "blocked"
    )
    learning = _learning_pipeline_status(root, required_learning_runs)
    setup_status = (
        "blocked"
        if runtime_status == "blocked"
        else learning["status"]
        if learning["status"] != "ready"
        else runtime_status
    )
    required_human_decisions = _required_human_decisions(learning["claim_review_queue"])
    excluded_run_gates = [
        "reference_visibility_proof",
        "agent_assignment_gate",
        "image_qa_blocks_final_package",
        "hitl_order_before_imagegen",
        "approvals_cover_required_gates",
    ]
    doctor_payload = {
        "schema_version": "1.0",
        "scope": "brain_setup",
        "setup_status": setup_status,
        "runtime_status": runtime_status,
        "learning_pipeline_status": learning["status"],
        "claim_review_queue": learning["claim_review_queue"],
        "missing_learning_runs": learning["missing_learning_runs"],
        "required_learning_runs": required_learning_runs,
        "lint": lint_report,
        "retrieval_eval": eval_report,
        "required_human_decisions": required_human_decisions,
        "excluded_run_gates": excluded_run_gates,
    }
    (reports / "retrieval_eval.json").write_text(
        json.dumps(eval_report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (reports / "doctor.json").write_text(
        json.dumps(doctor_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    report = "\n".join(
        [
            "# A Story Brain Doctor",
            "",
            "Scope: `brain_setup`",
            "",
            "This doctor validates the memory/semantic-retrieval setup only. Creative run gates are intentionally out of scope here.",
            "",
            "## Status",
            "",
            f"- Brain setup status: `{setup_status}`",
            f"- Runtime status: `{runtime_status}`",
            f"- Learning pipeline status: `{learning['status']}`",
            f"- Lint: `{lint_report['status']}`",
            f"- Retrieval eval: `{eval_report['status']}`",
            "",
            "## Creative Run Gates Excluded",
            "",
            "\n".join(f"- `{gate}`" for gate in excluded_run_gates),
            "",
            "## Lint",
            "",
            json.dumps(lint_report, indent=2, sort_keys=True),
            "",
            "## Retrieval Eval",
            "",
            json.dumps(eval_report, indent=2, sort_keys=True),
            "",
            "## Orphans",
            "",
            "- Not implemented beyond index/link validation in schema v1.",
            "",
            "## Memory Claim Review Queue",
            "",
            "Human-review and quarantine claims are deliberately kept out of canonical brain pages until reviewed. Auto-apply claims can influence workflow behavior immediately, but high-risk identity, style, and creator-preference claims stay in the queue.",
            "",
            json.dumps(learning["claim_review_queue"], indent=2, sort_keys=True),
            "",
            "## Missing Learning Extractions",
            "",
            "\n".join(f"- `{run_id}`" for run_id in learning["missing_learning_runs"]) or "- None.",
            "",
            "## Required Human Decisions",
            "",
            "\n".join(f"- {decision}" for decision in required_human_decisions) or "- None.",
            "",
        ]
    )
    (reports / "doctor.md").write_text(report, encoding="utf-8")
    return report


def _qrels_include_runs(qrels_path: Path) -> list[str]:
    try:
        qrels = json.loads(qrels_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if not isinstance(qrels, list):
        return []
    return sorted(
        {
            str(item["run_id"])
            for item in qrels
            if isinstance(item, dict) and item.get("run_id")
        }
    )


def _learning_pipeline_status(root: Path, required_runs: list[str]) -> dict:
    missing_runs: list[str] = []
    runs_to_check = required_runs or []
    for run_id in runs_to_check:
        claims_path = root / "runs" / run_id / "memory/claim_candidates.json"
        if not claims_path.exists():
            missing_runs.append(run_id)
    records = [
        record
        for record in load_claim_records(root)
        if not runs_to_check or record.claim.run_id in set(runs_to_check)
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


def _required_human_decisions(claim_review_queue: dict[str, int]) -> list[str]:
    if claim_review_queue.get("open_human_review", 0) or claim_review_queue.get(
        "open_quarantine_review", 0
    ):
        return [
            "Review open human-review and quarantine memory claims before promoting them into canonical brain pages."
        ]
    return []


def _claim_summary(claims) -> dict[str, int]:
    summary = {"total": len(claims)}
    for claim in claims:
        summary[claim.promotion_policy] = summary.get(claim.promotion_policy, 0) + 1
        summary[claim.status] = summary.get(claim.status, 0) + 1
    return summary


def _filter_claim_records(records, status: str):
    if status == "all":
        return records
    if status == "open":
        return [
            record
            for record in records
            if record.effective_status in {"candidate", "quarantined"}
            and record.latest_event is None
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
    lines = ["# Memory Claims", "", json.dumps(payload["summary"], indent=2, sort_keys=True), ""]
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


if __name__ == "__main__":
    raise SystemExit(main())
