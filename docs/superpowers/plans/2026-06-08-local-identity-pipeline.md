# Local Identity Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a zero-OpenAI-API dry-run proof builder for a local/open-weight A Story of Two identity workflow.

**Architecture:** A small standard-library Python CLI reads a run's selected references, converts them into explicit local image input records with roles and SHA-256 hashes, records the proposed local model stack, and writes proof/report artifacts under the run folder. It refuses prompt-only reference delivery and marks image generation blocked until an actual local ComfyUI or equivalent workflow is present.

**Tech Stack:** Python standard library, `unittest`, local files under `runs/<run_id>/`, no API keys, no downloads, no paid services.

---

### Task 1: Test The Proof Contract

**Files:**
- Create: `tests/test_local_identity_pipeline.py`

- [x] **Step 1: Write failing tests**

Add tests that build a fake run, call `scripts.local_identity_pipeline.build_local_identity_reference_proof`, and assert:
- Aachu and Zuv references have SHA-256 hashes.
- Every reference records an explicit role and `local_binary_input` delivery mode.
- Prompt-only delivery raises `PromptOnlyReferenceError`.
- Missing local workflow marks the proof blocked with `LOCAL_WORKFLOW_MISSING`.

- [x] **Step 2: Run tests to verify RED**

Run: `python3 -m unittest tests.test_local_identity_pipeline -v`

Expected: FAIL because `scripts.local_identity_pipeline` does not exist yet.

### Task 2: Implement The Dry-Run Builder

**Files:**
- Create: `scripts/local_identity_pipeline.py`

- [x] **Step 1: Implement minimal proof builder**

Implement:
- `build_local_identity_reference_proof(repo_root, run_id, workflow_id, workflow_file=None, reference_delivery_mode="local_binary_input")`
- `write_proof_artifacts(repo_root, proof)`
- CLI arguments: `--run-id`, `--workflow-id`, `--workflow-file`, `--dry-run`.

- [x] **Step 2: Run tests to verify GREEN**

Run: `python3 -m unittest tests.test_local_identity_pipeline -v`

Expected: PASS.

### Task 3: Generate The Active Run Proof

**Files:**
- Create: `runs/2026-06-07_17-57_auto/evals/local_identity_reference_proof.json`
- Create: `runs/2026-06-07_17-57_auto/evals/local_identity_reference_proof_report.md`

- [x] **Step 1: Run the dry-run CLI**

Run:

```bash
python3 scripts/local_identity_pipeline.py --run-id 2026-06-07_17-57_auto --workflow-id option_b_sdxl_instantid_pulid_ipadapter --dry-run
```

Expected: exits 0, writes proof/report, records explicit reference hashes, and marks generation blocked until a local workflow file is provided.

### Task 4: Update Run Strategy

**Files:**
- Modify: `runs/2026-06-07_17-57_auto/references-used/reference_delivery_strategy.md`
- Modify: `runs/2026-06-07_17-57_auto/docs/approvals.md`
- Modify: `runs/2026-06-07_17-57_auto/logs/trace.jsonl`

- [x] **Step 1: Record the local fallback**

Append a local/open-weight section explaining that built-in prompt/context generation is blocked, OpenAI API is disallowed, the next dry-run proof artifacts are available, and creator approval is required before downloading or running local models.

### Task 5: Verify

**Files:**
- Check: `scripts/local_identity_pipeline.py`
- Check: `tests/test_local_identity_pipeline.py`
- Check: `runs/2026-06-07_17-57_auto/evals/local_identity_reference_proof.json`
- Check: `runs/2026-06-07_17-57_auto/evals/local_identity_reference_proof_report.md`

- [x] **Step 1: Run verification commands**

Run:

```bash
python3 -m unittest tests.test_local_identity_pipeline -v
python3 -m json.tool runs/2026-06-07_17-57_auto/evals/local_identity_reference_proof.json >/tmp/local_identity_reference_proof.validated.json
python3 -c 'import json, pathlib; [json.loads(line) for line in pathlib.Path("runs/2026-06-07_17-57_auto/logs/trace.jsonl").read_text().splitlines() if line.strip()]'
```

Expected: tests pass; proof JSON is valid; trace JSONL parses line-by-line.

### Task 6: Discover Local Stack

**Files:**
- Modify: `scripts/local_identity_pipeline.py`
- Modify: `tests/test_local_identity_pipeline.py`
- Create: `runs/2026-06-07_17-57_auto/evals/local_identity_stack_discovery.json`
- Create: `runs/2026-06-07_17-57_auto/evals/local_identity_stack_discovery_report.md`

- [x] **Step 1: Write failing discovery tests**

Add tests for missing ComfyUI/workflow/models and for a ready fake local stack.

- [x] **Step 2: Run tests to verify RED**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_local_identity_pipeline -v`

Expected: FAIL because `discover_local_identity_stack` does not exist.

- [x] **Step 3: Implement no-download local discovery**

Add discovery logic for ComfyUI executable/root/server, local workflow file, and SDXL/InstantID/PuLID/IP-Adapter model candidates.

- [x] **Step 4: Run tests to verify GREEN**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_local_identity_pipeline -v`

Expected: PASS.

- [x] **Step 5: Run active discovery**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/local_identity_pipeline.py --run-id 2026-06-07_17-57_auto --workflow-id option_b_sdxl_instantid_pulid_ipadapter --workflow-file runs/2026-06-07_17-57_auto/local-workflows/identity-proof-comfyui.json --discover-local-stack --dry-run
```

Expected: writes discovery JSON/report and marks blocked if ComfyUI, workflow, or local model files are missing.
