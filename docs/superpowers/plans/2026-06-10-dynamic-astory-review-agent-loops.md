# Dynamic A Story Review Agent Loops Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a dynamic A Story review-agent workflow that classifies run types, audits every relevant artifact, validates automatic reference loading, and loops until each run is either pass-ready or explicitly blocked by a real hard gate.

**Architecture:** Extend the existing repo QA script into a workflow-aware review system with small helpers for run classification, prompt discovery, story-contract extraction, reference-context validation, and loop orchestration. Add an explicit Artifact Review Guardian persona and update the A Story skill so every run uses parallel specialist agents for review/build/test lanes before final packaging.

**Tech Stack:** Python standard library, `unittest`, Markdown skill/persona docs, JSON/JSONL run artifacts, existing `scripts/prepare_imagegen_reference_context.py`, existing `scripts/astory_repo_qa.py`.

---

## Parallel Agent Sprint Contract

Every implementation sprint for this feature must use multiple specialist agents unless only one file remains in scope.

Recommended dispatch:
- **Agent A - QA Architecture:** workflow detection, prompt discovery, dynamic checks in `scripts/astory_repo_qa.py`.
- **Agent B - Reference Context:** run-aware reference/style selection in `scripts/prepare_imagegen_reference_context.py`.
- **Agent C - Review Persona And Skill Wiring:** new Artifact Review Guardian persona plus updates to `.agents/skills/astory/SKILL.md` and reference contracts.
- **Agent T - Test Specialist:** unit tests, regression tests, full verification commands, and QA artifact inspection.

Agent rule:
- Agents may read the whole repo, but each agent edits only the files assigned in its task.
- Agent T writes tests before implementation lands and reruns focused tests after each implementation task.
- The coordinator reviews all agent outputs, resolves conflicts, then runs the full verification suite.

## Target File Structure

- Modify: `scripts/astory_repo_qa.py`
  - Responsibility: workflow classification, dynamic run checks, loop orchestration, report writing.
- Modify: `scripts/prepare_imagegen_reference_context.py`
  - Responsibility: build run-aware reference load plans and keep manual attachments disabled.
- Modify: `tests/test_astory_repo_qa.py`
  - Responsibility: workflow classification, all-prompt QA, loop/blocker behavior.
- Modify: `tests/test_imagegen_reference_context.py`
  - Responsibility: run-aware reference selection and load-plan invariants.
- Create: `.agents/skills/astory/personas/review-room/artifact-review-guardian.md`
  - Responsibility: human-readable review-agent role and checklist.
- Modify: `.agents/skills/astory/SKILL.md`
  - Responsibility: require review-room pass, parallel specialist agents, and reference visibility proof before final imagegen.
- Modify: `.agents/skills/astory/references/imagegen-contract.md`
  - Responsibility: document automatic local reference loading and proof loop.
- Modify: `.agents/skills/astory/references/master-prompt.md`
  - Responsibility: reinforce dynamic scene/reference selection and no prompt-only identity.
- Generate during verification:
  - `runs/2026-06-10_22-22_heart-rent/evals/repo_qa_review.json`
  - `runs/2026-06-10_22-22_heart-rent/evals/repo_qa_review.md`
  - `runs/2026-06-10_22-22_heart-rent/evals/repo_qa_review_loop.json`
  - `runs/2026-06-10_22-55_couple-banter/evals/repo_qa_review.json`
  - `runs/2026-06-10_22-55_couple-banter/evals/repo_qa_review.md`
  - `runs/2026-06-10_22-55_couple-banter/evals/repo_qa_review_loop.json`

## Research-Backed Design Constraints

This plan intentionally keeps the implementation small, explicit, and artifact-driven.

Sources consulted on 2026-06-10:
- Anthropic Engineering, "Building effective agents": `https://www.anthropic.com/engineering/building-effective-agents`
- OpenAI Agents SDK guardrails: `https://openai.github.io/openai-agents-python/guardrails/`
- OpenAI Agents SDK tracing: `https://openai.github.io/openai-agents-python/tracing/`
- LangGraph workflows and agents: `https://docs.langchain.com/oss/python/langgraph/workflows-agents`
- Python `unittest` discovery: `https://docs.python.org/3/library/unittest.html#test-discovery`

- Use predefined workflow routing for known run categories instead of a fully autonomous reviewer. Anthropic and LangGraph both distinguish predictable workflows from open-ended agents; this repo has clear run artifact types, so deterministic classification is the safer fit.
- Use parallel specialist agents only where work is genuinely separable: QA architecture, reference context, skill/persona wiring, and tests. This follows the parallelization pattern for independent checks while avoiding unnecessary agent sprawl.
- Use a bounded evaluator-optimizer loop for QA. The loop must stop when the run passes, reaches `max_iterations`, or hits a human/external blocker such as missing reference visibility proof.
- Preserve the existing `DISCOVER_AND_ASSIGN_AGENTS` hard gate. The review loop may add checks, but it must not weaken or bypass the proof that multi-agent availability was checked and agent outputs were recorded.
- Treat `scripts/astory_repo_qa.py` checks as guardrails, not suggestions. Blockers must stop final imagegen/package progression.
- Preserve traceability through JSON/Markdown artifacts. Every loop run should write machine-readable evidence under `runs/<run_id>/evals/`.
- Keep tests as isolated `unittest` cases that can run through discovery with `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`.

