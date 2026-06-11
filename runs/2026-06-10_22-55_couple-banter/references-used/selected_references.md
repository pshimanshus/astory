# Selected References

Operational machine-readable manifest:

- `runs/2026-06-10_22-55_couple-banter/references-used/selected_references.json`
- `runs/2026-06-10_22-55_couple-banter/evals/imagegen_reference_load_plan.json`
- `runs/2026-06-10_22-55_couple-banter/evals/imagegen_reference_load_plan.md`

Manual user attachments are not required for repo-local identity/style/current-request
images. Before any final imagegen call, Codex must load every path in the JSON
`view_image_queue` with `view_image` in the current conversation. If any queued
image cannot be read, or if the active imagegen path cannot use loaded image
context, the run must be blocked instead of generating final Aachu/Zuv artwork.

The lists below are the original human-readable selection notes. The JSON load
plan is the operational source of truth for automated loading.

## Current Request Source Images

- `runs/2026-06-10_22-55_couple-banter/input/source_01_video-watch.jpeg`
  - Role: exact text, meme emotion, gentle squeeze composition essence.
  - Not role: animal identity, screenshot UI, typography style, platform artifacts.
- `runs/2026-06-10_22-55_couple-banter/input/source_02_annoy-you.jpeg`
  - Role: exact text, heart prop idea, proud-annoyance mood.
  - Not role: dog identity, screenshot UI, typography style, platform artifacts.

## Identity References

Aachu face identity:

- `references/identity/aachu/face/aachu-face-crop-car-purple-01.jpg`
- `references/identity/aachu/face/aachu-face-crop-cafe-neutral-01.jpg`
- `references/identity/aachu/face/aachu-face-crop-home-black-01.jpg`
- `references/identity/aachu/face/aachu-face-crop-lavender-smile-01.jpg`

Zuv face identity:

- `references/identity/zuv/face/zuv-face-crop-balcony-neutral-01.jpg`
- `references/identity/zuv/face/zuv-face-crop-balcony-neutral-03.jpg`
- `references/identity/zuv/face/zuv-face-crop-dinner-smile-02.jpg`
- `references/identity/zuv/face/zuv-face-crop-balcony-laugh-01.jpg`

Together/body-language:

- `references/identity/together/face-and-body-language/together-cabin-hug-01.jpg`
- `references/identity/together/face-and-body-language/together-casual-icecream-standing-01.jpg`

Expression support:

- `references/identity/aachu/reactions/aachu-reaction-cafe-pout-01.jpg`
- `references/identity/aachu/reactions/aachu-reaction-cafe-wide-eyed-01.jpg`
- `references/identity/zuv/smiles/zuv-smile-balcony-laugh-01.jpg`

## Style References

- `references/style/observational-intimacy-premium/contact-sheet.png`
- `references/style/observational-intimacy-premium/slide-03.png`
- `references/style/observational-intimacy-premium/slide-04.png`
- `references/style/observational-intimacy-premium/slide-06.png`

## Text And Brand

- `references/text-style/README.md`
- `references/brand/README.md`
