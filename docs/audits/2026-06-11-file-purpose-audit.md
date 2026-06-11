# File Purpose Audit — 2026-06-11

Auditor persona: Idris (Principal Engineer) + Vikram (Artifact Review Guardian).
Method: read each file (or homogeneous family), compare to its stated purpose and
to `AGENTS.md`, the `/astory` `SKILL.md`, the references, and the tests. Verdict +
action per row. See `docs/audits/README.md` for verdict definitions and the
grouping method.

Scope: 152 per-file targets (md/py/json/jsonl/yaml/txt/tsv/config) + image folders
audited at folder level + `runs/` excluded (run artifacts, not source).

## Summary

Rows/families audited: **56** (152 per-file targets collapsed into families where
homogeneous; image folders + `runs/` audited at folder level).

Verdict tally:
- **keep: 41** — the spine is healthy. Personas (just ensouled), the brain layer,
  all scripts, all tests, the master prompt, and the reference folders serve their
  purpose. No `delete` found; nothing is dead.
- **tighten: 12** — mostly two patterns: (a) Codex-centric wording that predates
  the Claude+Codex shared mind, and (b) stale snapshots / aspirational docs.
- **fix: 3** — `ARCHITECTURE.md` (stale), and the split failure taxonomy
  (`FAILURE_TAXONOMY.md` + skill `references/failure-taxonomy.md`), counted once
  as fix and once as merge.
- **merge: 1** — the two failure taxonomies.
- **delete: 0**

**Headline read:** nothing here is broken or dead. The drift is *narrative*, not
structural — several docs describe a system that is either Codex-only or never
got built, while the real system (Claude+Codex shared mind, the brain, the QA
loop, the ensouled cast) has moved ahead of its own documentation. The risk is a
future agent trusting a stale doc over reality.

### Top 5 highest-leverage actions

1. **Reconcile `ARCHITECTURE.md` with reality** (fix). Its state machine is the
   old ~25-state version and its agent list omits the Review Room, the named
   cast, and the engineering crew — it now contradicts `AGENTS.md` and `SKILL.md`.
   Either sync it to SKILL.md's 32-state machine or demote it to "conceptual map —
   SKILL.md is canonical."
2. **Unify the failure taxonomy** (fix + merge). Make skill
   `references/failure-taxonomy.md` the single canonical list; have root
   `FAILURE_TAXONOMY.md` point to it. Add the missing `AGENT_ASSIGNMENT_MISSING`
   to the root copy and register the `REFERENCE_VISIBILITY_PROOF_*` codes that
   `imagegen-contract.md` and `astory_repo_qa.py` already emit but neither
   taxonomy declares.
3. **Banner `agentic-operating-system.md` as design-vision** (tighten). Add a
   header that the implemented memory system is the brain (`references/brain/` +
   `scripts/astory_brain/`), and that the `memory/`/vector-index/10-skill design
   below is partly unbuilt — so no agent cites unbuilt structure as truth.
4. **Decide the fate of `local_identity_pipeline.py`** (tighten). 2301 lines,
   fully tested, but orphaned from the live workflow (only plan docs reference
   it). Either wire it into `/astory` or relabel it as a retained proof-of-concept
   so its presence stops implying it's live.
5. **De-Codex the top docs** (tighten). `README.md`, `ASSUMPTIONS.md`,
   `RUNBOOK.md`, and one phrase in `house-style-contract.md` still say "Codex"
   where the system is now the Claude+Codex shared mind defined in `AGENTS.md`.

### Brain cross-link (proposed, not applied)

The recurring drift pattern — *docs describing a Codex-only or unbuilt system
while the real system moved ahead* — is worth remembering so future runs catch it
early. Proposed (do **not** auto-write to compiled brain pages): a `run-lessons`
note via `scripts/astory_brain_cli.py`, "Audit 2026-06-11: documentation drifts
behind the real system; treat `AGENTS.md` + `SKILL.md` + tests as truth over
narrative docs." Promotion stays a creator/review decision.

