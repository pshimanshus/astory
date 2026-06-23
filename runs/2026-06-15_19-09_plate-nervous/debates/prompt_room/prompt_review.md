# Prompt Room Review

Run: `2026-06-15_19-09_plate-nervous`

## Identity Guardian / Priya

Status: `pass_with_risk`

- Identity reference paths: 4 raw Aachu face anchors and 4 raw Zuv face anchors from `runs/2026-06-15_19-09_plate-nervous/evals/imagegen_reference_load_plan.json`.
- Missing references: none for a face-visible generation.
- Prompt fixes applied: face anchors are highest priority; style/text descriptions are forbidden from replacing raw references; no generic "South Asian couple" shortcut.
- Residual risk: built-in imagegen prompt accepts text and visible context, but does not expose an explicit per-image input slot in the tool schema. This is recorded as an active limitation, not hidden.
- Failure codes if violated: `IDENTITY_REFERENCE_INPUT_UNPROVEN`, `IDENTITY_DRIFT`, `FACE_MERGE`.

## Style Guardian / Reza

Status: `pass`

- Style strengths: prompt uses native `1080x1080 px`, neutral white/off-white paper, hand-drawn integrated charcoal text, and tiny bottom-right brandmark.
- Style risks: style refs include some tan warmth; prompt explicitly rejects yellow, mustard, sepia, beige/tan, parchment, coffee-stained, and heavy cream cast.
- Failure codes if violated: `YELLOW_PAPER_CAST`, `STYLE_DRIFT`, `TEXT_NOT_EXACT`, `BRANDMARK_MISSING`.

## Scene Logic Critic / Samar

Status: `pass`

- Cover-the-text test: guarded plate + Zuv's betrayed eyeline should read as "he is about to steal from her plate" even without the text.
- Pose risks: hands must stay simple; Aachu holds plate close, Zuv keeps one phone hand and no actual stealing hand yet.
- Required scene fixes applied: one clear plate, no overcrowded gestures, no top-down identity-risk frame.
- Failure codes if violated: `SCENE_LOGIC_CONTRADICTION`, `ANATOMY_FAILURE`, `PROMPT_OVERLOAD`.
