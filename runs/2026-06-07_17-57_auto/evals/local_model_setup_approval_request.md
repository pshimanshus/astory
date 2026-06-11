# Local Model Setup Status

Run: `2026-06-07_17-57_auto`

Status: `execution_blocked_cpu_stalled`

## Why This Is Needed

The built-in prompt/context imagegen path failed creator face-match review. This run now uses a zero-OpenAI-API local path, but final or proof generation remains blocked until every required local component is present.

Setup blockers resolved:

- `LOCAL_WORKFLOW_MISSING`: resolved by `runs/2026-06-07_17-57_auto/local-workflows/identity-proof-comfyui.json`
- `LOCAL_MODELS_MISSING`: resolved for the minimum InstantID proof path by downloading `sd_xl_base_1.0.safetensors`

Current execution blocker:

- `LOCAL_CPU_EXECUTION_STALLED`

## Proposed First Stack

Use Option B first:

`SDXL + InstantID via ComfyUI`, with PuLID/IP-Adapter as optional add-ons if the first identity proof fails.

Reason: this is the most targeted zero-shot path for face identity because Aachu and Zuv face crops can condition identity separately from style references.

## Completed Local Setup

- OpenAI API: none
- Paid cloud API: none
- ComfyUI cloned to `runs/2026-06-07_17-57_auto/local-tools/ComfyUI`
- Virtualenv created at `runs/2026-06-07_17-57_auto/local-tools/ComfyUI/.venv`
- ComfyUI requirements installed locally
- Custom nodes cloned: `ComfyUI_IPAdapter_plus`, `ComfyUI_InstantID`, `PuLID_ComfyUI`
- Custom node dependencies installed
- ComfyUI CPU quick-test passed
- SDXL base checkpoint downloaded and hashed
- InstantID adapter downloaded and hashed
- InstantID ControlNet downloaded and hashed
- AntelopeV2 InsightFace files downloaded, extracted, and hashed
- Non-final identity proof workflow created and hashed
- Workflow input images copied into ComfyUI input and hashed

Model manifest:

- `runs/2026-06-07_17-57_auto/evals/local_model_requirements.json`

Refreshed discovery:

- `runs/2026-06-07_17-57_auto/evals/local_identity_stack_discovery.json`
- `runs/2026-06-07_17-57_auto/evals/local_identity_stack_discovery_report.md`

## Guardrails

- Do not generate carousel slides during setup.
- Do not generate final Aachu/Zuv artwork during setup.
- First model output must be one non-final identity proof image only.
- Identity proof image must have Aachu and Zuv side-by-side, face-forward enough to judge identity.
- No story text, no brandmark, no shawl.
- If creator rejects identity proof, stop and do not generate slides.

## Execution Attempt Result

Two ComfyUI prompts were queued and interrupted because they remained at `0` sampler steps:

- `75b8aae3-f73c-45bd-8172-035377c0ec3c`: `1280x960`, `18` steps, interrupted after `365.74s`.
- `b804bbd6-a3e8-4926-8660-025195a5441a`: `640x480`, `4` steps, interrupted after `522.26s`.

No proof image was saved.

Execution report:

- `runs/2026-06-07_17-57_auto/evals/local_identity_execution_report.md`

## Next Step Requiring Approval

Approve a faster local execution path before retrying exactly one non-final identity proof image.

Ready files:

- `runs/2026-06-07_17-57_auto/local-workflows/identity-proof-comfyui.json`
- `runs/2026-06-07_17-57_auto/local-tools/ComfyUI/models/checkpoints/sd_xl_base_1.0.safetensors`

The next successful execution must generate only:

- Aachu and Zuv side-by-side
- face-forward enough for identity review
- no story text
- no brandmark
- no shawl

If the creator rejects this proof, stop and do not generate carousel slides.