## Root docs
| File | Stated purpose | Observed reality | Verdict | Action |
| --- | --- | --- | --- | --- |
| `AGENTS.md` | Shared studio mind for Claude + Codex: worldview, cast, routing | Just rewritten this session; current spine | keep | none |
| `README.md` | Project overview / entry point for `/astory` | Accurate and thorough, but framed "Codex-native / Codex skill" throughout — predates the Claude+Codex shared mind | tighten | Reframe to the shared studio mind; replace "Codex skill" with "repo skill (Claude + Codex)" |
| `ARCHITECTURE.md` | Product shape, runtime agents, state machine, data flow | **Stale.** State machine is the old ~25-state version (missing `MEMORY_RECALL_PREFLIGHT`, `DISCOVER_AND_ASSIGN_AGENTS`, all `REVIEW_ROOM_*` states). "Runtime Agents" omits the Review Room, the named cast, and the engineering crew. Contradicts `AGENTS.md` and `SKILL.md` | fix | Reconcile state machine with SKILL.md's 32-state list; add Review Room + engineering crew; or demote to "conceptual map — SKILL.md is canonical" |
| `ASSUMPTIONS.md` | Base operating assumptions | Accurate, but Codex-centric ("Codex built-in imagegen") | tighten | De-Codex the wording to "built-in image tool"; otherwise keep |
| `EVALS.md` | Eval score scale, dimensions, thresholds | Current; matches the eval template families and SKILL.md thresholds | keep | Optional: cross-link to `templates/evals/*` so the dimensions stay in sync |
| `FAILURE_TAXONOMY.md` | Canonical failure codes | **Duplicate + drift.** Near-identical to `.agents/.../references/failure-taxonomy.md` but **missing `AGENT_ASSIGNMENT_MISSING`**; neither file lists the `REFERENCE_VISIBILITY_PROOF_*` codes used in the imagegen contract and repo QA | fix + merge | Pick one canonical taxonomy (the skill ref), have root point to it; add the missing visibility-proof codes |
| `ROADMAP.md` | V1/V2/V3 roadmap | Generic; does not reflect what was actually built (the brain, the dynamic QA loop, personas-with-soul) | tighten | Update to current reality, or mark items shipped/in-progress |
| `RUNBOOK.md` | Operator steps: setup, run, resume, audit | Accurate, but "Invoke `/astory setup` in Codex" is Codex-centric | tighten | De-Codex; otherwise keep |

## .agents/ — skill, personas, agent config
| File / family | Stated purpose | Observed reality | Verdict | Action |
| --- | --- | --- | --- | --- |
| `SKILL.md` | The `/astory` workflow: state machine, gates, rooms | Comprehensive and current, but does not yet reference the persona souls or the mandatory skill-routing | tighten | **Track A** adds the Studio Mind & Cast pointer + per-room cast tags |
| `agents/openai.yaml` | Codex skill-discovery manifest (display name, implicit invocation) | Valid; Codex-specific by design (Codex reads it for skill discovery) | keep | none |
| 14 persona files (`personas/**/*.md`) | Room personas (idea/story/prompt/image-qa/review) + engineering | Just rewritten with souls; all 13 creative files retain their `Required Output` JSON contract (verified); engineering persona added | keep | none |
| `references/master-prompt.md` | Canonical illustration prompt contract | Comprehensive, creator-locked v2; current | keep | none |
| `references/house-style-contract.md` | Style QA contract | Solid; one Codex-centric phrase ("visible to Codex") | keep | Minor: de-Codex the one phrase |
| `references/imagegen-contract.md` | Imagegen preconditions + Binder V2 + retry rule | Current and detailed, but uses `REFERENCE_VISIBILITY_PROOF_*` failure codes not registered in either taxonomy | tighten | Register those 3 codes in the canonical taxonomy |
| `references/failure-taxonomy.md` | Failure codes for evals/traces/reports | More complete than root copy (has `AGENT_ASSIGNMENT_MISSING`) but still missing the `REFERENCE_VISIBILITY_PROOF_*` codes | fix | Make this the single canonical taxonomy; add missing codes; root file points here |

