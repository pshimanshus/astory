# Runbook

## First-Time Setup

1. Add clean face identity images to `references/identity/aachu/face/` and `references/identity/zuv/face/`.
2. Add expression references to `references/identity/*/smiles/` and `references/identity/*/reactions/`.
3. Add couple references to `references/identity/together/face-and-body-language/` when available.
4. Add wardrobe/place support only to `references/wardrobe/` and `references/places/`; never use them as face identity refs.
5. Add approved style references to `references/style/`.
6. Review `references/identity/_dossier/identity-generation-preflight.md`, `references/text-style/README.md`, and `references/brand/README.md`.
7. Invoke `/astory setup` in Codex.

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
