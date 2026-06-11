# Identity Guardian Audit

Run: `2026-06-10_22-55_couple-banter`

Status: creator rejected; prior automated image QA must be treated as overridden.

## Specific Visual Failures

- Aachu's likeness drifted badly: her face reads older, heavier, and more generic than the references. The generated version adds tired eyes, broad cheek mass, heavier jaw/under-chin weight, and a mature expression that does not match the younger, fresh, playful Aachu refs.
- Aachu is not compositionally protected. In slide 01 she is pressed into/behind the sofa and Zuv, with her body and face competing against cushions, scarf, and furniture. In slide 02 the heart prop and Zuv's foreground position reduce her clarity instead of making her the mischievous center of the joke.
- Zuv is closer in hair/beard cues but still over-rounded: cheeks, head shape, and jaw are too puffy compared with the leaner face structure and clearer jawline in the Zuv references.
- The couple energy is too calm and decorative. The scenes feel like cozy lifestyle illustrations, not funny chaotic couple banter. The original memes are about affectionate menace and proud annoyance; the exports soften that into static couch/table arrangements.
- The visual hierarchy is weak for sharing: too much room decor and prop clutter, not enough immediate readable facial acting. The joke text lands, but the faces and pose do not sell the punchline.

## Non-Negotiable Next-Prompt Constraints

- Aachu must look like a young, lively version of the reference person: fresh face, clear almond-shaped eyes, neat dark brows, small straight nose, natural soft smile/pout, long black hair, smooth skin, and a naturally oval/soft-heart face structure.
- Do not inflate either face. No puffy cheeks, swollen jaw, oversized head, heavy under-chin, jowls, or age-up shading. Keep natural cheek softness while preserving visible cheekbone/jaw/chin structure.
- Aachu must be clearly visible and not buried in furniture, cushions, scarf, heart prop, or Zuv's body. At least 80% of her face must be unobstructed, with eyes, nose, mouth, jawline, and hairline readable.
- Both faces must be large enough to audit identity at phone-screen size. No tiny faces, no side-profile-only faces, no hidden eyes, no merged facial features.
- Slide 01 must show playful chaos: Aachu actively teasing/trapping Zuv over the video-watch joke, but her full face and intention must remain visible. The sofa may exist only as support, not as a visual hiding place.
- Slide 02 must make Aachu the proud-annoying chaos engine, not a background figure. The heart prop should frame or support her expression without covering her likeness.
- Keep the exact meme texts, but let the body language carry the banter: teasing eye contact, amused resistance, mock-serious threat, playful interruption, couple shorthand.

## Identity-Preservation Wording For Next Prompt

Use this identity lock language in the revised prompt:

> Preserve Aachu and Zuv as the same specific couple from the visible identity references, not generic Indian couple characters. Aachu has a youthful natural oval/soft-heart face, long black hair, clear expressive almond eyes, neat brows, a small straight nose, soft lips, and a fresh playful expression; do not age her up, widen her face, add puffiness, or hide her behind props/furniture. Zuv has thick dark wavy hair, strong brows, expressive eyes, short beard/moustache, and a naturally defined non-puffy face; do not enlarge or round his head or cheeks. Keep both identities readable at thumbnail size while rendering in the A Story of Two watercolor-and-ink style.

Reference priority:

- Aachu: prioritize `aachu-face-crop-car-purple-01.jpg`, `aachu-face-crop-cafe-neutral-01.jpg`, and `aachu-face-crop-lavender-smile-01.jpg` for youthful face structure, eyes, brows, hair framing, and natural expression.
- Zuv: prioritize `zuv-face-crop-balcony-neutral-01.jpg`, `zuv-face-crop-balcony-neutral-03.jpg`, and `zuv-face-crop-balcony-laugh-01.jpg` for hair volume, beard, brows, jawline, and expressive reaction.

## Hard Rejection Criteria

- Reject if Aachu looks older, tired, matronly, over-rounded, puffy, or generic.
- Reject if Zuv's face becomes oversized, swollen, overly round, or identity-generic.
- Reject if Aachu is stuffed into a sofa, hidden behind Zuv, hidden behind the heart/scarf, or less visually clear than Zuv.
- Reject if either face cannot be identity-audited immediately at phone size.
- Reject if the scene reads calm/cozy/decorative instead of funny, chaotic, affectionate couple banter.
- Reject if clutter competes with the faces or joke action.
- Reject if text is changed, animals/platform UI appear, the brand mark is missing, or the output aspect ratio is wrong.
