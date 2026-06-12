# A Story Orchestrator — Phase 2 (Guards + Gates) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harden the Phase 1 copilot so it cannot be driven out of order — state-position guards on `record_idea_round`, decision-vocabulary validation on `record_hitl`, `proceed` auto-advances the cursor, and a new `gates.py` that physically refuses to advance past a gate state whose required artifacts are missing.

**Architecture:** Phase 2 closes the three loose ends from the Phase 1 final integration review, then adds the first *enforced* hard gate. `gates.py` is pure: given `repo_root`/`run_id`/`state_name`, it checks the spine's declared `produces` paths exist on disk and returns missing ones. `runner.advance_checked` consumes it — refusing to advance past a `kind="gate"` state with missing artifacts and recording the result in `RunState.gates`. The CLI gains one subcommand, `advance`, exposing checked advancement with the established nonzero-exit-on-blocked convention.

**Tech Stack:** Python 3 stdlib only. Builds on Phase 0/1 (`spine.py`, `state.py`, `validate.py`, `runner.py`, `astory_orchestrator_cli.py`). Same conventions: `unittest`, `from __future__ import annotations`, `json.dumps(indent=2, sort_keys=True)` for persisted JSON, argparse CLI, TDD.

---

## Why these four tasks (traceability)

From the Phase 1 final integration review:
1. "No state-position guard on `idea-round`" — the loop counter and the spine cursor are decoupled; you can record an idea round at `INIT_RUN`. → **Task 1**
2. "`approve` default decision … any non-approved string silently blocks (no validation of the decision vocabulary)." → **Task 1**
3. "`proceed` does not advance state." → **Task 2**
From the original Boris architecture: "gates.py — the hard gates as assertions … code that physically cannot be bypassed." → **Tasks 3-4** (artifact-presence enforcement; richer content gates like agent-assignment come with the legs that produce them, Phase 3).

## File Structure

| File | Responsibility | New? |
| --- | --- | --- |
| `scripts/astory_orchestrator/runner.py` | Add `IDEA_ROUND_STATES`, `HITL_DECISIONS`, position guard, vocabulary guard, proceed-auto-advance, `advance_checked`. | Modify |
| `scripts/astory_orchestrator/gates.py` | Pure artifact-presence gate: `missing_artifacts`, `check_gate`. | Create |
| `scripts/astory_orchestrator_cli.py` | Add `advance` subcommand (checked advancement). | Modify |
| `tests/test_astory_orchestrator_runner.py` | Guard + auto-advance tests. | Modify |
| `tests/test_astory_orchestrator_gates.py` | Gate unit tests. | Create |
| `tests/test_astory_orchestrator_cli.py` | `advance` subcommand tests. | Modify |

## Out of scope for Phase 2 (deferred to Phase 3)

- Story/prompt/image legs and their loops.
- `dispatch.py` persona packet builder.
- Content-level gate checks (e.g., parsing `pre_generation_eval.json` for `agent_assignment_status`) — Phase 2 enforces artifact *presence* only; content gates arrive with the legs that produce those artifacts.
- Any change to `SKILL.md` or the live `/astory` workflow.

## Current code you will modify (exact, as of commit `3d6a5ea`)

`scripts/astory_orchestrator/runner.py` ends with:

```python
IDEA_ROOM_KEY = "idea_room"
MAX_IDEA_ROUNDS = 2


def record_idea_round(repo_root: str | Path, state: RunState, scoreboard: dict) -> dict:
    """Record one idea-room scoring round and decide proceed/rerun/blocked.

    The retry counter lives in RunState.retries[IDEA_ROOM_KEY], so the bound is
    enforced by code across reloads — not remembered by the model.
    """

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

    run_state_mod.save_state(repo_root, state.run_id, state)
    return {
        "decision": decision,
        "round": round_number,
        "selected_score": score,
        "threshold": validate.threshold(scoreboard),
    }
```

and `record_hitl` contains:

```python
    state.hitl[state.current_state] = decision
    if decision in {"approved", "approved_with_revision"}:
        return advance(repo_root, state)
```

