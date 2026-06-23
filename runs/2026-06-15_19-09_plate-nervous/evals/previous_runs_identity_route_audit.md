# Previous Runs Identity Route Audit

Run: `2026-06-15_19-09_plate-nervous`

Purpose: answer whether the face-match success came from a process we had "been doing forever," or from a newly complete combination of gates, references, prompt weighting, and scene constraints.

## Short Answer

Older runs had pieces of this route, but not the same complete route with a creator-approved face-match outcome.

The `plate-nervous` candidate is different because it combined:

- raw Aachu/Zuv face anchors in the active `view_image_queue`
- `imagegen_reference_visibility_proof.json` confirming 11 of 11 references loaded in the current conversation
- `pre_generation_eval.json` with agent-assignment limitation recorded
- `agent_assignment_matrix.md`
- `prompt_room/prompt_review.md`
- `scene_landing_preview.md`
- `scene_options.json`, `selected_idea.json`, `slide_beat_map.json`, `slide_count_decision.md`
- a compact single-slide `slide_01_prompt.txt`
- a medium-wide face-readable scene with identity-friendly expressions
- one generated candidate that the creator explicitly promoted as the best Aachu/Zuv face match so far

## Comparison Runs

### `2026-06-07_17-57_auto`

Had some reference loading, but the creator rejected identity.

Evidence:

- `runs/2026-06-07_17-57_auto/evals/reference_input_proof_report.md`
- `runs/2026-06-07_17-57_auto/evals/image_quality_creator_rejection_report.md`
- `runs/2026-06-07_17-57_auto/debates/image_qa_room/image_qa_debate.md`

Key finding:

- The report says references were loaded with `view_image`, but creator verdict was `faces are still not matching at all`.
- The run itself concludes that visible references did not prove explicit image-input delivery for identity preservation.
- Earlier internal QA was too lenient: it scored face match around 3.8-3.9, but creator QA superseded it with `IDENTITY_DRIFT`.

Difference from `plate-nervous`:

- Not the current raw-identity-first manifest/proof route.
- No equivalent complete scene-landing + prompt-room + visibility-proof + compact-prompt chain that produced a creator-promoted identity result.

### `2026-06-10_22-22_heart-rent`

Had many attempts and eventually cleaned references, but the route was unstable and not final-approved.

Evidence:

- `runs/2026-06-10_22-22_heart-rent/evals/image_quality_eval.json`
- `runs/2026-06-10_22-22_heart-rent/evals/repo_qa_review.md`

Key finding:

- Multiple candidates were rejected for `IDENTITY_DRIFT`, `STYLE_DRIFT`, wrong aspect ratio, missing brandmark, Aachu age drift, and missing couple energy.
- Attempt 10 improved Aachu and couple energy but was still `pending_creator_image_qa`.
- Current repo QA marks blockers including stale visibility proof, missing scene landing preview, incomplete agent assignment proof, prompt overload, and old canvas/brandmark contract mismatch.

Difference from `plate-nervous`:

- Not a clean one-pass route.
- Too many retries, overloaded prompt history, stale proof, and no creator-promoted final face-match baseline.

### `2026-06-10_22-55_couple-banter`

Had a serious route: actual multi-agent assignment, reference load plan, 19 loaded references, pre-gen eval, prompt approval, and imagegen.

Evidence:

- `runs/2026-06-10_22-55_couple-banter/logs/trace.jsonl`
- `runs/2026-06-10_22-55_couple-banter/evals/pre_generation_eval_report.md`
- `runs/2026-06-10_22-55_couple-banter/evals/image_quality_eval.json`

Key finding:

- Automated QA scored identity high, but creator rejected the exports.
- Creator rejection: faces were too fat/round, Aachu looked old/unclear, she was buried in the sofa, and the couple energy was not satisfactory.
- The run generated multiple surfaces, which increased canvas/composition pressure.

Difference from `plate-nervous`:

- The pipeline existed, but the final rendered identity did not pass creator taste.
- Scene/composition hurt identity: Aachu was visually stuffed/buried, unlike `plate-nervous`, where both faces stayed readable and clean.

### `2026-06-11_23-45_reel-side-eye`

This is the clearest failed predecessor.

Evidence:

- `runs/2026-06-11_23-45_reel-side-eye/evals/image_quality_report.md`
- `runs/2026-06-11_23-45_reel-side-eye/evals/image_quality_eval.json`
- `runs/2026-06-11_23-45_reel-side-eye/evals/review_room_imagegen_blocker_check.json`

Key finding:

- It had manifest/proof artifacts, but the active queue used binder/contact-sheet images, not raw high-resolution identity photos.
- The report says binder thumbnails weakened the face-match signal.
- It also had warm/yellow prompt conflict and prompt overload.
- Creator rejected candidates for `YELLOW_PAPER_CAST`, `IDENTITY_DRIFT`, and `STYLE_DRIFT`.

Difference from `plate-nervous`:

- `plate-nervous` used raw Aachu/Zuv face anchors directly in the active queue:
  - 4 Aachu raw face anchors
  - 4 Zuv raw face anchors
  - 3 style references
- No binder-only proof. No warm/yellow prompt conflict. Compact prompt.

### `2026-06-14_17-51_ig-reference-concept`

Had strong idea/story agent work and references, but it was not the same identity-generation route.

Evidence:

- `runs/2026-06-14_17-51_ig-reference-concept/logs/trace.jsonl`
- `runs/2026-06-14_17-51_ig-reference-concept/references-used/selected_references.json`
- `runs/2026-06-14_17-51_ig-reference-concept/evals/imagegen_reference_visibility_proof.json`

Key finding:

- Strong actual multi-agent work happened around concept/idea/story.
- It did not have the same full prompt-room + pre-generation eval + compact `slide_01_prompt.txt` route that produced this face-match candidate.

Difference from `plate-nervous`:

- Not the same single-slide identity proof loop.
- The `plate-nervous` run tied identity proof, prompt compactness, scene readability, and post-image creator QA into one traceable route.

## Why `plate-nervous` Captured Identity Better

1. Raw references were active, not just documented.
2. There were exactly enough face anchors: 4 Aachu + 4 Zuv, not a diluted contact-sheet/binder setup.
3. Style references were explicitly demoted to style only, not allowed to replace identity.
4. The prompt put identity first before scene, text, and style.
5. The prompt was compact: fewer competing instructions than the overloaded failed runs.
6. The scene made both faces readable: medium-wide, front three-quarter, simple living-room setup.
7. The emotional action was small and natural: suspicious side glance and mischievous plate attention.
8. There was one candidate, not a batch of multi-surface outputs.
9. Image QA came from the actual rendered output and creator verdict, not just internal scoring.

## Current Lesson

We were trying versions of this before, but the whole route was not consistently present, and prior outputs were often rejected for identity drift. The `plate-nervous` route is the first captured evidence where the full chain produced a creator-promoted Aachu/Zuv face-match baseline.
