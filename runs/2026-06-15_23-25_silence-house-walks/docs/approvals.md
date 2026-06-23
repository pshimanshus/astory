# Approvals

Run: `2026-06-15_23-25_silence-house-walks`

## Idea Lock

Status: approved

Decision: creator direct-lock. Use the supplied quote/concept as-is and do not run concept thinking.

Evidence:
- `runs/2026-06-15_23-25_silence-house-walks/planning/selected_idea.json`
- `runs/2026-06-15_23-25_silence-house-walks/planning/scene_landing_preview.md`

## Story / Slide Count Lock

Status: approved

Decision: one single illustration, not a carousel.

Evidence:
- `runs/2026-06-15_23-25_silence-house-walks/planning/story_concept.json`
- `runs/2026-06-15_23-25_silence-house-walks/planning/slide_count_decision.md`
- `runs/2026-06-15_23-25_silence-house-walks/planning/selected_scenes.json`

## Prompt Lock

Status: approved

Decision: prompt approved after targeted QA repair. The creator said "continue"; repairs preserved exact copy and single-illustration scope.

Evidence:
- `runs/2026-06-15_23-25_silence-house-walks/prompts/slide_01_prompt.txt`
- `runs/2026-06-15_23-25_silence-house-walks/debates/prompt_room/prompt_review.md`
- `runs/2026-06-15_23-25_silence-house-walks/evals/pre_generation_eval.json`
- `runs/2026-06-15_23-25_silence-house-walks/evals/imagegen_reference_visibility_proof.json`

## Image QA

Status: failed

Decision: all generated candidates rejected.

Evidence:
- `runs/2026-06-15_23-25_silence-house-walks/evals/image_quality_eval.json`
- `runs/2026-06-15_23-25_silence-house-walks/images/candidate_01_text_not_exact.png`
- `runs/2026-06-15_23-25_silence-house-walks/images/candidate_02_text_retry_01.png`
- `runs/2026-06-15_23-25_silence-house-walks/images/candidate_03_text_retry_02.png`

## Final Package

Status: blocked

Decision: no final package/export because image QA failed.

Note: this run intentionally does not pause for idea alternatives because the creator explicitly rejected concept thinking for this task.
