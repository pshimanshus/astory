# Audits

A purpose audit answers one question per file: **does this file serve a real,
current purpose, or is it drift?**

For each file (or homogeneous family of files): stated purpose, observed reality,
verdict, action.

Verdicts:
- `keep` — serves its purpose, no change needed.
- `tighten` — right idea, weak or incomplete execution.
- `merge` — overlaps another file; should be consolidated.
- `delete` — dead, duplicated, or superseded.
- `fix` — actively wrong, or contradicts `AGENTS.md` / the references / the tests.

## Method

- Load-bearing and unique files get their own row.
- Large homogeneous families (template stubs, brain index `*.jsonl`, the 14
  persona files) are audited as a group with one row, and individual rows are
  broken out only for members that deviate from the family verdict. This is
  deliberate: 60 near-identical template stubs do not need 60 identical rows, and
  padding them would hide the few that actually matter.
- Binary data (images) is audited at the folder level, never per file.

## When to re-run

- After a major refactor lands.
- When `AGENTS.md`'s worldview changes.
- Quarterly, otherwise.
