# A Story of Two — Website Illustration Art-Order (single prompt for Codex)

Paste everything between the lines into Codex as one brief.

---

**ROLE.** Generate a kit of **website illustration assets** for *A Story of Two*
(Aachu & Zuv). These are **not** Instagram story slides — they are modular art
assets dropped into a responsive HTML/CSS website. Follow our locked house style
and identity exactly, but follow the **WEB SURFACE RULES** below — they override
the 1080×1350 slide rule.

**NON-NEGOTIABLE HOUSE STYLE (same as our IG art).**
- Premium hand-drawn romantic editorial **watercolor-and-ink**: soft transparent
  watercolor blooms, fine ink + pencil linework, gentle crosshatching, visible
  paper grain, imperfect organic edges, soft faded edges. Intimate, tender,
  cozy, premium.
- Paper: neutral **warm ivory / off-white only**. HARD NO: yellow, mustard,
  sepia, parchment, beige/tan dominance, coffee-stained, heavy cream, neon,
  harsh contrast, glossy digital finish.
- Accents, used lightly: muted denim blue, soft navy, faded sage, peach blush,
  dusty coral, warm camel.
- HARD NO look: anime, cartoon, doll/model face, 3D render, flat vector,
  photorealism, quote-card/poster, generic AI watercolor, children's book.
- **Identity — faces are the highest priority.** Use the real face anchors in
  `references/identity/aachu/` and `references/identity/zuv/`, and the
  `references/style/best-illustration/` finish lock. Aachu: large expressive dark
  eyes, natural brows, soft oval/round face, fuller lips, long dark voluminous
  hair, playful real-person charm. Zuv: thick dark wavy hair, thick brows,
  trimmed beard + mustache, rounded/oval face, gentle gaze. The **same two real
  people** every time — never merge, invent, over-beautify, or change
  ethnicity / age / skin tone / hairstyle identity.
- Brandmark: tiny low-contrast handwritten `@a.storyof.two`, bottom-right of
  painterly scenes only (omit on frames/motifs/textures).

**WEB SURFACE RULES (these override the slide rules).**
- Deliver every asset as a **transparent-background PNG** (except the seamless
  texture tile), sRGB, at **@2x**.
- **NO baked text anywhere** — no headlines, captions, labels, numbers, or UI.
  The website renders all type in real HTML. The *only* allowed lettering is the
  book-spine labels in motif C and the corner brandmark on scenes.
- **Frames/containers must have EMPTY transparent interiors.** We place real
  reels/photos inside them in code. Do **not** draw fake reels, fake phone
  screens, or placeholder content inside frames. (This is the #1 fix vs. the last
  version, which painted fake reels.)
- Any asset with the couple must ship **per-breakpoint crops** so they are never
  cut off: **Desktop** (landscape), **Tablet / iPad** (≈4:5), **Mobile**
  (portrait 9:16). Keep the couple inside a safe area; let paper fade at edges.

**ASSETS — deliver all of these.**

*A. Painterly scenes (couple).*
- **A1 Hero** — Aachu & Zuv at a warm wooden writing desk, journaling/sketching
  together: chai, scattered maps & polaroids, a shelf with books and a soft lamp.
  Generous empty ivory paper on one side for our headline. Three crops:
  `hero-desktop` (16:9, couple in the right third), `hero-tablet` (4:5),
  `hero-mobile` (9:16, couple upper-centre).
- **A2 Character cut-outs** (transparent, no setting), for margins/empty folds:
  `aachu-wave`, `zuv-chai`, `together-backtoback`, `together-walk`.
- **A3 Section vignettes** (transparent spot scenes, **landscape + portrait
  each**): `vignette-travel` (mountain ledge), `vignette-home` (sofa/chai
  evening), `vignette-desk` (shelf + lamp corner, no people).

*B. Painterly frames (EMPTY interiors — optional; we also build code versions).*
- **B1 `frame-reel`** — 9:16 hand-painted film/phone frame, empty transparent
  centre, ink border + corner ticks.
- **B2 `frame-polaroid`** — instant-photo frame, empty centre (~4:5), painted
  washi-tape corners.
- **B3 `frame-card`** — torn-paper card frame for carousels, empty centre.

*C. Motifs / objects (transparent spot illustrations, small).*
chai cup with steam · pocket-watch · wedding-ring pair · vintage camera · potted
plant · a stack of books with spines reading **moments / places / people / us**
(only text allowed) · pressed-flower sprig · paper clips · washi-tape strips ·
folded map fragment · a scatter of tiny **blank** polaroids.

*D. Textures / edges.*
- **D1 `tear-edge`** — seamless horizontal torn-paper edge strip (transparent),
  top + bottom variants.
- **D2 `paper-tile`** — seamless, subtle ivory paper-grain tile (opaque,
  tileable).
- **D3 `wash-blobs`** — a few soft transparent watercolor wash shapes in
  denim / sage / coral / blush, to sit behind text.

**DELIVERY.**
- Folder `site-illustrations/` with `scenes/  frames/  motifs/  textures/`.
- Transparent PNG @2x (texture tile may be opaque), sRGB.
- A `manifest.json` listing each file:
  `{ name, file, purpose, aspect, transparent, safe_area, breakpoint }`.
- A1 ships all three crops; A3 ships landscape + portrait.
- Re-check before export: empty frame interiors · zero baked text · warm ivory
  (never yellow) · real Aachu/Zuv faces · @2x transparent PNG.

---
