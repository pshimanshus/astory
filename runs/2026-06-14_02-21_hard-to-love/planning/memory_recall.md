# Memory Recall

Run: `2026-06-14_02-21_hard-to-love`
Query: `hard to love concept no forced both people every slide native 1080x1080 brandmark best-illustration style references`

## Cited Findings

- Directly read `references/brain/pages/run-lessons.md`: concept screenshots should be treated as concept, mood, broad composition, text, and premise references only unless the creator explicitly promotes them to style references.
- Directly read `references/brain/pages/run-lessons.md`: do not default to repeated close-angle two-face sideways-looking compositions; prefer action-led staging, varied eyelines, and concrete behavior or objects carrying the proof.
- Directly read `references/brain/pages/run-lessons.md`: final A Story imagegen now requires native `1080x1080 px` square output in every prompt; wrong-size outputs are hard rejects, not resize/crop/pad tasks.
- Directly read `references/brain/pages/run-lessons.md`: identity reference angles are likeness cues only, not final pose or camera instructions.

## Retrieval Evidence

- `python3 scripts/astory_brain_cli.py doctor --repo-root .` returned blocked: missing citation paths for deleted identity README files and retrieval eval failures.
- `python3 scripts/astory_brain_cli.py index --repo-root . --output references/brain/index` completed.
- `python3 scripts/astory_brain_cli.py recall --index references/brain/index --query "hard to love concept no forced both people every slide native 1080x1080 brandmark best-illustration style references" --run-id 2026-06-14_02-21_hard-to-love --limit 8` returned no cited findings.

## Gaps

- Automated recall produced no run-specific cited results.
- Brain lint is currently failing due unrelated reference-path churn in the dirty worktree.

## Usability For This Run

Use current visible references, direct markdown evidence, and creator approvals only. Do not use automated brain claims as identity/style truth for this run.

