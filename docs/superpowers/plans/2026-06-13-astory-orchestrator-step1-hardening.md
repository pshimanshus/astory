# A Story Orchestrator — Step 1 Hardening (Spine-Derived Verifiers + Dead-Code Removal)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tidy the verify-before-advance abstraction so it scales to the prompt/image legs — verify **all** of a state's declared artifacts (not just one), guard the validator registry against spine drift, and remove the now-orphaned `gates.check_gate`.

**Architecture:** Replace the three hardcoded `_verify_*` wrappers + `STATE_VERIFIERS` with a `STATE_CONTENT_VALIDATORS` registry mapping `state -> {run-relative artifact path: validator}`. `verify_state` enforces presence of **all** declared `produces` (uniformly, via `gates.missing_artifacts`, for any enforced state) and runs content validators on the registered paths. A test asserts every registry path is declared in the spine, killing the duplication-drift risk. Separately, delete `gates.check_gate` (dead in production after the Phase 3 refactor), preserving its multi-artifact coverage as a `missing_artifacts` test.

**Tech Stack:** Python 3 stdlib only. Builds on Phases 0–3. Conventions: `unittest`, `from __future__ import annotations`, TDD.

---

## Why (traceability to the Phase 3 final review)

1. "Verifier artifact paths are hardcoded in runner.py, duplicating the spine's produces" → Task 1 (registry keyed by path + drift-guard test).
2. "SELECT_AND_ORDER_SLIDES produces two artifacts but only one is verified" (`debates/story_room/story_debate.md` declared but unverifiable) → Task 1 (uniform all-produces presence).
3. "`gates.check_gate` is now orphaned in production" → Task 2 (remove it).

## File Structure

| File | Responsibility | Change |
| --- | --- | --- |
| `scripts/astory_orchestrator/runner.py` | Replace `_verify_*`/`STATE_VERIFIERS` with `STATE_CONTENT_VALIDATORS`; `verify_state` enforces all-produces presence + path-keyed content validation. | Modify |
| `scripts/astory_orchestrator/gates.py` | Remove `check_gate` (and now-unused `Any` import); keep `missing_artifacts`. | Modify |
| `tests/test_astory_orchestrator_runner.py` | Add drift-guard + all-produces verification tests. | Modify |
| `tests/test_astory_orchestrator_gates.py` | Remove `CheckGateTests`; preserve multi-artifact coverage as a `missing_artifacts` test. | Modify |

## Verified preconditions (grepped)

- `STATE_VERIFIERS`, `_verify_story_concept/_verify_slide_beat_map/_verify_selected_scenes` are referenced ONLY inside `runner.py`.
- `gates.check_gate` is referenced ONLY in `gates.py` and `tests/test_astory_orchestrator_gates.py` (no production caller).
- `gates.missing_artifacts` stays — used by `verify_state`.
- `advance_checked` consumes `verify_state`'s dict (`enforced`/`ok`/`missing`/`problems`) and is UNCHANGED by this work.
- SELECT_AND_ORDER_SLIDES `produces` = `("planning/selected_scenes.json", "debates/story_room/story_debate.md")`.

## Current code being replaced (runner.py, exact)

```python
def _verify_story_concept(repo_root: str | Path, run_id: str) -> list[str]:
    return validate.validate_story_concept(
        _read_run_json(repo_root, run_id, "planning/story_concept.json")
    )


def _verify_slide_beat_map(repo_root: str | Path, run_id: str) -> list[str]:
    return validate.validate_slide_beat_map(
        _read_run_json(repo_root, run_id, "planning/slide_beat_map.json")
    )


def _verify_selected_scenes(repo_root: str | Path, run_id: str) -> list[str]:
    return validate.validate_selected_scenes(
        _read_run_json(repo_root, run_id, "planning/selected_scenes.json")
    )


# state name -> content verifier returning a list of problem codes.
STATE_VERIFIERS = {
    "GENERATE_STORY_CONCEPT": _verify_story_concept,
    "GENERATE_SLIDE_BEATS": _verify_slide_beat_map,
    "SELECT_AND_ORDER_SLIDES": _verify_selected_scenes,
}


def verify_state(repo_root: str | Path, run_id: str, state_name: str) -> dict:
    """Report whether a state's contract is satisfied.

    Combines gate-presence (for `kind="gate"` states) with a registered content
    verifier (for states in STATE_VERIFIERS). `enforced` is False for plain
    states with neither, which therefore advance freely.
    """

    spec = spine.by_name(state_name)
    missing = (
        gates.missing_artifacts(repo_root, run_id, state_name)
        if spec.kind == "gate"
        else []
    )
    verifier = STATE_VERIFIERS.get(state_name)
    problems = verifier(repo_root, run_id) if verifier else []
    enforced = spec.kind == "gate" or verifier is not None
    return {
        "state": spec.name,
        "enforced": enforced,
        "ok": not missing and not problems,
        "missing": missing,
        "problems": problems,
    }
```

