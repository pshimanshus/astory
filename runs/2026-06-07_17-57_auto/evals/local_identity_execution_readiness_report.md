# Local Identity Execution Readiness

Run: `2026-06-07_17-57_auto`

Status: `blocked`

## Decision

- Non-final identity proof allowed now: `False`
- Final carousel generation allowed: `False`
- Failure codes: `LOCAL_CPU_EXECUTION_STALLED`
- Reason: Local identity execution is not ready: LOCAL_CPU_EXECUTION_STALLED.

## Workflow

- Path: `runs/2026-06-07_17-57_auto/local-workflows/identity-proof-comfyui.json`
- Exists: `True`
- SHA-256: `3594810dbd688f10d6ff3977a6ff97180663e0ed616d4215fbaff6f78d8f1fd3`
- Binding status: `pass`
- LoadImage inputs: `astory_identity_proof/aachu_face_anchor.jpg, astory_identity_proof/together_pose_context.jpg, astory_identity_proof/zuv_face_anchor.jpg`
- ApplyInstantID nodes: `2`

## Copied Reference Inputs

- Status: `pass`
- Failure codes: `none`

| Role | Path | Status | SHA-256 |
| --- | --- | --- | --- |
| `aachu_face_anchor` | `runs/2026-06-07_17-57_auto/local-tools/ComfyUI/input/astory_identity_proof/aachu_face_anchor.jpg` | `pass` | `5de7bf34c52d0fd7f59e216343c974c643d2f7bac4b50676ede85b61605fcf5d` |
| `zuv_face_anchor` | `runs/2026-06-07_17-57_auto/local-tools/ComfyUI/input/astory_identity_proof/zuv_face_anchor.jpg` | `pass` | `43d0e147563b55237b79646684945044a12a0f9152f7fbd3b12ea3a74bb7f3f8` |
| `together_pose_context` | `runs/2026-06-07_17-57_auto/local-tools/ComfyUI/input/astory_identity_proof/together_pose_context.jpg` | `pass` | `86757dcf414e8a857cbfb2d3215e7a85fb7cec1bfaf8c79c6c9cb782bc08f7fe` |

## Hardware

- Effective execution device: `cpu`
- MPS available: `False`
- CUDA available: `False`

## Previous Execution

- Report: `runs/2026-06-07_17-57_auto/evals/local_identity_execution_report.json`
- Status: `blocked`
- Failure code: `LOCAL_CPU_EXECUTION_STALLED`
- Identity proof generated: `False`
- Final artwork generated: `False`
- Attempts: `2`

## Guardrail

This readiness check did not install dependencies, download model weights, or execute generation. Keep final Aachu/Zuv carousel generation blocked until a non-final identity proof image is generated locally and accepted by creator QA.
