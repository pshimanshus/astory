# Agent Assignment Matrix

Run: `2026-06-14_17-51_ig-reference-concept`
Timestamp: `2026-06-14T12:24:53Z`

## Tool Discovery

`tool_search` for `multi-agent spawn agent` found `multi_agent_v1.spawn_agent`.

Assignment status: `actual_multi_agent`

## Room Assignments

| Room | Agent | Persona | Subagent ID | Nickname | Ownership | Success Criteria | Hard Rejects | Prompt Packet |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Idea Room | Relatability Ethnographer | `.agents/skills/astory/personas/idea-room/relatability-ethnographer.md` | `019ec619-38dd-74d0-85b7-1c43f4449216` | Schrodinger | Tiny true couple behavior and anti-generic specificity | 3-5 behavior-led candidates with visible proof, sendable recognition, and a top pick | Sentiment-only ideas, greeting-card romance, one-partner-as-fool jokes, stale tropes | `.agents/skills/astory/templates/agents/idea_room_agent_prompt.md` |
| Idea Room | Shareability Strategist | `.agents/skills/astory/personas/idea-room/shareability-strategist.md` | `019ec619-3996-7120-96ff-eda9cf9c2c1c` | Planck | Hook, send trigger, tag/comment reason | 3-5 candidates scored for shareability, hook strength, simplicity, freshness, and brand fit | Like-only ideas, vague shareability, influencer-caption energy, mean call-outs | `.agents/skills/astory/templates/agents/idea_room_agent_prompt.md` |
| Idea Room | Visual Story Director | `.agents/skills/astory/personas/idea-room/visual-story-director.md` | `019ec619-3a24-7e83-9da4-7ce8352d6c13` | Aristotle | Stageable visual proof, scene feasibility, slide-count hints | 3-5 candidates with first-frame visual, payoff frame, prop logic, and imagegen feasibility risks | Mood-only visuals, cramped two-face staging, microtext, impossible body logic, copied reference style | `.agents/skills/astory/templates/agents/idea_room_agent_prompt.md` |
| Story Room | Story Director | `.agents/skills/astory/personas/story-room/story-director.md` | `019ec626-c2e1-7501-a386-d21b3184bfa5` | Einstein | Story spine and emotional arc | Exact slide content with setup, escalation, payoff, and no repeated beat | Quote-card ending, narration doing image work, mean payoff, generic sweetness | `.agents/skills/astory/templates/agents/story_room_agent_prompt.md` |
| Story Room | Pacing Editor | `.agents/skills/astory/personas/story-room/pacing-editor.md` | `019ec626-c38e-7301-b9b9-66005e7ef1ce` | Maxwell | Slide count and economy | Defensible slide count, cut/keep verdicts, every slide earns place | Default two-slide reflex, padded bloat, filler slide | `.agents/skills/astory/templates/agents/story_room_agent_prompt.md` |
| Story Room | Swipe Retention Critic | `.agents/skills/astory/personas/story-room/swipe-retention-critic.md` | `019ec626-c442-7cc2-8b57-a7eb2c89e7c5` | Dirac | Swipe reason and retention leaks | Slide-by-slide swipe reason, hook/payoff recommendations, rewrite flags | Repeated beats, explained visuals, payoff too early, generic last slide | `.agents/skills/astory/templates/agents/story_room_agent_prompt.md` |

## Source Artifacts Given To Agents

- `runs/2026-06-14_17-51_ig-reference-concept/input/creative_brief.json`
- `runs/2026-06-14_17-51_ig-reference-concept/input/reference_analysis.md`
- `runs/2026-06-14_17-51_ig-reference-concept/planning/memory_recall.md`
- `references/brain/pages/outcome-attribution.md`
- `references/brain/pages/run-lessons.md`
- `.agents/skills/astory/references/house-style-contract.md`
- `.agents/skills/astory/references/failure-taxonomy.md`

## Output Paths

The coordinator will persist returned agent JSON into:

- `runs/2026-06-14_17-51_ig-reference-concept/debates/idea_room/agent_01_candidates.json`
- `runs/2026-06-14_17-51_ig-reference-concept/debates/idea_room/agent_02_candidates.json`
- `runs/2026-06-14_17-51_ig-reference-concept/debates/idea_room/agent_03_candidates.json`

Then the coordinator will write:

- `runs/2026-06-14_17-51_ig-reference-concept/debates/idea_room/cross_critique.md`
- `runs/2026-06-14_17-51_ig-reference-concept/debates/idea_room/repair_round.md`
- `runs/2026-06-14_17-51_ig-reference-concept/debates/idea_room/final_scoreboard.json`
- `runs/2026-06-14_17-51_ig-reference-concept/planning/idea_candidates.json`
- `runs/2026-06-14_17-51_ig-reference-concept/planning/selected_idea.json`
- `runs/2026-06-14_17-51_ig-reference-concept/planning/scene_landing_preview.md`
- `runs/2026-06-14_17-51_ig-reference-concept/planning/rejected_ideas.md`
- `runs/2026-06-14_17-51_ig-reference-concept/evals/idea_engagement_eval.json`
- `runs/2026-06-14_17-51_ig-reference-concept/evals/idea_engagement_report.md`

Story Room will produce:

- `runs/2026-06-14_17-51_ig-reference-concept/planning/story_concept.json`
- `runs/2026-06-14_17-51_ig-reference-concept/planning/slide_count_decision.md`
- `runs/2026-06-14_17-51_ig-reference-concept/planning/slide_beat_map.json`
- `runs/2026-06-14_17-51_ig-reference-concept/planning/scene_options.json`
- `runs/2026-06-14_17-51_ig-reference-concept/planning/selected_scenes.json`
- `runs/2026-06-14_17-51_ig-reference-concept/debates/story_room/story_debate.md`

## Limitation Notes

Subagents were instructed to return valid JSON rather than edit the main workspace directly. This keeps the run artifacts in the coordinator-owned workspace and avoids cross-worktree artifact drift.
