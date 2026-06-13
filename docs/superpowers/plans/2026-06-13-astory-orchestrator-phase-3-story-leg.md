# A Story Orchestrator — Phase 3 (Story Leg + Verify-Before-Advance) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Drive the second workflow leg — `GENERATE_STORY_CONCEPT → HITL_STORY_LOCK` (spine states 12–17) — as a copilot, by giving the orchestrator a **verify-creative-output-before-advance** capability: per-state artifact validators that the runner enforces before the cursor can move.

**Architecture:** The idea leg validated its output *inside* `record_idea_round`; the story leg's creative states have no such driver, so we add a reusable seam. Three shape-tolerant validators (`validate.py`) cover the story-leg JSON contracts. A `STATE_VERIFIERS` registry in `runner.py` maps a state to a function that reads and validates its declared artifact; `verify_state` combines that with the existing gate-presence check; and `advance_checked` is refactored to enforce via `verify_state` so a state with a registered verifier cannot be left until its artifact is present **and** valid. `HITL_STORY_LOCK` already works through the generic `record_hitl`/`approve` — no new HITL code.

**Tech Stack:** Python 3 stdlib only. Builds on Phases 0–2 (`spine.py`, `state.py`, `validate.py`, `gates.py`, `runner.py`, `astory_orchestrator_cli.py`). Conventions: `unittest`, `from __future__ import annotations`, `json.dumps(indent=2, sort_keys=True)`, argparse CLI, TDD.

---

## Grounding facts (from real artifacts, not memory)

Template vs real-run shapes diverge again — validators must accept both:

| Artifact | Template shape | Real-run shape |
| --- | --- | --- |
| `story_concept.json` | `risk_of_being_generic` (str) | `risks` (list); both have `title`, `one_line_summary`, `setup`, `escalation`, `payoff` |
| `slide_beat_map.json` | `slides[].slide_number`, `visual_scene` | `slides[].slide`, `beat`, `visual_proof`; both have `slide_count` and `exact_on_image_text` |
| `selected_scenes.json` | `slides[].selected_scene_option_id`, `hitl_summary` | `slides[].selected_scene_id`, `scene`, `why_selected`; both have `exact_on_image_text` |

Common denominator the validators key on: **story_concept** needs `title` + a summary + the setup/escalation/payoff arc; **slide_beat_map** needs a non-empty `slides`, `slide_count` consistent with `len(slides)`, and `exact_on_image_text` per slide; **selected_scenes** needs a non-empty `slides`, each with a selected-scene id (`selected_scene_id` OR `selected_scene_option_id`) and `exact_on_image_text`.

Spine facts (33-state, post scene-landing-preview): the story leg is states 12–17 — `GENERATE_STORY_CONCEPT`(12) → `DECIDE_SLIDE_COUNT`(13) → `GENERATE_SLIDE_BEATS`(14) → `GENERATE_SCENE_OPTIONS`(15) → `SELECT_AND_ORDER_SLIDES`(16) → `HITL_STORY_LOCK`(17) → `CREATE_CHARACTER_BIBLE`(18). Produces: state 12 → `planning/story_concept.json`; state 14 → `planning/slide_beat_map.json`; state 16 → `planning/selected_scenes.json` + `debates/story_room/story_debate.md`; state 17 → `docs/approvals.md`. All story-leg states are `kind="creative"` except `HITL_STORY_LOCK` (`hitl`).

## File Structure

| File | Responsibility | New? |
| --- | --- | --- |
| `scripts/astory_orchestrator/validate.py` | Add three shape-tolerant story-leg validators. | Modify |
| `scripts/astory_orchestrator/runner.py` | Add `STATE_VERIFIERS` registry, `_read_run_json`, `verify_state`; refactor `advance_checked` to enforce via `verify_state`. | Modify |
| `scripts/astory_orchestrator_cli.py` | Add `verify` subcommand. | Modify |
| `tests/test_astory_orchestrator_validate.py` | Story-validator tests (both shapes). | Modify |
| `tests/test_astory_orchestrator_runner.py` | `verify_state` + refactored-`advance_checked` enforcement tests. | Modify |
| `tests/test_astory_orchestrator_cli.py` | `verify` subcommand + story-leg walk. | Modify |

