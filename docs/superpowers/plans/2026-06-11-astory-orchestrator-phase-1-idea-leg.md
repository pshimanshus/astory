# A Story Orchestrator — Phase 1 (Idea-Room Leg, Copilot) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire the orchestrator as a **copilot** for one leg of the workflow — idea room → `HITL_IDEA_LOCK` (spine states 7-10) — so the bounded retry loop (`selected score < 4.0 → rerun, max 2 rounds`) and the HITL halt live in **code + `RunState`**, not in the model's attention.

**Architecture:** Three new pure-Python modules in the existing `scripts/astory_orchestrator/` package — `validate.py` (shape-tolerant idea-room artifact validators), `runner.py` (state advancement, HITL halt, and the bounded idea-room loop) — plus CLI subcommands that let a human/agent drive the leg. The runner owns the loop counter via `RunState.retries["idea_room"]`; it does not call any model. "Copilot" = the orchestrator tells you the next legal action and validates outputs; the creative work is still done by the agent.

**Tech Stack:** Python 3 stdlib only. Builds on Phase 0 (`spine.py`, `state.py`). Same conventions: frozen/plain dataclasses, `unittest`, `json.dumps(indent=2, sort_keys=True)`, argparse CLI.

---

## Critical design fact (learned from real artifacts, not templates)

The **template** and **real-run** idea-room schemas diverge. Validators MUST accept both:

| Field | Template shape | Real-run shape |
| --- | --- | --- |
| scoreboard entries | `survivors: [...]` | `candidates: [...]` |
| entry score | `scores.overall` (nested) | `overall_score` (flat) |
| threshold | `threshold` | `minimum_required_overall_score` |
| selected marker | `selected_idea_id` + `selection_status` | `selected` (title) + `selection_status` |
| `selected_idea.json` score | `final_idea_score` | **absent** — score is only in the scoreboard |

**Consequence:** the loop's stop condition reads the **scoreboard's selected candidate's score**, NOT `selected_idea.json`. `selected_idea.json` is validated for *structure* (id/title/concept), not score. Encode tolerance, not the drift.

## File Structure

| File | Responsibility | New? |
| --- | --- | --- |
| `scripts/astory_orchestrator/validate.py` | Shape-tolerant idea-room artifact validators + score extraction. Pure functions. | Create |
| `scripts/astory_orchestrator/runner.py` | State advancement, HITL halt, bounded idea-room loop. Reads/writes `RunState`; calls no model. | Create |
| `scripts/astory_orchestrator_cli.py` | Add `next`, `idea-round`, `approve` subcommands. | Modify |
| `tests/test_astory_orchestrator_validate.py` | Validator tests against BOTH template and real-run shapes. | Create |
| `tests/test_astory_orchestrator_runner.py` | Advancement, HITL halt, and bounded-loop tests. | Create |
| `tests/test_astory_orchestrator_cli.py` | Add end-to-end leg walk (rerun → blocked; proceed → HITL halt → approve). | Modify |

## Out of scope for Phase 1 (deferred)

- States past `HITL_IDEA_LOCK` (story/prompt/image legs) — Phase 2+.
- Calling the model / generating ideas — copilot only; the agent still creates.
- Gate enforcement as hard assertions (`gates.py`) — Phase 2.
- Dispatch packet builder (`dispatch.py`) — Phase 2.

---

## Task 1: Idea-room validators (`validate.py`)

**Files:**
- Create: `scripts/astory_orchestrator/validate.py`
- Test: `tests/test_astory_orchestrator_validate.py`

**TDD.** Write the test first, watch it fail, implement, watch it pass, commit.

- [ ] **Step 1: Write the failing test**

Create `tests/test_astory_orchestrator_validate.py`:

```python
import unittest

from scripts.astory_orchestrator import validate

# Real-run shape (runs/2026-06-10_22-22_heart-rent/debates/idea_room/final_scoreboard.json)
REAL_SCOREBOARD = {
    "selected": "Heart Rent Notice",
    "minimum_required_overall_score": 4.0,
    "candidates": [
        {"title": "Heart Rent Notice", "overall_score": 4.7, "selection_status": "selected"},
        {"title": "Security Deposit", "overall_score": 4.0, "selection_status": "rejected"},
        {"title": "Receipt At The Door", "overall_score": 3.7, "selection_status": "rejected"},
    ],
}

# Template shape (.agents/skills/astory/templates/debates/final_scoreboard.json)
TEMPLATE_SCOREBOARD = {
    "threshold": 4.0,
    "selected_idea_id": "idea_001",
    "survivors": [
        {
            "idea_id": "idea_001",
            "title": "A",
            "scores": {"overall": 4.5},
            "selection_status": "selected",
        },
        {
            "idea_id": "idea_002",
            "title": "B",
            "scores": {"overall": 3.2},
            "selection_status": "rejected",
        },
    ],
}

REAL_SELECTED_IDEA = {
    "id": "idea_01",
    "title": "Heart Rent Notice",
    "one_line_concept": "Aachu playfully asks Zuv to pay rent for living in her heart.",
}

TEMPLATE_SELECTED_IDEA = {
    "selected_idea_id": "idea_001",
    "final_title": "A",
    "final_concept": "concept text",
}


class ScoreExtractionTests(unittest.TestCase):
    def test_best_overall_score_real_shape(self):
        self.assertEqual(validate.best_overall_score(REAL_SCOREBOARD), 4.7)

    def test_best_overall_score_template_shape(self):
        self.assertEqual(validate.best_overall_score(TEMPLATE_SCOREBOARD), 4.5)

    def test_selected_score_prefers_selected_entry(self):
        self.assertEqual(validate.selected_score(REAL_SCOREBOARD), 4.7)
        self.assertEqual(validate.selected_score(TEMPLATE_SCOREBOARD), 4.5)

    def test_threshold_reads_either_key(self):
        self.assertEqual(validate.threshold(REAL_SCOREBOARD), 4.0)
        self.assertEqual(validate.threshold(TEMPLATE_SCOREBOARD), 4.0)
        self.assertEqual(validate.threshold({}), validate.MIN_IDEA_SCORE)

    def test_meets_threshold(self):
        self.assertTrue(validate.meets_threshold(REAL_SCOREBOARD))
        below = {
            "minimum_required_overall_score": 4.0,
            "candidates": [
                {"title": "X", "overall_score": 3.5, "selection_status": "selected"}
            ],
        }
        self.assertFalse(validate.meets_threshold(below))


class ScoreboardValidationTests(unittest.TestCase):
    def test_real_and_template_scoreboards_are_valid(self):
        self.assertEqual(validate.validate_final_scoreboard(REAL_SCOREBOARD), [])
        self.assertEqual(validate.validate_final_scoreboard(TEMPLATE_SCOREBOARD), [])

    def test_non_dict_scoreboard_reports_problem(self):
        self.assertTrue(validate.validate_final_scoreboard(None))
        self.assertTrue(validate.validate_final_scoreboard([]))

    def test_empty_entries_reports_problem(self):
        self.assertIn(
            "no_idea_entries",
            validate.validate_final_scoreboard({"candidates": []}),
        )

    def test_no_parseable_score_reports_problem(self):
        bad = {"candidates": [{"title": "X", "selection_status": "selected"}]}
        self.assertIn("no_parseable_overall_score", validate.validate_final_scoreboard(bad))


class SelectedIdeaValidationTests(unittest.TestCase):
    def test_real_and_template_selected_ideas_are_valid(self):
        self.assertEqual(validate.validate_selected_idea(REAL_SELECTED_IDEA), [])
        self.assertEqual(validate.validate_selected_idea(TEMPLATE_SELECTED_IDEA), [])

    def test_missing_id_title_concept_reported(self):
        problems = validate.validate_selected_idea({})
        self.assertIn("missing_id", problems)
        self.assertIn("missing_title", problems)
        self.assertIn("missing_concept", problems)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_validate -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scripts.astory_orchestrator.validate'`.

- [ ] **Step 3: Write minimal implementation**

Create `scripts/astory_orchestrator/validate.py`:

```python
"""Shape-tolerant validators for idea-room artifacts.

The template and real-run schemas diverge (survivors/candidates,
scores.overall/overall_score, threshold/minimum_required_overall_score). These
helpers accept either shape and answer the two questions the runner needs:
what is the selected idea's score, and is each artifact well-formed.
"""

from __future__ import annotations

from typing import Any

MIN_IDEA_SCORE = 4.0


def _entries(scoreboard: Any) -> list[dict[str, Any]]:
    if not isinstance(scoreboard, dict):
        return []
    raw = scoreboard.get("survivors")
    if not isinstance(raw, list):
        raw = scoreboard.get("candidates")
    if not isinstance(raw, list):
        return []
    return [entry for entry in raw if isinstance(entry, dict)]


def _entry_score(entry: dict[str, Any]) -> float | None:
    value = entry.get("overall_score")
    if isinstance(value, (int, float)):
        return float(value)
    scores = entry.get("scores")
    if isinstance(scores, dict) and isinstance(scores.get("overall"), (int, float)):
        return float(scores["overall"])
    return None


def best_overall_score(scoreboard: Any) -> float | None:
    parsed = [s for s in (_entry_score(e) for e in _entries(scoreboard)) if s is not None]
    return max(parsed) if parsed else None


def selected_entry(scoreboard: Any) -> dict[str, Any] | None:
    entries = _entries(scoreboard)
    if not entries:
        return None
    for entry in entries:
        if entry.get("selection_status") == "selected":
            return entry
    if isinstance(scoreboard, dict):
        marker = scoreboard.get("selected") or scoreboard.get("selected_idea_id")
        if marker is not None:
            for entry in entries:
                if marker in (entry.get("title"), entry.get("idea_id"), entry.get("id")):
                    return entry
    scored = [(e, _entry_score(e)) for e in entries]
    scored = [(e, s) for e, s in scored if s is not None]
    if scored:
        return max(scored, key=lambda pair: pair[1])[0]
    return None


def selected_score(scoreboard: Any) -> float | None:
    entry = selected_entry(scoreboard)
    if entry is not None:
        score = _entry_score(entry)
        if score is not None:
            return score
    return best_overall_score(scoreboard)


def threshold(scoreboard: Any) -> float:
    if isinstance(scoreboard, dict):
        for key in ("threshold", "minimum_required_overall_score"):
            value = scoreboard.get(key)
            if isinstance(value, (int, float)):
                return float(value)
    return MIN_IDEA_SCORE


def meets_threshold(scoreboard: Any) -> bool:
    score = selected_score(scoreboard)
    return score is not None and score >= threshold(scoreboard)


def validate_final_scoreboard(data: Any) -> list[str]:
    problems: list[str] = []
    if not isinstance(data, dict):
        return ["scoreboard_not_object"]
    entries = _entries(data)
    if not entries:
        problems.append("no_idea_entries")
        return problems
    if best_overall_score(data) is None:
        problems.append("no_parseable_overall_score")
    if selected_entry(data) is None:
        problems.append("no_selected_idea")
    return problems


def validate_selected_idea(data: Any) -> list[str]:
    problems: list[str] = []
    if not isinstance(data, dict):
        return ["selected_idea_not_object"]
    if not (data.get("id") or data.get("selected_idea_id")):
        problems.append("missing_id")
    if not (data.get("title") or data.get("final_title")):
        problems.append("missing_title")
    if not (data.get("one_line_concept") or data.get("final_concept")):
        problems.append("missing_concept")
    return problems
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_validate -v`
Expected: PASS (all tests).

- [ ] **Step 5: Commit**

```bash
cd "/Users/himanshusharma/A Story of Two V2"
git add scripts/astory_orchestrator/validate.py tests/test_astory_orchestrator_validate.py
git commit -m "feat(orchestrator): shape-tolerant idea-room validators"
```

---

## Task 2: Runner advancement + HITL halt (`runner.py`)

**Files:**
- Create: `scripts/astory_orchestrator/runner.py`
- Test: `tests/test_astory_orchestrator_runner.py`

**TDD.**

- [ ] **Step 1: Write the failing test**

Create `tests/test_astory_orchestrator_runner.py`:

```python
import tempfile
import unittest

from scripts.astory_orchestrator import runner
from scripts.astory_orchestrator import state as run_state_mod


def _fresh(tmp, run_id="2026-06-11_demo"):
    state = run_state_mod.new_run_state(run_id)
    run_state_mod.save_state(tmp, run_id, state)
    return state


class AdvanceTests(unittest.TestCase):
    def test_advance_moves_to_next_and_records_completed(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            advanced = runner.advance(tmp, state)
            self.assertEqual(advanced.current_state, "PARSE_CREATIVE_INPUT")
            self.assertIn("INIT_RUN", advanced.completed)
            self.assertEqual(advanced.status, "running")

    def test_advancing_into_hitl_state_sets_awaiting_hitl(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "SELECT_BEST_IDEA"
            advanced = runner.advance(tmp, state)
            self.assertEqual(advanced.current_state, "HITL_IDEA_LOCK")
            self.assertEqual(advanced.status, "awaiting_hitl")

    def test_advance_past_terminal_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "COMPLETE_OR_BLOCKED"
            with self.assertRaises(ValueError):
                runner.advance(tmp, state)


class NextActionTests(unittest.TestCase):
    def test_next_action_for_creative_state(self):
        state = run_state_mod.new_run_state("x")
        state.current_state = "GENERATE_OR_REFINE_IDEAS"
        action = runner.next_action(state)
        self.assertEqual(action["state"], "GENERATE_OR_REFINE_IDEAS")
        self.assertEqual(action["kind"], "creative")
        self.assertFalse(action["halt"])
        self.assertIn("planning/idea_candidates.json", action["produces"])

    def test_next_action_for_hitl_state_halts(self):
        state = run_state_mod.new_run_state("x")
        state.current_state = "HITL_IDEA_LOCK"
        action = runner.next_action(state)
        self.assertTrue(action["halt"])


class HitlTests(unittest.TestCase):
    def test_approved_advances_past_hitl(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "HITL_IDEA_LOCK"
            run_state_mod.save_state(tmp, "2026-06-11_demo", state)
            result = runner.record_hitl(tmp, state, "approved")
            self.assertEqual(result.hitl["HITL_IDEA_LOCK"], "approved")
            self.assertEqual(result.current_state, "GENERATE_STORY_CONCEPT")
            self.assertEqual(result.status, "running")

    def test_rejected_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "HITL_IDEA_LOCK"
            result = runner.record_hitl(tmp, state, "rejected")
            self.assertEqual(result.status, "blocked")
            self.assertEqual(result.current_state, "HITL_IDEA_LOCK")

    def test_record_hitl_on_non_hitl_state_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "GENERATE_OR_REFINE_IDEAS"
            with self.assertRaises(ValueError):
                runner.record_hitl(tmp, state, "approved")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_runner -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scripts.astory_orchestrator.runner'`.

- [ ] **Step 3: Write minimal implementation**

Create `scripts/astory_orchestrator/runner.py`:

```python
"""The idea-room leg controller (copilot mode).

Owns state advancement, the HITL halt, and the bounded idea-room retry loop.
Reads and writes `RunState`; it does NOT call any model. The creative work is
still produced by the agent — the runner only says what the next legal action
is, counts the loop, and records the HITL decision.
"""

from __future__ import annotations

from pathlib import Path

from scripts.astory_orchestrator import spine
from scripts.astory_orchestrator import state as run_state_mod
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
    state.hitl[state.current_state] = decision
    if decision in {"approved", "approved_with_revision"}:
        return advance(repo_root, state)
    state.status = "blocked"
    run_state_mod.save_state(repo_root, state.run_id, state)
    return state
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_runner -v`
Expected: PASS (all tests).

- [ ] **Step 5: Commit**

```bash
cd "/Users/himanshusharma/A Story of Two V2"
git add scripts/astory_orchestrator/runner.py tests/test_astory_orchestrator_runner.py
git commit -m "feat(orchestrator): runner advancement and HITL halt"
```

---

## Task 3: Bounded idea-room loop (`runner.py`)

This is the heart of Phase 1: the `< 4.0 → rerun, max 2 rounds` loop, with the counter in `RunState.retries["idea_room"]` — not the model's head.

**Files:**
- Modify: `scripts/astory_orchestrator/runner.py` (append loop logic)
- Test: `tests/test_astory_orchestrator_runner.py` (add `IdeaRoomLoopTests`)

**TDD.**

- [ ] **Step 1: Write the failing test**

