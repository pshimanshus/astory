# A Story of Two — Studio OS (The Blueprint)

Date: 2026-06-20
Status: **proposed end-to-end direction — read, then decide**
Supersedes: `docs/astory-lean-direction.md` (folds it in and goes wider)

This is the one-shot plan, the way we did the website and the app: a clear soul, a
real strategy, a clean structure, and a technical spec on current Claude / agentic
practice. It is deliberately **subtractive** — we prove it on one story before we
migrate anything.

---

## 0. What we learned (the bottom of it)

After reading the corpus, the runs, and the knowledge base end-to-end, the failure
is not prompts, gates, or models. It is this:

> **The studio performs knowledge it does not actually hold. The soul was never
> captured — so generation can only follow patterns, and patterns are monotony.**

The evidence: `story-canon/` is **0/68** cards with any text (an index of Save the
Cat, Story Grid, Pixar with empty shelves). Your taste-defining stories — *you are
my yellow, what is intimacy, you talk too much / yes because you listen, are you the
one I found, the pillow* — exist **nowhere in the repo as text.** The one good craft
doc (`illusion-of-novelty`) is literally *"a creator transcript pasted once."* It is
the best thing you have because it's the only soul that got written down.

Everything below builds from that single correction: **capture the soul, put one
storyteller with taste in charge of it, and let the machine only do mechanics.**

---

## 1. Soul (non-negotiable)

1. **We do not ship generic.** (Your law, from `AGENTS.md`.) If a tasteless,
   memoryless LLM could have produced it, it failed — even if "correct."
2. **We tell stories, not carousels.** The unit is a *story*. Its length (1, 2, 3,
   5, 10 illustrations) is chosen by the story, never assumed.
3. **Every story starts from one true unsaid feeling** someone aches to say.
4. **Patterns are the enemy; craft is the discipline.** Structure, hook, turn, the
   unsaid — applied *fresh* each time. Never a reusable template.
5. **Range, not a single look.** Your two biggest winners look nothing alike (bright
   wedding vs. dark candlelit sofa). House style is a *quality/finish* standard, not
   a fixed composition.
6. **Aachu & Zuv are real people.** Identity is sacred; likeness is structure, never
   a copied photo.

## 2. Strategy (how we actually win)

- **The moat is captured taste + craft**, not the winner-bank. The bank is what
  *competitors* did; the moat is *your voice and your story sense*, written down so
  the storyteller can stand on it.
- **One Storyteller with taste, not a committee.** A single director mind holds the
  whole arc — feeling → copy → scene → pixels — consulting the craft, the signal,
  and the look. The 13 personas become *lenses that one mind reads*, never voting
  rooms (rooms produced consensus blandness).
- **Two valid origins, never a third:** (a) **remix a specific proven story** + one
  human twist (the pillow law); (b) **originate from a true unsaid feeling** using
  craft. Never invent generic poetry; never templatize a winner.
- **The illustration is the differentiation.** The 715 competitors are text cards;
  we turn a true beat into a *believable Aachu/Zuv lived scene*.
- **Measure the send.** Rank by shares/saves per 1k reach (your `outcome-attribution`
  truth), feed it back. That's the flywheel — and it's the same engine the app
  (consumers) and the site (brand) point outward. **This is a content platform, not
  a printer.**

## 3. Structure — three brains, one mind, two hands

```
                       STUDIO MIND  (AGENTS.md: war-on-generic worldview + routing)
                                    │
        ┌──────────────── one STORYTELLER (Claude, taste-holder) ───────────────┐
        │  reads all three brains, makes ONE confident call, owns the feeling   │
        └───────────────────────────────┬──────────────────────────────────────┘
            CRAFT brain            SIGNAL brain              LOOK brain
        (NEW — the soul)        (have it already)        (have it already)
   storytelling craft +      winner-bank 715 +         face anchors +
   YOUR taste library +      owned outcomes            house-style +
   YOUR voice rules          (inspiration/remix         failure corpus
   (fills empty shelves)      sources, NOT templates)
                                    │
                          handoff package (structured)
                                    │
                         CODEX (the hands — mechanics only)
                  render @1080×1350 · bake romanized text · save
```

**Craft brain is the missing soul** — and the whole point. Concretely a new
`references/craft/`:
- `taste-library/` — your example stories as **story cards**: the exact on-image
  copy, the *unsaid feeling* underneath, why it worked (metric or reason), the craft
  move, the format length. (yellow, intimacy, the pillow, Monica-Chandler, are-you-
  the-one, you-talk-too-much…) This is your taste DNA.
- `story-craft/` — the actual teachings, distilled in your voice, that fill the
  empty `story-canon` shelves: Save the Cat beats, Story Grid love-genre obligatory
  moments, Pixar's rules, visual storytelling, the "mathematics of storytelling."
- `voice.md` — your copy laws: spoken not poetic, Hinglish that a real person sends,
  the unsaid, no therapy-page, no pattern-filling.

