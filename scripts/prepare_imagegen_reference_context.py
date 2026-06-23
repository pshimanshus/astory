#!/usr/bin/env python3
"""Prepare per-run local image reference manifests for A Story imagegen."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageOps


IDENTITY_ROOT = Path("references/identity")
STYLE_ROOT = Path("references/style/best-illustration")
FAILURES_ROOT = Path("references/failures/visual-inconsistencies")
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
TEXT_AND_BRAND_REFERENCES = [
    "references/text-style/README.md",
    "references/brand/README.md",
    ".agents/skills/astory/references/house-style-contract.md",
    ".agents/skills/astory/references/imagegen-contract.md",
]
MIN_FACE_ANCHORS_PER_SUBJECT = 4
ACTIVE_FACE_ANCHORS_PER_SUBJECT = 6
MIN_FACE_VIEW_BUCKETS_PER_SUBJECT = 2
MAX_EXPRESSION_SUPPORT = 4
MAX_TOGETHER_SUPPORT = 2
MAX_STYLE_REFERENCES = 3
BINDER_DIRNAME = "reference-binder"
BINDER_IMAGE_SIZE = (1200, 900)
BINDER_THUMBNAIL_SIZE = (260, 260)
BINDER_BG = (248, 248, 246)
BINDER_PANEL_BG = (255, 255, 255)
BINDER_INK = (38, 35, 31)
BINDER_MUTABLE_PACKET_FIELDS = {
    "absolute_path",
    "width",
    "height",
    "size_bytes",
    "sha256",
}
BINDER_SPECS = [
    {
        "role": "aachu_identity_binder",
        "filename": "aachu-identity-binder.png",
        "title": "Aachu face identity only",
        "source_roles": ["aachu_face_identity"],
        "instruction": "Use only for Aachu's face identity. Do not copy clothing, background, or lighting.",
        "required_for": ["face_visible_generation", "identity_preservation"],
    },
    {
        "role": "zuv_identity_binder",
        "filename": "zuv-identity-binder.png",
        "title": "Zuv face identity only",
        "source_roles": ["zuv_face_identity"],
        "instruction": "Use only for Zuv's face identity. Do not copy clothing, background, or lighting.",
        "required_for": ["face_visible_generation", "identity_preservation"],
    },
    {
        "role": "couple_body_language_binder",
        "filename": "couple-body-language-binder.png",
        "title": "Couple body language",
        "source_roles": ["together_body_language"],
        "instruction": "Use for closeness, posture, height relationship, and couple energy. Do not use as primary face identity.",
        "required_for": ["couple_composition", "relationship_dynamics"],
    },
    {
        "role": "style_binder",
        "filename": "style-binder.png",
        "title": "A Story visual style",
        "source_roles": ["style"],
        "instruction": "Use for watercolor, ink, texture, line quality, and mood only. Do not copy characters.",
        "required_for": ["style_preservation"],
    },
    {
        "role": "current_request_binder",
        "filename": "current-request-binder.png",
        "title": "Current request source intent",
        "source_roles": ["current_request"],
        "instruction": "Use for joke, caption intent, and composition memory only. Do not recreate screenshot UI.",
        "required_for": ["current_request_intent"],
    },
    {
        "role": "expression_support_binder",
        "filename": "expression-support-binder.png",
        "title": "Expression support only",
        "source_roles": ["expression_support"],
        "instruction": "Use for smile/reaction nuance only. Do not use as primary face identity.",
        "required_for": ["expression_support"],
    },
]
FACE_IDENTITY_USE_FOR = [
    "face_identity",
    "identity_structure",
    "feature_consistency",
    "expression_range",
]
FACE_IDENTITY_DO_NOT_USE_FOR = [
    "pose",
    "head_angle",
    "expression_lock",
    "wardrobe",
    "lighting",
    "background",
    "camera_position",
    "scene_composition",
]
SUPPORT_DO_NOT_USE_FOR = ["face_identity", "identity_structure"]
FACE_VIEW_BUCKET_ORDER = ("front", "three_quarter", "side")
FACE_VIEW_KEYWORDS = {
    "side": ("side", "profile"),
    "three_quarter": (
        "three-quarter",
        "three_quarter",
        "threequarter",
        "3q",
        "car-purple",
        "glance",
        "laugh",
        "lavender-smile",
    ),
    "front": ("front", "frontal", "neutral", "selfie", "cafe-neutral", "home-black"),
}
FACE_EXPRESSION_KEYWORDS = {
    "laugh": ("laugh", "laughing"),
    "smile": ("smile", "smiling"),
    "pout": ("pout",),
    "glance": ("glance", "side-eye", "side_eye"),
    "neutral": ("neutral", "front", "frontal"),
}
REFERENCE_POLICY_FIELDS = (
    "blocked_active_refs",
    "analysis_only_refs",
    "emotion_forbidden_refs",
)
SCENE_COLLISION_TERMS = {
    "cafe": ("cafe", "coffee", "cup", "friends table", "public table"),
    "club": ("club", "dance floor", "bar"),
    "party": ("party", "birthday", "gathering"),
}


class ReferenceContextError(ValueError):
    """Raised when imagegen references cannot be prepared safely."""


def build_reference_context(repo_root: Path | str, run_id: str) -> dict[str, Any]:
    """Build a deterministic local-reference manifest and view_image queue."""

    repo_root = Path(repo_root).resolve()
    run_root = repo_root / "runs" / run_id
    if not run_root.exists():
        raise ReferenceContextError(f"Run folder does not exist: runs/{run_id}")

    aachu_all = _classify_identity_images(repo_root, "aachu")
    zuv_all = _classify_identity_images(repo_root, "zuv")
    reference_policy = _load_reference_policy(run_root)
    prompt_text = _combined_prompt_text(run_root)

    _require_count("Aachu face anchors", aachu_all["face"], MIN_FACE_ANCHORS_PER_SUBJECT)
    _require_count("Zuv face anchors", zuv_all["face"], MIN_FACE_ANCHORS_PER_SUBJECT)

    aachu_exclusions = _active_face_exclusion_reasons(
        aachu_all["face"], reference_policy, prompt_text
    )
    zuv_exclusions = _active_face_exclusion_reasons(
        zuv_all["face"], reference_policy, prompt_text
    )
    aachu_active_candidates = _active_face_candidates(aachu_all["face"], aachu_exclusions)
    zuv_active_candidates = _active_face_candidates(zuv_all["face"], zuv_exclusions)
    _require_count(
        "Aachu active face anchors after reference policy",
        aachu_active_candidates,
        MIN_FACE_ANCHORS_PER_SUBJECT,
    )
    _require_count(
        "Zuv active face anchors after reference policy",
        zuv_active_candidates,
        MIN_FACE_ANCHORS_PER_SUBJECT,
    )

    aachu_face = _select_face_identity_anchors(
        repo_root, aachu_active_candidates, ACTIVE_FACE_ANCHORS_PER_SUBJECT
    )
    zuv_face = _select_face_identity_anchors(
        repo_root, zuv_active_candidates, ACTIVE_FACE_ANCHORS_PER_SUBJECT
    )
    expression = (aachu_all["expression"] + zuv_all["expression"])[:MAX_EXPRESSION_SUPPORT]
    together = _discover_images(repo_root, IDENTITY_ROOT / "together")[:MAX_TOGETHER_SUPPORT]
    current_request = _run_input_images(repo_root, run_root)
    style = _style_references(repo_root, run_root)

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
            )
            for path in paths
        ]
        for role, paths in grouped_paths.items()
    }

    text_and_brand = [
        _build_text_reference_record(repo_root, path)
        for path in TEXT_AND_BRAND_REFERENCES
    ]
    raw_reference_queue = [
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
    generation_reference_packet_queue = _build_generation_reference_packet_queue(
        repo_root=repo_root,
        run_id=run_id,
        groups=groups,
    )
    active_view_image_queue = _build_active_view_image_queue(groups)

    now = datetime.now().astimezone().isoformat(timespec="seconds")
    context = {
        "schema_version": "1.0",
        "run_id": run_id,
        "created_at": now,
        "status": "ready_to_load_with_view_image",
        "reference_delivery_strategy": "raw_identity_first_v1",
        "source_identity_root": str(IDENTITY_ROOT),
        "source_style_root": str(STYLE_ROOT),
        "manual_user_attachments_required": False,
        "prompt_only_allowed": False,
        "required_before_imagegen": [
            "Codex must call view_image for every path in view_image_queue in the current conversation before final imagegen.",
            "If any queued image cannot be read, stop and mark IDENTITY_REFERENCE_MISSING.",
            "If the active generation path cannot use the loaded image context, stop instead of generating final Aachu/Zuv artwork.",
        ],
        "reference_groups": groups,
        "identity_reference_usage_contract": _identity_reference_usage_contract(),
        "identity_reference_summary": _identity_reference_summary(groups),
        "reference_policy_summary": _reference_policy_summary(
            reference_policy,
            {
                **aachu_exclusions,
                **zuv_exclusions,
            },
        ),
        "text_and_brand_references": text_and_brand,
        "raw_reference_queue": raw_reference_queue,
        "raw_reference_queue_count": len(raw_reference_queue),
        "generation_reference_packet_queue": generation_reference_packet_queue,
        "generation_reference_packet_queue_count": len(
            generation_reference_packet_queue
        ),
        "active_view_image_queue": active_view_image_queue,
        "view_image_queue": active_view_image_queue,
        "view_image_queue_count": len(active_view_image_queue),
        "load_state": {
            "loaded_in_current_conversation": False,
            "proof_required": True,
            "proof_artifact": f"runs/{run_id}/evals/imagegen_reference_visibility_proof.json",
        },
    }
    context["load_plan_sha256"] = _load_plan_sha256(context)
    return context


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

    _write_reference_binders(repo_root, context)
    context["view_image_queue"] = list(context["active_view_image_queue"])
    context["view_image_queue_count"] = len(context["view_image_queue"])
    context["generation_reference_packet_queue_count"] = len(
        context["generation_reference_packet_queue"]
    )
    context["load_plan_sha256"] = _load_plan_sha256(context)

    manifest_path.write_text(json.dumps(context, indent=2) + "\n", encoding="utf-8")
    load_plan_path.write_text(json.dumps(context, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(_render_report(context), encoding="utf-8")
    return manifest_path, load_plan_path, report_path


def _build_active_view_image_queue(groups: dict[str, list[dict[str, Any]]]) -> list[str]:
    # Current-request screenshots often contain non-Aachu/Zuv faces and strong
    # poses. Keep them in the manifest/binders for analysis, but do not feed
    # them as active imagegen inputs for identity-sensitive final artwork.
    active_roles = (
        "aachu_face_identity",
        "zuv_face_identity",
        "style",
    )
    return [
        reference["path"]
        for role in active_roles
        for reference in groups.get(role, [])
    ]


def _build_generation_reference_packet_queue(
    repo_root: Path,
    run_id: str,
    groups: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    packets: list[dict[str, Any]] = []
    binder_dir = Path("runs") / run_id / "references-used" / BINDER_DIRNAME
    for spec in BINDER_SPECS:
        sources = [
            reference
            for role in spec["source_roles"]
            for reference in groups.get(role, [])
        ]
        if not sources:
            continue
        rel_path = (binder_dir / spec["filename"]).as_posix()
        packets.append(
            {
                "path": rel_path,
                "absolute_path": str((repo_root / rel_path).resolve()),
                "role": spec["role"],
                "title": spec["title"],
                "instruction": spec["instruction"],
                "source_roles": list(spec["source_roles"]),
                "source_paths": [source["path"] for source in sources],
                "source_sha256": [source["sha256"] for source in sources],
                "required_for": list(spec["required_for"]),
                "delivery_mode": "view_image_before_imagegen",
                "input_kind": "generated_reference_binder",
                "width": 0,
                "height": 0,
                "size_bytes": 0,
                "sha256": "",
            }
        )
    return packets


def _write_reference_binders(repo_root: Path, context: dict[str, Any]) -> None:
    packets = context.get("generation_reference_packet_queue") or []
    if not packets:
        raise ReferenceContextError("No generation reference binder packets were prepared.")

    by_path = {
        reference["path"]: reference
        for group in (context.get("reference_groups") or {}).values()
        for reference in group
        if isinstance(reference, dict) and reference.get("path")
    }
    for packet in packets:
        output_path = repo_root / packet["path"]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        sources = [
            by_path[path]
            for path in packet.get("source_paths", [])
            if path in by_path
        ]
        if not sources:
            raise ReferenceContextError(
                f"Binder packet has no source images: {packet['role']}"
            )
        image = _render_binder_image(repo_root, packet, sources)
        image.save(output_path)
        width, height = _image_size(output_path)
        packet["absolute_path"] = str(output_path.resolve())
        packet["width"] = width
        packet["height"] = height
        packet["size_bytes"] = output_path.stat().st_size
        packet["sha256"] = _sha256_file(output_path)


def _render_binder_image(
    repo_root: Path, packet: dict[str, Any], sources: list[dict[str, Any]]
) -> Image.Image:
    canvas = Image.new("RGB", BINDER_IMAGE_SIZE, BINDER_BG)
    draw = ImageDraw.Draw(canvas)
    draw.text((36, 28), packet["title"], fill=BINDER_INK)
    draw.text((36, 56), f"Role: {packet['role']}", fill=BINDER_INK)
    draw.text((36, 84), packet["instruction"], fill=BINDER_INK)

    start_y = 140
    margin_x = 36
    gap_x = 26
    gap_y = 28
    panel_w = 260
    panel_h = 330
    columns = 4
    for index, source in enumerate(sources[:8]):
        col = index % columns
        row = index // columns
        x = margin_x + col * (panel_w + gap_x)
        y = start_y + row * (panel_h + gap_y)
        draw.rectangle(
            (x, y, x + panel_w, y + panel_h),
            fill=BINDER_PANEL_BG,
            outline=(214, 207, 195),
        )
        thumb = _open_thumbnail(repo_root / source["path"])
        tx = x + (panel_w - thumb.width) // 2
        ty = y + 14
        canvas.paste(thumb, (tx, ty))
        label = f"{index + 1}. {source.get('subject') or source['role']} | {source['role']}"
        draw.text((x + 12, y + 286), label[:42], fill=BINDER_INK)
        draw.text((x + 12, y + 306), source["path"][-42:], fill=(88, 81, 72))

    return canvas


def _open_thumbnail(path: Path) -> Image.Image:
    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        image.thumbnail(BINDER_THUMBNAIL_SIZE)
        thumb = Image.new("RGB", BINDER_THUMBNAIL_SIZE, (248, 248, 246))
        x = (BINDER_THUMBNAIL_SIZE[0] - image.width) // 2
        y = (BINDER_THUMBNAIL_SIZE[1] - image.height) // 2
        thumb.paste(image, (x, y))
        return thumb


def _load_plan_sha256(context: dict[str, Any]) -> str:
    payload = {
        "schema_version": context.get("schema_version"),
        "run_id": context.get("run_id"),
        "reference_delivery_strategy": context.get("reference_delivery_strategy"),
        "identity_reference_summary": context.get("identity_reference_summary"),
        "reference_policy_summary": context.get("reference_policy_summary"),
        "raw_reference_queue": context.get("raw_reference_queue"),
        "generation_reference_packet_queue": [
            {
                key: value
                for key, value in packet.items()
                if key not in BINDER_MUTABLE_PACKET_FIELDS
            }
            for packet in context.get("generation_reference_packet_queue", [])
        ],
        "active_view_image_queue": context.get("active_view_image_queue"),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    return hashlib.sha256(encoded).hexdigest()


ROLE_QUALITY = {
    "current_request": "current_request",
    "aachu_face_identity": "identity",
    "zuv_face_identity": "identity",
    "expression_support": "support",
    "together_body_language": "support",
    "style": "style",
}


def _identity_reference_usage_contract() -> dict[str, Any]:
    return {
        "mode": "identity_structure_not_pose_template",
        "raw_face_anchors_use_for": FACE_IDENTITY_USE_FOR,
        "raw_face_anchors_do_not_use_for": FACE_IDENTITY_DO_NOT_USE_FOR,
        "rule": (
            "Use multiple raw face anchors to synthesize stable likeness. Do not "
            "copy one reference photo's pose, head angle, eye state, expression, "
            "wardrobe, lighting, background, camera position, or scene composition."
        ),
        "min_face_view_buckets_per_subject": MIN_FACE_VIEW_BUCKETS_PER_SUBJECT,
    }


def _identity_reference_summary(groups: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for subject, group_name in [
        ("aachu", "aachu_face_identity"),
        ("zuv", "zuv_face_identity"),
    ]:
        records = groups.get(group_name, [])
        buckets = sorted({reference.get("view_bucket", "unknown") for reference in records})
        informative = [bucket for bucket in buckets if bucket != "unknown"]
        summary[subject] = {
            "face_anchor_count": len(records),
            "view_buckets": buckets,
            "view_bucket_count": len(informative or buckets),
            "expression_buckets": sorted(
                {
                    reference.get("expression_bucket", "unknown")
                    for reference in records
                }
            ),
        }
    return summary


def _subject_for(role: str, rel_path: str) -> str:
    if role in ("aachu_face_identity",):
        return "aachu"
    if role in ("zuv_face_identity",):
        return "zuv"
    if role == "together_body_language":
        return "couple"
    if role == "style":
        return "style"
    if role == "current_request":
        return "current_request"
    # expression_support spans both subjects; derive from the folder.
    if "/identity/aachu/" in rel_path:
        return "aachu"
    if "/identity/zuv/" in rel_path:
        return "zuv"
    return role


def _build_reference_record(
    repo_root: Path,
    rel_path: str,
    role: str,
) -> dict[str, Any]:
    path = repo_root / rel_path
    if not path.exists():
        raise ReferenceContextError(f"Missing image reference: {rel_path}")
    if path.suffix.lower() not in IMAGE_SUFFIXES:
        raise ReferenceContextError(f"Queued reference is not an image: {rel_path}")

    width, height = _image_size(path)
    digest = _sha256_file(path)

    record = {
        "path": rel_path,
        "absolute_path": str(path.resolve()),
        "role": role,
        "subject": _subject_for(role, rel_path),
        "quality": ROLE_QUALITY.get(role, "support"),
        "delivery_mode": "view_image_before_imagegen",
        "input_kind": "local_image_file",
        "width": width,
        "height": height,
        "size_bytes": path.stat().st_size,
        "sha256": digest,
        "use_for": [],
        "do_not_use_for": [],
    }
    if role in {"aachu_face_identity", "zuv_face_identity"}:
        record.update(
            {
                "use_for": list(FACE_IDENTITY_USE_FOR),
                "do_not_use_for": list(FACE_IDENTITY_DO_NOT_USE_FOR),
                "view_bucket": _face_view_bucket(rel_path),
                "expression_bucket": _face_expression_bucket(rel_path),
                "usage_contract": _identity_reference_usage_contract(),
            }
        )
    elif role in {"expression_support", "together_body_language", "current_request"}:
        record["do_not_use_for"] = list(SUPPORT_DO_NOT_USE_FOR)
    return record


def _discover_images(repo_root: Path, rel_dir: Path) -> list[str]:
    """Return sorted repo-relative paths of image files directly in rel_dir."""

    directory = repo_root / rel_dir
    if not directory.exists():
        return []
    return [
        (rel_dir / entry.name).as_posix()
        for entry in sorted(directory.iterdir(), key=lambda item: item.name)
        if entry.is_file() and entry.suffix.lower() in IMAGE_SUFFIXES
    ]


def _classify_identity_images(repo_root: Path, subject: str) -> dict[str, list[str]]:
    """Split a subject identity folder into face-identity and expression support.

    Files whose names mention ``face`` or ``portrait`` are face-identity anchors;
    reaction/smile crops are expression support only.
    """

    face: list[str] = []
    expression: list[str] = []
    for rel_path in _discover_images(repo_root, IDENTITY_ROOT / subject):
        stem = Path(rel_path).stem.lower()
        if "face" in stem or "portrait" in stem:
            face.append(rel_path)
        else:
            expression.append(rel_path)
    return {"face": face, "expression": expression}


def _load_reference_policy(run_root: Path) -> dict[str, Any]:
    policy_path = run_root / "references-used/reference_policy.json"
    if not policy_path.exists():
        policy_path = run_root / "input/reference_policy.json"
    if not policy_path.exists():
        return _empty_reference_policy()
    try:
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ReferenceContextError(
            f"Invalid reference policy JSON: {policy_path.relative_to(run_root)}"
        ) from exc
    if not isinstance(policy, dict):
        raise ReferenceContextError("Reference policy must be a JSON object.")

    normalized = _empty_reference_policy()
    for field in REFERENCE_POLICY_FIELDS:
        value = policy.get(field, [])
        if isinstance(value, str):
            value = [value]
        if not isinstance(value, list):
            raise ReferenceContextError(f"Reference policy field must be a list: {field}")
        normalized[field] = [str(item) for item in value if str(item).strip()]
    normalized["reason"] = str(policy.get("reason") or "").strip()
    return normalized


def _empty_reference_policy() -> dict[str, Any]:
    return {
        "blocked_active_refs": [],
        "analysis_only_refs": [],
        "emotion_forbidden_refs": [],
        "reason": "",
    }


def _combined_prompt_text(run_root: Path) -> str:
    prompts_dir = run_root / "prompts"
    if not prompts_dir.exists():
        return ""
    return "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in sorted(prompts_dir.glob("slide_*_prompt.txt"))
        if path.is_file()
    )


def _active_face_exclusion_reasons(
    paths: list[str], policy: dict[str, Any], prompt_text: str
) -> dict[str, list[str]]:
    blocked = set(policy.get("blocked_active_refs") or [])
    analysis_only = set(policy.get("analysis_only_refs") or [])
    emotion_forbidden = set(policy.get("emotion_forbidden_refs") or [])
    prompt_scene_terms = _prompt_scene_terms(prompt_text)
    prompt_forbids_smile = _prompt_forbids_smile(prompt_text)
    exclusions: dict[str, list[str]] = {}

    for path in paths:
        reasons: list[str] = []
        if path in blocked:
            reasons.append("policy_blocked_active_ref")
        if path in analysis_only:
            reasons.append("policy_analysis_only_ref")
        if path in emotion_forbidden:
            reasons.append("policy_emotion_forbidden_ref")
        if prompt_forbids_smile and _face_expression_bucket(path) in {"smile", "laugh"}:
            reasons.append("emotion_forbidden:smile")
        for term in prompt_scene_terms:
            if _path_has_scene_collision(path, term):
                reasons.append(f"scene_overlap:{term}")
        if reasons:
            exclusions[path] = reasons
    return exclusions


def _active_face_candidates(paths: list[str], exclusions: dict[str, list[str]]) -> list[str]:
    return [path for path in paths if path not in exclusions]


def _reference_policy_summary(
    policy: dict[str, Any], exclusions: dict[str, list[str]]
) -> dict[str, Any]:
    analysis_only_refs = {
        *policy.get("analysis_only_refs", []),
        *[
            path
            for path, reasons in exclusions.items()
            if any(reason.startswith("scene_overlap:") for reason in reasons)
        ],
    }
    emotion_forbidden_refs = {
        *policy.get("emotion_forbidden_refs", []),
        *[
            path
            for path, reasons in exclusions.items()
            if any(reason.startswith("emotion_forbidden:") for reason in reasons)
        ],
    }
    return {
        "blocked_active_refs": sorted(set(policy.get("blocked_active_refs", []))),
        "analysis_only_refs": sorted(analysis_only_refs),
        "emotion_forbidden_refs": sorted(emotion_forbidden_refs),
        "reason": policy.get("reason", ""),
        "exclusion_reasons": {
            path: reasons for path, reasons in sorted(exclusions.items())
        },
    }


def _prompt_scene_terms(prompt_text: str) -> list[str]:
    lower = prompt_text.lower()
    return [
        term
        for term, markers in SCENE_COLLISION_TERMS.items()
        if any(marker in lower for marker in markers)
    ]


def _prompt_forbids_smile(prompt_text: str) -> bool:
    lower = prompt_text.lower()
    return any(
        marker in lower
        for marker in (
            "no smile",
            "no smiles",
            "no smirk",
            "unsmiling",
            "not smiling",
            "must not smile",
            "do not smile",
        )
    )


def _path_has_scene_collision(rel_path: str, scene_term: str) -> bool:
    stem = Path(rel_path).stem.lower()
    if "crop" in stem:
        return False
    return scene_term in stem


def _select_face_identity_anchors(repo_root: Path, paths: list[str], limit: int) -> list[str]:
    selected: list[str] = []
    remaining = sorted(paths)
    for bucket in FACE_VIEW_BUCKET_ORDER:
        candidates = [
            path for path in remaining if _face_view_bucket(path) == bucket
        ]
        match = next(
            iter(sorted(candidates, key=lambda path: _face_anchor_sort_key(repo_root, path))),
            None,
        )
        if match:
            selected.append(match)
            remaining.remove(match)
        if len(selected) >= limit:
            return selected
    for path in sorted(remaining, key=lambda item: _face_anchor_sort_key(repo_root, item)):
        selected.append(path)
        if len(selected) >= limit:
            return selected
    return selected


def _face_anchor_sort_key(repo_root: Path, rel_path: str) -> tuple[int, int, str]:
    unknown_view_penalty = 1 if _face_view_bucket(rel_path) == "unknown" else 0
    return (unknown_view_penalty, -_safe_image_area(repo_root / rel_path), rel_path)


def _safe_image_area(path: Path) -> int:
    try:
        width, height = _image_size(path)
    except Exception:
        return 0
    return width * height


def _face_view_bucket(rel_path: str) -> str:
    stem = Path(rel_path).stem.lower()
    for bucket in ("side", "three_quarter", "front"):
        if any(keyword in stem for keyword in FACE_VIEW_KEYWORDS[bucket]):
            return bucket
    return "unknown"


def _face_expression_bucket(rel_path: str) -> str:
    stem = Path(rel_path).stem.lower()
    for bucket, keywords in FACE_EXPRESSION_KEYWORDS.items():
        if any(keyword in stem for keyword in keywords):
            return bucket
    return "unknown"


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
    """Discover style-lock references from the best-illustration folder.

    Loose screenshots are deprioritised in favour of curated illustration files
    so the active view_image queue stays representative of the approved finish.
    """

    discovered = _discover_images(repo_root, STYLE_ROOT)
    if not discovered:
        return []
    curated = [path for path in discovered if not Path(path).name.startswith("Screenshot")]
    ordered = curated or discovered
    return ordered[:MAX_STYLE_REFERENCES]


def _render_report(context: dict[str, Any]) -> str:
    queue_lines = "\n".join(
        f"- `{path}`" for path in context["view_image_queue"]
    )
    binder_lines = "\n".join(
        f"- `{packet['path']}` ({packet['role']})"
        for packet in context.get("generation_reference_packet_queue", [])
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

## Supplemental Binder Packets

These packets are generated for audit/review only. They do not satisfy the final
identity input gate by themselves.

{binder_lines}
"""


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
