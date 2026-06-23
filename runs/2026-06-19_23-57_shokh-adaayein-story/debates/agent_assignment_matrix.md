## Agent Assignment Matrix

Tool discovery result: `multi_agent_v1.spawn_agent` is available after
`tool_search` for `multi-agent spawn agent`.

Execution choice: local fallback passes. The active tool rule says not to spawn
subagents unless the user explicitly asks for subagents, delegation, or parallel
agent work. The creator asked to create the images directly, so this run does
not spawn external agents.

| Room | Local Pass | Owner | Success Criteria | Hard Rejects |
| --- | --- | --- | --- | --- |
| Prompt Room | Identity Guardian | Face identity | Aachu and Zuv remain the same people across all slides | Generic faces, role reversal, over-beautified drift |
| Prompt Room | Style Guardian | House style | Premium watercolor-and-ink, neutral off-white paper, not quote-card | Yellow/parchment cast, generic AI watercolor, poster layout |
| Prompt Room | Scene Logic Critic | Scene proof | Each scene proves the two-line caption through gesture, eyeline, and prop logic | Visual mood without action, impossible hand/body logic |
| Image QA Room | Face Match Reviewer | Image acceptance | Faces stay close to loaded anchors | Face merge, drift, new ethnicity/age |
| Image QA Room | Publishing QA Reviewer | Story readiness | Story canvas, readable text, top brandmark | Missing brandmark, wrong or unreadable text |

Limitation recorded: local passes do not provide independent subagent outputs,
but they preserve the same prompt and QA responsibilities for this direct run.
