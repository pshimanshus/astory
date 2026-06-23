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
    ".agents/skills/astory/templates/evals/pre_imagegen_blocker_check.json",
    ".agents/skills/astory/templates/evals/image_quality_eval.json",
    ".agents/skills/astory/templates/debates/agent_assignment_matrix.md",
    ".agents/skills/astory/templates/agents/story_room_agent_prompt.md",
    ".agents/skills/astory/templates/agents/visual_scene_discussion_prompt.md",
    ".agents/skills/astory/templates/agents/review_room_agent_prompt.md",
    ".agents/skills/astory/templates/prompts/slide_prompt.txt",
    ".agents/skills/astory/templates/planning/memory_recall.md",
    ".agents/skills/astory/templates/planning/scene_landing_preview.md",
    ".agents/skills/astory/templates/planning/novelty_candidate_ledger.json",
    ".agents/skills/astory/templates/planning/source_winner_novelty_model.json",
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
MIN_RAW_FACE_ANCHORS_PER_SUBJECT = 4
MIN_FACE_VIEW_BUCKETS_PER_SUBJECT = 2
YELLOW_PRONE_PROMPT_TERMS = [
    "warm lamplight",
    "warm glow",
    "warm ivory",
    "warm negative space",
    "warm minimal",
    "warm watercolor",
    "warm skin shading",
    "cream paper",
    "terracotta",
    "warm tan",
    "tan pants",
    "camel",
    "vintage palette",
]
PROMPT_OVERLOAD_MAX_NONEMPTY_LINES = 115
PROMPT_OVERLOAD_MAX_MAJOR_SECTIONS = 10
PROMPT_MAJOR_SECTION_RE = re.compile(r"^[A-Z][A-Z0-9 /_-]{2,}:$")
PROMPT_CANVAS_SIZE_RE = re.compile(r"\b1080\s*[x×]\s*1350\s*px\b", re.IGNORECASE)
NON_PORTRAIT_SURFACE_RE = re.compile(
    r"\b(?:1\s*:\s*1|9\s*:\s*16|1080\s*(?:px)?\s*(?:wide\s+by|x)\s*1080|1080\s*(?:px)?\s*(?:tall|high)|square)\b",
    re.IGNORECASE,
)
HARD_IMAGE_FAILURE_CODES = {
    "YELLOW_PAPER_CAST",
    "IDENTITY_DRIFT",
    "FACE_MERGE",
    "STYLE_DRIFT",
    "PROMPT_OVERLOAD",
    "BRANDMARK_MISSING",
    "WRONG_CANVAS_SIZE",
    "VISUAL_SETTING_CONTRADICTION",
    "TEXT_UNREADABLE",
    "TEXT_NOT_EXACT",
    "ANATOMY_FAILURE",
}
PRE_IMAGEGEN_BLOCKER_FIELDS = [
    "emotional_state_check",
    "identity_reference_collision_check",
    "fallback_review_check",
    "creator_prompt_lock_check",
    "canvas_output_expectation",
    "imagegen_allowed",
]
ACHE_PROMPT_TERMS = (
    "tere bina",
    "khaali",
    "without him",
    "without them",
    "missing",
    "lost",
    "lonely",
    "empty",
    "hollow",
    "absence",
    "ache",
)
POSITIVE_EXPRESSION_RE = re.compile(
    r"\b(smile|smiles|smiling|smirk|smirking|pleasant|coy|nostalgic)\b",
    re.IGNORECASE,
)
NEGATED_EXPRESSION_MARKERS = (
    "no smile",
    "no smiles",
    "no smirk",
    "unsmiling",
    "not smiling",
    "must not smile",
    "must not",
    "do not smile",
    "do not copy",
    "do not use",
    "not copy",
    "without smiling",
    "without a smile",
    "hard no",
)
REFERENCE_SCENE_COLLISION_TERMS = {
    "cafe": ("cafe", "coffee", "cup", "friends table", "public table"),
    "club": ("club", "dance floor", "bar"),
    "party": ("party", "birthday", "gathering"),
}


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
        _check_reference_active_identity_inputs(root, run_dir),
        _check_memory_recall(root, run_dir, workflow),
        _check_prompt_story_contract(root, run_dir, workflow),
        _check_prompt_reference_gate(root, run_dir, workflow),
        _check_prompt_forbidden_role_reversal(root, run_dir, workflow),
        _check_prompt_canvas_size(root, run_dir, workflow),
        _check_prompt_brandmark_gate(root, run_dir, workflow),
        _check_prompt_palette_conflict(root, run_dir, workflow),
        _check_prompt_overload(root, run_dir, workflow),
        _check_pre_imagegen_blocker_check(root, run_dir, workflow),
        _check_reference_visibility_proof(root, run_dir),
        _check_gold_standard_identity_route_gate(root, run_dir, workflow),
        _check_image_qa_blocks_final_package(run_dir),
        _check_final_package_has_illustration_proof(run_dir),
        _check_final_package_not_started(run_dir),
        _check_accepted_candidate_filename_guard(run_dir),
        _check_generation_stops_after_hard_reject(run_dir),
        _check_prompt_repair_reapproval(run_dir),
        _check_trace_jsonl_valid(run_dir),
        _check_novelty_candidate_ledger(run_dir),
        _check_scene_landing_preview(run_dir),
        _check_source_winner_novelty_model(run_dir),
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


