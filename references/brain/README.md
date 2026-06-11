# A Story Brain

This folder is the canonical A Story brain layer.

- `pages/` contains compiled knowledge pages. These are source of truth.
- `schema/` defines the page taxonomy and migration contract.
- `index/` is derived cache. It can be deleted and rebuilt.
- `reports/` is derived diagnostic output.

Raw run folders, approvals, prompts, evals, and local references remain
canonical evidence. Brain pages may summarize them, but every current-truth
claim must cite a local source path.

## QA Scope

Use `python3 scripts/astory_brain_cli.py doctor --repo-root .` to validate this
memory setup. The doctor is scoped to `brain_setup`: schema, compiled pages,
derived index health, lint, and retrieval eval.

The doctor separates runtime readiness from learning governance. Runtime can be
`ready` while the learning pipeline is `operational_with_review_queue` if a run
has high-risk human-review or quarantine claims waiting for promotion decisions.
That is the expected safe operating mode: low-risk operational claims may be
auto-applied, while identity, style, and creator-preference claims stay out of
canonical brain pages until reviewed.

Use `python3 scripts/astory_brain_cli.py learn --repo-root . --run-id <run_id>
--write` after a run has meaningful eval/approval evidence. This writes:

- `runs/<run_id>/memory/claim_candidates.json`
- `runs/<run_id>/memory/claim_candidates.md`
- `references/brain/ledger/events.jsonl`

Do not use run-level blockers from `scripts/astory_repo_qa.py --run-id <run_id>`
to judge whether the brain setup is ready. Repo QA is for an active creative
production run and intentionally checks unrelated gates such as reference
visibility proof, prompt-room agent proof, HITL order, image QA, and final
package readiness.
