from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

from .models import BrainSource


TEXT_SUFFIXES = {".md", ".json", ".jsonl", ".txt"}
EXCLUDED_PARTS = {
    ".git",
    ".DS_Store",
    "__pycache__",
    "images",
    "exports",
    "node_modules",
}
DERIVED_PREFIXES = ("references/brain/index/", "references/brain/reports/")


def scan_sources(repo_root: str | Path, include_runs: list[str]) -> list[BrainSource]:
    root = Path(repo_root).resolve()
    candidates: list[Path] = []
    for rel_root in ("references", ".agents/skills/astory/references"):
        base = root / rel_root
        if base.exists():
            candidates.extend(_iter_text_files(base))

    for run_id in include_runs:
        run_dir = root / "runs" / run_id
        if run_dir.exists():
            for rel in (
                "docs",
                "prompts",
                "evals",
                "planning",
                "logs",
                "references-used",
                "memory",
            ):
                base = run_dir / rel
                if base.exists():
                    candidates.extend(_iter_text_files(base))

    sources: list[BrainSource] = []
    for path in sorted(set(candidates), key=lambda item: item.resolve().relative_to(root).as_posix()):
        rel_path = path.resolve().relative_to(root).as_posix()
        if rel_path.startswith(DERIVED_PREFIXES):
            continue
        sources.append(
            BrainSource(
                source_id=f"source:{_stable_id(rel_path)}",
                path=rel_path,
                kind=_kind_for_path(rel_path),
                scope=_scope_for_path(rel_path),
                run_id=_run_id_for_path(rel_path),
                role=_role_for_path(rel_path),
                sha256=_sha256_file(path),
                modified_at=_mtime_iso(path),
            )
        )
    return sources


def _iter_text_files(base: Path) -> list[Path]:
    paths: list[Path] = []
    for path in base.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        if path.suffix.lower() in TEXT_SUFFIXES:
            paths.append(path)
    return paths


def _kind_for_path(path: str):
    if path.endswith("/docs/approvals.md"):
        return "approval"
    if "/prompts/" in path and path.endswith(".txt"):
        return "prompt"
    if "/evals/" in path:
        return "eval"
    if path.endswith("/docs/retro.md"):
        return "retro"
    if path.endswith("/logs/trace.jsonl"):
        return "trace"
    if path.startswith("references/brain/pages/"):
        return "compiled_page"
    if path.startswith(".agents/skills/astory/references/"):
        return "skill_reference"
    if path.startswith("references/"):
        return "reference"
    return "reference"


def _scope_for_path(path: str) -> str:
    if path.startswith("runs/"):
        return "run"
    if path.startswith(".agents/"):
        return "skill"
    return "reference"


def _run_id_for_path(path: str) -> str | None:
    parts = path.split("/")
    if len(parts) >= 2 and parts[0] == "runs":
        return parts[1]
    return None


def _role_for_path(path: str) -> str | None:
    parts = path.split("/")
    role_markers = {
        "aachu": "aachu",
        "zuv": "zuv",
        "together": "together",
        "style": "style",
        "wardrobe": "wardrobe",
        "places": "place",
        "brand": "brand",
        "text-style": "text",
    }
    for part in parts:
        if part in role_markers:
            return role_markers[part]
    return None


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _stable_id(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:16]


def _mtime_iso(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()
