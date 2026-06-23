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
- Before any written creative artifact, storyboard, caption, on-image text,
  prompt, visual suggestion, or creative thought, use
  `anti-ai-slop-human-copy-filter`. Its Viral Research Layer is the default
  first layer for jams and recommendations, not an optional add-on.
- When a compatible permissioned source winner exists in
  `references/text-style/winner-bank/`, do not default to fresh invention.
  Build a source-preserving remix: preserve the allowed copy/premise/caption/
  structure, then add the A Story wrapper through Aachu/Zuv scene, conversation,
  daily-life behavior, or final-slide payoff.
- Treat `AI_SLOP_COPY_DRIFT` as a hard creative failure: if copy or visual
  direction becomes preachy, generic, therapy-page, quote-card, platform-blind,
  or moved away from the creator's original setup, stop and repair before
  continuing.
- Use built-in Codex `imagegen` only for images.
- Do not ask for API keys, provider setup, npm commands, or a local app.
- Do not generate or accept final Aachu/Zuv artwork from text-only identity descriptions.
- Do not ask the creator to manually attach identity/style images that already exist in `references/`; resolve and load them from the repo.
- Do not write or send an imagegen prompt unless it explicitly requests native `1080x1350 px` output.
- Do not write or send an A Story imagegen prompt that leaves the locked
  on-image text blank, plans to add text later, or omits the exact text from
  generation. Missing generated text is a hard failure, not a production detail.
- Do not mark a final image complete if faces drift, merge, over-beautify, or become generic.
- Do not mark a final image complete if the `@a.storyof.two` brandmark is missing.
- Do not assume a two-slide carousel. Slide count is story-led, usually 3-6 and up to 10 only when justified.
- Do not ask for idea lock from concept, score, or rationale alone. Before `HITL_IDEA_LOCK`, write a scene-landing preview that makes the creator feel the first frame, swipe tension, payoff frame, and share trigger.
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
- identity references in `references/identity/aachu/`, `references/identity/zuv/`, and `references/identity/together/`
- style references in `references/style/best-illustration/`
- failure examples to avoid in `references/failures/visual-inconsistencies/`
- text-style and brand rules
- current-request images come from the active run's `input/` folder, not a curated reference root

Write the result to `docs/setup_status.md`. Mark setup `ready` only when the reference hard gate passes and final imagegen can proceed after selected local references are made visible to Codex. Otherwise mark setup `blocked` and name the blocking failure code.

## Project Paths

Workspace:
`/Users/himanshusharma/A Story of Two V2`

Reference roots:
- `references/identity/aachu/`
- `references/identity/zuv/`
- `references/identity/together/`
- `references/style/best-illustration/`
- `references/failures/visual-inconsistencies/`
- `references/text-style/`
- `references/text-style/winner-bank/`
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
- Winner bank when the brief can be grounded in a proven source:
  `references/text-style/winner-bank/winner_bank.json`,
  `references/text-style/winner-bank/posts_merged.json`,
  `references/text-style/winner-bank/chunk_results.json`,
  `references/text-style/winner-bank/winner_contact_sheet.jpg`, and
  `references/text-style/winner-bank-index-2026-06-14.json`
- Winner modeling lens for source-preserving remixes:
  `references/text-style/illusion-of-novelty-storytelling-2026-06-18.md`

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
10. `CREATE_SCENE_LANDING_PREVIEW`
11. `HITL_IDEA_LOCK`
12. `GENERATE_STORY_CONCEPT`
13. `DECIDE_SLIDE_COUNT`
14. `GENERATE_SLIDE_BEATS`
15. `GENERATE_SCENE_OPTIONS`
16. `SELECT_AND_ORDER_SLIDES`
17. `HITL_STORY_LOCK`
18. `CREATE_CHARACTER_BIBLE`
19. `CREATE_STYLE_BIBLE`
20. `CREATE_PROMPT_PACK`
21. `PRE_GENERATION_EVAL`
22. `REVIEW_ROOM_QA`
23. `HITL_PROMPT_LOCK`
24. `LOAD_REFERENCE_IMAGES_IN_CONTEXT`
25. `REVIEW_ROOM_IMAGEGEN_BLOCKER_CHECK`
26. `GENERATE_IMAGES_WITH_IMAGEGEN`
27. `IMAGE_QUALITY_EVAL`
28. `REVIEW_ROOM_FINAL_BLOCKER_CHECK`
29. `RETRY_OR_REVISE_IF_NEEDED`
30. `FINAL_QA`
31. `EXPORT_AND_PACKAGE`
32. `WRITE_REPORTS`
33. `COMPLETE_OR_BLOCKED`

