# Local Identity Execution Report

Run: `2026-06-07_17-57_auto`

Status: `blocked`

Failure code: `LOCAL_CPU_EXECUTION_STALLED`

## What Ran

One local ComfyUI server was started with:

- OpenAI API: none
- Paid cloud API: none
- Device: `cpu`
- Workflow: `runs/2026-06-07_17-57_auto/local-workflows/identity-proof-comfyui.json`

The workflow used real `LoadImage` inputs from ComfyUI's local input folder:

| Role | Path | SHA-256 |
| --- | --- | --- |
| `aachu_face_anchor` | `runs/2026-06-07_17-57_auto/local-tools/ComfyUI/input/astory_identity_proof/aachu_face_anchor.jpg` | `5de7bf34c52d0fd7f59e216343c974c643d2f7bac4b50676ede85b61605fcf5d` |
| `zuv_face_anchor` | `runs/2026-06-07_17-57_auto/local-tools/ComfyUI/input/astory_identity_proof/zuv_face_anchor.jpg` | `43d0e147563b55237b79646684945044a12a0f9152f7fbd3b12ea3a74bb7f3f8` |
| `together_pose_context` | `runs/2026-06-07_17-57_auto/local-tools/ComfyUI/input/astory_identity_proof/together_pose_context.jpg` | `86757dcf414e8a857cbfb2d3215e7a85fb7cec1bfaf8c79c6c9cb782bc08f7fe` |

## Attempts

| Prompt ID | Resolution | Steps | Result |
| --- | --- | --- | --- |
| `75b8aae3-f73c-45bd-8172-035377c0ec3c` | `1280x960` | `18` | Interrupted after `365.74s`; still at `0/18`. |
| `b804bbd6-a3e8-4926-8660-025195a5441a` | `640x480` | `4` | Interrupted after `522.26s`; still at `0/4`. |

No identity proof image was saved.

## Hardware Finding

- `torch.backends.mps.is_available()`: `false`
- `torch.backends.mps.is_built()`: `true`
- `torch.cuda.is_available()`: `false`
- Effective execution device: `cpu`

## Decision

The local proof pipeline is wired and proves reference-image delivery, but this CPU-only environment is not practical for SDXL + InstantID image execution.

Final carousel generation remains blocked.

## Smallest Next Step

Use a faster local execution path before retrying:

- MPS-enabled PyTorch/ComfyUI on supported Apple GPU, or
- CUDA machine, or
- SDXL Turbo/Lightning-compatible InstantID workflow, or
- smaller/local identity adapter path.
