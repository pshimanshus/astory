# Creator Image QA Rejection

Run: `2026-06-07_17-57_auto`

## Status

`revision_required`

The creator rejected the current generated image set at the Image QA gate. The prior Image QA verdict was too lenient and is superseded by this report.

## Creator Feedback

- The carousel images are inconsistent.
- Slide 1 shows Zuv carrying the shawl, while slide 2 does not have the shawl.
- The generated faces do not match Aachu/Zuv references closely enough.
- The imagegen/reference flow likely failed because local paths or Python-selected reference manifests are not the same as passing actual image inputs as references.

## Revised QA Verdict

Do not final-package or accept any current generated image as final.

Primary hard failures:

- `IDENTITY_DRIFT`: generated faces do not match the selected references closely enough.
- `SCENE_LOGIC_CONTRADICTION`: shawl visibility continuity breaks between slide 1 and slide 2.
- `TEXT_NOT_EXACT`: some tiny brandmarks are also malformed, but this is secondary until identity and continuity are fixed.

## Story Continuity Fix

New continuity lock:

- Slide 1: no visible shawl; show Zuv noticing.
- Slide 2: no visible shawl; show Aachu's self-contained "I'm fine" act.
- Slide 3: first visible shawl reveal; Zuv brings/offers the folded shawl.
- Slide 4: shawl rests on Aachu, payoff warmth.

Updated artifacts:

- `runs/2026-06-07_17-57_auto/planning/slide_beat_map.json`
- `runs/2026-06-07_17-57_auto/planning/selected_scenes.json`
- `runs/2026-06-07_17-57_auto/prompts/slide_01_post_4x5.txt`
- `runs/2026-06-07_17-57_auto/prompts/slide_01_story_9x16.txt`

## Reference Delivery Finding

The current built-in generation path used locally selected references and `view_image` inspection. That made references visible for evaluation and prompt writing, but it did not guarantee that the image model received those references as actual image inputs for identity preservation.

For identity-sensitive final Aachu/Zuv artwork, the next generation attempt must use one of these approaches:

1. Built-in image edit/reference flow where the selected identity images are visible in the conversation and explicitly labeled as reference images or edit targets.
2. Explicit CLI/API image edit flow, only if the creator asks for that fallback, where the selected reference images are passed as image inputs.
3. Mark final image generation blocked if the active tool path cannot pass actual image references.

## Required Next Step

Pause at Image QA. Do not regenerate yet unless the creator approves the corrected reference-input strategy.
