# Shared Agentic Operating System Plan

Date: 2026-06-07

Scope: two V2 projects sharing one inspectable development operating system. This repository, `/Users/himanshusharma/A Story of Two V2`, already contains the first seed: a lean `AGENTS.md`, repo-scoped `.agents/skills/astory/`, `references/`, `runs/`, and `docs/setup_status.md`.

Official Codex source basis:
- Codex best practices: https://developers.openai.com/codex/learn/best-practices
- AGENTS.md: https://developers.openai.com/codex/guides/agents-md
- Skills: https://developers.openai.com/codex/skills
- MCP: https://developers.openai.com/codex/mcp
- Automations: https://developers.openai.com/codex/app/automations
- Subagents: https://developers.openai.com/codex/subagents
- Memories: https://developers.openai.com/codex/memories
- Hooks: https://developers.openai.com/codex/hooks
- Sandboxing and approvals: https://developers.openai.com/codex/agent-approvals-security
- Review: https://developers.openai.com/codex/app/review
- Embeddings: https://platform.openai.com/docs/guides/embeddings

## 1. Executive Narrative

Project A and Project B should evolve from ordinary repositories into two product codebases with one shared habit: every useful repeated action becomes easier next time. V1 is "ask Codex, hope the context is enough, manually patch the gaps." V2 is "give Codex durable project guidance, let skills handle repeatable workflows, record failures and decisions as searchable evidence, and require review before durable rules change."

The system is trying to become a practical learning loop:

`Observe -> Diagnose -> Propose -> Debate -> Implement small change -> Validate -> Record -> Generalize -> Report health`

What changes from V1 to V2:
- Instructions move from chat history into `AGENTS.md`, focused docs, and repo skills.
- Repeated manual workflows move into `.agents/skills/<workflow>/SKILL.md`.
- Failures produce a short retrospective, a memory entry, and usually a test or eval candidate.
- Decisions and rejected ideas are stored so future agents can cite them instead of rediscovering them.
- Health reports make debt visible before it becomes folklore.

How agents collaborate:
- The main orchestrator owns scope, final judgment, and human gates.
- Explorer agents gather repo evidence.
- Builder agents implement small changes only after a plan is approved.
- Skeptic/reviewer agents attack assumptions, diffs, and missing tests.
- Memory curator agents record durable lessons after evidence exists.

How memory works:
- `AGENTS.md` is for mandatory rules.
- Checked-in docs are for durable project knowledge and decisions.
- Codex memories are a helpful local recall layer, not a source of required team truth.
- A vector index retrieves past failures, decisions, rejected ideas, health reports, and skill candidates.
- Every retrieved memory must be cited by file path and id.

How skills emerge:
- A skill is created only after a workflow repeats, causes mistakes, or requires a fragile sequence.
- First version is instruction-only unless a script removes real risk.
- Scripts are added only when deterministic execution is better than model judgment.

How failures become leverage:
- A failed command, bad assumption, broken test, user correction, review comment, or blocked HITL gate creates a retrospective.
- The retrospective decides whether the lesson becomes a test, eval, skill, AGENTS rule, doc update, or memory only.

How chaos is avoided:
- No blind self-modification.
- Durable updates require evidence, proposed diff, reason, validation, rollback path, and approval.
- `AGENTS.md` stays lean. Details live in linked docs and skills.
- Automations report and propose. They do not merge, deploy, rotate secrets, or change production by default.

Health after 30 days:
- One root `AGENTS.md`, three working skills, one health report template, one failure schema, and first memory ingestion prototype.
- Project commands and fragile areas are documented.
- First failures have linked tests or eval candidates.

Health after 60 days:
- Weekly health report runs reliably.
- Top repeated manual workflows have skills.
- Rejected ideas and decisions are searchable.
- PR/review guidance is consistent across both projects.

Health after 90 days:
- New agents can understand either project in under 10 minutes.
- Health reports reveal trends, not just one-off warnings.
- Most repeated failures have regression checks.
- Skills have been pruned, tested, and kept small.

## 2. System Architecture

Text diagram:

```text
Human owner
  |
  v
Main orchestrator
  |
  +-- Instruction layer: AGENTS.md, code_review.md, PLANS.md, DoD
  +-- Skill layer: .agents/skills/*, skill registry, skill evals
  +-- Memory layer: docs artifacts + memory/ JSONL store + vector index + Codex memories
  +-- Evaluation layer: tests, lint, typecheck, product checks, agent evals
  +-- Orchestration layer: explorer, builder, skeptic, reviewer, test, curator
  +-- Safety layer: sandbox, approvals, worktrees, secrets rules, rollback
  |
  v
Small approved changes -> validation -> durable record -> health report
```

Repo/folder structure:

```text
.
├── AGENTS.md
├── code_review.md
├── PLANS.md
├── docs/
│   ├── agentic-operating-system.md
│   ├── health-reports/
│   ├── decisions/
│   ├── failures/
│   ├── rejected-ideas/
│   ├── playbooks/
│   └── templates/
├── .agents/
│   ├── skill-registry.md
│   └── skills/
│       ├── failure-retrospective/
│       ├── health-report/
│       ├── idea-debate/
│       └── ...
├── .codex/
│   ├── config.toml
│   ├── agents/
│   │   ├── skeptic.toml
│   │   ├── explorer.toml
│   │   ├── reviewer.toml
│   │   └── memory-curator.toml
│   └── rules/
├── memory/
│   ├── schemas/
│   ├── raw/
│   ├── processed/
│   ├── vector-index/
│   └── retrieval.md
├── evals/
│   ├── agent-behavior/
│   ├── failure-regressions/
│   └── skill-evals/
└── scripts/
    ├── ingest_memory.py
    ├── retrieve_memory.py
    ├── generate_health_report.py
    └── create_failure_eval.py
```

