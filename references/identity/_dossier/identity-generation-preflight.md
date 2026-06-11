# Identity Generation Preflight

Last updated: `2026-06-08`

Read this before every A Story of Two image generation run.

## Hard Rule

Do not generate final Aachu/Zuv artwork from text-only identity descriptions.
Face-visible slides require actual image inputs from the face folders plus any
scene-specific support references.

## Reference Roles

Use references by role, not by filename beauty.

| Role | Folders | Allowed to control | Never controls |
|------|---------|--------------------|----------------|
| Face identity | `references/identity/aachu/face/`, `references/identity/zuv/face/` | face structure, eyes, brows, hair, skin tone, beard | wardrobe, place, formal mood |
| Smiles/reactions | `references/identity/*/smiles/`, `references/identity/*/reactions/` | expression, emotion, gesture | primary face identity |
| Together | `references/identity/together/face-and-body-language/` | closeness, height, body scale, posture | solo face identity |
| Formal secondary | `references/identity/together/formal-secondary/` | wedding/formal context only | everyday default identity |
| Wardrobe | `references/wardrobe/` | clothes, jewelry, accessories, props | face identity |
| Places | `references/places/` | memory setting, layout, light, atmosphere | face identity |

## Contact Sheets

Use these contact sheets to pick the right reference type:

- `references/identity/_dossier/identity-face-contact-sheet.jpg`
- `references/identity/_dossier/identity-expressions-contact-sheet.jpg`
- `references/identity/_dossier/together-contact-sheet.jpg`
- `references/identity/_dossier/wardrobe-contact-sheet.jpg`
- `references/identity/_dossier/places-contact-sheet.jpg`

The face contact sheet must contain only clean portrait/face anchors. Scenery,
cloth folds, tiny faces, sunglasses, UI screenshots, and blurred partial people
must not appear there.

## Default Face Identity Selection

For any face-visible generation, load:

- the 4 default Aachu close face anchors from `selected_generation_recipe.face_visible_default.default_aachu_close_face_anchors`
- the 4 default Zuv close face anchors from `selected_generation_recipe.face_visible_default.default_zuv_close_face_anchors`
- 1-2 together/body-language references when both appear in the same slide

Then add only the support refs the scene needs:

- optional face-angle support only when the composition needs a side/profile/laughing angle
- smiles/reactions for exact expression
- wardrobe refs for specific clothing or accessories
- place refs for a real memory setting
- formal-secondary refs only for a formal/wedding story

## Non-Negotiables

**Aachu must preserve:**

- long dark hair with natural volume
- large expressive dark eyes and active brows
- soft oval/round face structure
- warm fair-medium skin tone
- fuller lips and readable playful expression
- petite/slightly smaller presence relative to Zuv

**Zuv must preserve:**

- thick dark wavy hair with visible volume
- thick dark brows
- warm brown skin tone
- trimmed beard and mustache
- rounded/oval masculine face structure
- medium-tall broader build relative to Aachu

## Hard Rejects

Reject or block the run if:

- face identity is prompt-only
- wardrobe/place/formal refs are used as primary face refs
- sunglasses images are used for eye identity
- a formal/wedding image drives an everyday scene
- Aachu or Zuv becomes generic, over-beautified, face-merged, or unrecognizable
- the active generation path cannot pass actual image references as image inputs

## Known Legacy False Positives

Do not trust automated face-count metadata from the old contact sheet. It marked
several non-face images as face-bearing references, including scenery, cloth
folds, architecture crops, and partial blurred shots. The refreshed
`identity-dossier.json` records those IDs under `deprecated_legacy_false_positives`.

## Procedure

1. Open `identity-dossier.json`.
2. Choose face refs first from `selected_generation_recipe.face_visible_default`.
3. Choose optional expression/together/wardrobe/place refs only when the slide
   needs that role.
4. Run `python3 scripts/prepare_imagegen_reference_context.py --run-id <run_id>`
   so the run gets `references-used/selected_references.json` and
   `evals/imagegen_reference_load_plan.json`.
5. Make every image in `view_image_queue` visible to Codex with `view_image`;
   the creator does not need to attach repo-local identity/style images manually.
6. Write `evals/imagegen_reference_visibility_proof.json` before calling
   imagegen.
7. Generate one identity proof before final carousel slides if the generation
   path has recently failed identity matching.
8. QA faces before style, typography, props, or packaging.
