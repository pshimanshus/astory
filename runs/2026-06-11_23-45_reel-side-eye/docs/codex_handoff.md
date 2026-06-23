# Codex Handoff — 2026-06-11_23-45_reel-side-eye

This run was driven through a failed imagegen attempt and then repaired in Codex. The run is now blocked at prompt/reference reapproval; do not resume directly into imagegen.

## Resume command

`/astory resume 2026-06-11_23-45_reel-side-eye`

## What is already locked (do not redo)

- Idea lock: approved with revision — `docs/approvals.md` ## HITL Idea Lock
- Story lock: 4 slides, scenes 1a/2a/3a/4d, same-reel-twist pivot — ## HITL Story Lock
- Prompt pack: `prompts/slide_0{1..4}_4x5_prompt.txt` repaired after Image QA rejection; .md siblings are annotated docs of the same prompts.
- Prompt QA: `evals/pre_generation_eval.json` (pass; `agent_assignment_status: fallback_local_passes_with_limitation_recorded`)
- Prompt lock: old approval is superseded. Check `docs/approvals.md` ## HITL Prompt Repair / Reapproval Required.
- Rejected images remain rejected: `images/slide_01_4x5_attempt_01_candidate.png`, `images/slide_02_4x5_attempt_01_candidate.png`.

## Codex TODO (states 23-32)

1. Re-run agent discovery; upgrade Image QA / Review rooms to actual `multi_agent_v1` if visible.
2. Show the repaired prompt/reference setup to the creator and record fresh approval before loading references.
3. `python3 scripts/prepare_imagegen_reference_context.py --run-id 2026-06-11_23-45_reel-side-eye` (refresh sha), then `view_image` every path in the raw-identity-first `view_image_queue` in `evals/imagegen_reference_load_plan.json`; write a fresh `evals/imagegen_reference_visibility_proof.json`.
4. `python3 scripts/astory_repo_qa.py --run-id 2026-06-11_23-45_reel-side-eye --loop --max-iterations 2` — must clear `reference_visibility_proof` before imagegen.
5. Generate slide 1 only with built-in imagegen, native 4:5, exact on-image text, brandmark bottom-right. Trace `GENERATE_IMAGES_WITH_IMAGEGEN`.
6. Run Image QA on slide 1 before generating any later slide. If slide 1 has `YELLOW_PAPER_CAST`, `IDENTITY_DRIFT`, `STYLE_DRIFT`, `PROMPT_OVERLOAD`, text failure, or anatomy failure, stop and record Image QA.
7. If slide 1 passes Image QA, continue slides one at a time with QA between slides. Watch flags from pre-generation eval:
   - **Slide 3**: identity hot zone — exaggerated playful side-eye must stay within Aachu face anchors; reject caricature/drift.
   - **Slide 4**: two phones held face-to-face — check fingers/grips; screens must be plain glow, no UI on any slide.
   - All slides: neutral off-white paper (no yellow/parchment), playful-not-angry expressions, wardrobe identical across slides (white shirt/jeans; navy hoodie/khaki pants).
8. HITL image QA gate → retries (max 2 per failure type) → final QA → exports (4:5) → reports → `docs/retro.md` → `python3 scripts/astory_brain_cli.py autopilot --repo-root . --run-id 2026-06-11_23-45_reel-side-eye --phase post_run`.

## Memory claims governing this handoff

- `claim:ed11d6f016d3b4e2`: prompt-only generation forbidden; raw active reference queue must be loaded with `view_image`.
- `claim:88f81213cad79449`: filenames are not acceptance proof; only image QA + creator approval.