Append to `tests/test_astory_orchestrator_runner.py` (add the import near the top with the others):

```python
from scripts.astory_orchestrator import validate  # noqa: E402  (add to existing imports)


PASS_SCOREBOARD = {
    "minimum_required_overall_score": 4.0,
    "candidates": [{"title": "Win", "overall_score": 4.6, "selection_status": "selected"}],
}
FAIL_SCOREBOARD = {
    "minimum_required_overall_score": 4.0,
    "candidates": [{"title": "Weak", "overall_score": 3.4, "selection_status": "selected"}],
}


class IdeaRoomLoopTests(unittest.TestCase):
    def test_passing_scoreboard_proceeds(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "SCORE_IDEAS"
            result = runner.record_idea_round(tmp, state, PASS_SCOREBOARD)
            self.assertEqual(result["decision"], "proceed")
            self.assertEqual(result["round"], 1)
            self.assertEqual(state.retries["idea_room"], 1)

    def test_first_fail_reruns_second_fail_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "SCORE_IDEAS"

            first = runner.record_idea_round(tmp, state, FAIL_SCOREBOARD)
            self.assertEqual(first["decision"], "rerun")
            self.assertEqual(state.retries["idea_room"], 1)

            second = runner.record_idea_round(tmp, state, FAIL_SCOREBOARD)
            self.assertEqual(second["decision"], "blocked")
            self.assertEqual(state.retries["idea_room"], 2)
            self.assertEqual(state.status, "blocked")

    def test_counter_survives_reload(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "SCORE_IDEAS"
            runner.record_idea_round(tmp, state, FAIL_SCOREBOARD)
            reloaded = run_state_mod.load_state(tmp, state.run_id)
            self.assertEqual(reloaded.retries["idea_room"], 1)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_runner.IdeaRoomLoopTests -v`
Expected: FAIL with `AttributeError: module 'scripts.astory_orchestrator.runner' has no attribute 'record_idea_round'`.

- [ ] **Step 3: Write minimal implementation**

Add the import and append the loop function in `scripts/astory_orchestrator/runner.py`:

```python
# add to the imports at the top of runner.py:
from scripts.astory_orchestrator import validate
```

```python
# append to runner.py:
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

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_runner -v`
Expected: PASS (all runner tests including the loop).

- [ ] **Step 5: Commit**

```bash
cd "/Users/himanshusharma/A Story of Two V2"
git add scripts/astory_orchestrator/runner.py tests/test_astory_orchestrator_runner.py
git commit -m "feat(orchestrator): bounded idea-room loop with counter in RunState"
```

---

## Task 4: CLI leg drivers + end-to-end walk

**Files:**
- Modify: `scripts/astory_orchestrator_cli.py` (add `next`, `idea-round`, `approve`)
- Test: `tests/test_astory_orchestrator_cli.py` (add `IdeaLegWalkTests`)