def _check_reference_active_identity_inputs(root: Path, run_dir: Path) -> dict[str, Any]:
    manifest_path = run_dir / "references-used/selected_references.json"
    manifest = _read_json(manifest_path)
    if not isinstance(manifest, dict) or not manifest.get("reference_groups"):
        return _check(
            "reference_active_identity_inputs",
            "not_applicable",
            "No active imagegen reference manifest exists for this workflow.",
            path=_rel(manifest_path, root),
            failure_code=None,
            severity="info",
        )

    active_paths = _manifest_view_image_paths(manifest)
    errors = _raw_identity_input_errors(active_paths)
    diversity_errors = _identity_reference_diversity_errors(
        manifest.get("reference_groups") or {}
    )
    all_errors = errors + diversity_errors
    failure_code = None
    if diversity_errors and not errors:
        failure_code = "IDENTITY_REFERENCE_DIVERSITY_MISSING"
    elif all_errors:
        failure_code = "IDENTITY_REFERENCE_INPUT_UNPROVEN"
    return _check(
        "reference_active_identity_inputs",
        "pass" if not all_errors else "fail",
        (
            "Active imagegen queue includes diverse raw Aachu/Zuv face anchors."
            if not all_errors
            else "Active imagegen queue does not prove diverse raw Aachu/Zuv face-anchor inputs."
        ),
        path=_rel(manifest_path, root),
        active_view_image_queue=active_paths,
        raw_aachu_face_anchor_count=_raw_face_anchor_count(active_paths, "aachu"),
        raw_zuv_face_anchor_count=_raw_face_anchor_count(active_paths, "zuv"),
        identity_view_summary=_identity_reference_view_summary(
            manifest.get("reference_groups") or {}
        ),
        identity_input_errors=all_errors,
        failure_code=failure_code,
        final_imagegen_allowed=not all_errors,
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


def _check_prompt_palette_conflict(
    root: Path, run_dir: Path, workflow: dict[str, Any]
) -> dict[str, Any]:
    prompt_paths = _prompt_files(run_dir)
    if not prompt_paths:
        return _prompt_not_applicable("prompt_palette_conflict", run_dir)

    prompt_results = []
    failed = []
    for path in prompt_paths:
        text = _read_text(path)
        lower = text.lower()
        yellow_prone_terms = [
            term for term in YELLOW_PRONE_PROMPT_TERMS if term in lower
        ]
        has_no_yellow = "no yellow" in lower or "not yellow" in lower
        has_neutral_paper = (
            "neutral off-white" in lower
            or "neutral white/off-white" in lower
            or "neutral premium ivory/off-white" in lower
        )
        conflict = len(yellow_prone_terms) >= 3 and has_no_yellow
        result = {
            "path": _rel(path, root),
            "status": "fail" if conflict else "pass",
            "yellow_prone_terms": yellow_prone_terms,
            "has_no_yellow_constraint": has_no_yellow,
            "has_neutral_paper_constraint": has_neutral_paper,
        }
        prompt_results.append(result)
        if conflict:
            failed.append(result)

    return _check(
        "prompt_palette_conflict",
        "pass" if not failed else "fail",
        (
            "Prompt palette language avoids yellow-prone positive conflicts."
            if not failed
            else "Prompt palette language contains yellow-prone positive cues that conflict with the no-yellow rule."
        ),
        prompt_results=prompt_results,
        failed_prompt_count=len(failed),
        failure_code=None if not failed else "PROMPT_PALETTE_CONFLICT",
        workflow_type=workflow.get("type"),
        severity="blocker",
    )


def _check_prompt_canvas_size(
    root: Path, run_dir: Path, workflow: dict[str, Any]
) -> dict[str, Any]:
    prompt_paths = _prompt_files(run_dir)
    if not prompt_paths:
        return _prompt_not_applicable("prompt_canvas_size", run_dir)

    prompt_results = []
    failed = []
    for path in prompt_paths:
        text = _read_text(path)
        has_portrait_gate = bool(PROMPT_CANVAS_SIZE_RE.search(text))
        has_non_portrait_surface = bool(NON_PORTRAIT_SURFACE_RE.search(text))
        canvas_size_errors = []
        if not has_portrait_gate:
            canvas_size_errors.append("missing_1080x1350_px")
        if has_non_portrait_surface:
            canvas_size_errors.append("non_portrait_surface_language")

        result = {
            "path": _rel(path, root),
            "status": "fail" if canvas_size_errors else "pass",
            "has_1080x1350_px_gate": has_portrait_gate,
            "has_non_portrait_surface_language": has_non_portrait_surface,
            "canvas_size_errors": canvas_size_errors,
        }
        prompt_results.append(result)
        if canvas_size_errors:
            failed.append(result)

    return _check(
        "prompt_canvas_size",
        "pass" if not failed else "fail",
        (
            "Every imagegen prompt explicitly requests a native 1080x1350 px portrait canvas."
            if not failed
            else "One or more imagegen prompts are missing the native 1080x1350 px portrait canvas gate."
        ),
        prompt_results=prompt_results,
        failed_prompt_count=len(failed),
        failure_code=None if not failed else "PROMPT_CANVAS_SIZE_MISSING",
        workflow_type=workflow.get("type"),
        severity="blocker",
    )


def _check_prompt_brandmark_gate(
    root: Path, run_dir: Path, workflow: dict[str, Any]
) -> dict[str, Any]:
    prompt_paths = _prompt_files(run_dir)
    if not prompt_paths:
        return _prompt_not_applicable("prompt_brandmark_gate", run_dir)

    prompt_results = []
    failed = []
    for path in prompt_paths:
        text = _read_text(path).lower()
        brandmark_errors = []
        if "@a.storyof.two" not in text:
            brandmark_errors.append("missing_at_storyof_two")
        if "top-right" not in text and "top right" not in text:
            brandmark_errors.append("missing_top_right_placement")

        result = {
            "path": _rel(path, root),
            "status": "fail" if brandmark_errors else "pass",
            "brandmark_errors": brandmark_errors,
        }
        prompt_results.append(result)
        if brandmark_errors:
            failed.append(result)

    return _check(
        "prompt_brandmark_gate",
        "pass" if not failed else "fail",
        (
            "Every imagegen prompt requires the tiny top-right @a.storyof.two brandmark."
            if not failed
            else "One or more imagegen prompts are missing the top-right @a.storyof.two brandmark gate."
        ),
        prompt_results=prompt_results,
        failed_prompt_count=len(failed),
        failure_code=None if not failed else "PROMPT_BRANDMARK_MISSING",
        workflow_type=workflow.get("type"),
        severity="blocker",
    )


def _check_prompt_overload(
    root: Path, run_dir: Path, workflow: dict[str, Any]
) -> dict[str, Any]:
    prompt_paths = _prompt_files(run_dir)
    if not prompt_paths:
        return _prompt_not_applicable("prompt_overload", run_dir)

    prompt_results = []
    failed = []
    for path in prompt_paths:
        text = _read_text(path)
        nonempty_lines = [line for line in text.splitlines() if line.strip()]
        major_sections = [
            line.strip()
            for line in text.splitlines()
            if PROMPT_MAJOR_SECTION_RE.match(line.strip())
        ]
        overload_reasons = []
        if len(nonempty_lines) > PROMPT_OVERLOAD_MAX_NONEMPTY_LINES:
            overload_reasons.append("too_many_nonempty_lines")
        if len(major_sections) > PROMPT_OVERLOAD_MAX_MAJOR_SECTIONS:
            overload_reasons.append("too_many_major_sections")

        result = {
            "path": _rel(path, root),
            "status": "fail" if overload_reasons else "pass",
            "nonempty_line_count": len(nonempty_lines),
            "max_nonempty_lines": PROMPT_OVERLOAD_MAX_NONEMPTY_LINES,
            "major_section_count": len(major_sections),
            "max_major_sections": PROMPT_OVERLOAD_MAX_MAJOR_SECTIONS,
            "major_sections": major_sections,
            "overload_reasons": overload_reasons,
        }
        prompt_results.append(result)
        if overload_reasons:
            failed.append(result)

    return _check(
        "prompt_overload",
        "pass" if not failed else "fail",
        (
            "Prompt instruction stack is compact enough for imagegen."
            if not failed
            else "Prompt instruction stack is overloaded with too many competing constraints."
        ),
        prompt_results=prompt_results,
        failed_prompt_count=len(failed),
        failure_code=None if not failed else "PROMPT_OVERLOAD",
        workflow_type=workflow.get("type"),
        severity="blocker",
    )


def _check_pre_imagegen_blocker_check(
    root: Path, run_dir: Path, workflow: dict[str, Any]
) -> dict[str, Any]:
    artifact_path = run_dir / "evals/pre_imagegen_blocker_check.json"
    if not _pre_imagegen_blocker_check_required(run_dir, workflow):
        return _check(
            "pre_imagegen_blocker_check",
            "not_applicable",
            "Pre-imagegen blocker check is not required until prompt/reference loading or imagegen begins.",
            path=f"runs/{run_dir.name}/evals/pre_imagegen_blocker_check.json",
            failure_code=None,
            final_imagegen_allowed=False,
            severity="info",
        )

    emotional_state_check = _pre_imagegen_emotional_state_check(root, run_dir)
    identity_reference_collision_check = _pre_imagegen_identity_collision_check(
        root, run_dir
    )
    fallback_review_check = _pre_imagegen_fallback_review_check(run_dir)
    creator_prompt_lock_check = _pre_imagegen_creator_prompt_lock_check(run_dir)
    canvas_output_expectation = _pre_imagegen_canvas_output_expectation(root, run_dir)
    computed_checks = [
        emotional_state_check,
        identity_reference_collision_check,
        fallback_review_check,
        creator_prompt_lock_check,
        canvas_output_expectation,
    ]
    computed_failure_codes = [
        code
        for check in computed_checks
        for code in check.get("failure_codes", [])
        if code
    ]

    if not artifact_path.exists():
        return _check(
            "pre_imagegen_blocker_check",
            "fail",
            "Pre-imagegen blocker check artifact is required before imagegen.",
            path=f"runs/{run_dir.name}/evals/pre_imagegen_blocker_check.json",
            missing_fields=PRE_IMAGEGEN_BLOCKER_FIELDS,
            computed_failure_codes=computed_failure_codes,
            emotional_state_check=emotional_state_check,
            identity_reference_collision_check=identity_reference_collision_check,
            fallback_review_check=fallback_review_check,
            creator_prompt_lock_check=creator_prompt_lock_check,
            canvas_output_expectation=canvas_output_expectation,
            failure_code="PRE_IMAGEGEN_BLOCKER_CHECK_MISSING",
            final_imagegen_allowed=False,
            severity="blocker",
        )

    artifact = _read_json(artifact_path)
    if not isinstance(artifact, dict):
        return _check(
            "pre_imagegen_blocker_check",
            "fail",
            "Pre-imagegen blocker check artifact is invalid JSON.",
            path=f"runs/{run_dir.name}/evals/pre_imagegen_blocker_check.json",
            missing_fields=PRE_IMAGEGEN_BLOCKER_FIELDS,
            computed_failure_codes=computed_failure_codes,
            emotional_state_check=emotional_state_check,
            identity_reference_collision_check=identity_reference_collision_check,
            fallback_review_check=fallback_review_check,
            creator_prompt_lock_check=creator_prompt_lock_check,
            canvas_output_expectation=canvas_output_expectation,
            failure_code="PRE_IMAGEGEN_BLOCKER_CHECK_INVALID",
            final_imagegen_allowed=False,
            severity="blocker",
        )

    missing_fields = [
        field for field in PRE_IMAGEGEN_BLOCKER_FIELDS if field not in artifact
    ]
    artifact_failure_codes = _pre_imagegen_artifact_failure_codes(artifact)
    all_failure_codes = list(
        dict.fromkeys(missing_fields + artifact_failure_codes + computed_failure_codes)
    )
    imagegen_allowed = (
        artifact.get("imagegen_allowed") is True and not all_failure_codes
    )
    status = "pass" if imagegen_allowed else "fail"
    return _check(
        "pre_imagegen_blocker_check",
        status,
        (
            "Pre-imagegen blocker check allows imagegen."
            if status == "pass"
            else "Pre-imagegen blocker check blocks imagegen until emotional, reference, fallback, prompt-lock, and canvas risks are cleared."
        ),
        path=f"runs/{run_dir.name}/evals/pre_imagegen_blocker_check.json",
        missing_fields=missing_fields,
        artifact_failure_codes=artifact_failure_codes,
        computed_failure_codes=computed_failure_codes,
        emotional_state_check=emotional_state_check,
        identity_reference_collision_check=identity_reference_collision_check,
        fallback_review_check=fallback_review_check,
        creator_prompt_lock_check=creator_prompt_lock_check,
        canvas_output_expectation=canvas_output_expectation,
        artifact_imagegen_allowed=artifact.get("imagegen_allowed"),
        failure_code=None if status == "pass" else "PRE_IMAGEGEN_BLOCKER_CHECK_FAILED",
        final_imagegen_allowed=imagegen_allowed,
        severity="blocker",
    )


def _pre_imagegen_blocker_check_required(
    run_dir: Path, workflow: dict[str, Any]
) -> bool:
    if workflow.get("type") in {"unknown_run", "local_identity_execution_run"}:
        return False
    if not _prompt_files(run_dir) and not _imagegen_was_attempted(run_dir):
        return False
    events, _ = _read_jsonl(run_dir / "logs/trace.jsonl")
    reference_or_generation_started = (
        (run_dir / "references-used/selected_references.json").exists()
        or (run_dir / "evals/imagegen_reference_load_plan.json").exists()
        or _imagegen_was_attempted(run_dir)
        or any(
            event.get("state")
            in {
                "LOAD_REFERENCE_IMAGES_IN_CONTEXT",
                "REVIEW_ROOM_IMAGEGEN_BLOCKER_CHECK",
                "GENERATE_IMAGES_WITH_IMAGEGEN",
            }
            for event in events
        )
    )
    return reference_or_generation_started


def _pre_imagegen_artifact_failure_codes(artifact: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for field in PRE_IMAGEGEN_BLOCKER_FIELDS:
        if field == "imagegen_allowed" or field not in artifact:
            continue
        value = artifact.get(field)
        status = str(value.get("status") if isinstance(value, dict) else value).lower()
        if status not in {"pass", "passed", "ok", "clear"}:
            if isinstance(value, dict) and value.get("failure_codes"):
                failures.extend(str(code) for code in value["failure_codes"])
            else:
                failures.append(f"{field.upper()}_FAILED")
    if artifact.get("imagegen_allowed") is not True:
        failures.append("PRE_IMAGEGEN_BLOCKER_CHECK_NOT_ALLOWED")
    return failures


def _pre_imagegen_emotional_state_check(root: Path, run_dir: Path) -> dict[str, Any]:
    prompt_results: list[dict[str, Any]] = []
    failure_codes: list[str] = []
    for prompt_path in _prompt_files(run_dir):
        text = _read_text(prompt_path)
        positive_terms = _positive_expression_terms(text)
        has_ache_context = any(term in text.lower() for term in ACHE_PROMPT_TERMS)
        forbids_smile = _prompt_forbids_smile(text)
        failed = bool(positive_terms and (has_ache_context or forbids_smile))
        if failed:
            failure_codes.append("EMOTIONAL_STATE_CONTRADICTION")
        prompt_results.append(
            {
                "path": _rel(prompt_path, root),
                "status": "fail" if failed else "pass",
                "positive_expression_terms": positive_terms,
                "has_ache_context": has_ache_context,
                "forbids_smile": forbids_smile,
            }
        )
    return {
        "status": "fail" if failure_codes else "pass",
        "prompt_results": prompt_results,
        "failure_codes": list(dict.fromkeys(failure_codes)),
    }


def _positive_expression_terms(prompt_text: str) -> list[str]:
    terms: list[str] = []
    for line in prompt_text.splitlines():
        lower = line.lower()
        if any(marker in lower for marker in NEGATED_EXPRESSION_MARKERS):
            continue
        terms.extend(match.group(0).lower() for match in POSITIVE_EXPRESSION_RE.finditer(line))
    return list(dict.fromkeys(terms))


def _pre_imagegen_identity_collision_check(
    root: Path, run_dir: Path
) -> dict[str, Any]:
    manifest = _read_json(run_dir / "references-used/selected_references.json")
    active_paths = _manifest_view_image_paths(manifest) if isinstance(manifest, dict) else []
    policy = _read_reference_policy(run_dir)
    policy_unsafe = set(policy.get("blocked_active_refs", []))
    policy_unsafe.update(policy.get("analysis_only_refs", []))
    policy_unsafe.update(policy.get("emotion_forbidden_refs", []))
    prompt_text = "\n".join(_read_text(path) for path in _prompt_files(run_dir))
    scene_terms = _prompt_scene_terms(prompt_text)
    prompt_forbids_smile = _prompt_forbids_smile(prompt_text)
    unsafe_active_refs: list[str] = []
    ref_reasons: dict[str, list[str]] = {}

    for path in active_paths:
        reasons: list[str] = []
        if path in policy_unsafe:
            reasons.append("active_ref_violates_reference_policy")
        if prompt_forbids_smile and _path_expression_bucket(path) in {"smile", "laugh"}:
            reasons.append("active_ref_violates_no_smile_beat")
        for scene_term in scene_terms:
            if _active_ref_has_scene_collision(path, scene_term):
                reasons.append(f"active_ref_scene_overlap:{scene_term}")
        if reasons:
            unsafe_active_refs.append(path)
            ref_reasons[path] = reasons

    return {
        "status": "fail" if unsafe_active_refs else "pass",
        "unsafe_active_refs": unsafe_active_refs,
        "reference_reasons": ref_reasons,
        "scene_terms": scene_terms,
        "failure_codes": ["IDENTITY_REFERENCE_POSE_COPY"] if unsafe_active_refs else [],
    }


def _pre_imagegen_fallback_review_check(run_dir: Path) -> dict[str, Any]:
    pregen = _read_json(run_dir / "evals/pre_generation_eval.json")
    assignment_status = pregen.get("agent_assignment_status") if isinstance(pregen, dict) else None
    has_major_correction = _has_major_creator_visual_correction(run_dir)
    failed = (
        assignment_status == "fallback_local_passes_with_limitation_recorded"
        and has_major_correction
    )
    return {
        "status": "fail" if failed else "pass",
        "agent_assignment_status": assignment_status,
        "major_creator_visual_correction": has_major_correction,
        "failure_codes": ["FALLBACK_REVIEW_AFTER_CREATOR_CORRECTION"] if failed else [],
    }


def _pre_imagegen_creator_prompt_lock_check(run_dir: Path) -> dict[str, Any]:
    has_major_correction = _has_major_creator_visual_correction(run_dir)
    approvals = _read_text(run_dir / "docs/approvals.md")
    prompt_section = _approval_section(approvals, ["Prompt Lock", "HITL Prompt Lock"])
    prompt_lock_approved = "status: approved" in prompt_section.lower()
    has_visible_prompt_summary = any(
        marker in prompt_section.lower()
        for marker in (
            "prompt summary",
            "slide-by-slide",
            "slide by slide",
            "prompt files",
            "prompts/",
            "prompt_review.md",
        )
    )
    broad_proceed_only = "proceed" in prompt_section.lower() and not has_visible_prompt_summary
    failed = has_major_correction and (
        broad_proceed_only or (prompt_lock_approved and not has_visible_prompt_summary)
    )
    return {
        "status": "fail" if failed else "pass",
        "major_creator_visual_correction": has_major_correction,
        "prompt_lock_approved": prompt_lock_approved,
        "has_visible_prompt_summary": has_visible_prompt_summary,
        "broad_proceed_only": broad_proceed_only,
        "failure_codes": ["PROMPT_LOCK_NOT_CREATOR_VISIBLE"] if failed else [],
    }


def _pre_imagegen_canvas_output_expectation(root: Path, run_dir: Path) -> dict[str, Any]:
    prompt_results: list[dict[str, Any]] = []
    failure_codes: list[str] = []
    for prompt_path in _prompt_files(run_dir):
        text = _read_text(prompt_path)
        missing_canvas = not PROMPT_CANVAS_SIZE_RE.search(text)
        non_portrait = bool(NON_PORTRAIT_SURFACE_RE.search(text))
        errors: list[str] = []
        if missing_canvas:
            errors.append("missing_1080x1350_px")
        if non_portrait:
            errors.append("non_portrait_surface_language")
        if errors:
            failure_codes.append("PROMPT_CANVAS_SIZE_MISSING")
        prompt_results.append(
            {
                "path": _rel(prompt_path, root),
                "status": "fail" if errors else "pass",
                "canvas_errors": errors,
            }
        )
    return {
        "status": "fail" if failure_codes else "pass",
        "prompt_results": prompt_results,
        "failure_codes": list(dict.fromkeys(failure_codes)),
    }


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
        validation = _validate_reference_visibility_proof(manifest, proof)
        status = "pass" if validation["valid"] else "fail"
        return _check(
            "reference_visibility_proof",
            status,
            validation["summary"],
            expected_artifact=proof_rel,
            failure_code=validation["failure_code"],
            final_imagegen_allowed=status == "pass",
            view_image_queue_count=_manifest_queue_count(manifest),
            load_plan_sha256=manifest.get("load_plan_sha256"),
            proof_load_plan_sha256=proof.get("load_plan_sha256"),
            missing_loaded_paths=validation.get("missing_loaded_paths", []),
            unexpected_loaded_paths=validation.get("unexpected_loaded_paths", []),
            validation_errors=validation.get("validation_errors", []),
            severity="blocker",
        )

    if imagegen_happened:
        return _check(
            "reference_visibility_proof",
            "fail",
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
        "fail",
        "Reference load plan requires a visibility proof before final imagegen; final generation remains blocked until it exists.",
        expected_artifact=proof_rel,
        failure_code="REFERENCE_VISIBILITY_PROOF_REQUIRED_BEFORE_FINAL_IMAGEGEN",
        final_imagegen_allowed=False,
        imagegen_attempted_without_proof=False,
        view_image_queue_count=_manifest_queue_count(manifest),
        severity="blocker",
    )


def _check_gold_standard_identity_route_gate(
    root: Path, run_dir: Path, workflow: dict[str, Any]
) -> dict[str, Any]:
    prompt_paths = _prompt_files(run_dir)
    if not prompt_paths and not _imagegen_was_attempted(run_dir):
        return _check(
            "gold_standard_identity_route_gate",
            "not_applicable",
            "Gold-standard identity route is not required until prompt work or imagegen begins.",
            workflow_type=workflow.get("type"),
            missing_requirements=[],
            failure_code=None,
            severity="info",
        )

    manifest_path = run_dir / "references-used/selected_references.json"
    manifest = _read_json(manifest_path)
    proof_rel = None
    if isinstance(manifest, dict):
        proof_rel = ((manifest.get("load_state") or {}).get("proof_artifact"))
    if not proof_rel:
        proof_rel = f"runs/{run_dir.name}/evals/imagegen_reference_visibility_proof.json"
    proof_path = root / proof_rel
    proof = _read_json(proof_path)
    pregen_path = run_dir / "evals/pre_generation_eval.json"
    pregen = _read_json(pregen_path)
    events, trace_errors = _read_jsonl(run_dir / "logs/trace.jsonl")

    groups = manifest.get("reference_groups") if isinstance(manifest, dict) else {}
    if not isinstance(groups, dict):
        groups = {}
    active_paths = _manifest_view_image_paths(manifest) if isinstance(manifest, dict) else []
    prompt_text = _normalize_text("\n".join(_read_text(path) for path in prompt_paths))
    prompt_lower = prompt_text.lower()

    style_count = _gold_standard_style_reference_count(groups)
    queue_count = _manifest_queue_count(manifest)
    prompt_outputs = _pregen_prompt_outputs(pregen)
    prompt_output_paths = [
        _resolve_run_artifact_path(root, run_dir, path) for path in prompt_outputs
    ]
    prompt_outputs_exist = bool(prompt_output_paths) and all(
        path.exists() for path in prompt_output_paths
    )

    missing: list[str] = []
    if not isinstance(manifest, dict):
        missing.append("references-used/selected_references.json")
    if len(groups.get("aachu_face_identity") or []) < 4:
        missing.append("aachu_face_identity_refs_lt_4")
    if len(groups.get("zuv_face_identity") or []) < 4:
        missing.append("zuv_face_identity_refs_lt_4")
    if style_count < 3:
        missing.append("style_reference_refs_lt_3")
    if queue_count < 11 or len(active_paths) < 11:
        missing.append("view_image_queue_lt_11")

    proof_validation = {"valid": False, "validation_errors": ["missing_manifest_or_proof"]}
    if isinstance(manifest, dict) and isinstance(proof, dict):
        proof_validation = _validate_reference_visibility_proof(manifest, proof)
    if not proof_path.exists() or not isinstance(proof, dict):
        missing.append("evals/imagegen_reference_visibility_proof.json")
    elif not proof_validation.get("valid"):
        missing.append("imagegen_reference_visibility_proof_valid")
    if isinstance(proof, dict):
        if proof.get("loaded_in_current_conversation") is not True:
            missing.append("loaded_in_current_conversation_true")
        if proof.get("loaded_count") != proof.get("expected_count"):
            missing.append("loaded_count_equals_expected_count")
        if int(proof.get("expected_count") or 0) < 11:
            missing.append("expected_count_at_least_11")

    if not isinstance(pregen, dict):
        missing.append("evals/pre_generation_eval.json")
    else:
        if pregen.get("agent_assignment_status") not in {
            "actual_multi_agent",
            "fallback_local_passes_with_limitation_recorded",
        }:
            missing.append("pre_generation_eval.agent_assignment_status")
        if not prompt_outputs:
            missing.append("pre_generation_eval.prompt_room_outputs")
        elif not prompt_outputs_exist:
            missing.append("pre_generation_eval.prompt_room_outputs_exist")

    required_files = [
        "debates/agent_assignment_matrix.md",
        "debates/prompt_room/prompt_review.md",
        "planning/scene_landing_preview.md",
        "planning/scene_options.json",
        "planning/selected_idea.json",
        "planning/slide_beat_map.json",
        "planning/slide_count_decision.md",
    ]
    for rel_path in required_files:
        if not (run_dir / rel_path).exists():
            missing.append(rel_path)

    prompt_evidence = _gold_standard_prompt_evidence(prompt_lower)
    for key, passed in prompt_evidence.items():
        if not passed:
            missing.append(key)

    required_trace_states = {
        "CREATE_SCENE_LANDING_PREVIEW": {"ok", "complete", "approved", "pass"},
        "DISCOVER_AND_ASSIGN_AGENTS": {
            "ok",
            "complete",
            "actual_multi_agent",
            "fallback_local_passes",
            "fallback_local_passes_with_limitation_recorded",
            "revised_pending_creator_approval",
        },
        "LOAD_REFERENCE_IMAGES_IN_CONTEXT": {"ok", "complete", "pass"},
        "PRE_GENERATION_EVAL": {
            "ok",
            "complete",
            "pass",
            "pass_with_recorded_limitations",
        },
    }
    trace_state_presence = {
        state: _trace_has_state(events, state, statuses)
        for state, statuses in required_trace_states.items()
    }
    for state, present in trace_state_presence.items():
        if not present:
            missing.append(f"logs/trace.jsonl.{state}")
    if trace_errors:
        missing.append("logs/trace.jsonl.valid")

    status = "pass" if not missing else "fail"
    return _check(
        "gold_standard_identity_route_gate",
        status,
        (
            "Gold-standard identity route is complete before imagegen/final progression."
            if status == "pass"
            else "Gold-standard identity route is incomplete; stop before imagegen/final progression."
        ),
        workflow_type=workflow.get("type"),
        path=f"runs/{run_dir.name}/references-used/selected_references.json",
        proof_artifact=proof_rel,
        aachu_face_identity_count=len(groups.get("aachu_face_identity") or []),
        zuv_face_identity_count=len(groups.get("zuv_face_identity") or []),
        style_reference_count=style_count,
        view_image_queue_count=queue_count,
        active_view_image_path_count=len(active_paths),
        prompt_files=[_rel(path, root) for path in prompt_paths],
        prompt_evidence=prompt_evidence,
        prompt_room_outputs=prompt_outputs,
        trace_state_presence=trace_state_presence,
        trace_errors=trace_errors,
        proof_validation_errors=proof_validation.get("validation_errors", []),
        missing_requirements=missing,
        failure_code=None if status == "pass" else "GOLD_STANDARD_IDENTITY_ROUTE_MISSING",
        final_imagegen_allowed=status == "pass",
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
        or "reject" in str(hard_gate)
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


def _check_final_package_has_illustration_proof(run_dir: Path) -> dict[str, Any]:
    packaged_artifacts = _packaged_illustration_artifacts(run_dir)
    final_qa_paths = sorted((run_dir / "evals").glob("final*qa*.json"))
    final_qa = [_read_json(path) for path in final_qa_paths]
    has_final_ready_claim = any(
        isinstance(doc, dict)
        and str(doc.get("decision") or doc.get("status") or "").lower()
        in {"ready_for_creator_review", "pass", "complete"}
        for doc in final_qa
    )
    if not packaged_artifacts and not has_final_ready_claim:
        return _check(
            "final_package_has_illustration_proof",
            "not_applicable",
            "No final package or final-ready QA claim exists yet.",
            packaged_artifacts=[],
            final_qa_artifacts=[f"runs/{run_dir.name}/{path.relative_to(run_dir)}" for path in final_qa_paths],
            failure_code=None,
            severity="info",
        )

    imagegen_attempted = _imagegen_was_attempted(run_dir)
    qa_candidates = []
    for path in sorted((run_dir / "evals").glob("image_quality*.json")):
        doc = _read_json(path)
        if not isinstance(doc, dict):
            continue
        qa_candidates.append(
            {
                "path": f"runs/{run_dir.name}/{path.relative_to(run_dir)}",
                "status": doc.get("status"),
                "hard_gate_result": doc.get("hard_gate_result"),
            }
        )
    has_passing_image_qa = any(
        str(item.get("hard_gate_result") or "").lower()
        in {"pass", "passed", "approved", "ready_for_creator_review"}
        or str(item.get("status") or "").lower()
        in {"pass", "passed", "ready_for_creator_review"}
        for item in qa_candidates
    )
    scene_artifacts_present = all(
        (run_dir / rel_path).exists()
        for rel_path in [
            "planning/scene_landing_preview.md",
            "planning/scene_options.json",
            "planning/slide_beat_map.json",
        ]
    )
    passed = imagegen_attempted and has_passing_image_qa and scene_artifacts_present
    return _check(
        "final_package_has_illustration_proof",
        "pass" if passed else "fail",
        "Final packages must be A Story illustrations, not deterministic quote-card renders; require imagegen attempt, passing Image QA, and scene-proof artifacts.",
        packaged_artifacts=packaged_artifacts,
        final_qa_artifacts=[f"runs/{run_dir.name}/{path.relative_to(run_dir)}" for path in final_qa_paths],
        imagegen_attempted=imagegen_attempted,
        image_quality_candidates=qa_candidates,
        scene_artifacts_present=scene_artifacts_present,
        failure_code=None if passed else "QUOTE_CARD_NOT_ILLUSTRATION",
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


def _check_generation_stops_after_hard_reject(run_dir: Path) -> dict[str, Any]:
    attempts_path = run_dir / "images/generation_attempts.json"
    attempts_doc = _read_json(attempts_path)
    attempts = attempts_doc.get("attempts") if isinstance(attempts_doc, dict) else []
    if not attempts_path.exists() or not isinstance(attempts, list):
        return _check(
            "generation_stops_after_hard_reject",
            "not_applicable",
            "No generation attempts artifact exists for sequencing review.",
            path=f"runs/{run_dir.name}/images/generation_attempts.json",
            failure_code=None,
            severity="info",
        )

    first_hard_reject = None
    continued_after_hard_reject: list[dict[str, Any]] = []
    for index, attempt in enumerate(attempts):
        if not isinstance(attempt, dict):
            continue
        if first_hard_reject is None and _attempt_has_hard_reject(attempt):
            first_hard_reject = {"index": index, **attempt}
            continue
        if first_hard_reject is not None:
            continued_after_hard_reject.append({"index": index, **attempt})

    failed = first_hard_reject is not None and bool(continued_after_hard_reject)
    acknowledged = failed and _historical_generation_violation_acknowledged(run_dir)
    return _check(
        "generation_stops_after_hard_reject",
        "fail" if failed and not acknowledged else "pass",
        (
            "Generation stopped after the first hard-rejected candidate."
            if not failed
            else "Historical generation continuation was acknowledged by a repair gate and returned to prompt reapproval."
            if acknowledged
            else "Generation continued after a hard-rejected candidate."
        ),
        path=f"runs/{run_dir.name}/images/generation_attempts.json",
        first_hard_reject=first_hard_reject,
        continued_after_hard_reject=continued_after_hard_reject,
        historical_violation_acknowledged=acknowledged,
        failure_code=None
        if not failed or acknowledged
        else "GENERATION_CONTINUED_AFTER_HARD_REJECT",
        severity="blocker",
    )


def _historical_generation_violation_acknowledged(run_dir: Path) -> bool:
    events, errors = _read_jsonl(run_dir / "logs/trace.jsonl")
    if errors:
        return False

    repair_index = None
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            continue
        failures = event.get("failure") or []
        if isinstance(failures, str):
            failures = [failures]
        failure_codes = {str(code) for code in failures}
        if (
            event.get("state") == "RETRY_OR_REVISE_IF_NEEDED"
            and str(event.get("status"))
            in {"repair_recorded", "blocked_until_reapproval"}
            and "GENERATION_CONTINUED_AFTER_HARD_REJECT" in failure_codes
        ):
            repair_index = index
            continue
        if repair_index is not None and index > repair_index:
            if event.get("state") == "HITL_PROMPT_LOCK" and str(
                event.get("status")
            ) in {"reapproval_required", "pending_reapproval"}:
                return True
    return False


def _check_prompt_repair_reapproval(run_dir: Path) -> dict[str, Any]:
    events, errors = _read_jsonl(run_dir / "logs/trace.jsonl")
    approvals = _read_text(run_dir / "docs/approvals.md")
    approvals_require_reapproval = (
        "## HITL Prompt Repair / Reapproval Required" in approvals
        and "Status: reapproval_required" in approvals
    )

    if errors:
        return _check(
            "prompt_repair_reapproval",
            "fail",
            "Cannot verify repaired prompt approval because trace JSONL is invalid.",
            reapproval_required=approvals_require_reapproval,
            reapproved_after_repair=False,
            parse_errors=errors,
            failure_code="HITL_NOT_APPROVED",
            severity="blocker",
        )

    reapproval_indices = [
        index
        for index, event in enumerate(events)
        if isinstance(event, dict)
        and event.get("state") == "HITL_PROMPT_LOCK"
        and (
            str(event.get("status")) in {"reapproval_required", "pending_reapproval"}
            or str(event.get("decision")) in {"pending_reapproval", "blocked_until_creator_reapproval"}
        )
    ]
    reapproval_required = approvals_require_reapproval or bool(reapproval_indices)
    if not reapproval_required:
        return _check(
            "prompt_repair_reapproval",
            "not_applicable",
            "No repaired prompt reapproval gate is active for this run.",
            reapproval_required=False,
            reapproved_after_repair=False,
            failure_code=None,
            severity="info",
        )

    last_reapproval_index = max(reapproval_indices) if reapproval_indices else -1
    reapproved_after_repair = any(
        isinstance(event, dict)
        and index > last_reapproval_index
        and event.get("state") == "HITL_PROMPT_LOCK"
        and (
            str(event.get("status")) == "approved"
            or str(event.get("decision")) == "approved"
        )
        for index, event in enumerate(events)
    )

    return _check(
        "prompt_repair_reapproval",
        "pass" if reapproved_after_repair else "fail",
        (
            "Repaired prompt/reference setup has fresh creator approval."
            if reapproved_after_repair
            else "Repaired prompt/reference setup requires fresh creator approval before imagegen."
        ),
        reapproval_required=True,
        reapproved_after_repair=reapproved_after_repair,
        failure_code=None if reapproved_after_repair else "HITL_NOT_APPROVED",
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


def _check_scene_landing_preview(run_dir: Path) -> dict[str, Any]:
    preview_path = run_dir / "planning/scene_landing_preview.md"
    approvals = _read_text(run_dir / "docs/approvals.md")
    events, trace_errors = _read_jsonl(run_dir / "logs/trace.jsonl")
    idea_lock_approved = _section_contains_any(
        approvals,
        ["Idea Lock", "HITL Idea Lock"],
        "Status: approved",
    ) or any(
        event.get("state") == "HITL_IDEA_LOCK"
        and event.get("status") in {"approved", "approved_with_revision"}
        for event in events
    )
    preview_trace_index = _first_event_index(
        events, "CREATE_SCENE_LANDING_PREVIEW", {"complete", "approved", "pass"}
    )
    idea_lock_index = _first_event_index(
        events, "HITL_IDEA_LOCK", {"approved", "approved_with_revision"}
    )
    preview_started = preview_path.exists() or preview_trace_index is not None

    if not idea_lock_approved and not preview_started:
        return _check(
            "scene_landing_preview",
            "not_applicable",
            "Scene landing preview is not required until idea lock is presented or approved.",
            path=f"runs/{run_dir.name}/planning/scene_landing_preview.md",
            severity="info",
        )

    missing: list[str] = []
    text = _read_text(preview_path)
    lower = text.lower()
    if not preview_path.exists():
        missing.append("planning/scene_landing_preview.md")
    if re.search(r"\{\{[^}]+\}\}", text):
        missing.append("template_placeholders")

    required_markers = {
        "exact_hook_text": ("exact first-slide text", "exact hook text"),
        "first_frame_visual": ("first-frame visual", "first frame visual"),
        "swipe_reason": ("why the first swipe happens", "swipe reason"),
        "mini_slide_arc": ("mini slide arc", "3-5 slide", "mini arc"),
        "payoff_frame": ("payoff frame",),
        "share_trigger": ("why someone sends it", "share trigger"),
        "flat_generic_risk": (
            "what could make it land flat/generic",
            "flat/generic risk",
        ),
        "correction": ("correction if it feels flat", "correction"),
    }
    for requirement, markers in required_markers.items():
        if not any(marker in lower for marker in markers):
            missing.append(requirement)

    nonempty_lines = [line for line in text.splitlines() if line.strip()]
    if preview_path.exists() and len(nonempty_lines) < 12:
        missing.append("preview_too_thin")
    if idea_lock_approved and "scene_landing_preview.md" not in approvals:
        missing.append("docs/approvals.md.scene_landing_preview_path")
    if (
        idea_lock_index is not None
        and preview_trace_index is not None
        and preview_trace_index > idea_lock_index
    ):
        missing.append("trace_order_scene_landing_after_idea_lock")
    if trace_errors and idea_lock_approved:
        missing.append("logs/trace.jsonl.valid")

    status = "pass" if not missing else "fail"
    return _check(
        "scene_landing_preview",
        status,
        (
            "Scene landing preview is concrete before idea lock."
            if status == "pass"
            else "Scene landing preview is missing or too abstract before idea lock."
        ),
        path=f"runs/{run_dir.name}/planning/scene_landing_preview.md",
        idea_lock_approved=idea_lock_approved,
        preview_trace_present=preview_trace_index is not None,
        missing_requirements=missing,
        failure_code=None if status == "pass" else "SCENE_LANDING_MISSING",
        severity="blocker",
    )


def _check_novelty_candidate_ledger(run_dir: Path) -> dict[str, Any]:
    ledger_path = run_dir / "planning/novelty_candidate_ledger.json"
    approvals = _read_text(run_dir / "docs/approvals.md")
    events, trace_errors = _read_jsonl(run_dir / "logs/trace.jsonl")
    idea_lock_approved = _section_contains_any(
        approvals,
        ["Idea Lock", "HITL Idea Lock"],
        "Status: approved",
    ) or any(
        event.get("state") == "HITL_IDEA_LOCK"
        and event.get("status") in {"approved", "approved_with_revision"}
        for event in events
    )
    score_trace_index = _first_event_index(
        events, "SCORE_IDEAS", {"complete", "approved", "pass"}
    )
    select_trace_index = _first_event_index(
        events, "SELECT_BEST_IDEA", {"complete", "approved", "pass"}
    )
    ledger_started = (
        ledger_path.exists()
        or score_trace_index is not None
        or select_trace_index is not None
        or (run_dir / "planning/selected_idea.json").exists()
    )

    if not idea_lock_approved and not ledger_started:
        return _check(
            "novelty_candidate_ledger",
            "not_applicable",
            "Novelty candidate ledger is not required until idea scoring, selection, or idea lock.",
            path=f"runs/{run_dir.name}/planning/novelty_candidate_ledger.json",
            severity="info",
        )

    missing: list[str] = []
    raw_text = _read_text(ledger_path)
    ledger = _read_json(ledger_path)
    if not ledger_path.exists():
        missing.append("planning/novelty_candidate_ledger.json")
    if re.search(r"\{\{[^}]+\}\}", raw_text):
        missing.append("template_placeholders")
    if not isinstance(ledger, dict):
        missing.append("novelty_candidate_ledger.valid_json")
        ledger = {}

    selected_candidate_id = ledger.get("selected_candidate_id")
    if not _usable_model_text(selected_candidate_id):
        missing.append("selected_candidate_id")

    candidates = ledger.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        missing.append("candidates")
        candidates = []

    selected_candidate = None
    for candidate in candidates:
        if (
            isinstance(candidate, dict)
            and candidate.get("candidate_id") == selected_candidate_id
        ):
            selected_candidate = candidate
            break
    if _usable_model_text(selected_candidate_id) and selected_candidate is None:
        missing.append("selected_candidate_id.matches_candidate")

    source_bank_search = ledger.get("source_bank_search")
    uses_winner_bank = False
    if isinstance(source_bank_search, dict):
        uses_winner_bank = source_bank_search.get("used_winner_bank") is True
        bank_paths = source_bank_search.get("bank_paths")
        evidence_gap = source_bank_search.get("evidence_gap")
        if uses_winner_bank and not (
            isinstance(bank_paths, list)
            and any(_usable_model_text(path) for path in bank_paths)
        ):
            missing.append("source_bank_search.bank_paths")
        if not uses_winner_bank and not _usable_model_text(evidence_gap):
            missing.append("source_bank_search.evidence_gap")
    else:
        missing.append("source_bank_search")

    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            missing.append(f"candidates[{index}].valid_object")
            continue
        decision = candidate.get("decision")
        serious_candidate = decision in {"selected", "shortlisted"} or (
            candidate.get("candidate_id") == selected_candidate_id
        )
        if not serious_candidate:
            continue
        if candidate.get("candidate_id") == selected_candidate_id and decision != "selected":
            missing.append(f"candidates[{index}].decision")
        _collect_required_text_fields(
            candidate,
            [
                ("candidate_id", ["candidate_id"]),
                ("title", ["title"]),
                ("source_engine.old_familiar_topic", ["source_engine", "old_familiar_topic"]),
                ("source_engine.first_frame_stop", ["source_engine", "first_frame_stop"]),
                ("source_engine.swipe_reason", ["source_engine", "swipe_reason"]),
                (
                    "source_engine.send_or_save_trigger",
                    ["source_engine", "send_or_save_trigger"],
                ),
                ("source_engine.what_must_stay", ["source_engine", "what_must_stay"]),
                ("novelty_model.new_reveal", ["novelty_model", "new_reveal"]),
                ("novelty_model.viewer_outcome", ["novelty_model", "viewer_outcome"]),
                ("novelty_model.contrast_frame", ["novelty_model", "contrast_frame"]),
                ("novelty_model.bullseye_proof", ["novelty_model", "bullseye_proof"]),
                (
                    "novelty_model.protect_the_illusion",
                    ["novelty_model", "protect_the_illusion"],
                ),
            ],
            missing,
            f"candidates[{index}]",
        )
        if uses_winner_bank:
            _collect_required_text_fields(
                candidate,
                [
                    ("source_winner.source_url", ["source_winner", "source_url"]),
                    ("source_winner.metric_signal", ["source_winner", "metric_signal"]),
                ],
                missing,
                f"candidates[{index}]",
            )

        urgency = _nested_value(candidate, ["novelty_model", "urgency"])
        if not isinstance(urgency, dict):
            missing.append(f"candidates[{index}].novelty_model.urgency")
        elif urgency.get("used") not in {True, False}:
            missing.append(f"candidates[{index}].novelty_model.urgency.used")
        elif not _usable_model_text(urgency.get("reason")):
            missing.append(f"candidates[{index}].novelty_model.urgency.reason")

        wrappers = candidate.get("a_story_wrappers")
        if not isinstance(wrappers, list) or not wrappers:
            missing.append(f"candidates[{index}].a_story_wrappers")
        elif not any(_complete_a_story_wrapper(wrapper) for wrapper in wrappers):
            missing.append(f"candidates[{index}].a_story_wrappers.complete_wrapper")

        scores = candidate.get("selection_scores")
        if not isinstance(scores, dict):
            missing.append(f"candidates[{index}].selection_scores")
        else:
            required_scores = [
                "winner_fit",
                "source_preservation",
                "novelty_strength",
                "aachu_zuv_specificity",
                "send_save_trigger",
                "anti_slop_risk",
                "visual_proof_potential",
                "total",
            ]
            for score_name in required_scores:
                if not isinstance(scores.get(score_name), (int, float)):
                    missing.append(f"candidates[{index}].selection_scores.{score_name}")
            if isinstance(scores.get("total"), (int, float)) and scores["total"] <= 0:
                missing.append(f"candidates[{index}].selection_scores.total")

    if trace_errors and (idea_lock_approved or ledger_started):
        missing.append("logs/trace.jsonl.valid")

    status = "pass" if not missing else "fail"
    return _check(
        "novelty_candidate_ledger",
        status,
        (
            "Novelty candidate ledger proves selection before idea lock."
            if status == "pass"
            else "Novelty candidate ledger is missing or too incomplete before idea lock."
        ),
        path=f"runs/{run_dir.name}/planning/novelty_candidate_ledger.json",
        idea_lock_approved=idea_lock_approved,
        ledger_trace_present=score_trace_index is not None,
        selected_candidate_id=selected_candidate_id,
        missing_requirements=missing,
        failure_code=None if status == "pass" else "NOVELTY_CANDIDATE_LEDGER_MISSING",
        severity="blocker",
    )


def _check_source_winner_novelty_model(run_dir: Path) -> dict[str, Any]:
    contract_path = run_dir / "planning/source_winner_remix_contract.json"
    model_path = run_dir / "planning/source_winner_novelty_model.json"
    contract = _read_json(contract_path)
    requires_model = _source_winner_contract_requires_novelty_model(contract)

    if not requires_model:
        return _check(
            "source_winner_novelty_model",
            "not_applicable",
            "Source-winner novelty modeling is not required without a source-winner remix contract.",
            path=f"runs/{run_dir.name}/planning/source_winner_novelty_model.json",
            contract_path=f"runs/{run_dir.name}/planning/source_winner_remix_contract.json",
            severity="info",
        )

    missing: list[str] = []
    raw_text = _read_text(model_path)
    model = _read_json(model_path)
    if not model_path.exists():
        missing.append("planning/source_winner_novelty_model.json")
    if re.search(r"\{\{[^}]+\}\}", raw_text):
        missing.append("template_placeholders")
    if not isinstance(model, dict):
        missing.append("source_winner_novelty_model.valid_json")
        model = {}

    framework_path = "references/text-style/illusion-of-novelty-storytelling-2026-06-18.md"
    if model.get("framework_reference") != framework_path:
        missing.append("framework_reference")

    required_text_fields = {
        "source_winner.source_url": _nested_value(model, ["source_winner", "source_url"]),
        "source_winner.old_familiar_topic": _nested_value(
            model, ["source_winner", "old_familiar_topic"]
        ),
        "illusion_of_novelty_model.new_reveal": _nested_value(
            model, ["illusion_of_novelty_model", "new_reveal"]
        ),
        "illusion_of_novelty_model.viewer_outcome": _nested_value(
            model, ["illusion_of_novelty_model", "viewer_outcome"]
        ),
        "illusion_of_novelty_model.contrast_frame": _nested_value(
            model, ["illusion_of_novelty_model", "contrast_frame"]
        ),
        "illusion_of_novelty_model.bullseye_proof": _nested_value(
            model, ["illusion_of_novelty_model", "bullseye_proof"]
        ),
        "illusion_of_novelty_model.protect_the_illusion": _nested_value(
            model, ["illusion_of_novelty_model", "protect_the_illusion"]
        ),
        "a_story_translation.what_stays_from_source": _nested_value(
            model, ["a_story_translation", "what_stays_from_source"]
        ),
        "a_story_translation.what_changes_for_aachu_zuv": _nested_value(
            model, ["a_story_translation", "what_changes_for_aachu_zuv"]
        ),
        "a_story_translation.lived_scene_wrapper": _nested_value(
            model, ["a_story_translation", "lived_scene_wrapper"]
        ),
    }
    for field, value in required_text_fields.items():
        if not _usable_model_text(value):
            missing.append(field)

    urgency = _nested_value(model, ["illusion_of_novelty_model", "urgency"])
    if not isinstance(urgency, dict):
        missing.append("illusion_of_novelty_model.urgency")
    elif urgency.get("used") not in {True, False}:
        missing.append("illusion_of_novelty_model.urgency.used")
    elif not _usable_model_text(urgency.get("reason")):
        missing.append("illusion_of_novelty_model.urgency.reason")

    removed_lines = _nested_value(
        model,
        ["a_story_translation", "lines_to_remove_because_they_explain_the_lesson"],
    )
    if not isinstance(removed_lines, list) or not any(
        _usable_model_text(item) for item in removed_lines
    ):
        missing.append(
            "a_story_translation.lines_to_remove_because_they_explain_the_lesson"
        )

    status = "pass" if not missing else "fail"
    return _check(
        "source_winner_novelty_model",
        status,
        (
            "Source winner has been modeled through the Illusion of Novelty framework."
            if status == "pass"
            else "Source winner needs an Illusion of Novelty modeling pass before idea lock."
        ),
        path=f"runs/{run_dir.name}/planning/source_winner_novelty_model.json",
        contract_path=f"runs/{run_dir.name}/planning/source_winner_remix_contract.json",
        missing_requirements=missing,
        failure_code=None if status == "pass" else "SOURCE_WINNER_NOVELTY_MODEL_MISSING",
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
    pre_imagegen_ready = (
        indices["idea"] is not None
        and indices["story"] is not None
        and indices["prompt"] is not None
        and indices["imagegen"] is None
        and indices["idea"] < indices["story"] < indices["prompt"]
    )
    post_imagegen_ordered = (
        indices["idea"] is not None
        and indices["story"] is not None
        and indices["prompt"] is not None
        and indices["imagegen"] is not None
        and indices["idea"] < indices["story"] < indices["prompt"] < indices["imagegen"]
    )
    ordered = pre_imagegen_ready or post_imagegen_ordered
    return _check(
        "hitl_order_before_imagegen",
        "pass" if ordered else "fail",
        "Idea, story, and prompt locks are recorded before image generation.",
        event_indices=indices,
        order_state=(
            "pre_imagegen_ready"
            if pre_imagegen_ready
            else "post_imagegen_ordered"
            if post_imagegen_ordered
            else "invalid"
        ),
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


def _read_reference_policy(run_dir: Path) -> dict[str, list[str]]:
    policy_path = run_dir / "references-used/reference_policy.json"
    policy = _read_json(policy_path)
    if not isinstance(policy, dict):
        return {
            "blocked_active_refs": [],
            "analysis_only_refs": [],
            "emotion_forbidden_refs": [],
        }
    result: dict[str, list[str]] = {}
    for field in (
        "blocked_active_refs",
        "analysis_only_refs",
        "emotion_forbidden_refs",
    ):
        value = policy.get(field) or []
        if isinstance(value, str):
            value = [value]
        result[field] = [str(item) for item in value if str(item).strip()]
    return result


def _prompt_forbids_smile(prompt_text: str) -> bool:
    lower = prompt_text.lower()
    return any(marker in lower for marker in NEGATED_EXPRESSION_MARKERS)


def _prompt_scene_terms(prompt_text: str) -> list[str]:
    lower = prompt_text.lower()
    return [
        term
        for term, markers in REFERENCE_SCENE_COLLISION_TERMS.items()
        if any(marker in lower for marker in markers)
    ]


def _active_ref_has_scene_collision(path: str, scene_term: str) -> bool:
    if not str(path).startswith("references/identity/"):
        return False
    stem = Path(path).stem.lower()
    if "crop" in stem:
        return False
    return scene_term in stem


def _path_expression_bucket(path: str) -> str:
    stem = Path(path).stem.lower()
    if "laugh" in stem:
        return "laugh"
    if "smile" in stem or "smiling" in stem:
        return "smile"
    if "pout" in stem:
        return "pout"
    if "glance" in stem:
        return "glance"
    return "unknown"


def _has_major_creator_visual_correction(run_dir: Path) -> bool:
    notes = _read_text(run_dir / "planning/creator_direction_notes.md").lower()
    if any(
        marker in notes
        for marker in (
            "major creator correction",
            "creator correction",
            "no smile",
            "copied cafe",
            "reference",
        )
    ):
        return True

    process_failure = _read_json(run_dir / "evals/process_failure_audit.json")
    if isinstance(process_failure, dict) and process_failure.get("status") in {
        "process_failed",
        "blocked",
    }:
        return True

    events, errors = _read_jsonl(run_dir / "logs/trace.jsonl")
    if errors:
        return False
    return any(
        event.get("state") == "SESSION_LEARNING_CAPTURE"
        or str(event.get("correction_type", "")).lower() == "major_visual_correction"
        for event in events
        if isinstance(event, dict)
    )


def _approval_section(text: str, headings: list[str]) -> str:
    for heading in headings:
        marker = f"## {heading}"
        if marker not in text:
            continue
        body = text.split(marker, 1)[1]
        next_marker = body.find("\n## ")
        if next_marker >= 0:
            body = body[:next_marker]
        return body
    return ""


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


def _record_marks_face_identity(ref: dict[str, Any]) -> bool:
    return (
        ref.get("dossier_role") == "face_anchor"
        or ref.get("quality") == "identity"
        or "face_identity" in str(ref.get("role", ""))
    )


def _is_raw_face_anchor_path(path: str, subject: str) -> bool:
    text = str(path)
    if "/reference-binder/" in text:
        return False
    subject_prefix = f"references/identity/{subject}/"
    if not text.startswith(subject_prefix):
        return False
    stem = Path(text).stem.lower()
    return "/face/" in text or "face" in stem or "portrait" in stem


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
            if not _record_marks_face_identity(ref):
                errors.append(f"{group_name}[{index}].face_identity_role")
            if not _is_raw_face_anchor_path(path, subject):
                errors.append(f"{group_name}[{index}].path_not_raw_face_anchor")
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
    loaded_paths = proof.get("loaded_reference_paths") or proof.get("loaded_paths")
    if isinstance(loaded_paths, list):
        path_text = {str(path) for path in loaded_paths}
        has_aachu_face = any(_is_raw_face_anchor_path(path, "aachu") for path in path_text)
        has_zuv_face = any(_is_raw_face_anchor_path(path, "zuv") for path in path_text)
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


def _gold_standard_style_reference_count(groups: dict[str, Any]) -> int:
    aliases = [
        "style",
        "style_reference",
        "style_references",
        "best_illustration_style",
        "best_illustration_references",
    ]
    return max(
        (len(groups.get(alias) or []) for alias in aliases),
        default=0,
    )


def _pregen_prompt_outputs(pregen: Any) -> list[str]:
    if not isinstance(pregen, dict):
        return []
    value = pregen.get("prompt_room_outputs") or pregen.get("agent_outputs") or []
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if isinstance(item, str)]


def _resolve_run_artifact_path(root: Path, run_dir: Path, artifact: str) -> Path:
    path = Path(artifact)
    if path.is_absolute():
        return path
    if artifact.startswith("runs/"):
        return root / artifact
    return run_dir / artifact


def _gold_standard_prompt_evidence(prompt_lower: str) -> dict[str, bool]:
    has_highest_priority = (
        "highest-priority visual input" in prompt_lower
        or "highest priority visual input" in prompt_lower
    )
    has_raw_named_face_anchors = (
        "raw" in prompt_lower
        and "aachu" in prompt_lower
        and "zuv" in prompt_lower
        and ("face-anchor" in prompt_lower or "face anchor" in prompt_lower)
    )
    blocks_binder_replacement = (
        "style images" in prompt_lower
        and "binders" in prompt_lower
        and "text descriptions" in prompt_lower
        and "replace raw face anchors" in prompt_lower
    )
    face_readability = (
        ("faces readable" in prompt_lower or "readable faces" in prompt_lower)
        and ("medium-wide" in prompt_lower or "medium wide" in prompt_lower)
        and (
            "front three-quarter" in prompt_lower
            or "front three quarter" in prompt_lower
        )
    )
    blocks_single_anchor_pose_copy = (
        ("single anchor" in prompt_lower or "single reference" in prompt_lower)
        and ("do not copy" in prompt_lower or "not copy" in prompt_lower)
        and "pose" in prompt_lower
        and "head angle" in prompt_lower
        and ("eye state" in prompt_lower or "eye structure" in prompt_lower)
        and "expression" in prompt_lower
        and "wardrobe" in prompt_lower
        and "lighting" in prompt_lower
        and (
            "camera position" in prompt_lower
            or "camera angle" in prompt_lower
            or "composition" in prompt_lower
        )
    )
    return {
        "prompt_raw_identity_priority": (
            has_highest_priority and has_raw_named_face_anchors
        ),
        "prompt_blocks_binder_text_replacement": blocks_binder_replacement,
        "prompt_blocks_single_anchor_pose_copy": blocks_single_anchor_pose_copy,
        "prompt_face_readable_composition": face_readability,
    }


def _trace_has_state(
    events: list[dict[str, Any]], state: str, allowed_statuses: set[str]
) -> bool:
    return any(
        event.get("state") == state
        and str(event.get("status", "")).lower() in allowed_statuses
        for event in events
    )


def _validate_reference_visibility_proof(
    manifest: dict[str, Any], proof: dict[str, Any]
) -> dict[str, Any]:
    expected_paths = _manifest_view_image_paths(manifest)
    loaded_paths = proof.get("loaded_paths") or proof.get("loaded_reference_paths") or []
    if not isinstance(loaded_paths, list):
        loaded_paths = []
    loaded_paths = [str(path) for path in loaded_paths]

    expected_set = set(expected_paths)
    loaded_set = set(loaded_paths)
    missing_paths = [path for path in expected_paths if path not in loaded_set]
    unexpected_paths = [path for path in loaded_paths if path not in expected_set]
    validation_errors: list[str] = []

    manifest_hash = manifest.get("load_plan_sha256")
    proof_hash = proof.get("load_plan_sha256")
    if manifest_hash and proof_hash != manifest_hash:
        return {
            "valid": False,
            "summary": "Reference visibility proof is stale for the current load plan.",
            "failure_code": "REFERENCE_VISIBILITY_PROOF_STALE",
            "missing_loaded_paths": missing_paths,
            "unexpected_loaded_paths": unexpected_paths,
            "validation_errors": ["load_plan_sha256_mismatch"],
        }

    if proof.get("loaded_in_current_conversation") is not True:
        validation_errors.append("not_loaded_in_current_conversation")
    if "view_image" not in str(proof.get("loading_method", "")):
        validation_errors.append("loading_method_not_view_image")
    if not _proof_has_image_roles(proof):
        validation_errors.append("identity_roles_missing")
    if proof.get("loaded_count") is not None and proof.get("loaded_count") != len(
        loaded_paths
    ):
        validation_errors.append("loaded_count_mismatch")
    if proof.get("expected_count") is not None and proof.get("expected_count") != len(
        expected_paths
    ):
        validation_errors.append("expected_count_mismatch")

    if missing_paths:
        return {
            "valid": False,
            "summary": "Reference visibility proof is missing required active view_image paths.",
            "failure_code": "REFERENCE_VISIBILITY_PROOF_INCOMPLETE",
            "missing_loaded_paths": missing_paths,
            "unexpected_loaded_paths": unexpected_paths,
            "validation_errors": validation_errors,
        }
    if unexpected_paths:
        return {
            "valid": False,
            "summary": "Reference visibility proof loaded paths outside the active load plan.",
            "failure_code": "REFERENCE_VISIBILITY_PROOF_PATH_MISMATCH",
            "missing_loaded_paths": missing_paths,
            "unexpected_loaded_paths": unexpected_paths,
            "validation_errors": validation_errors,
        }
    identity_errors = _raw_identity_input_errors(expected_paths)
    diversity_errors = _identity_reference_diversity_errors(
        manifest.get("reference_groups") or {}
    )
    loaded_identity_errors = [
        error.replace("active_queue", "loaded_paths", 1)
        for error in _raw_identity_input_errors(loaded_paths)
    ]
    if proof.get("active_generation_path_can_use_loaded_image_context") is False:
        identity_errors.append("active_generation_path_cannot_use_loaded_image_context")
    if identity_errors or loaded_identity_errors or diversity_errors:
        failure_code = (
            "IDENTITY_REFERENCE_DIVERSITY_MISSING"
            if diversity_errors and not identity_errors and not loaded_identity_errors
            else "IDENTITY_REFERENCE_INPUT_UNPROVEN"
        )
        return {
            "valid": False,
            "summary": "Reference visibility proof does not prove diverse raw face-anchor image inputs.",
            "failure_code": failure_code,
            "missing_loaded_paths": missing_paths,
            "unexpected_loaded_paths": unexpected_paths,
            "validation_errors": validation_errors
            + identity_errors
            + loaded_identity_errors
            + diversity_errors,
        }
    if validation_errors:
        return {
            "valid": False,
            "summary": "Reference visibility proof exists but does not prove active image context.",
            "failure_code": "REFERENCE_VISIBILITY_PROOF_INVALID",
            "missing_loaded_paths": missing_paths,
            "unexpected_loaded_paths": unexpected_paths,
            "validation_errors": validation_errors,
        }
    return {
        "valid": True,
        "summary": "Reference visibility proof matches the active load plan and records raw face-anchor image roles.",
        "failure_code": None,
        "missing_loaded_paths": [],
        "unexpected_loaded_paths": [],
        "validation_errors": [],
    }


def _raw_identity_input_errors(paths: list[str]) -> list[str]:
    errors: list[str] = []
    if any("/reference-binder/" in path for path in paths):
        errors.append("active_queue_contains_reference_binder_paths")
    if _raw_face_anchor_count(paths, "aachu") < MIN_RAW_FACE_ANCHORS_PER_SUBJECT:
        errors.append("active_queue_missing_raw_aachu_face_anchors")
    if _raw_face_anchor_count(paths, "zuv") < MIN_RAW_FACE_ANCHORS_PER_SUBJECT:
        errors.append("active_queue_missing_raw_zuv_face_anchors")
    return errors


def _raw_face_anchor_count(paths: list[str], subject: str) -> int:
    return sum(1 for path in paths if _is_raw_face_anchor_path(str(path), subject))


def _identity_reference_diversity_errors(groups: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for group_name in ("aachu_face_identity", "zuv_face_identity"):
        buckets = _identity_group_view_buckets(groups.get(group_name) or [])
        informative = [bucket for bucket in buckets if bucket != "unknown"]
        if len(informative or buckets) < MIN_FACE_VIEW_BUCKETS_PER_SUBJECT:
            errors.append(f"{group_name}_view_bucket_lt_2")
    return errors


def _identity_reference_view_summary(groups: dict[str, Any]) -> dict[str, Any]:
    return {
        group_name: _identity_group_view_buckets(groups.get(group_name) or [])
        for group_name in ("aachu_face_identity", "zuv_face_identity")
    }


def _identity_group_view_buckets(refs: list[Any]) -> list[str]:
    buckets = {
        _identity_reference_view_bucket(ref)
        for ref in refs
        if isinstance(ref, dict)
    }
    return sorted(buckets)


def _identity_reference_view_bucket(ref: dict[str, Any]) -> str:
    value = str(ref.get("view_bucket") or "").strip().lower()
    if value:
        return value
    path = str(ref.get("path") or "")
    stem = Path(path).stem.lower()
    if "side" in stem or "profile" in stem:
        return "side"
    if (
        "three-quarter" in stem
        or "three_quarter" in stem
        or "threequarter" in stem
        or "3q" in stem
        or "car-purple" in stem
        or "glance" in stem
        or "laugh" in stem
        or "lavender-smile" in stem
    ):
        return "three_quarter"
    if (
        "front" in stem
        or "frontal" in stem
        or "neutral" in stem
        or "selfie" in stem
        or "cafe-neutral" in stem
        or "home-black" in stem
    ):
        return "front"
    return "unknown"


def _attempt_has_hard_reject(attempt: dict[str, Any]) -> bool:
    status = str(attempt.get("status", "")).lower()
    failure_codes = {
        str(code)
        for code in attempt.get("failure_codes", [])
        if isinstance(code, str)
    }
    has_hard_failure = bool(failure_codes & HARD_IMAGE_FAILURE_CODES)
    return has_hard_failure and (
        "reject" in status
        or "fail" in status
        or "block" in status
    )


def _manifest_view_image_paths(manifest: dict[str, Any]) -> list[str]:
    queue = manifest.get("active_view_image_queue") or manifest.get("view_image_queue") or []
    paths: list[str] = []
    for item in queue:
        if isinstance(item, dict) and item.get("path"):
            paths.append(str(item["path"]))
        elif isinstance(item, str):
            paths.append(item)
    return paths


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
        "IDENTITY_REFERENCE_INPUT_UNPROVEN",
        "PROMPT_PALETTE_CONFLICT",
        "GENERATION_CONTINUED_AFTER_HARD_REJECT",
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


def _packaged_illustration_artifacts(run_dir: Path) -> list[str]:
    candidates: list[Path] = []
    for dirname in ["final", "package", "final-carousel", "corrected-exact-source-carousel", "exports"]:
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


def _source_winner_contract_requires_novelty_model(contract: Any) -> bool:
    if not isinstance(contract, dict):
        return False
    mode = str(contract.get("remix_mode") or contract.get("status") or "").lower()
    if mode in {"fresh_original", "not_applicable", "none"}:
        return False
    if "permissioned_source_preserving_remix" in mode or "premise_only" in mode:
        return True
    source_winner = contract.get("source_winner")
    if isinstance(source_winner, dict):
        return any(
            _usable_model_text(source_winner.get(key))
            for key in ("source_url", "source_shortcode", "source_account")
        )
    return False


def _nested_value(value: Any, keys: list[str]) -> Any:
    cursor = value
    for key in keys:
        if not isinstance(cursor, dict):
            return None
        cursor = cursor.get(key)
    return cursor


def _collect_required_text_fields(
    value: dict[str, Any],
    fields: list[tuple[str, list[str]]],
    missing: list[str],
    prefix: str,
) -> None:
    for field_name, path in fields:
        if not _usable_model_text(_nested_value(value, path)):
            missing.append(f"{prefix}.{field_name}")


def _complete_a_story_wrapper(wrapper: Any) -> bool:
    if not isinstance(wrapper, dict):
        return False
    required_fields = [
        "wrapper_id",
        "wrapper_type",
        "what_changes_for_aachu_zuv",
        "lived_scene_wrapper",
        "visual_proof",
        "send_or_comment_trigger",
        "flat_or_generic_risk",
    ]
    return all(_usable_model_text(wrapper.get(field)) for field in required_fields)


def _usable_model_text(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    text = value.strip()
    return bool(text) and "{{" not in text and "}}" not in text


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
        "reference_active_identity_inputs": "IDENTITY_REFERENCE_INPUT_UNPROVEN",
        "prompt_palette_conflict": "PROMPT_PALETTE_CONFLICT",
        "prompt_canvas_size": "PROMPT_CANVAS_SIZE_MISSING",
        "prompt_brandmark_gate": "PROMPT_BRANDMARK_MISSING",
        "prompt_overload": "PROMPT_OVERLOAD",
        "pre_imagegen_blocker_check": "PRE_IMAGEGEN_BLOCKER_CHECK_FAILED",
        "gold_standard_identity_route_gate": "GOLD_STANDARD_IDENTITY_ROUTE_MISSING",
        "final_package_has_illustration_proof": "QUOTE_CARD_NOT_ILLUSTRATION",
        "generation_stops_after_hard_reject": "GENERATION_CONTINUED_AFTER_HARD_REJECT",
        "prompt_repair_reapproval": "HITL_NOT_APPROVED",
        "skill_contract_present": "SKILL_CONTRACT_MISSING",
        "master_prompt_present": "MASTER_PROMPT_MISSING",
        "required_templates_present": "REQUIRED_TEMPLATE_MISSING",
        "final_package_not_started": "FINAL_PACKAGE_STARTED_WHILE_BLOCKED",
        "accepted_candidate_filename_guard": "ACCEPTED_CANDIDATE_FILENAME_UNSAFE",
        "trace_jsonl_valid": "TRACE_JSONL_INVALID",
        "novelty_candidate_ledger": "NOVELTY_CANDIDATE_LEDGER_MISSING",
        "scene_landing_preview": "SCENE_LANDING_MISSING",
        "source_winner_novelty_model": "SOURCE_WINNER_NOVELTY_MODEL_MISSING",
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
