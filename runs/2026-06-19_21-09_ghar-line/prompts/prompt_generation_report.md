# Prompt Generation Report

Run: `2026-06-19_21-09_ghar-line`

## Status

Prompt pack replaced for iteration 2: girl's POV in a lively cafe/friends setting, with Zuv absent in every slide.

## Prompt Files

- `runs/2026-06-19_21-09_ghar-line/prompts/slide_01_prompt.txt`
- `runs/2026-06-19_21-09_ghar-line/prompts/slide_02_prompt.txt`
- `runs/2026-06-19_21-09_ghar-line/prompts/slide_03_prompt.txt`
- `runs/2026-06-19_21-09_ghar-line/prompts/slide_04_prompt.txt`
- `runs/2026-06-19_21-09_ghar-line/prompts/negative_prompt.txt`

## Prompt Contract Checks

- Every slide prompt explicitly requests native `1080x1350 px`.
- Every slide prompt includes exact baked-in on-image text.
- Every slide prompt includes tiny low-contrast handwritten `@a.storyof.two` top-right.
- Every slide prompt makes raw Aachu/Zuv face anchors the highest-priority visual input.
- Every slide prompt uses Zuv references only as an absence boundary and blocks him as face, body, silhouette, reflection, photo, memory figure, ghost, phone wallpaper, or background lookalike.
- Every slide prompt keeps Aachu's face readable in a medium-wide, front three-quarter composition.
- Every slide prompt now blocks copying identity-reference pose, smile, cup/table setup, jacket/wardrobe, lighting, background, camera angle, or pleasant expression.
- Style references are limited to watercolor-and-ink finish, neutral paper, text style, and composition.

## Known Risks

- Slide 4 has the densest text and needs strict text rendering.
- Background friends must not become detailed identity faces.
- Because the built-in image tool can be tempted by named references, Image QA must reject any visible Zuv or substitute male lead immediately.
- Because slide 1 attempts copied the cafe identity reference, Image QA must reject any candidate where Aachu smiles or appears superimposed from an identity photo.