Append a JSON line to `logs/trace.jsonl` at every state using `templates/logs/trace_event.jsonl`. For every HITL state, also append the creator decision to `docs/approvals.md` using `templates/docs/approvals.md`.

## Source Winner Remix Loop

This loop exists because the creator's winning A Story posts often come from
source-preserving remixes, not from abstract fresh ideation. The bank is a
working stock page, not a theoretical moodboard.

Default behavior:
- During `GENERATE_OR_REFINE_IDEAS`, search the winner bank for compatible
  posts before inventing new premises.
- Every serious candidate must name a source winner unless the creator asked
  for a fresh original or the bank has no compatible winner.
- During `SCORE_IDEAS`, write `planning/novelty_candidate_ledger.json` before
  choosing the winner. The ledger records each serious candidate's source
  engine, old familiar topic, new reveal, viewer outcome, bullseye proof, A
  Story wrappers, selection scores, and anti-slop risk. It is the selection
  function, not a post-hoc explanation.
- During `SELECT_BEST_IDEA`, write
  `planning/source_winner_remix_contract.json` before idea lock. This contract
  records source URL, account, metrics, exact copy/premise/caption/slide
  structure allowed to stay, what changes, A Story wrapper, added payoff, and
  what must not be polished away.
- During `CREATE_SCENE_LANDING_PREVIEW`, write
  `planning/source_winner_novelty_model.json` and
  `planning/winner_landing_comparison.md`. Compare the proposed A Story landing
  against the source winner. The novelty model must explain the source winner's
  new reveal, viewer outcome, contrast frame, real/skipped urgency, bullseye
  proof, and what must not be explained away before writing the A Story landing.
  The landing comparison then checks first-frame stop, swipe reason, emotional
  turn, comment/send trigger, caption move, and final-slide payoff.
- Hook mechanics are diagnostic only. Do not create a rigid hook gate or block a
  source-winner remix because it fails to match a formula. The higher-priority
  question is why the winner worked and what novelty made an old feeling feel
  new. Use delay/confusion/relevance/curiosity language only when it helps
  protect or repair that engine.
- During `PRE_GENERATION_EVAL`, write
  `evals/source_winner_alignment_eval.json`. Block if the copy/story has moved
  away from the permissioned source winner without a creator-approved reason.
- During `IMAGE_QUALITY_EVAL`, write
  `evals/source_winner_image_alignment.json`. Block if the images decorate the
  source instead of turning it into a readable couple moment.
- During `FINAL_QA`, write `evals/final_winner_landing_check.json`. Do not
  package if the final generation no longer lands like the winning post.

Hard reject:
- turning a source winner into a vague lesson or "mechanic";
- replacing permissioned source copy with smoother AI wording;
- adding Aachu/Zuv beside a quote without a lived scene wrapper;
- rendering exact source copy as a quote-card, poster, typography card,
  deterministic text layout, or decorative design theme instead of a real
  Aachu/Zuv watercolor-and-ink illustration with scene logic;
- generating an illustration plate without the exact locked text baked into the
  generated image, unless the creator explicitly requested a non-final layout
  proof;
- approving a pretty final that does not preserve the source winner's send/save
  reason.

