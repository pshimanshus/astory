# Agent Assignment Matrix

Run: `2026-06-13_02-33_fresh-slate`

Assignment timestamp: `2026-06-13T02:34:00+05:30`

## Tool Discovery

- `multi_agent_v1.spawn_agent` visible at first check: `true`
- `tool_search` used when not visible: `false`
- Final assignment mode: `actual_multi_agent`
- Limitation if fallback: `not_applicable`

## Assigned Rooms

This turn is a fresh idea-only `/astory auto` run. Story, prompt, image QA, and final package rooms remain unassigned until the creator chooses an idea and asks to continue.

| Room | Agent | Assignment Mode | Agent Id Or Local Label | Prompt Packet | Ownership | Success Criteria | Hard Rejects | Output Path |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Idea Room | Relatability Ethnographer | `actual_multi_agent` | `019ebda6-13be-77d1-97f4-98c2576d2baa` | `.agents/skills/astory/personas/idea-room/relatability-ethnographer.md` | Find tiny true couple behaviors and reject sentiment posing as scenes. | 4 fresh behavior-level candidates that avoid prior shortlist patterns and have exact relational triggers. | Generic romance, greeting-card sentiment, one-sided fool/saint jokes, overposted tropes, previous shortlist repeats. | `debates/idea_room/agent_01_candidates.json` |
| Idea Room | Shareability Strategist | `actual_multi_agent` | `019ebda6-3c39-7982-8b3f-fbf502666a60` | `.agents/skills/astory/personas/idea-room/shareability-strategist.md` | Identify send-trigger, tag reason, comment bait, and hook strength. | 4 fresh candidates with clear share/comment mechanics and warm call-out energy. | Like-only posts, influencer-caption energy, mean teasing, recycled meme templates, previous shortlist repeats. | `debates/idea_room/agent_02_candidates.json` |
| Idea Room | Visual Story Director | `actual_multi_agent` | `019ebda6-60c7-73a0-aa93-e983b78a19bb` | `.agents/skills/astory/personas/idea-room/visual-story-director.md` | Protect stageability, readable props, identity safety, and phone-screen composition. | 4 visually stageable candidates with clean slide arcs and production risks named. | Feeling without action, cramped poses, microtext, crowded faces, excessive locations, previous shortlist repeats. | `debates/idea_room/agent_03_candidates.json` |

## Gate Decision

- `DISCOVER_AND_ASSIGN_AGENTS`: `complete`
- Failure code if blocked: `not_applicable`
- Next state: `GENERATE_OR_REFINE_IDEAS`
