# Image QA Debate

Run: `2026-06-07_17-57_auto`

Candidates reviewed:

- `runs/2026-06-07_17-57_auto/images/slide_01_post_4x5_attempt_03_candidate.png`
- `runs/2026-06-07_17-57_auto/images/slide_01_story_9x16_attempt_01_candidate.png`
- `runs/2026-06-07_17-57_auto/images/slide_02_post_4x5_attempt_01_candidate.png`
- `runs/2026-06-07_17-57_auto/images/slide_02_story_9x16_attempt_01_candidate.png`
- `runs/2026-06-07_17-57_auto/images/slide_03_post_4x5_attempt_01_candidate.png`
- `runs/2026-06-07_17-57_auto/images/slide_03_story_9x16_attempt_01_candidate.png`
- `runs/2026-06-07_17-57_auto/images/slide_04_post_4x5_attempt_01_candidate.png`
- `runs/2026-06-07_17-57_auto/images/slide_04_story_9x16_attempt_01_candidate.png`

## Face Match Reviewer

Status: `accept_with_minor_risk`

Per-person scores:

- Aachu face match: `3.9/5`
- Zuv face match: `3.8/5`
- Cross-slide consistency: `4.2/5`
- Hair/beard continuity: `4.0/5`
- Skin tone continuity: `4.1/5`
- Reference influence visibility: `3.9/5`

Visible matches:

- Aachu keeps the long dark hair, soft oval face, strong brow/eye structure, and quiet self-contained expression from the selected references.
- Zuv keeps the dark hair, beard density, medium skin tone, and attentive expression from the selected references.
- The couple remains consistent across the 8 candidates; no face merge, age drift, or swapped identities are visible.

Drift notes:

- Both characters are slightly idealized in the house illustration style, especially Zuv's curl volume and Aachu's model-like profile.
- This is a soft risk rather than a hard rejection because the reference influence remains visible and the style contact sheet supports this degree of romantic stylization.

Failure codes: `[]`

## Style Fidelity Reviewer

Status: `retry`

Style scores:

- Paper tone: `4.6/5`
- Linework: `4.4/5`
- Watercolor texture: `4.4/5`
- Premium editorial feel: `4.3/5`
- Text integration: `4.5/5`
- Palette discipline: `4.2/5`
- Brandmark presence and exactness: `3.2/5`

Style pass notes:

- Neutral ivory paper and visible grain are present across all candidates.
- Fine ink/pencil lines, transparent watercolor washes, terrace details, and handmade text match the observational-intimacy premium style.
- The set avoids photorealism, anime, poster text, quote-card layout, and yellow/parchment cast.

Style failures:

- Slide 2 post brandmark appears malformed as `@a.storyuf.two`.
- Slide 4 post brandmark appears malformed as `@a.storyofl.two`.

Failure codes: `TEXT_NOT_EXACT`

## Publishing QA Reviewer

Status: `retry`

Publishability score: `3.7/5`

Accepted candidates:

- Slide 1 post: accept.
- Slide 1 story/reel: accept.
- Slide 2 story/reel: accept. Curly handwritten quotation marks around `"I'm fine"` are readable and preserve the approved line's meaning.
- Slide 3 post: accept.
- Slide 3 story/reel: accept.
- Slide 4 story/reel: accept.

Retry candidates:

- Slide 2 post: hard reject because the bottom-right brandmark is not exact.
- Slide 4 post: hard reject because the bottom-right brandmark is not exact.

Asset gaps:

- Final exports and package are intentionally not produced until the Image QA gate passes.
- Two native 4:5 post retries are required before final QA.

Manual review notes:

- All post candidates are native 4:5 at `1122 x 1402`.
- All story/reel candidates are native 9:16 at `941 x 1672`.
- On-image story text is readable and aligned with the approved prompt pack.
- The two post brandmark failures must not be hidden or shipped.

Failure codes: `TEXT_NOT_EXACT`

## Arbiter Decision

`retry`

Six of eight candidates can move forward after creator approval, but the set cannot be published because two post surfaces have malformed brandmarks. Retry only:

- `slide_02_post_4x5`
- `slide_04_post_4x5`

Do not regenerate the six accepted candidates unless the creator asks for broader visual changes.

## Required Retry Prompt Delta

For both retry surfaces, preserve the same scene, aspect ratio, character placement, wardrobe, paper tone, exact story text, and style. Add this targeted delta:

> Render the tiny bottom-right handle exactly as `@a.storyof.two`, using simple handwritten lowercase letters. Do not invent, shorten, replace, or add extra letters. Keep it low-contrast but readable. If unsure, leave extra quiet margin around the bottom-right mark so it remains clear.

If imagegen fails the exact handle again after retry, use a no-brandmark art retry and reserve the exact handle for a final packaging overlay after creator approval.
