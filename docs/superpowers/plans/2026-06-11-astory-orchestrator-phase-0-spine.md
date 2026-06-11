# A Story Orchestrator — Phase 0 (Spine) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Promote the 32-state `/astory` workflow from prose narrated inside the model's context ([SKILL.md:83-118](../../../.agents/skills/astory/SKILL.md#L83-L118)) into inspectable, executable **data** — a state spine and a per-run state file — with **zero change to the live `/astory` workflow**.

**Architecture:** A new pure-data Python package `scripts/astory_orchestrator/` holds (a) `spine.py` — the 32 states as an ordered, validated transition table, and (b) `state.py` — a `RunState` model persisted to `runs/<run_id>/state/run_state.json`. A thin inspect-only CLI (`scripts/astory_orchestrator_cli.py`) exposes `spine`, `validate-spine`, `init`, `status`. A test asserts the spine stays in lock-step with `SKILL.md`. Nothing in this phase drives a run, enforces a gate, or runs a loop — it only makes the plan a first-class object.

**Tech Stack:** Python 3 stdlib only (`dataclasses`, `typing.Literal`, `json`, `argparse`, `pathlib`, `unittest`). No new dependencies. Matches existing `scripts/astory_brain/` conventions (frozen dataclasses, `Literal` enums, functional module helpers, `json.dumps(..., indent=2, sort_keys=True)`).

---

## Why this phase, in one line

Today the model is orchestrator + bookkeeper + creative worker simultaneously; the loop and the gate-state live in its attention. Phase 0 moves the *plan* out of context into a file the runner (built in later phases) will own. This phase ships the plan-as-data and proves it matches the written spec — nothing more.

## File Structure

| File | Responsibility | New? |
| --- | --- | --- |
| `scripts/astory_orchestrator/__init__.py` | Package marker (mirrors `scripts/astory_brain/__init__.py`). | Create |
| `scripts/astory_orchestrator/spine.py` | The 32 states as data: `StateSpec`, `STATES`, helpers, `validate_spine()`. | Create |
| `scripts/astory_orchestrator/state.py` | `RunState` model + `to_dict`/`from_dict`/`new_run_state`/`save_state`/`load_state`. | Create |
| `scripts/astory_orchestrator/README.md` | One-page: what this package is, Phase 0 = inspect-only, not yet wired into `/astory`. | Create |
| `scripts/astory_orchestrator_cli.py` | Inspect-only CLI: `spine`, `validate-spine`, `init`, `status`. | Create |
| `tests/test_astory_orchestrator_spine.py` | Spine structure + `SKILL.md` sync tests. | Create |
| `tests/test_astory_orchestrator_state.py` | `RunState` model + persistence tests. | Create |
| `tests/test_astory_orchestrator_cli.py` | CLI smoke tests via `subprocess`. | Create |

## What Phase 0 deliberately EXCLUDES (so nothing is "missed" by accident)

These are **out of scope** here and belong to later phases — listed explicitly so the boundary is a decision, not an omission:

- **No runner / `while` loop** (Phase 1). The spine is linear `next` pointers only; it does not execute.
- **No branching or retry loops** in the spine (Phase 1+). `RETRY_OR_REVISE_IF_NEEDED` is encoded as a normal linear node for now; real looping lives in the runner.
- **No gate enforcement** (Phase 2). Gate states are *labeled* (`kind="gate"`) but no assertion blocks anything yet.
- **No dispatch packets / model invocation** (Phase 1+).
- **No artifact schema validation** (Phase 1+). `produces` paths are declared as data; nothing validates them against real files yet.
- **No wiring into `SKILL.md` / `/astory`.** The live workflow is untouched. `state.py` writes a *new additive* file under a *new* `state/` subfolder; no existing run artifact is read or rewritten.

---

## Task 1: Spine data model and the 32 states

**Files:**
- Create: `scripts/astory_orchestrator/__init__.py`
- Create: `scripts/astory_orchestrator/spine.py`
- Test: `tests/test_astory_orchestrator_spine.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_astory_orchestrator_spine.py`:

