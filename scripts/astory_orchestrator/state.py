"""Per-run orchestrator state.

`RunState` is the single source of truth for "where is this run" — current
state, completed states, gate results, retry counters, HITL decisions, and
artifact status. Phase 0 only builds and persists it; later phases let a runner
advance it. Persisted to `runs/<run_id>/state/run_state.json` (a new additive
file; no existing run artifact is touched).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from scripts.astory_orchestrator.spine import first_state, is_state

RunStatus = Literal["running", "awaiting_hitl", "blocked", "complete"]

SCHEMA_VERSION = "1.0"
_VALID_STATUS: set[str] = {"running", "awaiting_hitl", "blocked", "complete"}


@dataclass
class RunState:
    run_id: str
    current_state: str
    status: RunStatus = "running"
    schema_version: str = SCHEMA_VERSION
    completed: list[str] = field(default_factory=list)
    gates: dict[str, str] = field(default_factory=dict)
    retries: dict[str, int] = field(default_factory=dict)
    hitl: dict[str, str] = field(default_factory=dict)
    artifacts: dict[str, str] = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def new_run_state(run_id: str) -> RunState:
    now = _utc_now_iso()
    return RunState(
        run_id=run_id,
        current_state=first_state(),
        status="running",
        created_at=now,
        updated_at=now,
    )


def to_dict(state: RunState) -> dict[str, Any]:
    return {
        "schema_version": state.schema_version,
        "run_id": state.run_id,
        "current_state": state.current_state,
        "status": state.status,
        "completed": list(state.completed),
        "gates": dict(state.gates),
        "retries": dict(state.retries),
        "hitl": dict(state.hitl),
        "artifacts": dict(state.artifacts),
        "created_at": state.created_at,
        "updated_at": state.updated_at,
    }


def from_dict(data: dict[str, Any]) -> RunState:
    run_id = data.get("run_id")
    if not run_id:
        raise ValueError("run_state missing run_id")

    current_state = data.get("current_state")
    if not isinstance(current_state, str) or not is_state(current_state):
        raise ValueError(f"unknown current_state: {current_state!r}")

    status = data.get("status", "running")
    if status not in _VALID_STATUS:
        raise ValueError(f"invalid run_state status: {status!r}")

    return RunState(
        run_id=run_id,
        current_state=current_state,
        status=status,
        schema_version=data.get("schema_version", SCHEMA_VERSION),
        completed=list(data.get("completed", [])),
        gates=dict(data.get("gates", {})),
        retries=dict(data.get("retries", {})),
        hitl=dict(data.get("hitl", {})),
        artifacts=dict(data.get("artifacts", {})),
        created_at=data.get("created_at", ""),
        updated_at=data.get("updated_at", ""),
    )


def state_path(repo_root: str | Path, run_id: str) -> Path:
    return Path(repo_root).resolve() / "runs" / run_id / "state" / "run_state.json"


def save_state(repo_root: str | Path, run_id: str, state: RunState) -> Path:
    state.updated_at = _utc_now_iso()
    path = state_path(repo_root, run_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(to_dict(state), indent=2, sort_keys=True) + "\n")
    return path


def load_state(repo_root: str | Path, run_id: str) -> RunState | None:
    path = state_path(repo_root, run_id)
    if not path.exists():
        return None
    return from_dict(json.loads(path.read_text()))