## Session Learning Capture Gate

This gate is for the main coordinator, not only dispatched agents. If the
creator corrects an assumption, tone, staging, process, or presentation during a
live session, capture that creator correction before continuing creative work.

Trigger phrases include but are not limited to:
- "not like that"
- "don't repeat this"
- "you are missing"
- "this should be"
- "why are you not"
- "remember this"
- "learning"
- "not landing"

Required hot-path action:
1. Stop generating new story, scene, prompt, or image content.
2. Write or update `planning/creator_direction_notes.md` with the correction,
   the rejected assumption, and the new active constraint.
3. Append a `SESSION_LEARNING_CAPTURE` JSONL event to `logs/trace.jsonl`.
4. If the correction changes workflow behavior, add a cited bullet to
   `references/brain/pages/run-lessons.md`.
5. Rebuild or refresh `references/brain/index/` before relying on recall.
6. Mention the updated artifact path to the creator, then continue from the
   corrected premise.

Do not rely on chat context to carry session learning. Do not wait until the end
of a run if the correction affects the next response.

## Anti-AI-Slop Copy Gate

Before any written creative artifact, storyboard, caption, on-image text,
prompt, visual suggestion, scene direction, or creative thought that shapes
copy, invoke `anti-ai-slop-human-copy-filter`.

This gate applies before Idea Room, Story Room, Visual Scene Discussion, Prompt
Room, creator-facing recommendations, and any direct answer that suggests copy
or visuals.

Required behavior:
- Run the filter's default-first Viral Research Layer before jamming or
  recommending copy, visuals, storyboards, prompts, captions, hooks, scenes, or
  creative direction.
- Use local performance memory first. If live/current platform research is
  needed and available, use it safely; if unavailable, record the evidence gap.
- Preserve the creator's original words/setup unless explicitly asked to create
  a new angle.
- Name the rejected generic version before proposing the human version.
- Make every line or scene carry a send/save/share/comment emotional job.
- If the output drifts into therapy-language, motivational lessons, quote-card
  romance, mood-only visual direction, or platform-blind correctness, mark
  `AI_SLOP_COPY_DRIFT` or the closest filter failure code and rewrite.

Artifacts that include creative copy should record the evidence basis, context
lock, emotional job, and rejected slop risk when useful. Do not bloat
creator-facing output with process notes unless the user asks for the audit.

## Brain Recall Gate

During `MEMORY_RECALL_PREFLIGHT`, build or refresh `references/brain/index/`,
run a recall query for the run's idea/theme/story context, and write
`planning/memory_recall.md` using `templates/planning/memory_recall.md`.

Rules:
- Use `python3 scripts/astory_brain_cli.py doctor --repo-root .` for memory
  setup QA. Do not treat active run blockers from `scripts/astory_repo_qa.py`
  as brain/setup blockers.
- If `planning/creator_direction_notes.md` exists, treat it as active run
  memory for story, scene, prompt, and QA work. Read it directly and cite it in
  the next room's evidence ledger; do not rely on chat context or generic
  memory recall to carry creator corrections.
- Do not run heavy memory learning, promotion, retrieval eval, or rollback
  loops before illustration generation. If an autopilot call is needed before
  imagegen, use `python3 scripts/astory_brain_cli.py autopilot --repo-root . --run-id <run_id> --phase pre_imagegen`;
  that phase must stay a lightweight no-op for learning and promotion.
- Treat the doctor's runtime status and learning-pipeline status separately.
  If runtime is ready but learning is `operational_with_review_queue`, the
  memory system is operating correctly with governed review: low-risk claims can
  apply immediately, while high-risk identity/style/creator-preference claims
  must stay in the claim queue until reviewed.
- Raw `runs/<run_id>/memory/claim_candidates.*` files are review queues, not
  production recall truth. Runtime recall may use `memory/active_claims.md` for
  auto-apply workflow memory and canonical `references/brain/pages/*` for
  promoted claims.
