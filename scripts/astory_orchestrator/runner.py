"""The idea-room leg controller (copilot mode).

Owns state advancement, the HITL halt, and the bounded idea-room retry loop.
Reads and writes `RunState`; it does NOT call any model. The creative work is
still produced by the agent — the runner only says what the next legal action
is, counts the loop, and records the HITL decision.
"""

from __future__ import annotations

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
    """Advance only if the current state's artifact gate passes.

    For `kind="gate"` states with missing declared artifacts, refuse to move,
    record `gates[state] = "fail"`, persist, and report what is missing. This
    is the gate the model cannot talk its way past.
    """

    check = gates.check_gate(repo_root, state.run_id, state.current_state)
    if check["is_gate"] and not check["ok"]:
        state.gates[state.current_state] = "fail"
        run_state_mod.save_state(repo_root, state.run_id, state)
        return {
            "advanced": False,
            "state": state.current_state,
            "missing": check["missing"],
        }
    if check["is_gate"]:
        state.gates[state.current_state] = "pass"
    gate_state = state.current_state
    advance(repo_root, state)
    return {"advanced": True, "state": gate_state, "missing": []}
