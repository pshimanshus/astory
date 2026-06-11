# Image Quality Report

Run: `2026-06-10_22-55_couple-banter`

## Status

`pass_pending_creator_image_qa_approval`

## Selected Exports

- `exports/slide_01_4x5.png` from `images/slide_01_4x5_attempt_02_candidate.png`
- `exports/slide_01_9x16.png` from `images/slide_01_9x16_attempt_01_candidate.png`
- `exports/slide_02_4x5.png` from `images/slide_02_4x5_attempt_01_candidate.png`
- `exports/slide_02_9x16.png` from `images/slide_02_9x16_attempt_01_candidate.png`

## Scores

- Slide 01 4:5: `4.76`
- Slide 01 9:16: `4.75`
- Slide 02 4:5: `4.74`
- Slide 02 9:16: `4.76`
- Overall: `4.75`

## Hard Failures

- Rejected `images/slide_01_4x5_attempt_01_candidate.png`: generated as `1003 x 1568`, which is too tall for native 4:5 post delivery.

## Required Retry Delta

Completed retry:

- Regenerated slide 01 4:5 with strict native 4:5 aspect-ratio instructions.

## Final Decision

The four selected exports pass automated image QA and are ready for creator Image QA approval. Final package remains pending until creator approval.
