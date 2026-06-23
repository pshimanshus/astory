---
name: anti-ai-slop-human-copy-filter
description: >-
  Use when Codex is about to think toward or produce any relationship, romance,
  humor, social, Instagram, A Story of Two, or creator-facing creative artifact:
  captions, hooks, on-screen text, carousel copy, reel scripts, storyboards,
  visual suggestions, scene directions, prompt copy, imagegen prompts, caption
  packs, or creative thought that shapes a written artifact. This skill is
  mandatory when the work could become preachy, polished, generic, therapy-page,
  motivational, platform-blind, or AI slop.
---

# Anti-AI-Slop Human Copy Filter

## Core Principle

The output should not sound written. It should sound felt.

This skill fires before any visible creative writing and before any creative
thinking that will shape copy, visuals, storyboards, prompts, captions, hooks,
scenes, or creative direction. Do not treat it as a polish pass after drafting.
It is the first layer of the creative loop.

## Current Creator Copy Contract

Apply these active A Story of Two constraints before drafting:

- Every line is written as a sentence someone could send, not a content pillar.
- The source-bank forms stay visible, but they are not treated as templates to fill.
- Visual wrappers are restrained; they prove the feeling without becoming quirky behavior.
- No chappal, dhaniya, roti, spoon, or object-led invention leads the premise.
- The copy aims for "I needed to say this" before "this is a carousel."
- Do not create polished "texts"; say the unsaid love thing in simple English.
- Use short, easy sentences that feel like someone is saying the line to their person.
- Avoid pretentious phrasing, abstract relationship words, and clever love-copy language.

## Mandatory Trigger

Use this skill before:

- captions
- on-screen text
- carousel copy
- reel hooks
- storyboards
- visual suggestions
- scene directions
- imagegen or creative prompts for creative content
- caption packs
- creative thought that leads to written creative artifacts
- any A Story of Two idea, scene, storyboard, prompt, packaging note, or copy
  recommendation

If another creative skill also applies, run this one first for taste and
platform grounding, then run the domain skill.

## Non-Negotiable Loop

For creative work, the loop is:

`Research -> Pattern Hypothesis -> Human Draft -> Slop Audit -> Rewrite -> Output`

Do not skip straight to draft. Do not ship the first emotionally tidy version.
If the output still sounds like a lesson, quote card, therapy page, brand deck,
or generic romantic reassurance, loop again.

## Default First Layer

Viral Research Layer is not optional for creative jamming.

When starting a jam, giving suggestions, selecting a direction, writing copy,
or proposing visuals, first ground the work in evidence. This applies to copy,
visuals, storyboards, prompts, captions, hooks, scenes, or creative direction.
In short: copy, visuals, storyboards, prompts, captions, hooks, scenes, or creative direction.

The research layer can be short or deep depending on the ask, but it must exist:

- For quick chat suggestions, do a fast evidence scan from local memory and
  known platform mechanics before writing.
- For A Story production, write the evidence basis into the relevant run
  artifact or Evidence Ledger.
- For strategy, ideation, or "what will work" questions, run a fuller research
  pass before recommending angles.
- If live research is unavailable, use latest local evidence and add an
  evidence gap note. Do not pretend current-market research happened.

## Research Worker

Start with evidence before taste.

1. **Local Performance Evidence**
   Read or search the strongest available local sources first:
   - `references/brain/pages/outcome-attribution.md`
   - `references/brain/reports/outcome_attribution.json`
   - `data/instagram/carousel_posts/*/carousel_export.json`
   - relevant `runs/<run_id>/evals/*engagement*` files when present
   - relevant creator corrections in `runs/<run_id>/planning/creator_direction_notes.md`

   Rank patterns by shares per 1k reach, saves per 1k reach, comments per 1k
   reach, profile/follow conversion, and reply/send potential. Likes are
   secondary because likes can disagree with send behavior.

