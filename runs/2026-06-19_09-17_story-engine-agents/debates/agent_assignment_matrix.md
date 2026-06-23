# Agent Assignment Matrix

Run: `2026-06-19_09-17_story-engine-agents`
Workflow type: `system_strategy_room`
Timestamp: `2026-06-19_09-17_IST`

## Tool Discovery

- `tool_search` query: `multi-agent spawn agent`
- Result: `multi_agent_v1.spawn_agent` available.
- Assignment status: `actual_multi_agent`

## Room Scope

This is not a standard carousel Idea Room. The creator asked to run the proposed
story-engine integration through the in-house trained agents. The room is
therefore a strategy/architecture room focused on incorporating winner-bank
evidence, the illusion-of-novelty doc, and storytelling mechanics into the
system.

## Assignments

| Agent | Persona | Sub-agent id | Nickname | Ownership | Success Criteria | Hard Rejects | Prompt Basis | Expected Output |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Relatability Ethnographer | Meera | `019eddfe-ee78-7633-95cb-89679a091d08` | Nash | Human-truth requirements for the story engine | Names what the system must capture so novelty stays rooted in real couple behavior | Abstract frameworks, therapy-page language, sentiment without behavior | Persona file + anti-slop + strategy prompt | `debates/system_room/meera_report.md` |
| Shareability Strategist | Kabir | `019eddfe-f405-7302-b93a-0b7a45a90508` | Einstein | Distribution and scoring model | Defines how winner matching should encode send/save mechanics and storytelling loops | Likes-first scoring, vague "engagement potential", source-detached novelty | Persona file + anti-slop + strategy prompt | `debates/system_room/kabir_report.md` |
| Visual Story Director | Tara | `019eddfe-f730-7fd2-819a-a16ed3e6e555` | Ampere | Scene-landing and visual-proof constraints | Turns novelty/story mechanics into first-frame, swipe tension, payoff, and imagegen-safe gates | Quote-card wrappers, mood-only visual direction, crowded faces, microtext | Persona file + anti-slop + strategy prompt | `debates/system_room/tara_report.md` |
| Principal Engineer | Idris | `019eddfe-fd2b-7eb2-8707-275360c33dad` | Carson | Minimal implementation architecture | Identifies existing integration points, missing code slice, artifact ownership, and test plan | Untested claims, duplicate gates, broad refactors, dirty-tree churn | Engineering persona + architecture prompt | `debates/system_room/idris_report.md` |

## Shared Evidence Packet

- `runs/2026-06-19_09-17_story-engine-agents/input/creative_brief.json`
- `references/text-style/illusion-of-novelty-storytelling-2026-06-18.md`
- `references/text-style/permissioned-winner-remix-workflow-2026-06-14.md`
- `references/brain/pages/outcome-attribution.md`
- `references/brain/pages/run-lessons.md`
- `.agents/skills/astory/templates/planning/source_winner_novelty_model.json`
- `backend/app/data_refs.py`
- `scripts/astory_repo_qa.py`
- `scripts/astory_orchestrator/spine.py`

## Limitation Notes

- Agents were instructed not to edit files. The main coordinator will summarize
  and write consolidated artifacts after reviewing their returned reports.
- This room does not approve a carousel idea, prompt, imagegen call, or final
  package.