These are stable → **prompt-cached** so every story is cheap and fast to generate.
Your #10 ("make it learn") = every new transcript/example updates these brains. That
is the learning loop — sharpen one mind, never add a gate.

## 4. The flow — one story, end to end

```
1. SEED        a true unsaid feeling · a proven story to remix · a song line /
               pop-culture ref / metaphor

2. STORYTELLER (Claude · extended thinking · reads CRAFT+SIGNAL+LOOK, cached)
     - name the unsaid feeling; write the plain-LM baseline (the floor)
     - choose the story AND its natural length (1–N), not a default carousel
     - write copy in your voice: spoken, true, the turn, the landing, the send
     - design each illustration as a SCENE that proves/turns the feeling
       (Tara's eye: two people? body language? the one prop/receipt? fresh frame?)
     - must beat the baseline and not be generic, or it doesn't pass
   ── GATE A (you): read copy + 1-line visual intent per illustration. go/no-go.

3. HANDOFF     Claude writes a STRUCTURED package (JSON schema) Codex runs:
               per-illustration positive prompt · exact romanized on-image text ·
               the raw 4+4 face anchors to view_image (binders excluded) ·
               1080×1350 · brandmark

4. CODEX       one paste-able prompt → view_image anchors → render one at a time →
               bake text → save to runs/<id>/images/

   ⟳ VISION-JUDGE LOOP (the missing Claude feature): Claude *looks* at each PNG vs
     (a) the intended feeling, (b) the failure corpus, (c) the house style, (d) the
     taste North Star. Fail → one targeted fix → re-render. Max 3.
   ── GATE B (you): eyeball pixels. accept/reject.

5. SHIP → MEASURE  shares/saves per 1k → feed SIGNAL + CRAFT brains.
```

## 5. Technical spec (current Claude / agentic practice)

- **Single-director agent.** One taste-holding loop owns the story. **Subagents only
  for genuinely parallel *research*** (pull fresh winners, mine the corpus) — never
  to make the creative call — and every subagent gets a full identity packet
  (`AGENTS.md` already mandates this).
- **Vision as the QA judge.** Claude's multimodal read of the rendered pixels is the
  real gate — generate→critique→revise against a true signal (the image), not a
  rubric. This single mechanism would have caught the ghar smile and the stale
  solo-portrait on sight.
- **Prompt caching** on the three brains + face-anchor context, so each story is a
  cheap delta, not a 700-file re-read.
- **Structured outputs** for the handoff package — deterministic JSON Codex executes
  one-shot. No prose ambiguity at the hand-off seam.
- **Skills, slimmed.** `/astory` stays as the workflow entry but becomes a ~1-page
  storyteller skill, not a 672-line, 8-room state machine.
- **MCP** for live Instagram insights → keeps SIGNAL brain current.
- **Evals, done right** (three, no rubric theater): (1) deterministic mechanical —
  vision-verify exact text, canvas size, faces present; (2) a held-out **taste North
  Star** — your accepted winners + known flops the vision-judge compares against;
  (3) the only real one — **send-behavior in production.**
- **Model routing.** Opus 4.8 for the storyteller + vision-judge (taste lives in the
  big model); Haiku 4.5 for cheap mechanical checks. Codex `imagegen` for pixels (no
  API key — your locked rule).
- **Text:** romanized Hinglish by default (renders; matches winners). Devanagari only
  on your explicit call, flagged high-risk.

## 6. Keep / Delete / Build

**Keep (your edge):** `illusion-of-novelty`, Visual Story Director (Tara), the
face-match mechanism (`imagegen-contract`), `outcome-attribution`, the winner-bank,
`house-style-contract`, the failure corpus, the studio-mind worldview, a *light* run
folder.

**Delete (ceremony, not taste):** the 8 debate rooms as multi-agent dispatch; the
~18 per-run eval files; the 13-artifact `gold_standard_identity_route_gate` (→ a
5-line pre-flight); per-run remix/novelty JSON ceremony; `agent_assignment_matrix`;
`SKILL.md` 672 lines → ~1 page.

**Build (small, soul-first):** the **CRAFT brain** (`references/craft/` — the missing
soul); the **vision-judge loop**; the **corrected Codex handoff**; the lean
storyteller skill.

## 7. First move — prove it on ONE story (not a rebuild)

1. Seed the CRAFT brain with a starter: 5–8 of your example stories as story cards +
   `voice.md` + the novelty doc (we already have it) + a first pass at the craft
   notes. (This is the soul, captured at last.)
2. Direct **one** story end-to-end the new way — Claude storytells from the craft
   brain, you gate, Codex renders, vision-judge loops.
3. Ship **one accepted illustration/story** that beats both the old machine *and* the
   plain-LM baseline.
4. *Then* — and only then — delete the rooms and slim the skill.

**One shipped story earns the refactor. Another plan does not.**