---

## Task 1: Position + vocabulary guards (`runner.py`)

**Files:**
- Modify: `scripts/astory_orchestrator/runner.py`
- Test: `tests/test_astory_orchestrator_runner.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_astory_orchestrator_runner.py`, before the `if __name__ == "__main__":` block:

```python
class GuardTests(unittest.TestCase):
    def test_idea_round_outside_idea_states_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "INIT_RUN"
            with self.assertRaises(ValueError):
                runner.record_idea_round(tmp, state, PASS_SCOREBOARD)

    def test_idea_round_allowed_in_each_idea_state(self):
        for state_name in runner.IDEA_ROUND_STATES:
            with tempfile.TemporaryDirectory() as tmp:
                state = _fresh(tmp)
                state.current_state = state_name
                result = runner.record_idea_round(tmp, state, FAIL_SCOREBOARD)
                self.assertEqual(result["decision"], "rerun")

    def test_unknown_hitl_decision_raises_and_records_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "HITL_IDEA_LOCK"
            with self.assertRaises(ValueError):
                runner.record_hitl(tmp, state, "maybe")
            self.assertNotIn("HITL_IDEA_LOCK", state.hitl)

    def test_rejection_decisions_block(self):
        for decision in ("rejected", "revision_requested"):
            with tempfile.TemporaryDirectory() as tmp:
                state = _fresh(tmp)
                state.current_state = "HITL_IDEA_LOCK"
                result = runner.record_hitl(tmp, state, decision)
                self.assertEqual(result.status, "blocked")
```

- [ ] **Step 2: Run tests to verify the new ones fail**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_runner -v`
Expected: `GuardTests` fail — `test_idea_round_outside_idea_states_raises` gets no ValueError, `test_idea_round_allowed_in_each_idea_state` fails with `AttributeError: ... no attribute 'IDEA_ROUND_STATES'`, `test_unknown_hitl_decision_raises_and_records_nothing` gets no ValueError. The pre-existing 11 runner tests still pass.

- [ ] **Step 3: Implement the guards**

In `scripts/astory_orchestrator/runner.py`:

(a) Below `MAX_IDEA_ROUNDS = 2`, add:

```python
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
```

(b) In `record_idea_round`, insert as the FIRST lines of the function body (before the counter increment):

```python
    if state.current_state not in IDEA_ROUND_STATES:
        raise ValueError(
            f"idea round not allowed at {state.current_state}; "
            f"expected one of {IDEA_ROUND_STATES}"
        )