```python
import re
import unittest
from pathlib import Path

from scripts.astory_orchestrator import spine

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = REPO_ROOT / ".agents/skills/astory/SKILL.md"


class SpineStructureTests(unittest.TestCase):
    def test_spine_has_thirty_two_states(self):
        self.assertEqual(len(spine.STATES), 32)

    def test_first_state_is_init_run(self):
        self.assertEqual(spine.first_state(), "INIT_RUN")

    def test_indices_are_contiguous_and_ordered(self):
        self.assertEqual([s.index for s in spine.STATES], list(range(1, 33)))

    def test_by_name_round_trips_and_raises_on_unknown(self):
        self.assertEqual(spine.by_name("SELECT_BEST_IDEA").name, "SELECT_BEST_IDEA")
        with self.assertRaises(KeyError):
            spine.by_name("NOT_A_STATE")

    def test_select_best_idea_produces_selected_idea(self):
        self.assertIn(
            "planning/selected_idea.json",
            spine.by_name("SELECT_BEST_IDEA").produces,
        )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_spine -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scripts.astory_orchestrator'`.

- [ ] **Step 3: Write minimal implementation**

Create `scripts/astory_orchestrator/__init__.py`:

```python
"""A Story orchestrator package (Phase 0: inspect-only spine + run state)."""
```

Create `scripts/astory_orchestrator/spine.py`:

```python
"""The A Story workflow spine: the 32-state machine encoded as data.

This mirrors the State Machine in `.agents/skills/astory/SKILL.md`. A test
(`tests/test_astory_orchestrator_spine.py`) asserts the two stay in sync. This
module is pure data + read helpers; it does not execute a run.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

StateKind = Literal[
    "control",
    "deterministic",
    "creative",
    "gate",
    "hitl",
    "terminal",
]

# Run-relative directories any `produces` path must live under.
RUN_SUBDIRS = (
    "input/",
    "planning/",
    "debates/",
    "prompts/",
    "references-used/",
    "images/",
    "exports/",
    "evals/",
    "logs/",
    "docs/",
    "reports/",
    "state/",
)


@dataclass(frozen=True)
class StateSpec:
    name: str
    index: int
    kind: StateKind
    next: str | None
    produces: tuple[str, ...] = ()


STATES: tuple[StateSpec, ...] = (
    StateSpec("INIT_RUN", 1, "control", "PARSE_CREATIVE_INPUT"),
    StateSpec(
        "PARSE_CREATIVE_INPUT", 2, "control", "DETERMINE_IDEA_MODE",
        ("input/creative_brief.json",),
    ),
    StateSpec("DETERMINE_IDEA_MODE", 3, "control", "REFERENCE_PREFLIGHT"),
    StateSpec(
        "REFERENCE_PREFLIGHT", 4, "deterministic", "MEMORY_RECALL_PREFLIGHT",
        ("planning/identity_preflight.md", "planning/style_preflight.md"),
    ),
    StateSpec(
        "MEMORY_RECALL_PREFLIGHT", 5, "deterministic", "DISCOVER_AND_ASSIGN_AGENTS",
        ("planning/memory_recall.md",),
    ),
    StateSpec(
        "DISCOVER_AND_ASSIGN_AGENTS", 6, "gate", "GENERATE_OR_REFINE_IDEAS",
        ("debates/agent_assignment_matrix.md",),
    ),
    StateSpec(
        "GENERATE_OR_REFINE_IDEAS", 7, "creative", "SCORE_IDEAS",
        (
            "debates/idea_room/agent_01_candidates.json",
            "debates/idea_room/agent_02_candidates.json",
            "debates/idea_room/agent_03_candidates.json",
            "planning/idea_candidates.json",
        ),
    ),
    StateSpec(
        "SCORE_IDEAS", 8, "creative", "SELECT_BEST_IDEA",
        (
            "debates/idea_room/cross_critique.md",
            "debates/idea_room/repair_round.md",
            "debates/idea_room/final_scoreboard.json",
            "evals/idea_engagement_eval.json",
            "evals/idea_engagement_report.md",
        ),
    ),
    StateSpec(
        "SELECT_BEST_IDEA", 9, "creative", "HITL_IDEA_LOCK",
        ("planning/selected_idea.json", "planning/rejected_ideas.md"),
    ),
    StateSpec(
        "HITL_IDEA_LOCK", 10, "hitl", "GENERATE_STORY_CONCEPT",
        ("docs/approvals.md",),
    ),
    StateSpec(
        "GENERATE_STORY_CONCEPT", 11, "creative", "DECIDE_SLIDE_COUNT",
        ("planning/story_concept.json",),
    ),
    StateSpec(
        "DECIDE_SLIDE_COUNT", 12, "creative", "GENERATE_SLIDE_BEATS",
        ("planning/slide_count_decision.md",),
    ),
    StateSpec(
        "GENERATE_SLIDE_BEATS", 13, "creative", "GENERATE_SCENE_OPTIONS",
        ("planning/slide_beat_map.json",),
    ),
    StateSpec(
        "GENERATE_SCENE_OPTIONS", 14, "creative", "SELECT_AND_ORDER_SLIDES",
        ("planning/scene_options.json",),
    ),
    StateSpec(
        "SELECT_AND_ORDER_SLIDES", 15, "creative", "HITL_STORY_LOCK",
        ("planning/selected_scenes.json", "debates/story_room/story_debate.md"),
    ),
    StateSpec(
        "HITL_STORY_LOCK", 16, "hitl", "CREATE_CHARACTER_BIBLE",
        ("docs/approvals.md",),
    ),
    StateSpec(
        "CREATE_CHARACTER_BIBLE", 17, "creative", "CREATE_STYLE_BIBLE",
        ("planning/character_bible.json",),
    ),
    StateSpec(
        "CREATE_STYLE_BIBLE", 18, "creative", "CREATE_PROMPT_PACK",
        ("planning/style_bible.json",),
    ),
    StateSpec(
        "CREATE_PROMPT_PACK", 19, "creative", "PRE_GENERATION_EVAL",
        (
            "prompts/slide_01_4x5_prompt.txt",
            "prompts/negative_prompt.txt",
            "prompts/prompt_generation_report.md",
        ),
    ),
    StateSpec(
        "PRE_GENERATION_EVAL", 20, "gate", "REVIEW_ROOM_QA",
        (
            "evals/pre_generation_eval.json",
            "evals/pre_generation_eval_report.md",
            "debates/prompt_room/prompt_review.md",
        ),
    ),
    StateSpec(
        "REVIEW_ROOM_QA", 21, "gate", "HITL_PROMPT_LOCK",
        ("evals/repo_qa_review.json", "evals/repo_qa_review.md"),
    ),
    StateSpec(
        "HITL_PROMPT_LOCK", 22, "hitl", "LOAD_REFERENCE_IMAGES_IN_CONTEXT",
        ("docs/approvals.md",),
    ),
    StateSpec(
        "LOAD_REFERENCE_IMAGES_IN_CONTEXT", 23, "deterministic",
        "REVIEW_ROOM_IMAGEGEN_BLOCKER_CHECK",
        (
            "references-used/selected_references.json",
            "evals/imagegen_reference_load_plan.json",
            "evals/imagegen_reference_visibility_proof.json",
        ),
    ),
    StateSpec(
        "REVIEW_ROOM_IMAGEGEN_BLOCKER_CHECK", 24, "gate",
        "GENERATE_IMAGES_WITH_IMAGEGEN",
        ("evals/repo_qa_review_loop.json",),
    ),
    StateSpec(
        "GENERATE_IMAGES_WITH_IMAGEGEN", 25, "creative", "IMAGE_QUALITY_EVAL",
        ("images/slide_01_4x5_attempt_01_candidate.png",),
    ),
    StateSpec(
        "IMAGE_QUALITY_EVAL", 26, "gate", "REVIEW_ROOM_FINAL_BLOCKER_CHECK",
        (
            "evals/image_quality_eval.json",
            "evals/image_quality_report.md",
            "debates/image_qa_room/image_qa_debate.md",
        ),
    ),
    StateSpec(
        "REVIEW_ROOM_FINAL_BLOCKER_CHECK", 27, "gate", "RETRY_OR_REVISE_IF_NEEDED",
        ("evals/repo_qa_review.json",),
    ),
    StateSpec("RETRY_OR_REVISE_IF_NEEDED", 28, "control", "FINAL_QA"),
    StateSpec("FINAL_QA", 29, "gate", "EXPORT_AND_PACKAGE"),
    StateSpec(
        "EXPORT_AND_PACKAGE", 30, "deterministic", "WRITE_REPORTS",
        ("exports/slide_01_post_4x5.png",),
    ),
    StateSpec(
        "WRITE_REPORTS", 31, "deterministic", "COMPLETE_OR_BLOCKED",
        ("docs/retro.md",),
    ),
    StateSpec("COMPLETE_OR_BLOCKED", 32, "terminal", None),
)

STATE_NAMES: tuple[str, ...] = tuple(s.name for s in STATES)
_BY_NAME: dict[str, StateSpec] = {s.name: s for s in STATES}
HITL_STATES: tuple[str, ...] = tuple(s.name for s in STATES if s.kind == "hitl")
GATE_STATES: tuple[str, ...] = tuple(s.name for s in STATES if s.kind == "gate")


def by_name(name: str) -> StateSpec:
    try:
        return _BY_NAME[name]
    except KeyError:
        raise KeyError(f"unknown spine state: {name!r}")


def is_state(name: str) -> bool:
    return name in _BY_NAME


def next_state(name: str) -> str | None:
    return by_name(name).next


def is_terminal(name: str) -> bool:
    return by_name(name).next is None


def first_state() -> str:
    return STATES[0].name
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_spine -v`
Expected: PASS (5 tests).

