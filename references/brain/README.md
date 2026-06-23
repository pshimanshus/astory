# A Story Brain

This folder is the canonical A Story brain layer.

- `pages/` contains compiled knowledge pages. These are source of truth.
- `schema/` defines the page taxonomy and migration contract.
- `policies/` contains memory-governance policy such as
  `policies/memory_autopilot.json`.
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
- `runs/<run_id>/memory/active_claims.md`
- `references/brain/ledger/events.jsonl`

For normal operation, prefer the autonomous post-run steward:

```bash
python3 scripts/astory_brain_cli.py autopilot --repo-root . --run-id <run_id> --phase post_run
```

The post-run autopilot extracts claims, applies
`references/brain/policies/memory_autopilot.json`, promotes safe workflow
lessons into cited canonical pages, defers high-risk identity/style/preference
claims, quarantines rejected-asset claims, rebuilds the index, runs lint/eval,
and rolls back any promotion that breaks verification.

The pre-imagegen phase is intentionally lightweight:

```bash
python3 scripts/astory_brain_cli.py autopilot --repo-root . --run-id <run_id> --phase pre_imagegen
```

That phase must not run learning, promotion, retrieval eval, or rollback loops.
It exists so `/astory` can prove autopilot will not add latency before
illustration generation or bypass the normal image gates.

## Claim Lifecycle

Learning writes claim snapshots into `runs/<run_id>/memory/claim_candidates.*`.
Those files are evidence queues. They are not canonical truth and are excluded
from runtime recall.

Effective claim states:

- `active_runtime`: auto-apply claim available to workflow behavior through
  `runs/<run_id>/memory/active_claims.md`.
- `candidate`: claim waiting for policy or review.
- `promoted`: reviewed or autopilot-approved claim written into
  `references/brain/pages/*`.
- `deferred`: claim intentionally held for repeated evidence.
- `rejected`: claim rejected as false, weak, stale, or no longer useful.
- `quarantined`: claim must not influence generation except as an explicit
  warning/failure mode.

Manual review remains available when needed:

```bash
python3 scripts/astory_brain_cli.py claims list --repo-root . --status open
python3 scripts/astory_brain_cli.py claims decide --repo-root . --claim-id claim:<id> --decision defer --reason "Need another approved run."
python3 scripts/astory_brain_cli.py claims decide --repo-root . --claim-id claim:<id> --decision promote --target-page references/brain/pages/run-lessons.md --reason "Explicit creator-approved workflow lesson."
```

Do not use run-level blockers from `scripts/astory_repo_qa.py --run-id <run_id>`
to judge whether the brain setup is ready. Repo QA is for an active creative
production run and intentionally checks unrelated gates such as reference
visibility proof, prompt-room agent proof, HITL order, image QA, and final
package readiness.