`_read_run_json` (directly above the block) stays unchanged.

---

## Task 1: Spine-derived, all-produces verifier registry

**Files:**
- Modify: `scripts/astory_orchestrator/runner.py`
- Test: `tests/test_astory_orchestrator_runner.py`

- [ ] **Step 1: Write the failing tests**

In `tests/test_astory_orchestrator_runner.py`, ensure `spine` is importable by adding to the imports at the top (after `from scripts.astory_orchestrator import validate  # noqa: F401`):

```python
from scripts.astory_orchestrator import spine
```

Then append a new test class before `if __name__ == "__main__":`:

```python
class RegistryAndAllProducesTests(unittest.TestCase):
    def _write_json(self, tmp, run_id, rel_path, payload):
        import json as _json
        path = Path(tmp) / "runs" / run_id / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_json.dumps(payload))

    def _touch(self, tmp, run_id, rel_path):
        path = Path(tmp) / "runs" / run_id / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x")

    def test_every_registered_validator_path_is_declared_in_spine(self):
        for state_name, validators in runner.STATE_CONTENT_VALIDATORS.items():
            produces = spine.by_name(state_name).produces
            for rel_path in validators:
                self.assertIn(
                    rel_path, produces,
                    f"{state_name} validator path {rel_path!r} not in spine produces",
                )

    def test_select_and_order_slides_requires_all_produces(self):
        # selected_scenes.json present + content-valid, but story_debate.md absent.
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            self._write_json(
                tmp, state.run_id, "planning/selected_scenes.json",
                {"slides": [{"selected_scene_id": "s1", "exact_on_image_text": "x"}]},
            )
            result = runner.verify_state(tmp, state.run_id, "SELECT_AND_ORDER_SLIDES")
            self.assertFalse(result["ok"])
            self.assertEqual(result["problems"], [])
            self.assertIn("debates/story_room/story_debate.md", result["missing"])

    def test_select_and_order_slides_ok_when_all_produces_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            self._write_json(
                tmp, state.run_id, "planning/selected_scenes.json",
                {"slides": [{"selected_scene_id": "s1", "exact_on_image_text": "x"}]},
            )
            self._touch(tmp, state.run_id, "debates/story_room/story_debate.md")
            result = runner.verify_state(tmp, state.run_id, "SELECT_AND_ORDER_SLIDES")
            self.assertTrue(result["ok"])
            self.assertEqual(result["missing"], [])

    def test_registered_state_missing_required_artifact_lists_it(self):
        # story concept file absent -> present in missing AND content not_object problem.
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            result = runner.verify_state(tmp, state.run_id, "GENERATE_STORY_CONCEPT")
            self.assertFalse(result["ok"])
            self.assertIn("planning/story_concept.json", result["missing"])
            self.assertIn("story_concept_not_object", result["problems"])
```

- [ ] **Step 2: Run to verify they fail**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_runner.RegistryAndAllProducesTests -v`
Expected: FAIL — `AttributeError: module 'scripts.astory_orchestrator.runner' has no attribute 'STATE_CONTENT_VALIDATORS'`, and the SELECT_AND_ORDER_SLIDES all-produces tests fail because the current `verify_state` does not check presence for creative states.

- [ ] **Step 3: Replace the registry + `verify_state` in `runner.py`**

Delete the three `_verify_story_concept`/`_verify_slide_beat_map`/`_verify_selected_scenes` functions and the `STATE_VERIFIERS` dict (shown verbatim in "Current code being replaced" above). Keep `_read_run_json`. In their place put:

```python
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
```

- [ ] **Step 4: Run the full runner suite**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_runner -v`
Expected: PASS — the new `RegistryAndAllProducesTests` plus all pre-existing runner tests. NOTE the pre-existing `VerifyStateTests` stay green: GENERATE_STORY_CONCEPT/GENERATE_SLIDE_BEATS each declare a single `produces`, so all-produces presence collapses to the single-file behavior those tests already assert; the corrupt-JSON test still sees `missing=[]` (file present) with a `*_not_object` problem.

- [ ] **Step 5: Commit**

```bash
cd "/Users/himanshusharma/A Story of Two V2"
git add scripts/astory_orchestrator/runner.py tests/test_astory_orchestrator_runner.py
git commit -m "refactor(orchestrator): spine-checked registry, verify all declared produces"
```

