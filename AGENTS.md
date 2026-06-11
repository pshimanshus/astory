# A Story of Two V2 Codex Guidance

This file is the lean repo router for Codex. Keep durable repo expectations here;
keep the detailed `/astory` workflow in the repo-scoped skill.

## Source Of Truth

- Workflow skill: `.agents/skills/astory/SKILL.md`
- References: `references/`
- Run artifacts: `runs/<run_id>/`
- Setup status: `docs/setup_status.md`

If this file conflicts with the `/astory` skill on workflow details, the skill
wins. If either conflicts with actual reference files, the local references win.

## Working Rules

- Use `/astory` for A Story of Two carousel setup, idea generation, resume,
  audit, prompt work, image generation, and final packaging.
- Do not final-generate Aachu/Zuv artwork unless selected identity and style
  references are available and made visible to Codex in context.
- Preserve HITL gates: idea lock, story/slide-count lock, prompt lock, image QA,
  and final package.
- Record HITL decisions in the run folder before continuing past a gate.
- Save run outputs under `runs/<run_id>/` using the skill folder contract.
- Use built-in Codex `imagegen` only for images; do not ask for API keys,
  provider setup, npm commands, or a local image app.
- Verify artifacts and checks before claiming a run is ready, blocked, or
  complete.
- Keep the repo-scoped `.agents/skills/astory/` skill as the single active
  A Story workflow entry. Prompt-only A Story guidance belongs inside that
  skill's references, not in a separate active personal skill.

## Current Skill Layout

The checked-in skill source is `.agents/skills/astory/`. Do not recreate a
second checked-in legacy skill copy elsewhere in the repo.

The old personal install at `~/.codex/skills/astory/` may exist, but it is not
authoritative for this repository.

The old personal prompt helper at `~/.codex/skills/a-story-carousel-prompt/`
may exist for archive/recovery only; it should not be treated as an active
repo workflow.
