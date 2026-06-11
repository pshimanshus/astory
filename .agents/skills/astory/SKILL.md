---
name: astory
description: Use when the user sends /astory, asks for an A Story of Two carousel, prompt, image, setup, resume, audit, idea generation, or Codex-native romantic watercolor-and-ink Instagram story production.
---

# A Story Agent

Run the Codex-native agentic creative-production system for `@a.storyof.two`.

## Operating Model

`/astory` is explicit permission to run the full multi-agent A Story workflow, including spawning specialist subagents when `multi_agent_v1` is available. The skill is the launcher; the product is the orchestrated creative system.

The repo-scoped source for this skill is `.agents/skills/astory/`. Do not treat a personal copy under `~/.codex/skills/astory/` as authoritative for this repository.

Non-negotiables:
- Use built-in Codex `imagegen` only for images.
- Do not ask for API keys, provider setup, npm commands, or a local app.
- Do not generate or accept final Aachu/Zuv artwork from text-only identity descriptions.
- Do not ask the creator to manually attach identity/style images that already exist in `references/`; resolve and load them from the repo.
- Do not mark a final image complete if faces drift, merge, over-beautify, or become generic.
- Do not assume a two-slide carousel. Slide count is story-led, usually 3-6 and up to 10 only when justified.
- Do not silently skip actual agent assignment. Before prompt lock or imagegen, prove `multi_agent_v1` availability was checked, assign agents when available, and record the assignment artifact.
- Pause for human approval at idea lock, story/slide-count lock, prompt lock, image QA, and final package.
- Record human approval evidence in the run's `docs/approvals.md` and `logs/trace.jsonl` before continuing past a HITL gate.
- Save artifacts into `/Users/himanshusharma/A Story of Two V2/runs/<run_id>/`.
- If a hard gate fails, mark the run `blocked`, not complete.

## Commands

- `/astory setup`: inspect V2 reference folders, confirm repo-scoped skill resources, write `docs/setup_status.md`, and mark ready or blocked.
- `/astory <idea>`: preserve the specific idea, improve angles, run idea-room debate, and pause for idea lock.
- `/astory theme: <theme>`: generate at least 10 ideas through the idea room.
- `/astory auto`: generate fresh high-engagement ideas from the brand rules.
- `/astory resume <run_id>`: inspect `logs/trace.jsonl`, continue from latest checkpoint, and preserve prior decisions.
- `/astory audit <run_id>`: audit required artifacts, unresolved failures, exports, evals, and portfolio completeness.

### `/astory setup` Contract

Setup must inspect and report:
- repo-scoped skill source at `.agents/skills/astory/`
- required skill resources: `SKILL.md`, `agents/openai.yaml`, personas, templates, references, house-style contract, imagegen contract, and failure taxonomy
- canonical prompt reference: `references/master-prompt.md`
- identity references in `references/identity/aachu/`, `references/identity/zuv/`, `references/identity/together/`, and `references/identity/current-request/`
- style references in `references/style/`
- text-style and brand rules
- stale dossier paths that still point to older external reference roots, with V2-local `references/...` remaps

Write the result to `docs/setup_status.md`. Mark setup `ready` only when the reference hard gate passes and final imagegen can proceed after selected local references are made visible to Codex. Otherwise mark setup `blocked` and name the blocking failure code.

## Project Paths

Workspace:
`/Users/himanshusharma/A Story of Two V2`

Reference roots:
- `references/identity/aachu/`
- `references/identity/zuv/`
- `references/identity/together/`
- `references/identity/current-request/`
- `references/style/`
- `references/text-style/`
- `references/brand/`
- `references/brain/`

Run root:
`runs/YYYY-MM-DD_HH-MM_slug/`

Run folders:
`input/`, `planning/`, `debates/`, `prompts/`, `references-used/`, `images/`, `exports/`, `evals/`, `logs/`, `docs/`

## Required Resources

Load only what is needed:
- Personas: `personas/<room>/*.md`
- Agent prompt packets: `templates/agents/*.md`
- Templates: `templates/**/*.json`, `templates/**/*.md`, `templates/**/*.txt`
- Style contract: `references/house-style-contract.md`
- Imagegen contract: `references/imagegen-contract.md`
- Master prompt: `references/master-prompt.md`
- Failure taxonomy: `references/failure-taxonomy.md`

## State Machine

Every run follows this state order:

1. `INIT_RUN`
2. `PARSE_CREATIVE_INPUT`
3. `DETERMINE_IDEA_MODE`
4. `REFERENCE_PREFLIGHT`
5. `MEMORY_RECALL_PREFLIGHT`
6. `DISCOVER_AND_ASSIGN_AGENTS`
7. `GENERATE_OR_REFINE_IDEAS`
8. `SCORE_IDEAS`
9. `SELECT_BEST_IDEA`
10. `HITL_IDEA_LOCK`
11. `GENERATE_STORY_CONCEPT`
12. `DECIDE_SLIDE_COUNT`
13. `GENERATE_SLIDE_BEATS`
14. `GENERATE_SCENE_OPTIONS`
15. `SELECT_AND_ORDER_SLIDES`
16. `HITL_STORY_LOCK`
17. `CREATE_CHARACTER_BIBLE`
18. `CREATE_STYLE_BIBLE`
19. `CREATE_PROMPT_PACK`
20. `PRE_GENERATION_EVAL`
21. `REVIEW_ROOM_QA`
22. `HITL_PROMPT_LOCK`
23. `LOAD_REFERENCE_IMAGES_IN_CONTEXT`
24. `REVIEW_ROOM_IMAGEGEN_BLOCKER_CHECK`
25. `GENERATE_IMAGES_WITH_IMAGEGEN`
26. `IMAGE_QUALITY_EVAL`
27. `REVIEW_ROOM_FINAL_BLOCKER_CHECK`
28. `RETRY_OR_REVISE_IF_NEEDED`
29. `FINAL_QA`
30. `EXPORT_AND_PACKAGE`
31. `WRITE_REPORTS`
32. `COMPLETE_OR_BLOCKED`

Append a JSON line to `logs/trace.jsonl` at every state using `templates/logs/trace_event.jsonl`. For every HITL state, also append the creator decision to `docs/approvals.md` using `templates/docs/approvals.md`.

## Brain Recall Gate

During `MEMORY_RECALL_PREFLIGHT`, build or refresh `references/brain/index/`,
run a recall query for the run's idea/theme/story context, and write
`planning/memory_recall.md` using `templates/planning/memory_recall.md`.

Rules:
- Use `python3 scripts/astory_brain_cli.py doctor --repo-root .` for memory
  setup QA. Do not treat active run blockers from `scripts/astory_repo_qa.py`
  as brain/setup blockers.
- Treat the doctor's runtime status and learning-pipeline status separately.
  If runtime is ready but learning is `operational_with_review_queue`, the
  memory system is operating correctly with governed review: low-risk claims can
  apply immediately, while high-risk identity/style/creator-preference claims
  must stay in the claim queue until reviewed.
- After a run has meaningful eval/approval evidence, run
  `python3 scripts/astory_brain_cli.py learn --repo-root . --run-id <run_id> --write`
  to create claim candidates and append ledger events.
- Do not use uncited memory claims in idea, story, prompt, image QA, or final-package artifacts.
- Memory recall may surface risks, past lessons, and gaps, but it cannot bypass HITL gates or visible-reference imagegen requirements.
- Treat `references/brain/index/` and `references/brain/reports/` as derived cache. If deleted, they must be rebuildable from canonical markdown and run artifacts.
- If recall results are weak, record the weakness and continue from current visible references and approvals rather than treating memory as truth.
- If brain lint fails, fix the brain page or mark the run blocked with the lint failure code before using the claim.

During `WRITE_REPORTS`, write `docs/retro.md` from `templates/docs/retro.md`.
List proposed updates to `references/brain/pages/*`, but do not silently modify
compiled brain pages unless the creator explicitly asks for memory writeback.
The learning pipeline may write claim candidates and ledger events, but it must
not silently promote high-risk claims into compiled brain pages.

## Agent Assignment Hard Gate

This gate exists because missing the real agent assignment weakens creative
quality and violates the `/astory` operating model.

During `DISCOVER_AND_ASSIGN_AGENTS`:

1. If `multi_agent_v1.spawn_agent` is visible, use it for the required rooms.
2. If it is not visible and `tool_search` is available, call `tool_search` for
   `multi-agent spawn agent` before deciding the tool is unavailable.
3. If `multi_agent_v1.spawn_agent` is still unavailable after discovery, run the
   same room personas as separate labeled local passes and state the limitation.
4. Write `debates/agent_assignment_matrix.md` before any idea-room output is
   treated as complete.
5. Use the matching prompt packet from `templates/agents/` when dispatching
   Story Room, Visual Scene Discussion, or Review Room agents. The packet must
   include run paths, source artifacts, reference rules, output artifacts,
   discussion protocol, and failure codes.
6. Append a `DISCOVER_AND_ASSIGN_AGENTS` trace event with `actual_multi_agent`,
   `fallback_local_passes`, or `blocked`.

`debates/agent_assignment_matrix.md` must include:

- tool discovery result and timestamp
- each room to be run
- agent/persona names
- actual subagent ids when spawned, or fallback local-pass labels
- ownership, success criteria, and hard rejects for each agent
- prompt packet/template path used for each assignment
- output paths produced by each agent

Hard block:

- Do not show `HITL_PROMPT_LOCK` unless `debates/agent_assignment_matrix.md`
  exists and the prompt-room outputs are recorded.
- Do not call imagegen unless `evals/pre_generation_eval.json` records
  `agent_assignment_status: "actual_multi_agent"` or
  `agent_assignment_status: "fallback_local_passes_with_limitation_recorded"`.
- If this proof is missing, stop and mark `AGENT_ASSIGNMENT_MISSING`.

## Multi-Agent Rooms

When `multi_agent_v1.spawn_agent` is available after the Agent Assignment Hard
Gate, spawn the room agents below. If the tool is unavailable after discovery,
run the same personas as separate, labeled passes and state the limitation in
the assignment matrix, evals, trace, approvals, and run report.

### Idea Room

Mandatory for every creative run.

Spawn:
- Relatability Ethnographer
- Shareability Strategist
- Visual Story Director

Protocol:
1. Each agent independently proposes candidates.
2. Merge and cluster duplicates.
3. Each agent critiques the other agents' strongest ideas.
4. Agents repair their best idea without losing emotional truth.
5. Score survivors on the full engagement rubric.
6. Select only if overall score is at least 4.0.
7. If no idea reaches 4.0, run a second room with "avoid first-round patterns".

Artifacts:
- `debates/idea_room/agent_01_candidates.json`
- `debates/idea_room/agent_02_candidates.json`
- `debates/idea_room/agent_03_candidates.json`
- `debates/idea_room/cross_critique.md`
- `debates/idea_room/repair_round.md`
- `debates/idea_room/final_scoreboard.json`
- `planning/idea_candidates.json`
- `planning/selected_idea.json`
- `planning/rejected_ideas.md`
- `evals/idea_engagement_eval.json`
- `evals/idea_engagement_report.md`

### Story Room

Run after idea lock.

Spawn:
- Story Director
- Pacing Editor
- Swipe Retention Critic

Outputs:
- `planning/story_concept.json`
- `planning/slide_count_decision.md`
- `planning/slide_beat_map.json`
- `planning/scene_options.json`
- `planning/selected_scenes.json`
- `debates/story_room/story_debate.md`

Dispatch:
- Use `templates/agents/story_room_agent_prompt.md` for Story Director,
  Pacing Editor, and Swipe Retention Critic.
- Use `templates/agents/visual_scene_discussion_prompt.md` for the visual
  treatment round that creates and scores scene alternatives.

Scene protocol:
1. Generate multiple viable visual treatments per slide before prompt writing.
2. For each slide, include at least 3 scene options unless the story logic makes alternatives impossible.
3. Score options on scene-text proof, identity preservation, visual freshness, phone-screen readability, wardrobe continuity, and style fit.
4. Select the scene that best proves the exact on-image text while keeping faces natural and reference-driven.
5. Save rejected scene reasons so future revisions can avoid repeating weak visual choices.

Pause at `HITL_STORY_LOCK` after selecting scenes. Show the story arc, chosen slide count, selected scenes, why fewer slides fail, why more slides dilute, risks, and artifact paths. Do not create character/style bibles until the creator approves or revises.

### Prompt QA Room

Run before imagegen.

Spawn:
- Identity Guardian
- Style Guardian
- Scene Logic Critic

Outputs:
- `debates/prompt_room/prompt_review.md`
- `debates/prompt_room/<agent_slug>_audit.md` for each assigned agent when the run needs targeted quality ownership
- `evals/pre_generation_eval.json`
- `evals/pre_generation_eval_report.md`

### Image QA Room

Run after imagegen candidates.

Spawn:
- Face Match Reviewer
- Style Fidelity Reviewer
- Publishing QA Reviewer

Outputs:
- `debates/image_qa_room/image_qa_debate.md`
- `evals/image_quality_eval.json`
- `evals/image_quality_report.md`

### Review Room

Run before prompt lock, before final imagegen, and again before final package.

Spawn:
- Artifact Review Guardian

Dispatch:
- Use `templates/agents/review_room_agent_prompt.md`.

Protocol:
1. Detect the run workflow type from local artifacts.
2. Run `scripts/prepare_imagegen_reference_context.py` when prompts are present and imagegen may happen.
3. Run `scripts/astory_repo_qa.py --run-id <run_id>`.
4. Review every blocker before moving forward.
5. Confirm `agent_assignment_gate` passes before prompt lock or imagegen.
6. If imagegen is next, load every `view_image_queue` path with `view_image` and write `evals/imagegen_reference_visibility_proof.json`.
7. Run `scripts/astory_repo_qa.py --run-id <run_id> --loop --max-iterations 2` after reference visibility proof is written and before imagegen.

