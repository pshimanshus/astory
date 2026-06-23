# Agent Assignment Matrix

Run: `2026-06-15_19-09_plate-nervous`

## Tool Discovery

- `tool_search` query: `multi-agent spawn agent`
- Result: `multi_agent_v1.spawn_agent` discoverable in this session.
- Runtime constraint: the discovered tool says to use `spawn_agent` only when the user explicitly asks for sub-agents, delegation, or parallel agent work.
- Decision: local labeled passes for prompt QA and review, because the creator asked for an illustration using the A Story skill, not explicit delegation.

## Assignment

| Room | Agent / Persona | Mode | Ownership | Success Criteria | Hard Rejects | Prompt Packet |
| --- | --- | --- | --- | --- | --- | --- |
| Prompt QA | Identity Guardian / Priya | local_pass | Face-reference gate | Four Aachu and four Zuv raw identity anchors loaded and referenced as highest priority | text-only identity, face merge, generic couple | `.agents/skills/astory/templates/agents/visual_scene_discussion_prompt.md` and master prompt contract |
| Prompt QA | Style Guardian / Reza | local_pass | House style and palette | Neutral off-white paper, integrated handwriting, no yellow cast | parchment/yellow, quote-card, overlay typography | `.agents/skills/astory/references/house-style-contract.md` |
| Prompt QA | Scene Logic Critic / Samar | local_pass | Scene-text proof | Guarded plate and fake-distraction eyeline prove the line | generic eating scene, broken hands, unreadable prop | `.agents/skills/astory/templates/agents/visual_scene_discussion_prompt.md` |
| Review Room | Artifact Review Guardian / Vikram | local_pass | Imagegen gate | Reference load plan, visibility proof, prompt canvas/brandmark checks | missing proof, prompt-only identity | `.agents/skills/astory/templates/agents/review_room_agent_prompt.md` |

## Limitation

This is not `actual_multi_agent`; it is `fallback_local_passes_with_limitation_recorded` because the spawned-agent tool was discoverable but not invoked under its explicit-delegation runtime constraint.
