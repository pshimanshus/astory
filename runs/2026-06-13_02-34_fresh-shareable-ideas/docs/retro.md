# Run Retro

Run: `2026-06-13_02-34_fresh-shareable-ideas`
Status: `blocked_at_hitl_idea_lock_pending_scene_landing_correction`

## What Worked

- The idea room produced fresh, non-generic behavioral ideas.
- Actual multi-agent assignment was discovered and recorded.
- The selected idea, `The Packet Pause`, has a strong tiny behavior and share trigger.

## What Failed Or Drifted

- The recommendation was presented like a strategy artifact: title, score, rationale, risks.
- The creator correctly flagged that good ideas were not landing as scenes or presentations.
- Root cause: the `/astory` skill required idea score/rationale before idea lock, but did not require a scene-landing preview before asking the creator to approve.

## Prompt Lessons

- Do not call an idea final until the first frame, exact hook text, swipe reason, mini slide arc, payoff frame, share trigger, and flat/generic risk are visible.
- A scene must be felt before it is explained.

## Identity / Style Lessons

- Scene landing should keep Aachu/Zuv in concrete body language and props before any prompt writing begins.
- If a scene depends on an abstract explanation rather than visible proof, it is not ready for prompt work.

## Proposed Brain Updates

- Future `/astory` idea locks must include `planning/scene_landing_preview.md`.
- The idea-lock presentation must show scene-first proof, not only selection rationale.
- If the creator says an idea is good but not landing, record the correction immediately in the run retro and update the workflow gate if needed.

## Evidence

- `runs/2026-06-13_02-34_fresh-shareable-ideas/planning/selected_idea.json`
- `runs/2026-06-13_02-34_fresh-shareable-ideas/planning/idea_choice_shortlist.md`
- `runs/2026-06-13_02-34_fresh-shareable-ideas/planning/scene_landing_preview.md`
- `.agents/skills/astory/SKILL.md`
- `.agents/skills/astory/templates/planning/scene_landing_preview.md`
