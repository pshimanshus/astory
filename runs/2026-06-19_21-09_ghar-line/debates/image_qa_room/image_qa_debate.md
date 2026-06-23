# Image QA Debate

Run: `2026-06-19_21-09_ghar-line`

## Scope

Reviewed slide 1, iteration 2, attempts 1 and 2.

## Face Match Reviewer

Decision: `hard_reject`

The candidates copy too much of the cafe identity reference's smile, cup/table pose, jacket, and pleasant emotional state. A recognizable-ish face is not enough if the image feels superimposed from a reference photo. For this beat, Aachu must be unsmiling and emotionally absent.

## Style Fidelity Reviewer

Decision: `hard_reject`

The watercolor-and-ink finish, text integration, and top-right brandmark are present, but the visual direction fails because it inherits the cafe reference's cheerful pose and table/cup setup. Attempt 1 also leans slightly tan. Neither can pass final style QA.

## Publishing QA Reviewer

Decision: `hard_reject`

Both candidates are `1122x1402`, not native `1080x1350 px`. The run contract says wrong-size output is a hard reject and must not be repaired by resizing, cropping, or padding into final artwork. The smile/reference-copying issue is a separate hard rejection.

## First Hard Questions

- Emotional truth before canvas: `block`; Aachu smiles when the beat needs unsmiling absence.
- Reference-copying before prettiness: `block`; the candidates copy the cafe identity reference's smile, cup/table pose, jacket, and pleasant emotional state.
- What would the creator immediately reject: the image looking like the existing cafe identity photo was superimposed into watercolor.
- Which identity reference did the candidate copy too literally: `references/identity/aachu/aachu-face-cafe-neutral-01.jpg`.

## Final Room Decision

`blocked_on_wrong_canvas_size_and_reference_pose_copy`

Stop before slide 2. Record `WRONG_CANVAS_SIZE`, `IDENTITY_REFERENCE_POSE_COPY`, and `SMILING_CONTRADICTS_ACHE`. Keep both candidates only as rejected visual evidence.