**TDD** for the new behavior.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_astory_orchestrator_cli.py`:

```python
class IdeaLegWalkTests(unittest.TestCase):
    def _write_scoreboard(self, tmp, overall):
        import json as _json
        path = Path(tmp) / "scoreboard.json"
        path.write_text(
            _json.dumps(
                {
                    "minimum_required_overall_score": 4.0,
                    "candidates": [
                        {"title": "X", "overall_score": overall, "selection_status": "selected"}
                    ],
                }
            )
        )
        return path

    def _set_state(self, tmp, run_id, current_state):
        # init then move current_state by editing the saved file via the CLI's modules
        from scripts.astory_orchestrator import state as run_state_mod
        st = run_state_mod.new_run_state(run_id)
        st.current_state = current_state
        run_state_mod.save_state(tmp, run_id, st)

    def test_idea_round_rerun_then_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._set_state(tmp, "demo", "SCORE_IDEAS")
            board = self._write_scoreboard(tmp, 3.4)

            first = _run("--repo-root", tmp, "idea-round", "--run-id", "demo",
                         "--scoreboard", str(board))
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(json.loads(first.stdout)["decision"], "rerun")

            second = _run("--repo-root", tmp, "idea-round", "--run-id", "demo",
                          "--scoreboard", str(board))
            self.assertEqual(json.loads(second.stdout)["decision"], "blocked")

    def test_idea_round_proceed_then_next_halts_then_approve(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._set_state(tmp, "demo", "SCORE_IDEAS")
            board = self._write_scoreboard(tmp, 4.6)

            proceed = _run("--repo-root", tmp, "idea-round", "--run-id", "demo",
                           "--scoreboard", str(board))
            self.assertEqual(json.loads(proceed.stdout)["decision"], "proceed")

            # Move to HITL by setting state directly, then confirm next halts.
            self._set_state(tmp, "demo", "HITL_IDEA_LOCK")
            nxt = _run("--repo-root", tmp, "next", "--run-id", "demo")
            self.assertEqual(nxt.returncode, 0, nxt.stderr)
            self.assertTrue(json.loads(nxt.stdout)["halt"])

            approve = _run("--repo-root", tmp, "approve", "--run-id", "demo")
            self.assertEqual(approve.returncode, 0, approve.stderr)
            self.assertEqual(json.loads(approve.stdout)["current_state"],
                             "GENERATE_STORY_CONCEPT")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_cli.IdeaLegWalkTests -v`
Expected: FAIL — the `next`, `idea-round`, and `approve` subcommands don't exist (argparse exits non-zero).

- [ ] **Step 3: Write minimal implementation**

In `scripts/astory_orchestrator_cli.py`, add the import for runner and three handlers, and register the subparsers.

Add to imports:

```python
from scripts.astory_orchestrator import runner
```

Add handlers (after `_cmd_status`):

```python
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
    scoreboard = json.loads(Path(args.scoreboard).read_text())
    result = runner.record_idea_round(args.repo_root, state, scoreboard)
    print(json.dumps(result, indent=2))
    return 0


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
    return 0
```

Register subparsers (inside `main()`, alongside the existing ones):

```python
    p_next = sub.add_parser("next", help="Show the next legal action for a run.")
    p_next.add_argument("--run-id", required=True)

    p_idea = sub.add_parser("idea-round", help="Record one idea-room scoring round.")
    p_idea.add_argument("--run-id", required=True)
    p_idea.add_argument("--scoreboard", required=True, help="Path to a final_scoreboard.json.")

    p_approve = sub.add_parser("approve", help="Record a HITL decision at the current gate.")
    p_approve.add_argument("--run-id", required=True)
    p_approve.add_argument("--decision", default="approved")
```

Add to the `handlers` dict:

```python
        "next": _cmd_next,
        "idea-round": _cmd_idea_round,
        "approve": _cmd_approve,
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_cli -v`
Expected: PASS (existing CLI tests + the new leg walk).

- [ ] **Step 5: Commit**

```bash
cd "/Users/himanshusharma/A Story of Two V2"
git add scripts/astory_orchestrator_cli.py tests/test_astory_orchestrator_cli.py
git commit -m "feat(orchestrator): CLI drivers for the idea-room leg (next/idea-round/approve)"
```

---

## Self-Review

**1. Spec coverage:** validators shape-tolerant (Task 1) ✓; advancement + HITL halt (Task 2) ✓; bounded loop with counter in RunState (Task 3) ✓; CLI leg drivers + end-to-end walk (Task 4) ✓; loop reads scoreboard not selected_idea.json ✓.

**2. Placeholder scan:** all code complete; no TBD/"handle edge cases"/"similar to". ✓

**3. Type consistency:** `validate.selected_score`/`meets_threshold`/`threshold`/`MIN_IDEA_SCORE` used identically in Task 1 and Task 3. `runner.advance`/`next_action`/`record_hitl`/`record_idea_round` signatures match across Tasks 2-4 and the CLI. `RunState.retries`/`completed`/`hitl`/`status` match Phase 0. ✓

## Definition of Done (Phase 1)

- Full suite green: `python3 -m unittest` over all `tests/test_*.py`.
- `idea-round` returns `rerun` then `blocked` on two below-threshold rounds; `proceed` on a passing one.
- `next` reports `halt: true` at `HITL_IDEA_LOCK`; `approve` advances to `GENERATE_STORY_CONCEPT`.
- The idea-room retry counter persists in `runs/<id>/state/run_state.json` and survives reload.
- `/astory` SKILL.md and all pre-existing tests unchanged.
