# HITL Approvals

Run: `2026-06-15_19-09_plate-nervous`

## Approval Log

## Idea Lock

- Timestamp: `2026-06-15T19:09:00+05:30`
- Status: approved
- Decision: approved by direct creator request to create an A Story-style illustration from the current food-stealing carousel direction.
- Approved artifact paths: `runs/2026-06-15_19-09_plate-nervous/planning/selected_idea.json`, `runs/2026-06-15_19-09_plate-nervous/planning/scene_landing_preview.md`
- Risks shown to creator: generic eating-together scene, weak plate danger, quote-card romance.
- Agent assignment status: fallback_local_passes_with_limitation_recorded
- Creator notes: direct chat request: `create [$astory] ... styke illustration`
- Next state: `HITL_STORY_LOCK`

## Story / Slide Count Lock

- Timestamp: `2026-06-15T19:09:00+05:30`
- Status: approved
- Decision: scoped to one first-slide proof-of-style illustration, not a full carousel package.
- Approved artifact paths: `runs/2026-06-15_19-09_plate-nervous/planning/story_concept.json`, `runs/2026-06-15_19-09_plate-nervous/planning/slide_count_decision.md`, `runs/2026-06-15_19-09_plate-nervous/planning/slide_beat_map.json`, `runs/2026-06-15_19-09_plate-nervous/planning/selected_scenes.json`
- Risks shown to creator: one-slide proof cannot validate full carousel pacing; text rendering may need repair after imagegen.
- Agent assignment status: fallback_local_passes_with_limitation_recorded
- Creator notes: proceed with the slide-1 proof image.
- Next state: `HITL_PROMPT_LOCK`

## Prompt Lock

- Timestamp: `2026-06-15T19:28:00+05:30`
- Status: approved
- Decision: proceed under creator's direct "create" instruction.
- Approved artifact paths: `runs/2026-06-15_19-09_plate-nervous/prompts/slide_01_prompt.txt`, `runs/2026-06-15_19-09_plate-nervous/debates/prompt_room/prompt_review.md`, `runs/2026-06-15_19-09_plate-nervous/evals/imagegen_reference_visibility_proof.json`
- Risks shown to creator: built-in imagegen has no explicit image-input field; references are loaded in current context and recorded, but identity must still be QA-blocked if rendered faces drift.
- Agent assignment status: fallback_local_passes_with_limitation_recorded
- Creator notes: create the illustration.
- Next state: `GENERATE_IMAGES_WITH_IMAGEGEN`

## Image QA

- Timestamp: `2026-06-15T21:33:30+05:30`
- Status: retry
- Decision: creator promoted `slide_01_attempt_01_candidate.png` as the strongest Aachu/Zuv face-match baseline so far, but requested repair before final: Aachu's eyes must not read cross-eyed, final surface must be native 1080x1350 px portrait, and brandmark must move to top-right.
- Approved artifact paths: `runs/2026-06-15_19-09_plate-nervous/images/slide_01_attempt_01_candidate.png` as identity-match baseline evidence only; `runs/2026-06-15_19-09_plate-nervous/planning/creator_direction_notes.md`
- Risks shown to creator: candidate is 1254x1254, brandmark is bottom-right, quote/apostrophe text is malformed, and Aachu's eye direction needs repair.
- Agent assignment status: not_applicable
- Creator notes: preserve the exact generation route and artifact trail as the gold-standard process for future face match.
- Next state: `RETRY_OR_REVISE_IF_NEEDED`

## Final Package

- Timestamp: `2026-06-15T19:28:00+05:30`
- Status: not started
- Decision: final package is not started before image QA.
- Approved artifact paths: none yet.
- Risks shown to creator: no export can be called final without image QA and final approval.
- Agent assignment status: not_applicable
- Creator notes: final package waits for image QA.
- Next state: `IMAGE_QUALITY_EVAL`
