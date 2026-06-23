# Agent Assignment Matrix

Run: `2026-06-15_23-25_silence-house-walks`

Tool discovery result: `multi_agent_v1.spawn_agent` available after `tool_search` query `multi-agent spawn agent`.

Timestamp: `2026-06-15T23:31:00+05:30`

Workflow note: creator explicitly requested no concept thinking, so no Idea Room invention was assigned. Actual multi-agent assignment is scoped to production QA before imagegen.

| Room | Agent / Persona | Subagent ID | Ownership | Success Criteria | Hard Rejects | Prompt Packet / Inputs | Output Path |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Prompt QA Room | Identity Guardian / Priya | `019ecc74-4209-7f41-9190-9c2e7056a9d1` | Face-anchor and identity safety | Loaded raw Aachu and Zuv references are role-separated, sufficient, and explicitly prioritized in prompt. | text-only identity, face merge, role reversal, missing anchors | Persona: `.agents/skills/astory/personas/prompt-room/identity-guardian.md`; prompt: `prompts/slide_01_prompt.txt`; contracts and load plan | `debates/prompt_room/identity_guardian_audit.md` |
| Prompt QA Room | Style Guardian / Reza | `019ecc74-50ad-7a10-b5cf-abd1ae26763e` | House style, paper, typography, brandmark | Prompt preserves premium watercolor-and-ink, neutral off-white paper, integrated text, and top-right brandmark. | yellow/parchment cast, poster/quote-card, overlay text, missing brandmark | Persona: `.agents/skills/astory/personas/prompt-room/style-guardian.md`; prompt: `prompts/slide_01_prompt.txt`; style contracts and brand/text rules | `debates/prompt_room/style_guardian_audit.md` |
| Prompt QA Room | Scene Logic Critic / Samar | `019ecc74-5984-7953-826d-819c57664c40` | Scene-text proof and physical believability | The image should read as a cautious home after silence even with text covered. | generic sad couple, mood-only staging, contradictions, cramped anatomy | Persona: `.agents/skills/astory/personas/prompt-room/scene-logic-critic.md`; selected scene, scene options, prompt, failure taxonomy | `debates/prompt_room/scene_logic_critic_audit.md` |

Assignment status: `actual_multi_agent`

Limitation: no concept/idea agents were spawned because the creator explicitly locked the concept and asked to skip concept thinking.
