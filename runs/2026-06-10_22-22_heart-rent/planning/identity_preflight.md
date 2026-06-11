# Identity Preflight

Status: pass for planning, pending visual loading before imagegen.

The local V2 identity hard gate is satisfiable:

- Aachu face anchors available in `references/identity/aachu/face/`.
- Zuv face anchors available in `references/identity/zuv/face/`.
- Together/body-language support references available in `references/identity/together/face-and-body-language/`.
- Dossier default recipe is available at `references/identity/_dossier/identity-dossier.json`.

Selected default Aachu face identity anchors:

- `references/identity/aachu/face/aachu-face-crop-car-purple-01.jpg`
- `references/identity/aachu/face/aachu-face-crop-cafe-neutral-01.jpg`
- `references/identity/aachu/face/aachu-face-crop-home-black-01.jpg`
- `references/identity/aachu/face/aachu-face-crop-kitchen-neutral-01.jpg`

Selected default Zuv face identity anchors:

- `references/identity/zuv/face/zuv-face-crop-balcony-neutral-01.jpg`
- `references/identity/zuv/face/zuv-face-crop-balcony-neutral-03.jpg`
- `references/identity/zuv/face/zuv-face-crop-balcony-neutral-02.jpg`
- `references/identity/zuv/face/zuv-face-crop-dinner-smile-02.jpg`

Selected together/body-language support:

- `references/identity/together/face-and-body-language/together-casual-icecream-standing-01.jpg`
- `references/identity/together/face-and-body-language/together-cabin-hug-01.jpg`

Generation rule:

Before final imagegen, these local image files must be loaded with `view_image` so the generation path is grounded in actual faces, not text-only descriptions.

Primary identity risk:

- `IDENTITY_DRIFT` if the prompt over-emphasizes meme staging or wallet prop over face preservation.
- `FACE_MERGE` if Aachu and Zuv are placed too close with overlapping faces.

Mitigation:

Use a medium shot with both faces visible but separated: Aachu on one side holding a small open rent notebook or wallet, Zuv opposite her with a sheepish smile and one hand over his chest.
