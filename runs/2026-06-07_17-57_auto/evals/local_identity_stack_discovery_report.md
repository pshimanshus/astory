# Local Identity Stack Discovery

Run: `2026-06-07_17-57_auto`

Status: `ready_for_creator_execution_approval`

## Decision

- Final/model execution state: `pending_creator_model_execution_approval`
- Failure codes: `none`
- Reason: ComfyUI, a local workflow file, and required model candidates are present. Model execution is still gated on creator approval and identity QA.

## ComfyUI

- Available: `True`
- Executable: `not found`
- Server URL: `http://127.0.0.1:8188`
- Server available: `False`

Roots found:

- `runs/2026-06-07_17-57_auto/local-tools/ComfyUI`

## Workflow File

- Status: `found`
- Path: `runs/2026-06-07_17-57_auto/local-workflows/identity-proof-comfyui.json`

## Python Dependencies

- Status: `found`
- Missing modules: `none`

## Model Inventory

- Minimum status: `found`
- Optional add-on status: `missing`
- Missing minimum roles: `none`

Minimum InstantID proof models:

- `sdxl_base_checkpoint`: 1 candidate(s), status `found`
- `instantid_ip_adapter`: 1 candidate(s), status `found`
- `instantid_controlnet`: 1 candidate(s), status `found`
- `insightface_antelopev2`: 5 candidate(s), status `found`

Optional PuLID/IP-Adapter add-on models:

- `pulid_sdxl_model`: 0 candidate(s), status `missing`
- `clip_vision_vit_h`: 0 candidate(s), status `missing`
- `ipadapter_plus_face_sdxl`: 0 candidate(s), status `missing`

## Guardrail

This discovery step did not install dependencies, download model weights, or execute generation. Do not generate final carousel slides until a non-final identity proof image passes creator review.
