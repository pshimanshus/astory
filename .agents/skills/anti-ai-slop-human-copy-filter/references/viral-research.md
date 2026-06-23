# Viral Research Layer

## Default First Layer

Start with evidence before taste.

Viral Research Layer is not optional for creative jamming. It is the first layer
whenever Codex starts jamming, suggests copy, suggests visuals, ranks ideas,
writes storyboards, writes prompts, or recommends creative direction.

The point is not to lazily copy what is trending. The point is to understand
what is currently making people save, share, tag, comment, or DM their person,
then use that evidence correctly.

If the source is not permissioned, extract the mechanic without reproducing the
creator's language. If the creator has permissioned a source winner, use a
permissioned source-preserving remix: keep the winning engine visible, preserve
what is allowed to stay, and build the A Story wrapper around it.

## Dynamic Loop

Run this loop before the final recommendation:

`Research -> Pattern Hypothesis -> Human Draft -> Slop Audit -> Rewrite -> Output`

Loop rules:

- If the research does not reveal a share/send/save mechanic, keep looking or
  mark `EVIDENCE_GAP_UNDISCLOSED`.
- If the pattern hypothesis is only "make it emotional", reject it.
- If the draft sounds like a lesson, quote card, therapy page, or brand caption,
  reject it.
- If the visual suggestion only says mood words such as "soft", "warm",
  "intimate", "cozy", or "romantic", reject it.
- If the rewrite moves away from the user's original words/setup, bring it back.

## Local Evidence First

Read or search:

- `references/brain/pages/outcome-attribution.md`
- `references/brain/reports/outcome_attribution.json`
- `data/instagram/carousel_posts/*/carousel_export.json`
- relevant `runs/<run_id>/evals/*engagement*` files
- relevant `runs/<run_id>/planning/creator_direction_notes.md`
- relevant `runs/<run_id>/docs/retro.md`

Prefer:

- shares per 1k reach
- saves per 1k reach
- comments per 1k reach
- profile visits or follow conversion when available
- replies, DMs, tags, or send-trigger evidence when recorded

Likes are secondary. A post can be liked because it is pretty and still fail as
a send/save artifact.

## Live Research With Apify

If live Apify research is unavailable, use local evidence and return an evidence
gap note instead of pretending current-market research happened. Always return an evidence gap note when the gap changes confidence.

Use live research when:

- the user asks what is working now
- the user asks for copy or visual suggestions where current platform mechanics
  could change the answer
- the work is a new A Story jam, strategy pass, idea room, caption pack, reel
  hook set, or visual direction pass
- local evidence is stale, weak, or mismatched to the current theme

Use tokens only from environment variables:

- `APIFY_API_TOKEN`
- `APIFY_TOKEN`
- `APPIFY_API_TOKEN`
- `APIFY_USER_ID`

Never print, expose, store, or log token values. Never hardcode tokens into repo
files, run artifacts, prompts, terminal commands, screenshots, or debug output.
If a command might echo env values, do not run it.

When live research is available, sample relevant handles or posts and extract:

- first-frame hook wording pattern
- exact on-screen text length and placement pattern
- whether text is question, accusation, confession, list, contrast, or punchline
- caption length and structure
- comment prompt type
- send-to-partner trigger
- save trigger
- visual object or staging mechanic
- carousel slide count and pacing
- reveal or payoff timing
- humor type: savage, domestic, mock accusation, apology, teasing, absurd
- emotional type: fight repair, missing them, insecurity, devotion, nostalgia
- language code: English, Hinglish, Hindi-English rhythm, Indian couple slang

For non-permissioned public research, extract mechanics, e.g. "mock complaint
that becomes a care receipt by slide 4" or "ordinary object proves the apology
before either person says sorry."

For permissioned winners: Do not reduce permissioned source winners to vague mechanics.
Preserve the winning engine. Record the source winner, public or owned metric
signal, exact copy/premise/caption/slide structure allowed to stay, what
changes, and the A Story wrapper that turns the source into a lived couple
moment.

## Pattern Hypothesis

After evidence, write a compact pattern hypothesis:

- observed mechanic
- likely share/save reason
- emotion it triggers
- how it could adapt to this exact user setup
- what would make it generic
- what wording or visual trope must be avoided

Weak hypothesis:
"People like emotional posts, so make it soft."

Usable hypothesis:
"The share trigger is a mock accusation that lets the sender say 'this is me'
without apologizing directly. For this setup, keep the question raw and let the
care object answer it."

## Creative Application

For copy, derive:

- first-slide hook options
- raw human phrasing
- savage/funny options
- soft/emotional options
- caption options
- comment or send prompt
- rejected generic version

For visuals, derive:

- first-frame visual hook
- object or gesture carrying the feeling
- camera distance and negative space
- what does not need faces
- what would make the image feel first-obvious
- what the scene must prove without caption help

For storyboards, derive:

- slide count reason
- swipe question per slide
- emotional turn
- payoff behavior
- share trigger
- flat/generic risk

## Research Output

For quick chat, keep the evidence basis terse. For run artifacts, include enough
to audit:

- source/date or local export id
- observed mechanic
- metric signal if available
- why it likely shares/saves/comments
- adaptation for this exact setup
- risk of becoming generic
- evidence gap note, if live research or local data was unavailable

Do not let research bloat the creative output. The viewer should feel the final
piece, not see the homework.
