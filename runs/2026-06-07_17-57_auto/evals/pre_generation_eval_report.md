# Pre-Generation Eval Report

Run: `2026-06-07_17-57_auto`

## Status

`pass`

## Scores

- Story coherence: `4.8`
- Slide count fit: `4.8`
- Scene selection quality: `4.7`
- Visual clarity: `4.6`
- Prompt clarity: `4.5`
- Character consistency potential: `4.4`
- Style consistency potential: `4.5`
- Text readability potential: `4.4`
- Brand fit: `4.8`
- Publishability: `4.3`
- Overall: `4.52`

## Weak Dimensions

- Character consistency cannot be fully proven until local identity references are visibly loaded before imagegen.
- Anatomy risk remains around shawl handling and hands, although prompt revisions now reduce that risk.
- Text readability requires final image QA because baked-in handwriting can drift.

## Required Revisions Before Imagegen

- None to the prompt pack before prompt-lock review.
- After prompt approval, load selected local identity/style references visibly with `view_image`.

## Gate Decision

Prompts can proceed to `HITL_PROMPT_LOCK`.

Final image generation must not begin until:

- prompt approval is recorded in `docs/approvals.md`;
- selected references are loaded visibly in context;
- the run trace records `LOAD_REFERENCE_IMAGES_IN_CONTEXT`.