- [ ] **Step 5: Commit**

```bash
cd "/Users/himanshusharma/A Story of Two V2"
git add scripts/astory_orchestrator/__init__.py scripts/astory_orchestrator/spine.py tests/test_astory_orchestrator_spine.py
git commit -m "feat(orchestrator): encode 32-state astory spine as data"
```

---

## Task 2: Spine self-validation (`validate_spine`)

**Files:**
- Modify: `scripts/astory_orchestrator/spine.py` (append `validate_spine`)
- Test: `tests/test_astory_orchestrator_spine.py` (add `SpineIntegrityTests`)

- [ ] **Step 1: Write the failing test**

Append to `tests/test_astory_orchestrator_spine.py`:

```python
class SpineIntegrityTests(unittest.TestCase):
    def test_validate_spine_reports_no_problems(self):
        self.assertEqual(spine.validate_spine(), [])

    def test_single_linear_chain_visits_every_state_once(self):
        visited = []
        cursor = spine.first_state()
        while cursor is not None:
            self.assertNotIn(cursor, visited, "cycle in spine chain")
            visited.append(cursor)
            cursor = spine.next_state(cursor)
        self.assertEqual(set(visited), set(spine.STATE_NAMES))
        self.assertEqual(visited[-1], "COMPLETE_OR_BLOCKED")

    def test_required_hitl_states(self):
        self.assertEqual(
            spine.HITL_STATES,
            ("HITL_IDEA_LOCK", "HITL_STORY_LOCK", "HITL_PROMPT_LOCK"),
        )

    def test_hard_gate_states_present(self):
        for gate in (
            "DISCOVER_AND_ASSIGN_AGENTS",
            "REVIEW_ROOM_QA",
            "REVIEW_ROOM_IMAGEGEN_BLOCKER_CHECK",
            "REVIEW_ROOM_FINAL_BLOCKER_CHECK",
        ):
            self.assertIn(gate, spine.GATE_STATES)

    def test_produces_paths_use_known_run_subdirs(self):
        for spec in spine.STATES:
            for path in spec.produces:
                self.assertTrue(
                    path.startswith(spine.RUN_SUBDIRS),
                    f"{spec.name} produces path outside run dirs: {path}",
                )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_spine.SpineIntegrityTests -v`
Expected: FAIL with `AttributeError: module 'scripts.astory_orchestrator.spine' has no attribute 'validate_spine'`.

- [ ] **Step 3: Write minimal implementation**

Append to `scripts/astory_orchestrator/spine.py`:

```python
def validate_spine() -> list[str]:
    """Return a list of structural problems; empty means the spine is valid."""

    problems: list[str] = []

    for position, spec in enumerate(STATES, start=1):
        if spec.index != position:
            problems.append(
                f"index_out_of_order: {spec.name} has index {spec.index}, "
                f"expected {position}"
            )

    if len(STATE_NAMES) != len(set(STATE_NAMES)):
        problems.append("duplicate_state_names")

    for spec in STATES:
        if spec.next is not None and spec.next not in _BY_NAME:
            problems.append(f"unknown_next: {spec.name} -> {spec.next}")

    terminals = [s.name for s in STATES if s.next is None]
    if terminals != [STATES[-1].name]:
        problems.append(f"terminal_set_invalid: {terminals}")

    visited: list[str] = []
    seen: set[str] = set()
    cursor: str | None = STATES[0].name
    while cursor is not None:
        if cursor in seen:
            problems.append(f"cycle_detected_at: {cursor}")
            break
        seen.add(cursor)
        visited.append(cursor)
        cursor = _BY_NAME[cursor].next if cursor in _BY_NAME else None
    if set(visited) != set(STATE_NAMES):
        missing = sorted(set(STATE_NAMES) - set(visited))
        problems.append(f"chain_does_not_cover_all_states: missing={missing}")

    for required in ("HITL_IDEA_LOCK", "HITL_STORY_LOCK", "HITL_PROMPT_LOCK"):
        if required not in _BY_NAME or _BY_NAME[required].kind != "hitl":
            problems.append(f"missing_hitl_state: {required}")

    for spec in STATES:
        for path in spec.produces:
            if not path.startswith(RUN_SUBDIRS):
                problems.append(
                    f"produces_path_outside_run_dirs: {spec.name} -> {path}"
                )

    return problems
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_spine -v`
Expected: PASS (all spine tests).

- [ ] **Step 5: Commit**

```bash
cd "/Users/himanshusharma/A Story of Two V2"
git add scripts/astory_orchestrator/spine.py tests/test_astory_orchestrator_spine.py
git commit -m "feat(orchestrator): add validate_spine integrity checks"
```

---

## Task 3: Lock the spine to SKILL.md (sync guard test)

This is the highest-value test in the phase: it makes the spine and the written `SKILL.md` State Machine a single source of truth. If either drifts, CI fails.

**Files:**
- Test: `tests/test_astory_orchestrator_spine.py` (add `SpineMatchesSkillTests`)

- [ ] **Step 1: Write the failing test**

Append to `tests/test_astory_orchestrator_spine.py`:

```python
class SpineMatchesSkillTests(unittest.TestCase):
    def test_spine_names_match_skill_state_machine(self):
        text = SKILL_PATH.read_text()
        section = text.split("## State Machine", 1)[1].split("\n## ", 1)[0]
        names = re.findall(r"^\d+\.\s+`([A-Z_]+)`", section, flags=re.MULTILINE)
        self.assertEqual(tuple(names), spine.STATE_NAMES)
```

- [ ] **Step 2: Run test to verify it fails or passes meaningfully**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_spine.SpineMatchesSkillTests -v`
Expected: PASS if the Task 1 ordering matches `SKILL.md:85-118` exactly. If it FAILS, the assertion error prints the two tuples side by side — fix `STATES` in `spine.py` to match `SKILL.md` (do **not** edit `SKILL.md`; it is the source of truth for the names/order).

- [ ] **Step 3: (Only if Step 2 failed) Reconcile**

Correct the offending `StateSpec` entries in `scripts/astory_orchestrator/spine.py` so order and names equal the `SKILL.md` list. Re-run Step 2 until PASS.

- [ ] **Step 4: Commit**

```bash
cd "/Users/himanshusharma/A Story of Two V2"
git add tests/test_astory_orchestrator_spine.py scripts/astory_orchestrator/spine.py
git commit -m "test(orchestrator): assert spine matches SKILL.md state machine"
```

---

## Task 4: `RunState` model (in-memory + serialization)

**Files:**
- Create: `scripts/astory_orchestrator/state.py`
- Test: `tests/test_astory_orchestrator_state.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_astory_orchestrator_state.py`:

```python
import unittest

