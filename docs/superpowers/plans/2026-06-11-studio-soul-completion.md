# Studio Soul Completion — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish the three things the persona-soul pass deliberately left untouched — align the `/astory` SKILL.md with the new cast and skill-routing, run a complete file-by-file purpose audit, and wire dynamic workflows/loops into one concrete, scheduled studio routine — so the whole system reads as one opinionated studio rather than a scaffold with souls bolted on.

**Architecture:** Three independent tracks. **Track B (audit)** is analysis-only and produces the substrate the others stand on, so it runs first. **Track A (SKILL.md alignment)** is a docs edit that makes the workflow doc point at the souls and the mandatory skill-routing. **Track C (dynamic loops)** is a small design doc plus one real wiring: a brain `learn`-after-run gate in SKILL.md and one ready-to-approve scheduled `/schedule` routine for a weekly studio health report. No production code changes the brain or QA scripts' behavior; this is wiring and documentation guarded by the existing 90-test suite.

**Tech Stack:** Markdown (skill, personas, AGENTS.md, audit docs), Python stdlib + `unittest` (existing test suite as the regression guard), the existing brain CLI (`scripts/astory_brain_cli.py`), the existing repo-QA script (`scripts/astory_repo_qa.py`), and Claude Code dynamic primitives (`/loop`, `ScheduleWakeup`, `/schedule`/`CronCreate`).

---

## Shared Constraints (read once, apply to every task)

- **Never break the contract.** Personas, templates, and references carry machine-readable fields the brain/pipeline parse. After any docs edit, the regression guard is:
  `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests` → must stay `OK` (currently 90 tests).
- **Evidence before "done."** Per Idris (the Principal Engineer persona), no task is complete until its verification command was run *in-session* and the output pasted. This is enforced by `superpowers:verification-before-completion`.
- **Tight diffs.** One track per branch/commit cluster. No drive-by edits to files outside the task's declared file list.
- **Names are working names.** Meera/Kabir/Tara/Dev/Nina/Arjun/Priya/Reza/Samar/Leela/Faiz/Maya/Vikram/Idris can be renamed; do not hardcode dependencies on the names anywhere a script reads.

## File Structure (what each track creates or modifies)

**Track A — SKILL.md alignment**
- Modify: `.agents/skills/astory/SKILL.md` — add a "Studio Mind & Cast" pointer, a skill-routing reminder, and per-room "become the persona" notes that match the dispatch packets.

**Track B — File-by-file purpose audit**
- Create: `docs/audits/2026-06-11-file-purpose-audit.md` — one row per repo file: stated purpose, does-it-serve-it verdict, action (keep / tighten / merge / delete / fix), owner.
- Create: `docs/audits/README.md` — what an audit is, when to re-run it.

**Track C — Dynamic workflows & loops**
- Create: `docs/playbooks/dynamic-loops.md` — maps each Claude dynamic primitive (`/loop`, `ScheduleWakeup`, `/schedule`/`CronCreate`, parallel `Agent`, `Monitor`) to a concrete use-case in this repo, with "use / don't use" rules.
- Modify: `.agents/skills/astory/SKILL.md` — promote brain `learn`-after-meaningful-run from a buried rule into an explicit post-run step with a self-paced loop option.
- Create: `docs/playbooks/weekly-studio-health.md` — the exact `/schedule` prompt for a weekly studio health report, ready for the creator to approve (creator-triggered; the plan does not auto-create the cron).

---

## Track B: File-by-File Purpose Audit (do first)

This is the substrate. It is analysis-only — it changes no behavior, only produces a judgment doc the creator stands on top of. It runs first because its findings may retarget Tracks A and C (e.g., if it finds ARCHITECTURE.md contradicts the new AGENTS.md, that becomes a Track A fix).

### Task B1: Scaffold the audit doc and scope

**Files:**
- Create: `docs/audits/README.md`
- Create: `docs/audits/2026-06-11-file-purpose-audit.md`

- [ ] **Step 1: Generate the authoritative file list to audit**

Run:
```bash
cd "/Users/himanshusharma/A Story of Two V2/" && \
find . -type f \
  -not -path './.git/*' -not -path './.remember/*' \
  -not -path './runs/*' -not -name '.DS_Store' \
  -not -name '*.pyc' -not -path '*/__pycache__/*' \
  -not -path './references/*/*.jpg' -not -path './references/*/*.png' \
  -not -path './references/*/*.jpeg' | sort
```
Expected: the list of source/doc/config/script/test files (images and run artifacts excluded — they are data, audited as folders, not per-file).