2. **Live Platform Evidence When Available**
   If current platform patterns matter, use Apify or other approved research
   tools only through environment variables such as `APIFY_API_TOKEN`,
   `APIFY_TOKEN`, `APPIFY_API_TOKEN`, or `APIFY_USER_ID`.

   Never print, expose, store, or log the token. Never hardcode it into repo
   files, run artifacts, prompts, command strings, screenshots, or terminal
   output. If a command may echo env values, do not run it.

   Study mechanics for non-permissioned public research:
   - first-frame hook shape
   - on-screen text length and grammar
   - caption structure
   - comment trigger
   - send-to-partner trigger
   - save trigger
   - image or visual composition pattern
   - carousel pacing pattern
   - savage/funny spouse-coded formats
   - fight-repair formats
   - Hinglish and Indian couple patterns
   - formats where the line feels like a DM, not an essay

   For non-permissioned public research, extract emotional mechanics only.
   Do not reproduce another creator's caption, premise, or phrasing unless the
   creator has explicitly permissioned the source for reuse.

   For a permissioned source-preserving remix, the job changes. The source
   winner is no longer a vague inspiration pattern; it is the working engine.
   Exact copy, premise, caption, and slide structure may be preserved when the
   creator has permissioned that source. Record what stays, what changes, and
   the A Story wrapper that turns the proven post into a lived Aachu/Zuv moment
   instead of a plain quote-card repeat.

3. **Evidence Gap Rule**
   If local files are missing, live research is blocked, Apify is unavailable,
   or handles are not known, name the gap in the artifact notes and keep the
   recommendation provisional. Missing research is not fatal for every tiny
   response, but hiding the gap is a failure.

For deeper research instructions, read `references/viral-research.md`.

## Context Lock

Before drafting, answer these silently or in the artifact notes:

- What is the exact human situation?
- Who is speaking?
- Who is receiving it?
- What emotion should it trigger?
- Why would someone share this?
- What exact words/setup must not be moved away from?
- What is the creator trying to make the viewer feel in the body, not
  understand in the head?
- What would make a real couple send this to each other today?

The user's original words, premise, and setup are binding unless the user
explicitly asks for a new angle. Do not convert raw emotion into a cleaner
metaphor, lesson, or therapy-language explanation.

## Permissioned Source-Preserving Remix

When the creator says a source winner is permissioned, do not hide it behind
abstract "pattern intelligence." Attach the work to the actual source and keep
the winning engine visible.

Required before drafting from a winner:

- source account, URL, format, and metric signal;
- copy status: exact, lightly edited, caption-preserved, or premise-only;
- exact copy, premise, caption, and slide structure that are allowed to stay;
- the A Story wrapper: couple conversation, daily-life scene, added final
  payoff, caption frame, or visual moment that makes it ours;
- what must not be "improved" into AI polish;
- what would make the remix weaker than the source winner.

The anti-slop question becomes: preserve the winning engine, then ask, "Would a
real person send this to their partner?" If the answer depends on a clean moral
or generic quote-page polish, rewrite back toward the source and the lived
couple moment.

## Emotional Jobs

Every line or visual direction must do at least one:

- make someone laugh
- make someone send it to their partner
- make someone say "this is us"
- make someone feel seen
- make someone feel love, nostalgia, or missing-them ache
- make someone feel playful anger
- make someone feel soft after a fight
- make someone save the post
- make someone tag their person
- make someone feel brave enough to restart a conversation
- make someone think "I hate that this is accurate"

If a line only explains the feeling, it has not done the job.

## AI Slop Detection

Reject and rewrite anything that sounds:

- preachy
- over-polished
- motivational-speaker-like
- generic couple-content
- too poetic
- too perfect
- emotionally vague
- platform-blind
- written for everyone but felt by no one
- like a brand wrote it
- like a therapy page wrote it
- like an Instagram quote page from 2018
- like a carousel trying to teach love instead of trigger a share
- like a clean moral attached to a messy human moment