- After a run has meaningful eval/approval evidence, run
  `python3 scripts/astory_brain_cli.py learn --repo-root . --run-id <run_id> --write`
  to create claim candidates and append ledger events.
- Prefer the autonomous post-run loop:
  `python3 scripts/astory_brain_cli.py autopilot --repo-root . --run-id <run_id> --phase post_run`.
  It learns, applies the repo policy in
  `references/brain/policies/memory_autopilot.json`, promotes safe workflow
  lessons, defers high-risk identity/style/preference claims, quarantines
  rejected-asset claims, rebuilds the index, runs lint/eval, and rolls back any
  promotion that breaks verification.
- Do not use uncited memory claims in idea, story, prompt, image QA, or final-package artifacts.
- Memory recall may surface risks, past lessons, and gaps, but it cannot bypass HITL gates or visible-reference imagegen requirements.
- Treat `references/brain/index/` and `references/brain/reports/` as derived cache. If deleted, they must be rebuildable from canonical markdown and run artifacts.
- If recall results are weak, record the weakness and continue from current visible references and approvals rather than treating memory as truth.
- If brain lint fails, fix the brain page or mark the run blocked with the lint failure code before using the claim.

During `WRITE_REPORTS`, write `docs/retro.md` from `templates/docs/retro.md`.
Then run the memory autopilot post-run phase. The autopilot may modify compiled
brain pages only through policy-governed, cited, verified promotions. It must
not silently promote high-risk identity, style, or creator-preference claims
from a single run; those claims are auto-deferred unless policy and repeated
evidence justify promotion later.

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
   Idea Room, Story Room, Visual Scene Discussion, or Review Room agents. The packet must
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
- After a major creator visual correction, `fallback_local_passes_with_limitation_recorded`
  can only produce draft review artifacts. It cannot unlock imagegen until the
  corrected prompt/reference pack has fresh creator-visible approval and
  `evals/pre_imagegen_blocker_check.json` allows imagegen.
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

Dispatch:
- Use `templates/agents/idea_room_agent_prompt.md` for Relatability
  Ethnographer, Shareability Strategist, and Visual Story Director. Do not
  dispatch Idea Room agents with only a persona file, compressed role blurb, or
  bare JSON schema; that is a prompt-packet failure and the room must be rerun
  before idea lock.

Protocol:
1. Each agent independently proposes candidates.
2. Merge and cluster duplicates.
3. Each agent critiques the other agents' strongest ideas.
4. Agents repair their best idea without losing emotional truth.
5. Score survivors on the full engagement rubric.
6. Write `planning/novelty_candidate_ledger.json` so every shortlisted or
   selected candidate proves its source engine, novelty model, A Story wrapper,
   selection scores, and anti-slop risk before final selection.
7. Select only if overall score is at least 4.0 and the novelty candidate
   ledger gate can pass.
8. Before idea lock, create a scene-landing preview for the selected idea and strongest alternatives. The preview must make the idea feel like a carousel, not a pitch deck: first-frame visual, exact hook text, 3-5 slide mini arc, payoff frame, why someone sends it, and what would make it land flat.
9. For any permissioned source winner candidate, preserve the source winner's
   copy/premise/caption/slide engine in
   `planning/source_winner_remix_contract.json` before presenting it as the
   recommended idea.
10. If the selected idea's scene-landing preview or winner landing comparison
   does not land, repair the A Story wrapper or choose another source winner
   before `HITL_IDEA_LOCK`.
11. If no idea reaches 4.0, run a second room with "avoid first-round patterns".