---

## Task 2: Remove orphaned `gates.check_gate`

**Files:**
- Modify: `scripts/astory_orchestrator/gates.py`
- Test: `tests/test_astory_orchestrator_gates.py`

- [ ] **Step 1: Preserve the valuable coverage as a `missing_artifacts` test, then delete `CheckGateTests`**

In `tests/test_astory_orchestrator_gates.py`: delete the entire `CheckGateTests` class (lines 40–82, the `class CheckGateTests` block). Add this multi-artifact test to the existing `MissingArtifactsTests` class (it preserves the PRE_GENERATION_EVAL subset coverage via the surviving API):

```python
    def test_multi_artifact_state_lists_only_missing_subset(self):
        with tempfile.TemporaryDirectory() as tmp:
            _touch(tmp, "demo", "evals/pre_generation_eval.json")
            self.assertEqual(
                sorted(gates.missing_artifacts(tmp, "demo", "PRE_GENERATION_EVAL")),
                [
                    "debates/prompt_room/prompt_review.md",
                    "evals/pre_generation_eval_report.md",
                ],
            )
```

- [ ] **Step 2: Run to verify the test references no longer resolve**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_gates -v`
Expected: PASS for the surviving `MissingArtifactsTests` (including the new multi-artifact test). `CheckGateTests` is gone, so it is no longer collected. (`gates.check_gate` still exists at this point, but nothing references it.)

- [ ] **Step 3: Remove `check_gate` and the now-unused import from `gates.py`**

In `scripts/astory_orchestrator/gates.py`: delete the entire `check_gate` function (lines 25–39). Remove the now-unused `from typing import Any` import (line 12). Update the module docstring's stale "Phase 2 enforces presence only" note to reflect that content checks now live in the runner. The file becomes:

```python
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
```

- [ ] **Step 4: Run the gates suite, then the full orchestrator suite**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_gates -v`
Expected: PASS.

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_spine tests.test_astory_orchestrator_state tests.test_astory_orchestrator_validate tests.test_astory_orchestrator_runner tests.test_astory_orchestrator_gates tests.test_astory_orchestrator_cli`
Expected: ALL PASS (the CLI `advance`/`verify` paths route through `verify_state`/`missing_artifacts`, never `check_gate`).

- [ ] **Step 5: Commit**

```bash
cd "/Users/himanshusharma/A Story of Two V2"
git add scripts/astory_orchestrator/gates.py tests/test_astory_orchestrator_gates.py
git commit -m "refactor(orchestrator): remove orphaned gates.check_gate"
```

---

## Self-Review

**1. Spec coverage:** finding #1 (hardcoded paths / drift) → Task 1 registry keyed by path + `test_every_registered_validator_path_is_declared_in_spine`; finding #2 (only one of two produces verified) → Task 1 uniform `missing_artifacts` for enforced states + the two SELECT_AND_ORDER_SLIDES tests; finding #3 (orphaned `check_gate`) → Task 2 removal with preserved multi-artifact coverage.

**2. Placeholder scan:** every step has complete code and exact commands; no TBD/"handle edge cases"/"similar to".

**3. Type consistency:** `verify_state` keeps its exact return shape (`state`/`enforced`/`ok`/`missing`/`problems`), so `advance_checked` and the CLI are untouched and their tests stay green. `STATE_CONTENT_VALIDATORS` is the only new public symbol; it is referenced by the Task 1 drift-guard test and `verify_state`. `gates.missing_artifacts` signature unchanged.

**Regression guard:** pre-existing `VerifyStateTests` and `AdvanceCheckedVerifiesContentTests` use single-produces states (GENERATE_STORY_CONCEPT / GENERATE_SLIDE_BEATS) or non-registered/gate states, so the all-produces change is behavior-identical for them; only SELECT_AND_ORDER_SLIDES (two produces, previously under-verified) changes, and only the new tests exercise it.

## Definition of Done (Step 1 hardening)

- Full orchestrator suite green (was 102; net change: +4 runner tests, −5 `CheckGateTests` +1 `missing_artifacts` test).
- `runner.STATE_CONTENT_VALIDATORS` keyed by run-relative path; a test fails if any key drifts from the spine's `produces`.
- `SELECT_AND_ORDER_SLIDES` refuses until BOTH `selected_scenes.json` and `story_debate.md` exist.
- `gates.check_gate` deleted; no production or test references remain; `missing_artifacts` retains multi-artifact coverage.
- `advance_checked`, the CLI, and `SKILL.md` unchanged.
