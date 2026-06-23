# A Story Repo QA Review

Run: `2026-06-18_21-48_identity-route-redo-test`
Overall status: `pass`

## Blocking Findings

- None.

## Reference Summary

- `aachu_face_identity_count`: `6`
- `zuv_face_identity_count`: `6`
- `expression_support_count`: `4`
- `together_body_language_count`: `2`
- `style_reference_count`: `3`
- `text_and_brand_reference_count`: `4`
- `view_image_queue_count`: `15`
- `view_image_queue_actual_count`: `15`
- `prompt_only_allowed`: `False`

## Checks

- `skill_contract_present`: `pass` / `blocker`
- `master_prompt_present`: `pass` / `blocker`
- `required_templates_present`: `pass` / `blocker`
- `reference_manifest_integrity`: `pass` / `blocker`
- `reference_active_identity_inputs`: `pass` / `blocker`
- `memory_recall`: `pass` / `blocker`
- `prompt_story_contract`: `pass` / `blocker`
- `prompt_reference_gate`: `pass` / `blocker`
- `prompt_forbidden_role_reversal`: `pass` / `blocker`
- `prompt_canvas_size`: `pass` / `blocker`
- `prompt_brandmark_gate`: `pass` / `blocker`
- `prompt_palette_conflict`: `pass` / `blocker`
- `prompt_overload`: `pass` / `blocker`
- `reference_visibility_proof`: `pass` / `blocker`
- `gold_standard_identity_route_gate`: `pass` / `blocker`
- `image_qa_blocks_final_package`: `not_applicable` / `info`
- `final_package_has_illustration_proof`: `not_applicable` / `info`
- `final_package_not_started`: `pass` / `blocker`
- `accepted_candidate_filename_guard`: `not_applicable` / `info`
- `generation_stops_after_hard_reject`: `not_applicable` / `info`
- `prompt_repair_reapproval`: `not_applicable` / `info`
- `trace_jsonl_valid`: `pass` / `blocker`
- `scene_landing_preview`: `pass` / `blocker`
- `hitl_order_before_imagegen`: `pass` / `blocker`
- `agent_assignment_gate`: `pass` / `blocker`
- `approvals_cover_required_gates`: `pass` / `blocker`
- `local_identity_execution_report`: `not_applicable` / `info`
