from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_MEMORY_AUTOPILOT_POLICY = {
    "auto_promote_auto_apply": True,
    "auto_defer_high_risk": True,
    "auto_quarantine_rejected_assets": True,
}


def load_memory_autopilot_policy(repo_root: str | Path) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    policy = dict(DEFAULT_MEMORY_AUTOPILOT_POLICY)
    path = root / "references/brain/policies/memory_autopilot.json"
    if not path.exists():
        return policy
    try:
        override = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return policy
    if not isinstance(override, dict):
        return policy
    for key, value in override.items():
        if key in policy and isinstance(value, type(policy[key])):
            policy[key] = value
    return policy