```

(c) In `record_hitl`, insert AFTER the existing `if spec.kind != "hitl": raise ...` block and BEFORE `state.hitl[state.current_state] = decision`:

```python
    if decision not in HITL_DECISIONS:
        raise ValueError(
            f"unknown HITL decision: {decision!r}; expected one of {HITL_DECISIONS}"
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_runner -v`
Expected: PASS. NOTE: the pre-existing `IdeaRoomLoopTests` set `current_state = "SCORE_IDEAS"`, which is in `IDEA_ROUND_STATES`, so they keep passing unchanged.

- [ ] **Step 5: Commit**

```bash
cd "/Users/himanshusharma/A Story of Two V2"
git add scripts/astory_orchestrator/runner.py tests/test_astory_orchestrator_runner.py
git commit -m "feat(orchestrator): position and decision-vocabulary guards"
```

---

## Task 2: `proceed` auto-advances the cursor (`runner.py`)

**Files:**
- Modify: `scripts/astory_orchestrator/runner.py`
- Test: `tests/test_astory_orchestrator_runner.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_astory_orchestrator_runner.py`, before the `if __name__ == "__main__":` block:

```python
class ProceedAdvancesTests(unittest.TestCase):
    def test_proceed_advances_cursor(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "SCORE_IDEAS"
            result = runner.record_idea_round(tmp, state, PASS_SCOREBOARD)
            self.assertEqual(result["decision"], "proceed")
            self.assertEqual(state.current_state, "SELECT_BEST_IDEA")
            self.assertIn("SCORE_IDEAS", state.completed)

    def test_rerun_keeps_cursor(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "SCORE_IDEAS"
            runner.record_idea_round(tmp, state, FAIL_SCOREBOARD)
            self.assertEqual(state.current_state, "SCORE_IDEAS")

    def test_proceed_persists_advanced_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "SCORE_IDEAS"
            runner.record_idea_round(tmp, state, PASS_SCOREBOARD)
            reloaded = run_state_mod.load_state(tmp, state.run_id)
            self.assertEqual(reloaded.current_state, "SELECT_BEST_IDEA")
```

- [ ] **Step 2: Run tests to verify the new ones fail**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_runner.ProceedAdvancesTests -v`
Expected: FAIL — after `proceed`, `current_state` is still `"SCORE_IDEAS"`.

- [ ] **Step 3: Implement**

In `record_idea_round`, replace:

```python
    run_state_mod.save_state(repo_root, state.run_id, state)
    return {
```

with:

```python
    if decision == "proceed":
        advance(repo_root, state)
    else:
        run_state_mod.save_state(repo_root, state.run_id, state)
    return {
```

(`advance` already appends to `completed`, moves the cursor, sets status, and saves — so the proceed branch must not double-save.)

- [ ] **Step 4: Run the full runner + CLI tests**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_runner tests.test_astory_orchestrator_cli -v`
Expected: PASS. NOTE: the CLI test `test_idea_round_proceed_then_next_halts_then_approve` re-plants `HITL_IDEA_LOCK` via `_set_state` after proceed, so it remains valid (the auto-advance lands on `SELECT_BEST_IDEA`, then the test overwrites state).

- [ ] **Step 5: Commit**

```bash
cd "/Users/himanshusharma/A Story of Two V2"
git add scripts/astory_orchestrator/runner.py tests/test_astory_orchestrator_runner.py
git commit -m "feat(orchestrator): proceed auto-advances the spine cursor"
```

---

## Task 3: Artifact-presence gate (`gates.py`)

**Files:**
- Create: `scripts/astory_orchestrator/gates.py`
- Test: `tests/test_astory_orchestrator_gates.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_astory_orchestrator_gates.py`:

```python
import tempfile
import unittest
from pathlib import Path

from scripts.astory_orchestrator import gates


def _touch(repo_root, run_id, rel_path):
    path = Path(repo_root) / "runs" / run_id / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("x")


class MissingArtifactsTests(unittest.TestCase):
    def test_all_present_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            _touch(tmp, "demo", "debates/agent_assignment_matrix.md")
            self.assertEqual(
                gates.missing_artifacts(tmp, "demo", "DISCOVER_AND_ASSIGN_AGENTS"),
                [],
            )

    def test_missing_listed_run_relative(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(
                gates.missing_artifacts(tmp, "demo", "DISCOVER_AND_ASSIGN_AGENTS"),
                ["debates/agent_assignment_matrix.md"],
            )

    def test_state_with_no_produces_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(gates.missing_artifacts(tmp, "demo", "INIT_RUN"), [])

    def test_unknown_state_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(KeyError):
                gates.missing_artifacts(tmp, "demo", "NOT_A_STATE")


class CheckGateTests(unittest.TestCase):
    def test_gate_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            _touch(tmp, "demo", "debates/agent_assignment_matrix.md")
            result = gates.check_gate(tmp, "demo", "DISCOVER_AND_ASSIGN_AGENTS")
            self.assertTrue(result["ok"])
            self.assertEqual(result["missing"], [])

    def test_gate_fail_lists_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = gates.check_gate(tmp, "demo", "DISCOVER_AND_ASSIGN_AGENTS")
            self.assertFalse(result["ok"])
            self.assertEqual(result["missing"], ["debates/agent_assignment_matrix.md"])
            self.assertEqual(result["state"], "DISCOVER_AND_ASSIGN_AGENTS")

    def test_non_gate_state_is_ok_but_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = gates.check_gate(tmp, "demo", "INIT_RUN")
            self.assertTrue(result["ok"])
            self.assertFalse(result["is_gate"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_gates -v`
Expected: FAIL with `ImportError: cannot import name 'gates'`.

- [ ] **Step 3: Write minimal implementation**

Create `scripts/astory_orchestrator/gates.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_gates -v`
Expected: PASS (7 tests).

- [ ] **Step 5: Commit**

```bash
cd "/Users/himanshusharma/A Story of Two V2"
git add scripts/astory_orchestrator/gates.py tests/test_astory_orchestrator_gates.py
git commit -m "feat(orchestrator): artifact-presence gates from spine produces"
```

---

## Task 4: Checked advancement (`runner.advance_checked` + CLI `advance`)

**Files:**
- Modify: `scripts/astory_orchestrator/runner.py`
- Modify: `scripts/astory_orchestrator_cli.py`
- Test: `tests/test_astory_orchestrator_runner.py`, `tests/test_astory_orchestrator_cli.py`

- [ ] **Step 1: Write the failing runner tests**

Append to `tests/test_astory_orchestrator_runner.py`, before `if __name__ == "__main__":`. Also add `from pathlib import Path` to the imports at the top of the file:

```python
class AdvanceCheckedTests(unittest.TestCase):
    def _touch(self, tmp, run_id, rel_path):
        path = Path(tmp) / "runs" / run_id / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x")

    def test_gate_state_with_missing_artifacts_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "DISCOVER_AND_ASSIGN_AGENTS"
            result = runner.advance_checked(tmp, state)
            self.assertFalse(result["advanced"])
            self.assertEqual(
                result["missing"], ["debates/agent_assignment_matrix.md"]
            )
            self.assertEqual(state.current_state, "DISCOVER_AND_ASSIGN_AGENTS")
            self.assertEqual(state.gates["DISCOVER_AND_ASSIGN_AGENTS"], "fail")

    def test_gate_state_with_artifacts_advances(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "DISCOVER_AND_ASSIGN_AGENTS"
            self._touch(tmp, state.run_id, "debates/agent_assignment_matrix.md")
            result = runner.advance_checked(tmp, state)
            self.assertTrue(result["advanced"])
            self.assertEqual(state.current_state, "GENERATE_OR_REFINE_IDEAS")
            self.assertEqual(state.gates["DISCOVER_AND_ASSIGN_AGENTS"], "pass")

    def test_non_gate_state_advances_without_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            result = runner.advance_checked(tmp, state)
            self.assertTrue(result["advanced"])
            self.assertEqual(state.current_state, "PARSE_CREATIVE_INPUT")

    def test_gate_refusal_persists(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "DISCOVER_AND_ASSIGN_AGENTS"
            runner.advance_checked(tmp, state)
            reloaded = run_state_mod.load_state(tmp, state.run_id)
            self.assertEqual(reloaded.gates["DISCOVER_AND_ASSIGN_AGENTS"], "fail")
```

- [ ] **Step 2: Run to verify the new tests fail**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_runner.AdvanceCheckedTests -v`
Expected: FAIL with `AttributeError: ... no attribute 'advance_checked'`.

- [ ] **Step 3: Implement `advance_checked`**

In `scripts/astory_orchestrator/runner.py`:

(a) Add to the imports:

```python
from scripts.astory_orchestrator import gates
```

(b) Append at the end of the file:

```python
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
```

- [ ] **Step 4: Run runner tests to verify they pass**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_runner -v`
Expected: PASS (all, including the 4 new `AdvanceCheckedTests`).

- [ ] **Step 5: Write the failing CLI test**

Append to `tests/test_astory_orchestrator_cli.py`, inside `IdeaLegWalkTests` (it already has `_set_state`):

```python
    def test_advance_blocked_at_gate_then_passes_with_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._set_state(tmp, "demo", "DISCOVER_AND_ASSIGN_AGENTS")

            refused = _run("--repo-root", tmp, "advance", "--run-id", "demo")
            self.assertEqual(refused.returncode, 1)
            body = json.loads(refused.stdout)
            self.assertFalse(body["advanced"])
            self.assertIn("debates/agent_assignment_matrix.md", body["missing"])

            artifact = Path(tmp) / "runs" / "demo" / "debates" / "agent_assignment_matrix.md"
            artifact.parent.mkdir(parents=True, exist_ok=True)
            artifact.write_text("matrix")

            ok = _run("--repo-root", tmp, "advance", "--run-id", "demo")
            self.assertEqual(ok.returncode, 0, ok.stderr)
            self.assertTrue(json.loads(ok.stdout)["advanced"])
```

- [ ] **Step 6: Run to verify the CLI test fails**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_cli -v`
Expected: the new test FAILS (unknown `advance` subcommand → argparse exits 2).

- [ ] **Step 7: Implement the CLI subcommand**

In `scripts/astory_orchestrator_cli.py`:

(a) Add a handler after `_cmd_approve`:

```python
def _cmd_advance(args: argparse.Namespace) -> int:
    state = run_state_mod.load_state(args.repo_root, args.run_id)
    if state is None:
        print(json.dumps({"status": "no_state", "run_id": args.run_id}, indent=2))
        return 1
    result = runner.advance_checked(args.repo_root, state)
    print(json.dumps(result, indent=2))
    return 0 if result["advanced"] else 1
```

(b) Register the subparser in `main()` alongside the others:

```python
    p_advance = sub.add_parser("advance", help="Advance one state; refuses at a failing gate.")
    p_advance.add_argument("--run-id", required=True)
```

(c) Add to the handlers dict:

```python
        "advance": _cmd_advance,
```

- [ ] **Step 8: Run the full orchestrator suite**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_spine tests.test_astory_orchestrator_state tests.test_astory_orchestrator_validate tests.test_astory_orchestrator_runner tests.test_astory_orchestrator_gates tests.test_astory_orchestrator_cli -v`
Expected: ALL PASS.

- [ ] **Step 9: Commit**

```bash
cd "/Users/himanshusharma/A Story of Two V2"
git add scripts/astory_orchestrator/runner.py scripts/astory_orchestrator_cli.py tests/test_astory_orchestrator_runner.py tests/test_astory_orchestrator_cli.py
git commit -m "feat(orchestrator): checked advancement with enforced artifact gates"
```

---

## Self-Review

**1. Spec coverage:** review-finding 1 (position guard) → Task 1; finding 2 (decision vocabulary) → Task 1; finding 3 (proceed advances) → Task 2; gates-as-code → Tasks 3-4. No gaps for the Phase 2 scope; legs/dispatch explicitly deferred.

**2. Placeholder scan:** all steps carry complete code and exact commands; no TBD/"handle edge cases"/"similar to Task N".

**3. Type consistency:** `gates.missing_artifacts(repo_root, run_id, state_name)` and `gates.check_gate(...)` used identically in Task 3 tests and Task 4 runner. `advance_checked` return keys (`advanced`, `state`, `missing`) match runner tests and the CLI handler/test. `IDEA_ROUND_STATES`/`HITL_DECISIONS` referenced in Task 1 tests match the Task 1 implementation. `record_hitl` blocked path already covers `rejected`/`revision_requested` since both are non-approving members of `HITL_DECISIONS`.

**Interaction check:** Task 1's guard runs before Task 2's auto-advance edit (both in `record_idea_round`); the final function body order is guard → counter → decision → proceed-advance/save. Pre-existing tests stay green: `IdeaRoomLoopTests` use `SCORE_IDEAS` (allowed by guard; rerun/blocked paths don't advance), CLI walk re-plants state after proceed.

## Definition of Done (Phase 2)

- Full repo suite green (was 160; Phase 2 adds ~16).
- `record_idea_round` at `INIT_RUN` raises; `record_hitl` with `"maybe"` raises.
- `proceed` lands the cursor on `SELECT_BEST_IDEA` and persists it.
- CLI `advance` exits 1 with a `missing` list at an unsatisfied gate state and exits 0 once the artifact exists.
- No change to `SKILL.md`, spine.py, state.py, validate.py, or any pre-existing test.