## Banned Directions

Do not use or drift toward:

- "In a world where..."
- "Love is not about..."
- "True love means..."
- "At the end of the day..."
- "Sometimes the smallest things..."
- "Real love is when..."
- "Choose someone who..."
- generic life lessons
- forced depth
- moral of the story endings
- polished healing-language conclusions
- therapy-summary copy
- abstract reassurance that could fit any couple
- overused couple tropes unless made freshly specific

If the output could sit on a generic relationship quote account, it fails.

## Human Rewrite Rules

Rewrite until the copy feels:

- conversational
- slightly imperfect
- specific
- emotionally obvious
- platform-native
- easy to send
- easy to imagine in a real couple's chat
- shareable without explanation
- tied to a physical object, gesture, phrase, silence, timing, or habit
- close to the user's original setup
- not trying too hard

Prefer:

- a half-joking accusation over a polished confession
- an object doing emotional work over a sentence explaining emotion
- one painfully specific behavior over a universal lesson
- a line someone would text over a line someone would frame
- a setup that lets the viewer complete the feeling

Delete any line that sounds "good" but not sendable. Delete any line that
teaches instead of making people feel. Delete any line that moves away from the
provided setup.

## Visual Suggestion Rules

This filter applies to visuals too. A visual suggestion is slop when it says
"cozy", "romantic", "intimate", "soft", or "warm" without proving the feeling
through a scene.

Before proposing visuals, name:

- the platform mechanic the visual is serving
- the exact scene action
- the object, distance, body position, eyeline, or negative space carrying the
  emotion
- why someone swipes, saves, comments, or sends from that frame
- what first-obvious generic scene you are rejecting

For A Story of Two, do not force both people into every slide. Use one person,
hands, an object, aftermath, a doorway, a message, or empty space when that is
truer and more shareable.

## Self-Enforcement

Block output or mark it unsafe when:

- no evidence basis exists for a creative recommendation
- the Viral Research Layer was skipped during jamming
- the original setup drifted
- the emotional job is unclear
- the line explains instead of triggers
- the scene could be generated by any competent LLM
- the copy would not plausibly be sent in a real relationship
- the visual suggestion is only mood words
- the output is clean, correct, and dead

Use failure codes. Repair before presenting the work as a recommendation.

## Silent Quality Test

Before final output, ask:

- Would a real person send this to their partner?
- Does this sound like something someone would actually say?
- Is it too clean?
- Is it trying to teach instead of making people feel?
- Did I stay close to the original setup?
- Is there a real emotional reason to share this?
- Can this work as on-screen text within 2 seconds?
- Does the visual prove the line without explaining it?
- Did I extract mechanics rather than copy another creator?
- Did I name the evidence gap if live research was not available?

If any answer fails, run the loop again.

## Output Shape For Copy Tasks

For direct copy requests, provide only useful variants:

- Viral on-screen text options
- Caption options
- More human/raw versions
- Savage/funny versions when relevant
- Soft/emotional versions when relevant
- Visual hooks when useful
- Minimal SEO keywords only

For internal A Story artifacts, do not bloat the output. Apply the filter and
record the context lock, evidence basis, emotional job, rejected generic version,
and `AI_SLOP_COPY_DRIFT` risk where useful.

## Failure Codes

- `AI_SLOP_COPY_DRIFT`
- `VIRAL_RESEARCH_LAYER_SKIPPED`
- `ORIGINAL_SETUP_DRIFT`
- `PREACHY_THERAPY_LANGUAGE`
- `SHARE_TRIGGER_MISSING`
- `EMOTIONALLY_VAGUE`
- `TOO_POLISHED`
- `PLATFORM_MECHANIC_MISSING`
- `VISUAL_ONLY_MOOD_WORDS`
- `EVIDENCE_GAP_UNDISCLOSED`
- `VIRAL_RESEARCH_TOKEN_LEAK_RISK`
