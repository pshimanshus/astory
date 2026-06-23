# Agent Assignment Matrix

Run: `2026-06-14_02-21_hard-to-love`

Assignment timestamp: `2026-06-14T10:54:08+05:30`

## Tool Discovery

- `multi_agent_v1.spawn_agent` visible at first check: `false`
- `tool_search` used when not visible: `true`
- `multi_agent_v1.spawn_agent` availability after discovery: `true`
- Initial assignment mode: `actual_multi_agent`
- Corrected final assignment mode for Idea Room: `fallback_local_passes_with_limitation_recorded`
- Limitation if fallback: closed-packet subagent rerun hit usage limit / shutdown before producing usable artifacts.

## Assignment History

- `2026-06-14T02:34:32+05:30`: initial Idea Room agents were spawned, but the dispatch used compressed persona prompts instead of the closed prompt packet.
- `2026-06-14T02:41:26+05:30`: creator/session correction recorded `IDEA_ROOM_PROMPT_PACKET_MISSING`; those outputs were copied into `debates/idea_room/superseded_ad_hoc_2026-06-14_02-41/` and must not be used as lock proof.
- `2026-06-14T10:54:08+05:30`: closed-packet subagent rerun attempted with `019ec2dc-c96c-7ca0-a88c-e399c3badc18`, `019ec2dd-a2ae-73a1-b429-3b8f248036c6`, and `019ec2de-ae39-7282-9ccf-68085fa4921c`; one errored on usage limit and two were shut down without usable artifacts.
- `2026-06-14T10:54:08+05:30`: closed-packet local fallback passes wrote the canonical Idea Room artifacts.
- `2026-06-14T11:19:00+05:30`: Story Director agent `019ec4aa-dc72-7e51-b098-9388aaf8cd7c` completed `debates/story_room/story_director_pass.md` using the closed Story Room prompt packet.
- `2026-06-14T11:20:00+05:30`: Pacing Editor agent `019ec4ab-b56f-7f61-8767-981ad8cd3f3c` completed `debates/story_room/pacing_editor_pass.md` using the closed Story Room prompt packet.
- `2026-06-14T11:29:00+05:30`: Swipe Retention Critic agent `019ec4b1-ec65-70f2-8a58-2afde4966538` completed `debates/story_room/swipe_retention_pass.md` using the closed Story Room prompt packet.
- `2026-06-14T11:31:55+05:30`: Visual Scene Discussion was completed as a local orchestrator pass using `templates/agents/visual_scene_discussion_prompt.md` requirements, because canonical scene selection needed to integrate the three returned Story Room passes into shared artifacts.

## Assigned Rooms

