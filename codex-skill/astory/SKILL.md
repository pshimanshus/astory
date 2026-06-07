---
name: astory
description: Use when the user sends /astory, asks for an A Story of Two carousel, wants agentic idea generation, setup, resume, audit, image generation, or Codex-native romantic watercolor-and-ink Instagram story production.
---

# A Story Agent

Run the Codex-native agentic creative-production system for `@a.storyof.two`.

## Operating Model

`/astory` is explicit permission to run the full multi-agent A Story workflow, including spawning specialist subagents when `multi_agent_v1` is available. The skill is the launcher; the product is the orchestrated creative system.

Non-negotiables:
- Use built-in Codex `imagegen` only for images.
- Do not ask for API keys, provider setup, npm commands, or a local app.
- Do not generate or accept final Aachu/Zuv artwork from text-only identity descriptions.
- Do not mark a final image complete if faces drift, merge, over-beautify, or become generic.
- Do not assume a two-slide carousel. Slide count is story-led, usually 3-6 and up to 10 only when justified.
- Pause for human approval at idea lock, story/slide-count lock, prompt lock, image QA, and final package.
- Save artifacts into `/Users/himanshusharma/A Story of Two V2/runs/<run_id>/`.
- If a hard gate fails, mark the run `blocked`, not complete.

## Commands

- `/astory setup`: inspect V2 reference folders and write `docs/setup_status.md`.
- `/astory <idea>`: preserve the specific idea, improve angles, run idea-room debate, and pause for idea lock.
- `/astory theme: <theme>`: generate at least 10 ideas through the idea room.
- `/astory auto`: generate fresh high-engagement ideas from the brand rules.
- `/astory resume <run_id>`: inspect `logs/trace.jsonl`, continue from latest checkpoint, and preserve prior decisions.
- `/astory audit <run_id>`: audit required artifacts, unresolved failures, exports, evals, and portfolio completeness.

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

Run root:
`runs/YYYY-MM-DD_HH-MM_slug/`

Run folders:
`input/`, `planning/`, `debates/`, `prompts/`, `references-used/`, `images/`, `exports/`, `evals/`, `logs/`, `docs/`

## Required Resources

Load only what is needed:
- Personas: `personas/<room>/*.md`
- Templates: `templates/**/*.json`, `templates/**/*.md`, `templates/**/*.txt`
- Style contract: `references/house-style-contract.md`
- Imagegen contract: `references/imagegen-contract.md`
- Failure taxonomy: `references/failure-taxonomy.md`

## State Machine

Every run follows this state order:

1. `INIT_RUN`
2. `PARSE_CREATIVE_INPUT`
3. `DETERMINE_IDEA_MODE`
4. `REFERENCE_PREFLIGHT`
5. `GENERATE_OR_REFINE_IDEAS`
6. `SCORE_IDEAS`
7. `SELECT_BEST_IDEA`
8. `HITL_IDEA_LOCK`
9. `GENERATE_STORY_CONCEPT`
10. `DECIDE_SLIDE_COUNT`
11. `GENERATE_SLIDE_BEATS`
12. `SELECT_AND_ORDER_SLIDES`
13. `CREATE_CHARACTER_BIBLE`
14. `CREATE_STYLE_BIBLE`
15. `CREATE_PROMPT_PACK`
16. `PRE_GENERATION_EVAL`
17. `HITL_PROMPT_LOCK`
18. `LOAD_REFERENCE_IMAGES_IN_CONTEXT`
19. `GENERATE_IMAGES_WITH_IMAGEGEN`
20. `IMAGE_QUALITY_EVAL`
21. `RETRY_OR_REVISE_IF_NEEDED`
22. `FINAL_QA`
23. `EXPORT_AND_PACKAGE`
24. `WRITE_REPORTS`
25. `COMPLETE_OR_BLOCKED`

Append a JSON line to `logs/trace.jsonl` at every state using `templates/logs/trace_event.jsonl`.

## Multi-Agent Rooms

When `multi_agent_v1.spawn_agent` is available, spawn the room agents below. If the tool is unavailable, run the same personas as separate, labeled passes and state the limitation in the run report.

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
- `debates/story_room/story_debate.md`

### Prompt QA Room

Run before imagegen.

Spawn:
- Identity Guardian
- Style Guardian
- Scene Logic Critic

Outputs:
- `debates/prompt_room/prompt_review.md`
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

## HITL Gates

At each gate, show the creator the decision, risks, and artifact paths. Do not continue until approved or revised.

- Reference setup gate: missing references block final imagegen.
- Idea lock gate: selected idea, score, why it wins, risks, rejected summary.
- Story/slide-count gate: story arc, chosen slide count, why fewer fails, why more dilutes.
- Prompt lock gate: slide-by-slide text, scene, and prompt summary.
- Image QA gate: pass/fail per slide, retries, hard failures.
- Final package gate: final assets, reports, unresolved risks.

## Reference Hard Gate

Minimum final-generation requirement:
- At least one clear Aachu face reference.
- At least one clear Zuv face reference.
- Prefer at least one together/couple reference.
- Style references or locked style rules are present.
- Text-style rules for baked-in handwritten typography are present.

Before final imagegen, use `view_image` to make selected local identity/style references visible in context when needed. If references are not visible to the generation path, stop and mark `IDENTITY_REFERENCE_MISSING`.

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

Build prompts from `references/house-style-contract.md` plus the slide beat. Every slide prompt must include:
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

Only call a run complete when required artifacts exist, hard gates pass, final images are saved in `exports/`, and the run report documents human approvals, eval scores, retries, failures, and limitations.