---

### Task 1: Test Dynamic Workflow Classification

**Agent:** Agent T - Test Specialist

**Files:**
- Modify: `tests/test_astory_repo_qa.py`

- [ ] **Step 1: Write failing workflow classification tests**

Add tests that assert the QA layer detects the current run types without hard-coded run IDs:

```python
def test_detects_imagegen_story_run_for_heart_rent(self):
    audit = astory_repo_qa.run_repo_qa(REPO_ROOT, "2026-06-10_22-22_heart-rent")

    self.assertEqual(audit["workflow"]["type"], "imagegen_story_run")
    self.assertIn("prompts", audit["workflow"]["evidence"])
    self.assertIn("reference_load_plan", audit["workflow"]["evidence"])


def test_detects_prompt_revision_run_for_couple_banter(self):
    audit = astory_repo_qa.run_repo_qa(REPO_ROOT, "2026-06-10_22-55_couple-banter")

    self.assertIn(
        audit["workflow"]["type"],
        {"prompt_revision_run", "imagegen_story_run"},
    )
    self.assertIn("prompt_files", audit["workflow"])
    self.assertGreaterEqual(len(audit["workflow"]["prompt_files"]), 1)


def test_detects_local_identity_execution_run(self):
    audit = astory_repo_qa.run_repo_qa(REPO_ROOT, "2026-06-07_17-57_auto")

    self.assertEqual(audit["workflow"]["type"], "local_identity_execution_run")
    self.assertIn("local_identity_proof", audit["workflow"]["evidence"])
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_repo_qa -v
```

Expected: FAIL because `audit["workflow"]` does not exist yet.

---

### Task 2: Implement Workflow Detection

**Agent:** Agent A - QA Architecture

**Files:**
- Modify: `scripts/astory_repo_qa.py`

- [ ] **Step 1: Add workflow helper functions**

Add these helpers near the top-level QA helpers:

```python
def _detect_workflow(run_dir: Path) -> dict[str, Any]:
    prompt_files = _prompt_files(run_dir)
    evidence: list[str] = []

    if prompt_files:
        evidence.append("prompts")
    if (run_dir / "evals/imagegen_reference_load_plan.json").exists():
        evidence.append("reference_load_plan")
    if (run_dir / "evals/imagegen_reference_visibility_proof.json").exists():
        evidence.append("reference_visibility_proof")
    if (run_dir / "evals/local_identity_reference_proof.json").exists():
        evidence.append("local_identity_proof")
    if (run_dir / "references-used/selected_references.json").exists():
        evidence.append("selected_references")

    if "local_identity_proof" in evidence and not prompt_files:
        workflow_type = "local_identity_execution_run"
    elif prompt_files and "reference_load_plan" in evidence:
        workflow_type = "imagegen_story_run"
    elif prompt_files:
        workflow_type = "prompt_revision_run"
    elif "selected_references" in evidence:
        workflow_type = "reference_library_run"
    else:
        workflow_type = "unknown_run"

    return {
        "type": workflow_type,
        "evidence": evidence,
        "prompt_files": [_rel(path, run_dir.parent.parent) for path in prompt_files],
    }


def _prompt_files(run_dir: Path) -> list[Path]:
    prompts_dir = run_dir / "prompts"
    if not prompts_dir.exists():
        return []
    return sorted(path for path in prompts_dir.glob("*.txt") if path.is_file())
```

- [ ] **Step 2: Wire workflow into `run_repo_qa`**

Update `run_repo_qa` so it computes workflow once and includes it in the returned audit:

```python
workflow = _detect_workflow(run_dir)
checks = [
    _check_skill_contract(root),
    _check_master_prompt(root),
    _check_required_templates(root),
    _check_reference_manifest(root, run_dir),
    _check_prompt_story_contract(root, run_dir, workflow),
    _check_prompt_reference_gate(root, run_dir, workflow),
    _check_prompt_forbidden_role_reversal(root, run_dir, workflow),
    _check_reference_visibility_proof(root, run_dir),
    _check_image_qa_blocks_final_package(run_dir),
    _check_final_package_not_started(run_dir),
    _check_accepted_candidate_filename_guard(run_dir),
    _check_trace_jsonl_valid(run_dir),
    _check_hitl_order_before_imagegen(run_dir),
    _check_approvals_cover_required_gates(run_dir),
    _check_local_identity_execution_report(run_dir),
]
```

Add `"workflow": workflow` to the returned dictionary.

