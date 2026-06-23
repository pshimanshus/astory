# Kabir Report - Shareability Strategist

## Scoring Model

Use a two-stage matcher: first prove travel, then prove story fit.

Recommended score:

`winner_story_score = performance_signal 35 + story_engine_fit 30 + A Story transformability 20 + novelty_preservation 10 + format_fit 5 - risk_caps`

For owned A Story posts, `performance_signal` should rank by shares per 1k
first, then saves per 1k, comments per 1k, follow conversion. Local truth backs
this: `DYJpjt9CQYY` wins on send behavior at 40.15 shares per 1k while likes
alone mislead.

For third-party winner bank posts, public likes or `winnerScore` can only be a
weak prior. Cap any public-only source unless comments, tag/send proxies,
format, and mechanic tags show why people would forward it.

Match by travel mechanism, not topic similarity:

- same viewer outcome;
- same social-risk cover for sending;
- same context/conflict movement;
- same kind of visual receipt;
- preservable final payoff.

## Encoding Story Mechanics

Add a structured `story_engine` layer per shortlisted source winner:

- `beat_map`: slide/reel beats with `context`, `but`, `therefore`, `payoff`;
  penalize pure `and_then` sequencing.
- `visual_hook`: first-frame or first-slide receipt, visible object/action/text,
  and whether the viewer understands before reading caption.
- `last_line_payoff`: final slide/caption/reel line, payoff type, whether it
  loops back to the hook, and whether it avoids explaining the lesson.
- `send_reason`: exact sender, recipient, social cover, likely tag/comment,
  emotional job. "Relatable" is not a reason.
- `novelty_model`: old topic, new reveal, contrast frame, bullseye proof,
  urgency if real, what not to explain.
- `preservation_contract`: what stays, what changes, copy status, A Story
  wrapper.

If any of these are inferred without slide text, transcript, or comments, mark
the gap.

## Backend/Data Loader Missing

`backend/app/data_refs.py` currently reduces the bank to `caption`,
`slide_count`, `comments`, and `send_proxy`. That is too thin.

Missing:

- source URL, account, shortcode, format, timestamp;
- likes/views/comment ratio/tag proxy/latest comments/mechanic tags;
- first-party shares/saves/reach/follows when available;
- slide-level text/OCR, first-frame visual, reel transcript;
- structured hook, voice, prompt type, story beats, payoff;
- permission/remix fields: copy status, what stays, what changes;
- score trace with caps and evidence gaps.

## Failure Modes And Hard Gates

Hard block if:

- source URL or "what stays" is missing;
- selector ranks by likes/`winnerScore` without send/save/comment evidence;
- send reason is generic;
- beat map is just `and_then`;
- final payoff becomes a moral or therapy summary;
- visual hook is only mood words;
- source winner is used as a moodboard instead of a preserved engine;
- novelty changes the winning mechanism instead of revealing it differently;
- evidence gaps are hidden.

Cap score if slide OCR/transcript is unavailable. The system can shortlist, but
it should not claim story-engine confidence.

## Recommended Slice

Build a `winner_story_summary` / `winner_story_engine` shortlist layer before
generation:

- expand backend loader to preserve source, metrics, proxies, comments, tags,
  format, and gaps;
- shortlist top candidates by travel evidence;
- run story-mechanics extraction only on that shortlist;
- output a traceable `source_winner_story_engine` artifact that feeds the
  existing `source_winner_novelty_model.json`;
- add tests that prove likes-only winners cannot outrank send-proven candidates
  without a risk cap.
