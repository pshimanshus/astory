# Local Identity Handoff

Run: `2026-06-07_17-57_auto`

Status: `ready_for_non_cpu_handoff`

## Why This Exists

The source machine is `cpu` and is blocked by `LOCAL_COMPUTE_CPU_ONLY, LOCAL_CPU_EXECUTION_STALLED`. Move this run bundle to a machine where PyTorch reports `mps_available: true` or `cuda_available: true`.

## Missing Required Files

- `none`

## Files To Transfer / Verify

| Role | Path | Status | SHA-256 |
| --- | --- | --- | --- |
| `workflow` | `runs/2026-06-07_17-57_auto/local-workflows/identity-proof-comfyui.json` | `pass` | `3594810dbd688f10d6ff3977a6ff97180663e0ed616d4215fbaff6f78d8f1fd3` |
| `selected_reference_manifest` | `runs/2026-06-07_17-57_auto/references-used/selected_references.json` | `pass` | `625ec2b6abc847fb6400535c2e8bf7a9a6a705ba9617f07d9b0866a4d936af59` |
| `local_reference_proof` | `runs/2026-06-07_17-57_auto/evals/local_identity_reference_proof.json` | `pass` | `c0f040239209c47ceedafb3e16d3311bbab226f60a96aa66fe3a09b57b862b73` |
| `local_stack_discovery` | `runs/2026-06-07_17-57_auto/evals/local_identity_stack_discovery.json` | `pass` | `487aaa8e0fee41cdcc514546928a22844f8eb2e1ee45f3ed7de2b74940e548f6` |
| `local_execution_readiness` | `runs/2026-06-07_17-57_auto/evals/local_identity_execution_readiness.json` | `pass` | `ff7aa86544b69f3aa3c2e93bf626c2d16405bce42c5162832a17198ab7ba07b3` |
| `local_compute_diagnostic` | `runs/2026-06-07_17-57_auto/evals/local_compute_diagnostic.json` | `pass` | `120dd5a56e99866da49fad84e716775b5e884718724b4e07399d8038fa52b2e7` |
| `aachu_face_anchor` | `runs/2026-06-07_17-57_auto/local-tools/ComfyUI/input/astory_identity_proof/aachu_face_anchor.jpg` | `pass` | `5de7bf34c52d0fd7f59e216343c974c643d2f7bac4b50676ede85b61605fcf5d` |
| `zuv_face_anchor` | `runs/2026-06-07_17-57_auto/local-tools/ComfyUI/input/astory_identity_proof/zuv_face_anchor.jpg` | `pass` | `43d0e147563b55237b79646684945044a12a0f9152f7fbd3b12ea3a74bb7f3f8` |
| `together_pose_context` | `runs/2026-06-07_17-57_auto/local-tools/ComfyUI/input/astory_identity_proof/together_pose_context.jpg` | `pass` | `86757dcf414e8a857cbfb2d3215e7a85fb7cec1bfaf8c79c6c9cb782bc08f7fe` |
| `base_checkpoint` | `runs/2026-06-07_17-57_auto/local-tools/ComfyUI/models/checkpoints/sd_xl_base_1.0.safetensors` | `pass` | `31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b` |
| `identity_adapter` | `runs/2026-06-07_17-57_auto/local-tools/ComfyUI/models/instantid/ip-adapter.bin` | `pass` | `02b3618e36d803784166660520098089a81388e61a93ef8002aa79a5b1c546e1` |
| `controlnet` | `runs/2026-06-07_17-57_auto/local-tools/ComfyUI/models/controlnet/instantid-controlnet.safetensors` | `pass` | `c8127be9f174101ebdafee9964d856b49b634435cf6daa396d3f593cf0bbbb05` |
| `insightface_antelopev2_1` | `runs/2026-06-07_17-57_auto/local-tools/ComfyUI/models/insightface/models/antelopev2/genderage.onnx` | `pass` | `4fde69b1c810857b88c64a335084f1c3fe8f01246c9a191b48c7bb756d6652fb` |
| `insightface_antelopev2_2` | `runs/2026-06-07_17-57_auto/local-tools/ComfyUI/models/insightface/models/antelopev2/2d106det.onnx` | `pass` | `f001b856447c413801ef5c42091ed0cd516fcd21f2d6b79635b1e733a7109dbf` |
| `insightface_antelopev2_3` | `runs/2026-06-07_17-57_auto/local-tools/ComfyUI/models/insightface/models/antelopev2/1k3d68.onnx` | `pass` | `df5c06b8a0c12e422b2ed8947b8869faa4105387f199c477af038aa01f9a45cc` |
| `insightface_antelopev2_4` | `runs/2026-06-07_17-57_auto/local-tools/ComfyUI/models/insightface/models/antelopev2/glintr100.onnx` | `pass` | `4ab1d6435d639628a6f3e5008dd4f929edf4c4124b1a7169e1048f9fef534cdf` |
| `insightface_antelopev2_5` | `runs/2026-06-07_17-57_auto/local-tools/ComfyUI/models/insightface/models/antelopev2/scrfd_10g_bnkps.onnx` | `pass` | `5838f7fe053675b1c7a08b633df49e7af5495cee0493c7dcf6697200b85b5b91` |

## Target Machine Checks

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/local_identity_pipeline.py --run-id 2026-06-07_17-57_auto --workflow-id option_b_sdxl_instantid_pulid_ipadapter --workflow-file runs/2026-06-07_17-57_auto/local-workflows/identity-proof-comfyui.json --dry-run --compute-diagnostic
```

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/local_identity_pipeline.py --run-id 2026-06-07_17-57_auto --workflow-id option_b_sdxl_instantid_pulid_ipadapter --workflow-file runs/2026-06-07_17-57_auto/local-workflows/identity-proof-comfyui.json --dry-run --execution-readiness
```

## Guardrails

- Do not run this proof on CPU.
- Do not generate final carousel slides from the handoff.
- Generate at most one non-final identity proof before creator QA.
- If identity proof fails, revise workflow before story art.

## Sources

- [PyTorch MPS backend](https://docs.pytorch.org/docs/2.12/notes/mps.html)
- [ComfyUI](https://github.com/Comfy-Org/ComfyUI)