## Out of scope for Phase 3 (deferred)

- `DECIDE_SLIDE_COUNT` (markdown) and `GENERATE_SCENE_OPTIONS` (intermediate) get **no** content verifier — they advance as plain creative states. Only the three load-bearing JSON contracts are enforced. Noted, not forgotten.
- The prompt leg, image leg, and `dispatch.py` persona-packet builder — later phases.
- No change to `SKILL.md` or the live `/astory` workflow.

## Current code you will modify (exact, as of commit `f631fb1`)

`scripts/astory_orchestrator/runner.py` `advance_checked` currently reads:

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

Its imports already include `spine`, `gates`, `validate`, `state as run_state_mod`, `RunState`, and `from pathlib import Path`. It does **not** currently import `json`.

---

## Task 1: Story-leg validators (`validate.py`)

**Files:**
- Modify: `scripts/astory_orchestrator/validate.py`
- Test: `tests/test_astory_orchestrator_validate.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_astory_orchestrator_validate.py`, before the `if __name__ == "__main__":` block:

```python
# --- Story leg fixtures (template + real-run shapes) ---

REAL_STORY_CONCEPT = {
    "title": "Heart Rent Notice",
    "one_line_summary": "Aachu jokingly asks Zuv to pay rent for living in her heart.",
    "emotional_hook": "Love has become permanent.",
    "setup": "A cozy interior with negative space.",
    "escalation": "Aachu holds a tiny rent note toward Zuv.",
    "payoff": "Zuv offers a paper heart as payment.",
    "relationship_truth": "Love becomes a home.",
    "risks": ["Do not make Aachu look stern."],
}
TEMPLATE_STORY_CONCEPT = {
    "title": "T",
    "one_line_summary": "summary",
    "emotional_hook": "hook",
    "setup": "setup",
    "escalation": "escalation",
    "payoff": "payoff",
    "relationship_truth": "truth",
    "risk_of_being_generic": "risk",
}

REAL_BEAT_MAP = {
    "slide_count": 1,
    "slides": [
        {"slide": 1, "exact_on_image_text": "pay rent for living in my heart", "beat": "ask"}
    ],
}
TEMPLATE_BEAT_MAP = {
    "slide_count": 1,
    "slides": [
        {"slide_number": 1, "exact_on_image_text": "x", "visual_scene": "scene"}
    ],
}

REAL_SELECTED_SCENES = {
    "slides": [
        {
            "slide": 1,
            "selected_scene_id": "scene_01",
            "exact_on_image_text": "pay rent for living in my heart",
            "scene": "Aachu extends a rent note.",
        }
    ],
}
TEMPLATE_SELECTED_SCENES = {
    "slides": [
        {
            "slide_number": 1,
            "selected_scene_option_id": "1A",
            "exact_on_image_text": "x",
        }
    ],
}


class StoryConceptValidationTests(unittest.TestCase):
    def test_real_and_template_are_valid(self):
        self.assertEqual(validate.validate_story_concept(REAL_STORY_CONCEPT), [])
        self.assertEqual(validate.validate_story_concept(TEMPLATE_STORY_CONCEPT), [])

    def test_non_dict_reports_problem(self):
        self.assertEqual(validate.validate_story_concept(None), ["story_concept_not_object"])

    def test_missing_arc_and_title_reported(self):
        problems = validate.validate_story_concept({"setup": "s"})
        self.assertIn("missing_title", problems)
        self.assertIn("missing_summary", problems)
        self.assertIn("missing_escalation", problems)
        self.assertIn("missing_payoff", problems)


class SlideBeatMapValidationTests(unittest.TestCase):
    def test_real_and_template_are_valid(self):
        self.assertEqual(validate.validate_slide_beat_map(REAL_BEAT_MAP), [])
        self.assertEqual(validate.validate_slide_beat_map(TEMPLATE_BEAT_MAP), [])

    def test_empty_slides_reports_problem(self):
        self.assertIn("no_slides", validate.validate_slide_beat_map({"slides": []}))

    def test_slide_count_mismatch_reported(self):
        bad = {"slide_count": 3, "slides": [{"exact_on_image_text": "x"}]}
        self.assertIn("slide_count_mismatch", validate.validate_slide_beat_map(bad))

    def test_slide_missing_text_reported(self):
        bad = {"slide_count": 1, "slides": [{"slide": 1}]}
        self.assertIn("slide_0_missing_exact_on_image_text",
                      validate.validate_slide_beat_map(bad))


class SelectedScenesValidationTests(unittest.TestCase):
    def test_real_and_template_are_valid(self):
        self.assertEqual(validate.validate_selected_scenes(REAL_SELECTED_SCENES), [])
        self.assertEqual(validate.validate_selected_scenes(TEMPLATE_SELECTED_SCENES), [])

    def test_empty_slides_reports_problem(self):
        self.assertIn("no_slides", validate.validate_selected_scenes({"slides": []}))

    def test_slide_missing_scene_and_text_reported(self):
        bad = {"slides": [{"slide": 1}]}
        problems = validate.validate_selected_scenes(bad)
        self.assertIn("slide_0_missing_selected_scene", problems)
        self.assertIn("slide_0_missing_exact_on_image_text", problems)
```

