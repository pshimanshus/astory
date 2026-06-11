# `/astory` Agentic System Granular Sprint Plan

## Sprint 0: Source-Of-Truth Workspace

- Initialize this folder as the clean project source.
- Create source, references, runs, docs, scratchbook, and sprint folders.
- Create identity, style, text-style, and brand reference folders.
- Write README, architecture, runbook, evals, taxonomy, roadmap, assumptions, setup status, and build log.

## Sprint 1: Skill Package Source

- Create `.agents/skills/astory/SKILL.md`.
- Define `/astory` triggers, non-negotiables, runtime modes, state machine, HITL gates, setup, resume, and audit.
- Create `.agents/skills/astory/agents/openai.yaml`.

## Sprint 2: Multi-Agent Persona Pack

- Add Idea Room personas: Relatability Ethnographer, Shareability Strategist, Visual Story Director.
- Add Story Room personas: Story Director, Pacing Editor, Swipe Retention Critic.
- Add Prompt Room personas: Identity Guardian, Style Guardian, Scene Logic Critic.
- Add Image QA Room personas: Face Match Reviewer, Style Fidelity Reviewer, Publishing QA Reviewer.
- Ensure every persona has mission, success definition, golden output, anti-patterns, rubric, output format, and failure codes.

## Sprint 3: Workflow Templates

- Add templates for input, planning, debates, bibles, prompts, evals, trace events, reports, caption pack, setup, audit, and resume.
- Keep templates stable and predictable so every run creates a useful scratchbook trail.

## Sprint 4: Setup And Reference Gate

- Define `/astory setup` behavior in the skill.
- Enforce minimum identity requirements.
- Write setup status format.
- Block final imagegen if identity references are missing or not visible to Codex.

## Sprint 5: Idea Room Agentic Debate

- Require 3 idea agents for every creative run.
- Define specific idea, theme, and auto modes.
- Require cross-critique, repair, scoring, threshold selection, and second round if weak.
- Save idea-room debate artifacts and pause for HITL idea lock.

## Sprint 6: Story And Slide Count Room

- Require story-room debate after idea lock.
- Decide story-led slide count.
- Produce story concept, slide count decision, and slide beat map.
- Pause for story/slide-count approval.

## Sprint 7: Prompt Pack And Prompt QA

- Build prompts from the A Story house style contract.
- Require exact text, identity lock, style lock, brandmark, scene logic, native aspect ratio, and negative constraints.
- Run prompt QA room and pause before imagegen.

## Sprint 8: Imagegen And Image QA

- Use built-in Codex `imagegen`, one slide at a time.
- Make identity and style references visible before final generation.
- Run image QA room.
- Retry hard failures up to 2 times, then block.

## Sprint 9: Reports, Audit, And Closeout

- Generate caption pack, run report, failure modes, portfolio case study, production handoff, and audit summary.
- Define `/astory audit <run_id>` and `/astory resume <run_id>`.

## Sprint 10: Install And Verification

- Keep `.agents/skills/astory/` as the authoritative repo-scoped skill source.
- Validate the repo-scoped skill.
- Verify setup behavior against empty references.
- Run a dry planning scenario after the repo-scoped skill is available in a new Codex turn.
