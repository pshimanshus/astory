#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

try:
    from .astory_brain.eval import run_retrieval_eval
    from .astory_brain.indexer import build_index
    from .astory_brain.learning import extract_learning_report, write_learning_artifacts
    from .astory_brain.lint import lint_brain
    from .astory_brain.retrieval import recall
    from .astory_brain.synthesis import synthesize_recall
except ImportError:
    from astory_brain.eval import run_retrieval_eval
    from astory_brain.indexer import build_index
    from astory_brain.learning import extract_learning_report, write_learning_artifacts
    from astory_brain.lint import lint_brain
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
        "required_human_decisions": [
            "Review human_review and quarantine memory claims before promoting them into canonical brain pages."
        ],
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
            "- Review human_review and quarantine memory claims before promoting them into canonical brain pages.",
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
    summary: dict[str, int] = {
        "total": 0,
        "auto_apply": 0,
        "human_review": 0,
        "quarantine": 0,
        "quarantined": 0,
    }
    missing_runs: list[str] = []
    runs_to_check = required_runs or []
    for run_id in runs_to_check:
        claims_path = root / "runs" / run_id / "memory/claim_candidates.json"
        if not claims_path.exists():
            missing_runs.append(run_id)
            continue
        payload = json.loads(claims_path.read_text(encoding="utf-8"))
        claim_summary = payload.get("summary") or {}
        for key, value in claim_summary.items():
            if isinstance(value, int):
                summary[key] = summary.get(key, 0) + value

    if missing_runs:
        status = "needs_extraction"
    elif summary.get("human_review", 0) or summary.get("quarantine", 0) or summary.get("quarantined", 0):
        status = "operational_with_review_queue"
    else:
        status = "ready"
    return {
        "status": status,
        "claim_review_queue": summary,
        "missing_learning_runs": missing_runs,
    }


def _claim_summary(claims) -> dict[str, int]:
    summary = {"total": len(claims)}
    for claim in claims:
        summary[claim.promotion_policy] = summary.get(claim.promotion_policy, 0) + 1
        summary[claim.status] = summary.get(claim.status, 0) + 1
    return summary


if __name__ == "__main__":
    raise SystemExit(main())
