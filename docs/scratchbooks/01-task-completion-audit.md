# `/astory` Task Completion Audit

Date: `2026-06-07`

## Status Legend

- `Done`: implemented and verified structurally.
- `Dry-run verified`: exercised in a planning-only run.
- `Defined, not production-run verified`: behavior exists in skill/templates but has not been exercised through final imagegen.
- `Pending`: not done yet.

## Granular Sprint Plan Audit

| Sprint | Planned Work | Status | Evidence |
|---|---|---|---|
| Sprint 0 | Source-of-truth workspace, git, root folders, README, docs, scratchbook | Done | Root docs, `docs/scratchbooks/00-build-log.md`, commit `b089668` |
| Sprint 1 | `/astory` repo-scoped skill package source | Done | `.agents/skills/astory/`, validator passed |
| Sprint 2 | Multi-agent persona pack | Done | 12 persona files under `.agents/skills/astory/personas/` |
| Sprint 3 | Workflow templates | Done | templates for input, planning, scene selection, debates, prompts, evals, logs, reports |
| Sprint 4 | Setup and reference gate | Done | `docs/setup_status.md`; identity and style refs now imported |
| Sprint 5 | Idea-room agentic debate | Dry-run verified | `runs/2026-06-07_12-59-22_kitchen-help-dry-run/debates/idea_room/` |
| Sprint 6 | Story and slide-count room | Defined, not production-run verified | Personas/templates exist; no full story-room run yet |
| Sprint 7 | Prompt pack and prompt QA | Defined, not production-run verified | Prompt templates/personas exist; no prompt-lock run yet |
| Sprint 8 | Imagegen and image QA | Defined, not production-run verified | Skill rules/personas exist; no final imagegen run yet |
| Sprint 9 | Reports, audit, closeout | Partially dry-run verified | Dry-run reports exist; final image package reports not yet exercised |
| Sprint 10 | Repo-scoped skill verification | Partially done | Skill source is validated under `.agents/skills/astory/`; `/astory setup` behavior represented in docs; fresh-turn discovery still needs real invocation |

## Attached System Plan Audit

| Plan Area | Status | Notes |
|---|---|---|
| Codex-native skill/workspace architecture | Done | Implemented as `/astory`, not `/story`, per later user correction |
| Workspace structure | Done | V2 has docs, references, runs, skill source |
| Skill responsibilities | Done | Covered in `.agents/skills/astory/SKILL.md` |
| State machine | Done | Defined in skill and architecture docs |
| Input Interpreter | Template done; dry-run verified | `input/creative_brief.json` created in dry run |
| Idea Strategist | Dry-run verified | 3 subagents, scoring, selection, rejected ideas |
| Story Planner | Defined, pending run | Templates/personas exist |
| Slide Count Director | Defined, pending run | Persona and template exist |
| Scene Generator/Selector | Defined, pending run | Separate `scene_options.json` and `selected_scenes.json` templates now exist; not production-run verified yet |
| Character Bible Agent | Defined, pending run | Template exists; identity refs imported |
| Style Bible Agent | Defined, pending run | Template exists; style refs imported |
| Prompt Architect | Defined, pending run | Prompt templates exist |
| Pre-Generation Evaluator | Defined, pending run | Eval template exists |
| Image Producer | Defined, pending run | Built-in imagegen rules exist; no generated images yet |
| Image Quality Evaluator | Defined, pending run | Personas/eval template exist |
| Revision Agent | Defined, pending run | Revision template exists |
| Caption/Distribution Agent | Defined, pending run | Caption template exists |
| Report Writer | Partially dry-run verified | Dry-run reports exist; final package reports pending |
| HITL gates | Defined; idea lock dry-run verified | Full prompt/image/final gates pending real run |
| Failure taxonomy | Done | Root and skill reference taxonomy exist |

## Remaining Concrete Gaps

1. Run a fresh `/astory setup` invocation in a new Codex turn/session so skill discovery uses the repo-scoped skill.
2. Run a full `/astory` production flow past idea lock now that identity and style references are present.
3. Exercise story room, slide-count decision, scene selection, prompt QA, built-in imagegen, image QA, retries, caption pack, and final package.
4. Commit style-reference import, scene-template coverage, and audit updates.
