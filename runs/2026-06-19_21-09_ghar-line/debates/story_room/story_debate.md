# Story Room Debate

Run: `2026-06-19_21-09_ghar-line`

## Evidence Ledger

| Artifact | Path | What We Used | Gap Or Risk |
| --- | --- | --- | --- |
| Creative brief | `runs/2026-06-19_21-09_ghar-line/input/creative_brief.json` | Creator's repaired Slide 1 and Slide 2 concept | Supplied Slide 2 is too long as one illustration |
| Creator corrections | `runs/2026-06-19_21-09_ghar-line/planning/creator_direction_notes.md` | Prior slide 2 rejected as fake-soft/generic; no welcome-back lane | Must keep the new version from becoming quote-card |
| Memory recall | `runs/2026-06-19_21-09_ghar-line/planning/memory_recall.md` | Sendability and exact-run rejection memory | No live platform research |
| Source winner contract | `runs/2026-06-19_21-09_ghar-line/planning/source_winner_remix_contract.json` | Premise-only person-as-home engine | Do not copy external text |
| Novelty model | `runs/2026-06-19_21-09_ghar-line/planning/source_winner_novelty_model.json` | New reveal: the untouched side proves the ache | If the kept side is unclear, it becomes quote-card |
| Winner landing comparison | `runs/2026-06-19_21-09_ghar-line/planning/winner_landing_comparison.md` | Preserve short, direct sendable recognition | Stale welcome-back language was repaired before this pass |
| House style | `.agents/skills/astory/references/house-style-contract.md` | Scene must prove text; readable integrated hand text; no quote-card | Imagegen still gated on references and repo QA |

## Premise Lock

The approved emotional truth is: without one specific person, even a familiar home feels hollow. This is not a request for the person to come back tired, not a needy comfort note, and not a public lesson that "home is a person."

The physical receipt is the kept usual side. Aachu does not take Zuv's place even when he is absent.

## Agent Positions

### Story Director / Dev

Dev recommended a 3-slide structure:

1. Exact lyric and empty kept side.
2. Heart returning plus familiar corners empty.
3. Safe silence plus one-person-home payoff.

Strength: protects the original two-part shape and avoids over-explaining. Risk: slide 2 and slide 3 both remain text-heavy, and the final "sense of home" realization may still feel crowded.

### Pacing Editor / Nina

Nina recommended 4 slides:

1. Exact lyric.
2. Heart keeps returning.
3. Familiar corners feel empty.
4. Safe silence and one-person-home payoff.

Strength: each slide changes the viewer's understanding and the text remains readable. Risk: if the fourth slide overplays "Ghar was never a place," it can become a moral.

### Swipe Retention Critic / Arjun

Arjun recommended 4 slides max. He marked the original one-block Slide 2 as `TEXT_UNREADABLE`, cut "That is the real ache of Ghar..." from visible text, and argued the payoff should be safe silence rather than an explained moral.

## Studio-Head Decision

Use 4 slides.

Why: the creator's repaired Slide 2 contains four distinct turns: person becomes a place, familiar corners empty, silence safe, home was one person. Forcing them into one or two additional slides repeats the earlier failure: good emotion, heavy execution. Four slides give the text and scene enough air while staying below the point where it becomes a lesson.

## Locked Slide Text For Story Approval

### Slide 1

```text
Khaali hai jo tere bina,
main woh ghar hoon tera.
```

### Slide 2

```text
Some people don't just enter your life,
they become the place
your heart keeps returning to.
```

### Slide 3

```text
Without them,
even the most familiar corners
feel empty.
```

### Slide 4

```text
And with them,
even silence feels safe.

Ghar was never a place.
It was always that one person.
```

Cut from on-image text:

```text
That is the real ache of Ghar -
not just missing someone, but realizing that...
```

This line remains concept/caption logic only, because on-image it explains the carousel instead of letting the scene prove it.

## Story Lock Risks

- `TEXT_UNREADABLE`: Slide 4 is the longest and needs prompt-room text layout attention.
- `AI_SLOP_COPY_DRIFT`: The final two lines can become generic if the visual does not first prove the kept side and safe silence.
- `QUOTE_CARD_NOT_ILLUSTRATION`: Every slide must keep the room/body behavior visible, not just text over a soft background.
- `GOLD_STANDARD_IDENTITY_ROUTE_MISSING`: Final imagegen remains blocked until the reference visibility and repo QA gates pass.