- [ ] **Step 3: Run workflow tests to verify GREEN**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_repo_qa.AStoryRepoQATests.test_detects_imagegen_story_run_for_heart_rent tests.test_astory_repo_qa.AStoryRepoQATests.test_detects_prompt_revision_run_for_couple_banter tests.test_astory_repo_qa.AStoryRepoQATests.test_detects_local_identity_execution_run -v
```

Expected: PASS.

---

### Task 2A: Preserve Agent Assignment Hard Gate

**Agent:** Agent T - Test Specialist

**Files:**
- Modify: `tests/test_astory_repo_qa.py`
- Modify: `scripts/astory_repo_qa.py`

- [ ] **Step 1: Write regression tests for agent-assignment proof**

Add:

```python
def test_agent_assignment_gate_is_still_required_for_prompt_locked_runs(self):
    audit = astory_repo_qa.run_repo_qa(REPO_ROOT, "2026-06-10_22-22_heart-rent")
    check = audit["checks_by_id"]["agent_assignment_gate"]

    self.assertEqual(check["status"], "pass")
    self.assertIn(
        check["assignment_status"],
        {"actual_multi_agent", "fallback_local_passes_with_limitation_recorded"},
    )
    self.assertTrue(check["assignment_trace_present"])


def test_agent_assignment_gate_is_present_in_every_audit(self):
    audit = astory_repo_qa.run_repo_qa(REPO_ROOT, "2026-06-10_22-55_couple-banter")

    self.assertIn("agent_assignment_gate", audit["checks_by_id"])
```

- [ ] **Step 2: Run tests**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_repo_qa.AStoryRepoQATests.test_agent_assignment_gate_is_still_required_for_prompt_locked_runs tests.test_astory_repo_qa.AStoryRepoQATests.test_agent_assignment_gate_is_present_in_every_audit -v
```

Expected: PASS if the current gate remains wired. If this fails while adding workflow detection, restore `_check_agent_assignment_gate(run_dir)` in `run_repo_qa` before continuing.

- [ ] **Step 3: Preserve the check order**

In `scripts/astory_repo_qa.py`, keep `_check_agent_assignment_gate(run_dir)` in the check list after HITL ordering and before approval/final checks:

```python
_check_trace_jsonl_valid(run_dir),
_check_hitl_order_before_imagegen(run_dir),
_check_agent_assignment_gate(run_dir),
_check_approvals_cover_required_gates(run_dir),
```

Expected: the dynamic workflow refactor does not remove or downgrade `AGENT_ASSIGNMENT_MISSING`.

---

### Task 3: Test All-Prompt Reference Gates

**Agent:** Agent T - Test Specialist

**Files:**
- Modify: `tests/test_astory_repo_qa.py`

- [ ] **Step 1: Write failing tests for all prompt files**

Add tests proving QA checks every prompt in a multi-slide run:

```python
def test_prompt_reference_gate_checks_every_prompt_file(self):
    audit = astory_repo_qa.run_repo_qa(REPO_ROOT, "2026-06-10_22-55_couple-banter")
    check = audit["checks_by_id"]["prompt_reference_gate"]

    self.assertIn("prompt_results", check)
    self.assertGreaterEqual(len(check["prompt_results"]), 4)
    self.assertTrue(all(item["status"] == "pass" for item in check["prompt_results"]))


def test_prompt_role_reversal_checks_every_prompt_file(self):
    audit = astory_repo_qa.run_repo_qa(REPO_ROOT, "2026-06-10_22-55_couple-banter")
    check = audit["checks_by_id"]["prompt_forbidden_role_reversal"]

    self.assertIn("prompt_results", check)
    self.assertGreaterEqual(len(check["prompt_results"]), 4)
    self.assertTrue(all(item["status"] == "pass" for item in check["prompt_results"]))
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_repo_qa.AStoryRepoQATests.test_prompt_reference_gate_checks_every_prompt_file tests.test_astory_repo_qa.AStoryRepoQATests.test_prompt_role_reversal_checks_every_prompt_file -v
```

Expected: FAIL because QA currently reads only `prompts/slide_01_4x5_prompt.txt`.

---

### Task 4: Replace Primary-Prompt Assumption With Prompt Iteration

**Agent:** Agent A - QA Architecture

**Files:**
- Modify: `scripts/astory_repo_qa.py`

- [ ] **Step 1: Add reusable prompt check runner**

Add:

```python
def _check_all_prompts(
    root: Path,
    run_dir: Path,
    check_id: str,
    summary: str,
    evaluator,
) -> dict[str, Any]:
    prompt_paths = _prompt_files(run_dir)
    if not prompt_paths:
        return _prompt_not_applicable(check_id, run_dir)

    prompt_results = []
    for prompt_path in prompt_paths:
        prompt = _read_text(prompt_path)
        evidence = evaluator(prompt)
        prompt_results.append(
            {
                "path": _rel(prompt_path, root),
                "status": "pass" if all(evidence.values()) else "fail",
                "evidence": evidence,
            }
        )

    status = "pass" if all(item["status"] == "pass" for item in prompt_results) else "fail"
    return _check(
        check_id,
        status,
        summary,
        prompt_results=prompt_results,
        severity="blocker",
    )
```

- [ ] **Step 2: Update reference gate check**

Change `_check_prompt_reference_gate` to call `_check_all_prompts`:

```python
def _check_prompt_reference_gate(root: Path, run_dir: Path, workflow: dict[str, Any]) -> dict[str, Any]:
    def evaluator(prompt: str) -> dict[str, bool]:
        lower = prompt.lower()
        return {
            "generation_hard_gate": "generation hard gate" in lower,
            "no_paths_only": "do not generate from text descriptions or file paths alone" in lower,
            "aachu_refs": "aachu face identity" in lower or "aachu_face_identity" in lower,
            "zuv_refs": "zuv face identity" in lower or "zuv_face_identity" in lower,
            "style_refs": "style references" in lower or "style:" in lower,
        }

    return _check_all_prompts(
        root,
        run_dir,
        "prompt_reference_gate",
        "Every prompt preserves the reference-image delivery gate.",
        evaluator,
    )
```

