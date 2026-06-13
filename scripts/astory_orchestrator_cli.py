#!/usr/bin/env python3
"""A Story orchestrator CLI (copilot mode).

Inspect-only subcommands:
  spine           Print the 32-state spine as JSON.
  validate-spine  Print structural problems; exit 1 if any.
  init            Create runs/<run_id>/state/run_state.json (idempotent unless --force).
  status          Print current_state / status / next_state for a run.

State-advancing subcommands (drive the idea-room leg):
  next            Show the next legal action for a run (may halt for HITL).
  idea-round      Record one idea-room scoring round and advance run state.
  approve         Record a HITL decision at the current gate and advance.

It does not call any model or dispatch agents; the operator supplies inputs
(e.g. a scoreboard) and the CLI advances run state and enforces leg gates.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure repo root is importable so `scripts.*` resolves when run as a file.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.astory_orchestrator import spine
from scripts.astory_orchestrator import state as run_state_mod
from scripts.astory_orchestrator import runner


def _cmd_spine(args: argparse.Namespace) -> int:
    payload = [
        {
            "index": s.index,
            "name": s.name,
            "kind": s.kind,
            "next": s.next,
            "produces": list(s.produces),
        }
        for s in spine.STATES
    ]
    print(json.dumps(payload, indent=2))
    return 0


def _cmd_validate_spine(args: argparse.Namespace) -> int:
    problems = spine.validate_spine()
    print(json.dumps({"ok": not problems, "problems": problems}, indent=2))
    return 0 if not problems else 1


def _cmd_init(args: argparse.Namespace) -> int:
    existing = run_state_mod.load_state(args.repo_root, args.run_id)
    if existing is not None and not args.force:
        print(json.dumps({"status": "exists", "run_id": args.run_id}, indent=2))
        return 1
    state = run_state_mod.new_run_state(args.run_id)
    path = run_state_mod.save_state(args.repo_root, args.run_id, state)
    print(
        json.dumps(
            {
                "status": "created",
                "path": str(path),
                "current_state": state.current_state,
            },
            indent=2,
        )
    )
    return 0


def _cmd_status(args: argparse.Namespace) -> int:
    state = run_state_mod.load_state(args.repo_root, args.run_id)
    if state is None:
        print(json.dumps({"status": "no_state", "run_id": args.run_id}, indent=2))
        return 1
    print(
        json.dumps(
            {
                "run_id": state.run_id,
                "current_state": state.current_state,
                "status": state.status,
                "completed_count": len(state.completed),
                "next_state": spine.next_state(state.current_state),
            },
            indent=2,
        )
    )
    return 0


def _cmd_next(args: argparse.Namespace) -> int:
    state = run_state_mod.load_state(args.repo_root, args.run_id)
    if state is None:
        print(json.dumps({"status": "no_state", "run_id": args.run_id}, indent=2))
        return 1
    print(json.dumps(runner.next_action(state), indent=2))
    return 0


def _cmd_idea_round(args: argparse.Namespace) -> int:
    state = run_state_mod.load_state(args.repo_root, args.run_id)
    if state is None:
        print(json.dumps({"status": "no_state", "run_id": args.run_id}, indent=2))
        return 1
    try:
        scoreboard = json.loads(Path(args.scoreboard).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "bad_scoreboard", "path": args.scoreboard, "error": str(exc)}, indent=2))
        return 1
    result = runner.record_idea_round(args.repo_root, state, scoreboard)
    print(json.dumps(result, indent=2))
    return 1 if result["decision"] == "blocked" else 0


def _cmd_approve(args: argparse.Namespace) -> int:
    state = run_state_mod.load_state(args.repo_root, args.run_id)
    if state is None:
        print(json.dumps({"status": "no_state", "run_id": args.run_id}, indent=2))
        return 1
    result = runner.record_hitl(args.repo_root, state, args.decision)
    print(
        json.dumps(
            {"current_state": result.current_state, "status": result.status},
            indent=2,
        )
    )
    return 1 if result.status == "blocked" else 0


def _cmd_advance(args: argparse.Namespace) -> int:
    state = run_state_mod.load_state(args.repo_root, args.run_id)
    if state is None:
        print(json.dumps({"status": "no_state", "run_id": args.run_id}, indent=2))
        return 1
    if spine.next_state(state.current_state) is None:
        print(
            json.dumps(
                {"status": "terminal", "current_state": state.current_state},
                indent=2,
            )
        )
        return 1
    result = runner.advance_checked(args.repo_root, state)
    print(json.dumps(result, indent=2))
    return 0 if result["advanced"] else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="A Story orchestrator: inspect the spine and drive the idea-room leg."
    )
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("spine", help="Print the 32-state spine as JSON.")
    sub.add_parser("validate-spine", help="Validate the spine; exit 1 on problems.")

    p_init = sub.add_parser("init", help="Create a run's state file.")
    p_init.add_argument("--run-id", required=True)
    p_init.add_argument("--force", action="store_true", help="Overwrite existing state.")

    p_status = sub.add_parser("status", help="Show a run's current state.")
    p_status.add_argument("--run-id", required=True)

    p_next = sub.add_parser("next", help="Show the next legal action for a run.")
    p_next.add_argument("--run-id", required=True)

    p_idea = sub.add_parser("idea-round", help="Record one idea-room scoring round.")
    p_idea.add_argument("--run-id", required=True)
    p_idea.add_argument("--scoreboard", required=True, help="Path to a final_scoreboard.json.")

    p_approve = sub.add_parser("approve", help="Record a HITL decision at the current gate.")
    p_approve.add_argument("--run-id", required=True)
    p_approve.add_argument("--decision", default="approved")

    p_advance = sub.add_parser("advance", help="Advance one state; refuses at a failing gate.")
    p_advance.add_argument("--run-id", required=True)

    args = parser.parse_args()
    handlers = {
        "spine": _cmd_spine,
        "validate-spine": _cmd_validate_spine,
        "init": _cmd_init,
        "status": _cmd_status,
        "next": _cmd_next,
        "idea-round": _cmd_idea_round,
        "approve": _cmd_approve,
        "advance": _cmd_advance,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
