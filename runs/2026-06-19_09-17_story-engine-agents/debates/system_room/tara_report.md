# Tara Report - Visual Story Director

## Evidence Basis

Local truth says rank by sends/saves, not likes. The storytelling transcript
adds three production rules:

- visual hook before text/audio;
- build from the final slide backward;
- every slide must move by `but` or `therefore`, never `and then`.

## Required `winner_story_engine` Fields

- `source_identity`: source URL, account, shortcode, format, metric signal,
  copy status, slide structure.
- `source_causality`: why it worked, what must stay, send/save/comment trigger,
  caption move, first-frame stop, swipe reason.
- `novelty_model`: old topic, `new_reveal`, viewer outcome, `contrast_frame`,
  urgency used/skipped, `bullseye_proof`, what not to explain.
- `visual_translation`: lived Aachu/Zuv wrapper, visible receipt,
  object/gesture/eyeline/body-distance proof, first-frame visual hook, payoff
  frame.
- `beat_constraints`: final slide intent first, slide count range, per-slide
  `context_delta`, `conflict_delta`, `but_or_therefore_link`, swipe question,
  proof receipt.
- `imagegen_feasibility`: face proximity, number of faces, prop count, location
  count, text load, microtext risk, anatomy risk, identity-reference need,
  style-fit risk.
- `anti_slop_blockers`: quote-card risk, decorative-wrapper risk,
  moral-explanation risk, source-engine drift risk, generic-romance risk.

## Translating Novelty Into Frames

`new_reveal` becomes the first-frame visual hook. The viewer should see the
contradiction or hidden angle before reading much. If the reveal cannot become
an object, action, distance, or eyeline, it is not ready.

`contrast_frame` becomes swipe tension. Each slide should tighten the old
belief versus the new truth through `but` or `therefore`: new context, then a
complication, then a consequence. No slide gets to merely restate the mood.

`bullseye_proof` becomes the payoff frame. The last frame should show the
receipt that makes the whole thing undeniable without explaining the lesson. If
the proof is only a metric or abstract claim, Story Room must translate it into
a lived scene before story lock.

## Gates Against Quote-Card Failure

- Block before idea lock if `scene_landing_preview.md` is title/score/rationale
  instead of first-frame, swipe reason, mini arc, payoff frame, and send
  trigger.
- Block before story lock if any slide lacks a visible receipt proving the
  text, a `but_or_therefore` transition, or a concrete scene change.
- Block before prompt writing if Aachu/Zuv are merely placed beside source
  copy, a poster, a text card, a book page, or decorative background.

Add or strengthen:

- `VISIBLE_RECEIPT_MISSING`
- `BUT_THEREFORE_CHAIN_MISSING`
- `DECORATIVE_WRAPPER_ONLY`
- `QUOTE_CARD_STAGING`
- `PAYOFF_FRAME_EXPLAINS_LESSON`

## Early Imagegen / Identity Risks

Detect early:

- cramped two-face closeups, face-touching poses, mirror/reflection faces, or
  crowded couple framing;
- too much text, phone screenshots, tiny chat bubbles, or microtext-dependent
  jokes;
- more props/locations/people than one 1080x1350 frame can hold cleanly;
- emotional beats that require perfect subtle facial acting instead of readable
  object/action proof;
- body logic problems: impossible hands, unclear eyelines, awkward crouching,
  prop placement contradictions;
- identity route missing raw Aachu/Zuv anchors, or prompts relying on text
  descriptions instead of visible references;
- style drift into generic watercolor, poster design, parchment/yellow paper,
  anime, photorealism, or over-beautified faces.

## Recommended Slice

Implement the `winner_story_engine` contract inside the existing novelty/scene
pipeline, then update QA only around that contract: `novelty_candidate_ledger`,
`source_winner_novelty_model`, `scene_landing_preview`, and `slide_beat_map`
validators should require visible receipts, `but/therefore` beat links,
payoff-first planning, and imagegen-risk fields.

Keep it small: schema, tests, blockers before touching agent prose.