Memory layers:
- Layer 0, prompt/thread: temporary task facts.
- Layer 1, `AGENTS.md`: mandatory repo rules and commands.
- Layer 2, checked-in docs: decisions, failures, rejected ideas, health reports, playbooks.
- Layer 3, semantic memory: vector index over Layer 2 plus selected traces and review notes.
- Layer 4, Codex local memories: personal/project recall, never the only place for rules.

Skill layers:
- Repo skills in `.agents/skills/`: project workflows.
- User skills in `~/.codex/skills`: personal workflows.
- Plugin skills: distributable bundles if the shared OS should move across teams.
- Scripts inside skills only when they improve reliability.

Agent roles:

| Role | Job | Default mode |
| --- | --- | --- |
| Main orchestrator | Owns scope, gates, final synthesis | medium/high reasoning |
| Explorer | Reads files, maps commands, finds evidence | read-heavy |
| Builder | Implements approved small changes | workspace-write |
| Skeptic/debunker | Attacks assumptions and risks | high reasoning |
| Reviewer | Reviews diffs, tests, security, maintainability | high reasoning |
| Test/eval agent | Creates and runs validation | workspace-write |
| Memory curator | Records lessons with citations | read/write docs |
| Skill creator | Converts repeated workflows into skills | write `.agents/skills` |
| Health reporter | Runs checks and writes reports | read-heavy first |
| Product strategist | Evaluates user value and tradeoffs | read-heavy |

Codex config layers:
- User `~/.codex/config.toml`: personal defaults, memories, trusted MCP, profiles.
- Project `.codex/config.toml`: repo-safe defaults, agents, MCP settings, hooks, rules. Only after project trust.
- CLI overrides: one-off model, sandbox, approval, or profile.
- Rules: allow/prompt/forbid command prefixes outside the sandbox.

AGENTS hierarchy:
- Global `~/.codex/AGENTS.md`: personal style and universal safety.
- Repo `AGENTS.md`: shared standards and project router.
- Subtree `AGENTS.md` or `AGENTS.override.md`: local rules near specialized code.
- Keep root under roughly 200 lines. Link out for detail.

Evaluation/test infrastructure:
- Normal code checks: unit, integration, lint, typecheck, build.
- Product checks: acceptance criteria, UX review, accessibility, edge cases.
- Agent behavior evals: did the agent follow gates, cite memory, avoid forbidden actions?
- Skill evals: trigger precision, required artifact completion, validation behavior.
- Failure regressions: every repeated failure gets a test, eval, or checklist.

Pipelines:
- Health report: gather commands -> run safe checks -> summarize risks -> update health report -> propose memory/skill/eval changes.
- Idea critique: propose -> skeptic -> evidence -> builder smallest test -> reviewer -> decision -> memory update.
- Semantic retrieval: query -> embed -> vector candidates -> keyword/path filters -> freshness/risk boost -> cite top evidence.
- Docs update: evidence -> proposed diff -> reason -> validation -> rollback -> human review.
- Failure-to-skill: repeated manual pain -> skill candidate -> first instruction-only skill -> manual trial -> skill eval -> optional script.

## 3. AGENTS.md Design

Starter root `AGENTS.md`:

```md
# Shared V2 Codex Guidance

## Purpose

This repository is part of a two-project V2 system. Codex should help build product value while improving the development system itself: repeated workflows become skills, repeated failures become tests/evals/memory, and durable rules are reviewed before they become instructions.

## Source Of Truth

- Product docs: `docs/`
- Agent workflows: `.agents/skills/`
- Skill registry: `.agents/skill-registry.md`
- Decisions: `docs/decisions/`
- Failures: `docs/failures/`
- Rejected ideas: `docs/rejected-ideas/`
- Health reports: `docs/health-reports/`

If this file conflicts with a closer `AGENTS.md` or `AGENTS.override.md`, the closer file wins for that subtree. If instructions conflict with source files or tests, inspect the source and ask before changing durable guidance.

## Working Rules

- Read relevant instructions, docs, and tests before making changes.
- Keep changes small, reviewable, and tied to the user request.
- Prefer existing project patterns over new abstractions.
- Do not overwrite user changes.
- Do not self-modify durable rules without evidence, proposed diff, validation, rollback path, and human approval.
- Use repo skills for repeated workflows.
- Record new durable lessons in checked-in docs before relying on them later.

## Project Layout

- Project A: `[PROJECT_A_PATH]` - `[PROJECT_A_PURPOSE]`
- Project B: `[PROJECT_B_PATH]` - `[PROJECT_B_PURPOSE]`
- Shared agent OS: `.agents/`, `docs/`, `memory/`, `evals/`, `scripts/`

## How To Run

Project A:
- Install: `TODO: discover from package manager or docs`
- Dev: `TODO`
- Test: `TODO`
- Lint/typecheck/build: `TODO`

Project B:
- Install: `TODO`
- Dev: `TODO`
- Test: `TODO`
- Lint/typecheck/build: `TODO`

When a command is unknown, discover it from `README`, package manifests, Makefiles, CI, or existing scripts. Mark unknown commands as TODO in docs instead of inventing them.

## Coding Standards

- Use clear names and small modules.
- Add abstractions only when they remove real duplication or risk.
- Add tests proportionate to risk.
- Keep generated or tool output out of commits unless it is an intended artifact.

## Product And UX Standards

- Start from the user problem.
- State the smallest falsification test for product ideas.
- For UX changes, check empty, loading, error, long-content, and mobile states when applicable.

## Security And Dependency Rules

- Never expose secrets in logs, memory, docs, prompts, or commits.
- Ask approval before adding production dependencies.
- Ask approval before credential, infrastructure, network, or deployment changes.
- Prefer sandboxed, workspace-local work.

## Review Expectations

- Use `code_review.md` for review stance.
- Findings first, ordered by severity, with file references.
- Before completion, run relevant checks or explain exactly why they could not run.

## Definition Of Done

- Requirement satisfied.
- Relevant tests/checks run or blocked with reason.
- Docs updated when behavior or workflow changed.
- Failure, eval, memory, or skill proposal created when a repeated mistake appeared.
- Diff reviewed for unrelated churn.

## When To Create Or Update A Skill

Create a skill when a workflow repeats at least twice, is fragile, needs many steps, or is valuable enough that future agents should not rediscover it. Keep the first version instruction-only unless a deterministic script is clearly safer.

## When To Update Memory

Update memory for failures, decisions, rejected ideas, validated patterns, repeated corrections, and health report findings. Do not store secrets, speculation, or raw noisy logs.

## When To Create An Eval

Create an eval when a failure can recur, an agent ignored a rule, a skill can regress, or product quality depends on repeatable judgment.

## Human Approval Required

- Durable changes to `AGENTS.md`, skills, memory schemas, eval policy, hooks, rules, or automations.
- Dependency additions, production credentials, infrastructure, deployment, data deletion, or broad network access.
- Merging, releasing, or publishing.

## Agents Must Never

- Commit secrets or generated credential files.
- Auto-merge or deploy by default.
- Delete user work to clean up the diff.
- Treat chat memory as mandatory project truth.
- Add broad rules to `AGENTS.md` from one weak example.
```

Subdirectory `AGENTS.md` template:

```md
# [Subtree Name] Codex Guidance

## Scope

Applies to files under `[path/]`.

## Local Source Of Truth

- Main entry points:
- Tests:
- Docs:

## Local Commands

- Test:
- Lint/typecheck:
- Build:

## Local Rules

- Rule 1:
- Rule 2:

## Review Focus

- Risk 1:
- Risk 2:

## Do Not

- Local forbidden action:
```

## 4. Skill System Design

Skill quality checklist:
- Name is lowercase hyphen-case and under 64 characters.
- Frontmatter has only `name` and `description`.
- Description says exactly when to trigger and when not to trigger.
- Body is short, imperative, and artifact-focused.
- Inputs and outputs are explicit.
- Required validation is stated.
- Scripts exist only when deterministic reliability matters.
- Skill has at least one realistic eval prompt.
- Skill registry links owner, version, and last review date.

Initial catalog:

| Skill | Purpose | Trigger phrases | Inputs | Outputs | Use | Do not use | Files/tools | Quality bar |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| failure-retrospective | Convert failure into lesson | failed run, retrospective, learn from failure | logs, error, task, fix | failure memory, eval/skill/rule proposal | after concrete failure | vague anxiety | docs/failures, memory schema | root cause and validation present |
| health-report | Produce repo health report | health report, audit health | repo, commands, docs | daily/weekly/release report | recurring checks | replacing tests | test/lint/build commands | top risks and next actions |
| idea-debate | Propose, attack, refine ideas | debate ideas, skeptic, product ideas | prompt, constraints, memory | accepted/rejected ideas | product/UX/architecture ideas | trivial tasks | docs/rejected-ideas | decisions cite evidence |
| agent-md-maintenance | Propose AGENTS updates | update AGENTS, repeated agent mistake | evidence, current rules | patch proposal | repeated durable rules | one-off preference | AGENTS.md | lean diff and rollback |
| semantic-memory-ingestion | Ingest docs/logs into vector memory | ingest memory, index failures | docs, JSONL, embeddings | chunks, metadata, index | after curated artifacts exist | raw secret logs | scripts/ingest_memory.py | citations resolve |
| eval-from-failure | Turn failure into eval/test | make eval from bug | failure record | test/eval/checklist | recurring failure | unrepeatable incident | evals/*, tests | fails before fix or checks behavior |
| codex-handoff | Create Codex-ready handoff | handoff, resume task | goal, context, constraints | handoff doc | task transfer | tiny tasks | docs/templates | clear done-when |
| product-critique | First-principles product review | critique product, UX risk | idea, users, evidence | critique, falsification test | product changes | pure refactor | docs/decisions | identifies assumptions |
| implementation-plan | Convert idea into staged plan | implementation plan | approved spec | phases, tests, rollback | multi-step implementation | coding immediately | PLANS.md | small testable steps |
| docs-refactor | Keep docs useful | refactor docs, docs audit | docs tree | doc patch proposal | stale docs | code design | docs/* | less text, more truth |

Starter SKILL.md skeletons:

```md
---
name: failure-retrospective
description: Use after a failed run, failed test, blocked implementation, user correction, review finding, or repeated mistake to create a structured lesson, memory entry, eval candidate, and proposed AGENTS.md or skill update. Do not use for hypothetical risks without evidence.
---

# Failure Retrospective

Inputs: task, symptoms, logs or review notes, attempted fix, final outcome.

Workflow:
1. Identify failure type and root cause from evidence.
2. Record failed approach and why it failed.
3. Record successful fix or current blocker.
4. Decide: test, eval, skill, AGENTS update, docs update, or memory only.
5. Write `docs/failures/YYYY-MM-DD-<slug>.md`.
6. Add a JSONL memory entry only after secrets are checked.
7. Propose durable updates as diffs, not silent edits.

Output: failure report, memory entry, validation command, and next durable update proposal.
```

```md
---
name: health-report
description: Use to create daily, weekly, release-readiness, or post-failure project health reports covering build, tests, lint/type health, architecture drift, docs, agent-readiness, memory quality, skill quality, repeated failures, stale decisions, and next eval/skill candidates.
---

# Health Report

Workflow:
1. Inspect repo status and known commands.
2. Run safe checks that are documented and approved.
3. Summarize health by category with evidence.
4. Identify top 5 risks and top 5 improvements.
5. Propose memory, skill, eval, or docs updates.
6. Save report to `docs/health-reports/YYYY-MM-DD-<kind>.md`.

Do not fix code during the report unless the user explicitly asks.
```

```md
---
name: idea-debate
description: Use when generating, critiquing, rejecting, parking, prototyping, or improving product, UX, architecture, or workflow ideas through proposer, skeptic, evidence, builder, reviewer, and memory-curator roles.
---

# Idea Debate

For each idea, produce: idea, user problem, expected impact, core assumption, fastest falsification test, skeptic critique, evidence found, decision, why, next action, memory update.

Workflow:
1. Proposer creates candidates.
2. Skeptic attacks assumptions, incentives, UX, feasibility, and maintenance.
3. Evidence agent searches repo, logs, docs, metrics, and memory.
4. Builder defines the smallest testable prototype for survivors.
5. Reviewer checks risk and regression potential.
6. Memory curator records accepted, parked, and rejected ideas.
```

```md
---
name: agent-md-maintenance
description: Use when repeated agent mistakes, durable repo rules, review findings, or health reports suggest a precise AGENTS.md update. Do not use for one-off preferences or broad vague guidance.
---

# AGENTS.md Maintenance

Workflow:
1. Gather at least two evidence points or one high-severity incident.
2. Check whether a skill or doc is better than root AGENTS.md.
3. Draft the smallest rule.
4. Provide proposed diff, reason, validation, and rollback.
5. Wait for human approval before editing.
```

```md
---
name: semantic-memory-ingestion
description: Use to ingest curated failures, decisions, rejected ideas, health reports, PR reviews, and validated patterns into a searchable semantic memory store with embeddings, metadata, dedupe, and citations. Do not ingest raw secret-bearing logs.
---

# Semantic Memory Ingestion

Workflow: collect curated source files, redact secrets, chunk by artifact section, embed chunk text, write metadata JSONL, update vector index, run retrieval smoke test, save ingestion report.
```

```md
---
name: eval-from-failure
description: Use after a bug, failed test, bad agent assumption, repeated correction, or review finding when the failure can recur and should become a regression test, agent behavior eval, skill eval, checklist, or validation rule.
---

# Eval From Failure

Workflow: classify failure, choose eval type, write the smallest failing check, run it to confirm signal where possible, link it from the failure memory, and document what passing means.
```

```md
---
name: codex-handoff
description: Use to create a Codex-ready handoff for continuing work in another thread, worktree, project, or agent, with goal, context, constraints, files, commands, expected artifacts, validation gates, and open risks.
---

# Codex Handoff

Output sections: goal, current state, constraints, files to inspect, commands to run, decisions already made, unresolved questions, done-when, rollback, and validation.
```

```md
---
name: product-critique
description: Use to critique proposed product or UX changes from first principles: user value, behavior, incentives, edge cases, adoption, failure modes, tradeoffs, and smallest falsification test.
---

# Product Critique

Workflow: name the user problem, state the behavior change, identify assumptions, attack failure modes, define falsification test, recommend reject, park, prototype, or implement.
```

```md
---
name: implementation-plan
description: Use to turn an approved product, architecture, workflow, or skill idea into staged technical work with tasks, files, tests, validation commands, risks, rollback paths, and definition of done.
---

# Implementation Plan

Workflow: map files, split into small phases, define tests before implementation, include validation commands, define rollback, and save plan under `docs/plans/` or the repo's chosen plan path.
```

```md
---
name: docs-refactor
description: Use to audit, simplify, reorganize, or update project documentation so humans and agents can find current truth quickly. Do not use to bury decisions in prose when AGENTS.md, tests, or schemas are better.
---

# Docs Refactor

Workflow: inventory docs, identify stale/conflicting/duplicated sections, propose a smaller structure, preserve source-of-truth links, validate references, and provide a diff summary.
```

## 5. Semantic Memory Design

Store:
- Failure reports with root cause and validation.
- Decisions with alternatives and revisit triggers.
- Rejected ideas with evidence and conditions for reconsideration.
- Validated patterns and successful fixes.
- Health report summaries and risk trends.
- Skill candidates and skill eval results.
- Review comments that changed behavior.

Never store:
- Secrets, tokens, credentials, private keys, session cookies.
- Raw logs before redaction.
- Personal data not needed for engineering decisions.
- Speculation without evidence.
- Duplicates of whole large files.
- Mandatory rules that only exist in memory.

Chunking:
- Chunk by artifact section, not arbitrary token windows.
- Target 300 to 800 tokens per chunk.
- Include title, id, project, date, artifact type, tags, and source path in every chunk.
- For traces, chunk only summarized events or failure windows.

Embedding model recommendation:
- Start with `text-embedding-3-small` for cost-effective semantic search.
- Use `text-embedding-3-large` only for high-recall cross-language or high-value retrieval.
- Store model name, dimensions, and created_at in index metadata.
- Use dimensions reduction only after measuring retrieval quality.

Storage recommendation:
- MVP: JSONL metadata plus a local NumPy/SQLite store and brute-force cosine search. This is enough for hundreds or low thousands of curated memories.
- Phase 2: `sqlite-vec`, LanceDB, or another local vector store if query volume grows.
- Avoid hosted vector DB until both projects prove memory volume and access policy.

Retrieval algorithm:
1. Build query text from task, repo, files, and failure symptoms.
2. Embed query.
3. Retrieve top 30 by cosine similarity.
4. Add keyword/path/tag matches.
5. Boost recent unresolved failures and active decisions.
6. Down-rank superseded, archived, or low-confidence entries.
7. Return top 5 to the agent with id, path, date, summary, and why it matched.

Ranking logic:
- 50 percent vector similarity.
- 20 percent exact tag/path/project match.
- 15 percent freshness for active work.
- 10 percent severity or repeated frequency.
- 5 percent validation strength.

Freshness:
- Active failures: high boost until linked test/eval passes.
- Decisions: boost until revisit trigger expires.
- Rejected ideas: low by default, boost near revisit date or when conditions match.
- Old health reports: used for trend only.

Deduplication:
- Stable id includes artifact type, date, project, and slug.
- Hash normalized `embedding_text`.
- If new entry is similar above threshold and same type/project, link it as recurrence instead of storing duplicate.

Decay and archival:
- Archive memories not cited for 180 days unless they are high severity or source-of-truth decisions.
- Keep archived files searchable but down-ranked.
- Delete redacted raw inputs after processing unless needed for audit.

Conflict resolution:
1. Source files and tests win.
2. Closest `AGENTS.md` wins for instructions.
3. Current approved decisions win over older decisions.
4. Memory entries must cite source artifacts.
5. Conflicts produce a docs update proposal, not silent guessing.

Schemas:

```json
{
  "id": "failure-2026-06-07-project-a-slug",
  "project": "project-a",
  "date": "2026-06-07",
  "task": "",
  "failure_type": "",
  "symptoms": [],
  "root_cause": "",
  "failed_approach": "",
  "why_it_failed": "",
  "successful_fix": "",
  "validation_command": "",
  "files_involved": [],
  "linked_test_or_eval": "",
  "should_update_agents_md": false,
  "should_create_skill": false,
  "embedding_text": "",
  "tags": []
}
```

```json
{
  "id": "decision-2026-06-07-project-a-slug",
  "project": "project-a",
  "date": "2026-06-07",
  "decision": "",
  "context": "",
  "alternatives_considered": [],
  "tradeoffs": [],
  "owner": "",
  "status": "active",
  "revisit_trigger": "",
  "linked_files": [],
  "embedding_text": "",
  "tags": []
}
```

```json
{
  "id": "rejected-idea-2026-06-07-project-a-slug",
  "project": "project-a",
  "date": "2026-06-07",
  "idea": "",
  "proposed_by": "",
  "rejection_reason": "",
  "hidden_assumption": "",
  "evidence_against": [],
  "what_would_change_our_mind": "",
  "future_revisit_date_or_condition": "",
  "related_ideas": [],
  "embedding_text": "",
  "tags": []
}
```

```json
{
  "id": "skill-candidate-2026-06-07-slug",
  "repeated_manual_work": "",
  "frequency": "",
  "pain_level": "",
  "candidate_skill_name": "",
  "expected_inputs": [],
  "expected_outputs": [],
  "automation_risk": "",
  "first_version_scope": "",
  "validation_method": "",
  "embedding_text": "",
  "tags": []
}
```

## 6. Failure-To-Learning Loop

What counts as failure:
- Failed tests, failed builds, lint/type errors.
- A fix that did not work.
- A user correction caused by wrong assumption.
- A PR review finding.
- A blocked HITL gate.
- A flaky or confusing command.
- A production/deployment failure.
- A repeated manual action that wasted time.

Who diagnoses it:
- Main orchestrator for scope.
- Explorer for evidence.
- Skeptic for root-cause challenge.
- Test/eval agent for regression check.
- Memory curator for durable entry.

Artifacts:
- `docs/failures/YYYY-MM-DD-<slug>.md`
- `memory/raw/failures.jsonl`
- linked test/eval/checklist where applicable
- optional AGENTS/skill/docs proposal

Decision tree:

```text
Did something concrete fail?
  no -> do not create failure memory
  yes -> is there evidence?
    no -> write investigation note only
    yes -> can it recur?
      no -> memory only if high severity
      yes -> can code/test catch it?
        yes -> create test or regression eval
        no -> can skill/checklist catch it?
          yes -> create skill/eval/checklist proposal
          no -> memory with revisit trigger

Was the failure caused by unclear durable rule?
  yes -> propose small AGENTS.md update

Was it caused by repeated workflow friction?
  yes -> create skill candidate

Is the evidence weak or duplicate?
  yes -> link to existing memory, do not add new entry
```

Noise controls:
- Require source path, command, review link, or artifact.
- No memory from a single low-impact typo unless repeated.
- One summary entry per incident, not per log line.
- Weekly memory pruning in health report.

How to know the lesson helped:
- Same failure does not recur for 30 days.
- Linked regression check catches an intentional bad sample.
- Future handoffs cite the memory and avoid the mistake.
- Health report shows reduced repeated-failure count.

## 7. Idea Generation, Debunking, And Build-Upon Workflow

Roles:
- Proposer: names idea and expected upside.
- Skeptic: attacks assumptions, incentives, UX, feasibility, risk.
- Evidence agent: checks repo, logs, metrics, prior memory, user evidence.
- Builder: defines smallest testable implementation.
- Reviewer: checks maintainability and regressions.
- Memory curator: records accepted, parked, rejected ideas.

Per-idea output:

```md
## Idea

- Idea:
- User problem:
- Expected impact:
- Core assumption:
- Fastest falsification test:
- Skeptic critique:
- Evidence found:
- Decision: reject | park | prototype | implement
- Why:
- Next action:
- Memory update:
```

Decision policy:
- Reject if upside depends on a false assumption or creates more maintenance than value.
- Park if evidence is insufficient but upside could matter later.
- Prototype if risk is bounded and falsification is cheap.
- Implement only when value, evidence, and validation path are clear.

## 8. Health Report System

Categories:
- build health
- test health
- lint/type health
- dependency health
- architecture health
- UX/product health
- documentation health
- agent-readiness health
- memory quality
- skill quality
- AGENTS.md quality
- repeated failure patterns
- stale decisions
- rejected ideas worth revisiting
- top 5 risks
- top 5 improvements
- next skill
- next eval

Reports:

| Report | Trigger | Inputs | Commands/tools | Path | Scoring | Owner/reviewer | Feeds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Daily lightweight | start/end of workday or manual | git status, TODOs, known checks | safe tests/lint if cheap | `docs/health-reports/YYYY-MM-DD-daily.md` | green/yellow/red | health reporter/human | memory candidates |
| Weekly deep | weekly | all docs, failures, decisions, skills | tests, lint, build, doc audit | `docs/health-reports/YYYY-MM-DD-weekly.md` | 0-5 per category | health reporter/reviewer | skills/evals/docs |
| Release readiness | before release | release diff, checks, risks | full validation | `docs/health-reports/YYYY-MM-DD-release.md` | pass/block | reviewer/human | release decision |
| Post-failure | after incident | logs, failed command, fix | reproduction check | `docs/health-reports/YYYY-MM-DD-post-failure.md` | severity/recur risk | orchestrator/human | failure memory |

Scoring rubric:
- 5: healthy, documented, checked, low risk.
- 4: minor issues, clear owner.
- 3: usable but accumulating debt.
- 2: risky, repeated failures, missing docs/checks.
- 1: blocked or unreliable.
- 0: unknown because basic evidence is missing.

## 9. Implementation Roadmap

Phase 0, audit and baseline:
- Goals: map both repos, commands, docs, fragile areas.
- Tasks: inspect README, manifests, CI, docs, existing skills, test commands.
- Files: `docs/health-reports/<date>-baseline.md`, `docs/playbooks/command-map.md`.
- Outputs: baseline health report, command inventory, repeated workflow list.
- Validation: commands marked known/TODO with evidence.
- Risks: inventing commands; avoid by citing source files.
- Rollback: delete baseline report if inaccurate.
- Done: human can see current health and unknowns.

Phase 1, Codex foundation:
- Goals: durable guidance and review policy.
- Tasks: create/update `AGENTS.md`, `code_review.md`, `PLANS.md`, approval policy, worktree strategy.
- Files: root docs plus optional `.codex/config.toml`.
- Validation: `codex --ask-for-approval never "Summarize current instructions."`
- Risks: bloated root guidance.
- Rollback: restore prior `AGENTS.md`.
- Done: root rules are lean and test/lint commands are discoverable.

Phase 2, skill system MVP:
- Goals: first three skills.
- Tasks: create `failure-retrospective`, `health-report`, `idea-debate`, registry, quality checklist.
- Files: `.agents/skills/*/SKILL.md`, `.agents/skill-registry.md`.
- Validation: run realistic prompts manually; validate frontmatter.
- Risks: too many skills too early.
- Current repo note: in some managed Codex sandboxes, `.agents/` may be protected and require an approval flow to edit.
- Rollback: disable or remove unused skill.
- Done: three skills produce useful artifacts.

Phase 3, memory MVP:
- Goals: curated memory store and retrieval.
- Tasks: schemas, JSONL store, brute-force embedding retrieval.
- Files: `memory/schemas/*.json`, `memory/raw/*.jsonl`, `scripts/ingest_memory.py`, `scripts/retrieve_memory.py`.
- Validation: retrieve a known failure by paraphrase.
- Risks: secrets/noise.
- Rollback: delete generated index, keep curated source docs.
- Done: top results cite source paths.

Phase 4, failure/eval loop:
- Goals: convert real failures into checks.
- Tasks: retrospective flow, eval-from-failure skill, first regression tests/evals.
- Files: `docs/failures/`, `evals/failure-regressions/`.
- Validation: eval catches known bad sample.
- Risks: eval theater.
- Rollback: remove weak evals.
- Done: at least one failure has a useful regression check.

Phase 5, idea debate loop:
- Goals: product/UX idea quality.
- Tasks: proposer/skeptic/evidence workflow, rejected ideas store, one prototype plan.
- Files: `docs/rejected-ideas/`, `docs/decisions/`.
- Validation: rejected ideas have clear evidence and revisit conditions.
- Risks: endless debate.
- Rollback: timebox debate.
- Done: one survivor has smallest falsification test.

Phase 6, health reports and automation:
- Goals: recurring reports.
- Tasks: daily/weekly templates, then automation only after manual runs are stable.
- Files: `scripts/generate_health_report.py`, optional Codex automation prompt.
- Validation: two manual reports before scheduling.
- Risks: unattended noisy writes.
- Rollback: disable automation, keep manual command.
- Done: reports create reviewable findings.

Phase 7, hardening:
- Goals: prune and stabilize.
- Tasks: memory pruning, AGENTS slimming, skill trigger tuning, dashboards, rollback docs.
- Validation: fewer stale memories and fewer repeated failures.
- Risks: overfitting to last incident.
- Rollback: archive experimental rules.
- Done: system is smaller, not bigger.

## 10. Concrete File Tree

Use this target tree after MVP, adjusted to each repo:

```text
.
├── AGENTS.md
├── code_review.md
├── PLANS.md
├── docs/
│   ├── agentic-operating-system.md
│   ├── health-reports/
│   ├── decisions/
│   ├── failures/
│   ├── rejected-ideas/
│   ├── playbooks/
│   └── templates/
├── .agents/
│   ├── skill-registry.md
│   └── skills/
│       ├── failure-retrospective/SKILL.md
│       ├── health-report/SKILL.md
│       ├── idea-debate/SKILL.md
│       ├── agent-md-maintenance/SKILL.md
│       ├── semantic-memory-ingestion/SKILL.md
│       ├── eval-from-failure/SKILL.md
│       ├── codex-handoff/SKILL.md
│       ├── product-critique/SKILL.md
│       ├── implementation-plan/SKILL.md
│       └── docs-refactor/SKILL.md
├── .codex/
│   ├── config.toml
│   ├── agents/
│   └── rules/
├── memory/
│   ├── schemas/
│   ├── raw/
│   ├── processed/
│   ├── vector-index/
│   └── retrieval.md
├── evals/
│   ├── agent-behavior/
│   ├── failure-regressions/
│   └── skill-evals/
└── scripts/
    ├── ingest_memory.py
    ├── retrieve_memory.py
    ├── generate_health_report.py
    └── create_failure_eval.py
```

## 11. Concrete Starter Artifacts

`code_review.md`:

```md
# Code Review Guide

Review stance: find correctness, security, regression, maintainability, test, and product risks. Findings first. Cite files and lines. Ignore style nits unless they hide a real bug.

Severity:
- P0: data loss, security breach, production outage.
- P1: likely user-visible bug, failing critical path, serious missing test.
- P2: maintainability or edge-case risk worth fixing before merge.

Checklist:
- Does behavior match the request?
- Are tests meaningful?
- Are secrets safe?
- Is rollback clear?
- Are docs updated when behavior changed?
```

`PLANS.md`:

```md
# Plan Template

## Goal

## Context

## Constraints

## Files To Inspect

## Proposed Phases

## Tests And Validation

## Risks

## Rollback

## Done When
```

`.agents/skill-registry.md`:

```md
# Skill Registry

| Skill | Purpose | Owner | Version | Last reviewed | Eval prompt | Status |
| --- | --- | --- | --- | --- | --- | --- |
| failure-retrospective | Convert concrete failures into lessons and checks | human | 0.1 | 2026-06-07 | "Turn this failed test log into a lesson" | planned |
| health-report | Produce project health reports | human | 0.1 | 2026-06-07 | "Create weekly health report" | planned |
| idea-debate | Debate product/workflow ideas | human | 0.1 | 2026-06-07 | "Debate these 5 ideas" | planned |
```

Health report template:

```md
# Health Report: YYYY-MM-DD KIND

## Summary

## Scores

| Category | Score | Evidence | Next action |
| --- | ---: | --- | --- |

## Top 5 Risks

## Top 5 Improvements

## Repeated Failures

## Stale Decisions

## Rejected Ideas To Revisit

## Next Skill Candidate

## Next Eval Candidate

## Memory Updates Proposed

## Commands Run

## Blockers
```

Codex handoff template:

```md
# Codex Handoff

## Goal

## Current State

## Constraints

## Files To Inspect First

## Commands To Run

## Decisions Already Made

## Open Risks

## Done When

## Rollback

## Validation Gates
```

Weekly improvement loop:

```md
# Weekly Improvement Loop

1. Read latest health report.
2. Pick one repeated failure.
3. Pick one repeated manual workflow.
4. Pick one stale or bloated doc/rule.
5. Propose at most three durable changes.
6. For each: evidence, diff, validation, rollback.
7. Apply only approved changes.
8. Record outcome in next health report.
```

## 12. Commands And Validation

Initialize guidance:

```bash
mkdir -p docs/{health-reports,decisions,failures,rejected-ideas,playbooks,templates}
mkdir -p .agents/skills
mkdir -p memory/{schemas,raw,processed,vector-index}
mkdir -p evals/{agent-behavior,failure-regressions,skill-evals}
```

Discover project commands:

```bash
find . -maxdepth 3 -type f \( -name 'package.json' -o -name 'Makefile' -o -name 'pyproject.toml' -o -name 'Cargo.toml' -o -name '*.xcodeproj' -o -name '*.xcworkspace' \) -print
rg -n "test|lint|typecheck|build|dev|start" README.md docs .github package.json Makefile pyproject.toml 2>/dev/null
```

Current repo likely TODO commands:

```bash
# Project A test: TODO discover
# Project A lint: TODO discover
# Project A build: TODO discover
# Project B test: TODO discover
# Project B lint: TODO discover
# Project B build: TODO discover
```

Codex instruction verification:

```bash
codex --ask-for-approval never "Summarize the current instructions and list which AGENTS.md files loaded."
codex --cd . --ask-for-approval never "List active repo skills and their trigger descriptions."
```

Skill validation:

```bash
python3 /Users/himanshusharma/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/failure-retrospective
python3 /Users/himanshusharma/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/health-report
python3 /Users/himanshusharma/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/idea-debate
```

Memory ingestion after scripts exist:

```bash
python3 scripts/ingest_memory.py --source docs/failures --type failure --out memory/processed/failures.jsonl
python3 scripts/retrieve_memory.py --query "agent forgot to run tests after image generation workflow"
```

Health report after scripts exist:

```bash
python3 scripts/generate_health_report.py --kind weekly --project .
```

Eval commands after evals exist:

```bash
python3 scripts/create_failure_eval.py docs/failures/YYYY-MM-DD-slug.md
pytest evals/failure-regressions -q
```

Diff review:

```bash
git status --short
git diff -- AGENTS.md code_review.md PLANS.md .agents docs memory evals scripts
git diff --check
```

## 13. Strong Critique

Where this is over-engineered:
- Ten skills upfront is too many. Start with three.
- Custom agents for every role are unnecessary until manual role passes work.
- Hooks and automations can create invisible complexity.
- A vector DB before 100 curated memories is premature.

What should not be automated yet:
- AGENTS.md edits.
- Skill edits.
- Dependency changes.
- Releases, deploys, merge decisions.
- Memory ingestion from raw logs.
- Production credentials or infrastructure.

Memory garbage risks:
- Raw logs, duplicate incidents, speculative lessons, unreviewed opinions, old health noise.
- "User corrected me once" turned into global law.
- Vague rejected ideas without evidence.

AGENTS.md bloat risks:
- Adding every lesson to root rules.
- Repeating skill instructions inside AGENTS.
- Keeping project-specific detail at the shared root.

Ways agents get worse over time:
- Retrieval returns stale decisions without status.
- Skills over-trigger and override judgment.
- Health reports reward checklist volume over signal.
- Automations produce unaudited diffs.
- Too many roles create diffusion of responsibility.

Top 10 failure modes:
1. AGENTS.md becomes a junk drawer.
2. Skills trigger on adjacent tasks and waste context.
3. Memory index stores secrets or noisy logs.
4. Repeated failures are documented but not tested.
5. Health reports become performative.
6. Subagents edit overlapping files.
7. Automations run with too much access.
8. Decisions are never revisited.
9. Embedding retrieval cites obsolete guidance.
10. Humans stop reviewing durable-rule changes.

Human-owned:
- Product direction.
- Approval policy.
- Dependency and infra changes.
- Final merge/release.
- Brand and UX taste gates.
- Durable instruction changes.

Smallest useful version:
- One lean `AGENTS.md`.
- Three skills.
- One failure schema.
- One health report template.
- One retrieval prototype.
- One eval-from-failure loop.
- One idea debate workflow.

What Karpathy would simplify:
- Use files before platforms.
- Use JSONL before a database.
- Use one orchestrator before many agents.
- Use manual weekly reports before automations.
- Make every abstraction earn its keep.

What Codex best practices push:
- Put durable guidance in `AGENTS.md`.
- Turn repeated workflows into skills.
- Use sandbox and approvals deliberately.
- Use MCP for live external tools/context.
- Use worktrees for isolated parallel/background work.
- Validate with tests/review before completion.

## 14. Final Recommended MVP

MVP components:
- One root `AGENTS.md`.
- Three skills: failure-retrospective, health-report, idea-debate.
- One failure memory schema.
- One health report template.
- One semantic retrieval prototype.
- One eval-from-failure loop.
- One idea debate workflow.

7-day execution plan:

Day 1:
- Audit both repos.
- Write command map.
- Create baseline health report.
- Do not create skills yet unless repeated workflows are already known.

Day 2:
- Finalize lean root `AGENTS.md`.
- Add `code_review.md` and `PLANS.md`.
- Validate instruction loading.

Day 3:
- Create `failure-retrospective` skill.
- Run it on one real or recent failure.
- Save first failure memory.

Day 4:
- Create `health-report` skill and template.
- Produce first daily report manually.
- Identify top repeated failure and next eval candidate.

Day 5:
- Create `idea-debate` skill.
- Run debate on 5 candidate improvements.
- Reject/park/prototype with evidence.

Day 6:
- Implement memory MVP: JSONL schema plus brute-force retrieval over curated docs.
- Retrieve one known failure by paraphrase.
- Add citation rules to handoff template.

Day 7:
- Convert one failure into a test, eval, or checklist.
- Produce weekly health report.
- Propose at most three durable updates: one AGENTS rule, one skill improvement, one eval.
- Human reviews all durable changes.

The rule for week two: do not add the next seven skills until the first three have produced useful artifacts twice.
