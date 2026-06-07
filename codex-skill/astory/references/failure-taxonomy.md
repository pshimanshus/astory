# Failure Taxonomy

Use these exact codes in evals, trace logs, reports, and blocked states.

- `IDENTITY_REFERENCE_MISSING`
- `IDENTITY_DRIFT`
- `FACE_MERGE`
- `STYLE_DRIFT`
- `YELLOW_PAPER_CAST`
- `TEXT_UNREADABLE`
- `TEXT_NOT_EXACT`
- `BRANDMARK_MISSING`
- `SCENE_LOGIC_CONTRADICTION`
- `ANATOMY_FAILURE`
- `WARDROBE_CONTINUITY_FAILURE`
- `GENERIC_IDEA`
- `WEAK_PAYOFF`
- `TOO_MANY_SLIDES`
- `TOO_FEW_SLIDES`
- `PROMPT_OVERLOAD`
- `HITL_NOT_APPROVED`
- `IMAGEGEN_TOOL_FAILURE`
- `ARTIFACT_MISSING`
- `DEBATE_COLLAPSE`
- `LOW_SCORE_NO_SELECTION`

Each failure record includes:
- stage
- severity
- failed gate
- likely cause
- attempted repair
- retry count
- final status
- prevention note