- [ ] **Step 2: Write `docs/audits/README.md`**

```markdown
# Audits

A purpose audit answers one question per file: **does this file serve a real,
current purpose, or is it drift?**

For each file: stated purpose, observed reality, verdict, action.

Verdicts: `keep` (serves its purpose), `tighten` (right idea, weak execution),
`merge` (overlaps another file), `delete` (dead/duplicated), `fix` (actively
wrong or contradicts AGENTS.md / the references / the tests).

Re-run a full audit when: a major refactor lands, AGENTS.md's worldview changes,
or quarterly. File images and `runs/` artifacts are audited at the folder level,
not per file.
```

- [ ] **Step 3: Create the audit doc skeleton with the section map**

```markdown
# File Purpose Audit — 2026-06-11

Auditor persona: Idris (Principal Engineer) + Vikram (Artifact Review Guardian).
Method: read each file, compare to its stated purpose and to AGENTS.md, the
`/astory` SKILL.md, the references, and the tests. Verdict + action per file.

## Summary
- Files audited: TBD-after-fill
- keep: _ / tighten: _ / merge: _ / delete: _ / fix: _
- Top 5 highest-leverage actions: (filled in Task B5)

## Root docs
| File | Stated purpose | Observed reality | Verdict | Action |
| --- | --- | --- | --- | --- |

## .agents/ (skill, personas, templates, agent config)
| File | Stated purpose | Observed reality | Verdict | Action |
| --- | --- | --- | --- | --- |

## scripts/ (brain, QA, pipelines)
| File | Stated purpose | Observed reality | Verdict | Action |
| --- | --- | --- | --- | --- |

## tests/
| File | Stated purpose | Observed reality | Verdict | Action |
| --- | --- | --- | --- | --- |

## docs/ (plans, sprints, scratchbooks, system design)
| File | Stated purpose | Observed reality | Verdict | Action |
| --- | --- | --- | --- | --- |

## references/ (folder-level: identity, style, wardrobe, places, brain, brand, text-style)
| Folder | Stated purpose | Observed reality | Verdict | Action |
| --- | --- | --- | --- | --- |
```

- [ ] **Step 4: Commit the scaffold**

```bash
git add docs/audits/README.md docs/audits/2026-06-11-file-purpose-audit.md
git commit -m "docs: scaffold file-purpose audit"
```

### Task B2: Audit root docs and `.agents/`

**Files:**
- Modify: `docs/audits/2026-06-11-file-purpose-audit.md`

- [ ] **Step 1: Read and judge every root doc**

Read each of: `README.md`, `ARCHITECTURE.md`, `ASSUMPTIONS.md`, `EVALS.md`,
`FAILURE_TAXONOMY.md`, `ROADMAP.md`, `RUNBOOK.md`, `AGENTS.md`.
For each, fill one table row. Specifically check:
- Does it contradict the new `AGENTS.md` studio mind? (e.g., `ARCHITECTURE.md`'s
  "Runtime Agents" list predates the engineering persona and the named cast →
  likely `fix`.)
