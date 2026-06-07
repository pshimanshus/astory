# Failure Modes

Run: `2026-06-07_12-59-22_kitchen-help-dry-run`

| Code | Stage | Severity | Cause | Fix Attempted | Retry Count | Final Status | Prevention |
|---|---|---|---|---|---:|---|---|
| `IDENTITY_REFERENCE_MISSING` | `REFERENCE_PREFLIGHT` | hard gate | No Aachu/Zuv image files in V2 references | Planning-only dry run continued; imagegen skipped | 0 | blocked for imagegen | Add Aachu/Zuv identity images and rerun `/astory setup` |
| `STYLE_DRIFT` | `REFERENCE_PREFLIGHT` | medium | No approved style image references in V2 | Text style rules used for planning only | 0 | unresolved | Add approved style-lock images |
| `HITL_NOT_APPROVED` | `HITL_IDEA_LOCK` | expected | Dry run stopped before user approval | Selected idea recorded as pending | 0 | pending | Approve or revise selected idea in a real run |