- [ ] **Step 2: Run to verify they fail**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_validate -v`
Expected: FAIL with `AttributeError: module 'scripts.astory_orchestrator.validate' has no attribute 'validate_story_concept'`.

- [ ] **Step 3: Implement the validators**

Append to `scripts/astory_orchestrator/validate.py`:

```python
def validate_story_concept(data: Any) -> list[str]:
    if not isinstance(data, dict):
        return ["story_concept_not_object"]
    problems: list[str] = []
    if not data.get("title"):
        problems.append("missing_title")
    if not (data.get("one_line_summary") or data.get("emotional_hook")):
        problems.append("missing_summary")
    for beat in ("setup", "escalation", "payoff"):
        if not data.get(beat):
            problems.append(f"missing_{beat}")
    return problems


def validate_slide_beat_map(data: Any) -> list[str]:
    if not isinstance(data, dict):
        return ["slide_beat_map_not_object"]
    slides = data.get("slides")
    if not isinstance(slides, list) or not slides:
        return ["no_slides"]
    problems: list[str] = []
    count = data.get("slide_count")
    if isinstance(count, int) and count != len(slides):
        problems.append("slide_count_mismatch")
    for index, slide in enumerate(slides):
        if not isinstance(slide, dict) or not slide.get("exact_on_image_text"):
            problems.append(f"slide_{index}_missing_exact_on_image_text")
    return problems


def validate_selected_scenes(data: Any) -> list[str]:
    if not isinstance(data, dict):
        return ["selected_scenes_not_object"]
    slides = data.get("slides")
    if not isinstance(slides, list) or not slides:
        return ["no_slides"]
    problems: list[str] = []
    for index, slide in enumerate(slides):
        if not isinstance(slide, dict):
            problems.append(f"slide_{index}_not_object")
            continue
        if not (slide.get("selected_scene_id") or slide.get("selected_scene_option_id")):
            problems.append(f"slide_{index}_missing_selected_scene")
        if not slide.get("exact_on_image_text"):
            problems.append(f"slide_{index}_missing_exact_on_image_text")
    return problems
```

- [ ] **Step 4: Run to verify they pass**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_validate -v`
Expected: PASS (all, old + new).

- [ ] **Step 5: Commit**

```bash
cd "/Users/himanshusharma/A Story of Two V2"
git add scripts/astory_orchestrator/validate.py tests/test_astory_orchestrator_validate.py
git commit -m "feat(orchestrator): shape-tolerant story-leg validators"
```

---

## Task 2: Verifier registry + `verify_state` (`runner.py`)

**Files:**
- Modify: `scripts/astory_orchestrator/runner.py`
- Test: `tests/test_astory_orchestrator_runner.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_astory_orchestrator_runner.py`, before `if __name__ == "__main__":` (the file already imports `json`? it does NOT — but these tests write JSON via `run_state_mod`/files; use the `_touch`-style helper below which writes text):

