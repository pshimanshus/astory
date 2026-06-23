# A Story of Two — Lean Creative Direction (v2)

Date: 2026-06-20
Status: **proposed direction — read, then decide**

> v1 of this doc was wrong in two ways: it treated your engineered assets (novelty
> framework, Visual Story Director, face-match mechanism, outcome data) as
> "machinery to delete," and it got your execution model wrong (you generate inside
> **Codex `imagegen`**, not via an API). This v2 keeps your assets, fixes the
> orchestration around them, and gets the Codex face-match handoff right.

---

## 1. The real diagnosis: good knowledge, buried by process

Your system's **knowledge is good.** The failure is **orchestration + a missing
feedback loop.**

**The winner vs. the pipeline (the freshness gap, concretely):**

| Your winners (e.g. `DYJpjt9CQYY`, 40.15 shares/1k) | What the pipeline ships (e.g. ghar cafe) |
|---|---|
| Character **scene**: two people, body language | Solo **mood portrait**: one person, static |
| A specific funny/true **receipt** (tissue + water + "mujhe kuch nahi hua") | No receipt — just a pretty sad face |
| **Hook** that earns the swipe ("He didn't marry peace") | Poetic line, no curiosity, no swipe |
| **Romanized Hinglish** (renders perfectly) | Mixed; Devanagari *fails* in imagegen |
| Wide, action-led, alive | Close, sideways, "AI sad girl" |

The pipeline output violates *your own* `illusion-of-novelty` doc and *your own*
outcome data. The knowledge to do it right is in the repo; the machine doesn't
apply it because the creative call is spread across 8 rooms and buried under gates.

**Why it's buried (`run-lessons.md` is the proof):** every creator correction
became a *permanent mandatory gate* — scene-landing preview (06-13), 1080×1350
lock (06-15), the 11-reference `gold_standard_identity_route_gate` as a hard
blocker (06-16/17), required novelty-model JSON (06-18)… Each fix was reasonable.
Making each one a permanent gate is the disease. Result: `gold_standard_route`
needs **11 references + 13 artifacts**, a run spawns **70+ files across 8 rooms**,
and **3 of 5 runs never ship a single image.**