| Room | Agent | Assignment Mode | Agent Id Or Local Label | Prompt Packet | Ownership | Success Criteria | Hard Rejects | Output Path |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Idea Room | Relatability Ethnographer | `fallback_local_passes_with_limitation_recorded` | `local-pass-idea-01-meera-closed-packet` | `templates/agents/idea_room_agent_prompt.md` | Find the behavior-level truth under the hard-to-love concept. | 3-5 specific candidates with evidence ledger, premise lock, slide arc, scene-landing seed, and persona-specific scores. | `GENERIC_IDEA`, sentiment without behavior, forced two-person slide logic. | `debates/idea_room/agent_01_candidates.json` |
| Idea Room | Shareability Strategist | `fallback_local_passes_with_limitation_recorded` | `local-pass-idea-02-kabir-closed-packet` | `templates/agents/idea_room_agent_prompt.md` | Find the send/comment trigger. | 3-5 candidates with named tag reason, 3-second hook, evidence ledger, and scene-landing seed. | influencer-caption energy, recycled meme energy, mean call-out. | `debates/idea_room/agent_02_candidates.json` |
| Idea Room | Visual Story Director | `fallback_local_passes_with_limitation_recorded` | `local-pass-idea-03-tara-closed-packet` | `templates/agents/idea_room_agent_prompt.md` | Make the concept stageable without identity drift or forced crowding. | 3-5 visual candidates with slide arc, first moment, payoff, feasibility risks, and scene-landing seed. | cramped faces, stale close-angle defaults, microtext, impossible body logic. | `debates/idea_room/agent_03_candidates.json` |
| Story Room | Story Director | `actual_multi_agent_closed_packet` | `019ec4aa-dc72-7e51-b098-9388aaf8cd7c` | `templates/agents/story_room_agent_prompt.md` | Turn locked idea into story spine. | Story concept honors approved idea and creator direction notes. | generic reassurance arc, ignoring no-forced-both constraint. | `debates/story_room/story_director_pass.md; planning/story_concept.json` |
| Story Room | Pacing Editor | `actual_multi_agent_closed_packet` | `019ec4ab-b56f-7f61-8767-981ad8cd3f3c` | `templates/agents/story_room_agent_prompt.md` | Choose slide count and pacing. | Slide count has clear fewer/more rationale. | too many slides, thin payoff, repeated staging. | `debates/story_room/pacing_editor_pass.md; planning/slide_count_decision.md` |
| Story Room | Swipe Retention Critic | `actual_multi_agent_closed_packet` | `019ec4b1-ec65-70f2-8a58-2afde4966538` | `templates/agents/story_room_agent_prompt.md` | Protect swipe tension. | Each slide creates a reason to continue. | no payoff, obvious repetition, quote-card pacing. | `debates/story_room/swipe_retention_pass.md; planning/slide_beat_map.json` |
| Story Room | Visual Scene Discussion | `local_orchestrator_closed_packet_requirements` | `local-pass-story-visual-scene-discussion` | `templates/agents/visual_scene_discussion_prompt.md` | Generate and score scene options. | At least 3 viable scene options per slide unless impossible. | `VISUAL_SETTING_CONTRADICTION`, `SCENE_LOGIC_CONTRADICTION`. | `planning/scene_options.json; planning/selected_scenes.json` |
| Prompt QA Room | Identity Guardian | `pending_after_story_lock` | `pending` | `.agents/skills/astory/personas/prompt-room/identity-guardian.md` | Protect Aachu/Zuv likeness. | Prompt pack prioritizes raw face anchors and avoids role reversal. | `IDENTITY_REFERENCE_INPUT_UNPROVEN`, `IDENTITY_DRIFT`, `FACE_MERGE`. | `debates/prompt_room/identity_guardian_audit.md` |
| Prompt QA Room | Style Guardian | `pending_after_story_lock` | `pending` | `.agents/skills/astory/personas/prompt-room/style-guardian.md` | Protect house style. | Prompts use best-illustration style without copying concept or turning yellow. | `STYLE_DRIFT`, `YELLOW_PAPER_CAST`, `PROMPT_PALETTE_CONFLICT`. | `debates/prompt_room/style_guardian_audit.md` |
| Prompt QA Room | Scene Logic Critic | `pending_after_story_lock` | `pending` | `.agents/skills/astory/personas/prompt-room/scene-logic-critic.md` | Protect physical/emotional logic. | Every scene proves its exact text with believable props, hands, bodies, and eyelines. | `SCENE_LOGIC_CONTRADICTION`, `ANATOMY_FAILURE`. | `debates/prompt_room/scene_logic_critic_audit.md` |
| Review Room | Artifact Review Guardian | `pending_before_prompt_lock` | `pending` | `templates/agents/review_room_agent_prompt.md` | Audit real artifacts and block missing gates. | Repo QA, reference manifest, prompt canvas, and assignment gates checked. | stale proof, prompt-only identity, skipped HITL. | `evals/repo_qa_review.json; evals/repo_qa_review_loop.json` |
| Image QA Room | Face Match Reviewer | `pending_after_imagegen` | `pending` | `.agents/skills/astory/personas/image-qa-room/face-match-reviewer.md` | Judge rendered Aachu/Zuv likeness. | Accept only specific non-generic faces. | `IDENTITY_DRIFT`, `FACE_MERGE`, over-beautified faces. | `debates/image_qa_room/face_match_audit.md` |
| Image QA Room | Style Fidelity Reviewer | `pending_after_imagegen` | `pending` | `.agents/skills/astory/personas/image-qa-room/style-fidelity-reviewer.md` | Judge house style and surface. | Native 1080x1080, off-white paper, no yellow/quote-card/poster drift. | `WRONG_CANVAS_SIZE`, `YELLOW_PAPER_CAST`, `STYLE_DRIFT`. | `debates/image_qa_room/style_fidelity_audit.md` |
| Image QA Room | Publishing QA Reviewer | `pending_after_imagegen` | `pending` | `.agents/skills/astory/personas/image-qa-room/publishing-qa-reviewer.md` | Judge publish readiness. | Exact text, brandmark, no obvious artifact failures. | `TEXT_NOT_EXACT`, `TEXT_UNREADABLE`, `BRANDMARK_MISSING`. | `debates/image_qa_room/publishing_qa_audit.md` |

## Gate Decision

- `DISCOVER_AND_ASSIGN_AGENTS`: `complete_with_recorded_limitation`
- Failure code if blocked: `none`
- Recorded limitation: `IDEA_ROOM_PROMPT_PACKET_MISSING` invalidated the first pass; usage limit blocked closed-packet subagent rerun; closed-packet local fallback was used.
- Story Room assignment status: `actual_multi_agent_closed_packet_plus_local_visual_scene_merge`
- Next state: `HITL_STORY_LOCK`