from scripts.astory_orchestrator import state as run_state_mod


class RunStateModelTests(unittest.TestCase):
    def test_new_run_state_starts_at_init_run(self):
        state = run_state_mod.new_run_state("2026-06-11_demo")
        self.assertEqual(state.current_state, "INIT_RUN")
        self.assertEqual(state.status, "running")
        self.assertEqual(state.completed, [])
        self.assertTrue(state.created_at)
        self.assertEqual(state.created_at, state.updated_at)

    def test_to_dict_from_dict_round_trip(self):
        state = run_state_mod.new_run_state("2026-06-11_demo")
        state.completed = ["INIT_RUN"]
        state.current_state = "PARSE_CREATIVE_INPUT"
        state.gates = {"agent_assignment": "pending"}
        state.retries = {"idea_room": 1}
        restored = run_state_mod.from_dict(run_state_mod.to_dict(state))
        self.assertEqual(restored.current_state, "PARSE_CREATIVE_INPUT")
        self.assertEqual(restored.completed, ["INIT_RUN"])
        self.assertEqual(restored.gates, {"agent_assignment": "pending"})
        self.assertEqual(restored.retries, {"idea_room": 1})

    def test_from_dict_rejects_unknown_current_state(self):
        bad = run_state_mod.to_dict(run_state_mod.new_run_state("x"))
        bad["current_state"] = "NOT_A_STATE"
        with self.assertRaises(ValueError):
            run_state_mod.from_dict(bad)

    def test_from_dict_rejects_invalid_status(self):
        bad = run_state_mod.to_dict(run_state_mod.new_run_state("x"))
        bad["status"] = "exploding"
        with self.assertRaises(ValueError):
            run_state_mod.from_dict(bad)

    def test_from_dict_requires_run_id(self):
        bad = run_state_mod.to_dict(run_state_mod.new_run_state("x"))
        bad["run_id"] = ""
        with self.assertRaises(ValueError):
            run_state_mod.from_dict(bad)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_state -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scripts.astory_orchestrator.state'`.

- [ ] **Step 3: Write minimal implementation**

Create `scripts/astory_orchestrator/state.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_state -v`
Expected: PASS (5 tests).

- [ ] **Step 5: Commit**

```bash
cd "/Users/himanshusharma/A Story of Two V2"
git add scripts/astory_orchestrator/state.py tests/test_astory_orchestrator_state.py
git commit -m "feat(orchestrator): add RunState model with strict from_dict"
```

---

## Task 5: Persist `RunState` to `runs/<run_id>/state/run_state.json`

**Files:**
- Modify: `scripts/astory_orchestrator/state.py` (append `state_path`, `save_state`, `load_state`)
- Test: `tests/test_astory_orchestrator_state.py` (add `RunStatePersistenceTests`)

- [ ] **Step 1: Write the failing test**

Append to `tests/test_astory_orchestrator_state.py`:

```python
import tempfile
from pathlib import Path


class RunStatePersistenceTests(unittest.TestCase):
    def test_save_then_load_round_trips(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_id = "2026-06-11_demo"
            state = run_state_mod.new_run_state(run_id)
            path = run_state_mod.save_state(tmp, run_id, state)
            self.assertTrue(path.exists())
            self.assertEqual(
                path,
                Path(tmp).resolve() / "runs" / run_id / "state" / "run_state.json",
            )
            loaded = run_state_mod.load_state(tmp, run_id)
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded.current_state, "INIT_RUN")
            self.assertEqual(loaded.run_id, run_id)

    def test_save_state_writes_sorted_json_with_trailing_newline(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_id = "2026-06-11_demo"
            path = run_state_mod.save_state(
                tmp, run_id, run_state_mod.new_run_state(run_id)
            )
            text = path.read_text()
            self.assertTrue(text.endswith("\n"))
            # keys are sorted -> "completed" appears before "current_state"
            self.assertLess(text.index('"completed"'), text.index('"current_state"'))

    def test_load_state_returns_none_when_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(run_state_mod.load_state(tmp, "missing_run"))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_state.RunStatePersistenceTests -v`
