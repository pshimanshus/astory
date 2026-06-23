# Memory Recall

Run: `2026-06-11_23-45_reel-side-eye`
Query: `couple banter reel sending teasing side-eye carousel humor`

## Cited Findings

- `claim:88f81213cad79449` (promoted): a filename containing `accepted_candidate` is not final acceptance proof; final status requires explicit image QA + creator approval evidence. Source: `references/brain/pages/run-lessons.md`.
- `claim:ed11d6f016d3b4e2` (promoted): final Aachu/Zuv imagegen requires loading the queued local reference images with `view_image`; prompt-only generation is forbidden. Source: `references/brain/pages/run-lessons.md`.
- Couple-banter lesson: "The humor must stay affectionate; any harsh restraint, irritation, or quote-card treatment fails." Source: `runs/2026-06-10_22-55_couple-banter/planning/selected_idea.json`.
- Promise-in-three risk note: prevent hand-anatomy issues; keep faces readable; avoid forced gestures. Source: `runs/2026-06-11_23-05_promise-in-three/planning/selected_idea.json`.

## Retrieval Evidence

- `python3 scripts/astory_brain_cli.py doctor --repo-root .` (2026-06-11): runtime ready; learning `operational_with_review_queue` (2 promoted, 1 quarantined, 0 open reviews, 0 required human decisions).
- Promoted claims read from `references/brain/pages/run-lessons.md` (canonical promoted page).
- Run-artifact lessons read directly from prior run planning files cited above.

## Gaps

- No promoted claims about multi-slide escalation pacing; story room reasoned from house style + jam analysis (open → escalate → pivot → resolve), not memory.
- Review-queue claim candidates in `runs/*/memory/claim_candidates.*` were not used (not production recall truth).

## Usability For This Run

- Affection rule applied to idea critique (rejected no-pivot variant) and to slide 2-3 expression direction (playful, never angry).
- Hand-anatomy lesson applied to scene selection (slide 3 has no hands; slide 4 specifies simple closed grips) and to prompt negative constraints.
- Both promoted claims govern the imagegen handoff: Codex must load the binder queue with `view_image` before generating, and acceptance comes only from image QA + creator approval, never filenames.
- Recall does not bypass any HITL gate or visible-reference requirement.
