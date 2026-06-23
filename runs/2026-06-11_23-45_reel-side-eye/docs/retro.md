# Run Retro

Run: `2026-06-11_23-45_reel-side-eye`
Status: `blocked_until_prompt_reference_reapproval`

## What Worked

- The creator caught the failure before final packaging.
- Image QA now records the rejected candidates and the exact failure codes.
- The repaired load plan now uses raw Aachu/Zuv face anchors as active inputs.

## What Failed Or Drifted

- The active imagegen queue used generated Reference Binder contact sheets instead of raw face anchors.
- Repo QA accepted binder visibility as identity proof.
- Prompt wording carried yellow-prone positive cues that overpowered the no-yellow rule.
- Generation continued to slide 2 after slide 1 already had hard-reject failures.

## Prompt Lessons

- Localized light is acceptable; global paper/background wording must stay neutral white/off-white.
- Do not mix multiple yellow-prone positive cues with a negative no-yellow sentence.
- Identity and paper-tone constraints need to be validated before any new candidate is generated.

## Identity / Style Lessons

- Binder packets are useful for audit and review, but they are not final identity inputs.
- Final Aachu/Zuv imagegen requires raw face anchors in the active queue and a fresh visibility proof.
- Anime/cartoon drift plus generic faces is a hard block even if text is present.

## Proposed Brain Updates

- Promote a workflow lesson only after review: binder-only `view_image` proof must not unlock final Aachu/Zuv imagegen.
- Promote a workflow lesson only after review: hard-rejected slide 1 blocks later slide generation until Image QA and prompt/reference repair happen.

## Evidence

- `runs/2026-06-11_23-45_reel-side-eye/evals/image_quality_eval.json`
- `runs/2026-06-11_23-45_reel-side-eye/evals/imagegen_reference_load_plan.json`
- `runs/2026-06-11_23-45_reel-side-eye/evals/imagegen_reference_visibility_proof.json`
- `runs/2026-06-11_23-45_reel-side-eye/evals/repo_qa_review.json`
- `runs/2026-06-11_23-45_reel-side-eye/images/generation_attempts.json`
