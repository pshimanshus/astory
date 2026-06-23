# Agent Assignment Matrix

Run: `{{run_id}}`

Assignment timestamp: `{{timestamp}}`

## Tool Discovery

- `multi_agent_v1.spawn_agent` visible at first check: `true|false`
- `tool_search` used when not visible: `true|false|not_available`
- Final assignment mode: `actual_multi_agent|fallback_local_passes|blocked`
- Limitation if fallback: `{{limitation}}`

## Assigned Rooms

| Room | Agent | Assignment Mode | Agent Id Or Local Label | Prompt Packet | Ownership | Success Criteria | Hard Rejects | Output Path |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Idea Room | Relatability Ethnographer | `{{mode}}` | `{{id_or_label}}` | `templates/agents/idea_room_agent_prompt.md` | `{{ownership}}` | `{{success_criteria}}` | `{{hard_rejects}}` | `{{output_path}}` |
| Idea Room | Shareability Strategist | `{{mode}}` | `{{id_or_label}}` | `templates/agents/idea_room_agent_prompt.md` | `{{ownership}}` | `{{success_criteria}}` | `{{hard_rejects}}` | `{{output_path}}` |
| Idea Room | Visual Story Director | `{{mode}}` | `{{id_or_label}}` | `templates/agents/idea_room_agent_prompt.md` | `{{ownership}}` | `{{success_criteria}}` | `{{hard_rejects}}` | `{{output_path}}` |
| Story Room | Story Director | `{{mode}}` | `{{id_or_label}}` | `templates/agents/story_room_agent_prompt.md` | `{{ownership}}` | `{{success_criteria}}` | `{{hard_rejects}}` | `{{output_path}}` |
| Story Room | Pacing Editor | `{{mode}}` | `{{id_or_label}}` | `templates/agents/story_room_agent_prompt.md` | `{{ownership}}` | `{{success_criteria}}` | `{{hard_rejects}}` | `{{output_path}}` |
| Story Room | Swipe Retention Critic | `{{mode}}` | `{{id_or_label}}` | `templates/agents/story_room_agent_prompt.md` | `{{ownership}}` | `{{success_criteria}}` | `{{hard_rejects}}` | `{{output_path}}` |
| Story Room | Visual Scene Discussion | `{{mode}}` | `{{id_or_label}}` | `templates/agents/visual_scene_discussion_prompt.md` | `{{ownership}}` | `{{success_criteria}}` | `{{hard_rejects}}` | `planning/scene_options.json; planning/selected_scenes.json` |
| Prompt QA Room | Identity Guardian | `{{mode}}` | `{{id_or_label}}` | `{{prompt_packet_or_persona}}` | `{{ownership}}` | `{{success_criteria}}` | `{{hard_rejects}}` | `{{output_path}}` |
| Prompt QA Room | Style Guardian | `{{mode}}` | `{{id_or_label}}` | `{{prompt_packet_or_persona}}` | `{{ownership}}` | `{{success_criteria}}` | `{{hard_rejects}}` | `{{output_path}}` |
| Prompt QA Room | Scene Logic Critic | `{{mode}}` | `{{id_or_label}}` | `{{prompt_packet_or_persona}}` | `{{ownership}}` | `{{success_criteria}}` | `{{hard_rejects}}` | `{{output_path}}` |
| Review Room | Artifact Review Guardian | `{{mode}}` | `{{id_or_label}}` | `templates/agents/review_room_agent_prompt.md` | `{{ownership}}` | `{{success_criteria}}` | `{{hard_rejects}}` | `evals/repo_qa_review.json; evals/repo_qa_review_loop.json` |
| Image QA Room | Face Match Reviewer | `{{mode}}` | `{{id_or_label}}` | `{{prompt_packet_or_persona}}` | `{{ownership}}` | `{{success_criteria}}` | `{{hard_rejects}}` | `{{output_path}}` |
| Image QA Room | Style Fidelity Reviewer | `{{mode}}` | `{{id_or_label}}` | `{{prompt_packet_or_persona}}` | `{{ownership}}` | `{{success_criteria}}` | `{{hard_rejects}}` | `{{output_path}}` |
| Image QA Room | Publishing QA Reviewer | `{{mode}}` | `{{id_or_label}}` | `{{prompt_packet_or_persona}}` | `{{ownership}}` | `{{success_criteria}}` | `{{hard_rejects}}` | `{{output_path}}` |

## Gate Decision

- `DISCOVER_AND_ASSIGN_AGENTS`: `complete|blocked`
- Failure code if blocked: `AGENT_ASSIGNMENT_MISSING|{{other_failure_code}}`
- Next state: `{{next_state}}`
