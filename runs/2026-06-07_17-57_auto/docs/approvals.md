# Approvals

Run: `2026-06-07_17-57_auto`

This file records explicit creator decisions at HITL gates.

## HITL Idea Lock

Status: `approved`

Decision: approved by creator.

Evidence:

- Creator reply: `approve idea`
- Approved idea: `The Shawl He Brought Before She Asked`
- Approval recorded at: `2026-06-07T18:00:00+05:30`

Approved to continue to:

- `GENERATE_STORY_CONCEPT`
- `DECIDE_SLIDE_COUNT`
- `GENERATE_SLIDE_BEATS`
- `GENERATE_SCENE_OPTIONS`
- `SELECT_AND_ORDER_SLIDES`

Required next pause: `HITL_STORY_LOCK`

## HITL Story Lock

Status: `approved`

Decision: approved by creator.

Evidence:

- Creator reply: `approve story`
- Story concept: `runs/2026-06-07_17-57_auto/planning/story_concept.json`
- Slide count decision: `runs/2026-06-07_17-57_auto/planning/slide_count_decision.md`
- Slide beat map: `runs/2026-06-07_17-57_auto/planning/slide_beat_map.json`
- Scene options: `runs/2026-06-07_17-57_auto/planning/scene_options.json`
- Selected scenes: `runs/2026-06-07_17-57_auto/planning/selected_scenes.json`
- Approval recorded at: `2026-06-07T18:39:59+05:30`

Required next pause after approval: `HITL_PROMPT_LOCK`

## HITL Prompt Lock

Status: `approved`

Decision: approved by creator.

Evidence:

- Creator reply: `approve prompts`
- Character bible: `runs/2026-06-07_17-57_auto/planning/character_bible.json`
- Style bible: `runs/2026-06-07_17-57_auto/planning/style_bible.json`
- Prompt manifest: `runs/2026-06-07_17-57_auto/prompts/prompt_pack_manifest.json`
- Prompt generation report: `runs/2026-06-07_17-57_auto/prompts/prompt_generation_report.md`
- Prompt QA review: `runs/2026-06-07_17-57_auto/debates/prompt_room/prompt_review.md`
- Pre-generation eval: `runs/2026-06-07_17-57_auto/evals/pre_generation_eval.json`
- Approval recorded at: `2026-06-07T18:51:54+05:30`

Required next step after approval: `LOAD_REFERENCE_IMAGES_IN_CONTEXT`

## HITL Image QA

Status: `rejected`

Decision: rejected by creator; revision required.

Evidence:

- Image QA debate: `runs/2026-06-07_17-57_auto/debates/image_qa_room/image_qa_debate.md`
- Image quality eval: `runs/2026-06-07_17-57_auto/evals/image_quality_eval.json`
- Image quality report: `runs/2026-06-07_17-57_auto/evals/image_quality_report.md`
- Generation attempts: `runs/2026-06-07_17-57_auto/images/generation_attempts.json`

Current QA result:

- Accepted current candidates: 0.
- Hard failures: `IDENTITY_DRIFT`, `SCENE_LOGIC_CONTRADICTION`, and secondary `TEXT_NOT_EXACT`.
- Creator feedback: faces do not match; slide 1 showed Zuv carrying the shawl but slide 2 did not include the shawl.
- Superseding report: `runs/2026-06-07_17-57_auto/evals/image_quality_creator_rejection_report.md`

Required next step after rejection: `RETRY_OR_REVISE_IF_NEEDED`

## Post Image QA Prompt Revision

Status: `attempted_blocked`

Decision: awaiting creator approval or revision after continuity fix.

Evidence:

- Revised slide 1 post prompt: `runs/2026-06-07_17-57_auto/prompts/slide_01_post_4x5.txt`
- Revised slide 1 story prompt: `runs/2026-06-07_17-57_auto/prompts/slide_01_story_9x16.txt`
- Revised beat map: `runs/2026-06-07_17-57_auto/planning/slide_beat_map.json`
- Revised selected scenes: `runs/2026-06-07_17-57_auto/planning/selected_scenes.json`

Revision summary:

- Slide 1: no visible shawl; Zuv notices.
- Slide 2: no visible shawl; Aachu performs the "I'm fine" act.
- Slide 3: first visible shawl reveal.
- Slide 4: shawl payoff.

Required next step after approval: confirm reference-input strategy before regenerating images.

## HITL Reference Input Proof

Status: `rejected`