Expected: FAIL with `AttributeError: module 'scripts.astory_orchestrator.state' has no attribute 'save_state'`.

- [ ] **Step 3: Write minimal implementation**

Append to `scripts/astory_orchestrator/state.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_state -v`
Expected: PASS (all state tests).

- [ ] **Step 5: Commit**

```bash
cd "/Users/himanshusharma/A Story of Two V2"
git add scripts/astory_orchestrator/state.py tests/test_astory_orchestrator_state.py
git commit -m "feat(orchestrator): persist RunState to runs/<id>/state/run_state.json"
```

---

## Task 6: Inspect-only CLI (`spine`, `validate-spine`, `init`, `status`)

**Files:**
- Create: `scripts/astory_orchestrator_cli.py`
- Test: `tests/test_astory_orchestrator_cli.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_astory_orchestrator_cli.py`:

```python
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CLI = REPO_ROOT / "scripts" / "astory_orchestrator_cli.py"


def _run(*args, cwd=REPO_ROOT):
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )


class OrchestratorCliTests(unittest.TestCase):
    def test_spine_command_prints_32_states(self):
        result = _run("spine")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(len(payload), 32)
        self.assertEqual(payload[0]["name"], "INIT_RUN")

    def test_validate_spine_command_ok(self):
        result = _run("validate-spine")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["ok"])

    def test_init_then_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            init = _run("--repo-root", tmp, "init", "--run-id", "demo")
            self.assertEqual(init.returncode, 0, init.stderr)
            self.assertEqual(json.loads(init.stdout)["status"], "created")

            status = _run("--repo-root", tmp, "status", "--run-id", "demo")
            self.assertEqual(status.returncode, 0, status.stderr)
            body = json.loads(status.stdout)
            self.assertEqual(body["current_state"], "INIT_RUN")
            self.assertEqual(body["next_state"], "PARSE_CREATIVE_INPUT")

    def test_init_refuses_existing_without_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(
                _run("--repo-root", tmp, "init", "--run-id", "demo").returncode, 0
            )
            second = _run("--repo-root", tmp, "init", "--run-id", "demo")
            self.assertEqual(second.returncode, 1)
            self.assertEqual(json.loads(second.stdout)["status"], "exists")

    def test_status_without_state_returns_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _run("--repo-root", tmp, "status", "--run-id", "demo")
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)["status"], "no_state")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_cli -v`
Expected: FAIL — the CLI file does not exist yet, so every `subprocess` call returns non-zero with a "can't open file" error and assertions fail.

- [ ] **Step 3: Write minimal implementation**

Create `scripts/astory_orchestrator_cli.py`:

```python
#!/usr/bin/env python3
"""A Story orchestrator CLI (Phase 0: inspect-only).

Subcommands:
  spine           Print the 32-state spine as JSON.
  validate-spine  Print structural problems; exit 1 if any.
  init            Create runs/<run_id>/state/run_state.json (idempotent unless --force).
  status          Print current_state / status / next_state for a run.

This does not run the workflow, dispatch agents, or enforce gates.
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


def main() -> int:
    parser = argparse.ArgumentParser(description="A Story orchestrator (Phase 0 inspect).")
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("spine", help="Print the 32-state spine as JSON.")
    sub.add_parser("validate-spine", help="Validate the spine; exit 1 on problems.")

    p_init = sub.add_parser("init", help="Create a run's state file.")
    p_init.add_argument("--run-id", required=True)
    p_init.add_argument("--force", action="store_true", help="Overwrite existing state.")

    p_status = sub.add_parser("status", help="Show a run's current state.")
    p_status.add_argument("--run-id", required=True)

    args = parser.parse_args()
    handlers = {
        "spine": _cmd_spine,
        "validate-spine": _cmd_validate_spine,
        "init": _cmd_init,
        "status": _cmd_status,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_cli -v`
Expected: PASS (5 tests).

- [ ] **Step 5: Commit**

```bash
cd "/Users/himanshusharma/A Story of Two V2"
git add scripts/astory_orchestrator_cli.py tests/test_astory_orchestrator_cli.py
git commit -m "feat(orchestrator): add inspect-only spine/state CLI"
```

