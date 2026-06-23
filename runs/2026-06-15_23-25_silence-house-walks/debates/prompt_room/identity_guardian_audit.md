# Identity Guardian Audit - Priya

run_id: `2026-06-15_23-25_silence-house-walks`
stage: pre-imagegen prompt QA
prompt: `runs/2026-06-15_23-25_silence-house-walks/prompts/slide_01_prompt.txt`
status: `revise`

## Gate Decision

Revise before imagegen. This is not a reference block: the run has the required
raw Aachu and Zuv face anchors, they are role-separated, and the visibility proof
matches the active view-image queue recorded in the load plan. The prompt also
puts raw face anchors above style and text descriptions.

The identity risk is compositional. Zuv is entering from a doorway and can easily
become too small or soft to preserve his actual eyes, brows, nose, beard, and
face shape. Aachu is in soft three-quarter profile; if the model turns that into
hidden hair, profile silhouette, or theatrical sadness, the face match weakens.
Do not generate until the scene repair also protects readable faces.

Anti-slop lock: one single illustration, supplied copy as-is. No alternate
concept, no alternate copy, no quote-card drift.

## Evidence Checked

- Prompt reviewed: `runs/2026-06-15_23-25_silence-house-walks/prompts/slide_01_prompt.txt`
- Reference manifest reviewed: `runs/2026-06-15_23-25_silence-house-walks/references-used/selected_references.json`
- Load plan reviewed: `runs/2026-06-15_23-25_silence-house-walks/evals/imagegen_reference_load_plan.json`
- Visibility proof reviewed: `runs/2026-06-15_23-25_silence-house-walks/evals/imagegen_reference_visibility_proof.json`
- Contracts reviewed: `.agents/skills/astory/references/house-style-contract.md`, `.agents/skills/astory/references/imagegen-contract.md`, `.agents/skills/astory/references/master-prompt.md`
- Actual queued raw face/style images opened with `view_image` in this audit.

## identity_reference_paths

### Aachu face identity

- `references/identity/aachu/aachu-face-cafe-neutral-01.jpg`
- `references/identity/aachu/aachu-face-crop-cafe-neutral-01.jpg`
- `references/identity/aachu/aachu-face-crop-car-purple-01.jpg`
- `references/identity/aachu/aachu-face-crop-home-black-01.jpg`

### Zuv face identity

- `references/identity/zuv/face-01.png`
- `references/identity/zuv/face-03.png`
- `references/identity/zuv/zuv-face-crop-balcony-laugh-01.jpg`
- `references/identity/zuv/zuv-face-crop-balcony-neutral-01.jpg`

### Support present in selected reference set

- `references/identity/together/together-01.jpg`
- `references/identity/together/together-03.png`

## missing_references

[]

## prompt_fixes

1. Keep the supplied on-image text exactly as written. Do not rewrite, translate,
   shorten, or add copy.
2. Add an identity-readability guard to the scene repair: both faces must remain
   visibly readable enough for face match, not silhouettes or tiny background
   figures.
3. Keep Aachu in three-quarter profile but with her face unobscured: visible eyes,
   brows, nose, lips, cheek structure, and natural hair volume from the Aachu raw
   anchors. No hidden-face sadness, no doll smoothing.
4. Keep Zuv no farther than a readable medium shot in the doorway: his brows,
   eyes, nose, beard/mustache shape, rounded/oval face, and thick wavy hair must
   remain identifiable from the Zuv raw anchors.
5. Do not let the style references overwrite identity or clothing. Use them only
   for watercolor-and-ink finish, neutral paper, integrated handwriting, and
   composition, as the prompt already says.

## scores

Scale: `1` weak/high-risk, `5` strong/low-risk.

| Criterion | Score | Note |
| --- | ---: | --- |
| reference availability | 5 | Four raw Aachu face anchors and four raw Zuv face anchors are present, local, role-separated, and visible. |
| reference role clarity | 5 | Load plan separates Aachu face identity, Zuv face identity, style, expression support, and together/body-language support. Prompt prioritizes raw face anchors over style. |
| face preservation strength | 4 | Prompt names loaded anchors as highest priority and blocks merge/role reversal/over-beautification. Needs stronger face-readability guard because of doorway/profile staging. |
| wardrobe anchor clarity | 3 | No continuity blocker for a single illustration, but prompt should prevent style-reference outfits or decorative prettiness from taking over the home-fight scene. |
| drift risk control | 3 | References are strong; composition can still shrink Zuv or hide Aachu. Revise before generation. |

## failure_codes

- `IDENTITY_DRIFT` - prompt-level risk until face readability is added to the scene repair.

Watchlist after generation:

- `FACE_MERGE`
- `WARDROBE_CONTINUITY_FAILURE`

Not active:

- `IDENTITY_REFERENCE_MISSING`
- `IDENTITY_REFERENCE_INPUT_UNPROVEN`

## Final Gate

Identity is not blocked by missing references. It is blocked from imagegen until
the prompt revision protects face scale and visibility. Faces are the brand; a
beautiful hallway with two soft strangers is still a failed A Story image.
