# Selected References

Machine-readable manifest:

- `runs/2026-06-10_22-22_heart-rent/references-used/selected_references.json`
- `runs/2026-06-10_22-22_heart-rent/evals/imagegen_reference_load_plan.json`
- `runs/2026-06-10_22-22_heart-rent/evals/imagegen_reference_load_plan.md`

Manual user attachments are not required for repo-local identity/style
references. Before any final imagegen call, Codex must load every path in the
JSON `view_image_queue` with `view_image` in the current conversation. If any
queued image cannot be read, or if the active imagegen path cannot use the
loaded image context, the run must be blocked instead of generating final
Aachu/Zuv artwork.

## Identity

Aachu close face anchors:

- `references/identity/aachu/face/aachu-face-crop-car-purple-01.jpg`
- `references/identity/aachu/face/aachu-face-crop-cafe-neutral-01.jpg`
- `references/identity/aachu/face/aachu-face-crop-home-black-01.jpg`
- `references/identity/aachu/face/aachu-face-crop-kitchen-neutral-01.jpg`

Zuv close face anchors:

- `references/identity/zuv/face/zuv-face-crop-balcony-neutral-01.jpg`
- `references/identity/zuv/face/zuv-face-crop-balcony-neutral-03.jpg`
- `references/identity/zuv/face/zuv-face-crop-balcony-neutral-02.jpg`
- `references/identity/zuv/face/zuv-face-crop-dinner-smile-02.jpg`

Together/body-language support:

- `references/identity/together/face-and-body-language/together-casual-icecream-standing-01.jpg`
- `references/identity/together/face-and-body-language/together-cabin-hug-01.jpg`

## Style

- `references/style/observational-intimacy-premium/contact-sheet.png`
- `references/style/observational-intimacy-premium/slide-01.png`
- `references/style/observational-intimacy-premium/slide-02.png`

## Text And Brand

- `references/text-style/README.md`
- `references/brand/README.md`
- `.agents/skills/astory/references/house-style-contract.md`
- `.agents/skills/astory/references/imagegen-contract.md`