Decision: rejected by creator; built-in context imagegen is blocked for final Aachu/Zuv identity work.

Evidence:

- Smoke-test candidate: `runs/2026-06-07_17-57_auto/images/identity_smoke_test_builtin_context_01.png`
- Reference proof JSON: `runs/2026-06-07_17-57_auto/evals/reference_input_proof.json`
- Reference proof report: `runs/2026-06-07_17-57_auto/evals/reference_input_proof_report.md`

Creator feedback:

- `faces are still not matching at all`
- Feedback recorded at: `2026-06-08T07:39:42+05:30`

Current decision:

- Failure code: `IDENTITY_DRIFT`
- Do not retry final Aachu/Zuv artwork with the current built-in prompt/context-only imagegen path.
- Required next path: explicit image-input API/edit workflow, or keep final image generation blocked.

## HITL Local Model Setup Approval

Status: `pending`

Decision: awaiting creator approval before any local model setup, heavy dependency install, model download, or model execution.

Evidence:

- Local proof script: `scripts/local_identity_pipeline.py`
- Local proof JSON: `runs/2026-06-07_17-57_auto/evals/local_identity_reference_proof.json`
- Local proof report: `runs/2026-06-07_17-57_auto/evals/local_identity_reference_proof_report.md`
- Reference strategy update: `runs/2026-06-07_17-57_auto/references-used/reference_delivery_strategy.md`

Current decision:

- OpenAI API path: disallowed by creator for this run.
- Paid cloud API path: disallowed by creator for this run.
- Reference delivery proof: `pass`, using local binary image inputs with hashes and roles.
- Workflow readiness: `blocked`, because no executable local workflow file exists yet.
- Failure code: `LOCAL_WORKFLOW_MISSING`

Required next step after approval:

- Run only a no-download local workflow discovery/setup check first.
- Generate only a non-final Aachu/Zuv identity proof image after the local workflow exists and creator approves model execution.
- Do not generate final carousel slides until the identity proof passes creator Image QA.

## HITL Local Discovery

Status: `completed_blocked`

Decision: creator replied `now proceed`; Codex proceeded with no-download local stack discovery only.

Evidence:

- Discovery JSON: `runs/2026-06-07_17-57_auto/evals/local_identity_stack_discovery.json`
- Discovery report: `runs/2026-06-07_17-57_auto/evals/local_identity_stack_discovery_report.md`
- Discovery command: `PYTHONDONTWRITEBYTECODE=1 python3 scripts/local_identity_pipeline.py --run-id 2026-06-07_17-57_auto --workflow-id option_b_sdxl_instantid_pulid_ipadapter --workflow-file runs/2026-06-07_17-57_auto/local-workflows/identity-proof-comfyui.json --discover-local-stack --dry-run`

Current decision:

- No heavy dependencies installed.
- No model weights downloaded.
- No local model execution run.
- Result: `blocked`
- Failure codes: `COMFYUI_MISSING`, `LOCAL_WORKFLOW_MISSING`, `LOCAL_MODELS_MISSING`

Required next approval:

- Explicit approval for local ComfyUI setup and model downloads, including expected disk/time cost, before attempting the actual non-final identity proof image.

## Role-Based Reference Library Refresh

Status: `completed_no_generation`

Decision: creator requested end-to-end review, corrected curation, multiple angles, and clear face shots. Codex refreshed the reference library and proof artifacts without generating images.

Evidence:

- Identity dossier: `references/identity/_dossier/identity-dossier.json`
- Face contact sheet: `references/identity/_dossier/identity-face-contact-sheet.jpg`
- Expression contact sheet: `references/identity/_dossier/identity-expressions-contact-sheet.jpg`
- Active run reference manifest: `runs/2026-06-07_17-57_auto/references-used/selected_references.json`
- Local proof JSON: `runs/2026-06-07_17-57_auto/evals/local_identity_reference_proof.json`
- Local proof report: `runs/2026-06-07_17-57_auto/evals/local_identity_reference_proof_report.md`

Current decision:

- No model execution run.
- No final carousel image generation run.
- Active face defaults now use 4 close Aachu crops and 4 close Zuv crops.
- Dossier contains 11 Aachu face anchors, 8 Zuv face anchors, and 53 active role-indexed inputs.
- Dossier deprecates 14 duplicate role aliases; active cross-role duplicate image hashes are 0.

Required next approval:

- Final or proof image generation still requires explicit approval for an actual image-input workflow/local model execution path.

## Identity Reference Call-Site Audit

Status: `completed_pass`

