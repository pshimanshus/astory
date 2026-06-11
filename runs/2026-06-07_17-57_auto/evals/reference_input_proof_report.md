# Reference Input Proof Report

Run: `2026-06-07_17-57_auto`

## Status

`blocked`

Creator verdict recorded at `2026-06-08T07:39:42+05:30`:

`faces are still not matching at all`

Generated smoke-test candidate:

`runs/2026-06-07_17-57_auto/images/identity_smoke_test_builtin_context_01.png`

Source cache:

`/Users/himanshusharma/.codex/generated_images/019ea20b-c45f-7dd2-a0f6-d60671547f75/ig_0f91ce6a40ee188d016a259db960bc8191bf7c3ba5b1335dad.png`

## Superseded By Role-Based Library

This failed context smoke test is retained as historical evidence only. Its legacy flat portrait/face paths are no longer the active generation reference call.

Current reference sources:

- Dossier: `references/identity/_dossier/identity-dossier.json`
- Active manifest: `runs/2026-06-07_17-57_auto/references-used/selected_references.json`
- Local proof: `runs/2026-06-07_17-57_auto/evals/local_identity_reference_proof.json`
- Aachu default face inputs: `references/identity/aachu/face/aachu-face-crop-car-purple-01.jpg`, `references/identity/aachu/face/aachu-face-crop-cafe-neutral-01.jpg`, `references/identity/aachu/face/aachu-face-crop-home-black-01.jpg`, `references/identity/aachu/face/aachu-face-crop-kitchen-neutral-01.jpg`
- Zuv default face inputs: `references/identity/zuv/face/zuv-face-crop-balcony-neutral-01.jpg`, `references/identity/zuv/face/zuv-face-crop-balcony-neutral-03.jpg`, `references/identity/zuv/face/zuv-face-crop-balcony-neutral-02.jpg`, `references/identity/zuv/face/zuv-face-crop-dinner-smile-02.jpg`

## What This Test Proves

- The selected identity and style references were loaded visibly with `view_image` immediately before generation.
- The built-in imagegen output picked up more identity-specific cues than the rejected carousel images.
- The output was saved into the run folder and can be reviewed as a non-final identity proof.

## What This Test Does Not Prove

- It does not prove explicit API-style image input delivery.
- The current built-in `image_gen` tool in this session exposes only a `prompt` argument, so this remains a context-based smoke test rather than a guaranteed image-input workflow.

## Creator QA

`fail`

Failure code: `IDENTITY_DRIFT`

The built-in context smoke test is rejected. Do not proceed with built-in context imagegen for final Aachu/Zuv artwork.

## Earlier Provisional QA

- Aachu: substantially closer than the rejected carousel outputs; recognizable cues include long dark hair, brows, smile, face shape, and wardrobe.
- Zuv: closer than the rejected carousel outputs; recognizable cues include beard, brows, skin tone, and hair volume, but the illustration still stylizes him and needs creator review.
- Style: matches the observational watercolor-and-ink direction well enough for a smoke test.

## Decision Needed

The creator judged the face match insufficient. Built-in context generation is blocked for final identity-sensitive output.

Required next path:

- Move to an explicit image-input API/edit path where Aachu/Zuv references are passed as actual image inputs, or keep this run blocked.
- Do not retry with stronger text prompts only.
