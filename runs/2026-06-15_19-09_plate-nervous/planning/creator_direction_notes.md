# Creator Direction Notes

## 2026-06-15 — Gold Standard Means The Full Identity-Match Route

Creator correction:
The gold standard from this session is not the food-stealing concept, the joke, or a vague "connection." The gold standard is the exact production route that produced the strongest Aachu/Zuv face match so far.

Rejected assumption:
Do not reduce this learning to "the image was emotionally good" or "the prompt concept worked." The creator is specifically praising the artifact path, reference visibility proof, evaluation trail, and prompt-room process that led to the render.

Gold-standard route to preserve:
- Run: `runs/2026-06-15_19-09_plate-nervous/`
- Dedicated route evidence note: `runs/2026-06-15_19-09_plate-nervous/planning/gold_standard_identity_route.md`
- Candidate copied from built-in imagegen output:
  `/Users/himanshusharma/.codex/generated_images/019ecb38-9851-7180-8e0d-7359dff409a5/ig_003fdf7c0a91e946016a300b0264b88190b26e2a2d92256d5d.png`
  to `runs/2026-06-15_19-09_plate-nervous/images/slide_01_attempt_01_candidate.png`
- Preserve the exact kind of evidence trail: `evals/imagegen_reference_visibility_proof.json`, `evals/pre_generation_eval.json`, `logs/trace.jsonl`, `planning/memory_recall.md`, `planning/scene_landing_preview.md`, `planning/scene_options.json`, `planning/selected_idea.json`, `planning/slide_beat_map.json`, `planning/slide_count_decision.md`, `debates/agent_assignment_matrix.md`, `debates/prompt_room/prompt_review.md`, and `prompts/slide_01_prompt.txt`.
- Preserve the creator-shared screenshots copied into `input/creator_gold_standard_candidate_shared.png`, `input/creator_gold_standard_file_trail_01.png`, `input/creator_gold_standard_file_trail_02.png`, and `input/creator_gold_standard_file_trail_03.png`.
- Preserve the raw-reference-first route: run `scripts/prepare_imagegen_reference_context.py`, load every queued Aachu/Zuv/style reference with `view_image`, write visibility proof, run pre-generation QA, then generate one slide at a time.
- Do not shortcut this into a text-only prompt, a remembered vibe, a binder-only proof, or a generic "use references" instruction.

New active constraints from the same correction:
- Future final A Story illustrations should be native `1080x1350 px` portrait, not square.
- The `@a.storyof.two` brandmark belongs at the top-right, tiny, low-contrast, and handwritten in the same house font.
- Aachu's eyes must stay natural and aligned. Do not copy a reference-frame eye-roll so literally that she looks cross-eyed; side-glance is allowed only when both pupils/eyelines read as physically coherent.
- The current candidate is the face-match gold-standard evidence, but it is not final publishing proof until the portrait canvas, top-right brandmark, exact text, and eye-direction QA pass.

Active constraint:
For future Aachu/Zuv imagegen, keep this run's artifact route as the identity-match baseline and update only the locked surface/brandmark/eye-direction constraints when regenerating.
