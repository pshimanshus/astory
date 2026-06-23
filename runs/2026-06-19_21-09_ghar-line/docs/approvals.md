# HITL Approvals

Run: `2026-06-19_21-09_ghar-line`

Use this file to record creator decisions before moving past human approval gates.

## Approval Log

## Idea Lock

- Status: approved
- Timestamp: `2026-06-19T21:57:55+05:30`
- Decision: `approved`
- Source gate: `HITL_IDEA_LOCK`
- Approved artifact paths: `runs/2026-06-19_21-09_ghar-line/input/creative_brief.json`, `runs/2026-06-19_21-09_ghar-line/planning/selected_idea.json`, `runs/2026-06-19_21-09_ghar-line/planning/creator_direction_notes.md`, `runs/2026-06-19_21-09_ghar-line/planning/scene_landing_preview.md`
- Risks shown to creator: `TEXT_UNREADABLE`, `QUOTE_CARD_NOT_ILLUSTRATION`, `AI_SLOP_COPY_DRIFT`, `GOLD_STANDARD_IDENTITY_ROUTE_MISSING`
- Agent assignment status: `actual_multi_agent`
- Creator notes: Creator supplied a repaired concept after rejecting the prior generic Slide 2.
- Next state: `GENERATE_STORY_CONCEPT`

## Story / Slide Count Lock

- Status: approved
- Timestamp: `2026-06-19T22:11:24+05:30`
- Decision: `approved`
- Source gate: `HITL_STORY_LOCK`
- Approved artifact paths: `runs/2026-06-19_21-09_ghar-line/planning/story_concept.json`, `runs/2026-06-19_21-09_ghar-line/planning/slide_count_decision.md`, `runs/2026-06-19_21-09_ghar-line/planning/slide_beat_map.json`, `runs/2026-06-19_21-09_ghar-line/planning/scene_options.json`, `runs/2026-06-19_21-09_ghar-line/planning/selected_scenes.json`
- Risks shown to creator: `TEXT_UNREADABLE`, `AI_SLOP_COPY_DRIFT`, `QUOTE_CARD_NOT_ILLUSTRATION`, `GOLD_STANDARD_IDENTITY_ROUTE_MISSING`
- Agent assignment status: `actual_multi_agent`
- Creator notes: Creator approved the 4-slide split and selected sofa-side scene sequence with "perfect; create the illustrations now ensuring identity matches."
- Next state: `CREATE_CHARACTER_BIBLE_AFTER_APPROVAL`

## Prompt Lock

- Status: approved
- Timestamp: `2026-06-19T22:11:24+05:30`
- Decision: `approved`
- Source gate: `HITL_PROMPT_LOCK`
- Approved artifact paths: `runs/2026-06-19_21-09_ghar-line/prompts/slide_01_prompt.txt`, `runs/2026-06-19_21-09_ghar-line/prompts/slide_02_prompt.txt`, `runs/2026-06-19_21-09_ghar-line/prompts/slide_03_prompt.txt`, `runs/2026-06-19_21-09_ghar-line/prompts/slide_04_prompt.txt`, `runs/2026-06-19_21-09_ghar-line/debates/prompt_room/prompt_review.md`, `runs/2026-06-19_21-09_ghar-line/evals/pre_generation_eval.json`
- Risks shown to creator: `IDENTITY_REFERENCE_INPUT_UNPROVEN`, `REFERENCE_VISIBILITY_PROOF_REQUIRED_BEFORE_FINAL_IMAGEGEN`, `YELLOW_PAPER_CAST`, `TEXT_UNREADABLE`, `QUOTE_CARD_NOT_ILLUSTRATION`
- Agent assignment status: `actual_multi_agent`
- Creator notes: Prompt lock approved from creator instruction to create the illustrations now while ensuring identity matches; imagegen still requires reference visibility proof first.
- Next state: `LOAD_REFERENCE_IMAGES_IN_CONTEXT`

### `HITL_IDEA_LOCK`

- Timestamp: `2026-06-19T21:10:01+05:30`
- Decision: `revise`
- Approved artifact paths: none
- Risks shown to creator: `AI_SLOP_COPY_DRIFT`, `QUOTE_CARD_NOT_ILLUSTRATION`, `TOO_FEW_SLIDES`
- Agent assignment status: `actual_multi_agent`
- Creator notes: Creator rejected the second-slide copy as fake-soft/generic and specifically rejected the "thak ke bhi aa jaana / main abhi bhi tumhara ghar hoon" lane.
- Next state: `RETRY_OR_REVISE_IDEA_COPY`