Decision: active run artifacts were checked and updated so identity/face reference calls cite the role-based defaults end to end.

Evidence:

- Audit JSON: `runs/2026-06-07_17-57_auto/evals/identity_reference_call_site_audit.json`
- Audit report: `runs/2026-06-07_17-57_auto/evals/identity_reference_call_site_audit_report.md`
- Updated prompts: `runs/2026-06-07_17-57_auto/prompts/`
- Updated planning artifacts: `runs/2026-06-07_17-57_auto/planning/`
- Updated prompt QA review: `runs/2026-06-07_17-57_auto/debates/prompt_room/prompt_review.md`

Current decision:

- Active findings: `0`
- Strict full-repo audit scanned `162` non-vendor text files and `85` identity/reference-bearing files.
- Legacy/vague flat-reference pattern matches in scanned text: `0`.
- Historical failed-proof evidence is superseded/redacted and is not an active generation input.
- Dossier support roles now explicitly block `face_identity` use.
- No model execution run.
- No final carousel image generation run.

## HITL Local Setup Progress

Status: `partial_setup_completed_blocked`

Decision: creator replied `now proceed`; Codex proceeded with local ComfyUI setup and downloaded only local/open-weight support files needed for an InstantID-first proof path. No OpenAI API, paid cloud API, final artwork, or local image generation was run.

Evidence:

- Local proof script: `scripts/local_identity_pipeline.py`
- Local proof tests: `tests/test_local_identity_pipeline.py`
- ComfyUI root: `runs/2026-06-07_17-57_auto/local-tools/ComfyUI`
- Local model manifest: `runs/2026-06-07_17-57_auto/evals/local_model_requirements.json`
- Refreshed discovery JSON: `runs/2026-06-07_17-57_auto/evals/local_identity_stack_discovery.json`
- Refreshed discovery report: `runs/2026-06-07_17-57_auto/evals/local_identity_stack_discovery_report.md`
- Reference strategy: `runs/2026-06-07_17-57_auto/references-used/reference_delivery_strategy.md`

Completed setup:

- ComfyUI cloned under the run folder.
- Local virtualenv and ComfyUI requirements installed.
- Custom nodes cloned: `ComfyUI_IPAdapter_plus`, `ComfyUI_InstantID`, `PuLID_ComfyUI`.
- Custom node dependencies installed.
- ComfyUI CPU quick-test passed.
- InstantID adapter, InstantID ControlNet, and AntelopeV2 InsightFace files downloaded and hashed.

Current blocker:

- `LOCAL_WORKFLOW_MISSING`
- `LOCAL_MODELS_MISSING`, narrowed to missing minimum role `sdxl_base_checkpoint`

Required next approval:

- Approve the exact SDXL checkpoint source/download and the executable ComfyUI identity-proof workflow before any model execution.
- First execution, once unblocked, must generate only one non-final identity proof image: no story text, no brandmark, no shawl.

## HITL Local Execution Approval

Status: `pending`

Decision: creator replied `proceed`; Codex downloaded the SDXL base checkpoint, created the executable ComfyUI API workflow, refreshed proof/discovery artifacts, and attempted exactly one non-final local identity proof path. The execution did not produce an image and was blocked for CPU-only runtime.

Evidence:

- SDXL checkpoint: `runs/2026-06-07_17-57_auto/local-tools/ComfyUI/models/checkpoints/sd_xl_base_1.0.safetensors`
- SDXL checkpoint SHA-256: `31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b`
- Identity proof workflow: `runs/2026-06-07_17-57_auto/local-workflows/identity-proof-comfyui.json`
- Workflow SHA-256: `78e92d8ae05f813fc5b6f1cc81ac0f3819f983f69f135c1d5f1fbf2b81ae9704`
- Refreshed proof JSON: `runs/2026-06-07_17-57_auto/evals/local_identity_reference_proof.json`
- Refreshed discovery JSON: `runs/2026-06-07_17-57_auto/evals/local_identity_stack_discovery.json`
- Local model manifest: `runs/2026-06-07_17-57_auto/evals/local_model_requirements.json`
- Local execution report: `runs/2026-06-07_17-57_auto/evals/local_identity_execution_report.md`

Current decision:

- Local stack status: `execution_blocked_cpu_stalled`
- Final carousel generation: still blocked
- Non-final identity proof image: not generated

Required next approval:

- Approve a faster local execution path before retrying identity proof.
- Do not generate carousel slides until the identity proof passes creator Image QA.
