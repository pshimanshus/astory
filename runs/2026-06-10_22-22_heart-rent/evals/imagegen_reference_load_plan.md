# Imagegen Reference Load Plan

Run: `2026-06-10_22-22_heart-rent`

Status: `ready_to_load_with_view_image`

Manual user attachments required: `False`
Prompt-only allowed: `False`

## Required Before Imagegen

Codex must load every path below with `view_image` in the current conversation
before any final Aachu/Zuv illustration is generated. If any image cannot be
read, or if the active generation path cannot use loaded image context, mark
the run blocked instead of generating final artwork.

## view_image Queue

- `references/identity/aachu/face/aachu-face-crop-car-purple-01.jpg`
- `references/identity/aachu/face/aachu-face-crop-cafe-neutral-01.jpg`
- `references/identity/aachu/face/aachu-face-crop-home-black-01.jpg`
- `references/identity/aachu/face/aachu-face-crop-kitchen-neutral-01.jpg`
- `references/identity/zuv/face/zuv-face-crop-balcony-neutral-01.jpg`
- `references/identity/zuv/face/zuv-face-crop-balcony-neutral-03.jpg`
- `references/identity/zuv/face/zuv-face-crop-balcony-neutral-02.jpg`
- `references/identity/zuv/face/zuv-face-crop-dinner-smile-02.jpg`
- `references/identity/aachu/smiles/aachu-smile-tan-shirt-01.jpg`
- `references/identity/aachu/smiles/aachu-smile-jewelry-close-01.jpg`
- `references/identity/aachu/smiles/aachu-smile-jewelry-necklace-01.jpg`
- `references/identity/aachu/reactions/aachu-reaction-cafe-pout-01.jpg`
- `references/identity/together/face-and-body-language/together-casual-icecream-standing-01.jpg`
- `references/identity/together/face-and-body-language/together-cabin-hug-01.jpg`
- `references/style/observational-intimacy-premium/contact-sheet.png`
- `references/style/observational-intimacy-premium/slide-01.png`
- `references/style/observational-intimacy-premium/slide-02.png`
