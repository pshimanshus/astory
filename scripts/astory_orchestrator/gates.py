"""Artifact-presence checks.

The spine declares what each state `produces` (run-relative paths). This module
answers one question: which of those files do not exist for a run? Content-level
validation lives in the runner's verifier registry. Pure functions — no RunState
mutation, no model calls.
"""

from __future__ import annotations

from pathlib import Path

from scripts.astory_orchestrator import spine


def missing_artifacts(repo_root: str | Path, run_id: str, state_name: str) -> list[str]:
    """Return the state's declared produces paths that do not exist on disk."""

    spec = spine.by_name(state_name)
    run_dir = Path(repo_root).resolve() / "runs" / run_id
    return [rel for rel in spec.produces if not (run_dir / rel).exists()]
