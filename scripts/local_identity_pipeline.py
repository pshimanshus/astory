#!/usr/bin/env python3
"""Dry-run proof builder for local A Story identity generation."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


IDENTITY_DOSSIER_PATH = Path("references/identity/_dossier/identity-dossier.json")
MIN_FACE_ANCHORS_PER_SUBJECT = 4
PROOF_FILENAME = "local_identity_reference_proof.json"
REPORT_FILENAME = "local_identity_reference_proof_report.md"
DISCOVERY_FILENAME = "local_identity_stack_discovery.json"
DISCOVERY_REPORT_FILENAME = "local_identity_stack_discovery_report.md"
READINESS_FILENAME = "local_identity_execution_readiness.json"
READINESS_REPORT_FILENAME = "local_identity_execution_readiness_report.md"
COMPUTE_DIAGNOSTIC_FILENAME = "local_compute_diagnostic.json"
COMPUTE_DIAGNOSTIC_REPORT_FILENAME = "local_compute_diagnostic_report.md"
HANDOFF_MANIFEST_FILENAME = "local_identity_handoff_manifest.json"
HANDOFF_REPORT_FILENAME = "local_identity_handoff_report.md"
SUPPORT_REFERENCE_ROLES_REQUIRING_FACE_IDENTITY_BLOCK = {
    "formal_secondary",
    "place",
    "reaction",
    "smile",
    "together_body_language",
    "together_scene",
    "wardrobe",
}


class PromptOnlyReferenceError(ValueError):
    """Raised when a workflow tries to deliver identity refs as prompt text."""


class ReferenceSelectionError(ValueError):
    """Raised when the selected reference manifest is missing required inputs."""


LOCAL_WORKFLOW_OPTIONS: dict[str, dict[str, Any]] = {
    "option_a_flux_kontext_dev": {
        "label": "Option A: FLUX.1 Kontext [dev] via ComfyUI",
        "engine": "ComfyUI local server",
        "primary_models": ["FLUX.1 Kontext [dev]"],
        "identity_method": "reference-image editing / in-context image conditioning",
        "why_consider": (
            "Strong general image-reference editing path; useful if the goal is to keep "
            "composition and style close to supplied references."
        ),
        "risk": (
            "Not a dedicated face-ID adapter; may still drift on two recurring people, "
            "and weights/workflow are large."
        ),
    },
    "option_b_sdxl_instantid_pulid_ipadapter": {
        "label": "Option B: SDXL + InstantID/PuLID/IP-Adapter via ComfyUI",
        "engine": "ComfyUI local server",
        "primary_models": ["SDXL", "InstantID", "PuLID", "IP-Adapter"],
        "identity_method": "explicit face-ID conditioning from local image inputs",
        "why_consider": (
            "Most targeted zero-shot identity path for Aachu/Zuv because face crops can "
            "drive identity separately from style references."
        ),
        "risk": (
            "Two-person identity often needs region control, masked generation, or "
            "separate passes; quality depends on local nodes and model weights."
        ),
    },
    "option_c_train_identity_loras": {
        "label": "Option C: train separate Aachu/Zuv identity LoRAs",
        "engine": "Local trainer plus ComfyUI inference",
        "primary_models": ["SDXL or FLUX base", "Aachu LoRA", "Zuv LoRA"],
        "identity_method": "trained recurring-character adapters",
        "why_consider": (
            "Fallback if zero-shot identity adapters fail creator face-match review."
        ),
        "risk": (
            "Requires curated datasets, training time, storage, and extra QA to avoid "
            "overfit or style collapse."
        ),
    },
}

MODEL_KEYWORDS: dict[str, tuple[str, ...]] = {
    "sdxl": ("sdxl", "xl_base"),
    "instantid": ("instantid", "instant-id", "instant_id"),
    "pulid": ("pulid", "pu-lid"),
    "ip_adapter": ("ip-adapter", "ipadapter", "ip_adapter"),
}

MINIMUM_MODEL_ARTIFACTS: dict[str, dict[str, Any]] = {
    "sdxl_base_checkpoint": {
        "target_paths": ("checkpoints/sd_xl_base_1.0.safetensors",),
        "search_subdirs": ("checkpoints",),
        "keywords": ("sdxl", "sd_xl", "xl_base", "xl-base"),
    },
    "instantid_ip_adapter": {
        "target_paths": ("instantid/ip-adapter.bin",),
        "search_subdirs": ("instantid",),
        "keywords": ("ip-adapter", "instantid", "instant-id", "instant_id"),
    },
    "instantid_controlnet": {
        "target_paths": ("controlnet/instantid-controlnet.safetensors",),
        "search_subdirs": ("controlnet",),
        "keywords": ("instantid-controlnet", "instantid", "instant-id", "instant_id"),
    },
    "insightface_antelopev2": {
        "required_files": (
            "insightface/models/antelopev2/genderage.onnx",
            "insightface/models/antelopev2/2d106det.onnx",
            "insightface/models/antelopev2/1k3d68.onnx",
            "insightface/models/antelopev2/glintr100.onnx",
            "insightface/models/antelopev2/scrfd_10g_bnkps.onnx",
        ),
    },
}

ADDON_MODEL_ARTIFACTS: dict[str, dict[str, Any]] = {
    "pulid_sdxl_model": {
        "target_paths": ("pulid/ip-adapter_pulid_sdxl_fp16.safetensors",),
        "search_subdirs": ("pulid",),
        "keywords": ("pulid", "pu-lid"),
    },
    "clip_vision_vit_h": {
        "target_paths": ("clip_vision/CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors",),
        "search_subdirs": ("clip_vision",),
        "keywords": ("clip-vit-h", "vit-h", "clip_vision"),
    },
    "ipadapter_plus_face_sdxl": {
        "target_paths": ("ipadapter/ip-adapter-plus-face_sdxl_vit-h.safetensors",),
        "search_subdirs": ("ipadapter", "ipadapter_models"),
        "keywords": ("ip-adapter-plus-face", "ipadapter-plus-face", "face_sdxl"),
    },
}

REQUIRED_COMFYUI_MODULES = ("torch", "aiohttp", "safetensors", "transformers")


def build_local_identity_reference_proof(
    repo_root: Path | str,
    run_id: str,
    workflow_id: str,
    workflow_file: Path | str | None = None,
    reference_delivery_mode: str = "local_binary_input",
) -> dict[str, Any]:
    """Build a dry-run proof that identity refs are explicit local image inputs."""

    if reference_delivery_mode != "local_binary_input":
        raise PromptOnlyReferenceError(
            "Prompt-only reference delivery is not allowed for Aachu/Zuv identity work."
        )

    repo_root = Path(repo_root).resolve()
    run_root = repo_root / "runs" / run_id
    selected_manifest = run_root / "references-used" / "selected_references.json"
    selected_references = _read_json(selected_manifest)
    reference_inputs = _build_reference_inputs(repo_root, selected_references)
    _validate_required_identity_inputs(reference_inputs)
    role_based_reference_library = _build_role_based_reference_library(repo_root)

    workflow = _select_workflow(workflow_id)
    workflow_status = _workflow_readiness(repo_root, workflow_id, workflow_file)
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    top_status = (
        "dry_run_pass_pending_creator_execution_approval"
        if workflow_status["status"] == "ready"
        else "blocked"
    )

    return {
        "schema_version": "1.0",
        "run_id": run_id,
        "created_at": now,
        "mode": "local_open_weight_identity_dry_run",
        "status": top_status,
        "zero_openai_api": True,
        "paid_cloud_api": False,
        "purpose": (
            "Prove selected Aachu/Zuv references are bound as explicit local image "
            "inputs before any non-final identity proof image is generated."
        ),
        "selected_manifest": _relative_path(selected_manifest, repo_root),
        "recommended_workflow_id": workflow_id,
        "recommended_model_stack": workflow,
        "candidate_model_stacks": [
            {"workflow_id": key, **value}
            for key, value in LOCAL_WORKFLOW_OPTIONS.items()
        ],
        "reference_delivery": {
            "status": "pass",
            "delivery_mode": "local_binary_input",
            "prompt_only_allowed": False,
            "proof_standard": (
                "Every selected identity/style reference must be represented as an "
                "image_file_bytes input with role, path, byte size, and SHA-256 hash."
            ),
        },
        "reference_inputs": reference_inputs,
        "role_based_reference_library": role_based_reference_library,
        "workflow_readiness": workflow_status,
        "identity_proof_request": {
            "status": "not_generated",
            "artifact_policy": "non_final_identity_proof_only",
            "surface": "identity_proof_side_by_side",
            "story_text": False,
            "brandmark": False,
            "shawl": False,
            "composition": (
                "Aachu and Zuv side-by-side, face-forward enough for creator identity "
                "review, neutral pose, no story text, no brandmark, no shawl."
            ),
            "blocker": (
                "Do not generate carousel slides until this identity proof is generated "
                "locally and accepted by the creator."
            ),
        },
        "final_decision": _final_decision(workflow_status),
    }


def write_proof_artifacts(repo_root: Path | str, proof: dict[str, Any]) -> tuple[Path, Path]:
    """Write the proof JSON and human report under the run evals folder."""

    repo_root = Path(repo_root).resolve()
    evals_dir = repo_root / "runs" / proof["run_id"] / "evals"
    evals_dir.mkdir(parents=True, exist_ok=True)
    proof_path = evals_dir / PROOF_FILENAME
    report_path = evals_dir / REPORT_FILENAME
    proof_path.write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(render_report(proof), encoding="utf-8")
    return proof_path, report_path


def discover_local_identity_stack(
    repo_root: Path | str,
    run_id: str,
    workflow_id: str,
    workflow_file: Path | str | None = None,
    search_roots: list[Path | str] | None = None,
    model_roots: list[Path | str] | None = None,
    comfyui_executable: str | None = "auto",
    server_stats: dict[str, Any] | None | str = "auto",
    python_modules: list[str] | None | str = "auto",
) -> dict[str, Any]:
    """Inspect the local machine for a no-download identity workflow."""

    repo_root = Path(repo_root).resolve()
    run_root = repo_root / "runs" / run_id
    workflow = _select_workflow(workflow_id)
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    executable = (
        shutil.which("comfyui") if comfyui_executable == "auto" else comfyui_executable
    )
    roots = (
        _default_comfyui_search_roots(repo_root, run_root)
        if search_roots is None
        else search_roots
    )
    existing_root_paths = _dedupe_paths(
        [Path(root).resolve() for root in roots if Path(root).exists()]
    )
    existing_roots = [_relative_path(root, repo_root) for root in existing_root_paths]
    stats = _fetch_comfyui_system_stats() if server_stats == "auto" else server_stats
    server_available = isinstance(stats, dict)
    comfyui_available = bool(executable or existing_roots or server_available)
    if python_modules == "auto":
        detected_modules, dependency_probe = _probe_comfyui_python_modules(
            existing_root_paths
        )
        dependency_status = _python_dependency_status(
            detected_modules if detected_modules is not None else "auto"
        )
        dependency_status["probe"] = dependency_probe
    else:
        dependency_status = _python_dependency_status(python_modules)
        dependency_status["probe"] = {
            "method": "provided_modules",
            "python": None,
            "error": None,
        }
    workflow_path = (
        (repo_root / workflow_file).resolve()
        if workflow_file
        else run_root / "local-workflows" / "identity-proof-comfyui.json"
    )
    workflow_found = workflow_path.exists()
    inventory = _discover_model_inventory(
        repo_root, _default_model_roots(repo_root, run_root, roots) if model_roots is None else model_roots
    )

    failure_codes: list[str] = []
    if not comfyui_available:
        failure_codes.append("COMFYUI_MISSING")
    if comfyui_available and dependency_status["status"] != "found":
        failure_codes.append("COMFYUI_DEPS_MISSING")
    if not workflow_found:
        failure_codes.append("LOCAL_WORKFLOW_MISSING")
    if inventory["status"] != "found":
        failure_codes.append("LOCAL_MODELS_MISSING")

    status = (
        "ready_for_creator_execution_approval"
        if not failure_codes
        else "blocked"
    )

    return {
        "schema_version": "1.0",
        "run_id": run_id,
        "created_at": now,
        "mode": "local_open_weight_stack_discovery",
        "status": status,
        "workflow_id": workflow_id,
        "recommended_model_stack": workflow,
        "zero_openai_api": True,
        "paid_cloud_api": False,
        "heavy_downloads_run": False,
        "model_execution_run": False,
        "comfyui": {
            "available": comfyui_available,
            "executable": executable,
            "existing_roots": existing_roots,
            "server_url": "http://127.0.0.1:8188",
            "server_available": server_available,
            "server_stats_observed": bool(stats),
        },
        "python_dependencies": dependency_status,
        "workflow": {
            "status": "found" if workflow_found else "missing",
            "path": _relative_path(workflow_path, repo_root),
            "exists": workflow_found,
        },
        "model_inventory": inventory,
        "failure_codes": failure_codes,
        "final_decision": {
            "status": "pending_creator_model_execution_approval"
            if status == "ready_for_creator_execution_approval"
            else "blocked",
            "failure_codes": failure_codes,
            "reason": _discovery_reason(status, failure_codes),
            "next_gate": "HITL_LOCAL_MODEL_EXECUTION_APPROVAL"
            if status == "ready_for_creator_execution_approval"
            else "HITL_LOCAL_MODEL_SETUP_APPROVAL",
        },
    }


def write_discovery_artifacts(
    repo_root: Path | str, discovery: dict[str, Any]
) -> tuple[Path, Path]:
    """Write local stack discovery JSON and report under the run evals folder."""

    repo_root = Path(repo_root).resolve()
    evals_dir = repo_root / "runs" / discovery["run_id"] / "evals"
    evals_dir.mkdir(parents=True, exist_ok=True)
    discovery_path = evals_dir / DISCOVERY_FILENAME
    report_path = evals_dir / DISCOVERY_REPORT_FILENAME
    discovery_path.write_text(json.dumps(discovery, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(render_discovery_report(discovery), encoding="utf-8")
    return discovery_path, report_path


def build_local_identity_execution_readiness(
    repo_root: Path | str,
    run_id: str,
    workflow_id: str = "option_b_sdxl_instantid_pulid_ipadapter",
    workflow_file: Path | str | None = None,
    discovery: dict[str, Any] | None = None,
    execution_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a no-download readiness gate for the next non-final proof attempt."""

    repo_root = Path(repo_root).resolve()
    run_root = repo_root / "runs" / run_id
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    workflow_path = (
        (repo_root / workflow_file).resolve()
        if workflow_file
        else run_root / "local-workflows" / "identity-proof-comfyui.json"
    )
    discovery = discovery or discover_local_identity_stack(
        repo_root=repo_root,
        run_id=run_id,
        workflow_id=workflow_id,
        workflow_file=_relative_path(workflow_path, repo_root),
    )
    execution_report = execution_report or _read_optional_json(
        run_root / "evals" / "local_identity_execution_report.json"
    )
    copied_inputs = _inspect_comfyui_identity_inputs(repo_root, run_root, execution_report)
    workflow_binding = _inspect_comfyui_workflow_binding(repo_root, workflow_path)
    hardware = _execution_hardware_status(execution_report)
    previous_attempts = (
        execution_report.get("attempts", []) if isinstance(execution_report, dict) else []
    )
    previous_cpu_stall = (
        isinstance(execution_report, dict)
        and execution_report.get("failure_code") == "LOCAL_CPU_EXECUTION_STALLED"
    )

    failure_codes: list[str] = []
    if discovery["status"] != "ready_for_creator_execution_approval":
        failure_codes.extend(discovery["failure_codes"])
    if copied_inputs["status"] != "pass":
        failure_codes.extend(copied_inputs["failure_codes"])
    if workflow_binding["status"] != "pass":
        failure_codes.extend(workflow_binding["failure_codes"])
    if previous_cpu_stall and hardware["effective_execution_device"] == "cpu":
        failure_codes.append("LOCAL_CPU_EXECUTION_STALLED")
    failure_codes = sorted(set(failure_codes))

    status = (
        "ready_for_creator_non_final_identity_proof_approval"
        if not failure_codes
        else "blocked"
    )
    return {
        "schema_version": "1.0",
        "run_id": run_id,
        "created_at": now,
        "mode": "local_identity_execution_readiness",
        "status": status,
        "workflow_id": workflow_id,
        "zero_openai_api": True,
        "paid_cloud_api": False,
        "heavy_downloads_run": False,
        "model_execution_run": False,
        "workflow": {
            "path": _relative_path(workflow_path, repo_root),
            "exists": workflow_path.exists(),
            "sha256": _sha256_file(workflow_path) if workflow_path.exists() else None,
        },
        "discovery_status": discovery["status"],
        "copied_reference_inputs": copied_inputs,
        "workflow_binding": workflow_binding,
        "hardware_status": hardware,
        "previous_execution": {
            "report_path": _relative_path(
                run_root / "evals" / "local_identity_execution_report.json",
                repo_root,
            ),
            "status": execution_report.get("status")
            if isinstance(execution_report, dict)
            else None,
            "failure_code": execution_report.get("failure_code")
            if isinstance(execution_report, dict)
            else None,
            "identity_proof_generated": execution_report.get("identity_proof_generated")
            if isinstance(execution_report, dict)
            else None,
            "final_artwork_generated": execution_report.get("final_artwork_generated")
            if isinstance(execution_report, dict)
            else None,
            "attempt_count": len(previous_attempts),
            "attempts": previous_attempts,
        },
        "failure_codes": failure_codes,
        "non_final_identity_proof_allowed": False,
        "final_carousel_generation_allowed": False,
        "final_decision": {
            "status": "pending_creator_model_execution_approval"
            if status == "ready_for_creator_non_final_identity_proof_approval"
            else "blocked",
            "failure_codes": failure_codes,
            "reason": _execution_readiness_reason(status, failure_codes),
            "next_gate": "HITL_LOCAL_MODEL_EXECUTION_APPROVAL"
            if status == "ready_for_creator_non_final_identity_proof_approval"
            else "HITL_LOCAL_EXECUTION_READINESS_REPAIR",
        },
    }


