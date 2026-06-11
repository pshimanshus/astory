# Local Identity Reference Proof

Run: `2026-06-07_17-57_auto`

Status: `dry_run_pass_pending_creator_execution_approval`

## Decision

- Final Aachu/Zuv artwork remains `pending_creator_model_execution_approval`.
- Failure codes: `none`.
- Reason: Reference image inputs are explicit and a local workflow file exists, but no model execution has been approved or run.

## Proposed Local Stack

Recommended: `option_b_sdxl_instantid_pulid_ipadapter`

Option B: SDXL + InstantID/PuLID/IP-Adapter via ComfyUI

- Engine: `ComfyUI local server`
- Identity method: explicit face-ID conditioning from local image inputs
- Why this first: Most targeted zero-shot identity path for Aachu/Zuv because face crops can drive identity separately from style references.
- Risk: Two-person identity often needs region control, masked generation, or separate passes; quality depends on local nodes and model weights.

## Options

- `option_a_flux_kontext_dev`: Option A: FLUX.1 Kontext [dev] via ComfyUI - reference-image editing / in-context image conditioning. Risk: Not a dedicated face-ID adapter; may still drift on two recurring people, and weights/workflow are large.
- `option_b_sdxl_instantid_pulid_ipadapter`: Option B: SDXL + InstantID/PuLID/IP-Adapter via ComfyUI - explicit face-ID conditioning from local image inputs. Risk: Two-person identity often needs region control, masked generation, or separate passes; quality depends on local nodes and model weights.
- `option_c_train_identity_loras`: Option C: train separate Aachu/Zuv identity LoRAs - trained recurring-character adapters. Risk: Requires curated datasets, training time, storage, and extra QA to avoid overfit or style collapse.

## Reference Input Proof

Prompt-only delivery allowed: `False`

| Person/group | Role | Path | SHA-256 |
| --- | --- | --- | --- |
| `aachu` | `aachu_identity_face_crop` | `references/identity/aachu/face/aachu-face-crop-car-purple-01.jpg` | `5de7bf34c52d0fd7f59e216343c974c643d2f7bac4b50676ede85b61605fcf5d` |
| `aachu` | `aachu_identity_face_crop` | `references/identity/aachu/face/aachu-face-crop-cafe-neutral-01.jpg` | `70edc1e0795fc36a7a380c3e0a77d9ed5b46c2efda8b11c6ded3e0066bc5cc2c` |
| `aachu` | `aachu_identity_face_crop` | `references/identity/aachu/face/aachu-face-crop-home-black-01.jpg` | `0d42f196b01aeb95b11d863feb36c7b4cbacfa0723f027f75ca272d42a4ea67c` |
| `aachu` | `aachu_identity_face_crop` | `references/identity/aachu/face/aachu-face-crop-kitchen-neutral-01.jpg` | `5fbce7ddb3c0fbc53a9e92c0dcc32a3988762c95ac7b54e50907262c8bb9c58c` |
| `zuv` | `zuv_identity_face_crop` | `references/identity/zuv/face/zuv-face-crop-balcony-neutral-01.jpg` | `43d0e147563b55237b79646684945044a12a0f9152f7fbd3b12ea3a74bb7f3f8` |
| `zuv` | `zuv_identity_face_crop` | `references/identity/zuv/face/zuv-face-crop-balcony-neutral-03.jpg` | `53388d76cb1c48ac83900bcf984f934967a793a7525cbfe96a7b9eaad6e80c96` |
| `zuv` | `zuv_identity_face_crop` | `references/identity/zuv/face/zuv-face-crop-balcony-neutral-02.jpg` | `e8d36169b631031e09a74ce565793b3407754e7d8ef5707d610f734f0b6dbdc4` |
| `zuv` | `zuv_identity_face_crop` | `references/identity/zuv/face/zuv-face-crop-dinner-smile-02.jpg` | `9841e823f486e5d0c1baece63178256e76aa1f5047e367c6dbcf6a98e0458479` |
| `couple` | `couple_relationship_reference` | `references/identity/together/face-and-body-language/together-casual-icecream-standing-01.jpg` | `86757dcf414e8a857cbfb2d3215e7a85fb7cec1bfaf8c79c6c9cb782bc08f7fe` |
| `couple` | `couple_relationship_reference` | `references/identity/together/face-and-body-language/together-cabin-hug-01.jpg` | `3a156a35d760a69e496b5b0f0c22ede0e59907f7cfb444ec39f08472b1ea9e09` |
| `style` | `style_reference` | `references/style/observational-intimacy-premium/contact-sheet.png` | `3fdc6819a2ae3707473e7006a77ad9fd95b846c8ce61aeb2e5724d4ec2ee7b05` |
| `style` | `style_reference` | `references/style/observational-intimacy-premium/slide-01.png` | `0f3ca21892cdee67eabd0acc57093758475973ec7fcea13ab582c62382367c7f` |
| `style` | `style_reference` | `references/style/observational-intimacy-premium/slide-02.png` | `7fcf94b8897db82d7cf7bcb9beb57eb683257f8a2c493a6c2ce4f849a8fd28c4` |
| `style` | `style_reference` | `references/style/observational-intimacy-premium/slide-03.png` | `d6d3e59fcfcfd6491a387bd582bcf16263b368fe35b0bec2d81b981df62fbb00` |
| `style` | `style_reference` | `references/style/observational-intimacy-premium/slide-04.png` | `bf52e6d1562dfa73dab4140bbb6b071c9e271e8a6ad7b0cb8d05b73369e94c54` |
| `style` | `style_reference` | `references/style/observational-intimacy-premium/slide-05.png` | `4cf7bbe3fd538a1edafcb25aa3b846557fb43312044c9a4be2ced92f9e0f99a6` |
| `style` | `style_reference` | `references/style/observational-intimacy-premium/slide-06.png` | `cc0608af1fe74878427c7ae35293d138f8a8a85b7293bab912a6895cdbf10fbb` |
| `style` | `style_reference` | `references/style/observational-intimacy-premium/slide-07.png` | `d8b26f7469e5130200939e57e6d457b0ab7b4c259d9206e9049e7d11c47fdf2a` |
| `style` | `style_reference` | `references/style/observational-intimacy-premium/slide-08.png` | `7e3bad705d5e7d5381d1ec460fe78bdecb23085195db2d5fc3b8709e4a44c67d` |

