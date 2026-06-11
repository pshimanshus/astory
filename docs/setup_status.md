# Setup Status

Last checked: `2026-06-08`

Command: `/astory setup`

Status: `ready_with_reference_gate`

## Skill Discovery

- Repo-scoped source skill: `.agents/skills/astory/` present.
- Personal install: not checked and not authoritative for this repository.
- Required resources present: `SKILL.md`, agent config, room personas, templates, house-style contract, imagegen contract, and failure taxonomy.

## Reference Gate

Decision: `pass_for_planning_and_prompting`

Planning, idea debate, story design, prompt drafting, evals, traces, and reports
are allowed.

Final Aachu/Zuv image generation is allowed only when the active generation path
can pass actual local reference images as image inputs. Prompt-only identity
descriptions remain blocked for final artwork.

Minimum final-generation requirements are satisfied by the role library:

- Aachu default close anchors: 4 selected in `identity-dossier.json` under `selected_generation_recipe.face_visible_default.default_aachu_close_face_anchors`.
- Zuv default close anchors: 4 selected in `identity-dossier.json` under `selected_generation_recipe.face_visible_default.default_zuv_close_face_anchors`.
- Together/couple references: present in `references/identity/together/face-and-body-language/`.
- Expression/reaction references: present in `references/identity/*/smiles/` and `references/identity/*/reactions/`.
- Wardrobe references: present in `references/wardrobe/`.
- Place/memory references: present in `references/places/`.
- Approved style references or locked style rules: present.
- Text-style rules for baked-in handwritten typography: present.
- Brand rules: present.

## Role Reference Inventory

- `references/identity/aachu/face/`: 11 face anchors, including derived close crops for direct, three-quarter, smile, and domestic angles.
- `references/identity/aachu/smiles/`: 4 smile references.
- `references/identity/aachu/reactions/`: 6 reaction references.
- `references/identity/zuv/face/`: 8 face anchors, including derived close crops for neutral, laugh, dinner smile, side/profile, and patterned-shirt angle support.
- `references/identity/zuv/smiles/`: 2 smile references.
- `references/identity/zuv/reactions/`: 2 reaction/build references.
- `references/identity/together/face-and-body-language/`: 3 couple body-language/scene references.
- `references/identity/together/formal-secondary/`: 4 wedding/formal secondary references.
- `references/wardrobe/aachu/`: 7 wardrobe references.
- `references/wardrobe/zuv/`: 8 wardrobe references.
- `references/wardrobe/couple/`: 3 couple wardrobe references.
- `references/places/`: 9 place and memory-setting references.
- `references/identity/current-request/`: no temporary request images currently; README only.

## Dossier And Contact Sheets

Operational dossier:

- `references/identity/_dossier/identity-dossier.json`
- `references/identity/_dossier/identity-generation-preflight.md`

Role contact sheets:

- `references/identity/_dossier/identity-face-contact-sheet.jpg`
- `references/identity/_dossier/identity-expressions-contact-sheet.jpg`
- `references/identity/_dossier/together-contact-sheet.jpg`
- `references/identity/_dossier/wardrobe-contact-sheet.jpg`
- `references/identity/_dossier/places-contact-sheet.jpg`

The face contact sheet is intentionally limited to clean face anchors. Scenery,
cloth folds, UI screenshots, tiny faces, sunglasses, and partial/blurred people
are marked as non-face references in the dossier.

## Generation Reference Selection

Use references by role:

- Face-visible slides: attach the 4 default close Aachu face refs and 4 default close Zuv face refs from the dossier, then add optional angle support only when the scene needs it.
- Emotional expression: add smile or reaction refs only as support.
- Couple scene: add together/body-language refs for height, closeness, and posture.
- Clothing-specific scene: add wardrobe refs, never as face refs.
- Real memory setting: add place refs, never as face refs.
- Formal/wedding story: add formal-secondary refs only when the story explicitly asks for that context.

Before final imagegen, inspect and load the selected references in context with
`view_image`; never generate final Aachu/Zuv artwork from text descriptions alone.

## Style, Text, And Brand

- Primary style lock: `references/style/observational-intimacy-premium/`
- Style requirements: premium hand-drawn romantic watercolor-and-ink, neutral ivory/off-white paper, visible grain, fine ink/pencil linework, transparent watercolor blooms, tactile everyday details, integrated readable handwritten text.
- Style hard rejects: yellow/parchment paper, generic AI watercolor, quote-card design, anime/cartoon, photorealism, 3D render, flat vector art, digital overlay typography.
- On-image text: exact wording, readable at phone-screen size, warm charcoal handwritten typography, upper-middle negative space, baked into the illustration.
- Brandmark: tiny low-contrast handwritten `@a.storyof.two` in the bottom-right corner as part of the artwork.

## Setup Notes

- The identity dossier no longer uses automated face-count metadata for curation.
- The old false positives from the legacy contact sheet are recorded under `deprecated_legacy_false_positives`.
- A future run must mark final imagegen blocked if selected identity/style references cannot be passed as visible image inputs.
- HITL approvals for production runs must be recorded in each run's `docs/approvals.md` before continuing past approval gates.
