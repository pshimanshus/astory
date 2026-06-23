# Prompt QA Review

Run: `2026-06-19_21-09_ghar-line`

## Agent Assignment Gate

- Assignment artifact: `runs/2026-06-19_21-09_ghar-line/debates/agent_assignment_matrix.md`
- Assignment status for iteration 2 prompt refresh: `fallback_local_passes_with_limitation_recorded`
- Gate decision: `pass_with_recorded_limitation`

The original run used actual multi-agent rooms. The creator's later visual correction invalidated the domestic prompt pack. This refresh was completed as local specialist passes because the current tool policy does not permit spawning fresh subagents unless the user explicitly asks for subagents.

## Identity Guardian

Status: `pass_pending_visibility_proof`

- Aachu is the only visible identity subject in all four prompts.
- Raw Aachu anchors control her face, skin tone, hair, and real-person proportions.
- Raw Zuv anchors remain named for the identity route but are used only as an absence boundary.
- Every prompt blocks Zuv as face, body, silhouette, reflection, framed photo, phone wallpaper, memory figure, ghost, or background lookalike.
- Background friends are required to stay anonymous and secondary.
- Single-anchor pose, expression, wardrobe, lighting, background, camera position, and composition copying is explicitly blocked.
- After creator correction, all prompts explicitly block copying the cafe identity reference's smile, cup/table setup, jacket, pleasant expression, and camera angle.

Remaining hard gate before imagegen: current reference visibility proof must match the active load plan and every queued reference must be visible in this conversation.

## Style Guardian

Status: `pass_pending_visibility_proof`

- Style references are constrained to ink linework, watercolor transparency, paper grain, integrated handwriting, neutral paper, and composition.
- Every prompt blocks yellow/parchment/sepia/beige/tan paper cast.
- Every prompt blocks copying tan/brown dominance, boxed brandmark, or bottom-right brandmark placement from style references.
- The cafe/friends setting stays soft and secondary; it should not become a dark club scene or a poster-like quote background.

## Scene Logic Critic

Status: `pass`

- Slide 1 proves full-place / hollow-feeling through an untouched cup or secondary table prop, closed shoulders, unsmiling mouth, disconnected gaze, and unclaimed beside-space.
- Slide 2 proves heart-returning through eyeline and body angle, not a phone or ghost.
- Slide 3 proves familiar-corner emptiness through the repeated cafe corner and Aachu's restrained touch near the empty beside-space.
- Slide 4 preserves the creator correction: no comeback, no resolution, only realization-through-absence.

## Creator Rejection Questions

- What would the creator immediately reject in this frame: Aachu smiling, looking pleasantly nostalgic, holding the cup like the source cafe photo, wearing/copied as the same jacket/table setup, or looking like the identity photo was watercolor-superimposed.
- Which loaded identity reference could imagegen copy too literally: `references/identity/aachu/aachu-face-cafe-neutral-01.jpg`; it is now blocked from active imagegen by `runs/2026-06-19_21-09_ghar-line/references-used/reference_policy.json`.
- Does the face expression prove or betray the line: it proves the line only if Aachu is unsmiling, held back, and socially unable to join; any smile, coyness, or pleasant cafe energy betrays `Khaali hai jo tere bina`.

## Canvas And Brandmark Gate

- Every prompt includes native `1080x1350 px`: `pass`
- Every prompt includes tiny top-right `@a.storyof.two`: `pass`
- Every selected scene has concrete visual setting logic: `pass`
- Every prompt contains exact on-image text: `pass`
- Every prompt blocks blank text / add-text-later workflow: `pass`

## Required Revisions

- None remaining before reference visibility and repo QA.

## Post-Failure Override

The earlier `pass_pending_reference_visibility` decision is invalidated by `runs/2026-06-19_21-09_ghar-line/evals/process_failure_audit.json`.

This prompt-room pass was a fallback local pass after the original multi-agent outputs were invalidated by creator corrections. It should not have unlocked imagegen. The prompt also contained an emotional-state contradiction and identity-reference pose-copy risk.

## Gate Decision

`invalidated_reapproval_required`

Imagegen remains blocked by `runs/2026-06-19_21-09_ghar-line/evals/pre_imagegen_blocker_check.json` until this corrected prompt/reference pack receives non-fallback review or fresh creator-visible reapproval.