### `HITL_IDEA_LOCK`

- Timestamp: `2026-06-19T21:57:55+05:30`
- Decision: `approved`
- Approved artifact paths: `runs/2026-06-19_21-09_ghar-line/input/creative_brief.json`, `runs/2026-06-19_21-09_ghar-line/planning/selected_idea.json`, `runs/2026-06-19_21-09_ghar-line/planning/creator_direction_notes.md`, `runs/2026-06-19_21-09_ghar-line/planning/scene_landing_preview.md`
- Risks shown to creator: `TEXT_UNREADABLE`, `QUOTE_CARD_NOT_ILLUSTRATION`, `AI_SLOP_COPY_DRIFT`, `GOLD_STANDARD_IDENTITY_ROUTE_MISSING`
- Agent assignment status: `actual_multi_agent`
- Creator notes: Creator supplied a repaired two-slide concept and asked to create the illustration. Treat the repaired text as approved idea input while preserving story-led slide-count and prompt/imagegen gates.
- Next state: `GENERATE_STORY_CONCEPT`

### `HITL_STORY_LOCK`

- Timestamp: `2026-06-19T22:11:24+05:30`
- Decision: `approved`
- Approved artifact paths: `runs/2026-06-19_21-09_ghar-line/planning/story_concept.json`, `runs/2026-06-19_21-09_ghar-line/planning/slide_count_decision.md`, `runs/2026-06-19_21-09_ghar-line/planning/slide_beat_map.json`, `runs/2026-06-19_21-09_ghar-line/planning/scene_options.json`, `runs/2026-06-19_21-09_ghar-line/planning/selected_scenes.json`
- Risks shown to creator: `TEXT_UNREADABLE`, `AI_SLOP_COPY_DRIFT`, `QUOTE_CARD_NOT_ILLUSTRATION`, `GOLD_STANDARD_IDENTITY_ROUTE_MISSING`
- Agent assignment status: `actual_multi_agent`
- Creator notes: Creator approved the 4-slide split and selected sofa-side scene sequence with "perfect; create the illustrations now ensuring identity matches."
- Next state: `CREATE_CHARACTER_BIBLE_AFTER_APPROVAL`

### `HITL_PROMPT_LOCK`

- Timestamp: `2026-06-19T22:11:24+05:30`
- Decision: `approved`
- Approved artifact paths: `runs/2026-06-19_21-09_ghar-line/prompts/slide_01_prompt.txt`, `runs/2026-06-19_21-09_ghar-line/prompts/slide_02_prompt.txt`, `runs/2026-06-19_21-09_ghar-line/prompts/slide_03_prompt.txt`, `runs/2026-06-19_21-09_ghar-line/prompts/slide_04_prompt.txt`, `runs/2026-06-19_21-09_ghar-line/debates/prompt_room/prompt_review.md`, `runs/2026-06-19_21-09_ghar-line/evals/pre_generation_eval.json`
- Risks shown to creator: `IDENTITY_REFERENCE_INPUT_UNPROVEN`, `REFERENCE_VISIBILITY_PROOF_REQUIRED_BEFORE_FINAL_IMAGEGEN`, `YELLOW_PAPER_CAST`, `TEXT_UNREADABLE`, `QUOTE_CARD_NOT_ILLUSTRATION`
- Agent assignment status: `actual_multi_agent`
- Creator notes: Prompt lock approved from creator instruction to create the illustrations now while ensuring identity matches; imagegen still requires reference visibility proof first.
- Next state: `LOAD_REFERENCE_IMAGES_IN_CONTEXT`

### `HITL_STORY_LOCK`

- Timestamp: `2026-06-19T22:36:40+05:30`
- Decision: `superseded_previous_story_lock`
- Approved artifact paths: none
- Risks shown to creator: `VISUAL_SETTING_ASSUMPTION_DRIFT`, `SAD_GIRL_IN_CROWD_GENERIC`, `BACKGROUND_FACES_DISTRACTION`, `TEXT_UNREADABLE`, `FACE_DRIFT`
- Agent assignment status: `actual_multi_agent_previous_room_outputs_invalidated_for_iteration_02`
- Creator notes: Creator interrupted the domestic house/sofa visual lane and requested a second iteration fully from the girl's perspective, where she can be somewhere full of people and still feel lost and alone.
- Next state: `HITL_STORY_LOCK_FOR_ITERATION_02`