## Role-Based Dossier Proof

Dossier: `references/identity/_dossier/identity-dossier.json`

- Status: `pass`
- Dossier status: `READY_WITH_ROLE_BASED_REFERENCES`
- Minimum clean face anchors required per person: `4`
- Aachu face anchors: `9`
- Zuv face anchors: `8`
- Role reference inputs indexed: `51`

| Subject/group | Role | Quality | Path | SHA-256 |
| --- | --- | --- | --- | --- |
| `aachu` | `face_anchor` | `primary` | `references/identity/aachu/face/aachu-face-crop-car-purple-01.jpg` | `5de7bf34c52d0fd7f59e216343c974c643d2f7bac4b50676ede85b61605fcf5d` |
| `aachu` | `face_anchor` | `primary` | `references/identity/aachu/face/aachu-face-crop-cafe-neutral-01.jpg` | `70edc1e0795fc36a7a380c3e0a77d9ed5b46c2efda8b11c6ded3e0066bc5cc2c` |
| `aachu` | `face_anchor` | `primary` | `references/identity/aachu/face/aachu-face-crop-home-black-01.jpg` | `0d42f196b01aeb95b11d863feb36c7b4cbacfa0723f027f75ca272d42a4ea67c` |
| `aachu` | `face_anchor` | `support` | `references/identity/aachu/face/aachu-face-crop-kitchen-neutral-01.jpg` | `5fbce7ddb3c0fbc53a9e92c0dcc32a3988762c95ac7b54e50907262c8bb9c58c` |
| `zuv` | `face_anchor` | `primary` | `references/identity/zuv/face/zuv-face-crop-balcony-neutral-01.jpg` | `43d0e147563b55237b79646684945044a12a0f9152f7fbd3b12ea3a74bb7f3f8` |
| `zuv` | `face_anchor` | `primary` | `references/identity/zuv/face/zuv-face-crop-balcony-neutral-03.jpg` | `53388d76cb1c48ac83900bcf984f934967a793a7525cbfe96a7b9eaad6e80c96` |
| `zuv` | `face_anchor` | `primary` | `references/identity/zuv/face/zuv-face-crop-balcony-neutral-02.jpg` | `e8d36169b631031e09a74ce565793b3407754e7d8ef5707d610f734f0b6dbdc4` |
| `zuv` | `face_anchor` | `primary` | `references/identity/zuv/face/zuv-face-crop-dinner-smile-02.jpg` | `9841e823f486e5d0c1baece63178256e76aa1f5047e367c6dbcf6a98e0458479` |
| `aachu` | `smile` | `primary` | `references/identity/aachu/smiles/aachu-smile-tan-shirt-01.jpg` | `8fa213dd0480fd1b49c839f4e51769af8c0e65b1586b6715ccab9f0729acfaa1` |
| `aachu` | `smile` | `primary` | `references/identity/aachu/smiles/aachu-smile-jewelry-close-01.jpg` | `658b6e718d61a0c1f6c4f46f5f6dc551d27bc11a2aedb2442e7ce2bbdf3903b3` |
| `zuv` | `smile` | `primary` | `references/identity/zuv/smiles/zuv-smile-dinner-close-01.jpg` | `afe94683280145d50994a3f6f8d9b83dcb27fa8474412d860b6de8739482f51c` |
| `zuv` | `smile` | `support` | `references/identity/zuv/smiles/zuv-smile-balcony-laugh-01.jpg` | `c7a8ad39d802e4cd6f9bf27112bcc46fe13ef2040d0a2576b4e45ca5b7ff7e3a` |
| `together` | `together_body_language` | `primary` | `references/identity/together/face-and-body-language/together-casual-icecream-standing-01.jpg` | `86757dcf414e8a857cbfb2d3215e7a85fb7cec1bfaf8c79c6c9cb782bc08f7fe` |
| `together` | `together_body_language` | `primary` | `references/identity/together/face-and-body-language/together-cabin-hug-01.jpg` | `3a156a35d760a69e496b5b0f0c22ede0e59907f7cfb444ec39f08472b1ea9e09` |

## Workflow Readiness

- Status: `ready`
- Workflow file: `runs/2026-06-07_17-57_auto/local-workflows/identity-proof-comfyui.json`
- Workflow file exists: `True`
- Execution engine: `ComfyUI local server`

## Non-Final Identity Proof Request

Aachu and Zuv side-by-side, face-forward enough for creator identity review, neutral pose, no story text, no brandmark, no shawl.

## Smallest Next Step

Refresh the dry-run proof and local stack discovery before any model execution:

```bash
python3 scripts/local_identity_pipeline.py --run-id 2026-06-07_17-57_auto --workflow-id option_b_sdxl_instantid_pulid_ipadapter --workflow-file runs/2026-06-07_17-57_auto/local-workflows/identity-proof-comfyui.json --dry-run
```

Then check:

- `runs/2026-06-07_17-57_auto/evals/local_identity_stack_discovery_report.md`
- `runs/2026-06-07_17-57_auto/evals/local_model_setup_approval_request.md`

If the workflow file or required local model weights are absent, keep the run blocked and do not generate carousel slides.