Artifacts:
- `debates/idea_room/agent_01_candidates.json`
- `debates/idea_room/agent_02_candidates.json`
- `debates/idea_room/agent_03_candidates.json`
- `debates/idea_room/cross_critique.md`
- `debates/idea_room/repair_round.md`
- `debates/idea_room/final_scoreboard.json`
- `planning/idea_candidates.json`
- `planning/novelty_candidate_ledger.json`
- `planning/selected_idea.json`
- `planning/source_winner_remix_contract.json`
- `planning/source_winner_novelty_model.json`
- `planning/scene_landing_preview.md`
- `planning/winner_landing_comparison.md`
- `planning/rejected_ideas.md`
- `evals/idea_engagement_eval.json`
- `evals/idea_engagement_report.md`

Scene landing preview hard gate:
- Required before `HITL_IDEA_LOCK`.
- Must include the recommended idea and at least 2 alternatives unless fewer ideas scored above threshold.
- `planning/novelty_candidate_ledger.json` must exist before selected idea is
  presented as final. It must include at least one selected candidate and every
  selected or shortlisted candidate must have usable `source_engine`,
  `novelty_model`, `a_story_wrappers`, `selection_scores`, and `anti_slop_risk`
  evidence.
- For each previewed idea, include: exact first-slide on-image text, first-frame visual, swipe reason, 3-5 slide mini arc, payoff frame, share/comment trigger, flat/generic risk, and correction if it feels flat.
- If the idea comes from a permissioned source winner, include the source URL,
  source metric signal, what stays, what changes, and why the A Story wrapper
  still preserves the winning post's landing mechanism.
- If the idea comes from a permissioned source winner, write
  `planning/source_winner_novelty_model.json` before idea lock. It must model
  the chosen winner through `illusion-of-novelty-storytelling-2026-06-18.md`:
  old/familiar topic, new reveal, viewer outcome, contrast frame, real or
  skipped urgency, bullseye proof, what not to explain, and the A Story lived
  scene translation. Hook diagnostics may be noted, but they must stay
  subordinate to why the winner worked and what novelty the A Story version is
  preserving.
- Do not present a recommended idea as "final" if `planning/scene_landing_preview.md` is missing or if the preview is only title/score/rationale.
- Do not present a recommended idea as "final" if
  `planning/novelty_candidate_ledger.json` is missing or if the selected idea
  was not chosen through the ledger.
- Do not present a source-winner remix as "final" if
  `planning/source_winner_remix_contract.json`,
  `planning/source_winner_novelty_model.json`, or
  `planning/winner_landing_comparison.md` is missing.
- If this proof is missing or too abstract, stop and mark `SCENE_LANDING_MISSING`.

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

Before writing:
- Use `anti-ai-slop-human-copy-filter` before any story text, storyboard,
  caption, on-image text, visual suggestion, prompt handoff, or creative
  thought. Start with the filter's Viral Research Layer and record any
  evidence gap instead of freewriting from taste.
- Read `planning/source_winner_remix_contract.json` and
  `planning/source_winner_novelty_model.json` and
  `planning/winner_landing_comparison.md` when present. The story room may add
  lived Aachu/Zuv behavior, but it must not polish away the source winner's
  permissioned copy, premise, caption move, slide structure, novelty mechanism,
  or landing mechanism.
- Read `planning/creator_direction_notes.md` if present. Creator corrections in
  that file are hard story/scene constraints, not optional inspiration.
- Preserve any recorded "do not repeat" or "not like that" correction in the
  premise lock, slide beat contract, rejected scene memory, and story-lock risk
  notes.

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
6. Reject any scene whose visual setting, prop placement, body logic, eyeline, or physical environment does not make concrete sense for the locked beat; mark `VISUAL_SETTING_CONTRADICTION` or `SCENE_LOGIC_CONTRADICTION` instead of handing it to prompt writing.

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
- `evals/source_winner_alignment_eval.json`

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
- `evals/source_winner_image_alignment.json`

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
6. Confirm `gold_standard_identity_route_gate` passes before prompt lock or imagegen.
7. Confirm `prompt_canvas_size` passes before prompt lock or imagegen.
8. Confirm `prompt_brandmark_gate` passes before prompt lock or imagegen.
9. Confirm `planning/novelty_candidate_ledger.json` exists and passes repo QA
   before idea lock or selected-idea approval.