## .agents/ — templates
| File / family | Stated purpose | Observed reality | Verdict | Action |
| --- | --- | --- | --- | --- |
| `templates/agents/*.md` (3 dispatch packets) | Agent dispatch prompts | Just enriched with the "Who You Are" identity injection | keep | none |
| `templates/planning/*`, `templates/debates/*`, `templates/evals/*`, `templates/reports/*`, `templates/docs/*`, `templates/prompts/*`, `templates/input/*`, `templates/logs/*` (≈44 files) | Canonical shapes for run artifacts | Reached via the `templates/**/*.{json,md,txt}` glob in "Required Resources" + filename convention against each room's Outputs list. Most map cleanly to a run artifact | keep | none (family) |
| `templates/debates/idea_debate_transcript.md` | Idea-room debate transcript shape | **Orphan suspect:** Idea Room artifacts list names `cross_critique.md` and `repair_round.md`, not `idea_debate_transcript.md`. No explicit reference found | tighten | Confirm against a real run; if unused, delete or wire into the Idea Room outputs |
| SKILL.md ↔ templates linkage | — | Only ~8 templates are named explicitly in SKILL.md; the other ~39 rely on glob + convention | tighten | (Track A) add a one-line note that the Outputs lists map to `templates/<area>/<same-name>` |

## scripts/ — brain modules + top-level scripts
Every brain module maps to a CLI subcommand or is a dependency of one, and every
script has a referencing test (verified). No dead modules.

| File | Stated purpose | Observed reality | Verdict | Action |
| --- | --- | --- | --- | --- |
| `astory_brain/models.py` (129) | Dataclasses for brain types | Clean; `test_astory_brain_models.py` | keep | none |
| `astory_brain/source_scan.py` (146) | Scan + hash canonical markdown sources | Used by indexer; tested via indexer | keep | none |
| `astory_brain/indexer.py` (191) | `index` subcommand — build chunks/links/sources/pages jsonl | Live; dedicated test | keep | none |
| `astory_brain/graph.py` (81) | Link graph over chunks | Used by retrieval; tested | keep | none |
| `astory_brain/retrieval.py` (203) | `recall` ranking | Live; dedicated test | keep | none |
| `astory_brain/synthesis.py` (84) | Synthesize recall into a result object | Live (`recall`); dedicated test | keep | none |
| `astory_brain/eval.py` (60) | `eval` — retrieval eval vs `tests/fixtures/brain/qrels.json` | Live; tested | keep | none |
| `astory_brain/lint.py` (217) | `lint` — brain page structure/citation checks | Live; dedicated test | keep | none |
| `astory_brain/learning.py` (378) | `learn` — extract report, write claim candidates + ledger | Live; dedicated test | keep | none |
| `astory_brain/policy.py` (30) | Load autopilot policy JSON | Live (`learn`/`autopilot`); tested | keep | none |
| `astory_brain/promotion.py` (46) | Claim promotion rules | Live; tested | keep | none |
| `astory_brain/claim_store.py` (222) | `claims list/decide` — claim queue store | Live; tested via autopilot | keep | none |
| `astory_brain/autopilot.py` (198) | `autopilot` — auto-apply low-risk claims | Live; dedicated test | keep | none |
| `astory_brain/page_store.py` (85) | Read/write compiled brain pages | Used by learning/promotion; dedicated test | keep | none |
| `astory_brain_cli.py` (398) | CLI entrypoint (index/recall/lint/eval/learn/autopilot/claims/doctor) | Clean dispatch; tested | keep | none |
| `prepare_imagegen_reference_context.py` (552) | Per-run reference manifest + Binder V2 | **Live** — referenced by SKILL.md, master-prompt, imagegen-contract; dedicated test | keep | none |
| `astory_repo_qa.py` (1609) | Repo-level run QA checks + bounded loop | Live and central; but **very large** for one file | tighten | Note only: consider splitting workflow-detection / checks / loop / reporting into modules if it grows again. Do not split now without need |
| `local_identity_pipeline.py` (2301) | Dry-run proof builder for local identity generation | **Orphaned from the live workflow** — not referenced by SKILL.md, AGENTS.md, README, or RUNBOOK; only by two plan docs. Has a test, so not dead. Largest file in the repo | tighten | Decide its fate: either wire it into the workflow, or move/label it as a retained proof-of-concept so future agents don't assume it's live |

