# Identity Preflight

Run: `2026-06-10_22-55_couple-banter`

Status: pass, visual loading still required before imagegen.

## Reference Counts

- Aachu close face anchors in `references/identity/aachu/face/`: at least 8 available.
- Zuv close face anchors in `references/identity/zuv/face/`: at least 8 available.
- Together/body-language references in `references/identity/together/face-and-body-language/`: available.
- Current request source images copied under `runs/2026-06-10_22-55_couple-banter/input/`: available.

## Selected Identity Anchors

Aachu face anchors:

- `references/identity/aachu/face/aachu-face-crop-car-purple-01.jpg`
- `references/identity/aachu/face/aachu-face-crop-cafe-neutral-01.jpg`
- `references/identity/aachu/face/aachu-face-crop-home-black-01.jpg`
- `references/identity/aachu/face/aachu-face-crop-lavender-smile-01.jpg`

Zuv face anchors:

- `references/identity/zuv/face/zuv-face-crop-balcony-neutral-01.jpg`
- `references/identity/zuv/face/zuv-face-crop-balcony-neutral-03.jpg`
- `references/identity/zuv/face/zuv-face-crop-dinner-smile-02.jpg`
- `references/identity/zuv/face/zuv-face-crop-balcony-laugh-01.jpg`

Together/body-language support:

- `references/identity/together/face-and-body-language/together-cabin-hug-01.jpg`
- `references/identity/together/face-and-body-language/together-casual-icecream-standing-01.jpg`

Expression support:

- `references/identity/aachu/reactions/aachu-reaction-cafe-pout-01.jpg`
- `references/identity/aachu/reactions/aachu-reaction-cafe-wide-eyed-01.jpg`
- `references/identity/zuv/smiles/zuv-smile-balcony-laugh-01.jpg`

## Gate Note

Before final imagegen, selected local face, together, style, and source images must be made visible to Codex with `view_image`. If they are not visible to the generation path, stop and mark `IDENTITY_REFERENCE_MISSING`.
