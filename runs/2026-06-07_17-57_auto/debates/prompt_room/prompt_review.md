# Prompt QA Review

Run: `2026-06-07_17-57_auto`

## Identity Guardian

Status: `conditional_pass_for_prompt_lock`

Identity references are selected, role-separated, and locally present:

- Dossier: `references/identity/_dossier/identity-dossier.json`
- Preflight: `references/identity/_dossier/identity-generation-preflight.md`
- Aachu face identity defaults: `references/identity/aachu/face/aachu-face-crop-car-purple-01.jpg`, `references/identity/aachu/face/aachu-face-crop-cafe-neutral-01.jpg`, `references/identity/aachu/face/aachu-face-crop-home-black-01.jpg`, `references/identity/aachu/face/aachu-face-crop-kitchen-neutral-01.jpg`
- Zuv face identity defaults: `references/identity/zuv/face/zuv-face-crop-balcony-neutral-01.jpg`, `references/identity/zuv/face/zuv-face-crop-balcony-neutral-03.jpg`, `references/identity/zuv/face/zuv-face-crop-balcony-neutral-02.jpg`, `references/identity/zuv/face/zuv-face-crop-dinner-smile-02.jpg`
- Together/body-language support: `references/identity/together/face-and-body-language/together-casual-icecream-standing-01.jpg`, `references/identity/together/face-and-body-language/together-cabin-hug-01.jpg`

The prompt pack now names reference roles clearly and prioritizes face identity inputs over expression, together/body-language, wardrobe, place, or style support.

Hard rule carried forward: final imagegen remains blocked until the active generation path passes the selected local face identity references as actual image inputs. Do not generate from text descriptions, character bibles, visible context, or file paths alone.

## Style Guardian

Initial status: `revise`

Applied fixes:

- Added stronger palette control to keep paper visibly neutral off-white.
- Clarified shawl as a modest warm-neutral accent, never the dominant background color.
- Revised brandmark rule to be tiny but still legible and baked into the paper.
- Added compact text-block guidance for slide 3.
- Added shawl textile-grain guidance for slide 4.
- Shortened repeated `AVOID` lists to reduce prompt overload while preserving hard rejects.

Remaining watchlist:

- `YELLOW_PAPER_CAST`
- `TEXT_UNREADABLE`
- `BRANDMARK_MISSING`
- `STYLE_DRIFT`

## Scene Logic Critic

Initial status: `revise`

Applied fixes:

- Slide 2: shawl is now fully off-frame and not visible, preserving the slide 3 reveal.
- Slide 2: replaced folded-arm ambiguity with one relaxed visible hand steadying the dupatta.
- Slide 4: locked one final pose: Aachu seated with shawl resting simply across her shoulders, hands visible and relaxed; Zuv seated close without touching the shawl.

Remaining watchlist:

- `ANATOMY_FAILURE`
- `SCENE_LOGIC_CONTRADICTION`

## Required Revisions

- None before prompt-lock review.

## Gate Decision

`pass`

Prompts can be shown for `HITL_PROMPT_LOCK`. Image generation must not begin until prompt approval is recorded and selected references are loaded visibly in the next state.
