"""The idea-room leg controller (copilot mode).

Owns state advancement, the HITL halt, and the bounded idea-room retry loop.
Reads and writes `RunState`; it does NOT call any model. The creative work is
still produced by the agent — the runner only says what the next legal action
is, counts the loop, and records the HITL decision.
"""

from __future__ import annotations

import json
from pathlib import Path

from scripts.astory_orchestrator import gates
from scripts.astory_orchestrator import spine
from scripts.astory_orchestrator import state as run_state_mod
from scripts.astory_orchestrator import validate
from scripts.astory_orchestrator.state import RunState


def _status_for(state_name: str) -> str:
    spec = spine.by_name(state_name)
    if spec.kind == "terminal":
        return "complete"
    if spec.kind == "hitl":
        return "awaiting_hitl"
    return "running"


def advance(repo_root: str | Path, state: RunState) -> RunState:
    """Mark current state complete and move to the spine's next state."""

    nxt = spine.next_state(state.current_state)
    if nxt is None:
        raise ValueError(f"cannot advance past terminal state: {state.current_state}")
    if state.current_state not in state.completed:
        state.completed.append(state.current_state)
    state.current_state = nxt
    state.status = _status_for(nxt)
    run_state_mod.save_state(repo_root, state.run_id, state)
    return state


def next_action(state: RunState) -> dict:
    """Describe the next legal action for the orchestrator/agent."""

    spec = spine.by_name(state.current_state)
    return {
        "state": spec.name,
        "kind": spec.kind,
        "produces": list(spec.produces),
        "halt": spec.kind == "hitl",
    }


def record_hitl(repo_root: str | Path, state: RunState, decision: str) -> RunState:
    """Record a human decision at a HITL state; advance if approved."""

    spec = spine.by_name(state.current_state)
    if spec.kind != "hitl":
        raise ValueError(f"not a HITL state: {state.current_state}")
    if decision not in HITL_DECISIONS:
        raise ValueError(
            f"unknown HITL decision: {decision!r}; expected one of {HITL_DECISIONS}"
        )
    state.hitl[state.current_state] = decision
    if decision in {"approved", "approved_with_revision"}:
        return advance(repo_root, state)
    state.status = "blocked"
    run_state_mod.save_state(repo_root, state.run_id, state)
    return state


IDEA_ROOM_KEY = "idea_room"
MAX_IDEA_ROUNDS = 2
IDEA_ROUND_STATES = (
    "GENERATE_OR_REFINE_IDEAS",
    "SCORE_IDEAS",
    "SELECT_BEST_IDEA",
)
HITL_DECISIONS = (
    "approved",
    "approved_with_revision",
    "rejected",
    "revision_requested",
)


def record_idea_round(repo_root: str | Path, state: RunState, scoreboard: dict) -> dict:
    """Record one idea-room scoring round and decide proceed/rerun/blocked.

    The retry counter lives in RunState.retries[IDEA_ROOM_KEY], so the bound is
    enforced by code across reloads — not remembered by the model.
    """

    if state.current_state not in IDEA_ROUND_STATES:
        raise ValueError(
            f"idea round not allowed at {state.current_state}; "
            f"expected one of {IDEA_ROUND_STATES}"
        )

    # A malformed scoreboard is an operator/artifact error, not a low score.
    # It must not consume a retry, advance, or mutate state — rerunning a
    # broken artifact cannot fix it. Surface it as a distinct outcome.
    problems = validate.validate_final_scoreboard(scoreboard)
    if problems:
        return {
            "decision": "invalid",
            "problems": problems,
            "round": state.retries.get(IDEA_ROOM_KEY, 0),
            "selected_score": None,
            "threshold": validate.threshold(scoreboard),
        }

    round_number = state.retries.get(IDEA_ROOM_KEY, 0) + 1
    state.retries[IDEA_ROOM_KEY] = round_number

    score = validate.selected_score(scoreboard)
    if validate.meets_threshold(scoreboard):
        decision = "proceed"
    elif round_number < MAX_IDEA_ROUNDS:
        decision = "rerun"
    else:
        decision = "blocked"
        state.status = "blocked"

    if decision == "proceed":
        advance(repo_root, state)
    else:
        run_state_mod.save_state(repo_root, state.run_id, state)
    return {
        "decision": decision,
        "round": round_number,
        "selected_score": score,
        "threshold": validate.threshold(scoreboard),
    }


def advance_checked(repo_root: str | Path, state: RunState) -> dict:
    """Advance only if the current state's contract is satisfied.

    Enforced states are gates (declared artifacts must be present) and states
    with a registered content verifier (artifact must be present and valid).
    On failure: record `gates[state] = "fail"`, persist, report `missing`
    (gate presence) and `problems` (content). Unenforced states advance freely.
    """

    name = state.current_state
    check = verify_state(repo_root, state.run_id, name)
    if check["enforced"] and not check["ok"]:
        state.gates[name] = "fail"
        run_state_mod.save_state(repo_root, state.run_id, state)
        return {
            "advanced": False,
            "state": name,
            "missing": check["missing"],
            "problems": check["problems"],
        }
    if check["enforced"]:
        state.gates[name] = "pass"
    advance(repo_root, state)
    return {"advanced": True, "state": name, "missing": [], "problems": []}


def _read_run_json(repo_root: str | Path, run_id: str, rel_path: str):
    path = Path(repo_root).resolve() / "runs" / run_id / rel_path
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return None


# state name -> {run-relative artifact path: content validator}.
# Every path here MUST be one of that state's spine `produces`
# (asserted by test_every_registered_validator_path_is_declared_in_spine).
# Presence of ALL declared produces is enforced separately, below.
STATE_CONTENT_VALIDATORS = {
    "GENERATE_STORY_CONCEPT": {
        "planning/story_concept.json": validate.validate_story_concept,
    },
    "GENERATE_SLIDE_BEATS": {
        "planning/slide_beat_map.json": validate.validate_slide_beat_map,
    },
    "SELECT_AND_ORDER_SLIDES": {
        "planning/selected_scenes.json": validate.validate_selected_scenes,
    },
}


def verify_state(repo_root: str | Path, run_id: str, state_name: str) -> dict:
    """Report whether a state's contract is satisfied.

    A state is enforced if it is a gate OR has registered content validators.
    For enforced states, ALL declared `produces` must be present (`missing`),
    and every registered artifact must pass its content validator (`problems`).
    Plain states (neither) are unenforced and advance freely.
    """

    spec = spine.by_name(state_name)
    content_validators = STATE_CONTENT_VALIDATORS.get(state_name)
    enforced = spec.kind == "gate" or content_validators is not None
    missing = (
        gates.missing_artifacts(repo_root, run_id, state_name) if enforced else []
    )
    problems: list[str] = []
    if content_validators:
        for rel_path, validator in content_validators.items():
            problems.extend(validator(_read_run_json(repo_root, run_id, rel_path)))
    return {
        "state": spec.name,
        "enforced": enforced,
        "ok": not missing and not problems,
        "missing": missing,
        "problems": problems,
    }
