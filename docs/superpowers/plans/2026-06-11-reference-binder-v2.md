# Reference Binder V2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make A Story imagegen reference loading harder to skip and less confusing by generating deterministic reference binder boards, requiring an ordered binder-first `view_image` queue, and tightening repo QA proof checks before final imagegen.

**Architecture:** Extend `scripts/prepare_imagegen_reference_context.py` so it writes role-separated contact-sheet binder PNGs under `runs/<run_id>/references-used/reference-binder/` and records both raw references and binder packets in the load plan. Update `scripts/astory_repo_qa.py` so visibility proof validation compares the proof to the exact current load plan hash and required queue, blocking imagegen when proof is missing, stale, incomplete, or path-mismatched.

**Tech Stack:** Python standard library, Pillow, unittest, existing A Story repo QA.

---

### Task 1: Binder Packet Manifest

**Files:**
- Modify: `scripts/prepare_imagegen_reference_context.py`
- Test: `tests/test_imagegen_reference_context.py`

- [ ] **Step 1: Write failing tests**
  Add tests asserting `build_reference_context()` includes `raw_reference_queue`, `generation_reference_packet_queue`, `active_view_image_queue`, and a stable `load_plan_sha256`, with binder packet paths and roles.

- [ ] **Step 2: Verify tests fail**
  Run: `python3 -m unittest tests.test_imagegen_reference_context.ImagegenReferenceContextTests`
  Expected: failures for missing binder packet fields.

- [ ] **Step 3: Implement binder packet records**
  Add deterministic binder roles for Aachu identity, Zuv identity, couple body language, style, current request, and expression support. Keep raw queue intact for auditing and make `view_image_queue` binder-first.

- [ ] **Step 4: Verify tests pass**
  Run the same unittest command.

### Task 2: Binder Image Generation

**Files:**
- Modify: `scripts/prepare_imagegen_reference_context.py`
- Test: `tests/test_imagegen_reference_context.py`

- [ ] **Step 1: Write failing tests**
  Add tests using `write_reference_context()` that assert binder PNGs are created, are local files, have hashes, and appear in the generation packet queue.

- [ ] **Step 2: Verify tests fail**
  Run: `python3 -m unittest tests.test_imagegen_reference_context.ImagegenReferenceContextTests`
  Expected: failures because binder files are not yet written.

- [ ] **Step 3: Implement binder renderer**
  Use Pillow to create simple contact sheets with labels and source thumbnails. Write them under `runs/<run_id>/references-used/reference-binder/`.

- [ ] **Step 4: Verify tests pass**
  Run the same unittest command.

### Task 3: Strict Visibility Proof QA

**Files:**
- Modify: `scripts/astory_repo_qa.py`
- Test: `tests/test_astory_repo_qa.py`

- [ ] **Step 1: Write failing tests**
  Add tests for stale `load_plan_sha256`, missing required loaded paths, and proof missing before attempted imagegen. Expected result: `reference_visibility_proof.status == "fail"` and `final_imagegen_allowed == False`.

- [ ] **Step 2: Verify tests fail**
  Run: `python3 -m unittest tests.test_astory_repo_qa.AStoryRepoQATests`
  Expected: failures because current QA accepts weak proof.

- [ ] **Step 3: Implement strict proof comparison**
  Compare proof `load_plan_sha256` and `loaded_paths` against the current load plan `active_view_image_queue` or `view_image_queue`. Fail on mismatch, missing paths, stale proof, or invalid roles.

- [ ] **Step 4: Verify tests pass**
  Run the same unittest command.

### Task 4: Full Verification

**Files:**
- No additional production files.

- [ ] **Step 1: Run focused tests**
  Run: `python3 -m unittest tests.test_imagegen_reference_context tests.test_astory_repo_qa`
  Expected: all tests pass.

- [ ] **Step 2: Run current run reference preparation**
  Run: `python3 scripts/prepare_imagegen_reference_context.py --run-id 2026-06-10_22-55_couple-banter`
  Expected: binder PNGs and updated load plan are written.

- [ ] **Step 3: Inspect worktree**
  Run: `git status --short`
  Expected: only intended files changed plus pre-existing unrelated dirty files.