**Two diseases, opposite cures (still true, now precise):**
- **Taste** (ghar's inverted smile, solo-portrait staleness, poetic-not-spoken copy)
  → fixed by **one director who actually applies your assets**, not a committee.
- **Execution** (silence's good art killed by Devanagari + wrong size; ghar's
  binder-collision identity failure) → fixed by **correct Codex handoff**:
  raw anchors fed right, romanized text, locked canvas.

---

## 2. What we KEEP (this is your edge — do not delete)

- **`illusion-of-novelty-storytelling`** — the editorial brain (new reveal,
  contrast, bullseye proof, protect the illusion, carousel shape). Excellent.
- **Visual Story Director "Tara"** — the staging/freshness eye. Her questions
  *become the director's checklist*, not a separate room.
- **Face-match mechanism** (`imagegen-contract` + `master-prompt`) — raw 4+4
  multi-angle anchors loaded via `view_image`, identity-structure-only, scene
  drives pose, text baked in. This is *correct* and proven by the
  `2026-06-15_19-09_plate-nervous` gold-standard route.
- **Outcome data** (`references/brain/pages/outcome-attribution.md`) — ranked by
  shares/1k, not likes. Your real competitive signal.
- **Winner bank**, **named failure corpus** (`references/failures/visual-inconsistencies/`),
  **house-style-contract**. All kept.

## 3. What we DELETE (ceremony, not taste)

- The **8 debate rooms as multi-agent dispatch** → collapse the good lenses into
  one director's checklist.
- The **per-run JSON ceremony**: `source_winner_remix_contract.json`,
  `source_winner_novelty_model.json`, `novelty_candidate_ledger.json`,
  `agent_assignment_matrix.md`, the ~18 eval files, repo-QA review loops.
  *(The framework docs stay; the per-run paperwork goes — the director applies
  the lens in prose, not in a JSON file.)*
- **`gold_standard_identity_route_gate`** as a 13-artifact hard blocker →
  replaced by a **5-line pre-flight checklist** (below).
- **`SKILL.md`: 672 lines → ~1 page** director brief.

---

## 4. The workflow: one director, two gates, one loop

```
[1] DIRECTOR PASS (Claude, applying your assets as a toolkit)
      - plain-LM baseline line (the floor, per your own rule)
      - novelty lens: old topic → fresh reveal → viewer outcome (send/save/tag)
      - Tara's staging: 2 people? body language? the ONE prop/receipt?
        eyeline? camera distance? is it FRESH not the stock sideways close-up?
      - copy: spoken Hinglish that a real person would send, not poetry
      → must beat the baseline AND look like a winner, not a mood portrait
   ── GATE A (you): read copy + 1-line visual intent per slide. go / no-go.

[2] PROMPT + REF SPEC (Claude writes the Codex package)
      - lean priority-stack prompt per slide (face match > house style > scene/text)
        NO "HARD NO" wall — positive direction (master-prompt already says this)
      - exact RAW anchors to view_image (4 Aachu + 4 Zuv, multi-angle)
      - binders / contact-sheets / source-faces EXCLUDED from the queue
      - exact on-image text, ROMANIZED, baked in; 1080×1350; brandmark top-right

[3] CODEX — ONE PASTE-ABLE PROMPT (see §5)
      view_image the anchors → generate slide-by-slide → save to images/

   ⟳ THE LOOP (the missing Claude feature): after each render, Claude-vision
     judges the actual PNG against (a) the intended feeling, (b) the named
     failure corpus (rubber hands, merged seats, identity drift, stale close-up,
     wrong text), (c) the winner bar. Fail → ONE targeted fix → re-gen. Max 3.
   ── GATE B (you): eyeball final pixels. accept / reject.

[4] ACCEPT → the PNGs are the post.
```

**5-line identity pre-flight** (replaces the 13-artifact gate):
1. 4 Aachu + 4 Zuv raw anchors loaded via `view_image`, multiple angles each?
2. Binders / contact-sheets / non-Aachu-Zuv faces excluded from the queue?
3. Prompt says "identity structure only; scene drives pose/expression/wardrobe"?
4. Exact text present, romanized, baked in; `1080x1350 px` in the prompt?
5. Tiny top-right `@a.storyof.two` brandmark requested?

If all 5 yes → generate. No 13-document route required.

---

## 5. "One go, one Codex prompt" — the handoff package (#8, #9)

You work in Cursor: Claude directs, then you switch to Codex and paste ONE prompt.
The package is a folder Claude writes; the prompt points Codex at it.

```
runs/<id>/handoff/
  GENERATE.md          # the one prompt you paste into Codex (self-contained)
  slide_01.txt … NN    # lean priority-stack prompt per slide (exact text inside)
  anchors.txt          # exact view_image paths: 4 Aachu + 4 Zuv (multi-angle)
                       #   from references/identity/aachu|zuv  (NO binders)
  style.txt            # references/style/best-illustration/ paths to load
```

`GENERATE.md` tells Codex, in order: (1) `view_image` every path in `anchors.txt`
and `style.txt` first; (2) for each `slide_NN.txt`, generate a native 1080×1350
illustration with the exact baked-in text; (3) one slide at a time; (4) save to
`runs/<id>/images/`; (5) stop on a hard failure and report. You give one go.

**Face match, stated plainly (this is #9, the most important thing):** imagegen
matches faces by *seeing* the raw anchors in context — not from text. So the
package's job is to make Codex **load the right images the right way**: 4+4 raw
multi-angle anchors as first-class inputs, everything else (binders, source
photos with other faces) kept out, and the prompt using them for *identity
structure only* so no single photo's pose/cafe/smile leaks into the scene. That
single feeding rule is what the ghar run violated.

**Text decision (open, yours):** imagegen renders **romanized Hinglish**
reliably (ghar's "Khaali hai…" and your winner's "mujhe kuch nahi hua" both
render); it **fails on Devanagari script** (silence). Default = romanize. Keep
Devanagari only on your explicit call, flagged high-risk.

---

## 6. How the system learns without getting heavier (#10)

New information you gather should **sharpen one director**, not add gates. It
feeds three *living* references the director reads at the start of every run:

1. **Winner board** — the proven posts + why each worked (shares/1k).
2. **Taste card** — one short evolving doc: what lands, what flops, banned habits
   (e.g. "no default sideways close-up," "spoken not poetic," "romanize text").
   *Every future correction updates this one card instead of becoming a new gate.*
3. **Failure corpus** — the visual-inconsistency images, used by the vision loop.

When you dump new research, Claude distills it into these three — not into more
process. That is the self-improvement loop, and it stays light.

---

## 7. First move: prove it on ONE post, don't rebuild

Do **not** migrate the skill first — that's how the last 18 plans died.

1. Pick one concept (ghar for a clean head-to-head, or remix a winner engine like
   `DYJpjt9CQYY`'s "married 'mujhe kuch nahi hua'").
2. Run the §4 flow **by hand** in chat: Claude directs (using your assets), you gate.
3. Write the §5 handoff folder; you paste one prompt into Codex; generate.
4. Vision-loop the pixels; you accept.
5. Ship **one accepted illustration end-to-end** that beats both the machine *and*
   the plain-LM baseline.
6. *Then* — and only then — we shrink `SKILL.md` and delete the rooms.

**One shipped post earns the refactor. Another plan does not.**
