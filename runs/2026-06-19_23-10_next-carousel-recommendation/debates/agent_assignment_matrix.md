# Agent Assignment Matrix

Run: `2026-06-19_23-10_next-carousel-recommendation`
Timestamp: `2026-06-19T23:10:00+05:30`

## Tool Discovery

`tool_search` for `multi-agent spawn agent` exposed `multi_agent_v1.spawn_agent`.
Assignment status: `actual_multi_agent`.

## Room

Idea Room is required for this `/astory` auto recommendation.

| Agent | Persona Path | Subagent ID | Ownership | Success Criteria | Hard Rejects | Prompt Packet | Output Path |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Relatability Ethnographer | `.agents/skills/astory/personas/idea-room/relatability-ethnographer.md` | `019ee0fa-090b-78a1-875e-9114261d5299` | Tiny true couple behaviors and non-generic emotional receipts. | Candidate ideas are behavior-led, specific, photographable, and sendable. | Greeting-card romance, generic comfort, trope-only partner jokes, sentiment without action. | `.agents/skills/astory/templates/agents/idea_room_agent_prompt.md` plus persona/workflow packet in dispatch. | `runs/2026-06-19_23-10_next-carousel-recommendation/debates/idea_room/agent_01_candidates.json` |
| Shareability Strategist | `.agents/skills/astory/personas/idea-room/shareability-strategist.md` | `019ee0fa-09b4-7bd0-bd4a-d32647269258` | Send/comment trigger, 3-second hook, and platform-native share reason. | Candidate ideas name who sends it, why, and what comment it earns. | Vague engagement rationale, influencer-caption energy, recycled meme shape, mean call-out. | `.agents/skills/astory/templates/agents/idea_room_agent_prompt.md` plus persona/workflow packet in dispatch. | `runs/2026-06-19_23-10_next-carousel-recommendation/debates/idea_room/agent_02_candidates.json` |
| Visual Story Director | `.agents/skills/astory/personas/idea-room/visual-story-director.md` | `019ee0fa-0af8-7f21-a22d-e8f34ef13bc0` | Stageability, first-frame visual proof, slide arc feasibility, and imagegen risk. | Candidate ideas can be staged as A Story watercolor-and-ink scenes without quote-card or crowded-face drift. | Mood-only scenes, forced two-person staging, microtext, impossible body logic, repeated close-angle sideways couple staging. | `.agents/skills/astory/templates/agents/idea_room_agent_prompt.md` plus persona/workflow packet in dispatch. | `runs/2026-06-19_23-10_next-carousel-recommendation/debates/idea_room/agent_03_candidates.json` |

## Evidence Packet Given

- `AGENTS.md` war-on-generic worldview.
- `.agents/skills/astory/SKILL.md` source-winner and idea-lock gates.
- `.agents/skills/anti-ai-slop-human-copy-filter/SKILL.md` copy filter.
- `references/brain/policies/current-copy-contract-2026-06-18.md`.
- `references/brain/pages/outcome-attribution.md`.
- `references/brain/pages/run-lessons.md`.
- `references/text-style/winner-bank-index-2026-06-14.json`.
- `references/text-style/winner-bank/winner_bank.json`.
- Source leads: `ig:DZS2GuipLku`, `ig:DZTTSUBEaRr`, `ig:DYG9a-FEuBQ`, owned `DYJpjt9CQYY`, owned `DY_t4Dek0pq`.

## Limitation

The subagents were asked to write disjoint JSON artifacts directly. Coordinator will merge, critique, repair, score, and select before presenting `HITL_IDEA_LOCK`.
