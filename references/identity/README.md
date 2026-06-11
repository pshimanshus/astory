# Identity References

Final Aachu/Zuv image generation requires actual identity references. Text-only
identity descriptions are not enough.

Use this library by role:

- `aachu/face/` and `zuv/face/`: clean portrait anchors and derived close face crops for face identity only.
- `aachu/smiles/`, `zuv/smiles/`: expression support for smile shape and warmth.
- `aachu/reactions/`, `zuv/reactions/`: expression, gesture, and body-language support.
- `together/face-and-body-language/`: couple closeness, height relationship, body scale, posture.
- `together/formal-secondary/`: wedding/formal context only.
- `current-request/`: temporary identity photos supplied for one run only.

Wardrobe and place references live outside this folder:

- `references/wardrobe/`
- `references/places/`

Never use wardrobe, place, formal, sunglasses, tiny-face, scenery, cloth, or
partial-person images as primary face identity references.

Current face-anchor inventory:

- Aachu: 11 face anchors, with 4 default close crops selected in the dossier.
- Zuv: 8 face anchors, with 4 default close crops selected in the dossier.
