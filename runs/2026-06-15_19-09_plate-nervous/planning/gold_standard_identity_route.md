# Gold Standard Identity Route

Run: `2026-06-15_19-09_plate-nervous`

## Creator Meaning

The creator clarified that "gold standard" means the exact route that produced the strongest Aachu/Zuv face match, not a general emotional connection, not the food-stealing idea, and not a simplified prompt trick.

The route to preserve is the whole artifact chain visible in the creator's screenshots:

- `debates/agent_assignment_matrix.md`
- `debates/prompt_room/prompt_review.md`
- `docs/approvals.md`
- `evals/imagegen_reference_visibility_proof.json`
- `evals/pre_generation_eval.json`
- `input/creative_brief.json`
- `logs/trace.jsonl`
- `planning/memory_recall.md`
- `planning/scene_landing_preview.md`
- `planning/scene_options.json`
- `planning/selected_idea.json`
- `planning/selected_scenes.json`
- `planning/slide_beat_map.json`
- `planning/slide_count_decision.md`
- `planning/story_concept.json`
- `prompts/slide_01_prompt.txt`
- the exact local reference visibility proof and raw image-loading sequence before imagegen

## Candidate Evidence

Original generated image path:
`/Users/himanshusharma/.codex/generated_images/019ecb38-9851-7180-8e0d-7359dff409a5/ig_003fdf7c0a91e946016a300b0264b88190b26e2a2d92256d5d.png`

Run-local candidate path:
`runs/2026-06-15_19-09_plate-nervous/images/slide_01_attempt_01_candidate.png`

Creator-shared candidate screenshot:
`runs/2026-06-15_19-09_plate-nervous/input/creator_gold_standard_candidate_shared.png`

Creator-shared process screenshots:

- `runs/2026-06-15_19-09_plate-nervous/input/creator_gold_standard_file_trail_01.png`
- `runs/2026-06-15_19-09_plate-nervous/input/creator_gold_standard_file_trail_02.png`
- `runs/2026-06-15_19-09_plate-nervous/input/creator_gold_standard_file_trail_03.png`

## Non-Negotiable Carryover

For future Aachu/Zuv generations, do not collapse this into "use good references." Repeat the route:

1. Create the full run artifact set before imagegen.
2. Prepare the local reference manifest.
3. Load the queued raw Aachu/Zuv/style images visibly in the current conversation.
4. Write `evals/imagegen_reference_visibility_proof.json`.
5. Write `evals/pre_generation_eval.json`.
6. Keep `logs/trace.jsonl` time-ordered.
7. Preserve the prompt-room review and the exact compact priority-stack prompt shape.
8. Generate one slide at a time.
9. QA the rendered face match from the actual output, not from the prompt or references alone.

Only the creator-requested final-output corrections should change on retry:
native `1080x1350 px`, top-right `@a.storyof.two`, exact text fidelity, and natural Aachu eye alignment.
