# Image Quality Eval Report

Run: `2026-06-19_21-09_ghar-line`

Status: `failed_wrong_canvas_size_and_reference_pose_copy`

Slide 1 was generated twice in the corrected iteration 2 lane. Both attempts are rejected. They failed the native canvas hard gate and also copied too much of the cafe identity reference's smile, cup/table pose, jacket, and pleasant emotional state.

## Attempts

- `images/slide_01_iteration_02_attempt_01_candidate.png`: `1122x1402`, rejected for `WRONG_CANVAS_SIZE`, `IDENTITY_REFERENCE_POSE_COPY`, and `SMILING_CONTRADICTS_ACHE`.
- `images/slide_01_iteration_02_attempt_02_candidate.png`: `1122x1402`, rejected for `WRONG_CANVAS_SIZE`, `IDENTITY_REFERENCE_POSE_COPY`, and `SMILING_CONTRADICTS_ACHE`.

## Observed Strengths

- Zuv does not appear or return.
- The on-image text appears readable and exact.
- The top-right `@a.storyof.two` brandmark is present.

## Blocking Failure

The A Story contract requires native `1080x1350 px` final illustration output. The built-in imagegen path returned `1122x1402` on both the initial prompt and the targeted retry. Do not resize, crop, or pad these candidates into finals.

The creator also rejected the emotional/identity route: Aachu is smiling, and the image looks like the cafe identity photo was superimposed into watercolor. Do not treat a reference smile/cup pose as scene proof. Identity references are face structure only.

## Decision

Stop before slide 2. Final package remains blocked.
