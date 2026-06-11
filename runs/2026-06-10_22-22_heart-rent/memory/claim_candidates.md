# Memory Claim Candidates

Run: `2026-06-10_22-22_heart-rent`

## `claim:03a4931fb5a18cea`

- Type: `creator_preference`
- Status: `candidate`
- Promotion policy: `human_review`
- Risk: `high`
- Confidence: `0.93`
- Evidence: `runs/2026-06-10_22-22_heart-rent/docs/approvals.md`, `runs/2026-06-10_22-22_heart-rent/evals/image_quality_eval.json`

Creator rejected an output where Aachu looked old; future retries for this concept must preserve youthful Aachu face identity from the approved anchors.

## `claim:183fb06cca8b8465`

- Type: `failure_mode`
- Status: `quarantined`
- Promotion policy: `quarantine`
- Risk: `medium`
- Confidence: `0.97`
- Evidence: `runs/2026-06-10_22-22_heart-rent/evals/image_quality_eval.json`

Rejected export `runs/2026-06-10_22-22_heart-rent/exports/slide_01_post_4x5.png` must not be promoted as final artwork or a style anchor.

## `claim:88f81213cad79449`

- Type: `failure_mode`
- Status: `candidate`
- Promotion policy: `auto_apply`
- Risk: `low`
- Confidence: `0.98`
- Evidence: `runs/2026-06-10_22-22_heart-rent/evals/image_quality_eval.json`

A filename containing accepted_candidate is not final acceptance proof; final status must come from explicit image QA and creator approval evidence.

## `claim:a05114b59588d9f3`

- Type: `creator_preference`
- Status: `candidate`
- Promotion policy: `human_review`
- Risk: `high`
- Confidence: `0.93`
- Evidence: `runs/2026-06-10_22-22_heart-rent/docs/approvals.md`, `runs/2026-06-10_22-22_heart-rent/evals/image_quality_eval.json`

Creator rejected a retry where couple energy was missing; future retries for this concept need visible closeness, shared attention, and affectionate body language.

## `claim:ed11d6f016d3b4e2`

- Type: `production_constraint`
- Status: `candidate`
- Promotion policy: `auto_apply`
- Risk: `medium`
- Confidence: `0.96`
- Evidence: `runs/2026-06-10_22-22_heart-rent/references-used/selected_references.json`

Final Aachu/Zuv imagegen for this run requires loading the queued local reference images with view_image; prompt-only generation is forbidden.
