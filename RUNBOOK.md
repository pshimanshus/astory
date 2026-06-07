# Runbook

## First-Time Setup

1. Add identity images to `references/identity/aachu/` and `references/identity/zuv/`.
2. Add couple references to `references/identity/together/` when available.
3. Add approved style references to `references/style/`.
4. Review `references/text-style/README.md` and `references/brand/README.md`.
5. Invoke `/astory setup` in Codex.

## Production Run

Use one of:

```text
/astory <specific idea>
/astory theme: <theme>
/astory auto
```

Approve or revise at each HITL gate. Do not ask the system to skip identity/reference gates for final artwork.

## Resume

Use:

```text
/astory resume <run_id>
```

The orchestrator reads `runs/<run_id>/logs/trace.jsonl` and continues from the latest checkpoint.

## Audit

Use:

```text
/astory audit <run_id>
```

The audit checks required artifacts, hard failures, unresolved risks, and final package completeness.
