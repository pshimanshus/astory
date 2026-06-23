# A Story Repo QA Review

Run: `2026-06-11_23-45_reel-side-eye`
Overall status: `pass`

## Blocking Findings

- None.

## Reference Summary

- `aachu_face_identity_count`: `4`
- `zuv_face_identity_count`: `4`
- `expression_support_count`: `4`
- `together_body_language_count`: `2`
- `style_reference_count`: `3`
- `text_and_brand_reference_count`: `4`
- `view_image_queue_count`: `11`
- `view_image_queue_actual_count`: `11`
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
- `prompt_palette_conflict`: `pass` / `blocker`
- `prompt_overload`: `pass` / `blocker`
- `reference_visibility_proof`: `pass` / `blocker`
- `image_qa_blocks_final_package`: `pass` / `blocker` (`IMAGE_QA_FAILED`)
- `final_package_not_started`: `pass` / `blocker`
- `accepted_candidate_filename_guard`: `not_applicable` / `info`
- `generation_stops_after_hard_reject`: `pass` / `blocker`
- `prompt_repair_reapproval`: `pass` / `blocker`
- `trace_jsonl_valid`: `pass` / `blocker`
- `hitl_order_before_imagegen`: `pass` / `blocker`
- `agent_assignment_gate`: `pass` / `blocker`
- `approvals_cover_required_gates`: `pass` / `blocker`
- `local_identity_execution_report`: `not_applicable` / `info`