def write_execution_readiness_artifacts(
    repo_root: Path | str, readiness: dict[str, Any]
) -> tuple[Path, Path]:
    """Write execution readiness JSON and report under the run evals folder."""

    repo_root = Path(repo_root).resolve()
    evals_dir = repo_root / "runs" / readiness["run_id"] / "evals"
    evals_dir.mkdir(parents=True, exist_ok=True)
    readiness_path = evals_dir / READINESS_FILENAME
    report_path = evals_dir / READINESS_REPORT_FILENAME
    readiness_path.write_text(json.dumps(readiness, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(render_execution_readiness_report(readiness), encoding="utf-8")
    return readiness_path, report_path


def build_local_compute_diagnostic(
    repo_root: Path | str,
    run_id: str,
    workflow_id: str = "option_b_sdxl_instantid_pulid_ipadapter",
    workflow_file: Path | str | None = None,
    discovery: dict[str, Any] | None = None,
    readiness: dict[str, Any] | None = None,
    execution_report: dict[str, Any] | None = None,
    torch_probe: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Diagnose whether local compute can run the next non-final proof."""

    repo_root = Path(repo_root).resolve()
    run_root = repo_root / "runs" / run_id
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    roots = _default_comfyui_search_roots(repo_root, run_root)
    existing_roots = _dedupe_paths(
        [Path(root).resolve() for root in roots if Path(root).exists()]
    )
    discovery = discovery or discover_local_identity_stack(
        repo_root=repo_root,
        run_id=run_id,
        workflow_id=workflow_id,
        workflow_file=workflow_file,
    )
    readiness = readiness or build_local_identity_execution_readiness(
        repo_root=repo_root,
        run_id=run_id,
        workflow_id=workflow_id,
        workflow_file=workflow_file,
        discovery=discovery,
        execution_report=execution_report,
    )
    torch_probe = torch_probe or _probe_torch_accelerator(existing_roots)

    selected_device = torch_probe.get("selected_device")
    local_compute_ready = selected_device in {"cuda", "mps"}
    failure_codes: list[str] = []
    if torch_probe.get("status") != "pass":
        failure_codes.append("TORCH_ACCELERATOR_PROBE_FAILED")
    if not local_compute_ready:
        failure_codes.append("LOCAL_COMPUTE_CPU_ONLY")
    previous = readiness.get("previous_execution", {})
    if previous.get("failure_code") == "LOCAL_CPU_EXECUTION_STALLED":
        failure_codes.append("LOCAL_CPU_EXECUTION_STALLED")
    failure_codes = sorted(set(failure_codes))

    status = "ready_for_creator_model_execution_approval" if not failure_codes else "blocked"
    return {
        "schema_version": "1.0",
        "run_id": run_id,
        "created_at": now,
        "mode": "local_compute_diagnostic",
        "status": status,
        "workflow_id": workflow_id,
        "zero_openai_api": True,
        "paid_cloud_api": False,
        "heavy_downloads_run": False,
        "model_execution_run": False,
        "system": {
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "mac_ver": platform.mac_ver()[0],
            "current_python": sys.executable,
        },
        "comfyui_roots": [_relative_path(root, repo_root) for root in existing_roots],
        "torch_probe": torch_probe,
        "stack_discovery_status": discovery["status"],
        "execution_readiness_status": readiness["status"],
        "local_compute_ready": local_compute_ready,
        "selected_execution_device": selected_device,
        "failure_codes": failure_codes,
        "non_final_identity_proof_allowed": False,
        "final_carousel_generation_allowed": False,
        "final_decision": {
            "status": "pending_creator_model_execution_approval"
            if status == "ready_for_creator_model_execution_approval"
            else "blocked",
            "failure_codes": failure_codes,
            "reason": _compute_diagnostic_reason(status, failure_codes, torch_probe),
            "next_gate": "HITL_LOCAL_MODEL_EXECUTION_APPROVAL"
            if status == "ready_for_creator_model_execution_approval"
            else "HITL_LOCAL_COMPUTE_REPAIR_OR_HANDOFF",
        },
        "recommended_next_step": _compute_diagnostic_next_step(
            local_compute_ready, torch_probe
        ),
        "sources": [
            {
                "label": "PyTorch MPS backend",
                "url": "https://docs.pytorch.org/docs/2.12/notes/mps.html",
            },
            {
                "label": "ComfyUI",
                "url": "https://github.com/Comfy-Org/ComfyUI",
            },
        ],
    }


def write_compute_diagnostic_artifacts(
    repo_root: Path | str, diagnostic: dict[str, Any]
) -> tuple[Path, Path]:
    """Write local compute diagnostic JSON and report under the run evals folder."""

    repo_root = Path(repo_root).resolve()
    evals_dir = repo_root / "runs" / diagnostic["run_id"] / "evals"
    evals_dir.mkdir(parents=True, exist_ok=True)
    diagnostic_path = evals_dir / COMPUTE_DIAGNOSTIC_FILENAME
    report_path = evals_dir / COMPUTE_DIAGNOSTIC_REPORT_FILENAME
    diagnostic_path.write_text(json.dumps(diagnostic, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(render_compute_diagnostic_report(diagnostic), encoding="utf-8")
    return diagnostic_path, report_path


def build_local_identity_handoff_manifest(
    repo_root: Path | str,
    run_id: str,
    workflow_id: str = "option_b_sdxl_instantid_pulid_ipadapter",
    workflow_file: Path | str | None = None,
    diagnostic: dict[str, Any] | None = None,
    discovery: dict[str, Any] | None = None,
    execution_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a manifest for moving the proof bundle to a non-CPU machine."""

    repo_root = Path(repo_root).resolve()
    run_root = repo_root / "runs" / run_id
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    workflow_path = (
        (repo_root / workflow_file).resolve()
        if workflow_file
        else run_root / "local-workflows" / "identity-proof-comfyui.json"
    )
    execution_report = execution_report or _read_optional_json(
        run_root / "evals" / "local_identity_execution_report.json"
    )
    discovery = discovery or _read_optional_json(
        run_root / "evals" / DISCOVERY_FILENAME
    )
    diagnostic = diagnostic or _read_optional_json(
        run_root / "evals" / COMPUTE_DIAGNOSTIC_FILENAME
    )
    if diagnostic is None:
        diagnostic = build_local_compute_diagnostic(
            repo_root=repo_root,
            run_id=run_id,
            workflow_id=workflow_id,
            workflow_file=workflow_file,
            discovery=discovery,
            execution_report=execution_report,
        )

    files = _handoff_file_records(
        repo_root, run_id, workflow_path, execution_report, discovery
    )
    required_failures = [
        record
        for record in files
        if record["required"] and record["status"] != "pass"
    ]
    status = "ready_for_non_cpu_handoff" if not required_failures else "blocked"
    return {
        "schema_version": "1.0",
        "run_id": run_id,
        "created_at": now,
        "mode": "local_identity_handoff_manifest",
        "status": status,
        "workflow_id": workflow_id,
        "zero_openai_api": True,
        "paid_cloud_api": False,
        "source_compute_status": diagnostic.get("status"),
        "source_failure_codes": diagnostic.get("failure_codes", []),
        "source_selected_execution_device": diagnostic.get("selected_execution_device"),
        "target_requirements": {
            "torch_mps_available_or_cuda_available": True,
            "accepted_devices": ["mps", "cuda"],
            "cpu_allowed": False,
            "first_output_policy": "one_non_final_identity_proof_only",
        },
        "files": files,
        "missing_required_files": [record["path"] for record in required_failures],
        "commands": {
            "target_compute_diagnostic": (
                "PYTHONDONTWRITEBYTECODE=1 python3 scripts/local_identity_pipeline.py "
                f"--run-id {run_id} --workflow-id {workflow_id} "
                f"--workflow-file {_relative_path(workflow_path, repo_root)} "
                "--dry-run --compute-diagnostic"
            ),
            "target_execution_readiness": (
                "PYTHONDONTWRITEBYTECODE=1 python3 scripts/local_identity_pipeline.py "
                f"--run-id {run_id} --workflow-id {workflow_id} "
                f"--workflow-file {_relative_path(workflow_path, repo_root)} "
                "--dry-run --execution-readiness"
            ),
        },
        "guardrails": [
            "Do not run this proof on CPU.",
            "Do not generate final carousel slides from the handoff.",
            "Generate at most one non-final identity proof before creator QA.",
            "If identity proof fails, revise workflow before story art.",
        ],
        "sources": [
            {
                "label": "PyTorch MPS backend",
                "url": "https://docs.pytorch.org/docs/2.12/notes/mps.html",
            },
            {
                "label": "ComfyUI",
                "url": "https://github.com/Comfy-Org/ComfyUI",
            },
        ],
    }


def write_handoff_artifacts(
    repo_root: Path | str, manifest: dict[str, Any]
) -> tuple[Path, Path]:
    """Write handoff manifest JSON and report under the run handoff folder."""

    repo_root = Path(repo_root).resolve()
    handoff_dir = (
        repo_root
        / "runs"
        / manifest["run_id"]
        / "local-handoff"
        / "identity-proof"
    )
    handoff_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = handoff_dir / HANDOFF_MANIFEST_FILENAME
    report_path = handoff_dir / HANDOFF_REPORT_FILENAME
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(render_handoff_report(manifest), encoding="utf-8")
    return manifest_path, report_path


def render_report(proof: dict[str, Any]) -> str:
    """Render a short human-readable report for creator review."""

    workflow = proof["recommended_model_stack"]
    readiness = proof["workflow_readiness"]
    decision = proof["final_decision"]
    role_library = proof["role_based_reference_library"]
    refs = "\n".join(
        (
            f"| `{ref['person']}` | `{ref['role']}` | `{ref['path']}` | "
            f"`{ref['sha256']}` |"
        )
        for ref in proof["reference_inputs"]
    )
    role_bundle_refs = "\n".join(
        (
            f"| `{ref['subject']}` | `{ref['role']}` | `{ref['quality']}` | "
            f"`{ref['path']}` | `{ref['sha256']}` |"
        )
        for ref in role_library["default_generation_bundle_inputs"]
    )
    options = "\n".join(
        (
            f"- `{option['workflow_id']}`: {option['label']} - "
            f"{option['identity_method']}. Risk: {option['risk']}"
        )
        for option in proof["candidate_model_stacks"]
    )
    workflow_file = readiness.get("workflow_file") or "not provided"

    return f"""# Local Identity Reference Proof

Run: `{proof['run_id']}`

Status: `{proof['status']}`

## Decision

- Final Aachu/Zuv artwork remains `{decision['status']}`.
- Failure codes: `{', '.join(decision['failure_codes']) or 'none'}`.
- Reason: {decision['reason']}

## Proposed Local Stack

Recommended: `{proof['recommended_workflow_id']}`

{workflow['label']}

- Engine: `{workflow['engine']}`
- Identity method: {workflow['identity_method']}
- Why this first: {workflow['why_consider']}
- Risk: {workflow['risk']}

## Options

{options}

## Reference Input Proof

Prompt-only delivery allowed: `{proof['reference_delivery']['prompt_only_allowed']}`

| Person/group | Role | Path | SHA-256 |
| --- | --- | --- | --- |
{refs}

## Role-Based Dossier Proof

Dossier: `{role_library['dossier_path']}`

- Status: `{role_library['status']}`
- Dossier status: `{role_library['dossier_status']}`
- Minimum clean face anchors required per person: `{role_library['required_min_face_anchors_per_subject']}`
- Aachu face anchors: `{role_library['face_anchor_counts']['aachu']}`
- Zuv face anchors: `{role_library['face_anchor_counts']['zuv']}`
- Role reference inputs indexed: `{role_library['role_reference_input_count']}`

| Subject/group | Role | Quality | Path | SHA-256 |
| --- | --- | --- | --- | --- |
{role_bundle_refs}

## Workflow Readiness

- Status: `{readiness['status']}`
- Workflow file: `{workflow_file}`
- Workflow file exists: `{readiness['workflow_file_exists']}`
- Execution engine: `{readiness['engine']}`

## Non-Final Identity Proof Request

{proof['identity_proof_request']['composition']}

## Smallest Next Step

Refresh the dry-run proof and local stack discovery before any model execution:

```bash
python3 scripts/local_identity_pipeline.py --run-id {proof['run_id']} --workflow-id {proof['recommended_workflow_id']} --workflow-file runs/{proof['run_id']}/local-workflows/identity-proof-comfyui.json --dry-run
```

Then check:

- `runs/{proof['run_id']}/evals/local_identity_stack_discovery_report.md`
- `runs/{proof['run_id']}/evals/local_model_setup_approval_request.md`

If the workflow file or required local model weights are absent, keep the run blocked and do not generate carousel slides.
"""


def render_discovery_report(discovery: dict[str, Any]) -> str:
    """Render a creator-readable local stack discovery report."""

    minimum_model_lines = "\n".join(
        (
            f"- `{key}`: {len(value['candidates'])} candidate(s), "
            f"status `{value['status']}`"
        )
        for key, value in discovery["model_inventory"]["minimum_required_models"].items()
    )
    addon_model_lines = "\n".join(
        (
            f"- `{key}`: {len(value['candidates'])} candidate(s), "
            f"status `{value['status']}`"
        )
        for key, value in discovery["model_inventory"]["addon_models"].items()
    )
    roots = discovery["comfyui"]["existing_roots"] or ["none found"]
    root_lines = "\n".join(f"- `{root}`" for root in roots)
    failure_codes = ", ".join(discovery["failure_codes"]) or "none"
    deps = discovery["python_dependencies"]
    missing_roles = (
        ", ".join(discovery["model_inventory"]["missing_minimum_roles"]) or "none"
    )

    return f"""# Local Identity Stack Discovery

Run: `{discovery['run_id']}`

Status: `{discovery['status']}`

## Decision

- Final/model execution state: `{discovery['final_decision']['status']}`
- Failure codes: `{failure_codes}`
- Reason: {discovery['final_decision']['reason']}

## ComfyUI

- Available: `{discovery['comfyui']['available']}`
- Executable: `{discovery['comfyui']['executable'] or 'not found'}`
- Server URL: `{discovery['comfyui']['server_url']}`
- Server available: `{discovery['comfyui']['server_available']}`

Roots found:

{root_lines}

## Workflow File

- Status: `{discovery['workflow']['status']}`
- Path: `{discovery['workflow']['path']}`

## Python Dependencies

- Status: `{deps['status']}`
- Missing modules: `{', '.join(deps['missing_modules']) or 'none'}`

## Model Inventory

- Minimum status: `{discovery['model_inventory']['minimum_status']}`
- Optional add-on status: `{discovery['model_inventory']['optional_status']}`
- Missing minimum roles: `{missing_roles}`

Minimum InstantID proof models:

{minimum_model_lines}

Optional PuLID/IP-Adapter add-on models:

{addon_model_lines}

## Guardrail

This discovery step did not install dependencies, download model weights, or execute generation. Do not generate final carousel slides until a non-final identity proof image passes creator review.
"""


def render_execution_readiness_report(readiness: dict[str, Any]) -> str:
    """Render a creator-readable local execution readiness report."""

    failure_codes = ", ".join(readiness["failure_codes"]) or "none"
    copied = readiness["copied_reference_inputs"]
    workflow = readiness["workflow_binding"]
    hardware = readiness["hardware_status"]
    previous = readiness["previous_execution"]
    copied_rows = "\n".join(
        (
            f"| `{item['role']}` | `{item['path']}` | `{item['status']}` | "
            f"`{item.get('sha256') or 'missing'}` |"
        )
        for item in copied["inputs"]
    )
    workflow_images = ", ".join(workflow["load_images"]) or "none"

    return f"""# Local Identity Execution Readiness

Run: `{readiness['run_id']}`

Status: `{readiness['status']}`

## Decision

- Non-final identity proof allowed now: `{readiness['non_final_identity_proof_allowed']}`
- Final carousel generation allowed: `{readiness['final_carousel_generation_allowed']}`
- Failure codes: `{failure_codes}`
- Reason: {readiness['final_decision']['reason']}

## Workflow

- Path: `{readiness['workflow']['path']}`
- Exists: `{readiness['workflow']['exists']}`
- SHA-256: `{readiness['workflow']['sha256'] or 'missing'}`
- Binding status: `{workflow['status']}`
- LoadImage inputs: `{workflow_images}`
- ApplyInstantID nodes: `{workflow['apply_instantid_node_count']}`

## Copied Reference Inputs

- Status: `{copied['status']}`
- Failure codes: `{', '.join(copied['failure_codes']) or 'none'}`

| Role | Path | Status | SHA-256 |
| --- | --- | --- | --- |
{copied_rows}

## Hardware

- Effective execution device: `{hardware['effective_execution_device']}`
- MPS available: `{hardware['mps_available']}`
- CUDA available: `{hardware['cuda_available']}`

## Previous Execution

- Report: `{previous['report_path']}`
- Status: `{previous['status']}`
- Failure code: `{previous['failure_code']}`
- Identity proof generated: `{previous['identity_proof_generated']}`
- Final artwork generated: `{previous['final_artwork_generated']}`
- Attempts: `{previous['attempt_count']}`

## Guardrail

This readiness check did not install dependencies, download model weights, or execute generation. Keep final Aachu/Zuv carousel generation blocked until a non-final identity proof image is generated locally and accepted by creator QA.
"""


def render_compute_diagnostic_report(diagnostic: dict[str, Any]) -> str:
    """Render a creator-readable compute diagnostic report."""

    probe = diagnostic["torch_probe"]
    failure_codes = ", ".join(diagnostic["failure_codes"]) or "none"
    roots = diagnostic["comfyui_roots"] or ["none found"]
    root_lines = "\n".join(f"- `{root}`" for root in roots)
    sources = "\n".join(
        f"- [{source['label']}]({source['url']})" for source in diagnostic["sources"]
    )

    return f"""# Local Compute Diagnostic

Run: `{diagnostic['run_id']}`

Status: `{diagnostic['status']}`

## Decision

- Local compute ready: `{diagnostic['local_compute_ready']}`
- Selected execution device: `{diagnostic['selected_execution_device']}`
- Non-final identity proof allowed now: `{diagnostic['non_final_identity_proof_allowed']}`
- Final carousel generation allowed: `{diagnostic['final_carousel_generation_allowed']}`
- Failure codes: `{failure_codes}`
- Reason: {diagnostic['final_decision']['reason']}

## Torch Probe

- Python: `{probe.get('python') or 'not found'}`
- Torch version: `{probe.get('torch_version') or 'unknown'}`
- MPS built: `{probe.get('mps_built')}`
- MPS available: `{probe.get('mps_available')}`
- CUDA available: `{probe.get('cuda_available')}`
- CUDA device count: `{probe.get('cuda_device_count')}`
- Unavailable reason: `{probe.get('unavailable_reason') or 'none'}`

## Machine

- Platform: `{diagnostic['system']['platform']}`
- Machine: `{diagnostic['system']['machine']}`
- macOS: `{diagnostic['system']['mac_ver'] or 'not macOS'}`

## ComfyUI Roots

{root_lines}

## Stack State

- Stack discovery: `{diagnostic['stack_discovery_status']}`
- Execution readiness: `{diagnostic['execution_readiness_status']}`

## Recommended Next Step

{diagnostic['recommended_next_step']}

## Sources

{sources}

## Guardrail

This diagnostic did not install dependencies, download model weights, or execute generation. Keep final Aachu/Zuv carousel generation blocked until a non-final identity proof image is generated on a non-CPU device and accepted by creator QA.
"""


def render_handoff_report(manifest: dict[str, Any]) -> str:
    """Render a concise report for the GPU/MPS handoff bundle."""

    failures = manifest["missing_required_files"] or ["none"]
    failure_lines = "\n".join(f"- `{path}`" for path in failures)
    file_rows = "\n".join(
        (
            f"| `{record['role']}` | `{record['path']}` | "
            f"`{record['status']}` | `{record.get('sha256') or 'missing'}` |"
        )
        for record in manifest["files"]
    )
    guardrails = "\n".join(f"- {item}" for item in manifest["guardrails"])
    sources = "\n".join(
        f"- [{source['label']}]({source['url']})" for source in manifest["sources"]
    )

    return f"""# Local Identity Handoff

Run: `{manifest['run_id']}`

Status: `{manifest['status']}`

## Why This Exists

The source machine is `{manifest['source_selected_execution_device']}` and is blocked by `{', '.join(manifest['source_failure_codes']) or 'none'}`. Move this run bundle to a machine where PyTorch reports `mps_available: true` or `cuda_available: true`.

## Missing Required Files

{failure_lines}

## Files To Transfer / Verify

| Role | Path | Status | SHA-256 |
| --- | --- | --- | --- |
{file_rows}

## Target Machine Checks

```bash
{manifest['commands']['target_compute_diagnostic']}
```

```bash
{manifest['commands']['target_execution_readiness']}
```

## Guardrails

{guardrails}

## Sources

{sources}
"""


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ReferenceSelectionError(f"Missing selected reference manifest: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _read_optional_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _handoff_file_records(
    repo_root: Path,
    run_id: str,
    workflow_path: Path,
    execution_report: dict[str, Any] | None,
    discovery: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    run_root = repo_root / "runs" / run_id
    records = [
        _handoff_record(repo_root, "workflow", workflow_path, True),
        _handoff_record(
            repo_root,
            "selected_reference_manifest",
            run_root / "references-used" / "selected_references.json",
            True,
        ),
        _handoff_record(
            repo_root,
            "local_reference_proof",
            run_root / "evals" / PROOF_FILENAME,
            True,
        ),
        _handoff_record(
            repo_root,
            "local_stack_discovery",
            run_root / "evals" / DISCOVERY_FILENAME,
            True,
        ),
        _handoff_record(
            repo_root,
            "local_execution_readiness",
            run_root / "evals" / READINESS_FILENAME,
            True,
        ),
        _handoff_record(
            repo_root,
            "local_compute_diagnostic",
            run_root / "evals" / COMPUTE_DIAGNOSTIC_FILENAME,
            True,
        ),
    ]

    if isinstance(execution_report, dict):
        for item in execution_report.get("workflow_inputs", []):
            if not isinstance(item, dict) or not item.get("path"):
                continue
            records.append(
                _handoff_record(
                    repo_root,
                    item.get("role") or "workflow_input",
                    repo_root / item["path"],
                    True,
                    item.get("sha256"),
                )
            )
        model_stack = execution_report.get("model_stack", {})
        for role in ("base_checkpoint", "identity_adapter", "controlnet"):
            item = model_stack.get(role)
            if isinstance(item, dict) and item.get("path"):
                records.append(
                    _handoff_record(
                        repo_root,
                        role,
                        repo_root / item["path"],
                        True,
                        item.get("sha256"),
                    )
                )

    if isinstance(discovery, dict):
        antelope = (
            discovery.get("model_inventory", {})
            .get("minimum_required_models", {})
            .get("insightface_antelopev2", {})
            .get("candidates", [])
        )
        for index, rel_path in enumerate(antelope, 1):
            records.append(
                _handoff_record(
                    repo_root,
                    f"insightface_antelopev2_{index}",
                    repo_root / rel_path,
                    True,
                )
            )

    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for record in records:
        key = record["path"]
        if key in seen:
            continue
        seen.add(key)
        deduped.append(record)
    return deduped


def _handoff_record(
    repo_root: Path,
    role: str,
    path: Path,
    required: bool,
    expected_sha256: str | None = None,
) -> dict[str, Any]:
    exists = path.exists()
    sha256 = _sha256_file(path) if exists and path.is_file() else None
    if not exists:
        status = "missing"
    elif expected_sha256 and sha256 != expected_sha256:
        status = "sha_mismatch"
    else:
        status = "pass"
    return {
        "role": role,
        "path": _relative_path(path, repo_root),
        "required": required,
        "exists": exists,
        "status": status,
        "size_bytes": path.stat().st_size if exists and path.is_file() else None,
        "sha256": sha256,
        "expected_sha256": expected_sha256,
    }


def _build_reference_inputs(
    repo_root: Path, selected_references: dict[str, Any]
) -> list[dict[str, Any]]:
    identity = selected_references.get("identity_references", {})
    refs: list[dict[str, Any]] = []

    for person in ("aachu", "zuv"):
        for rel_path in identity.get(person, []):
            role = (
                f"{person}_identity_face_crop"
                if "face" in Path(rel_path).stem.lower()
                else f"{person}_identity_portrait"
            )
            refs.append(_reference_record(repo_root, rel_path, person, role))

    for rel_path in identity.get("together", []):
        refs.append(
            _reference_record(
                repo_root, rel_path, "couple", "couple_relationship_reference"
            )
        )

    for rel_path in selected_references.get("style_references", []):
        refs.append(_reference_record(repo_root, rel_path, "style", "style_reference"))

    return refs


def _build_role_based_reference_library(repo_root: Path) -> dict[str, Any]:
    dossier_path = repo_root / IDENTITY_DOSSIER_PATH
    if not dossier_path.exists():
        raise ReferenceSelectionError(
            f"Missing role-based identity dossier: {IDENTITY_DOSSIER_PATH}"
        )

    dossier = _read_json(dossier_path)
    imported_references = dossier.get("imported_references", [])
    if not imported_references:
        raise ReferenceSelectionError("Identity dossier has no imported_references.")

    role_inputs = [
        _dossier_reference_record(repo_root, reference)
        for reference in imported_references
    ]
    records_by_path = {reference["path"]: reference for reference in role_inputs}
    _validate_role_based_reference_library(dossier, role_inputs, records_by_path)

    selected_bundle_paths = dossier.get("selected_generation_bundle", [])
    default_generation_bundle_inputs = [
        records_by_path[path] for path in selected_bundle_paths if path in records_by_path
    ]
    missing_bundle_paths = [
        path for path in selected_bundle_paths if path not in records_by_path
    ]
    if missing_bundle_paths:
        raise ReferenceSelectionError(
            "Selected generation bundle paths are missing from imported_references: "
            + ", ".join(missing_bundle_paths)
        )

    contact_sheet_inputs = [
        _reference_record(repo_root, path, "contact_sheet", "role_contact_sheet")
        for path in dossier.get("reference_images_for_generation", [])
        if "_dossier/" in path
    ]
    counts_by_subject_role = Counter(
        f"{reference['subject']}:{reference['role']}"
        for reference in role_inputs
    )
    face_anchor_counts = {
        person: sum(
            1
            for reference in role_inputs
            if reference["subject"] == person and reference["role"] == "face_anchor"
        )
        for person in ("aachu", "zuv")
    }

    return {
        "status": "pass",
        "dossier_path": _relative_path(dossier_path, repo_root),
        "schema_version": dossier.get("schema_version"),
        "dossier_status": dossier.get("status"),
        "required_min_face_anchors_per_subject": MIN_FACE_ANCHORS_PER_SUBJECT,
        "face_anchor_counts": face_anchor_counts,
        "counts_by_subject_role": dict(sorted(counts_by_subject_role.items())),
        "contact_sheet_inputs": contact_sheet_inputs,
        "default_generation_bundle_inputs": default_generation_bundle_inputs,
        "role_reference_input_count": len(role_inputs),
        "role_reference_inputs": role_inputs,
    }


def _dossier_reference_record(
    repo_root: Path, reference: dict[str, Any]
) -> dict[str, Any]:
    rel_path = reference.get("path")
    if not rel_path:
        raise ReferenceSelectionError(
            f"Identity dossier reference {reference.get('id', '<unknown>')} lacks path."
        )
    path = (repo_root / rel_path).resolve()
    if not path.exists():
        raise ReferenceSelectionError(f"Missing dossier reference image: {rel_path}")
    if not _is_image_path(path):
        raise ReferenceSelectionError(f"Dossier reference is not an image file: {rel_path}")

    digest = _sha256_file(path)
    expected_digest = reference.get("sha256")
    if expected_digest and digest != expected_digest:
        raise ReferenceSelectionError(
            f"Dossier SHA-256 mismatch for {rel_path}; update identity-dossier.json."
        )

    return {
        "dossier_id": reference.get("id"),
        "subject": reference.get("subject"),
        "person": reference.get("subject"),
        "role": reference.get("role"),
        "quality": reference.get("quality"),
        "path": rel_path,
        "absolute_path": str(path),
        "delivery_mode": "local_binary_input",
        "input_kind": "image_file_bytes",
        "use_for": reference.get("use_for", []),
        "do_not_use_for": reference.get("do_not_use_for", []),
        "source_path": reference.get("source_path"),
        "source_filename": reference.get("source_filename"),
        "size_bytes": path.stat().st_size,
        "sha256": digest,
    }


def _reference_record(
    repo_root: Path, rel_path: str, person: str, role: str
) -> dict[str, Any]:
    path = (repo_root / rel_path).resolve()
    if not path.exists():
        raise ReferenceSelectionError(f"Missing reference image: {rel_path}")
    if not _is_image_path(path):
        raise ReferenceSelectionError(f"Reference is not an image file: {rel_path}")
    return {
        "person": person,
        "role": role,
        "path": rel_path,
        "absolute_path": str(path),
        "delivery_mode": "local_binary_input",
        "input_kind": "image_file_bytes",
        "size_bytes": path.stat().st_size,
        "sha256": _sha256_file(path),
    }


def _validate_required_identity_inputs(reference_inputs: list[dict[str, Any]]) -> None:
    people = {ref["person"] for ref in reference_inputs}
    missing = [person for person in ("aachu", "zuv") if person not in people]
    if missing:
        raise ReferenceSelectionError(
            "Missing required identity references: " + ", ".join(missing)
        )
    for person in ("aachu", "zuv"):
        if not any(
            ref["person"] == person and ref["role"].endswith("_identity_face_crop")
            for ref in reference_inputs
        ):
            raise ReferenceSelectionError(f"Missing face crop reference for {person}")


def _validate_role_based_reference_library(
    dossier: dict[str, Any],
    role_inputs: list[dict[str, Any]],
    records_by_path: dict[str, dict[str, Any]],
) -> None:
    face_anchor_counts = {
        person: sum(
            1
            for reference in role_inputs
            if reference["subject"] == person and reference["role"] == "face_anchor"
        )
        for person in ("aachu", "zuv")
    }
    if any(
        count < MIN_FACE_ANCHORS_PER_SUBJECT
        for count in face_anchor_counts.values()
    ):
        raise ReferenceSelectionError(
            "At least 4 clean face anchors are required for aachu and zuv; "
            f"observed aachu={face_anchor_counts['aachu']}, "
            f"zuv={face_anchor_counts['zuv']}."
        )

    for reference in role_inputs:
        if not reference["role"]:
            raise ReferenceSelectionError(
                f"Dossier reference lacks role: {reference['path']}"
            )
        if not reference["subject"]:
            raise ReferenceSelectionError(
                f"Dossier reference lacks subject: {reference['path']}"
            )
        if reference["role"] == "face_anchor":
            expected_prefix = f"references/identity/{reference['subject']}/face/"
            if reference["subject"] not in {"aachu", "zuv"}:
                raise ReferenceSelectionError(
                    f"Face anchor has invalid subject {reference['subject']}: "
                    f"{reference['path']}"
                )
            if not reference["path"].startswith(expected_prefix):
                raise ReferenceSelectionError(
                    "Face anchor must live in the subject face folder: "
                    f"{reference['path']}"
                )
        elif reference["role"] in SUPPORT_REFERENCE_ROLES_REQUIRING_FACE_IDENTITY_BLOCK:
            if "face_identity" not in reference["do_not_use_for"]:
                raise ReferenceSelectionError(
                    "Support references must explicitly block face_identity use: "
                    f"{reference['path']}"
                )

    face_visible_default = (
        dossier.get("selected_generation_recipe", {})
        .get("face_visible_default", {})
    )
    default_groups = {
        "aachu": face_visible_default.get("default_aachu_close_face_anchors", []),
        "zuv": face_visible_default.get("default_zuv_close_face_anchors", []),
    }
    for person, paths in default_groups.items():
        if len(paths) < MIN_FACE_ANCHORS_PER_SUBJECT:
            raise ReferenceSelectionError(
                f"Default {person} close face anchors must include at least "
                f"{MIN_FACE_ANCHORS_PER_SUBJECT} images."
            )
        for rel_path in paths:
            record = records_by_path.get(rel_path)
            if not record:
                raise ReferenceSelectionError(
                    f"Default {person} face anchor missing from imported_references: "
                    f"{rel_path}"
                )
            if record["subject"] != person or record["role"] != "face_anchor":
                raise ReferenceSelectionError(
                    f"Default {person} face anchor points to wrong role: {rel_path}"
                )


def _select_workflow(workflow_id: str) -> dict[str, Any]:
    try:
        return LOCAL_WORKFLOW_OPTIONS[workflow_id]
    except KeyError as exc:
        known = ", ".join(sorted(LOCAL_WORKFLOW_OPTIONS))
        raise ValueError(f"Unknown workflow_id '{workflow_id}'. Known: {known}") from exc


def _workflow_readiness(
    repo_root: Path, workflow_id: str, workflow_file: Path | str | None
) -> dict[str, Any]:
    workflow = _select_workflow(workflow_id)
    workflow_path = (repo_root / workflow_file).resolve() if workflow_file else None
    exists = bool(workflow_path and workflow_path.exists())
    if exists:
        status = "ready"
        failure_codes: list[str] = []
        reason = (
            "A local workflow file exists. Model downloads and execution still require "
            "creator approval and separate identity proof QA."
        )
    else:
        status = "blocked"
        failure_codes = ["LOCAL_WORKFLOW_MISSING"]
        reason = (
            "No executable local workflow file was provided, so this dry run can prove "
            "reference binding but cannot generate an identity proof image."
        )

    return {
        "status": status,
        "workflow_id": workflow_id,
        "workflow_file": _relative_path(workflow_path, repo_root) if workflow_path else None,
        "workflow_file_exists": exists,
        "engine": workflow["engine"],
        "heavy_downloads_run": False,
        "model_execution_run": False,
        "failure_codes": failure_codes,
        "reason": reason,
    }


def _discover_model_inventory(
    repo_root: Path, model_roots: list[Path | str]
) -> dict[str, Any]:
    existing_roots = _dedupe_paths(
        [Path(root).resolve() for root in model_roots if Path(root).exists()]
    )
    minimum_required = {
        role: _find_model_artifact(existing_roots, spec, repo_root)
        for role, spec in MINIMUM_MODEL_ARTIFACTS.items()
    }
    addon_models = {
        role: _find_model_artifact(existing_roots, spec, repo_root)
        for role, spec in ADDON_MODEL_ARTIFACTS.items()
    }
    missing_minimum_roles = [
        role
        for role, artifact in minimum_required.items()
        if artifact["status"] != "found"
    ]
    status = "found" if existing_roots and not missing_minimum_roles else "missing"
    optional_found = sum(
        1 for artifact in addon_models.values() if artifact["status"] == "found"
    )
    optional_status = (
        "found"
        if optional_found == len(addon_models)
        else "partial"
        if optional_found
        else "missing"
    )
    legacy_required = _legacy_keyword_inventory(existing_roots, repo_root)
    return {
        "status": status,
        "minimum_status": status,
        "optional_status": optional_status,
        "missing_minimum_roles": missing_minimum_roles,
        "roots_checked": [_relative_path(root, repo_root) for root in existing_roots],
        "minimum_required_models": minimum_required,
        "addon_models": addon_models,
        "required_models": legacy_required,
    }


def _find_model_artifact(
    roots: list[Path], spec: dict[str, Any], repo_root: Path
) -> dict[str, Any]:
    required_files = spec.get("required_files", ())
    if required_files:
        for root in roots:
            paths = [root / rel_path for rel_path in required_files]
            if all(path.exists() for path in paths):
                return {
                    "status": "found",
                    "match_type": "required_file_set",
                    "candidates": [_relative_path(path, repo_root) for path in paths],
                }
        return {
            "status": "missing",
            "match_type": "required_file_set",
            "candidates": [],
            "required_files": list(required_files),
        }

    target_paths = spec.get("target_paths", ())
    candidates: list[str] = []
    for root in roots:
        for rel_path in target_paths:
            path = root / rel_path
            if path.exists():
                candidates.append(_relative_path(path, repo_root) or str(path))
    if not candidates:
        candidates = _find_model_candidates(
            roots,
            tuple(spec.get("keywords", ())),
            repo_root,
            tuple(spec.get("search_subdirs", ())),
        )

    return {
        "status": "found" if candidates else "missing",
        "match_type": "exact_path_or_keyword",
        "target_paths": list(target_paths),
        "keywords": list(spec.get("keywords", ())),
        "candidates": candidates,
    }


def _legacy_keyword_inventory(
    existing_roots: list[Path], repo_root: Path
) -> dict[str, dict[str, Any]]:
    required: dict[str, dict[str, Any]] = {}
    for key, keywords in MODEL_KEYWORDS.items():
        candidates = _find_model_candidates(existing_roots, keywords, repo_root)
        required[key] = {
            "status": "found" if candidates else "missing",
            "keywords": list(keywords),
            "candidates": candidates,
        }
    return required


def _find_model_candidates(
    roots: list[Path],
    keywords: tuple[str, ...],
    repo_root: Path,
    search_subdirs: tuple[str, ...] = (),
) -> list[str]:
    candidates: list[str] = []
    allowed_suffixes = {".safetensors", ".ckpt", ".pt", ".pth", ".bin", ".onnx"}
    for root in roots:
        scan_roots = [root / subdir for subdir in search_subdirs] if search_subdirs else [root]
        for scan_root in scan_roots:
            if not scan_root.exists():
                continue
            for path in scan_root.rglob("*"):
                if len(candidates) >= 20:
                    return candidates
                if not path.is_file() or path.suffix.lower() not in allowed_suffixes:
                    continue
                searchable = str(path.relative_to(root)).lower()
                if any(keyword in searchable for keyword in keywords):
                    candidates.append(_relative_path(path, repo_root) or str(path))
    return candidates


def _dedupe_paths(paths: list[Path]) -> list[Path]:
    deduped: list[Path] = []
    seen: set[Path | tuple[int, int]] = set()
    for path in paths:
        resolved = path.resolve()
        try:
            stat_key: Path | tuple[int, int] = (resolved.stat().st_dev, resolved.stat().st_ino)
        except OSError:
            stat_key = resolved
        if stat_key in seen:
            continue
        seen.add(stat_key)
        deduped.append(resolved)
    return deduped


def _python_dependency_status(python_modules: list[str] | None | str) -> dict[str, Any]:
    required = list(REQUIRED_COMFYUI_MODULES)
    if python_modules == "auto":
        present = [
            module for module in required if importlib.util.find_spec(module) is not None
        ]
    elif python_modules is None:
        present = []
    else:
        present = list(python_modules)

    missing = [module for module in required if module not in present]
    return {
        "status": "found" if not missing else "missing",
        "required_modules": required,
        "present_modules": present,
        "missing_modules": missing,
    }


def _probe_comfyui_python_modules(
    comfyui_roots: list[Path],
) -> tuple[list[str] | None, dict[str, Any]]:
    required = list(REQUIRED_COMFYUI_MODULES)
    for root in comfyui_roots:
        for rel_python in (
            ".venv/bin/python",
            "venv/bin/python",
            "python_embeded/python.exe",
        ):
            python_path = root / rel_python
            if not python_path.exists():
                continue
            code = (
                "import importlib.util, json; "
                f"mods={required!r}; "
                "print(json.dumps({m: importlib.util.find_spec(m) is not None for m in mods}))"
            )
            try:
                result = subprocess.run(
                    [str(python_path), "-c", code],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
            except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
                return (
                    None,
                    {
                        "method": "comfyui_venv",
                        "python": str(python_path),
                        "error": str(exc),
                    },
                )
            try:
                observed = json.loads(result.stdout)
            except json.JSONDecodeError as exc:
                return (
                    None,
                    {
                        "method": "comfyui_venv",
                        "python": str(python_path),
                        "error": str(exc),
                    },
                )
            present = [module for module in required if observed.get(module)]
            return (
                present,
                {
                    "method": "comfyui_venv",
                    "python": str(python_path),
                    "error": None,
                },
            )
    return (
        None,
        {
            "method": "current_python_fallback",
            "python": None,
            "error": "no ComfyUI virtualenv python found",
        },
    )


def _probe_torch_accelerator(comfyui_roots: list[Path]) -> dict[str, Any]:
    for root in comfyui_roots:
        for rel_python in (
            ".venv/bin/python",
            "venv/bin/python",
            "python_embeded/python.exe",
        ):
            python_path = root / rel_python
            if not python_path.exists():
                continue
            code = (
                "import json, platform, sys, torch; "
                "mps_built=torch.backends.mps.is_built(); "
                "mps_available=torch.backends.mps.is_available(); "
                "cuda_available=torch.cuda.is_available(); "
                "selected='cuda' if cuda_available else ('mps' if mps_available else 'cpu'); "
                "print(json.dumps({"
                "'python': sys.executable, "
                "'platform': platform.platform(), "
                "'machine': platform.machine(), "
                "'torch_version': torch.__version__, "
                "'mps_built': mps_built, "
                "'mps_available': mps_available, "
                "'cuda_available': cuda_available, "
                "'cuda_device_count': torch.cuda.device_count(), "
                "'selected_device': selected"
                "}))"
            )
            try:
                result = subprocess.run(
                    [str(python_path), "-c", code],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                observed = json.loads(result.stdout)
            except (
                OSError,
                subprocess.CalledProcessError,
                subprocess.TimeoutExpired,
                json.JSONDecodeError,
            ) as exc:
                return {
                    "status": "fail",
                    "python": str(python_path),
                    "error": str(exc),
                    "selected_device": "cpu",
                    "unavailable_reason": "TORCH_PROBE_FAILED",
                }
            observed["status"] = "pass"
            observed["unavailable_reason"] = _torch_unavailable_reason(observed)
            return observed

    return {
        "status": "fail",
        "python": None,
        "error": "No ComfyUI virtualenv python found.",
        "mps_built": None,
        "mps_available": None,
        "cuda_available": None,
        "cuda_device_count": 0,
        "selected_device": "cpu",
        "unavailable_reason": "COMFYUI_PYTHON_NOT_FOUND",
    }


def _torch_unavailable_reason(probe: dict[str, Any]) -> str | None:
    if probe.get("cuda_available") or probe.get("mps_available"):
        return None
    if probe.get("mps_built") is False:
        return "PYTORCH_NOT_BUILT_WITH_MPS"
    if probe.get("mps_built") is True and not probe.get("mps_available"):
        return "MACOS_OR_DEVICE_NOT_MPS_ENABLED"
    return "NO_CUDA_OR_MPS_ACCELERATOR"


def _default_comfyui_search_roots(repo_root: Path, run_root: Path) -> list[Path]:
    home = Path.home()
    return [
        run_root / "local-tools" / "ComfyUI",
        run_root / "local-tools" / "comfyui",
        repo_root / "ComfyUI",
        home / "ComfyUI",
        home / "comfyui",
        home / "Documents" / "ComfyUI",
        home / "Downloads" / "ComfyUI",
    ]


def _default_model_roots(repo_root: Path, run_root: Path, comfyui_roots: list[Path | str]) -> list[Path]:
    roots = [
        repo_root / "models",
        run_root / "local-models",
        Path.home() / ".cache" / "huggingface" / "hub",
    ]
    for root in comfyui_roots:
        roots.append(Path(root) / "models")
    return roots


def _fetch_comfyui_system_stats() -> dict[str, Any] | None:
    request = urllib.request.Request("http://127.0.0.1:8188/system_stats")
    try:
        with urllib.request.urlopen(request, timeout=1.0) as response:
            return json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError, json.JSONDecodeError):
        return None


def _inspect_comfyui_identity_inputs(
    repo_root: Path, run_root: Path, execution_report: dict[str, Any] | None
) -> dict[str, Any]:
    expected_inputs = (
        execution_report.get("workflow_inputs", [])
        if isinstance(execution_report, dict)
        else []
    )
    if not expected_inputs:
        expected_inputs = [
            {
                "role": "aachu_face_anchor",
                "path": _relative_path(
                    run_root
                    / "local-tools/ComfyUI/input/astory_identity_proof/aachu_face_anchor.jpg",
                    repo_root,
                ),
                "sha256": None,
            },
            {
                "role": "zuv_face_anchor",
                "path": _relative_path(
                    run_root
                    / "local-tools/ComfyUI/input/astory_identity_proof/zuv_face_anchor.jpg",
                    repo_root,
                ),
                "sha256": None,
            },
            {
                "role": "together_pose_context",
                "path": _relative_path(
                    run_root
                    / "local-tools/ComfyUI/input/astory_identity_proof/together_pose_context.jpg",
                    repo_root,
                ),
                "sha256": None,
            },
        ]

    records: list[dict[str, Any]] = []
    failure_codes: list[str] = []
    for item in expected_inputs:
        rel_path = item.get("path")
        path = repo_root / rel_path if rel_path else None
        exists = bool(path and path.exists())
        actual_sha = _sha256_file(path) if exists and path else None
        expected_sha = item.get("sha256")
        status = "pass"
        if not exists:
            status = "missing"
            failure_codes.append("COMFYUI_INPUT_REFERENCE_MISSING")
        elif expected_sha and actual_sha != expected_sha:
            status = "sha_mismatch"
            failure_codes.append("COMFYUI_INPUT_REFERENCE_SHA_MISMATCH")
        records.append(
            {
                "role": item.get("role"),
                "path": rel_path,
                "status": status,
                "size_bytes": path.stat().st_size if exists and path else None,
                "sha256": actual_sha,
                "expected_sha256": expected_sha,
            }
        )

    required_roles = {"aachu_face_anchor", "zuv_face_anchor", "together_pose_context"}
    observed_roles = {record["role"] for record in records}
    missing_roles = sorted(required_roles - observed_roles)
    if missing_roles:
        failure_codes.append("COMFYUI_INPUT_REFERENCE_ROLE_MISSING")

    return {
        "status": "pass" if not failure_codes else "fail",
        "input_dir": _relative_path(
            run_root / "local-tools/ComfyUI/input/astory_identity_proof",
            repo_root,
        ),
        "required_roles": sorted(required_roles),
        "missing_roles": missing_roles,
        "inputs": records,
        "failure_codes": sorted(set(failure_codes)),
    }


def _inspect_comfyui_workflow_binding(repo_root: Path, workflow_path: Path) -> dict[str, Any]:
    required_images = {
        "astory_identity_proof/aachu_face_anchor.jpg",
        "astory_identity_proof/zuv_face_anchor.jpg",
        "astory_identity_proof/together_pose_context.jpg",
    }
    if not workflow_path.exists():
        return {
            "status": "fail",
            "path": _relative_path(workflow_path, repo_root),
            "load_images": [],
            "missing_load_images": sorted(required_images),
            "checkpoint": None,
            "apply_instantid_node_count": 0,
            "failure_codes": ["LOCAL_WORKFLOW_MISSING"],
        }

    try:
        workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {
            "status": "fail",
            "path": _relative_path(workflow_path, repo_root),
            "load_images": [],
            "missing_load_images": sorted(required_images),
            "checkpoint": None,
            "apply_instantid_node_count": 0,
            "failure_codes": ["LOCAL_WORKFLOW_INVALID_JSON"],
        }

    nodes = workflow.values() if isinstance(workflow, dict) else []
    load_images = sorted(
        str(node.get("inputs", {}).get("image"))
        for node in nodes
        if isinstance(node, dict)
        and node.get("class_type") == "LoadImage"
        and node.get("inputs", {}).get("image")
    )
    checkpoints = sorted(
        str(node.get("inputs", {}).get("ckpt_name"))
        for node in nodes
        if isinstance(node, dict)
        and node.get("class_type") == "CheckpointLoaderSimple"
        and node.get("inputs", {}).get("ckpt_name")
    )
    apply_instantid_count = sum(
        1
        for node in nodes
        if isinstance(node, dict) and node.get("class_type") == "ApplyInstantID"
    )
    missing_images = sorted(required_images - set(load_images))
    failure_codes: list[str] = []
    if missing_images:
        failure_codes.append("LOCAL_WORKFLOW_REFERENCE_INPUT_MISSING")
    if "sd_xl_base_1.0.safetensors" not in checkpoints:
        failure_codes.append("LOCAL_WORKFLOW_SDXL_CHECKPOINT_MISSING")
    if apply_instantid_count < 2:
        failure_codes.append("LOCAL_WORKFLOW_IDENTITY_CONDITIONING_MISSING")

    return {
        "status": "pass" if not failure_codes else "fail",
        "path": _relative_path(workflow_path, repo_root),
        "load_images": load_images,
        "missing_load_images": missing_images,
        "checkpoint": checkpoints[0] if checkpoints else None,
        "apply_instantid_node_count": apply_instantid_count,
        "failure_codes": failure_codes,
    }


def _execution_hardware_status(
    execution_report: dict[str, Any] | None,
) -> dict[str, Any]:
    hardware = (
        execution_report.get("hardware_status", {})
        if isinstance(execution_report, dict)
        else {}
    )
    mps_available = bool(hardware.get("mps_available"))
    cuda_available = bool(hardware.get("cuda_available"))
    effective_device = hardware.get("effective_execution_device")
    if cuda_available:
        effective_device = "cuda"
    elif mps_available:
        effective_device = "mps"
    elif not effective_device:
        effective_device = "cpu"
    return {
        "mps_available": mps_available,
        "mps_built": bool(hardware.get("mps_built")),
        "cuda_available": cuda_available,
        "effective_execution_device": effective_device,
    }


def _discovery_reason(status: str, failure_codes: list[str]) -> str:
    if status == "ready_for_creator_execution_approval":
        return (
            "ComfyUI, a local workflow file, and required model candidates are present. "
            "Model execution is still gated on creator approval and identity QA."
        )
    return (
        "Local discovery could not find every required component: "
        + ", ".join(failure_codes)
        + "."
    )


def _execution_readiness_reason(status: str, failure_codes: list[str]) -> str:
    if status == "ready_for_creator_non_final_identity_proof_approval":
        return (
            "Local references, workflow bindings, required models, and execution "
            "device checks passed. Creator approval is still required before a "
            "single non-final identity proof attempt."
        )
    return (
        "Local identity execution is not ready: "
        + ", ".join(failure_codes)
        + "."
    )


def _compute_diagnostic_reason(
    status: str, failure_codes: list[str], torch_probe: dict[str, Any]
) -> str:
    if status == "ready_for_creator_model_execution_approval":
        return (
            "A non-CPU torch accelerator is available. A single non-final identity "
            "proof still requires creator approval before execution."
        )
    reason = torch_probe.get("unavailable_reason") or "unknown accelerator state"
    return (
        "Local compute is not ready for another identity proof attempt: "
        + ", ".join(failure_codes)
        + f". Torch reason: {reason}."
    )


def _compute_diagnostic_next_step(
    local_compute_ready: bool, torch_probe: dict[str, Any]
) -> str:
    if local_compute_ready:
        return (
            "Request creator approval for exactly one non-final local identity proof "
            "attempt. Keep carousel generation blocked."
        )
    reason = torch_probe.get("unavailable_reason")
    if reason == "MACOS_OR_DEVICE_NOT_MPS_ENABLED":
        return (
            "Do not retry on this CPU path. Use a machine where PyTorch reports "
            "`mps_available: true` or `cuda_available: true`, then run the same "
            "workflow bundle there."
        )
    if reason == "PYTORCH_NOT_BUILT_WITH_MPS":
        return (
            "Install or select a PyTorch build with MPS support only if the machine "
            "is Apple Silicon and macOS/device support exists; otherwise use CUDA/MPS "
            "handoff."
        )
    return (
        "Prepare the run-local workflow/reference/model handoff bundle for a GPU or "
        "MPS-capable machine before trying another proof."
    )


def _final_decision(workflow_status: dict[str, Any]) -> dict[str, Any]:
    if workflow_status["status"] == "ready":
        return {
            "status": "pending_creator_model_execution_approval",
            "failure_codes": [],
            "reason": (
                "Reference image inputs are explicit and a local workflow file exists, "
                "but no model execution has been approved or run."
            ),
            "next_gate": "HITL_LOCAL_MODEL_EXECUTION_APPROVAL",
        }
    return {
        "status": "blocked",
        "failure_codes": workflow_status["failure_codes"],
        "reason": workflow_status["reason"],
        "next_gate": "HITL_LOCAL_MODEL_SETUP_APPROVAL",
    }


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_image_path(path: Path) -> bool:
    return path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}


def _relative_path(path: Path | None, repo_root: Path) -> str | None:
    if path is None:
        return None
    try:
        return str(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return str(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a local identity reference proof for an A Story run."
    )
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument("--run-id", required=True, help="Run id under runs/.")
    parser.add_argument(
        "--workflow-id",
        default="option_b_sdxl_instantid_pulid_ipadapter",
        choices=sorted(LOCAL_WORKFLOW_OPTIONS),
        help="Local workflow stack to record in the proof.",
    )
    parser.add_argument(
        "--workflow-file",
        help="Path to a local workflow JSON, relative to the repo root.",
    )
    parser.add_argument(
        "--reference-delivery-mode",
        default="local_binary_input",
        help="Must remain local_binary_input; prompt_only_paths is refused.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Record proof only; never download models or execute generation.",
    )
    parser.add_argument(
        "--discover-local-stack",
        action="store_true",
        help="Inspect existing local ComfyUI/workflow/model files and write discovery artifacts.",
    )
    parser.add_argument(
        "--execution-readiness",
        action="store_true",
        help="Inspect whether the next non-final local identity proof attempt is allowed.",
    )
    parser.add_argument(
        "--compute-diagnostic",
        action="store_true",
        help="Diagnose local CPU/MPS/CUDA readiness for the next identity proof.",
    )
    parser.add_argument(
        "--handoff-manifest",
        action="store_true",
        help="Write a GPU/MPS handoff manifest for the local identity proof bundle.",
    )
    args = parser.parse_args(argv)

    if not args.dry_run:
        parser.error("Only --dry-run is implemented. Model execution is HITL-gated.")

    if args.handoff_manifest:
        manifest = build_local_identity_handoff_manifest(
            repo_root=Path(args.repo_root),
            run_id=args.run_id,
            workflow_id=args.workflow_id,
            workflow_file=args.workflow_file,
        )
        manifest_path, report_path = write_handoff_artifacts(
            Path(args.repo_root), manifest
        )
        print(f"Wrote {manifest_path}")
        print(f"Wrote {report_path}")
        print(f"Status: {manifest['status']}")
        return 0

    if args.compute_diagnostic:
        diagnostic = build_local_compute_diagnostic(
            repo_root=Path(args.repo_root),
            run_id=args.run_id,
            workflow_id=args.workflow_id,
            workflow_file=args.workflow_file,
        )
        diagnostic_path, report_path = write_compute_diagnostic_artifacts(
            Path(args.repo_root), diagnostic
        )
        print(f"Wrote {diagnostic_path}")
        print(f"Wrote {report_path}")
        print(f"Status: {diagnostic['status']}")
        print(f"Final decision: {diagnostic['final_decision']['status']}")
        return 0

    if args.execution_readiness:
        readiness = build_local_identity_execution_readiness(
            repo_root=Path(args.repo_root),
            run_id=args.run_id,
            workflow_id=args.workflow_id,
            workflow_file=args.workflow_file,
        )
        readiness_path, report_path = write_execution_readiness_artifacts(
            Path(args.repo_root), readiness
        )
        print(f"Wrote {readiness_path}")
        print(f"Wrote {report_path}")
        print(f"Status: {readiness['status']}")
        print(f"Final decision: {readiness['final_decision']['status']}")
        return 0

    if args.discover_local_stack:
        discovery = discover_local_identity_stack(
            repo_root=Path(args.repo_root),
            run_id=args.run_id,
            workflow_id=args.workflow_id,
            workflow_file=args.workflow_file,
        )
        discovery_path, report_path = write_discovery_artifacts(
            Path(args.repo_root), discovery
        )
        print(f"Wrote {discovery_path}")
        print(f"Wrote {report_path}")
        print(f"Status: {discovery['status']}")
        print(f"Final decision: {discovery['final_decision']['status']}")
        return 0

    try:
        proof = build_local_identity_reference_proof(
            repo_root=Path(args.repo_root),
            run_id=args.run_id,
            workflow_id=args.workflow_id,
            workflow_file=args.workflow_file,
            reference_delivery_mode=args.reference_delivery_mode,
        )
    except (PromptOnlyReferenceError, ReferenceSelectionError) as exc:
        parser.exit(2, f"ERROR: {exc}\n")

    proof_path, report_path = write_proof_artifacts(Path(args.repo_root), proof)
    print(f"Wrote {proof_path}")
    print(f"Wrote {report_path}")
    print(f"Status: {proof['status']}")
    print(f"Final decision: {proof['final_decision']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
