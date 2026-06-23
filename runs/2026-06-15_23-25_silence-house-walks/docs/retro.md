# Retro

Run: `2026-06-15_23-25_silence-house-walks`

## What Worked

- Direct-lock workflow preserved the creator's supplied quote and avoided concept drift.
- Prompt-room QA caught real identity and scene-logic risks before imagegen.
- Candidate 3 achieved the best quiet-house composition: readable couple, careful doorway, cup/spoon, and brand style.

## What Failed

- Built-in imagegen did not produce exact Devanagari text after two targeted text retries.
- Built-in imagegen returned `1122x1402` outputs despite explicit native `1080x1350 px` prompts.

## Prevention Note

For bilingual text-heavy A Story posts, separate illustration generation from exact typography only if the creator approves a typography compositing path. Under the current baked-in imagegen-only rule, this run must remain blocked.

## Memory Autopilot

Post-run autopilot ran and created one claim candidate, but rolled back its auto-promotion because retrieval eval failed on stale expected paths. Lint passed; no human intervention was required.