- [ ] **Step 3: Update role-reversal check**

Change `_check_prompt_forbidden_role_reversal` to:

```python
def _check_prompt_forbidden_role_reversal(root: Path, run_dir: Path, workflow: dict[str, Any]) -> dict[str, Any]:
    def evaluator(prompt: str) -> dict[str, bool]:
        lower = prompt.lower()
        return {
            "do_not_reverse_roles": "do not reverse the roles" in lower,
            "do_not_show_zuv_asking": "do not show zuv asking aachu" in lower,
        }

    return _check_all_prompts(
        root,
        run_dir,
        "prompt_forbidden_role_reversal",
        "Every prompt forbids reversing Aachu/Zuv roles.",
        evaluator,
    )
```

- [ ] **Step 4: Run all-prompt tests**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_repo_qa.AStoryRepoQATests.test_prompt_reference_gate_checks_every_prompt_file tests.test_astory_repo_qa.AStoryRepoQATests.test_prompt_role_reversal_checks_every_prompt_file -v
```

Expected: PASS.

---

### Task 5: Test Dynamic Story Contract Instead Of Hard-Coded Heart-Rent

**Agent:** Agent T - Test Specialist

**Files:**
- Modify: `tests/test_astory_repo_qa.py`

- [ ] **Step 1: Write failing tests for run-driven story contracts**

Add:

```python
def test_heart_rent_story_contract_uses_run_contract_metadata(self):
    audit = astory_repo_qa.run_repo_qa(REPO_ROOT, "2026-06-10_22-22_heart-rent")
    check = audit["checks_by_id"]["prompt_story_contract"]

    self.assertEqual(check["status"], "pass")
    self.assertEqual(check["contract_source"], "run_artifacts")
    self.assertIn("required_phrases", check)


def test_couple_banter_story_contract_is_not_heart_rent_specific(self):
    audit = astory_repo_qa.run_repo_qa(REPO_ROOT, "2026-06-10_22-55_couple-banter")
    check = audit["checks_by_id"]["prompt_story_contract"]

    self.assertNotIn("pay rent for living in", json.dumps(check).lower())
    self.assertIn(check["status"], {"pass", "not_applicable"})
```

- [ ] **Step 2: Add `json` import if missing**

At the top of `tests/test_astory_repo_qa.py`, add:

```python
import json
```

- [ ] **Step 3: Run tests to verify RED**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_repo_qa.AStoryRepoQATests.test_heart_rent_story_contract_uses_run_contract_metadata tests.test_astory_repo_qa.AStoryRepoQATests.test_couple_banter_story_contract_is_not_heart_rent_specific -v
```

Expected: FAIL because `_check_prompt_story_contract` is hard-coded.

---

### Task 6: Implement Run-Driven Story Contract

**Agent:** Agent A - QA Architecture

**Files:**
- Modify: `scripts/astory_repo_qa.py`

- [ ] **Step 1: Add story-contract extraction**

Add helpers:

```python
def _contract_phrase_values(value: Any) -> list[str]:
    phrases: list[str] = []
    if isinstance(value, str) and value.strip():
        phrases.append(value.strip())
    elif isinstance(value, list):
        for item in value:
            phrases.extend(_contract_phrase_values(item))
    elif isinstance(value, dict):
        for key in (
            "exact_on_image_text",
            "exact_text",
            "on_image_text",
            "text",
            "one_line_concept",
            "one_line_summary",
            "arc",
        ):
            phrases.extend(_contract_phrase_values(value.get(key)))
        for key in ("selected_ideas", "slides", "beats", "assets"):
            phrases.extend(_contract_phrase_values(value.get(key)))
    return phrases


def _story_contract(run_dir: Path) -> dict[str, Any]:
    selected_idea = _read_json(run_dir / "planning/selected_idea.json")
    story_concept = _read_json(run_dir / "planning/story_concept.json")
    slide_map = _read_json(run_dir / "planning/slide_beat_map.json")

    required_phrases = []
    required_phrases.extend(_contract_phrase_values(selected_idea))
    required_phrases.extend(_contract_phrase_values(story_concept))
    required_phrases.extend(_contract_phrase_values(slide_map))

    deduped = []
    for phrase in required_phrases:
        if phrase not in deduped:
            deduped.append(phrase)

    return {
        "source": "run_artifacts" if deduped else "not_available",
        "required_phrases": deduped,
    }
```

- [ ] **Step 2: Replace hard-coded story check**

Update `_check_prompt_story_contract`:

```python
def _check_prompt_story_contract(root: Path, run_dir: Path, workflow: dict[str, Any]) -> dict[str, Any]:
    contract = _story_contract(run_dir)
    prompt_paths = _prompt_files(run_dir)
    if not prompt_paths:
        return _prompt_not_applicable("prompt_story_contract", run_dir)
    if not contract["required_phrases"]:
        return _check(
            "prompt_story_contract",
            "not_applicable",
            "No run-specific story contract artifact was available for this workflow.",
            contract_source=contract["source"],
            severity="info",
        )

    prompt_text = "\n".join(_read_text(path).lower() for path in prompt_paths)
    required = {
        phrase: phrase.lower() in prompt_text
        for phrase in contract["required_phrases"]
        if len(phrase.split()) <= 18
    }
    status = "pass" if required and all(required.values()) else "fail"
    return _check(
        "prompt_story_contract",
        status,
        "Prompts preserve the run-specific locked story contract.",
        contract_source=contract["source"],
        required_phrases=list(required.keys()),
        evidence=required,
        severity="blocker",
    )
```

- [ ] **Step 3: Run dynamic story tests**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_repo_qa.AStoryRepoQATests.test_heart_rent_story_contract_uses_run_contract_metadata tests.test_astory_repo_qa.AStoryRepoQATests.test_couple_banter_story_contract_is_not_heart_rent_specific -v
```

Expected: PASS. The helper must read generic keys from `planning/selected_idea.json`, `planning/story_concept.json`, and `planning/slide_beat_map.json`; it must not contain literal story text such as `pay rent for living in my heart`.

---

### Task 7: Test Run-Aware Reference Context Selection

**Agent:** Agent T - Test Specialist

**Files:**
- Modify: `tests/test_imagegen_reference_context.py`

- [ ] **Step 1: Add tests for run input images and no manual attachments**

Add:

```python
def test_couple_banter_includes_current_request_images(self):
    context = build_reference_context(REPO_ROOT, "2026-06-10_22-55_couple-banter")
    current_request = context["reference_groups"]["current_request"]

    self.assertGreaterEqual(len(current_request), 1)
    self.assertTrue(
        all(item["role"] == "current_request" for item in current_request)
    )
    self.assertFalse(context["manual_user_attachments_required"])
    self.assertFalse(context["prompt_only_allowed"])


def test_style_references_are_recorded_as_loadable_local_images(self):
    context = build_reference_context(REPO_ROOT, "2026-06-10_22-22_heart-rent")
    style_refs = context["reference_groups"]["style"]

    self.assertGreaterEqual(len(style_refs), 1)
    self.assertTrue(all(item["input_kind"] == "local_image_file" for item in style_refs))
    self.assertTrue(all(item["delivery_mode"] == "view_image_before_imagegen" for item in style_refs))
```

- [ ] **Step 2: Run tests**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_imagegen_reference_context -v
```

Expected: PASS when the current reference context already satisfies the invariant. If this focused test fails, Task 8 is the implementation task that makes it pass.

---

### Task 8: Make Reference Context Run-Aware Without Weakening Identity Gates

**Agent:** Agent B - Reference Context

**Files:**
- Modify: `scripts/prepare_imagegen_reference_context.py`

- [ ] **Step 1: Add style discovery helper**

Add:

```python
def _style_references(repo_root: Path, run_root: Path) -> list[str]:
    selected_refs = _read_json(run_root / "references-used/selected_references.json")
    groups = selected_refs.get("reference_groups") if isinstance(selected_refs, dict) else None
    if isinstance(groups, dict):
        style_paths = [
            ref.get("path")
            for ref in groups.get("style", [])
            if isinstance(ref, dict) and ref.get("path")
        ]
        existing = [path for path in style_paths if (repo_root / path).exists()]
        if existing:
            return existing

    return [path for path in DEFAULT_STYLE_REFERENCES if (repo_root / path).exists()]
```

- [ ] **Step 2: Use discovered style references**

Change grouped paths:

```python
style = _style_references(repo_root, run_root)
grouped_paths = {
    "current_request": current_request,
    "aachu_face_identity": aachu_face,
    "zuv_face_identity": zuv_face,
    "expression_support": expression,
    "together_body_language": together,
    "style": style,
}
```

- [ ] **Step 3: Keep identity guardrails unchanged**

Verify these still exist:

```python
_require_count("Aachu default face anchors", aachu_face, MIN_FACE_ANCHORS_PER_SUBJECT)
_require_count("Zuv default face anchors", zuv_face, MIN_FACE_ANCHORS_PER_SUBJECT)
"manual_user_attachments_required": False
"prompt_only_allowed": False
```

- [ ] **Step 4: Run reference context tests**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_imagegen_reference_context -v
```

Expected: PASS.

---

### Task 9: Add Artifact Review Guardian Persona

**Agent:** Agent C - Review Persona And Skill Wiring

**Files:**
- Create: `.agents/skills/astory/personas/review-room/artifact-review-guardian.md`

- [ ] **Step 1: Create persona file**

Create:

```markdown
# Artifact Review Guardian

You are the final systems reviewer for A Story of Two runs. Your job is to find missing gates, stale references, wrong workflow assumptions, and unsafe shortcuts before image generation or final packaging.

## Review Stance

- Treat the local repo references as source of truth.
- Do not accept prompt-only identity delivery for Aachu or Zuv.
- Do not accept a final imagegen attempt unless each selected local image in `view_image_queue` has been viewed in the current Codex conversation and recorded in `imagegen_reference_visibility_proof.json`.
- Review every prompt file in `runs/<run_id>/prompts/`, not just slide 1.
- Apply checks based on the detected workflow type, not a single story template.
- Mark blocked states clearly with failure codes.

