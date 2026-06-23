# A Story Repo QA Review

Run: `2026-06-19_23-10_next-carousel-recommendation`
Overall status: `blocked`

## Blocking Findings

- `reference_manifest_integrity` / `REFERENCE_MANIFEST_INVALID`: Selected reference manifest is missing or invalid.
- `reference_visibility_proof` / `REFERENCE_VISIBILITY_PROOF_REQUIRED_BEFORE_FINAL_IMAGEGEN`: Reference load plan requires a visibility proof before final imagegen; final generation remains blocked until it exists.
- `final_package_not_started` / `FINAL_PACKAGE_STARTED_WHILE_BLOCKED`: Final Package gate remains not started while image QA is failed.
- `hitl_order_before_imagegen` / `HITL_ORDER_BEFORE_IMAGEGEN_MISSING`: Idea, story, and prompt locks are recorded before image generation.
- `approvals_cover_required_gates` / `HITL_APPROVALS_INCOMPLETE`: Approvals file records required HITL gates and current stopped gates.

## Reference Summary

- `aachu_face_identity_count`: `0`
- `zuv_face_identity_count`: `0`
- `expression_support_count`: `0`
- `together_body_language_count`: `0`
- `style_reference_count`: `0`
- `text_and_brand_reference_count`: `0`
- `view_image_queue_count`: `0`
- `view_image_queue_actual_count`: `0`
- `prompt_only_allowed`: `None`

## Checks

- `skill_contract_present`: `pass` / `blocker`
- `master_prompt_present`: `pass` / `blocker`
- `required_templates_present`: `pass` / `blocker`
- `reference_manifest_integrity`: `fail` / `blocker`
- `reference_active_identity_inputs`: `not_applicable` / `info`
- `memory_recall`: `pass` / `blocker`
- `prompt_story_contract`: `not_applicable` / `info`
- `prompt_reference_gate`: `not_applicable` / `info`
- `prompt_forbidden_role_reversal`: `not_applicable` / `info`
- `prompt_canvas_size`: `not_applicable` / `info`
- `prompt_brandmark_gate`: `not_applicable` / `info`
- `prompt_palette_conflict`: `not_applicable` / `info`
- `prompt_overload`: `not_applicable` / `info`
- `reference_visibility_proof`: `fail` / `blocker` (`REFERENCE_VISIBILITY_PROOF_REQUIRED_BEFORE_FINAL_IMAGEGEN`)
- `gold_standard_identity_route_gate`: `not_applicable` / `info`
- `image_qa_blocks_final_package`: `not_applicable` / `info`
- `final_package_has_illustration_proof`: `not_applicable` / `info`
- `final_package_not_started`: `fail` / `blocker`
- `accepted_candidate_filename_guard`: `not_applicable` / `info`
- `generation_stops_after_hard_reject`: `not_applicable` / `info`
- `prompt_repair_reapproval`: `not_applicable` / `info`
- `trace_jsonl_valid`: `pass` / `blocker`
- `novelty_candidate_ledger`: `pass` / `blocker`
- `scene_landing_preview`: `pass` / `blocker`
- `source_winner_novelty_model`: `pass` / `blocker`
- `hitl_order_before_imagegen`: `fail` / `blocker` (`HITL_ORDER_BEFORE_IMAGEGEN_MISSING`)
- `agent_assignment_gate`: `not_applicable` / `info`
- `approvals_cover_required_gates`: `fail` / `blocker`
- `local_identity_execution_report`: `not_applicable` / `info`
