# Image Quality Report

Run: `2026-06-07_17-57_auto`

## Status

`superseded_by_creator_rejection`

Superseded by: `runs/2026-06-07_17-57_auto/evals/image_quality_creator_rejection_report.md`

Reason: creator rejected the current generated image set for identity drift and shawl continuity contradiction after this initial Image QA pass.

This initial report accepted too much. It is retained only as historical QA context; do not use it as the current gate decision.

## Accepted Candidates

- Slide 1 post: `runs/2026-06-07_17-57_auto/images/slide_01_post_4x5_attempt_03_candidate.png`
- Slide 1 story/reel: `runs/2026-06-07_17-57_auto/images/slide_01_story_9x16_attempt_01_candidate.png`
- Slide 2 story/reel: `runs/2026-06-07_17-57_auto/images/slide_02_story_9x16_attempt_01_candidate.png`
- Slide 3 post: `runs/2026-06-07_17-57_auto/images/slide_03_post_4x5_attempt_01_candidate.png`
- Slide 3 story/reel: `runs/2026-06-07_17-57_auto/images/slide_03_story_9x16_attempt_01_candidate.png`
- Slide 4 story/reel: `runs/2026-06-07_17-57_auto/images/slide_04_story_9x16_attempt_01_candidate.png`

## Retry Candidates

- Slide 2 post: `runs/2026-06-07_17-57_auto/images/slide_02_post_4x5_attempt_01_candidate.png`
- Slide 4 post: `runs/2026-06-07_17-57_auto/images/slide_04_post_4x5_attempt_01_candidate.png`

## Scores

- Identity match: `3.9/5`
- Face consistency across slides: `4.2/5`
- Style consistency: `4.4/5`
- Text readability: `4.6/5`
- Exact text preservation: `4.0/5`
- Brandmark presence and exactness: `3.2/5`
- Neutral ivory paper: `4.6/5`
- Scene logic: `4.5/5`
- Pose anatomy: `4.2/5`
- Composition: `4.4/5`
- Publishability: `3.7/5`
- Overall: `3.9/5`

## Hard Failures

- `TEXT_NOT_EXACT`: Slide 2 post bottom-right brandmark appears malformed as `@a.storyuf.two` instead of `@a.storyof.two`.
- `TEXT_NOT_EXACT`: Slide 4 post bottom-right brandmark appears malformed as `@a.storyofl.two` instead of `@a.storyof.two`.

## Pass Notes

- All post candidates are native 4:5 at `1122 x 1402`.
- All story/reel candidates are native 9:16 at `941 x 1672`.
- Story text is readable and matches the approved prompt pack closely enough for publication on the accepted assets.
- Paper tone, watercolor grain, ink linework, and observational intimacy style are consistent.
- No face merge, major age drift, swapped identities, or scene-text contradiction is visible.

## Residual Risks

- Aachu and Zuv are slightly idealized in the illustration style. This is acceptable for the current house style but worth preserving carefully on retries.
- Tiny baked-in brandmarks are fragile in imagegen. If the next retries fail only on the handle again, the safer production move is to generate clean art without a handle and add the exact `@a.storyof.two` in final packaging after creator approval.

## Required Retry Delta

Retry only `slide_02_post_4x5` and `slide_04_post_4x5`.

Preserve the same scene, aspect ratio, character placement, wardrobe, paper tone, exact story text, and style. Add this targeted delta:

> Render the tiny bottom-right handle exactly as `@a.storyof.two`, using simple handwritten lowercase letters. Do not invent, shorten, replace, or add extra letters. Keep it low-contrast but readable. If unsure, leave extra quiet margin around the bottom-right mark so it remains clear.

## Final Decision

Pause at the Image QA gate. Creator decision is needed before retrying the two rejected post surfaces or changing the brandmark production strategy.
