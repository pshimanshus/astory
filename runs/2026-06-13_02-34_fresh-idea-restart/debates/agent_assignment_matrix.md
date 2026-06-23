# Agent Assignment Matrix

Run: `2026-06-13_02-34_fresh-idea-restart`

## Tool Discovery

- Timestamp: `2026-06-13T02:34:00+05:30`
- `multi_agent_v1.spawn_agent`: visible in this session from prior tool discovery.
- Assignment mode for this pass: `fallback_local_passes_with_limitation_recorded`
- Limitation: the visible `spawn_agent` tool contract says to spawn only when the user explicitly asks for sub-agents/delegation. The creator asked to start a fresh idea, not explicitly to delegate. Therefore this restart runs the required personas as labeled local passes and records the limitation instead of silently pretending actual subagents were spawned.

## Rooms

| Room | Agent / Persona | Assignment | Ownership | Hard Rejects | Output |
| --- | --- | --- | --- | --- | --- |
| Idea Room | Relatability Ethnographer / Meera | local pass | raw lived behaviors, tiny true details | sentiment, usefulness, one-sided saint/fool, repeated themes | `debates/idea_room/agent_01_candidates.json` |
| Idea Room | Shareability Strategist / Kabir | local pass | send reason, comment bait, who sends to whom | like-only ideas, recycled winner hooks, vague relatable claims | `debates/idea_room/agent_02_candidates.json` |
| Idea Room | Visual Story Director / Tara | local pass | stageability, prop/world clarity, imagegen feasibility | unstageable moods, crowded scenes, microtext, production traps | `debates/idea_room/agent_03_candidates.json` |

## Success Criteria

- Candidate set must span multiple emotional engines.
- Any candidate whose core is care/logistics/usefulness is rejected before scoring.
- Hooks must not clone known winner shapes.
- The selected shortlist must be presented as raw options, not a forced idea lock.