### `HITL_PROMPT_LOCK`

- Timestamp: `2026-06-19T22:36:40+05:30`
- Decision: `superseded_previous_prompt_lock`
- Approved artifact paths: none
- Risks shown to creator: `PROMPT_LOCK_INVALIDATED_BY_VISUAL_REVISION`, `VISUAL_SETTING_ASSUMPTION_DRIFT`
- Agent assignment status: `actual_multi_agent_previous_prompt_room_outputs_invalidated_for_iteration_02`
- Creator notes: Previous prompt pack was for the rejected domestic lane and must not be used for final imagegen.
- Next state: `CREATE_PROMPT_PACK_AFTER_ITERATION_02_STORY_LOCK`

### `HITL_STORY_LOCK`

- Timestamp: `2026-06-19T22:47:56+05:30`
- Decision: `revise_iteration_02_payoff`
- Approved artifact paths: none
- Risks shown to creator: `COMEBACK_PAYOFF_WEAKENS_ACHE`, `GENERIC_REUNION`, `ZUV_GHOSTING_OR_IMPLIED_RETURN`, `TEXT_DENSITY`
- Agent assignment status: `actual_multi_agent_previous_room_outputs_invalidated_for_iteration_02`
- Creator notes: Creator corrected that if Zuv comes back, the real impact is deceived/weakened. Iteration 2 must keep Zuv absent in every slide and make the final payoff a realization-through-absence, not a reunion.
- Next state: `HITL_STORY_LOCK_FOR_ITERATION_02_NO_COMEBACK`

### `HITL_STORY_LOCK`

- Status: approved
- Timestamp: `2026-06-19T23:08:38+05:30`
- Decision: `approved`
- Approved artifact paths: `runs/2026-06-19_21-09_ghar-line/planning/story_concept.json`, `runs/2026-06-19_21-09_ghar-line/planning/slide_count_decision.md`, `runs/2026-06-19_21-09_ghar-line/planning/slide_beat_map.json`, `runs/2026-06-19_21-09_ghar-line/planning/scene_options.json`, `runs/2026-06-19_21-09_ghar-line/planning/selected_scenes.json`, `runs/2026-06-19_21-09_ghar-line/planning/scene_landing_preview.md`
- Risks shown to creator: `SAD_GIRL_IN_CROWD_GENERIC`, `BACKGROUND_FACES_DISTRACTION`, `TEXT_UNREADABLE`, `COMEBACK_PAYOFF_WEAKENS_ACHE`, `ZUV_GHOSTING_OR_IMPLIED_RETURN`
- Agent assignment status: `fallback_local_passes_with_limitation_recorded`
- Creator notes: Creator said "Proceed with illustrations" after correcting that Zuv coming back would weaken the impact. Iteration 2 no-comeback cafe/friends lane is approved for prompt pack and imagegen gates.
- Next state: `CREATE_CHARACTER_BIBLE`

### `HITL_PROMPT_LOCK`

- Status: approved
- Timestamp: `2026-06-19T23:08:38+05:30`
- Decision: `approved`
- Approved artifact paths: `runs/2026-06-19_21-09_ghar-line/prompts/slide_01_prompt.txt`, `runs/2026-06-19_21-09_ghar-line/prompts/slide_02_prompt.txt`, `runs/2026-06-19_21-09_ghar-line/prompts/slide_03_prompt.txt`, `runs/2026-06-19_21-09_ghar-line/prompts/slide_04_prompt.txt`, `runs/2026-06-19_21-09_ghar-line/prompts/negative_prompt.txt`, `runs/2026-06-19_21-09_ghar-line/debates/prompt_room/prompt_review.md`, `runs/2026-06-19_21-09_ghar-line/evals/pre_generation_eval.json`
- Risks shown to creator: `IDENTITY_REFERENCE_INPUT_UNPROVEN`, `REFERENCE_VISIBILITY_PROOF_REQUIRED_BEFORE_FINAL_IMAGEGEN`, `TEXT_UNREADABLE`, `BACKGROUND_FACES_DISTRACTION`, `ZUV_VISIBLE_IN_NO_COMEBACK_LANE`
- Agent assignment status: `fallback_local_passes_with_limitation_recorded`
- Creator notes: Prompt lock treated as approved by the creator's instruction to proceed with illustrations from the corrected iteration 2 lane. Imagegen remains blocked until references are freshly visible and repo QA route gates pass.
- Next state: `LOAD_REFERENCE_IMAGES_IN_CONTEXT`

