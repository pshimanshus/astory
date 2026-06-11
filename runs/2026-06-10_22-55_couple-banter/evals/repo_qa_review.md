# A Story Repo QA Review

Run: `2026-06-10_22-55_couple-banter`
Overall status: `blocked`

## Blocking Findings

- `image_qa_blocks_final_package` / `IMAGE_QA_BLOCKS_FINAL_PACKAGE_FAILED`: Failed Image QA is blocking final packaging.
- `final_package_not_started` / `FINAL_PACKAGE_STARTED_WHILE_BLOCKED`: Final Package gate remains not started while image QA is failed.

## Reference Summary

- `aachu_face_identity_count`: `4`
- `zuv_face_identity_count`: `4`
- `expression_support_count`: `4`
- `together_body_language_count`: `2`
- `style_reference_count`: `3`
- `text_and_brand_reference_count`: `4`
- `view_image_queue_count`: `19`
- `view_image_queue_actual_count`: `19`
- `prompt_only_allowed`: `False`

## Checks

- `skill_contract_present`: `pass` / `blocker`
- `master_prompt_present`: `pass` / `blocker`
- `required_templates_present`: `pass` / `blocker`
- `reference_manifest_integrity`: `pass` / `blocker`
- `prompt_story_contract`: `pass` / `blocker`
- `prompt_reference_gate`: `pass` / `blocker`
- `prompt_forbidden_role_reversal`: `pass` / `blocker`
- `reference_visibility_proof`: `pass` / `blocker`
- `image_qa_blocks_final_package`: `fail` / `blocker`
- `final_package_not_started`: `fail` / `blocker`
- `accepted_candidate_filename_guard`: `not_applicable` / `info`
- `trace_jsonl_valid`: `pass` / `blocker`
- `hitl_order_before_imagegen`: `pass` / `blocker`
- `agent_assignment_gate`: `pass` / `blocker`
- `approvals_cover_required_gates`: `pass` / `blocker`
- `local_identity_execution_report`: `not_applicable` / `info`