- Does it still match reality? (e.g., `ARCHITECTURE.md`'s state machine is shorter
  than `SKILL.md`'s 32-state machine → likely `tighten` or `merge`.)

- [ ] **Step 2: Read and judge every file under `.agents/`**

Cover: `SKILL.md`, `agents/openai.yaml`, all 14 persona files, all `templates/**`
files, all `references/*.md`. For personas, the verdict is now mostly `keep`
(just soul-rewritten) — confirm each still carries its required-output schema.
For templates, check each is still referenced by SKILL.md or a script.

- [ ] **Step 3: Verify no doc edits leaked into source**

Run: `git status --short`
Expected: only `docs/audits/2026-06-11-file-purpose-audit.md` modified. If any
persona/template shows as modified, you edited instead of audited — revert it.

- [ ] **Step 4: Commit**

```bash
git add docs/audits/2026-06-11-file-purpose-audit.md
git commit -m "docs: audit root docs and .agents tree"
```

### Task B3: Audit `scripts/` and `tests/`

**Files:**
- Modify: `docs/audits/2026-06-11-file-purpose-audit.md`

- [ ] **Step 1: Map each script to its test and its caller**

Run:
```bash
cd "/Users/himanshusharma/A Story of Two V2/" && \
for m in scripts/astory_brain/*.py scripts/*.py; do \
  echo "### $m"; grep -rl "$(basename "$m" .py)" tests/ 2>/dev/null || echo "  (no test references basename)"; \
done
```
Expected: a basename→test map. A script with no test reference is a `tighten`
(needs coverage) or `delete` (dead) candidate — judge by whether SKILL.md or
another script imports it.

- [ ] **Step 2: Fill rows for every `scripts/**.py`**

For each of the 15 brain modules + 4 top-level scripts, record: what it does, who
calls it, is it tested, verdict. Flag any module that exists but is never imported
(e.g., confirm `autopilot.py`, `policy.py`, `promotion.py`, `claim_store.py` are
each reachable from the CLI subcommands `index/recall/lint/eval/learn/autopilot/claims/doctor`).

- [ ] **Step 3: Fill rows for every `tests/*.py`**

Record what behavior each test guards. Flag tests that duplicate coverage or test
nothing load-bearing.

- [ ] **Step 4: Confirm the suite still passes (nothing was touched)**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests`
Expected: `OK`, 90 tests.

- [ ] **Step 5: Commit**

```bash
git add docs/audits/2026-06-11-file-purpose-audit.md
git commit -m "docs: audit scripts and tests"
```

### Task B4: Audit `docs/` and `references/` (folder-level)

**Files:**
- Modify: `docs/audits/2026-06-11-file-purpose-audit.md`

- [ ] **Step 1: Judge each doc tree file**

Cover `docs/agentic-operating-system.md`, `docs/setup_status.md`, the 4 plans, the
2 scratchbooks, the sprints. Key check: does `agentic-operating-system.md`
(a design doc proposing `.codex/`, `memory/`, `evals/`, 10 skills) describe a
system that was *actually built*, or an aspiration? If aspiration, verdict is
`tighten` — mark which parts are real vs. proposed so future agents don't cite
unbuilt structure as truth.

- [ ] **Step 2: Judge each `references/` subtree at folder level**

For `identity/`, `style/`, `wardrobe/`, `places/`, `brain/`, `brand/`,
`text-style/`: confirm each has a README, each README matches the actual contents,
and the `brain/index/` + `brain/reports/` are flagged as derived cache (rebuildable),
per SKILL.md's "Brain Recall Gate".

- [ ] **Step 3: Commit**

```bash
git add docs/audits/2026-06-11-file-purpose-audit.md
git commit -m "docs: audit docs tree and references folders"
```

### Task B5: Synthesize findings

**Files:**
- Modify: `docs/audits/2026-06-11-file-purpose-audit.md`

- [ ] **Step 1: Fill the Summary block**

Count verdicts. Write the "Top 5 highest-leverage actions" — the five `fix`/`merge`/`delete`
items that most reduce drift (expected leaders: reconcile `ARCHITECTURE.md` with
`AGENTS.md`; mark aspirational sections of `agentic-operating-system.md`).

- [ ] **Step 2: Cross-link to the brain**

If the audit found a recurring drift pattern worth remembering, propose (do not
auto-apply) a brain page note via `scripts/astory_brain_cli.py` and record the
proposal in the audit doc's Summary. Do not silently write to compiled brain pages.

- [ ] **Step 3: Final regression check + commit**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests`
Expected: `OK`, 90 tests.
```bash
git add docs/audits/2026-06-11-file-purpose-audit.md
git commit -m "docs: synthesize file-purpose audit findings"
```

**Track B checkpoint:** Present the Summary + Top 5 actions to the creator. The
`fix` items become inputs to Track A and to a possible follow-up cleanup plan.

---

## Track A: SKILL.md Alignment With the Cast (do after B)

The `/astory` SKILL.md still describes rooms mechanically and never mentions the
souls or the mandatory skill-routing now in AGENTS.md. This track makes the
workflow doc point at the cast and the method, without changing the state machine
or any contract.

### Task A1: Add the Studio Mind & Cast pointer to SKILL.md

**Files:**
- Modify: `.agents/skills/astory/SKILL.md` (insert after the `## Operating Model` section, before `## Commands`)

- [ ] **Step 1: Insert the new section**

Add exactly:
```markdown
## Studio Mind & Cast

This skill runs inside the studio mind defined in `AGENTS.md`. Two rules from
there are binding inside every `/astory` run:

1. **We do not ship generic.** Every idea, beat, prompt, image, and line of code
   is judged against: *could a random competent LLM with no taste have produced
   this?* If yes, it fails, even if correct.
2. **Personas are people, not rubrics.** Before any room runs, load that room's
   persona files (`personas/<room>/*.md`) and *become* those people — their
   voice, taste, and "What I Refuse" lists are binding. The dispatch packets in
   `templates/agents/` carry the "Who You Are (Load This First)" injection; keep
   it when spawning agents.

Skill-routing inside a run (from AGENTS.md, mandatory):
- Idea/story/scene creative work → invoke `superpowers:brainstorming` first.
- Any code/test change to scripts or the brain → `superpowers:test-driven-development`.
- Any bug or surprising failure → `superpowers:systematic-debugging`.
- Before claiming a gate passed or a run is done → `superpowers:verification-before-completion`.
```

- [ ] **Step 2: Verify the insert didn't break the doc's structure**

Run: `grep -n '^## ' .agents/skills/astory/SKILL.md`
Expected: `## Studio Mind & Cast` appears once, between `## Operating Model` and
`## Commands`.

- [ ] **Step 3: Regression guard**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests`
Expected: `OK`, 90 tests (confirms no test parses SKILL.md in a way the edit broke).

- [ ] **Step 4: Commit**

```bash
git add .agents/skills/astory/SKILL.md
git commit -m "docs(skill): point /astory at the studio mind and cast"
```

### Task A2: Tag each Multi-Agent Room with its named cast

**Files:**
- Modify: `.agents/skills/astory/SKILL.md` (the `### Idea Room`, `### Story Room`, `### Prompt QA Room`, `### Image QA Room`, `### Review Room` headers under `## Multi-Agent Rooms`)

- [ ] **Step 1: Add a one-line cast roster under each room's `Spawn:` list**

For each room, immediately after its existing `Spawn:` bullet list, add a line of
the form (Idea Room shown; repeat the pattern per room with that room's people):
```markdown
Cast (become them, do not summarize them): Meera (Relatability Ethnographer),
Kabir (Shareability Strategist), Tara (Visual Story Director). Load
`personas/idea-room/*.md` before the room runs.
```
Story Room → Dev, Nina, Arjun (`personas/story-room/*.md`).
Prompt QA Room → Priya, Reza, Samar (`personas/prompt-room/*.md`).
Image QA Room → Leela, Faiz, Maya (`personas/image-qa-room/*.md`).
Review Room → Vikram (`personas/review-room/artifact-review-guardian.md`).

- [ ] **Step 2: Verify the role titles still match the personas (contract check)**

Run:
```bash
cd "/Users/himanshusharma/A Story of Two V2/" && \
grep -rl "Required Output" .agents/skills/astory/personas/ | wc -l
```
Expected: `13` (every creative persona still carries its Required Output contract;
the soul rewrite preserved it).

- [ ] **Step 3: Regression guard + commit**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests`
Expected: `OK`, 90 tests.
```bash
git add .agents/skills/astory/SKILL.md
git commit -m "docs(skill): name the cast in each multi-agent room"
```

**Track A checkpoint:** Show the creator the new SKILL.md sections; confirm the
voice/routing reads right before moving on.

---

## Track C: Dynamic Workflows & Loops (do last)

Design where Claude's dynamic primitives belong here, then wire exactly one real
recurring routine. Scope is deliberately small: a playbook + one SKILL.md gate +
one ready-to-approve schedule. No autonomous self-modification.

### Task C1: Write the dynamic-loops playbook

**Files:**
- Create: `docs/playbooks/dynamic-loops.md`

- [ ] **Step 1: Write the primitive→use-case map**

```markdown
# Dynamic Loops Playbook

Claude Code primitives, mapped to this repo. Use the smallest tool that fits.

| Primitive | What it is | Use it here for | Do NOT use for |
| --- | --- | --- | --- |
| `/loop` (self-paced) | Re-run a prompt/command until a condition holds | Driving `scripts/astory_repo_qa.py --run-id <id> --loop` to green-or-blocked on an active run | One-off tasks; anything with no clear stop condition |
| `ScheduleWakeup` | Re-invoke after a delay (same session intent) | Waiting on a long brain `index`/`learn` pass before continuing a run | Polling work the harness already notifies you about |
| `/schedule` (`CronCreate`) | Recurring cloud agent on a cron | Weekly studio health report (Task C3) | Anything that merges, deploys, or writes durable rules unattended |
| Parallel `Agent` dispatch | Fan out independent tracks | The Parallel Specialist Rule: impl / review / tests lanes | Tasks that share state or must be sequential |
| `Monitor` | Stream/watch a long command | Watching a long QA loop or test run | Short commands that just return |

## Rules
- A loop must have a stop condition: pass, max-iterations, or a real human/hard-gate blocker.
- Scheduled routines report and propose; they never cross a HITL gate or change
  durable rules (AGENTS.md, skills, brain pages) on their own.
- Prefer the existing bounded loop in `astory_repo_qa.py` over a free-running agent.
```

- [ ] **Step 2: Commit**

```bash
git add docs/playbooks/dynamic-loops.md
git commit -m "docs: dynamic-loops playbook mapping primitives to this repo"
```

### Task C2: Promote brain `learn`-after-run into an explicit SKILL.md step

**Files:**
- Modify: `.agents/skills/astory/SKILL.md` (the `## Brain Recall Gate` section already documents `learn`; add a sibling "after the run" step so it is not buried)

- [ ] **Step 1: Add a `## Post-Run Learning Loop` section after `## Brain Recall Gate`**

```markdown
## Post-Run Learning Loop

After a run reaches `COMPLETE_OR_BLOCKED` and has real eval/approval evidence,
run the learning pass so the studio gets smarter instead of relearning:

`python3 scripts/astory_brain_cli.py learn --repo-root . --run-id <run_id> --write`

This creates claim candidates and appends ledger events. It does NOT promote
high-risk identity/style/creator-preference claims into compiled brain pages —
those stay in the review queue (see `scripts/astory_brain_cli.py claims`).

Self-paced option: when several runs are pending learning, drive this with `/loop`
over the run ids rather than by hand. The loop's stop condition is "every run with
evidence has a ledger entry." It must never auto-promote queued high-risk claims.
```

- [ ] **Step 2: Verify brain CLI still exposes `learn` and `claims`**

Run: `python3 scripts/astory_brain_cli.py --help`
Expected: usage line lists `learn` and `claims` among the subcommands.

- [ ] **Step 3: Regression guard + commit**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests`
Expected: `OK`, 90 tests.
```bash
git add .agents/skills/astory/SKILL.md
git commit -m "docs(skill): add explicit post-run learning loop step"
```

### Task C3: Define the weekly studio health-report routine (creator approves)

**Files:**
- Create: `docs/playbooks/weekly-studio-health.md`

- [ ] **Step 1: Write the ready-to-approve schedule spec**

```markdown
# Weekly Studio Health Routine

The agentic-operating-system design describes a weekly health report but wires it
to nothing. This is the concrete, creator-approved version. It is creator-triggered:
the creator runs `/schedule` with the prompt below; agents do not self-create crons.

Cadence: weekly (e.g., Monday 09:00 local).

Schedule prompt:
> Produce this week's studio health report. Run the test suite
> (`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests`) and
> `python3 scripts/astory_brain_cli.py doctor --repo-root .`. Summarize: tests
> green/red, brain runtime + learning-queue status, runs added this week and which
> reached COMPLETE vs BLOCKED, top repeated failure codes from run traces, and the
> top 3 drift items still open from the latest `docs/audits/` file. Write the report
> to `docs/health-reports/YYYY-MM-DD-weekly.md`. PROPOSE at most 3 durable changes
> with evidence; do NOT apply them, do NOT cross any HITL gate, do NOT promote
> high-risk brain claims.

Stop/safety: report-and-propose only. The creator reviews every proposed durable
change. If tests are red, the report leads with that and proposes nothing else.
```

- [ ] **Step 2: Create the health-reports directory so the routine has a home**

Run: `mkdir -p "docs/health-reports" && touch "docs/health-reports/.gitkeep"`
Expected: directory exists.

- [ ] **Step 3: Commit**

```bash
git add docs/playbooks/weekly-studio-health.md docs/health-reports/.gitkeep
git commit -m "docs: define weekly studio health routine (creator-approved schedule)"
```

**Track C checkpoint:** Present the playbook + the schedule prompt. The creator
decides whether to run `/schedule` to actually create the weekly cron — this plan
stops at the ready-to-approve spec; it does not create the routine.

---

## Self-Review (run before declaring the plan done)

- **Spec coverage:** SKILL.md alignment → Track A (A1, A2). File-by-file audit →
  Track B (B1–B5). Dynamic workflows/loops → Track C (C1–C3). All three untouched
  items have tasks. ✓
- **Placeholder scan:** Every code/command step shows the exact command and
  expected output; markdown inserts show full text. The only intentional "TBD" is
  the audit's own Summary counts, which are filled in Task B5 by definition. ✓
- **Consistency:** The regression command
  (`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests` → `OK`, 90)
  is identical everywhere. Persona names match the cast written in the prior pass.
  Brain CLI subcommands (`learn`, `claims`, `doctor`) match the verified `--help`. ✓

## Suggested Order & Independence

- **B → A → C.** B is analysis-only and may retarget A/C. A and C both edit
  SKILL.md, so do not run them in parallel against the same file — sequence them.
- Each track is independently shippable: you can stop after B with a complete
  audit, after A with an aligned skill, or after C with the loops wired.
