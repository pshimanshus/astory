# Image Quality Eval

Run: `2026-06-11_23-45_reel-side-eye`

Status: `blocked`

## Creator Feedback

- No yellow: generated candidates have a yellow/parchment cast.
- Face consistency failed.
- Real face match failed despite supplied references.
- Style reads anime/cartoon/generic instead of approved A Story style.

## Rejected Candidates

- `runs/2026-06-11_23-45_reel-side-eye/images/slide_01_4x5_attempt_01_candidate.png`
  - Failure codes: `YELLOW_PAPER_CAST`, `IDENTITY_DRIFT`, `STYLE_DRIFT`
- `runs/2026-06-11_23-45_reel-side-eye/images/slide_02_4x5_attempt_01_candidate.png`
  - Failure codes: `YELLOW_PAPER_CAST`, `IDENTITY_DRIFT`, `STYLE_DRIFT`

## Why This Happened

The active imagegen queue used binder contact sheets, not the raw high-quality
face references. The raw queue contains the selected Aachu/Zuv face anchors, but
the active `view_image_queue` contained five 1200x900 binder sheets. Inside each
identity binder, each face photo is reduced to a 260x260 thumbnail with labels.
That satisfies "visible reference exists" but does not provide enough face-match
signal for final identity work.

The prompt also kept repeating warm-scene language: warm lamplight, warm glow,
warm ivory, camel/tan, terracotta, vintage, paper grain. The hard negative
against yellow was present, but the positive color/lighting language pushed the
model toward parchment.

Finally, the generation request was overloaded: identity preservation, scene,
style, typography, brandmark, palette, and hard negatives were all competing in
one long prompt. The model optimized for a pretty generic watercolor scene with
readable text instead of strict face match and neutral paper.

Operator error: slide 1 was already a hard reject. Generation should have stopped
there instead of continuing to slide 2.

## Gate Decision

Do not continue imagegen from this prompt/reference setup. Retry is blocked until
the reference delivery and prompt weighting are repaired.
