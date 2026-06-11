# astory_orchestrator (Phase 0 — inspect-only)

Encodes the `/astory` 32-state workflow as **data** so the plan stops living in
the model's context.

- `spine.py` — the 32 states as an ordered, validated transition table. Kept in
  sync with `.agents/skills/astory/SKILL.md` by
  `tests/test_astory_orchestrator_spine.py`.
- `state.py` — `RunState`, persisted to `runs/<run_id>/state/run_state.json`.
- `../astory_orchestrator_cli.py` — `spine`, `validate-spine`, `init`, `status`.

## Status

Phase 0 is **inspect-only**. It does NOT run the workflow, dispatch agents,
enforce gates, or run loops. The live `/astory` skill is unchanged. Later phases
add the runner (loops + HITL halt/resume), gate enforcement, and dispatch packets.

## Try it

```bash
python3 scripts/astory_orchestrator_cli.py spine
python3 scripts/astory_orchestrator_cli.py validate-spine
```