Artifacts:
- `evals/repo_qa_review.json`
- `evals/repo_qa_review.md`
- `evals/repo_qa_review_loop.json`
- `evals/imagegen_reference_visibility_proof.json`

## Parallel Specialist Rule

For implementation, audit, repair, or QA work touching more than one subsystem, use multiple specialist agents where available: one for implementation, one for review, and one for tests/verification. If no multi-agent tool is available, run the same roles as separate labeled passes.

## HITL Gates

At each gate, show the creator the decision, risks, and artifact paths. Do not continue until approved or revised.
Record each decision in `docs/approvals.md` and append a matching trace event before moving to the next state.

- Reference setup gate: missing references block final imagegen.
- Idea lock gate: selected idea, score, why it wins, risks, rejected summary.
- Story/slide-count gate: story arc, chosen slide count, why fewer fails, why more dilutes.
- Prompt lock gate: slide-by-slide text, scene, prompt summary, agent assignment status, and prompt-room outputs.
- Review Room prompt gate: workflow type, repo QA status, every prompt file checked, blockers, and `agent_assignment_gate` result before `HITL_PROMPT_LOCK`.
- Reference visibility gate: selected reference manifest, load plan, every `view_image_queue` path viewed through `view_image`, and `evals/imagegen_reference_visibility_proof.json`.
- Image QA gate: pass/fail per slide, retries, hard failures.
- Review Room final package gate: final blockers, image QA status, accepted-final proof, reports, and unresolved risks before export/package completion.
- Final package gate: final assets, reports, unresolved risks.

## Reference Hard Gate

Minimum final-generation requirement:
- At least four curated Aachu close face anchors from `references/identity/aachu/face/`.
- At least four curated Zuv close face anchors from `references/identity/zuv/face/`.
- Prefer at least one together/couple reference.
- Style references or locked style rules are present.
- Text-style rules for baked-in handwritten typography are present.

Before final imagegen:
- Run `python3 scripts/prepare_imagegen_reference_context.py --run-id <run_id>` to create `references-used/selected_references.json` and `evals/imagegen_reference_load_plan.json`.
- Use `view_image` on every path in `view_image_queue`; the creator does not need to attach these images manually.
- Write `evals/imagegen_reference_visibility_proof.json` recording the loaded paths, timestamp, and prompt files covered.
- If any queued image cannot be read, stop and mark `IDENTITY_REFERENCE_MISSING`.
- If the active generation path cannot use the loaded image context, stop and mark `IDENTITY_REFERENCE_INPUT_UNPROVEN` instead of generating final Aachu/Zuv artwork.

## Imagegen Rules

Use the built-in image tool one slide at a time.

For each final slide:
- Generate native 4:5 for Instagram posts.
- Generate separate native 9:16 for Reels/Stories.
- Never resize, crop, pad, or extend one surface into another.
- Include exact on-image text baked into the illustration.
- Include tiny low-contrast handwritten `@a.storyof.two` bottom-right.
- Save project-bound outputs into the run folder.

Hard-reject:
- identity drift, face merge, missing references
- yellow/parchment paper
- missing, wrong, or unreadable on-image text
- missing brandmark
- generic AI watercolor, quote-card, poster, anime, photorealism
- bad anatomy or scene/text contradiction

Retry up to 2 times per failure type with targeted prompt repair, then mark blocked.

## Prompt Contract

Build prompts from `references/master-prompt.md` plus the locked slide beat. Treat the master prompt as the canonical prompt contract formerly covered by the separate prompt-only skill. Use exact-template mode: preserve the master prompt structure and wording, replace only the bracketed on-image text and scene fields, then append only the minimum slide-specific rendering details needed for clarity.

Use `references/house-style-contract.md` and `references/imagegen-contract.md` as QA contracts for prompt review and generation decisions. Every slide prompt must include:
- exact on-image text
- text placement and typography
- scene
- pose/body language
- wardrobe anchors
- props
- background
- emotion
- identity lock
- face preservation rules
- style lock
- paper tone rule
- brandmark rule
- anatomy rules
- negative constraints
- native aspect ratio
- reference image role statement

## Completion Rule

Only call a run complete when required artifacts exist, hard gates pass, final images are saved in `exports/`, `docs/approvals.md` documents the human approvals, and the run report documents approval status, eval scores, retries, failures, and limitations.