10. Confirm source-winner alignment artifacts exist when
   `planning/source_winner_remix_contract.json` exists.
11. Confirm `planning/source_winner_novelty_model.json` exists and passes repo
    QA when `planning/source_winner_remix_contract.json` exists.
12. If imagegen is next, load every `view_image_queue` path with `view_image` and write `evals/imagegen_reference_visibility_proof.json`.
13. Run `scripts/astory_repo_qa.py --run-id <run_id> --loop --max-iterations 2` after reference visibility proof is written and before imagegen.

Artifacts:
- `evals/repo_qa_review.json`
- `evals/repo_qa_review.md`
- `evals/repo_qa_review_loop.json`
- `evals/imagegen_reference_visibility_proof.json`
- `evals/pre_imagegen_blocker_check.json`
- `evals/final_winner_landing_check.json`

## Parallel Specialist Rule

For implementation, audit, repair, or QA work touching more than one subsystem, use multiple specialist agents where available: one for implementation, one for review, and one for tests/verification. If no multi-agent tool is available, run the same roles as separate labeled passes.

## HITL Gates

At each gate, show the creator the decision, risks, and artifact paths. Do not continue until approved or revised.
Record each decision in `docs/approvals.md` and append a matching trace event before moving to the next state.

- Reference setup gate: missing references block final imagegen.
- Idea lock gate: selected idea, novelty candidate ledger, score, why it wins,
  scene-landing preview, risks, rejected summary. Show the first-frame visual,
  exact hook text, mini slide arc, payoff frame, why it will be shared, what
  could make it feel flat/generic, and artifact paths.
- Source winner gate: for permissioned remixes, show
  `planning/source_winner_remix_contract.json` and
  `planning/source_winner_novelty_model.json` and
  `planning/winner_landing_comparison.md`, including what stays, what changes,
  the new reveal, viewer outcome, contrast frame, bullseye proof, the A Story
  wrapper, and the risk of weakening the source winner.
- Story/slide-count gate: story arc, chosen slide count, why fewer fails, why more dilutes.
- Prompt lock gate: slide-by-slide text, scene, prompt summary, agent assignment status, and prompt-room outputs.
- Review Room prompt gate: workflow type, repo QA status, every prompt file checked, blockers, and `agent_assignment_gate` result before `HITL_PROMPT_LOCK`.
- Reference visibility gate: selected reference manifest, load plan, every `view_image_queue` path viewed through `view_image`, and `evals/imagegen_reference_visibility_proof.json`.
- Pre-imagegen blocker gate: `evals/pre_imagegen_blocker_check.json` must pass emotional-state, identity-reference collision, fallback-review, creator-visible prompt-lock, and canvas expectation checks before imagegen.
- Gold Standard Identity Route gate: `gold_standard_identity_route_gate` must pass before imagegen or final package. If it fails, stop and record `GOLD_STANDARD_IDENTITY_ROUTE_MISSING`; do not generate or package from partial identity proof.
- Image QA gate: pass/fail per slide, retries, hard failures.
- Review Room final package gate: final blockers, image QA status, accepted-final proof, reports, and unresolved risks before export/package completion.
- Winner landing final gate: for source-winner remixes,
  `evals/final_winner_landing_check.json` must pass before package completion.
- Final package gate: final assets, reports, unresolved risks.

## Reference Hard Gate

Minimum final-generation requirement:
- At least four curated Aachu close face anchors from `references/identity/aachu/`.
- At least four curated Zuv close face anchors from `references/identity/zuv/`.
- Prefer at least one together/couple reference from `references/identity/together/`.
- Style references from `references/style/best-illustration/` or locked style rules are present.
- Text-style rules for baked-in handwritten typography are present.

