# Idris Report - Principal Engineer

Inspected only. No files edited, no tests run.

## Existing Points

- The run brief already names the intended shape: winner-bank evidence first,
  novelty model second, backend matcher missing.
- The `/astory` skill already routes this through existing artifacts:
  `novelty_candidate_ledger`, `source_winner_remix_contract`,
  `source_winner_novelty_model`, `winner_landing_comparison`, and later
  alignment evals.
- The spine already declares the right artifact slots. No new state is needed.
- Repo QA already blocks missing or placeholder `novelty_candidate_ledger.json`
  and `source_winner_novelty_model.json`.
- The storytelling doc is properly subordinate to evidence: use the novelty
  framework after the evidence layer, not as a hook formula.

## Missing Piece

The missing slice is backend winner matching and evidence shaping.

`backend/app/data_refs.py` only loads the raw winner bank and returns a thin
summary. It drops the fields agents need to stay honest: source URL, account,
shortcode, rank, evidence paths, metric gaps, mechanic tags, comments,
public-vs-owned metric source, and enough communication seed to explain why a
winner worked.

Agents can fill the existing gates, but they still have to improvise matching.
That is the generic failure point.

## Proposed Shape

Smallest reversible implementation later:

- Keep existing gates. Do not add a new orchestrator state.
- Add a pure backend matcher, probably in `backend/app/data_refs.py` first
  unless it grows:
  - `load_winner_evidence(...)`
  - `match_winner_evidence(brief_text, records, limit=5, rank_by=...)`
- Return structured `WinnerEvidenceMatch` dictionaries with:
  - `source`: `source_url`, `source_account`, `source_shortcode`,
    `source_format`
  - `metrics`: likes/comments/views/winner score plus shares/saves/reach when
    actually available
  - `metric_gaps`: explicit unavailable fields
  - `evidence_paths`: raw bank/content-dump/export paths
  - `communication_seed`: hook/first line, mechanic tags, latest comment
    signal, send/save/comment proxy
  - `match`: score, reasons, risk flags
  - `novelty_seed`: old topic candidate, viewer outcome candidate, proof
    candidates, but not final prose
- Store matcher output inside existing `planning/novelty_candidate_ledger.json`
  under `source_bank_search.matches`, not a new gate artifact.
- Idea Room owns turning one match into `source_winner_remix_contract.json`.
- `CREATE_SCENE_LANDING_PREVIEW` owns `source_winner_novelty_model.json` and
  `winner_landing_comparison.md`.
- Repo QA remains validator, not generator.

## Test Plan

Next coding slice should be TDD and narrow:

- Backend unit tests with tiny fixture records:
  - preserves source URL/account/shortcode/evidence path;
  - ranks relevant source above irrelevant source;
  - does not invent shares/saves/reach for third-party bank records;
  - uses owned first-party metrics when present;
  - emits explicit metric gaps;
  - returns fields sufficient to fill
    `novelty_candidate_ledger.source_bank_search.matches`.
- Keep repo QA tests focused:
  - existing source-winner novelty model tests;
  - existing novelty ledger tests;
  - spine tests only if artifact declarations change, which should be avoided.
- Targeted commands later:
  - `python3 -m unittest backend/tests/test_data_refs.py -v`
  - `python3 -m unittest tests.test_astory_repo_qa tests.test_astory_orchestrator_spine -v`

## Risks

- Dirty tree is serious. `backend/app/data_refs.py`,
  `backend/tests/test_data_refs.py`, the novelty doc, source model template,
  and this run brief are untracked. `scripts/astory_repo_qa.py` and its tests
  are heavily modified. Do not casually overwrite.
- `scripts/astory_repo_qa.py` diff is large. Treat current behavior as
  working-tree truth, but implementation needs a clean review boundary.
- The normalized `references/text-style/research-bank/` artifact planned in
  docs is absent. Content dumps exist, so matcher should read current available
  sources or build deterministically, not assume the research bank exists.
- Third-party winner bank lacks true shares/saves/reach. Owned A Story exports
  have those metrics. Mixing them without `metric_source` and `metric_gaps`
  creates fake confidence.
- Current QA validates shape and completeness, not source consistency across
  ledger, remix contract, and novelty model. Do not add that gate in the first
  slice; stabilize backend evidence matching first.
