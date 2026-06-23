# Permissioned Winner Remix Workflow - 2026-06-14

This is the corrected workflow after the creator rejected the earlier
mechanics-only abstraction.

## Core Principle

Do not create fresh when a winner already exists.

Start with a specific high-performing post or carousel. Preserve what worked.
When the source is permissioned by the creator, exact copy, premise, caption,
and slide structure are allowed ingredients. A Story's job is not to sanitize
the source into a vague pattern. A Story's job is to make the winning content
feel like it happened between Aachu and Zuv.

## Required Row For Every Candidate

Each remix candidate must be recorded like this:

- Source account:
- Source URL:
- Source format:
- Public/owned metric signal:
- Copy status: exact / lightly edited / premise-only
- What stays:
- What changes:
- A Story wrapper:
- Added slide or payoff:
- Caption move:
- Why people would send/save/comment:
- Slop risk:

If a row cannot name the source URL and what stays, it is not a winner-bank
remix. It is fresh ideation and must be labelled that way.

## Winner Modeling Pass

After one winner post is selected, model it through
`illusion-of-novelty-storytelling-2026-06-18.md` before writing A Story copy or
slide beats.

This pass answers why the winner worked, not just what it said:

- What old/familiar topic did the winner make feel new?
- What new reveal, frame, name, or overlooked angle did it use?
- What viewer outcome did it attach to: send, save, tag, comment, soften, laugh,
  or feel seen?
- What old belief or obvious version did it contrast against?
- Did it have real urgency, or did it work without urgency?
- What was the bullseye proof: exact source performance, lived scene, comment
  behavior, visual receipt, or highly specific personal situation?
- What did the post avoid explaining so the emotional illusion stayed alive?

Then translate those answers into A Story:

- preserve the source winner's working engine;
- keep the same novelty/contrast/proof shape where possible;
- change the lived scene so it belongs to Aachu and Zuv;
- add only the details that make the viewer think, "this is us";
- remove any line that exposes the lesson, explains the psychology, or turns
  the post into clean relationship advice.

The point is not to copy the outer costume of the winner. The point is to copy
the way it made an old feeling feel freshly visible.

## What Counts As A Good A Story Wrapper

Good wrapper changes:

- plain text becomes a couple conversation
- book-page text becomes a scene with Aachu/Zuv acting it out
- quote-card statement becomes a visual payoff in the last slide
- abstract advice becomes a pillow, cup, door, phone, chair, or glance
- one extra final slide makes the relationship implication land harder
- caption reframes the source for A Story without diluting the copied engine

Weak wrapper changes:

- changing a few synonyms
- drawing Aachu and Zuv beside a quote
- inventing a new moral
- replacing a proven line with a cleaner AI-written one
- turning a source winner into an object-led seed with no visible source

## DZNl2zxiRD4 Is The Model

The creator cited `DZNl2zxiRD4` as the correct example:

- The source copy/premise was preserved.
- A Story changed the delivery into a couple conversation.
- A Story added the final slide that made people react.
- The post crossed 1M+ views and kept growing.

This means future research should not say "do not copy." It should say:

Preserve the winning engine. Change the lived scene.

## Storage

- 170-entry visible index:
  `references/text-style/winner-bank-index-2026-06-14.json`
- Durable full scrape with exact source text/captions:
  `references/text-style/winner-bank/winner_bank.json`
- Durable merged scrape:
  `references/text-style/winner-bank/posts_merged.json`
- Scrape run summary:
  `references/text-style/winner-bank/chunk_results.json`
- Winner contact sheet:
  `references/text-style/winner-bank/winner_contact_sheet.jpg`
- Original temporary scrape folder, kept only as backup:
  `/private/tmp/astory_winner_mining_v2/`
- Correction captured:
  `runs/2026-06-14_17-51_ig-reference-concept/planning/creator_direction_notes.md`