## Required Checks

- Workflow type is detected and evidence is listed.
- Reference manifest exists, resolves locally, and records SHA-256 hashes.
- Aachu and Zuv each have at least four face identity anchors for face-visible generation.
- Expression, together, wardrobe, and place references are supplementary and never substitute for face identity.
- Current-request images are included when present under `runs/<run_id>/input/`.
- HITL approvals appear before the workflow crosses each gate.
- Image QA failures block final package creation.
- Final package cannot use accepted-candidate filenames as proof of final acceptance.

## Output

Return findings in severity order, then list exact files/artifacts that must change before the run can proceed.
```

- [ ] **Step 2: Verify file exists**

Run:

```bash
test -f .agents/skills/astory/personas/review-room/artifact-review-guardian.md
```

Expected: exit 0.

---

### Task 10: Wire Review Room Into The A Story Skill

**Agent:** Agent C - Review Persona And Skill Wiring

**Files:**
- Modify: `.agents/skills/astory/SKILL.md`
- Modify: `.agents/skills/astory/references/imagegen-contract.md`
- Modify: `.agents/skills/astory/references/master-prompt.md`

- [ ] **Step 1: Update skill state machine**

In `.agents/skills/astory/SKILL.md`, preserve `DISCOVER_AND_ASSIGN_AGENTS` and `HITL_PROMPT_LOCK`, then insert review gates around prompt lock, reference loading, and final packaging:

```markdown
19. `PRE_GENERATION_EVAL`
20. `REVIEW_ROOM_QA`
21. `HITL_PROMPT_LOCK`
22. `LOAD_REFERENCE_IMAGES_IN_CONTEXT`
23. `REVIEW_ROOM_IMAGEGEN_BLOCKER_CHECK`
24. `GENERATE_IMAGES_WITH_IMAGEGEN`
25. `IMAGE_QUALITY_EVAL`
26. `REVIEW_ROOM_FINAL_BLOCKER_CHECK`
27. `RETRY_OR_REVISE_IF_NEEDED`
28. `FINAL_QA`
29. `EXPORT_AND_PACKAGE`
30. `WRITE_REPORTS`
31. `COMPLETE_OR_BLOCKED`
```

Do not change earlier states 1-18, especially `DISCOVER_AND_ASSIGN_AGENTS`.

- [ ] **Step 2: Add Review Room section**

Add:

```markdown
### Review Room

Run before final imagegen and again before final package.

Spawn:
- Artifact Review Guardian

Protocol:
1. Detect the run workflow type from local artifacts.
2. Run `scripts/prepare_imagegen_reference_context.py` when prompts are present and imagegen may happen.
3. Run `scripts/astory_repo_qa.py --run-id <run_id>`.
4. Review every blocker before moving forward.
5. Confirm `agent_assignment_gate` passes before prompt lock or imagegen.
6. If imagegen is next, load every `view_image_queue` path with `view_image` and write `evals/imagegen_reference_visibility_proof.json`.
7. Run `scripts/astory_repo_qa.py --run-id <run_id> --loop --max-iterations 2` after reference visibility proof is written and before imagegen.

Artifacts:
- `evals/repo_qa_review.json`
- `evals/repo_qa_review.md`
- `evals/repo_qa_review_loop.json`
- `evals/imagegen_reference_visibility_proof.json`
```

- [ ] **Step 3: Add parallel-agent rule**

Add:

```markdown
For implementation, audit, repair, or QA work touching more than one subsystem, use multiple specialist agents where available: one for implementation, one for review, and one for tests/verification. If no multi-agent tool is available, run the same roles as separate labeled passes.
```

- [ ] **Step 4: Update imagegen contract**

In `.agents/skills/astory/references/imagegen-contract.md`, add:

```markdown
Before final imagegen, the review room must confirm:
- selected references are local, hashed, and role-separated;
- manual user attachment is not required for existing repo references;
- every face-visible prompt has Aachu and Zuv face identity references;
- every file in `view_image_queue` has been loaded through `view_image` in the current conversation.
```

- [ ] **Step 5: Update master prompt**

In `.agents/skills/astory/references/master-prompt.md`, add one operational sentence:

```markdown
Use scene-specific reference groups dynamically: face identity for likeness, expression references for emotion, together references for body language, wardrobe references for clothing, and place references only for setting.
```

- [ ] **Step 6: Run wording scan**

Run:

```bash
rg -n "Review Room|Artifact Review Guardian|view_image_queue|manual user attachment" .agents/skills/astory
```

Expected: shows the new review-room contract and no instruction requiring the user to manually reattach existing repo references.

---

### Task 11: Test QA Loop Orchestration

**Agent:** Agent T - Test Specialist

**Files:**
- Modify: `tests/test_astory_repo_qa.py`

- [ ] **Step 1: Write failing loop tests**

Add:

```python
def test_review_loop_reports_blocked_when_visibility_proof_missing(self):
    result = astory_repo_qa.run_review_loop(
        REPO_ROOT,
        "2026-06-10_22-22_heart-rent",
        max_iterations=2,
        prepare_references=False,
    )

    self.assertEqual(result["status"], "blocked")
    self.assertGreaterEqual(len(result["iterations"]), 1)
    self.assertIn(
        "REFERENCE_VISIBILITY_PROOF_REQUIRED_BEFORE_FINAL_IMAGEGEN",
        json.dumps(result),
    )