## tests/
| File | Stated purpose | Observed reality | Verdict | Action |
| --- | --- | --- | --- | --- |
| `tests/test_astory_brain_*.py` (8 files) | Guard each brain module (models, indexer, retrieval, synthesis, learning, lint, page_store, autopilot) | One dedicated test per module; all pass | keep | none |
| `tests/test_astory_repo_qa.py` | Guard workflow classification + QA loop/blocker behavior | Guards the 1609-line QA script; passes | keep | none |
| `tests/test_imagegen_reference_context.py` | Guard run-aware reference selection + load-plan invariants | Guards the live binder script; passes | keep | none |
| `tests/test_local_identity_pipeline.py` | Guard the local identity pipeline | Keeps the orphaned 2301-line script green — coverage exists, but for a script the workflow doesn't call | keep | Revisit if the pipeline is retired (Action above) |
| `tests/fixtures/brain/qrels.json` | Retrieval eval gold set | Used by `eval`; current | keep | none |

## docs/ — plans, sprints, scratchbooks, system design
| File | Stated purpose | Observed reality | Verdict | Action |
| --- | --- | --- | --- | --- |
| `agentic-operating-system.md` | Shared agentic OS design (memory, skills, evals, health reports) | **Largely aspirational / superseded.** Proposes a `memory/` + vector-index (`text-embedding-3-small`) + `ingest_memory.py`/`retrieve_memory.py` + 10-skill architecture that was **not built as specified**. The real memory system (`references/brain/` + `scripts/astory_brain/`) is a different, better-fitted design (markdown pages + jsonl index + claim governance). Future agents could cite unbuilt structure as truth | tighten | Add a header banner: "design vision — the implemented memory system is the brain (`references/brain/`); sections below are partly unbuilt." Mark real-vs-proposed inline, or move to `docs/vision/` |
| `setup_status.md` | `/astory setup` gate result | Accurate as of 2026-06-08; correctly a point-in-time snapshot | keep | none (regenerated by `/astory setup`) |
| `scratchbooks/00-build-log.md` | Chronological build log | Historical record | keep | none |
| `scratchbooks/01-task-completion-audit.md` | Sprint completion status (2026-06-07) | Accurate at its date but stale (says "12 persona files"; now 14 with souls) | keep (historical) | Optional: add "snapshot — see git log for current state" note |
| `sprints/README.md` | Sprint-notes folder note | Accurate | keep | none |
| `sprints/2026-06-07-astory-granular-plan.md` | Original granular build plan | Historical plan | keep | none |
| `superpowers/plans/*.md` (6 plans) | Implementation plans (identity pipeline, brain, review loops, claim review, reference binder, studio-soul) | Historical + active record of planned/built work; includes this audit's parent plan | keep | none |

## references/ — folder-level
| Folder | Stated purpose | Observed reality | Verdict | Action |
| --- | --- | --- | --- | --- |
| `identity/` (aachu, zuv, together, current-request, `_dossier/`) | Face/identity anchors + operational dossier | README present; matches `setup_status.md` inventory; dossier drives generation recipe | keep | none |
| `style/observational-intimacy-premium/` | Approved house-style references | README + slides + contact sheet present | keep | none |
| `wardrobe/` (aachu, zuv, couple) | Wardrobe-only references | README present; role-separated from face anchors | keep | none |
| `places/` | Setting-only references | README present | keep | none |
| `brand/`, `text-style/` | Brand + handwritten-text rules | READMEs present | keep | none |
| `brain/` | Canonical memory layer (pages, schema, policies, index, reports, ledger) | **High quality.** README is current and correctly flags `index/` + `reports/` as derived cache (rebuildable); `pages/` (incl. `characters/`, `style/`) are source-of-truth with citation discipline | keep | none |
| `.carousel_research/` (65 jpg + `urls.tsv`) | Scraped competitor/brand carousel research | **Untracked** (git `??`); not referenced by SKILL.md or any script; informal research dump | tighten | Decide: commit as documented research, or add to `.gitignore`. Add a one-line README stating what it is and that it is not a runtime dependency |
