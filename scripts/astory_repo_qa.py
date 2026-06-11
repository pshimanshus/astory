"""Repo-level QA checks for A Story of Two runs.

This module audits run artifacts and records blockers. It deliberately does not
create substitute proof artifacts for image generation; missing proof remains a
reported failure.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_TEMPLATE_PATHS = [
    ".agents/skills/astory/templates/docs/approvals.md",
    ".agents/skills/astory/templates/logs/trace_event.jsonl",
    ".agents/skills/astory/templates/evals/pre_generation_eval.json",
    ".agents/skills/astory/templates/evals/image_quality_eval.json",
    ".agents/skills/astory/templates/debates/agent_assignment_matrix.md",
    ".agents/skills/astory/templates/agents/story_room_agent_prompt.md",
    ".agents/skills/astory/templates/agents/visual_scene_discussion_prompt.md",
    ".agents/skills/astory/templates/agents/review_room_agent_prompt.md",
    ".agents/skills/astory/templates/prompts/slide_prompt.txt",
    ".agents/skills/astory/templates/planning/memory_recall.md",
    ".agents/skills/astory/templates/docs/retro.md",
    ".agents/skills/astory/references/failure-taxonomy.md",
    ".agents/skills/astory/references/house-style-contract.md",
    ".agents/skills/astory/references/imagegen-contract.md",
]

REQUIRED_APPROVAL_GATES = [
    "Idea Lock",
    "Story / Slide Count Lock",
    "Prompt Lock",
    "Image QA",
    "Final Package",
]


def run_repo_qa(repo_root: str | Path, run_id: str) -> dict[str, Any]:
    """Return a structured QA audit for a run."""

    root = Path(repo_root).resolve()
    run_dir = root / "runs" / run_id
    workflow = _detect_workflow(run_dir, root)
    checks = [
        _check_skill_contract(root),
        _check_master_prompt(root),
        _check_required_templates(root),
        _check_reference_manifest(root, run_dir),
        _check_memory_recall(root, run_dir, workflow),
        _check_prompt_story_contract(root, run_dir, workflow),
        _check_prompt_reference_gate(root, run_dir, workflow),
        _check_prompt_forbidden_role_reversal(root, run_dir, workflow),
        _check_reference_visibility_proof(root, run_dir),
        _check_image_qa_blocks_final_package(run_dir),
        _check_final_package_not_started(run_dir),
        _check_accepted_candidate_filename_guard(run_dir),
        _check_trace_jsonl_valid(run_dir),
        _check_hitl_order_before_imagegen(run_dir),
        _check_agent_assignment_gate(run_dir),
        _check_approvals_cover_required_gates(run_dir),
        _check_local_identity_execution_report(run_dir),
    ]

    checks_by_id = {check["id"]: check for check in checks}
    reference_summary = checks_by_id["reference_manifest_integrity"].get(
        "reference_summary", _empty_reference_summary()
    )

    failing = [
        check
        for check in checks
        if (
            check.get("status") in {"fail", "blocked"}
            and check.get("severity") == "blocker"
        )
        or (
            check.get("severity") == "blocker"
            and check.get("final_imagegen_allowed") is False
        )
    ]
    overall_status = "blocked" if failing else "pass"

    return {
        "schema_version": "1.0",
        "run_id": run_id,
        "created_at": _utc_now_iso(),
        "overall_status": overall_status,
        "repo_root": str(root),
        "run_dir": str(run_dir),
        "workflow": workflow,
        "checks": checks,
        "checks_by_id": checks_by_id,
        "reference_summary": reference_summary,
        "blocking_findings": [
            {
                "id": check["id"],
                "failure_code": _failure_code_for_check(check),
                "summary": check.get("summary"),
            }
            for check in failing
        ],
    }


def run_review_loop(
    repo_root: str | Path,
    run_id: str,
    max_iterations: int = 3,
    prepare_references: bool = True,
) -> dict[str, Any]:
    """Run bounded repo QA iterations and write a loop artifact."""

    root = Path(repo_root).resolve()
    run_dir = root / "runs" / run_id
    iterations: list[dict[str, Any]] = []

    for iteration in range(1, max_iterations + 1):
        if prepare_references:
            _prepare_references_if_needed(root, run_id)

        audit = write_qa_artifacts(root, run_id)
        blockers = audit.get("blocking_findings", [])
        iterations.append(
            {
                "iteration": iteration,
                "overall_status": audit["overall_status"],
                "blocking_findings": blockers,
            }
        )

        if audit["overall_status"] == "pass":
            result = {
                "schema_version": "1.0",
                "run_id": run_id,
                "status": "pass",
                "max_iterations": max_iterations,
                "iterations": iterations,
            }
            _write_review_loop_artifact(run_dir, result)
            return result

        if _only_human_or_external_blockers(blockers):
            break

    result = {
        "schema_version": "1.0",
        "run_id": run_id,
        "status": "blocked",
        "max_iterations": max_iterations,
        "iterations": iterations,
    }
    _write_review_loop_artifact(run_dir, result)
    return result


def write_qa_artifacts(repo_root: str | Path, run_id: str) -> dict[str, Any]:
    audit = run_repo_qa(repo_root, run_id)
    run_dir = Path(repo_root).resolve() / "runs" / run_id
    evals_dir = run_dir / "evals"
    evals_dir.mkdir(parents=True, exist_ok=True)

    json_path = evals_dir / "repo_qa_review.json"
    report_path = evals_dir / "repo_qa_review.md"
    json_path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    report_path.write_text(_render_report(audit))

    audit["artifacts"] = {
        "json": _rel(json_path, Path(repo_root).resolve()),
        "report": _rel(report_path, Path(repo_root).resolve()),
    }
    return audit


def _detect_workflow(run_dir: Path, root: Path) -> dict[str, Any]:
    prompt_files = _prompt_files(run_dir)
    evidence: list[str] = []

    if prompt_files:
        evidence.append("prompts")
    if (run_dir / "evals/imagegen_reference_load_plan.json").exists():
        evidence.append("reference_load_plan")
    if (run_dir / "evals/imagegen_reference_visibility_proof.json").exists():
        evidence.append("reference_visibility_proof")
    if (run_dir / "evals/local_identity_reference_proof.json").exists():
        evidence.append("local_identity_proof")
    if (run_dir / "references-used/selected_references.json").exists():
        evidence.append("selected_references")

    if "local_identity_proof" in evidence and not prompt_files:
        workflow_type = "local_identity_execution_run"
    elif prompt_files and "reference_load_plan" in evidence:
        workflow_type = "imagegen_story_run"
    elif prompt_files:
        workflow_type = "prompt_revision_run"
    elif "selected_references" in evidence:
        workflow_type = "reference_library_run"
    else:
        workflow_type = "unknown_run"

    return {
        "type": workflow_type,
        "evidence": evidence,
        "prompt_files": [_rel(path, root) for path in prompt_files],
    }


def _prompt_files(run_dir: Path) -> list[Path]:
    prompts_dir = run_dir / "prompts"
    if not prompts_dir.exists():
        return []
    return sorted(path for path in prompts_dir.glob("slide_*_prompt.txt") if path.is_file())


def _check_skill_contract(root: Path) -> dict[str, Any]:
    path = root / ".agents/skills/astory/SKILL.md"
    text = _read_text(path)
    required_phrases = {
        "Reference Hard Gate": "Reference Hard Gate" in text,
        "HITL Gates": "HITL Gates" in text or "HITL gate" in text,
        "no text-only final identity": "Do not generate or accept final Aachu/Zuv artwork from text-only identity descriptions"
        in text,
        "reference visibility proof": "imagegen_reference_visibility_proof.json"
        in text,
    }
    missing = [phrase for phrase, present in required_phrases.items() if not present]
    return _check(
        "skill_contract_present",
        "pass" if path.exists() and not missing else "fail",
        "A Story skill contract is present and contains the identity/HITL gates.",
        path=_rel(path, root),
        missing_phrases=missing,
        severity="blocker",
    )


def _check_master_prompt(root: Path) -> dict[str, Any]:
    path = root / ".agents/skills/astory/references/master-prompt.md"
    text = _read_text(path)
    required = ["A Story of Two", "identity", "watercolor"]
    missing = [phrase for phrase in required if phrase.lower() not in text.lower()]
    return _check(
        "master_prompt_present",
        "pass" if path.exists() and not missing else "fail",
        "Master prompt reference is present.",
        path=_rel(path, root),
        missing_phrases=missing,
        severity="blocker",
    )


def _check_required_templates(root: Path) -> dict[str, Any]:
    missing = [path for path in REQUIRED_TEMPLATE_PATHS if not (root / path).exists()]
    return _check(
        "required_templates_present",
        "pass" if not missing else "fail",
        "Required skill templates and contracts are present.",
        checked_paths=REQUIRED_TEMPLATE_PATHS,
        missing_paths=missing,
        severity="blocker",
    )


def _check_reference_manifest(root: Path, run_dir: Path) -> dict[str, Any]:
    manifest_path = run_dir / "references-used/selected_references.json"
    manifest = _read_json(manifest_path)
    if not isinstance(manifest, dict):
        return _check(
            "reference_manifest_integrity",
            "fail",
            "Selected reference manifest is missing or invalid.",
            path=_rel(manifest_path, root),
            missing_paths=[_rel(manifest_path, root)],
            sha_mismatches=[],
            reference_summary=_empty_reference_summary(),
            severity="blocker",
        )

    if not isinstance(manifest.get("reference_groups"), dict):
        return _check_legacy_reference_manifest(root, run_dir, manifest_path, manifest)

    refs = _iter_manifest_refs(manifest)
    missing_paths: list[str] = []
    sha_mismatches: list[dict[str, str]] = []
    missing_hashes: list[str] = []

    for ref in refs:
        path_text = ref.get("path")
        sha_text = ref.get("sha256")
        if not path_text:
            missing_paths.append("<reference without path>")
            continue
        ref_path = root / path_text
        if not ref_path.exists():
            missing_paths.append(path_text)
            continue
        if not sha_text:
            missing_hashes.append(path_text)
            continue
        actual_sha = _sha256_file(ref_path)
        if actual_sha != sha_text:
            sha_mismatches.append(
                {
                    "path": path_text,
                    "expected": str(sha_text),
                    "actual": actual_sha,
                }
            )

    groups = manifest.get("reference_groups") or {}
    queue = manifest.get("view_image_queue") or []
    summary = {
        "aachu_face_identity_count": len(groups.get("aachu_face_identity") or []),
        "zuv_face_identity_count": len(groups.get("zuv_face_identity") or []),
        "expression_support_count": len(groups.get("expression_support") or []),
        "together_body_language_count": len(groups.get("together_body_language") or []),
        "style_reference_count": len(groups.get("style") or []),
        "text_and_brand_reference_count": len(manifest.get("text_and_brand_references") or []),
        "view_image_queue_count": manifest.get("view_image_queue_count", len(queue)),
        "view_image_queue_actual_count": len(queue),
        "prompt_only_allowed": manifest.get("prompt_only_allowed"),
    }
    role_errors = _reference_role_errors(groups)
    count_errors: list[str] = []
    if summary["aachu_face_identity_count"] < 4:
        count_errors.append("aachu_face_identity_count_lt_4")
    if summary["zuv_face_identity_count"] < 4:
        count_errors.append("zuv_face_identity_count_lt_4")
    if summary["style_reference_count"] < 1:
        count_errors.append("style_reference_count_lt_1")
    if summary["view_image_queue_count"] != summary["view_image_queue_actual_count"]:
        count_errors.append("view_image_queue_count_mismatch")
    if manifest.get("prompt_only_allowed") is not False:
        count_errors.append("prompt_only_allowed_not_false")

    status = (
        "pass"
        if not missing_paths
        and not sha_mismatches
        and not missing_hashes
        and not role_errors
        and not count_errors
        else "fail"
    )
    return _check(
        "reference_manifest_integrity",
        status,
        "Selected reference manifest resolves to existing hashed references.",
        path=_rel(manifest_path, root),
        missing_paths=missing_paths,
        sha_mismatches=sha_mismatches,
        missing_hashes=missing_hashes,
        role_errors=role_errors,
        count_errors=count_errors,
        reference_summary=summary,
        severity="blocker",
    )


def _check_legacy_reference_manifest(
    root: Path, run_dir: Path, manifest_path: Path, manifest: dict[str, Any]
) -> dict[str, Any]:
    refs = _iter_legacy_manifest_paths(manifest)
    missing_paths = [path for path in refs if not (root / path).exists()]
    identity_refs = manifest.get("identity_references") or {}
    style_refs = manifest.get("style_references") or []
    prompt_only_allowed = not (
        "not_prompt_only" in str(manifest.get("visibility_status", ""))
        or "actual local binary image inputs"
        in str(manifest.get("visibility_note", "")).lower()
    )
    summary = {
        "aachu_face_identity_count": len(identity_refs.get("aachu") or []),
        "zuv_face_identity_count": len(identity_refs.get("zuv") or []),
        "expression_support_count": 0,
        "together_body_language_count": len(identity_refs.get("together") or []),
        "style_reference_count": len(style_refs),
        "text_and_brand_reference_count": len(
            [
                item
                for item in [
                    manifest.get("text_style_reference"),
                    manifest.get("brand_reference"),
                    manifest.get("identity_dossier"),
                    manifest.get("identity_generation_preflight"),
                ]
                if item
            ]
        ),
        "view_image_queue_count": len(refs),
        "view_image_queue_actual_count": len(refs),
        "prompt_only_allowed": prompt_only_allowed,
    }
    count_errors: list[str] = []
    if summary["aachu_face_identity_count"] < 4:
        count_errors.append("aachu_face_identity_count_lt_4")
    if summary["zuv_face_identity_count"] < 4:
        count_errors.append("zuv_face_identity_count_lt_4")
    if summary["style_reference_count"] < 1:
        count_errors.append("style_reference_count_lt_1")
    if prompt_only_allowed:
        count_errors.append("prompt_only_allowed_not_false")

    return _check(
        "reference_manifest_integrity",
        "pass" if not missing_paths and not count_errors else "fail",
        "Selected reference manifest resolves to existing local references.",
        path=f"runs/{run_dir.name}/references-used/selected_references.json",
        schema="legacy_role_based_reference_library",
        missing_paths=missing_paths,
        sha_mismatches=[],
        missing_hashes=[],
        role_errors=[],
        count_errors=count_errors,
        reference_summary=summary,
        severity="blocker",
    )


def _check_memory_recall(
    root: Path,
    run_dir: Path,
    workflow: dict[str, Any],
) -> dict[str, Any]:
    if workflow.get("type") == "local_identity_execution_run":
        return _check(
            "memory_recall",
            "not_applicable",
            "Memory recall is not required for local identity execution proof runs.",
            expected_artifacts=[],
            workflow_type=workflow.get("type"),
            severity="info",
        )

    path = run_dir / "planning/memory_recall.md"
    expected = [f"runs/{run_dir.name}/planning/memory_recall.md"]
    if workflow.get("type") in {"unknown_run", "reference_library_run"} and not path.exists():
        return _check(
            "memory_recall",
            "not_applicable",
            "Memory recall is not required for this workflow type.",
            expected_artifacts=expected,
            workflow_type=workflow.get("type"),
            severity="info",
        )

    if not path.exists():
        return _check(
            "memory_recall",
            "blocked",
            "Memory recall artifact is missing for this run.",
            expected_artifacts=expected,
            failure_code="MEMORY_RECALL_MISSING",
            workflow_type=workflow.get("type"),
            severity="blocker",
        )

    text = _read_text(path)
    required_sections = ["## Cited Findings", "## Gaps", "## Usability For This Run"]
    missing_sections = [section for section in required_sections if section not in text]
    cited_findings = _markdown_section(text, "## Cited Findings")
    citations = [
        citation
        for citation in re.findall(r"`([^`]+)`", cited_findings)
        if "/" in citation and not citation.startswith(("http://", "https://"))
    ]
    citations = list(dict.fromkeys(citations))
    derived_citations = [
        citation
        for citation in citations
        if citation.startswith("references/brain/index/")
        or citation.startswith("references/brain/reports/")
    ]
    missing_paths = [
        citation
        for citation in citations
        if not (root / citation).exists() and citation not in derived_citations
    ]
    events, trace_errors = _read_jsonl(run_dir / "logs/trace.jsonl")
    memory_trace_present = any(
        event.get("state") == "MEMORY_RECALL_PREFLIGHT"
        and str(event.get("status", "")).lower()
        in {"complete", "retrospective_backfill_complete", "pass"}
        for event in events
    )
    if trace_errors or not memory_trace_present:
        failure_code = "MEMORY_RECALL_TRACE_MISSING"
    elif not citations or missing_sections or missing_paths or derived_citations:
        failure_code = "MEMORY_RECALL_INVALID"
    else:
        failure_code = None
    status = "pass" if failure_code is None else "fail"
    return _check(
        "memory_recall",
        status,
        "Memory recall contains cited findings, gaps, and usability notes.",
        path=_rel(path, root),
        expected_artifacts=expected,
        missing_sections=missing_sections,
        cited_paths=citations,
        derived_citations=derived_citations,
        missing_cited_paths=missing_paths,
        memory_trace_present=memory_trace_present,
        trace_errors=trace_errors,
        failure_code=failure_code,
        workflow_type=workflow.get("type"),
        severity="blocker",
    )


def _markdown_section(text: str, heading: str) -> str:
    if heading not in text:
        return ""
    after = text.split(heading, 1)[1]
    next_heading = re.search(r"\n## ", after)
    if not next_heading:
        return after
    return after[: next_heading.start()]


def _check_prompt_story_contract(
    root: Path, run_dir: Path, workflow: dict[str, Any]
) -> dict[str, Any]:
    prompt_paths = _prompt_files(run_dir)
    if not prompt_paths:
        return _prompt_not_applicable("prompt_story_contract", run_dir)

    contract = _story_contract(run_dir)
    if not contract["required_phrases"]:
        return _check(
            "prompt_story_contract",
            "not_applicable",
            "No run-specific story contract artifact was available for this workflow.",
            contract_source=contract["source"],
            workflow_type=workflow["type"],
            severity="info",
        )

    prompt_text = _normalize_text("\n".join(_read_text(path) for path in prompt_paths))
    required = {
        phrase: _normalize_text(phrase) in prompt_text
        for phrase in contract["required_phrases"]
        if len(phrase.split()) <= 18
    }
    status = "pass" if required and all(required.values()) else "fail"
    return _check(
        "prompt_story_contract",
        status,
        "Prompts preserve the run-specific locked story contract.",
        contract_source=contract["source"],
        required_phrases=list(required.keys()),
        evidence=required,
        prompt_files=[_rel(path, root) for path in prompt_paths],
        workflow_type=workflow["type"],
        severity="blocker",
    )


def _check_prompt_reference_gate(
    root: Path, run_dir: Path, workflow: dict[str, Any]
) -> dict[str, Any]:
    def evaluator(prompt: str) -> dict[str, bool]:
        lower = prompt.lower()
        has_do_not_generate = "do not generate" in lower and (
            "text descriptions or file paths alone" in lower
            or "text alone" in lower
        )
        return {
            "generation_hard_gate": "generation hard gate" in lower
            or has_do_not_generate,
            "no_paths_only": has_do_not_generate,
            "aachu_refs": "aachu face identity" in lower
            or "aachu_face_identity" in lower
            or "aachu/zuv face anchors" in lower,
            "zuv_refs": "zuv face identity" in lower
            or "zuv_face_identity" in lower
            or "aachu/zuv face anchors" in lower,
            "style_refs": "style references" in lower
            or "style refs" in lower
            or "observational-intimacy-premium" in lower
            or "style:" in lower,
        }

    return _check_all_prompts(
        root,
        run_dir,
        "prompt_reference_gate",
        "Every prompt preserves the reference-image delivery gate.",
        evaluator,
        workflow,
    )


def _check_prompt_forbidden_role_reversal(
    root: Path, run_dir: Path, workflow: dict[str, Any]
) -> dict[str, Any]:
    def evaluator(prompt: str) -> dict[str, bool]:
        lower = prompt.lower()
        return {
            "aachu_named": "aachu" in lower,
            "zuv_named": "zuv" in lower,
            "role_reversal_forbidden_or_not_present": (
                "do not reverse the roles" in lower
                or "zuv asks aachu" not in lower
                or "do not show zuv asking aachu" in lower
            ),
        }

    return _check_all_prompts(
        root,
        run_dir,
        "prompt_forbidden_role_reversal",
        "Every prompt keeps Aachu/Zuv roles explicit and unreversed.",
        evaluator,
        workflow,
    )


def _check_reference_visibility_proof(root: Path, run_dir: Path) -> dict[str, Any]:
    manifest_path = run_dir / "references-used/selected_references.json"
    manifest = _read_json(manifest_path)
    proof_rel = None
    if isinstance(manifest, dict):
        proof_rel = ((manifest.get("load_state") or {}).get("proof_artifact"))
    if isinstance(manifest, dict) and proof_rel is None and not manifest.get("reference_groups"):
        return _check(
            "reference_visibility_proof",
            "not_applicable",
            "This run uses the local identity proof path instead of the active imagegen reference-load proof artifact.",
            expected_artifact=None,
            final_imagegen_allowed=False,
            failure_code=None,
            view_image_queue_count=0,
            severity="info",
        )
    if not proof_rel:
        proof_rel = f"runs/{run_dir.name}/evals/imagegen_reference_visibility_proof.json"

    proof_path = root / proof_rel
    imagegen_happened = _imagegen_was_attempted(run_dir)
    if proof_path.exists():
        proof = _read_json(proof_path)
        status = "pass" if _proof_has_image_roles(proof) else "fail"
        return _check(
            "reference_visibility_proof",
            status,
            "Reference visibility proof exists and records image roles.",
            expected_artifact=proof_rel,
            failure_code=None if status == "pass" else "REFERENCE_VISIBILITY_PROOF_INVALID",
            final_imagegen_allowed=status == "pass",
            view_image_queue_count=_manifest_queue_count(manifest),
            severity="blocker",
        )

    if imagegen_happened:
        return _check(
            "reference_visibility_proof",
            "pass",
            "Reference load plan requires a visibility proof before final imagegen; final generation remains blocked until it exists.",
            expected_artifact=proof_rel,
            failure_code="REFERENCE_VISIBILITY_PROOF_REQUIRED_BEFORE_FINAL_IMAGEGEN",
            final_imagegen_allowed=False,
            imagegen_attempted_without_proof=True,
            view_image_queue_count=_manifest_queue_count(manifest),
            severity="blocker",
        )

    return _check(
        "reference_visibility_proof",
        "pass",
        "Reference load plan requires a visibility proof before final imagegen; final generation remains blocked until it exists.",
        expected_artifact=proof_rel,
        failure_code="REFERENCE_VISIBILITY_PROOF_REQUIRED_BEFORE_FINAL_IMAGEGEN",
        final_imagegen_allowed=False,
        imagegen_attempted_without_proof=False,
        view_image_queue_count=_manifest_queue_count(manifest),
        severity="blocker",
    )


def _check_image_qa_blocks_final_package(run_dir: Path) -> dict[str, Any]:
    qa_path = run_dir / "evals/image_quality_eval.json"
    qa = _read_json(qa_path)
    imagegen_attempted = _imagegen_was_attempted(run_dir)
    if not qa_path.exists() and not imagegen_attempted:
        return _check(
            "image_qa_blocks_final_package",
            "not_applicable",
            "Image QA is not required until imagegen has been attempted.",
            path=f"runs/{run_dir.name}/evals/image_quality_eval.json",
            failure_code=None,
            severity="info",
        )
    if not qa_path.exists() and imagegen_attempted:
        return _check(
            "image_qa_blocks_final_package",
            "fail",
            "Imagegen was attempted but Image QA is missing.",
            path=f"runs/{run_dir.name}/evals/image_quality_eval.json",
            failure_code="IMAGE_QA_MISSING",
            severity="blocker",
        )

    hard_gate = qa.get("hard_gate_result") if isinstance(qa, dict) else None
    status_text = qa.get("status") if isinstance(qa, dict) else None
    candidates = qa.get("candidates_reviewed") if isinstance(qa, dict) else []
    final_artifacts = _final_artifacts(run_dir)

    qa_failed = (
        hard_gate == "failed"
        or str(status_text).startswith("fail")
        or "rejection" in str(status_text)
        or "rejected" in str(status_text)
    )
    qa_pending = (
        hard_gate == "pending_creator_image_qa"
        or "pending_creator" in str(status_text)
    )
    qa_blocks_final = qa_failed or qa_pending
    final_blocked = qa_blocks_final and not final_artifacts
    failure_code = None
    if qa_failed:
        failure_code = "IMAGE_QA_FAILED"
    elif qa_pending:
        failure_code = "IMAGE_QA_PENDING_CREATOR_APPROVAL"
    return _check(
        "image_qa_blocks_final_package",
        "pass" if final_blocked else "fail",
        "Image QA is blocking final packaging until creator approval.",
        path=f"runs/{run_dir.name}/evals/image_quality_eval.json",
        hard_gate_result=hard_gate,
        image_quality_status=status_text,
        candidates_reviewed=len(candidates or []),
        final_artifacts=final_artifacts,
        failure_code=failure_code,
        severity="blocker",
    )


def _check_final_package_not_started(run_dir: Path) -> dict[str, Any]:
    approvals = _read_text(run_dir / "docs/approvals.md")
    final_artifacts = _final_artifacts(run_dir)
    final_section = (
        approvals.split("## Final Package", 1)[1]
        if "## Final Package" in approvals
        else ""
    )
    final_not_started = "Status: not started" in final_section
    final_blocked = "Status: blocked" in final_section
    local_report = _read_json(run_dir / "evals/local_identity_execution_report.json")
    local_blocks_final = (
        isinstance(local_report, dict)
        and local_report.get("final_artwork_generated") is False
        and local_report.get("status") == "blocked"
    )
    approvals_block_final = "Final carousel generation: still blocked" in approvals
    return _check(
        "final_package_not_started",
        "pass"
        if (final_not_started or final_blocked or local_blocks_final or approvals_block_final)
        and not final_artifacts
        else "fail",
        "Final Package gate remains not started while image QA is failed.",
        final_artifacts=final_artifacts,
        severity="blocker",
    )


def _check_accepted_candidate_filename_guard(run_dir: Path) -> dict[str, Any]:
    qa = _read_json(run_dir / "evals/image_quality_eval.json")
    candidates = qa.get("candidates_reviewed") if isinstance(qa, dict) else []
    accepted_name_candidates = [
        item
        for item in candidates or []
        if "accepted_candidate" in str(item.get("path", ""))
    ]
    rejected_after_review = [
        item.get("path")
        for item in accepted_name_candidates
        if item.get("status") == "rejected_after_creator_review"
    ]
    unsafe_statuses = [
        item
        for item in accepted_name_candidates
        if item.get("status") not in {"rejected_after_creator_review", "rejected"}
    ]
    if not accepted_name_candidates:
        return _check(
            "accepted_candidate_filename_guard",
            "not_applicable",
            "No accepted_candidate filenames are present in Image QA candidates.",
            accepted_candidate_paths=[],
            rejected_after_review=[],
            unsafe_statuses=[],
            severity="info",
        )
    return _check(
        "accepted_candidate_filename_guard",
        "pass" if accepted_name_candidates and not unsafe_statuses else "fail",
        "Files named accepted_candidate are not treated as final after creator rejection.",
        accepted_candidate_paths=[item.get("path") for item in accepted_name_candidates],
        rejected_after_review=rejected_after_review,
        unsafe_statuses=unsafe_statuses,
        severity="blocker",
    )


def _check_trace_jsonl_valid(run_dir: Path) -> dict[str, Any]:
    trace_path = run_dir / "logs/trace.jsonl"
    events, errors = _read_jsonl(trace_path)
    return _check(
        "trace_jsonl_valid",
        "pass" if trace_path.exists() and not errors else "fail",
        "Trace JSONL is parseable.",
        path=f"runs/{run_dir.name}/logs/trace.jsonl",
        event_count=len(events),
        parse_errors=errors,
        severity="blocker",
    )


def _check_hitl_order_before_imagegen(run_dir: Path) -> dict[str, Any]:
    events, errors = _read_jsonl(run_dir / "logs/trace.jsonl")
    if errors:
        return _check(
            "hitl_order_before_imagegen",
            "fail",
            "Cannot verify HITL order because trace JSONL is invalid.",
            parse_errors=errors,
            severity="blocker",
        )

    indices = {
        "idea": _first_event_index(events, "HITL_IDEA_LOCK", {"approved", "approved_with_revision"}),
        "story": _first_event_index(events, "HITL_STORY_LOCK", {"approved"}),
        "prompt": _first_event_index(events, "HITL_PROMPT_LOCK", {"approved"}),
        "imagegen": _first_event_index(events, "GENERATE_IMAGES_WITH_IMAGEGEN", None),
    }
    ordered = (
        indices["idea"] is not None
        and indices["story"] is not None
        and indices["prompt"] is not None
        and indices["imagegen"] is not None
        and indices["idea"] < indices["story"] < indices["prompt"] < indices["imagegen"]
    )
    return _check(
        "hitl_order_before_imagegen",
        "pass" if ordered else "fail",
        "Idea, story, and prompt locks are recorded before image generation.",
        event_indices=indices,
        failure_code=None if ordered else "HITL_ORDER_BEFORE_IMAGEGEN_MISSING",
        severity="blocker",
    )


def _check_agent_assignment_gate(run_dir: Path) -> dict[str, Any]:
    matrix_path = run_dir / "debates/agent_assignment_matrix.md"
    prompt_review_path = run_dir / "debates/prompt_room/prompt_review.md"
    pregen_path = run_dir / "evals/pre_generation_eval.json"
    pregen = _read_json(pregen_path)
    events, trace_errors = _read_jsonl(run_dir / "logs/trace.jsonl")
    approvals = _read_text(run_dir / "docs/approvals.md")

    prompt_lock_started = (
        "## Prompt Lock" in approvals
        or any(event.get("state") == "HITL_PROMPT_LOCK" for event in events)
    )
    if not prompt_lock_started and not _imagegen_was_attempted(run_dir):
        return _check(
            "agent_assignment_gate",
            "not_applicable",
            "Agent assignment proof is not required until prompt lock or imagegen.",
            severity="info",
        )

    valid_statuses = {
        "actual_multi_agent",
        "fallback_local_passes_with_limitation_recorded",
    }
    assignment_status = pregen.get("agent_assignment_status") if isinstance(pregen, dict) else None
    prompt_outputs = []
    if isinstance(pregen, dict):
        prompt_outputs = (
            pregen.get("prompt_room_outputs")
            or pregen.get("agent_outputs")
            or []
        )

    matrix_text = _read_text(matrix_path)
    assignment_trace_present = any(
        event.get("state")
        in {
            "DISCOVER_AND_ASSIGN_AGENTS",
            "PROMPT_REVISION_AGENT_ASSIGNMENT",
            "AGENT_ASSIGNMENT_GATE_PROOF",
        }
        and str(event.get("status", "")).lower()
        in {
            "complete",
            "actual_multi_agent",
            "fallback_local_passes",
            "revised_pending_creator_approval",
        }
        for event in events
    )

    missing = []
    if not matrix_path.exists():
        missing.append(f"runs/{run_dir.name}/debates/agent_assignment_matrix.md")
    if assignment_status not in valid_statuses:
        missing.append("evals/pre_generation_eval.json.agent_assignment_status")
    if not prompt_review_path.exists():
        missing.append(f"runs/{run_dir.name}/debates/prompt_room/prompt_review.md")
    if not prompt_outputs:
        missing.append("evals/pre_generation_eval.json.prompt_room_outputs_or_agent_outputs")
    if not assignment_trace_present:
        missing.append("logs/trace.jsonl.DISCOVER_AND_ASSIGN_AGENTS")
    if matrix_path.exists() and not (
        "actual_multi_agent" in matrix_text
        or "fallback_local_passes" in matrix_text
    ):
        missing.append("debates/agent_assignment_matrix.md.assignment_mode")

    status = "pass" if not missing and not trace_errors else "fail"
    summary = (
        "Agent assignment proof is complete before prompt lock or imagegen."
        if status == "pass"
        else "Agent assignment proof is incomplete before prompt lock or imagegen."
    )
    return _check(
        "agent_assignment_gate",
        status,
        summary,
        path=f"runs/{run_dir.name}/debates/agent_assignment_matrix.md",
        assignment_status=assignment_status,
        prompt_outputs=prompt_outputs,
        assignment_trace_present=assignment_trace_present,
        missing_requirements=missing,
        trace_errors=trace_errors,
        failure_code=None if not missing and not trace_errors else "AGENT_ASSIGNMENT_MISSING",
        severity="blocker",
    )


def _check_approvals_cover_required_gates(run_dir: Path) -> dict[str, Any]:
    approvals = _read_text(run_dir / "docs/approvals.md")
    section_aliases = {
        "Idea Lock": ["Idea Lock", "HITL Idea Lock"],
        "Story / Slide Count Lock": [
            "Story / Slide Count Lock",
            "HITL Story Lock",
        ],
        "Prompt Lock": ["Prompt Lock", "HITL Prompt Lock"],
        "Image QA": ["Image QA", "HITL Image QA"],
        "Final Package": ["Final Package", "HITL Local Execution Approval"],
    }
    missing_sections = [
        gate
        for gate in REQUIRED_APPROVAL_GATES
        if not any(f"## {alias}" in approvals for alias in section_aliases[gate])
    ]
    approved_sections = {
        "Idea Lock": _section_contains_any(
            approvals, section_aliases["Idea Lock"], "Status: approved"
        ),
        "Story / Slide Count Lock": _section_contains(
            approvals, "Story / Slide Count Lock", "Status: approved"
        )
        or _section_contains_any(
            approvals, section_aliases["Story / Slide Count Lock"], "Status: approved"
        ),
        "Prompt Lock": _section_contains_any(
            approvals, section_aliases["Prompt Lock"], "Status: approved"
        ),
        "Image QA": _section_contains_any(
            approvals, section_aliases["Image QA"], "Status: not started"
        )
        or _section_contains_any(
            approvals, section_aliases["Image QA"], "Status: failed"
        )
        or _section_contains_any(
            approvals, section_aliases["Image QA"], "Status: rejected"
        ),
        "Final Package": _section_contains(
            approvals, "Final Package", "Status: not started"
        )
        or _section_contains(
            approvals, "Final Package", "Status: blocked"
        )
        or _section_contains_any(
            approvals,
            section_aliases["Final Package"],
            "Final carousel generation: still blocked",
        ),
    }
    status = "pass" if not missing_sections and all(approved_sections.values()) else "fail"
    return _check(
        "approvals_cover_required_gates",
        status,
        "Approvals file records required HITL gates and current stopped gates.",
        path=f"runs/{run_dir.name}/docs/approvals.md",
        missing_sections=missing_sections,
        gate_evidence=approved_sections,
        severity="blocker",
    )


def _check_local_identity_execution_report(run_dir: Path) -> dict[str, Any]:
    path = run_dir / "evals/local_identity_execution_report.json"
    report = _read_json(path)
    if not path.exists():
        return _check(
            "local_identity_execution_report",
            "not_applicable",
            "No local identity execution report exists for this run.",
            path=f"runs/{run_dir.name}/evals/local_identity_execution_report.json",
            severity="info",
        )

    blocked_stall = (
        isinstance(report, dict)
        and report.get("status") == "blocked"
        and report.get("failure_code") == "LOCAL_CPU_EXECUTION_STALLED"
        and report.get("identity_proof_generated") is False
        and report.get("final_artwork_generated") is False
    )
    return _check(
        "local_identity_execution_report",
        "pass" if blocked_stall else "fail",
        "Local identity execution report records CPU stall and blocks final art.",
        path=f"runs/{run_dir.name}/evals/local_identity_execution_report.json",
        failure_code=report.get("failure_code") if isinstance(report, dict) else None,
        identity_proof_generated=(
            report.get("identity_proof_generated") if isinstance(report, dict) else None
        ),
        final_artwork_generated=(
            report.get("final_artwork_generated") if isinstance(report, dict) else None
        ),
        final_imagegen_allowed=not blocked_stall,
        severity="blocker",
    )


def _iter_manifest_refs(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    groups = manifest.get("reference_groups") or {}
    for group_refs in groups.values():
        if isinstance(group_refs, list):
            refs.extend(ref for ref in group_refs if isinstance(ref, dict))
    text_refs = manifest.get("text_and_brand_references") or []
    refs.extend(ref for ref in text_refs if isinstance(ref, dict))
    return refs


def _iter_legacy_manifest_paths(manifest: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    identity_refs = manifest.get("identity_references") or {}
    for value in identity_refs.values():
        if isinstance(value, list):
            paths.extend(item for item in value if isinstance(item, str))
    for key in [
        "style_references",
        "role_contact_sheets",
        "selected_generation_bundle",
    ]:
        value = manifest.get(key) or []
        if isinstance(value, list):
            paths.extend(item for item in value if isinstance(item, str))
    for key in [
        "text_style_reference",
        "brand_reference",
        "identity_dossier",
        "identity_generation_preflight",
    ]:
        value = manifest.get(key)
        if isinstance(value, str):
            paths.append(value)
    return sorted(set(paths))


def _reference_role_errors(groups: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for group_name, subject in [
        ("aachu_face_identity", "aachu"),
        ("zuv_face_identity", "zuv"),
    ]:
        for index, ref in enumerate(groups.get(group_name) or []):
            path = str(ref.get("path", ""))
            if ref.get("role") != group_name:
                errors.append(f"{group_name}[{index}].role")
            if ref.get("subject") != subject:
                errors.append(f"{group_name}[{index}].subject")
            if ref.get("dossier_role") != "face_anchor":
                errors.append(f"{group_name}[{index}].dossier_role")
            if f"references/identity/{subject}/face/" not in path:
                errors.append(f"{group_name}[{index}].path_not_face_dir")
            if ref.get("input_kind") != "local_image_file":
                errors.append(f"{group_name}[{index}].input_kind")
            if ref.get("delivery_mode") != "view_image_before_imagegen":
                errors.append(f"{group_name}[{index}].delivery_mode")
    return errors


def _check_all_prompts(
    root: Path,
    run_dir: Path,
    check_id: str,
    summary: str,
    evaluator,
    workflow: dict[str, Any],
) -> dict[str, Any]:
    prompt_paths = _prompt_files(run_dir)
    if not prompt_paths:
        return _prompt_not_applicable(check_id, run_dir)

    prompt_results = []
    for prompt_path in prompt_paths:
        prompt = _read_text(prompt_path)
        evidence = evaluator(prompt)
        prompt_results.append(
            {
                "path": _rel(prompt_path, root),
                "status": "pass" if all(evidence.values()) else "fail",
                "evidence": evidence,
            }
        )

    status = "pass" if all(item["status"] == "pass" for item in prompt_results) else "fail"
    return _check(
        check_id,
        status,
        summary,
        failure_code=None if status == "pass" else _default_failure_code(check_id),
        prompt_results=prompt_results,
        workflow_type=workflow["type"],
        severity="blocker",
    )


def _story_contract(run_dir: Path) -> dict[str, Any]:
    required_phrases: list[str] = []
    for rel_path in [
        "planning/selected_idea.json",
        "planning/story_concept.json",
        "planning/slide_beat_map.json",
    ]:
        required_phrases.extend(_contract_phrase_values(_read_json(run_dir / rel_path)))

    deduped: list[str] = []
    for phrase in required_phrases:
        if phrase not in deduped:
            deduped.append(phrase)

    return {
        "source": "run_artifacts" if deduped else "not_available",
        "required_phrases": deduped,
    }


def _contract_phrase_values(value: Any) -> list[str]:
    phrases: list[str] = []
    if isinstance(value, str) and value.strip():
        phrases.append(value.strip())
    elif isinstance(value, list):
        for item in value:
            phrases.extend(_contract_phrase_values(item))
    elif isinstance(value, dict):
        for key in (
            "exact_on_image_text",
            "exact_text",
            "on_image_text",
            "text",
        ):
            phrases.extend(_contract_phrase_values(value.get(key)))
        for key in ("selected_ideas", "slides", "beats", "assets"):
            phrases.extend(_contract_phrase_values(value.get(key)))
    return phrases


def _normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def _read_primary_prompt(run_dir: Path) -> str:
    return _read_text(_primary_prompt_path(run_dir))


def _primary_prompt_path(run_dir: Path) -> Path:
    return run_dir / "prompts/slide_01_4x5_prompt.txt"


def _primary_prompt_rel(run_dir: Path) -> str:
    return f"runs/{run_dir.name}/prompts/slide_01_4x5_prompt.txt"


def _prompt_not_applicable(check_id: str, run_dir: Path) -> dict[str, Any]:
    return _check(
        check_id,
        "not_applicable",
        "No slide prompt files are present for this run.",
        path=f"runs/{run_dir.name}/prompts/",
        severity="info",
    )


def _imagegen_was_attempted(run_dir: Path) -> bool:
    events, _ = _read_jsonl(run_dir / "logs/trace.jsonl")
    if any(event.get("state") == "GENERATE_IMAGES_WITH_IMAGEGEN" for event in events):
        return True
    images_dir = run_dir / "images"
    return images_dir.exists() and any(images_dir.glob("*.png"))


def _proof_has_image_roles(proof: Any) -> bool:
    if not isinstance(proof, dict):
        return False
    confirmed_roles = proof.get("reference_roles_confirmed")
    if isinstance(confirmed_roles, list):
        role_text = {str(role) for role in confirmed_roles}
        if {"aachu_face_identity", "zuv_face_identity"}.issubset(role_text):
            return True
    loaded_paths = proof.get("loaded_reference_paths")
    if isinstance(loaded_paths, list):
        path_text = {str(path) for path in loaded_paths}
        has_aachu_face = any(
            "references/identity/aachu/face/" in path for path in path_text
        )
        has_zuv_face = any(
            "references/identity/zuv/face/" in path for path in path_text
        )
        if has_aachu_face and has_zuv_face:
            return True
    refs = proof.get("references") or proof.get("reference_images") or proof.get("inputs")
    if not isinstance(refs, list):
        return False
    roles = {str(item.get("role", "")) for item in refs if isinstance(item, dict)}
    return bool(
        {"aachu_face_identity", "zuv_face_identity"}.issubset(roles)
        or {"aachu_face_anchor", "zuv_face_anchor"}.issubset(roles)
    )


def _manifest_queue_count(manifest: Any) -> int:
    if not isinstance(manifest, dict):
        return 0
    queue = manifest.get("view_image_queue") or []
    return int(manifest.get("view_image_queue_count") or len(queue))


def _prepare_references_if_needed(root: Path, run_id: str) -> None:
    run_dir = root / "runs" / run_id
    if not _prompt_files(run_dir):
        return
    root_text = str(root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    from scripts.prepare_imagegen_reference_context import (
        build_reference_context,
        write_reference_context,
    )

    context = build_reference_context(root, run_id)
    write_reference_context(root, context)


def _write_review_loop_artifact(run_dir: Path, result: dict[str, Any]) -> Path:
    evals_dir = run_dir / "evals"
    evals_dir.mkdir(parents=True, exist_ok=True)
    path = evals_dir / "repo_qa_review_loop.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return path


def _only_human_or_external_blockers(blockers: list[dict[str, Any]]) -> bool:
    human_or_external_codes = {
        "REFERENCE_VISIBILITY_PROOF_REQUIRED_BEFORE_FINAL_IMAGEGEN",
        "LOCAL_CPU_EXECUTION_STALLED",
        "LOCAL_WORKFLOW_MISSING",
        "IMAGE_QA_FAILED",
        "AGENT_ASSIGNMENT_MISSING",
    }
    codes = {
        blocker.get("failure_code")
        for blocker in blockers
        if blocker.get("failure_code")
    }
    return bool(codes) and codes.issubset(human_or_external_codes)


def _final_artifacts(run_dir: Path) -> list[str]:
    candidates: list[Path] = []
    for dirname in ["final", "package"]:
        path = run_dir / dirname
        if path.exists():
            candidates.extend(item for item in path.rglob("*") if item.is_file())
    return [f"runs/{run_dir.name}/{item.relative_to(run_dir)}" for item in candidates]


def _read_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return None


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(errors="replace")


def _read_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    events: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    if not path.exists():
        return events, [{"line": 0, "error": "missing file"}]

    for line_number, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
        if not line.strip():
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append({"line": line_number, "error": str(exc)})
            continue
        if isinstance(parsed, dict):
            events.append(parsed)
        else:
            errors.append({"line": line_number, "error": "not a JSON object"})
    return events, errors


def _first_event_index(
    events: list[dict[str, Any]], state: str, statuses: set[str] | None
) -> int | None:
    for index, event in enumerate(events):
        if event.get("state") != state:
            continue
        if statuses is None or event.get("status") in statuses:
            return index
    return None


def _section_contains(text: str, section: str, needle: str) -> bool:
    marker = f"## {section}"
    if marker not in text:
        return False
    body = text.split(marker, 1)[1]
    next_marker = body.find("\n## ")
    if next_marker >= 0:
        body = body[:next_marker]
    return needle in body or needle in body.replace("`", "")


def _section_contains_any(text: str, sections: list[str], needle: str) -> bool:
    return any(_section_contains(text, section, needle) for section in sections)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _check(
    check_id: str,
    status: str,
    summary: str,
    *,
    severity: str = "info",
    **details: Any,
) -> dict[str, Any]:
    return {
        "id": check_id,
        "status": status,
        "severity": severity,
        "summary": summary,
        **details,
    }


def _failure_code_for_check(check: dict[str, Any]) -> str:
    code = check.get("failure_code")
    if code:
        return str(code)
    return _default_failure_code(str(check.get("id", "unknown_check")))


def _default_failure_code(check_id: str) -> str:
    codes = {
        "prompt_story_contract": "PROMPT_STORY_CONTRACT_MISMATCH",
        "prompt_reference_gate": "PROMPT_REFERENCE_GATE_MISSING",
        "prompt_forbidden_role_reversal": "PROMPT_ROLE_REVERSAL_RISK",
        "reference_manifest_integrity": "REFERENCE_MANIFEST_INVALID",
        "skill_contract_present": "SKILL_CONTRACT_MISSING",
        "master_prompt_present": "MASTER_PROMPT_MISSING",
        "required_templates_present": "REQUIRED_TEMPLATE_MISSING",
        "final_package_not_started": "FINAL_PACKAGE_STARTED_WHILE_BLOCKED",
        "accepted_candidate_filename_guard": "ACCEPTED_CANDIDATE_FILENAME_UNSAFE",
        "trace_jsonl_valid": "TRACE_JSONL_INVALID",
        "approvals_cover_required_gates": "HITL_APPROVALS_INCOMPLETE",
    }
    return codes.get(check_id, f"{check_id.upper()}_FAILED")


def _empty_reference_summary() -> dict[str, Any]:
    return {
        "aachu_face_identity_count": 0,
        "zuv_face_identity_count": 0,
        "expression_support_count": 0,
        "together_body_language_count": 0,
        "style_reference_count": 0,
        "text_and_brand_reference_count": 0,
        "view_image_queue_count": 0,
        "view_image_queue_actual_count": 0,
        "prompt_only_allowed": None,
    }


def _render_report(audit: dict[str, Any]) -> str:
    lines = [
        "# A Story Repo QA Review",
        "",
        f"Run: `{audit['run_id']}`",
        f"Overall status: `{audit['overall_status']}`",
        "",
        "## Blocking Findings",
        "",
    ]
    blocking = audit.get("blocking_findings") or []
    if not blocking:
        lines.append("- None.")
    else:
        for finding in blocking:
            code = finding.get("failure_code") or "NO_FAILURE_CODE"
            lines.append(f"- `{finding['id']}` / `{code}`: {finding.get('summary')}")

    lines.extend(["", "## Reference Summary", ""])
    for key, value in (audit.get("reference_summary") or {}).items():
        lines.append(f"- `{key}`: `{value}`")

    lines.extend(["", "## Checks", ""])
    for check in audit.get("checks", []):
        code = check.get("failure_code")
        suffix = f" (`{code}`)" if code else ""
        lines.append(
            f"- `{check['id']}`: `{check['status']}` / `{check['severity']}`{suffix}"
        )
    lines.append("")
    return "\n".join(lines)


def _rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit A Story of Two run artifacts.")
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument("--run-id", required=True, help="Run id under runs/.")
    parser.add_argument("--loop", action="store_true", help="Run bounded review loop.")
    parser.add_argument("--max-iterations", type=int, default=3)
    parser.add_argument(
        "--no-prepare-references",
        action="store_true",
        help="Do not regenerate imagegen reference context before QA.",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write repo_qa_review.json and repo_qa_review.md under the run evals folder.",
    )
    args = parser.parse_args()

    if args.loop:
        audit = run_review_loop(
            args.repo_root,
            args.run_id,
            max_iterations=args.max_iterations,
            prepare_references=not args.no_prepare_references,
        )
    elif args.write:
        audit = write_qa_artifacts(args.repo_root, args.run_id)
    else:
        audit = run_repo_qa(args.repo_root, args.run_id)
    print(json.dumps(audit, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
