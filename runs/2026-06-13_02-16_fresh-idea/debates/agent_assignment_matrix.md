# Agent Assignment Matrix

Run: `2026-06-13_02-16_fresh-idea`

Assignment timestamp: `2026-06-13T02:17:00+05:30`

## Tool Discovery

- `multi_agent_v1.spawn_agent` visible at first check: `false`
- `tool_search` used when not visible: `true`
- Tool search query: `multi-agent spawn agent multi_agent_v1.spawn_agent`
- Final assignment mode: `actual_multi_agent`
- Limitation if fallback: `not_applicable`

## Assigned Rooms

This turn is an idea-only `/astory auto` run. Story, prompt, image QA, and final package rooms remain unassigned until the creator approves the idea and asks to continue.

| Room | Agent | Assignment Mode | Agent Id Or Local Label | Prompt Packet | Ownership | Success Criteria | Hard Rejects | Output Path |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Idea Room | Relatability Ethnographer | `actual_multi_agent` | `019ebd96-38b4-7f03-9e59-592f1d53ab1c` | `.agents/skills/astory/personas/idea-room/relatability-ethnographer.md` | Find tiny true couple behaviors and reject sentiment posing as scenes. | 3 behavior-level candidates with exact relational trigger, visual evidence, and non-generic warmth. | Generic romance, greeting-card sentiment, one-sided fool/saint jokes, overposted tropes. | `debates/idea_room/agent_01_candidates.json` |
| Idea Room | Shareability Strategist | `actual_multi_agent` | `019ebd96-5a3b-7a21-b423-4e359a55fb3d` | `.agents/skills/astory/personas/idea-room/shareability-strategist.md` | Identify send-trigger, tag reason, comment bait, and hook strength. | 3 candidates that read as sends, not likes, with warm call-out energy. | Influencer-caption energy, like-only posts, mean teasing, recycled meme template. | `debates/idea_room/agent_02_candidates.json` |
| Idea Room | Visual Story Director | `actual_multi_agent` | `019ebd96-7cb6-7780-95ed-7b2195996d92` | `.agents/skills/astory/personas/idea-room/visual-story-director.md` | Protect stageability, readable props, identity safety, and phone-screen composition. | 3 visually stageable candidates with clear slide arc and production risks named. | Feeling without action, cramped poses, microtext, crowded faces, excessive locations. | `debates/idea_room/agent_03_candidates.json` |

## Gate Decision

- `DISCOVER_AND_ASSIGN_AGENTS`: `complete`
- Failure code if blocked: `not_applicable`
- Next state: `GENERATE_OR_REFINE_IDEAS`
