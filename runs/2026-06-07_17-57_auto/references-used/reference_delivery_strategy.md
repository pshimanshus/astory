# Reference Delivery Strategy

Run: `2026-06-07_17-57_auto`

## Current Finding

The current image run should not be treated as final identity-preserving generation.

Update recorded `2026-06-08T07:39:42+05:30`: the built-in context smoke test was rejected by the creator because the faces still did not match. This means the current built-in prompt/context-only imagegen path is blocked for final Aachu/Zuv artwork.

The selected reference files were loaded for Codex inspection and were useful for prompt writing and QA, but the active built-in `image_gen` call available in this session only exposes a text prompt argument. That means the generated images may not have received Aachu/Zuv reference images as actual image inputs.

For exact recurring-person identity, local file paths, a Python-selected manifest, or a prompt section that lists image paths are not enough by themselves.

## Required Reference Roles

Before regenerating final art, each selected image must be explicitly delivered as one of:

- `identity reference`: controls Aachu/Zuv face, hair, skin tone, age, and relationship energy.
- `style reference`: controls watercolor-and-ink finish, paper, text style, and palette.
- `edit target`: only if editing/compositing from an existing generated or uploaded image.

## Built-In Context Test Result

Candidate:

`runs/2026-06-07_17-57_auto/images/identity_smoke_test_builtin_context_01.png`

Verdict: `blocked`

Failure code: `IDENTITY_DRIFT`

Creator feedback:

`faces are still not matching at all`

## Required Next Generation Strategy

1. Use an explicit image-input API/edit workflow where selected Aachu/Zuv references are passed as actual image inputs.
2. Record proof of the image inputs: role, path, hash, and generation call mode.
3. Generate one non-final identity proof image first.
4. Proceed to carousel slides only after creator accepts the identity proof.
5. Hard-reject if faces drift, even if style/text are good.

## Block Condition

If the active tool path cannot pass actual reference images or edit targets to the model, mark final imagegen blocked with `IDENTITY_REFERENCE_MISSING` / `IDENTITY_DRIFT` rather than producing more prompt-only finals.

For this run, the built-in context path has already failed and must not be retried for final art.

## Story Continuity Lock

- Slide 1: no visible shawl.
- Slide 2: no visible shawl.
- Slide 3: first visible folded shawl reveal.
- Slide 4: shawl resting/draped as payoff.

## Zero-OpenAI-API Local Fallback

Update recorded `2026-06-08T08:26:04+05:30`: creator requested a zero-OpenAI-API, no paid cloud path. The prior explicit OpenAI API/edit suggestion is superseded for this run.

Dry-run proof artifacts:

- `runs/2026-06-07_17-57_auto/evals/local_identity_reference_proof.json`
- `runs/2026-06-07_17-57_auto/evals/local_identity_reference_proof_report.md`
- `scripts/local_identity_pipeline.py`

Current local proof result:

- Reference delivery: `pass`
- Delivery mode: `local_binary_input`
- Prompt-only references allowed: `false`
- Recommended first local stack: `option_b_sdxl_instantid_pulid_ipadapter`
- Workflow readiness: `blocked`
- Failure code: `LOCAL_WORKFLOW_MISSING`

Model stack proposal:

1. Option A: FLUX.1 Kontext [dev] through ComfyUI for reference-image editing. Good for context/editing, but not a dedicated two-face identity adapter.
2. Option B: SDXL + InstantID/PuLID/IP-Adapter through ComfyUI. Recommended first because it uses explicit face-ID/image conditioning from Aachu/Zuv face crops and portraits.
3. Option C: train separate Aachu/Zuv identity LoRAs if zero-shot identity fails creator face-match review.

Hard gate:

- Do not download local model weights without creator approval.
- Do not install heavy dependencies without creator approval.
- Do not run local model execution without creator approval.
- Do not generate final carousel slides until a non-final identity proof image passes creator review.

Smallest next approved step:

```bash
python3 scripts/local_identity_pipeline.py --run-id 2026-06-07_17-57_auto --workflow-id option_b_sdxl_instantid_pulid_ipadapter --workflow-file runs/2026-06-07_17-57_auto/local-workflows/identity-proof-comfyui.json --dry-run
```

If the workflow file or local model weights do not exist, keep final image generation blocked.

## Local Stack Discovery Result

Update recorded `2026-06-08T08:43:42+05:30`: no-download discovery was run after creator said `now proceed`.

Discovery artifacts:

- `runs/2026-06-07_17-57_auto/evals/local_identity_stack_discovery.json`
- `runs/2026-06-07_17-57_auto/evals/local_identity_stack_discovery_report.md`

Discovery result:

