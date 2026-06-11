#!/usr/bin/env python3
"""Prepare per-run local image reference manifests for A Story imagegen."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageOps


DOSSIER_PATH = Path("references/identity/_dossier/identity-dossier.json")
PREFLIGHT_PATH = Path("references/identity/_dossier/identity-generation-preflight.md")
DEFAULT_STYLE_REFERENCES = [
    "references/style/observational-intimacy-premium/contact-sheet.png",
    "references/style/observational-intimacy-premium/slide-01.png",
    "references/style/observational-intimacy-premium/slide-02.png",
]
TEXT_AND_BRAND_REFERENCES = [
    "references/text-style/README.md",
    "references/brand/README.md",
    ".agents/skills/astory/references/house-style-contract.md",
    ".agents/skills/astory/references/imagegen-contract.md",
]
MIN_FACE_ANCHORS_PER_SUBJECT = 4


class ReferenceContextError(ValueError):
    """Raised when imagegen references cannot be prepared safely."""


def build_reference_context(repo_root: Path | str, run_id: str) -> dict[str, Any]:
    """Build a deterministic local-reference manifest and view_image queue."""

    repo_root = Path(repo_root).resolve()
    run_root = repo_root / "runs" / run_id
    if not run_root.exists():
        raise ReferenceContextError(f"Run folder does not exist: runs/{run_id}")

    dossier_path = repo_root / DOSSIER_PATH
    dossier = _read_json(dossier_path)
    imported_by_path = {
        reference["path"]: reference for reference in dossier.get("imported_references", [])
    }
    deprecated_paths = {
        reference["path"]
        for reference in dossier.get("deprecated_duplicate_role_overlaps", [])
    }
    recipe = dossier.get("selected_generation_recipe", {}).get(
        "face_visible_default", {}
    )

    aachu_face = recipe.get("default_aachu_close_face_anchors", [])
    zuv_face = recipe.get("default_zuv_close_face_anchors", [])
    together = recipe.get("together_support", [])[:2]
    expression = [
        path
        for path in recipe.get("expression_support", [])
        if path in imported_by_path
    ][:4]
    current_request = _run_input_images(repo_root, run_root)
    style = _style_references(repo_root, run_root)

    _require_count("Aachu default face anchors", aachu_face, MIN_FACE_ANCHORS_PER_SUBJECT)
    _require_count("Zuv default face anchors", zuv_face, MIN_FACE_ANCHORS_PER_SUBJECT)

    grouped_paths = {
        "current_request": current_request,
        "aachu_face_identity": aachu_face,
        "zuv_face_identity": zuv_face,
        "expression_support": expression,
        "together_body_language": together,
        "style": style,
    }
    groups = {
        role: [
            _build_reference_record(
                repo_root=repo_root,
                rel_path=path,
                role=role,
                dossier_record=imported_by_path.get(path),
                deprecated_paths=deprecated_paths,
            )
            for path in paths
        ]
        for role, paths in grouped_paths.items()
    }

    text_and_brand = [
        _build_text_reference_record(repo_root, path)
        for path in TEXT_AND_BRAND_REFERENCES
    ]
    view_image_queue = [
        reference["path"]
        for role in (
            "current_request",
            "aachu_face_identity",
            "zuv_face_identity",
            "expression_support",
            "together_body_language",
            "style",
        )
        for reference in groups[role]
    ]

    now = datetime.now().astimezone().isoformat(timespec="seconds")
    return {
        "schema_version": "1.0",
        "run_id": run_id,
        "created_at": now,
        "status": "ready_to_load_with_view_image",
        "source_dossier": str(DOSSIER_PATH),
        "source_preflight": str(PREFLIGHT_PATH),
        "manual_user_attachments_required": False,
        "prompt_only_allowed": False,
        "required_before_imagegen": [
            "Codex must call view_image for every path in view_image_queue in the current conversation before final imagegen.",
            "If any queued image cannot be read, stop and mark IDENTITY_REFERENCE_MISSING.",
            "If the active generation path cannot use the loaded image context, stop instead of generating final Aachu/Zuv artwork.",
        ],
        "reference_groups": groups,
        "text_and_brand_references": text_and_brand,
        "view_image_queue": view_image_queue,
        "view_image_queue_count": len(view_image_queue),
        "load_state": {
            "loaded_in_current_conversation": False,
            "proof_required": True,
            "proof_artifact": f"runs/{run_id}/evals/imagegen_reference_visibility_proof.json",
        },
    }


def write_reference_context(repo_root: Path | str, context: dict[str, Any]) -> tuple[Path, Path, Path]:
    """Write selected reference JSON plus imagegen load-plan artifacts."""

    repo_root = Path(repo_root).resolve()
    run_root = repo_root / "runs" / context["run_id"]
    references_dir = run_root / "references-used"
    evals_dir = run_root / "evals"
    references_dir.mkdir(parents=True, exist_ok=True)
    evals_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = references_dir / "selected_references.json"
    load_plan_path = evals_dir / "imagegen_reference_load_plan.json"
    report_path = evals_dir / "imagegen_reference_load_plan.md"

    manifest_path.write_text(json.dumps(context, indent=2) + "\n", encoding="utf-8")
    load_plan_path.write_text(json.dumps(context, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(_render_report(context), encoding="utf-8")
    return manifest_path, load_plan_path, report_path


def _build_reference_record(
    repo_root: Path,
    rel_path: str,
    role: str,
    dossier_record: dict[str, Any] | None,
    deprecated_paths: set[str],
) -> dict[str, Any]:
    if rel_path in deprecated_paths:
        raise ReferenceContextError(
            f"Deprecated duplicate role alias cannot be queued for imagegen: {rel_path}"
        )

    path = repo_root / rel_path
    if not path.exists():
        raise ReferenceContextError(f"Missing image reference: {rel_path}")
    if path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise ReferenceContextError(f"Queued reference is not an image: {rel_path}")

    width, height = _image_size(path)
    expected_sha = dossier_record.get("sha256") if dossier_record else None
    digest = _sha256_file(path)
    if expected_sha and expected_sha != digest:
        raise ReferenceContextError(f"SHA-256 mismatch for reference: {rel_path}")

    return {
        "path": rel_path,
        "absolute_path": str(path.resolve()),
        "role": role,
        "subject": dossier_record.get("subject") if dossier_record else role,
        "dossier_role": dossier_record.get("role") if dossier_record else None,
        "quality": dossier_record.get("quality") if dossier_record else "style",
        "delivery_mode": "view_image_before_imagegen",
        "input_kind": "local_image_file",
        "width": width,
        "height": height,
        "size_bytes": path.stat().st_size,
        "sha256": digest,
        "do_not_use_for": dossier_record.get("do_not_use_for", []) if dossier_record else [],
    }


def _build_text_reference_record(repo_root: Path, rel_path: str) -> dict[str, Any]:
    path = repo_root / rel_path
    if not path.exists():
        raise ReferenceContextError(f"Missing text/brand reference: {rel_path}")
    return {
        "path": rel_path,
        "absolute_path": str(path.resolve()),
        "role": "text_or_brand_rule",
        "input_kind": "local_text_file",
        "size_bytes": path.stat().st_size,
        "sha256": _sha256_file(path),
    }


def _run_input_images(repo_root: Path, run_root: Path) -> list[str]:
    input_dir = run_root / "input"
    if not input_dir.exists():
        return []
    image_suffixes = {".jpg", ".jpeg", ".png", ".webp"}
    return [
        path.resolve().relative_to(repo_root).as_posix()
        for path in sorted(input_dir.iterdir())
        if path.is_file() and path.suffix.lower() in image_suffixes
    ]


def _style_references(repo_root: Path, run_root: Path) -> list[str]:
    selected_refs_path = run_root / "references-used/selected_references.json"
    if selected_refs_path.exists():
        selected_refs = json.loads(selected_refs_path.read_text(encoding="utf-8"))
        groups = (
            selected_refs.get("reference_groups")
            if isinstance(selected_refs, dict)
            else None
        )
        if isinstance(groups, dict):
            style_paths = [
                ref.get("path")
                for ref in groups.get("style", [])
                if isinstance(ref, dict) and ref.get("path")
            ]
            existing = [path for path in style_paths if (repo_root / path).exists()]
            if existing:
                return existing

    return [path for path in DEFAULT_STYLE_REFERENCES if (repo_root / path).exists()]


def _render_report(context: dict[str, Any]) -> str:
    queue_lines = "\n".join(
        f"- `{path}`" for path in context["view_image_queue"]
    )
    return f"""# Imagegen Reference Load Plan

