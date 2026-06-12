"""Artifact-presence gates.

The spine declares what each state `produces` (run-relative paths). A gate
check answers: do those files actually exist for this run? Phase 2 enforces
presence only; content-level checks arrive with the legs that produce richer
artifacts. Pure functions — no RunState mutation, no model calls.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.astory_orchestrator import spine


def missing_artifacts(repo_root: str | Path, run_id: str, state_name: str) -> list[str]:
    """Return the state's declared produces paths that do not exist on disk."""

    spec = spine.by_name(state_name)
    run_dir = Path(repo_root).resolve() / "runs" / run_id
    return [rel for rel in spec.produces if not (run_dir / rel).exists()]


def check_gate(repo_root: str | Path, run_id: str, state_name: str) -> dict[str, Any]:
    """Check a state's artifact gate; `ok` is False only when artifacts are missing."""

    spec = spine.by_name(state_name)
    missing = missing_artifacts(repo_root, run_id, state_name)
    return {
        "state": spec.name,
        "is_gate": spec.kind == "gate",
        "ok": not missing,
        "missing": missing,
    }