Before final imagegen:
- Run `python3 scripts/prepare_imagegen_reference_context.py --run-id <run_id>` to create `references-used/selected_references.json` and `evals/imagegen_reference_load_plan.json`.
- Use `view_image` on every path in `view_image_queue`; the creator does not need to attach these images manually.
- Write `evals/imagegen_reference_visibility_proof.json` recording the loaded paths, timestamp, and prompt files covered.
- Write `evals/pre_imagegen_blocker_check.json`; if it finds emotional-state contradiction, active identity-reference scene collision, unsafe fallback review after correction, broad prompt-lock approval, or canvas uncertainty, stop before imagegen.
- Pass `gold_standard_identity_route_gate` in `scripts/astory_repo_qa.py`. This gate requires the full 2026-06-15 gold-standard route: at least four raw Aachu face anchors, four raw Zuv face anchors, three style references, 11 loaded references, current visibility proof, pre-generation eval, agent assignment matrix, prompt-room review, scene landing preview, scene options, selected idea, slide beat map, slide-count decision, trace states, and prompt language that makes raw Aachu/Zuv face anchors the highest-priority visual input while blocking style images, binders, or text descriptions from replacing them.
- If any queued image cannot be read, stop and mark `IDENTITY_REFERENCE_MISSING`.
- If `gold_standard_identity_route_gate` fails, stop and mark `GOLD_STANDARD_IDENTITY_ROUTE_MISSING`.
- If the active generation path cannot use the loaded image context, stop and mark `IDENTITY_REFERENCE_INPUT_UNPROVEN` instead of generating final Aachu/Zuv artwork.

## Imagegen Rules

Use the built-in image tool one slide at a time.

For each final slide:
- Generate native `1080x1350 px` portrait output.
- Never write an imagegen prompt that omits `1080x1350 px`.
- Never resize, crop, pad, or extend another surface into `1080x1350 px`.
- Include exact on-image text baked into the illustration.
- Include tiny low-contrast handwritten `@a.storyof.two` top-right.
- Save project-bound outputs into the run folder.

Hard-reject:
- identity drift, face merge, missing references
- yellow/parchment paper
- missing, wrong, or unreadable on-image text
- missing brandmark
- missing `1080x1350 px` prompt gate or wrong output canvas
- visual setting/scene logic that does not physically or emotionally make sense
- generic AI watercolor, quote-card, poster, anime, photorealism
- bad anatomy or scene/text contradiction

Retry up to 2 times per failure type with targeted prompt repair, then mark blocked.

## Prompt Contract

Build prompts from `references/master-prompt.md` plus the locked slide beat.
Before writing prompt text, use `anti-ai-slop-human-copy-filter` to protect the
exact on-image text, scene concept, and visual suggestion from
`AI_SLOP_COPY_DRIFT`. Prompts must preserve the creator's original setup and
must not turn the slide into generic romantic watercolor or quote-card staging.
Treat the master prompt as the canonical prompt contract formerly covered by the
separate prompt-only skill, but use compact priority-stack mode. Do not restore
the old long exact-template prompt. A prompt that repeats every possible rule
bucket as separate sections is a `PROMPT_OVERLOAD` failure, even if the
individual rules are good.

Use `references/house-style-contract.md` and `references/imagegen-contract.md`
as QA contracts for prompt review and generation decisions. Every slide prompt
must include, in no more than 10 major sections:
- exact on-image text
- locked scene and the one visual proof that makes the text work
- native `1080x1350 px` output requirement
- raw Aachu/Zuv face-anchor priority
- best-illustration style-reference priority
- neutral white/off-white paper rule with no yellow/parchment cast
- exact text placement and tiny top-right brandmark
- the minimum slide-specific anatomy/phone/prop negatives
- the final generation hard gate: no text-only/file-path-only identity, and one slide at a time

## Completion Rule

Only call a run complete when required artifacts exist, hard gates pass, final images are saved in `exports/`, `docs/approvals.md` documents the human approvals, and the run report documents approval status, eval scores, retries, failures, and limitations.
