# Reference Preflight

Run: `2026-06-14_02-21_hard-to-love`

## Status

Reference setup for planning is usable. Final imagegen is **not yet cleared** because the reference manifest, view-image queue, visibility proof, prompt lock, and repo QA loop still have to run after story/prompt approval.

## Current-Request Inputs

- Concept screenshots: copied to `input/concept/`.
- Approved style screenshots: copied to `input/style/`.
- Aachu identity attachments: copied to `input/identity/aachu/`.
- Zuv identity attachments: copied to `input/identity/zuv/`.

## Curated Repo References Found

- Aachu references exist under `references/identity/aachu/`.
- Zuv references exist under `references/identity/zuv/`.
- Together references exist under `references/identity/together/`.
- Best-illustration style references exist under `references/style/best-illustration/`.
- Text-style rules exist under `references/text-style/README.md`.
- Brand rules exist under `references/brand/README.md`.
- Visual failure examples exist under `references/failures/visual-inconsistencies/`.

## Risks

- The repo worktree is dirty and contains deleted/renamed identity README files; do not assume old citation paths are valid.
- Brain doctor currently fails because brain pages cite deleted `references/identity/*/README.md` paths. No automated memory claim should be used as truth for this run until that unrelated lint issue is fixed.
- Final imagegen must use the actual `view_image_queue` created by `scripts/prepare_imagegen_reference_context.py`; copied input folders alone are not enough.

