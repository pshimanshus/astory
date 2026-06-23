# HITL Approvals

Run: `2026-06-11_23-45_reel-side-eye`

## Approval Log

## HITL Idea Lock

- Timestamp: `2026-06-12T00:05+05:30`
- Status: approved (with revision)
- Decision: `approved`
- Approved artifact paths: `planning/selected_idea.json`, `debates/idea_room/`, `evals/idea_engagement_eval.json`
- Selected: `merged_reel_side_eye_v2` — "POV: You Left My Reel On Seen", 4-slide escalation carousel, score 4.6.
- Creator revision: slide 3 text was unclear ("I can see the 'seen'. I am seeing you." required explanation). Creator chose replacement: **"you watched it. and said NOTHING."** Beat unchanged (opened-but-no-reaction).
- Risks shown to creator: slide-3 close-up identity-drift hot zone; playful-not-angry side-eye; no rendered phone UI; pivot must be behavioral.
- Agent assignment status: `fallback_local_passes_with_limitation_recorded`
- Creator notes: "Perfect. Let's continue with the first one. I think it's okay."
- Next state: `GENERATE_STORY_CONCEPT`

## HITL Story Lock

- Timestamp: `2026-06-12T00:25+05:30`
- Status: approved (with revision)
- Decision: `approved`
- Approved artifact paths: `planning/slide_beat_map.json`, `planning/scene_options.json`, `planning/selected_scenes.json`, `planning/slide_count_decision.md`
- 4-slide count and scenes 1a/2a/3a approved as presented.
- Creator revision: slide 4 pivot "save them for us" rejected as bland. Creator selected pivot option A (same-reel twist): scene 4d, text "...you were sending me the SAME reel."
- Risks shown to creator: slide-4 two-phone hand composition; same-evening wardrobe continuity.
- Agent assignment status: `fallback_local_passes_with_limitation_recorded`
- Creator notes: "A. With such detailed prompts and research A has to be the only option."
- Next state: `CREATE_CHARACTER_BIBLE`

## HITL Prompt Lock

- Timestamp: `2026-06-12T23:22:32+05:30`
- Status: approved
- Decision: `approved`
- Artifact paths under review: `prompts/slide_01_4x5_prompt.txt` … `prompts/slide_04_4x5_prompt.txt`, `debates/prompt_room/prompt_review.md`, `evals/pre_generation_eval.json`
- Agent assignment status: `fallback_local_passes_with_limitation_recorded`
- Creator notes: `/astory resume 2026-06-11_23-45_reel-side-eye run this and create illustrations`
- Next state: `LOAD_REFERENCE_IMAGES_IN_CONTEXT` (Codex session)

## HITL Image QA

- Timestamp: `2026-06-12T23:36:30+05:30`
- Status: rejected
- Decision: `rejected_after_creator_review`
- Rejected artifact paths: `images/slide_01_4x5_attempt_01_candidate.png`, `images/slide_02_4x5_attempt_01_candidate.png`
- Failure codes: `YELLOW_PAPER_CAST`, `IDENTITY_DRIFT`, `STYLE_DRIFT`, `PROMPT_OVERLOAD`
- Creator notes: "nothing in the final image generated matches what I expect"; yellow/parchment cast, no face consistency, no real face match, anime/cartoon style despite references.
- Next state: `RETRY_OR_REVISE_IF_NEEDED` after reference/prompt pipeline repair.

## HITL Prompt Repair / Reapproval Required

- Timestamp: `2026-06-13T00:56:09+05:30`
- Status: reapproval_required
- Decision: `blocked_until_creator_reapproval`
- Repaired artifact paths: `prompts/slide_01_4x5_prompt.txt` … `prompts/slide_04_4x5_prompt.txt`, `evals/imagegen_reference_load_plan.json`, `references-used/selected_references.json`
- Superseded artifact paths: `evals/imagegen_reference_visibility_proof.json`, `evals/review_room_imagegen_blocker_check.json`
- Failure codes addressed in pipeline: `IDENTITY_REFERENCE_INPUT_UNPROVEN`, `PROMPT_PALETTE_CONFLICT`, `GENERATION_CONTINUED_AFTER_HARD_REJECT`
- Note: no new imagegen is allowed until raw face-anchor inputs are loaded with `view_image`, a fresh visibility proof is written, repo QA runs again, and the creator approves the repaired prompt/reference setup.
- Next state: `HITL_PROMPT_LOCK`

## HITL Prompt Repair / Reapproval Required - Compact Prompt Pass

- Timestamp: `2026-06-13T01:59:09+05:30`
- Status: reapproval_required
- Decision: `blocked_until_creator_reapproval`
- Repaired artifact paths: `prompts/slide_01_4x5_prompt.txt` … `prompts/slide_04_4x5_prompt.txt`, `.agents/skills/astory/references/master-prompt.md`, `.agents/skills/astory/templates/prompts/slide_prompt.txt`, `evals/imagegen_reference_visibility_proof.json`
- Failure codes addressed in pipeline: `PROMPT_OVERLOAD`, `IDENTITY_REFERENCE_INPUT_UNPROVEN`, `PROMPT_PALETTE_CONFLICT`, `GENERATION_CONTINUED_AFTER_HARD_REJECT`
- Evidence: prompt overload QA now passes with 8 major sections and 18 non-empty lines per slide prompt; reference visibility proof now matches the current load-plan hash and includes 4 raw Aachu face anchors, 4 raw Zuv face anchors, and 3 style refs loaded with `view_image`.
- Remaining blocker: `HITL_NOT_APPROVED` until creator approves this repaired prompt/reference setup.
- Next allowed generation step after approval: slide 1 only.

## HITL Prompt Repair Reapproval

- Timestamp: `2026-06-13T12:31:05+05:30`
- Status: approved
- Decision: `approved`
- Approved artifact paths: `prompts/slide_01_4x5_prompt.txt` … `prompts/slide_04_4x5_prompt.txt`, `evals/imagegen_reference_load_plan.json`, `evals/imagegen_reference_visibility_proof.json`, `evals/repo_qa_review.json`
- Creator notes: "let;s create the coursel in a story of two tyle with the concept we closed"
- Scope constraint: proceed with the repaired prompt/reference setup, then generate slide 1 only before any additional slides.
- Next state: `LOAD_REFERENCE_IMAGES_IN_CONTEXT`

## Final Package

- Timestamp: `not started`
- Status: not started
- Decision: `pending`
- Note: runs in Codex session after image QA.
