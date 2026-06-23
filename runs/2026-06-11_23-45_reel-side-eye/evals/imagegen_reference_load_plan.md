# Imagegen Reference Load Plan

Run: `2026-06-11_23-45_reel-side-eye`

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
- `references/style/observational-intimacy-premium/contact-sheet.png`
- `references/style/observational-intimacy-premium/slide-01.png`
- `references/style/observational-intimacy-premium/slide-02.png`

## Supplemental Binder Packets

These packets are generated for audit/review only. They do not satisfy the final
identity input gate by themselves.

- `runs/2026-06-11_23-45_reel-side-eye/references-used/reference-binder/aachu-identity-binder.png` (aachu_identity_binder)
- `runs/2026-06-11_23-45_reel-side-eye/references-used/reference-binder/zuv-identity-binder.png` (zuv_identity_binder)
- `runs/2026-06-11_23-45_reel-side-eye/references-used/reference-binder/couple-body-language-binder.png` (couple_body_language_binder)
- `runs/2026-06-11_23-45_reel-side-eye/references-used/reference-binder/style-binder.png` (style_binder)
- `runs/2026-06-11_23-45_reel-side-eye/references-used/reference-binder/expression-support-binder.png` (expression_support_binder)