def test_review_loop_has_bounded_iterations(self):
    result = astory_repo_qa.run_review_loop(
        REPO_ROOT,
        "2026-06-10_22-22_heart-rent",
        max_iterations=1,
        prepare_references=False,
    )

    self.assertEqual(len(result["iterations"]), 1)
    self.assertEqual(result["max_iterations"], 1)


def test_review_loop_writes_machine_readable_artifact(self):
    astory_repo_qa.run_review_loop(
        REPO_ROOT,
        "2026-06-10_22-22_heart-rent",
        max_iterations=1,
        prepare_references=False,
    )

    path = REPO_ROOT / "runs/2026-06-10_22-22_heart-rent/evals/repo_qa_review_loop.json"
    self.assertTrue(path.exists())
    self.assertEqual(json.loads(path.read_text())["run_id"], "2026-06-10_22-22_heart-rent")
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_repo_qa.AStoryRepoQATests.test_review_loop_reports_blocked_when_visibility_proof_missing tests.test_astory_repo_qa.AStoryRepoQATests.test_review_loop_has_bounded_iterations tests.test_astory_repo_qa.AStoryRepoQATests.test_review_loop_writes_machine_readable_artifact -v
```

Expected: FAIL because `run_review_loop` does not exist yet.

---

### Task 12: Implement Bounded Review Loop

**Agent:** Agent A - QA Architecture

**Files:**
- Modify: `scripts/astory_repo_qa.py`

- [ ] **Step 1: Add `run_review_loop`**

Add:

```python
def run_review_loop(
    repo_root: str | Path,
    run_id: str,
    max_iterations: int = 3,
    prepare_references: bool = True,
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    run_dir = root / "runs" / run_id
    iterations = []

    for iteration in range(1, max_iterations + 1):
        if prepare_references:
            _prepare_references_if_needed(root, run_id)

        audit = write_qa_artifacts(root, run_id)
        blockers = audit.get("blocking_findings", [])
        iterations.append(
            {
                "iteration": iteration,
                "overall_status": audit["overall_status"],
                "blocking_findings": blockers,
            }
        )

        if audit["overall_status"] == "pass":
            result = {
                "schema_version": "1.0",
                "run_id": run_id,
                "status": "pass",
                "max_iterations": max_iterations,
                "iterations": iterations,
            }
            _write_review_loop_artifact(run_dir, result)
            return result

        if _only_human_or_external_blockers(blockers):
            break

    result = {
        "schema_version": "1.0",
        "run_id": run_id,
        "status": "blocked",
        "max_iterations": max_iterations,
        "iterations": iterations,
    }
    _write_review_loop_artifact(run_dir, result)
    return result
```

- [ ] **Step 2: Add preparation helper**

Add:

```python
def _prepare_references_if_needed(root: Path, run_id: str) -> None:
    run_dir = root / "runs" / run_id
    if not _prompt_files(run_dir):
        return
    from scripts.prepare_imagegen_reference_context import (
        build_reference_context,
        write_reference_context,
    )

    context = build_reference_context(root, run_id)
    write_reference_context(root, context)
```

- [ ] **Step 3: Add loop artifact writer**

Add:

```python
def _write_review_loop_artifact(run_dir: Path, result: dict[str, Any]) -> Path:
    evals_dir = run_dir / "evals"
    evals_dir.mkdir(parents=True, exist_ok=True)
    path = evals_dir / "repo_qa_review_loop.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return path
```

- [ ] **Step 4: Add blocker classifier**

Add:

```python
def _only_human_or_external_blockers(blockers: list[dict[str, Any]]) -> bool:
    human_or_external_codes = {
        "REFERENCE_VISIBILITY_PROOF_REQUIRED_BEFORE_FINAL_IMAGEGEN",
        "LOCAL_CPU_EXECUTION_STALLED",
        "LOCAL_WORKFLOW_MISSING",
        "IMAGE_QA_FAILED",
    }
    codes = {
        blocker.get("failure_code")
        for blocker in blockers
        if blocker.get("failure_code")
    }
    return bool(codes) and codes.issubset(human_or_external_codes)
```

- [ ] **Step 5: Add CLI flags**

In `main`, add:

```python
parser.add_argument("--loop", action="store_true", help="Run bounded review loop.")
parser.add_argument("--max-iterations", type=int, default=3)
parser.add_argument(
    "--no-prepare-references",
    action="store_true",
    help="Do not regenerate imagegen reference context before QA.",
)
```

Route:

```python
if args.loop:
    result = run_review_loop(
        Path.cwd(),
        args.run_id,
        max_iterations=args.max_iterations,
        prepare_references=not args.no_prepare_references,
    )
else:
    result = write_qa_artifacts(Path.cwd(), args.run_id)
```

- [ ] **Step 6: Run loop tests**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_repo_qa.AStoryRepoQATests.test_review_loop_reports_blocked_when_visibility_proof_missing tests.test_astory_repo_qa.AStoryRepoQATests.test_review_loop_has_bounded_iterations tests.test_astory_repo_qa.AStoryRepoQATests.test_review_loop_writes_machine_readable_artifact -v
```

Expected: PASS.

---

### Task 13: Run Full Unit Suite

**Agent:** Agent T - Test Specialist

**Files:**
- Check: `tests/test_astory_repo_qa.py`
- Check: `tests/test_imagegen_reference_context.py`
- Check: `scripts/astory_repo_qa.py`
- Check: `scripts/prepare_imagegen_reference_context.py`

- [ ] **Step 1: Run all Python unit tests**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

Expected: all tests pass.

- [ ] **Step 2: Run JSON validation**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m json.tool references/identity/_dossier/identity-dossier.json >/tmp/identity-dossier.validated.json
```

Expected: exits 0.

- [ ] **Step 3: Run stale-path scan**

Run:

```bash
rg -n "config/references|astoryoftwo-analysis|manual.*attach|reattach" references docs .agents runs scripts tests
```

Expected: no stale external reference roots; no instruction that the creator must manually reattach local repo references.

---

### Task 14: Generate Fresh QA Artifacts For Current Runs

**Agent:** Agent A - QA Architecture

**Files:**
- Generate: `runs/2026-06-10_22-22_heart-rent/evals/repo_qa_review.json`
- Generate: `runs/2026-06-10_22-22_heart-rent/evals/repo_qa_review.md`
- Generate: `runs/2026-06-10_22-22_heart-rent/evals/repo_qa_review_loop.json`
- Generate: `runs/2026-06-10_22-55_couple-banter/evals/repo_qa_review.json`
- Generate: `runs/2026-06-10_22-55_couple-banter/evals/repo_qa_review.md`
- Generate: `runs/2026-06-10_22-55_couple-banter/evals/repo_qa_review_loop.json`

- [ ] **Step 1: Run review loop for heart-rent**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/astory_repo_qa.py --run-id 2026-06-10_22-22_heart-rent --loop --max-iterations 2
```

Expected: writes QA artifacts and reports blocked only for legitimate hard gates such as missing visibility proof or failed image QA.

- [ ] **Step 2: Run review loop for couple-banter**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/astory_repo_qa.py --run-id 2026-06-10_22-55_couple-banter --loop --max-iterations 2
```

Expected: writes QA artifacts, validates all prompt files, and does not apply the heart-rent story contract.

- [ ] **Step 3: Validate generated JSON artifacts**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m json.tool runs/2026-06-10_22-22_heart-rent/evals/repo_qa_review.json >/tmp/heart-rent-repo-qa.validated.json
PYTHONDONTWRITEBYTECODE=1 python3 -m json.tool runs/2026-06-10_22-22_heart-rent/evals/repo_qa_review_loop.json >/tmp/heart-rent-repo-qa-loop.validated.json
PYTHONDONTWRITEBYTECODE=1 python3 -m json.tool runs/2026-06-10_22-55_couple-banter/evals/repo_qa_review.json >/tmp/couple-banter-repo-qa.validated.json
PYTHONDONTWRITEBYTECODE=1 python3 -m json.tool runs/2026-06-10_22-55_couple-banter/evals/repo_qa_review_loop.json >/tmp/couple-banter-repo-qa-loop.validated.json
```

Expected: all four commands exit 0.

---

### Task 15: Final Coordinator Review

**Agent:** Coordinator plus Agent T - Test Specialist

**Files:**
- Check: all files changed in this plan

- [ ] **Step 1: Inspect changed files**

Run:

```bash
git diff -- scripts/astory_repo_qa.py scripts/prepare_imagegen_reference_context.py tests/test_astory_repo_qa.py tests/test_imagegen_reference_context.py .agents/skills/astory/SKILL.md .agents/skills/astory/references/imagegen-contract.md .agents/skills/astory/references/master-prompt.md .agents/skills/astory/personas/review-room/artifact-review-guardian.md
```

Expected: changes are limited to dynamic review, reference context, tests, and docs.

- [ ] **Step 2: Run full verification commands again**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python3 -m json.tool references/identity/_dossier/identity-dossier.json >/tmp/identity-dossier.validated.json
rg -n "config/references|astoryoftwo-analysis" references docs .agents runs scripts tests
```

Expected: tests pass, JSON validates, and stale path scan has no unwanted matches.

- [ ] **Step 3: Record final sprint result**

Update the final response with:
- files changed;
- tests run;
- current run statuses;
- remaining blockers, if any;
- whether final imagegen is allowed.

---

## Plan Self-Review

- Spec coverage: covers dynamic workflow types, review agent persona, bounded review loops, all-prompt checking, run-aware references, parallel specialist agents, and test-specialist verification.
- Placeholder scan: no deferred-marker terms or unspecified implementation steps remain.
- Type consistency: workflow dictionary uses `type`, `evidence`, and `prompt_files`; loop result uses `schema_version`, `run_id`, `status`, `max_iterations`, and `iterations`.
- Risk: Task 6 may need to adapt to the exact schemas present in `planning/*.json`; the guardrail is explicit that workers must read the real schema rather than hard-code a new story.