Run: `{context['run_id']}`

Status: `{context['status']}`

Manual user attachments required: `{context['manual_user_attachments_required']}`
Prompt-only allowed: `{context['prompt_only_allowed']}`

## Required Before Imagegen

Codex must load every path below with `view_image` in the current conversation
before any final Aachu/Zuv illustration is generated. If any image cannot be
read, or if the active generation path cannot use loaded image context, mark
the run blocked instead of generating final artwork.

## view_image Queue

{queue_lines}
"""


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ReferenceContextError(f"Missing JSON file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _require_count(label: str, paths: list[str], minimum: int) -> None:
    if len(paths) < minimum:
        raise ReferenceContextError(
            f"{label} must include at least {minimum} images; found {len(paths)}."
        )


def _image_size(path: Path) -> tuple[int, int]:
    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image)
        return image.size


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the per-run local image reference load plan for imagegen."
    )
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument("--run-id", required=True, help="Run id under runs/.")
    args = parser.parse_args(argv)

    context = build_reference_context(Path(args.repo_root), args.run_id)
    manifest_path, load_plan_path, report_path = write_reference_context(
        Path(args.repo_root), context
    )
    print(f"Wrote {manifest_path}")
    print(f"Wrote {load_plan_path}")
    print(f"Wrote {report_path}")
    print(f"view_image_queue_count {context['view_image_queue_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
