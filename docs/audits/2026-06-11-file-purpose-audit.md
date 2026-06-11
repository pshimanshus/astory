# File Purpose Audit — 2026-06-11

Auditor persona: Idris (Principal Engineer) + Vikram (Artifact Review Guardian).
Method: read each file (or homogeneous family), compare to its stated purpose and
to `AGENTS.md`, the `/astory` `SKILL.md`, the references, and the tests. Verdict +
action per row. See `docs/audits/README.md` for verdict definitions and the
grouping method.

Scope: 152 per-file targets (md/py/json/jsonl/yaml/txt/tsv/config) + image folders
audited at folder level + `runs/` excluded (run artifacts, not source).

## Summary

- Files/families audited: _filled in B5_
- keep: _ / tighten: _ / merge: _ / delete: _ / fix: _
- Top 5 highest-leverage actions: _filled in B5_

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
| File | Stated purpose | Observed reality | Verdict | Action |
| --- | --- | --- | --- | --- |

## tests/
| File | Stated purpose | Observed reality | Verdict | Action |
| --- | --- | --- | --- | --- |

## docs/ — plans, sprints, scratchbooks, system design
| File | Stated purpose | Observed reality | Verdict | Action |
| --- | --- | --- | --- | --- |

## references/ — folder-level
| Folder | Stated purpose | Observed reality | Verdict | Action |
| --- | --- | --- | --- | --- |