- Status: `blocked`
- ComfyUI executable/root/server: missing
- Local workflow file: missing
- SDXL candidate: missing
- InstantID candidate: missing
- PuLID candidate: missing
- IP-Adapter candidate: missing
- Failure codes: `COMFYUI_MISSING`, `LOCAL_WORKFLOW_MISSING`, `LOCAL_MODELS_MISSING`

Meaning:

- The repo can prove which identity references must be passed as local image bytes.
- The current machine does not yet have the local image-generation stack needed to generate the non-final identity proof.
- Heavy setup/download/model execution remains blocked until the creator explicitly approves that larger step.

## Role-Based Reference Library Refresh

Update recorded `2026-06-08T09:07:54+05:30`: the active run manifest now points at the role-based dossier instead of the older flat portrait/face bundle.

Updated artifacts:

- `references/identity/_dossier/identity-dossier.json`
- `references/identity/_dossier/identity-face-contact-sheet.jpg`
- `references/identity/_dossier/identity-expressions-contact-sheet.jpg`
- `references/identity/_dossier/together-contact-sheet.jpg`
- `references/identity/_dossier/wardrobe-contact-sheet.jpg`
- `references/identity/_dossier/places-contact-sheet.jpg`
- `runs/2026-06-07_17-57_auto/references-used/selected_references.json`
- `runs/2026-06-07_17-57_auto/evals/local_identity_reference_proof.json`
- `runs/2026-06-07_17-57_auto/evals/local_identity_reference_proof_report.md`

Current role inventory:

- Aachu face anchors: `11`
- Zuv face anchors: `8`
- Active dossier role inputs: `53`
- Deprecated duplicate role aliases: `14`
- Active cross-role duplicate image hashes: `0`
- Active default face inputs: 4 close Aachu crops and 4 close Zuv crops.

Guardrail:

- Face sheets contain only face anchors.
- Expressions, together/body-language, wardrobe, places, and formal-secondary references remain separate support roles.
- Exact duplicate images are active under only one canonical role; duplicate aliases are retained only in the dossier deprecation ledger.
- Wardrobe/place/formal/sunglasses references must never replace primary face identity anchors.

## Identity Reference Call-Site Audit

Update recorded `2026-06-08T09:30:00+05:30`: active prompt/planning/reference call sites were audited after the role-library refresh.

Audit artifacts:

- `runs/2026-06-07_17-57_auto/evals/identity_reference_call_site_audit.json`
- `runs/2026-06-07_17-57_auto/evals/identity_reference_call_site_audit_report.md`

Result:

- Status: `pass`
- Active prompt/planning/reference/doc/script findings: `0`
- Active call sites now cite the role-based dossier defaults, not legacy flat portrait/face references.
- Follow-up strict audit scanned `162` non-vendor text files and `85` identity/reference-bearing files line-by-line.
- Legacy/vague flat-reference pattern matches in scanned text: `0`.
- Historical failed-proof evidence is now superseded/redacted and is not an active generation source.

Strict full-repo audit artifacts:

- `runs/2026-06-07_17-57_auto/evals/identity_reference_full_repo_audit.json`
- `runs/2026-06-07_17-57_auto/evals/identity_reference_full_repo_audit_report.md`

Additional guardrail added:

- `scripts/local_identity_pipeline.py` now enforces that support references such as smile, reaction, together, wardrobe, place, and formal-secondary entries explicitly block `face_identity` use.
- `references/identity/_dossier/identity-dossier.json` now carries the same explicit support-role `do_not_use_for` guard.
- All eight active slide prompts use a `Generation hard gate` requiring actual local image inputs, not text descriptions or file paths alone.

## Local Stack Setup Progress

Update recorded `2026-06-08T09:33:06+05:30`: creator said `now proceed`; Codex proceeded with zero-OpenAI-API local setup work and refreshed discovery artifacts. No final artwork and no local model generation were run.

Installed or prepared under this run:

- ComfyUI cloned to `runs/2026-06-07_17-57_auto/local-tools/ComfyUI`.
- ComfyUI virtualenv created at `runs/2026-06-07_17-57_auto/local-tools/ComfyUI/.venv`.
- ComfyUI Python requirements installed locally.
- Custom nodes cloned: `ComfyUI_IPAdapter_plus`, `ComfyUI_InstantID`, and `PuLID_ComfyUI`.
- Custom node dependencies installed locally, including `insightface`, `onnxruntime`, `facexlib`, and `timm`.
- ComfyUI CPU quick-test passed.
- InstantID adapter downloaded and hashed: `runs/2026-06-07_17-57_auto/local-tools/ComfyUI/models/instantid/ip-adapter.bin`.
- InstantID ControlNet downloaded and hashed: `runs/2026-06-07_17-57_auto/local-tools/ComfyUI/models/controlnet/instantid-controlnet.safetensors`.
- AntelopeV2 InsightFace models downloaded, extracted, and hashed under `runs/2026-06-07_17-57_auto/local-tools/ComfyUI/models/insightface/models/antelopev2/`.