## Image QA

- Status: not started
- Timestamp: `2026-06-19T23:08:38+05:30`
- Decision: `pending_generated_candidates`
- Approved artifact paths: none
- Risks shown to creator: `TEXT_NOT_EXACT`, `BRANDMARK_MISSING`, `IDENTITY_DRIFT`, `ZUV_VISIBLE_IN_NO_COMEBACK_LANE`, `YELLOW_PAPER_CAST`
- Agent assignment status: `not_started`
- Creator notes: Image QA must run after generated candidates are saved under `runs/2026-06-19_21-09_ghar-line/images/`.
- Next state: `GENERATE_IMAGES_WITH_IMAGEGEN`

## Final Package

- Status: not started
- Timestamp: `2026-06-19T23:08:38+05:30`
- Decision: `blocked_until_image_qa_passes`
- Approved artifact paths: none
- Risks shown to creator: `QUOTE_CARD_NOT_ILLUSTRATION`, `FINAL_PACKAGE_STARTED_WHILE_BLOCKED`
- Agent assignment status: `not_started`
- Creator notes: Final package remains not started until imagegen candidates pass Image QA and final QA.
- Next state: `IMAGE_QUALITY_EVAL`

## HITL Image QA

- Status: failed
- Timestamp: `2026-06-19T23:30:09+05:30`
- Decision: `hard_reject`
- Approved artifact paths: none
- Rejected artifact paths: `runs/2026-06-19_21-09_ghar-line/images/slide_01_iteration_02_attempt_01_candidate.png`, `runs/2026-06-19_21-09_ghar-line/images/slide_01_iteration_02_attempt_02_candidate.png`
- Risks shown to creator: `WRONG_CANVAS_SIZE`, `IDENTITY_REFERENCE_POSE_COPY`, `SMILING_CONTRADICTS_ACHE`, `YELLOW_PAPER_CAST_WATCHPOINT`
- Agent assignment status: `fallback_local_passes_with_limitation_recorded`
- Creator notes: Both slide 1 iteration 2 attempts came out `1122x1402` instead of native `1080x1350 px`, and the creator rejected the smile/reference-photo superimposition. Stop before slide 2; do not resize/crop/pad or accept identity-reference pose copying into final artwork.
- Next state: `COMPLETE_OR_BLOCKED`

## Final Package

- Status: blocked
- Timestamp: `2026-06-19T23:30:09+05:30`
- Decision: `blocked`
- Approved artifact paths: none
- Risks shown to creator: `WRONG_CANVAS_SIZE`, `IDENTITY_REFERENCE_POSE_COPY`, `SMILING_CONTRADICTS_ACHE`, `FINAL_PACKAGE_STARTED_WHILE_BLOCKED`
- Agent assignment status: `not_started`
- Creator notes: Final package is blocked because no generated candidate passed native canvas Image QA or the creator's identity-expression correction.
- Next state: `COMPLETE_OR_BLOCKED`

## HITL Prompt Lock

- Status: invalidated
- Timestamp: `2026-06-19T23:40:00+05:30`
- Decision: `invalidated_process_failure`
- Approved artifact paths: none
- Invalidated artifact paths: `runs/2026-06-19_21-09_ghar-line/debates/prompt_room/prompt_review.md`, `runs/2026-06-19_21-09_ghar-line/evals/pre_generation_eval.json`, `runs/2026-06-19_21-09_ghar-line/prompts/slide_01_prompt.txt`
- Risks shown to creator: `FALLBACK_REVIEW_TREATED_AS_AGENT_PASS`, `EMOTIONAL_STATE_CONTRADICTION`, `IDENTITY_REFERENCE_POSE_COPY`, `HUMAN_CREATOR_BECAME_QA`
- Agent assignment status: `fallback_local_passes_invalid_for_imagegen_unlock`
- Creator notes: Creator challenged how the milestones, agents, reviewers, and QA passed a smiling/reference-copied image. Prompt lock is invalidated; no further imagegen may run until prompt review is rebuilt and reapproved.
- Next state: `RETRY_OR_REVISE_IF_NEEDED`