---

## Task 7: Package README + full-suite regression proof

**Files:**
- Create: `scripts/astory_orchestrator/README.md`

- [ ] **Step 1: Write the README**

Create `scripts/astory_orchestrator/README.md`:

```markdown
# astory_orchestrator (Phase 0 — inspect-only)

Encodes the `/astory` 32-state workflow as **data** so the plan stops living in
the model's context.

- `spine.py` — the 32 states as an ordered, validated transition table. Kept in
  sync with `.agents/skills/astory/SKILL.md` by
  `tests/test_astory_orchestrator_spine.py`.
- `state.py` — `RunState`, persisted to `runs/<run_id>/state/run_state.json`.
- `../astory_orchestrator_cli.py` — `spine`, `validate-spine`, `init`, `status`.

## Status

Phase 0 is **inspect-only**. It does NOT run the workflow, dispatch agents,
enforce gates, or run loops. The live `/astory` skill is unchanged. Later phases
add the runner (loops + HITL halt/resume), gate enforcement, and dispatch packets.

## Try it

```bash
python3 scripts/astory_orchestrator_cli.py spine
python3 scripts/astory_orchestrator_cli.py validate-spine
```
```

- [ ] **Step 2: Run the FULL test suite (prove zero regressions)**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest discover -s tests -t . -v`
Expected: PASS — all pre-existing tests (the ~90 already in the repo) plus the new orchestrator tests. **If any pre-existing test changed behavior, stop — Phase 0 must be additive.**

- [ ] **Step 3: Sanity-check the CLI by hand**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 scripts/astory_orchestrator_cli.py validate-spine`
Expected: `{"ok": true, "problems": []}`.

- [ ] **Step 4: Commit**

```bash
cd "/Users/himanshusharma/A Story of Two V2"
git add scripts/astory_orchestrator/README.md
git commit -m "docs(orchestrator): document Phase 0 inspect-only spine package"
```

---

## Self-Review

**1. Spec coverage**
- "32-state spine as data" → Task 1 (`STATES`) ✓
- "validated" → Task 2 (`validate_spine`) ✓
- "kept in sync with SKILL.md" → Task 3 (sync guard) ✓
- "per-run state file, real trace shape (state/status/artifacts)" → Tasks 4-5 (`RunState`: `current_state`, `status`, `artifacts`) ✓
- "inspect-only, zero workflow change" → CLI is read/create-only; `state/` is a new additive folder; `SKILL.md` untouched ✓
- "regression-proof" → Task 7 Step 2 full-suite run ✓

**2. Placeholder scan**
- No "TBD"/"handle edge cases"/"similar to Task N". Every code step shows complete code. ✓

**3. Type consistency**
- `StateSpec(name, index, kind, next, produces)` used identically in Tasks 1-2 and the CLI. ✓
- `RunState` field names (`current_state`, `completed`, `gates`, `retries`, `hitl`, `artifacts`) identical across Tasks 4-6. ✓
- Helper names stable: `first_state`, `is_state`, `next_state`, `by_name`, `validate_spine`, `new_run_state`, `to_dict`, `from_dict`, `state_path`, `save_state`, `load_state`. ✓
- CLI imports `spine` and `state as run_state_mod` — matches module filenames. ✓

## Definition of Done (Phase 0)

- `python3 scripts/astory_orchestrator_cli.py validate-spine` → `{"ok": true, "problems": []}`.
- `python3 -m unittest discover -s tests -t .` → all green (pre-existing + new).
- `spine` ↔ `SKILL.md` sync test passes (drift now fails CI).
- No existing run artifact, `SKILL.md`, or `/astory` behavior changed.

## Then: Phase 1 preview (do NOT start here)

With the spine and `RunState` in place, Phase 1 wires the harness as a **copilot** for one leg — idea room → `HITL_IDEA_LOCK` (states 7-10): the harness owns the `<4.0 → rerun, max 2` loop via `RunState.retries`, validates `final_scoreboard.json` + `selected_idea.json`, advances `current_state`, and halts at the HITL gate. That is where the loop physically leaves the model's head.
