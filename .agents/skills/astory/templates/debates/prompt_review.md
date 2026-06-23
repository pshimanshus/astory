# Prompt QA Review

Run: `{{run_id}}`

## Agent Assignment Gate

- Assignment artifact: `{{agent_assignment_artifact}}`
- Assignment status: `actual_multi_agent|fallback_local_passes_with_limitation_recorded|missing`
- Gate decision: `pass|block`

## Identity Guardian

{{identity_guardian_notes}}

## Style Guardian

{{style_guardian_notes}}

## Scene Logic Critic

{{scene_logic_notes}}

## Creator Rejection Questions

- What would the creator immediately reject in this frame: `{{creator_reject_frame}}`
- Which loaded identity reference could imagegen copy too literally: `{{unsafe_identity_reference_risk}}`
- Does the face expression prove or betray the line: `{{face_expression_truth}}`

If any answer is empty, generic, or marked unsafe, the gate decision is `block`.

## Canvas And Brandmark Gate

- Every prompt includes native `1080x1350 px`: `pass|block`
- Every prompt includes tiny top-right `@a.storyof.two`: `pass|block`
- Every selected scene has concrete visual_setting_logic: `pass|block`

## Required Revisions

- {{revision}}

## Gate Decision

`pass|revise|block`