```python
class VerifyStateTests(unittest.TestCase):
    def _write_json(self, tmp, run_id, rel_path, payload):
        import json as _json
        path = Path(tmp) / "runs" / run_id / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_json.dumps(payload))

    def test_registered_state_ok_when_artifact_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            self._write_json(
                tmp, state.run_id, "planning/story_concept.json",
                {"title": "T", "one_line_summary": "s", "setup": "a",
                 "escalation": "b", "payoff": "c"},
            )
            result = runner.verify_state(tmp, state.run_id, "GENERATE_STORY_CONCEPT")
            self.assertTrue(result["enforced"])
            self.assertTrue(result["ok"])
            self.assertEqual(result["problems"], [])

    def test_registered_state_reports_content_problems(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            self._write_json(tmp, state.run_id, "planning/story_concept.json", {"setup": "a"})
            result = runner.verify_state(tmp, state.run_id, "GENERATE_STORY_CONCEPT")
            self.assertFalse(result["ok"])
            self.assertIn("missing_title", result["problems"])

    def test_registered_state_missing_file_is_not_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            result = runner.verify_state(tmp, state.run_id, "GENERATE_SLIDE_BEATS")
            self.assertFalse(result["ok"])
            self.assertIn("slide_beat_map_not_object", result["problems"])

    def test_unregistered_non_gate_state_is_not_enforced_and_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            result = runner.verify_state(tmp, state.run_id, "DECIDE_SLIDE_COUNT")
            self.assertFalse(result["enforced"])
            self.assertTrue(result["ok"])

    def test_gate_state_presence_still_enforced(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            result = runner.verify_state(tmp, state.run_id, "DISCOVER_AND_ASSIGN_AGENTS")
            self.assertTrue(result["enforced"])
            self.assertFalse(result["ok"])
            self.assertEqual(result["missing"], ["debates/agent_assignment_matrix.md"])
```

- [ ] **Step 2: Run to verify they fail**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_runner.VerifyStateTests -v`
Expected: FAIL with `AttributeError: module 'scripts.astory_orchestrator.runner' has no attribute 'verify_state'`.

- [ ] **Step 3: Implement registry + `verify_state`**

In `scripts/astory_orchestrator/runner.py`:

(a) Add `import json` to the top-of-file imports (alongside the existing `from pathlib import Path`):

```python
import json
```

(b) Append at the end of the file:

```python
def _read_run_json(repo_root: str | Path, run_id: str, rel_path: str):
    path = Path(repo_root).resolve() / "runs" / run_id / rel_path
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return None


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

