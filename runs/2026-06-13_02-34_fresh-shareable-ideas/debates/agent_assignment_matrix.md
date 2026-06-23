# Agent Assignment Matrix

Run: `2026-06-13_02-34_fresh-shareable-ideas`

Assignment timestamp: `2026-06-13T02:37:00+05:30`

## Tool Discovery

- `multi_agent_v1.spawn_agent` visible at first check: `false`
- `tool_search` used when not visible: `true`
- Final assignment mode: `actual_multi_agent`
- Limitation if fallback: `none`

## Assigned Rooms

| Room | Agent | Assignment Mode | Agent Id Or Local Label | Prompt Packet | Ownership | Success Criteria | Hard Rejects | Output Path |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Idea Room | Relatability Ethnographer | `actual_multi_agent` | `019ebda8-baca-7d90-bdb2-61cc8bf9dfd0` (`Kierkegaard`) | `.agents/skills/astory/personas/idea-room/relatability-ethnographer.md` plus run brief | Find tiny true couple behaviors that can be staged without caption rescue. | Six non-generic ideas with everyday visual evidence, emotional truth, and warm mutuality. | `GENERIC_IDEA`; greeting-card sentiment; trope-first romance; one-sided fool/saint jokes. | `debates/idea_room/agent_01_candidates.json` |
| Idea Room | Shareability Strategist | `actual_multi_agent` | `019ebda8-bcdb-7791-a260-1114db627656` (`Schrodinger`) | `.agents/skills/astory/personas/idea-room/shareability-strategist.md` plus run brief | Find send-trigger ideas optimized for tagging, comments, and share behavior. | Six ideas with named hook, send reason, comment bait, and distribution risks. | Like-only ideas; influencer captions; mean call-outs; recycled meme templates. | `debates/idea_room/agent_02_candidates.json` |
| Idea Room | Visual Story Director | `actual_multi_agent` | `019ebda8-bdb2-7012-bc35-4471b69a092c` (`Bernoulli`) | `.agents/skills/astory/personas/idea-room/visual-story-director.md` plus run brief | Protect stageability, phone-screen readability, identity-safe framing, and visual freshness. | Six ideas with concrete slide arc, readable props/actions, and production risk notes. | Unstageable feelings; crowded face poses; microtext; anatomy traps; quote-card concepts. | `debates/idea_room/agent_03_candidates.json` |

## Scope Notes

- This run is currently stopped at the idea-room workflow. Story Room, Prompt QA Room, Review Room, Image QA Room, and final package assignments are intentionally not started until creator idea lock.
- Prior selected ideas to avoid: shared pocket system, can-we-leave language, helmet strap tax, still-mad-still-careful, reel side-eye, heart rent, promise-in-three, watch-my-videos banter, shawl-before-she-asks.
- Memory recall returned no cited findings for this query, so agents were instructed not to use uncited memory claims.

## Gate Decision

- `DISCOVER_AND_ASSIGN_AGENTS`: `complete`
- Failure code if blocked: `none`
- Next state: `GENERATE_OR_REFINE_IDEAS`
