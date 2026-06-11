# Local Compute Diagnostic

Run: `2026-06-07_17-57_auto`

Status: `blocked`

## Decision

- Local compute ready: `False`
- Selected execution device: `cpu`
- Non-final identity proof allowed now: `False`
- Final carousel generation allowed: `False`
- Failure codes: `LOCAL_COMPUTE_CPU_ONLY, LOCAL_CPU_EXECUTION_STALLED`
- Reason: Local compute is not ready for another identity proof attempt: LOCAL_COMPUTE_CPU_ONLY, LOCAL_CPU_EXECUTION_STALLED. Torch reason: MACOS_OR_DEVICE_NOT_MPS_ENABLED.

## Torch Probe

- Python: `/Users/himanshusharma/A Story of Two V2/runs/2026-06-07_17-57_auto/local-tools/ComfyUI/.venv/bin/python`
- Torch version: `2.12.0`
- MPS built: `True`
- MPS available: `False`
- CUDA available: `False`
- CUDA device count: `0`
- Unavailable reason: `MACOS_OR_DEVICE_NOT_MPS_ENABLED`

## Machine

- Platform: `macOS-26.5.1-arm64-arm-64bit-Mach-O`
- Machine: `arm64`
- macOS: `26.5.1`

## ComfyUI Roots

- `runs/2026-06-07_17-57_auto/local-tools/ComfyUI`

## Stack State

- Stack discovery: `ready_for_creator_execution_approval`
- Execution readiness: `blocked`

## Recommended Next Step

Do not retry on this CPU path. Use a machine where PyTorch reports `mps_available: true` or `cuda_available: true`, then run the same workflow bundle there.

## Sources

- [PyTorch MPS backend](https://docs.pytorch.org/docs/2.12/notes/mps.html)
- [ComfyUI](https://github.com/Comfy-Org/ComfyUI)

## Guardrail

This diagnostic did not install dependencies, download model weights, or execute generation. Keep final Aachu/Zuv carousel generation blocked until a non-final identity proof image is generated on a non-CPU device and accepted by creator QA.