- [ ] **Step 4: Run to verify they pass**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_runner -v`
Expected: PASS (all, old + new).

- [ ] **Step 5: Commit**

```bash
cd "/Users/himanshusharma/A Story of Two V2"
git add scripts/astory_orchestrator/runner.py tests/test_astory_orchestrator_runner.py
git commit -m "feat(orchestrator): per-state verifier registry and verify_state"
```

---

## Task 3: Enforce via `verify_state` in `advance_checked` (`runner.py`)

**Files:**
- Modify: `scripts/astory_orchestrator/runner.py`
- Test: `tests/test_astory_orchestrator_runner.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_astory_orchestrator_runner.py`, before `if __name__ == "__main__":`:

```python
class AdvanceCheckedVerifiesContentTests(unittest.TestCase):
    def _write_json(self, tmp, run_id, rel_path, payload):
        import json as _json
        path = Path(tmp) / "runs" / run_id / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_json.dumps(payload))

    def test_creative_state_refused_when_artifact_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "GENERATE_STORY_CONCEPT"
            self._write_json(tmp, state.run_id, "planning/story_concept.json", {"setup": "a"})
            result = runner.advance_checked(tmp, state)
            self.assertFalse(result["advanced"])
            self.assertIn("missing_title", result["problems"])
            self.assertEqual(state.current_state, "GENERATE_STORY_CONCEPT")
            self.assertEqual(state.gates["GENERATE_STORY_CONCEPT"], "fail")

    def test_creative_state_advances_when_artifact_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "GENERATE_STORY_CONCEPT"
            self._write_json(
                tmp, state.run_id, "planning/story_concept.json",
                {"title": "T", "one_line_summary": "s", "setup": "a",
                 "escalation": "b", "payoff": "c"},
            )
            result = runner.advance_checked(tmp, state)
            self.assertTrue(result["advanced"])
            self.assertEqual(state.current_state, "DECIDE_SLIDE_COUNT")
            self.assertEqual(state.gates["GENERATE_STORY_CONCEPT"], "pass")

    def test_unverified_creative_state_advances_freely(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _fresh(tmp)
            state.current_state = "DECIDE_SLIDE_COUNT"
            result = runner.advance_checked(tmp, state)
            self.assertTrue(result["advanced"])
            self.assertEqual(state.current_state, "GENERATE_SLIDE_BEATS")
```

Note: the Phase 2 `AdvanceCheckedTests` (gate behavior) must keep passing unchanged.

- [ ] **Step 2: Run to verify they fail**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_runner.AdvanceCheckedVerifiesContentTests -v`
Expected: FAIL — `test_creative_state_refused_when_artifact_invalid` advances anyway (current `advance_checked` only enforces at gates), and `result` has no `"problems"` key.

- [ ] **Step 3: Refactor `advance_checked`**

In `scripts/astory_orchestrator/runner.py`, replace the entire current `advance_checked` function (shown verbatim in "Current code you will modify" above) with:

```python
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
```

- [ ] **Step 4: Run the full runner suite to verify new + old pass**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_runner -v`
Expected: PASS — including Phase 2 `AdvanceCheckedTests` (gate states have no verifier, so `missing` still drives their refusal; their assertions on `result["missing"]`, `result["advanced"]`, and `state.gates[...]` remain satisfied; the added `"problems": []` key does not break them).

- [ ] **Step 5: Run the CLI suite (advance subcommand uses advance_checked)**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_cli -v`
Expected: PASS unchanged.

- [ ] **Step 6: Commit**

```bash
cd "/Users/himanshusharma/A Story of Two V2"
git add scripts/astory_orchestrator/runner.py tests/test_astory_orchestrator_runner.py
git commit -m "feat(orchestrator): advance_checked enforces registered content verifiers"
```

---

## Task 4: CLI `verify` subcommand + story-leg walk

**Files:**
- Modify: `scripts/astory_orchestrator_cli.py`
- Test: `tests/test_astory_orchestrator_cli.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_astory_orchestrator_cli.py`, inside `IdeaLegWalkTests` (it already has `_set_state` and `_run`):

```python
    def _write_run_json(self, tmp, run_id, rel_path, payload):
        path = Path(tmp) / "runs" / run_id / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload))

    def test_verify_reports_ok_for_valid_story_concept(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._set_state(tmp, "demo", "GENERATE_STORY_CONCEPT")
            self._write_run_json(
                tmp, "demo", "planning/story_concept.json",
                {"title": "T", "one_line_summary": "s", "setup": "a",
                 "escalation": "b", "payoff": "c"},
            )
            result = _run("--repo-root", tmp, "verify", "--run-id", "demo")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(result.stdout)["ok"])

    def test_verify_reports_nonzero_for_invalid_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._set_state(tmp, "demo", "GENERATE_STORY_CONCEPT")
            self._write_run_json(tmp, "demo", "planning/story_concept.json", {"setup": "a"})
            result = _run("--repo-root", tmp, "verify", "--run-id", "demo")
            self.assertEqual(result.returncode, 1)
            self.assertIn("missing_title", json.loads(result.stdout)["problems"])

    def test_story_leg_advances_concept_then_blocks_at_story_lock(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._set_state(tmp, "demo", "GENERATE_STORY_CONCEPT")
            self._write_run_json(
                tmp, "demo", "planning/story_concept.json",
                {"title": "T", "one_line_summary": "s", "setup": "a",
                 "escalation": "b", "payoff": "c"},
            )
            adv = _run("--repo-root", tmp, "advance", "--run-id", "demo")
            self.assertEqual(adv.returncode, 0, adv.stderr)
            self.assertTrue(json.loads(adv.stdout)["advanced"])

            # Jump to the story lock and confirm approve advances into the bible.
            self._set_state(tmp, "demo", "HITL_STORY_LOCK")
            approve = _run("--repo-root", tmp, "approve", "--run-id", "demo")
            self.assertEqual(approve.returncode, 0, approve.stderr)
            self.assertEqual(json.loads(approve.stdout)["current_state"],
                             "CREATE_CHARACTER_BIBLE")
```

- [ ] **Step 2: Run to verify they fail**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_cli -v`
Expected: the `verify` tests FAIL (argparse rejects unknown `verify` subcommand, exit 2).

- [ ] **Step 3: Implement the `verify` subcommand**

In `scripts/astory_orchestrator_cli.py`:

(a) Add a handler after `_cmd_advance`:

```python
def _cmd_verify(args: argparse.Namespace) -> int:
    state = run_state_mod.load_state(args.repo_root, args.run_id)
    if state is None:
        print(json.dumps({"status": "no_state", "run_id": args.run_id}, indent=2))
        return 1
    result = runner.verify_state(args.repo_root, state.run_id, state.current_state)
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1
```

(b) Register the subparser in `main()` alongside the others:

```python
    p_verify = sub.add_parser("verify", help="Verify the current state's artifact contract.")
    p_verify.add_argument("--run-id", required=True)
```

(c) Add to the handlers dict:

```python
        "verify": _cmd_verify,
```

- [ ] **Step 4: Run the full orchestrator suite**

Run: `cd "/Users/himanshusharma/A Story of Two V2" && python3 -m unittest tests.test_astory_orchestrator_spine tests.test_astory_orchestrator_state tests.test_astory_orchestrator_validate tests.test_astory_orchestrator_runner tests.test_astory_orchestrator_gates tests.test_astory_orchestrator_cli -v`
Expected: ALL PASS.

- [ ] **Step 5: Commit**

```bash
cd "/Users/himanshusharma/A Story of Two V2"
git add scripts/astory_orchestrator_cli.py tests/test_astory_orchestrator_cli.py
git commit -m "feat(orchestrator): CLI verify subcommand and story-leg walk"
```

---

## Self-Review

**1. Spec coverage:** three story validators (Task 1); verifier registry + `verify_state` combining gate-presence and content (Task 2); `advance_checked` enforces content for registered states while preserving gate behavior (Task 3); CLI `verify` + story-leg walk through `HITL_STORY_LOCK` approve (Task 4). `HITL_STORY_LOCK` needs no new code — generic `record_hitl`/`approve` already advance it (proven by Task 4's walk). Deferred `DECIDE_SLIDE_COUNT`/`GENERATE_SCENE_OPTIONS` content checks are explicitly out of scope.

**2. Placeholder scan:** every step carries complete code and exact commands; no TBD/"handle edge cases"/"similar to Task N".

**3. Type consistency:** `validate.validate_story_concept` / `validate_slide_beat_map` / `validate_selected_scenes` defined in Task 1 are the exact names called by the verifiers in Task 2. `verify_state` return keys (`state`, `enforced`, `ok`, `missing`, `problems`) defined in Task 2 are consumed unchanged by `advance_checked` (Task 3) and the CLI `_cmd_verify` (Task 4). `advance_checked`'s return now always includes `missing` and `problems` — Phase 2 `AdvanceCheckedTests` read only `advanced`/`missing`/`state.gates`, so they remain green.

**Regression guard:** Task 3 changes a Phase-2-tested function. Gate states (`DISCOVER_AND_ASSIGN_AGENTS`) have no verifier, so `verify_state` returns their gate `missing` with empty `problems`; `advance_checked`'s refusal/`gates["…"]="fail"`/`missing` payload is identical to Phase 2. Verified by keeping `AdvanceCheckedTests` in the suite (Task 3 Step 4).

## Definition of Done (Phase 3)

- Full orchestrator suite green (was 77; Phase 3 adds ~18).
- A creative story state cannot be left until its artifact is present and schema-valid; an invalid `story_concept.json` refuses with `problems` including `missing_title`.
- `verify` exits 0 on a valid current-state artifact, 1 on an invalid one.
- Approving `HITL_STORY_LOCK` advances to `CREATE_CHARACTER_BIBLE`.
- Phase 2 gate behavior and all pre-existing orchestrator tests unchanged.