Current refreshed discovery result:

- Status: `blocked`
- ComfyUI root: `found`
- Python dependencies: `found`
- Local workflow file: `missing`
- Minimum InstantID proof models found: `instantid_ip_adapter`, `instantid_controlnet`, `insightface_antelopev2`
- Missing minimum model role: `sdxl_base_checkpoint`
- Optional add-ons still missing: `pulid_sdxl_model`, `clip_vision_vit_h`, `ipadapter_plus_face_sdxl`
- Failure codes: `LOCAL_WORKFLOW_MISSING`, `LOCAL_MODELS_MISSING`

Updated setup artifacts:

- `runs/2026-06-07_17-57_auto/evals/local_identity_stack_discovery.json`
- `runs/2026-06-07_17-57_auto/evals/local_identity_stack_discovery_report.md`
- `runs/2026-06-07_17-57_auto/evals/local_model_requirements.json`
- `runs/2026-06-07_17-57_auto/evals/local_model_setup_approval_request.md`

Hard gate remains:

- Do not generate carousel slides.
- Do not call built-in prompt-only imagegen for final Aachu/Zuv identity.
- Do not run local model generation until the SDXL checkpoint and executable ComfyUI workflow exist.
- First local output must be a non-final identity proof only: Aachu and Zuv side-by-side, face-forward enough to judge identity, no story text, no brandmark, no shawl.

## Local Stack Ready For Non-Final Execution Approval

Update recorded `2026-06-10T22:12:00+05:30`: after creator said `proceed`, the SDXL checkpoint was downloaded and the executable ComfyUI API workflow was created. No model generation has been run yet.

Resolved blockers:

- `LOCAL_MODELS_MISSING`: resolved for the minimum InstantID proof path.
- `LOCAL_WORKFLOW_MISSING`: resolved by `runs/2026-06-07_17-57_auto/local-workflows/identity-proof-comfyui.json`.

Exact model/workflow proof:

- SDXL checkpoint: `runs/2026-06-07_17-57_auto/local-tools/ComfyUI/models/checkpoints/sd_xl_base_1.0.safetensors`
- SDXL SHA-256: `31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b`
- Workflow: `runs/2026-06-07_17-57_auto/local-workflows/identity-proof-comfyui.json`
- Workflow SHA-256: `78e92d8ae05f813fc5b6f1cc81ac0f3819f983f69f135c1d5f1fbf2b81ae9704`

ComfyUI input images used by the workflow:

- Aachu face anchor: `runs/2026-06-07_17-57_auto/local-tools/ComfyUI/input/astory_identity_proof/aachu_face_anchor.jpg`
- Aachu input SHA-256: `5de7bf34c52d0fd7f59e216343c974c643d2f7bac4b50676ede85b61605fcf5d`
- Zuv face anchor: `runs/2026-06-07_17-57_auto/local-tools/ComfyUI/input/astory_identity_proof/zuv_face_anchor.jpg`
- Zuv input SHA-256: `43d0e147563b55237b79646684945044a12a0f9152f7fbd3b12ea3a74bb7f3f8`
- Together pose/context input: `runs/2026-06-07_17-57_auto/local-tools/ComfyUI/input/astory_identity_proof/together_pose_context.jpg`
- Together input SHA-256: `86757dcf414e8a857cbfb2d3215e7a85fb7cec1bfaf8c79c6c9cb782bc08f7fe`

Current gate:

- Discovery status: `ready_for_creator_execution_approval`
- Dry-run proof status: `dry_run_pass_pending_creator_execution_approval`
- Final carousel generation remains blocked until the non-final identity proof image passes creator review.

## Local Execution Attempt Result

Update recorded `2026-06-10T22:16:21+05:30`: Codex attempted local execution after creator said `proceed`. The workflow validated and queued, but no proof image was produced.

Execution attempts:

- Prompt `75b8aae3-f73c-45bd-8172-035377c0ec3c`: `1280x960`, `18` steps, interrupted after `365.74s` while still at `0/18`.
- Prompt `b804bbd6-a3e8-4926-8660-025195a5441a`: `640x480`, `4` steps, interrupted after `522.26s` while still at `0/4`.

Hardware finding:

- `torch.backends.mps.is_available()`: `false`
- `torch.backends.mps.is_built()`: `true`
- `torch.cuda.is_available()`: `false`
- Effective execution device: `cpu`

Current status:

- Reference delivery proof: solved
- Local workflow/model setup: solved
- Local image execution: `blocked`
- Failure code: `LOCAL_CPU_EXECUTION_STALLED`
- Identity proof image: not generated
- Final carousel generation: still blocked

Execution report:

- `runs/2026-06-07_17-57_auto/evals/local_identity_execution_report.md`
- `runs/2026-06-07_17-57_auto/evals/local_identity_execution_report.json`
