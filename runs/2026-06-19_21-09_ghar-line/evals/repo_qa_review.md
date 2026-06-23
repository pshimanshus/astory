# A Story Repo QA Review

Run: `2026-06-19_21-09_ghar-line`
Overall status: `blocked`

## Blocking Findings

- `pre_imagegen_blocker_check` / `PRE_IMAGEGEN_BLOCKER_CHECK_FAILED`: Pre-imagegen blocker check blocks imagegen until emotional, reference, fallback, prompt-lock, and canvas risks are cleared.
- `reference_visibility_proof` / `REFERENCE_VISIBILITY_PROOF_STALE`: Reference visibility proof is stale for the current load plan.
- `gold_standard_identity_route_gate` / `GOLD_STANDARD_IDENTITY_ROUTE_MISSING`: Gold-standard identity route is incomplete; stop before imagegen/final progression.

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
- `pre_imagegen_blocker_check`: `fail` / `blocker` (`PRE_IMAGEGEN_BLOCKER_CHECK_FAILED`)
- `reference_visibility_proof`: `fail` / `blocker` (`REFERENCE_VISIBILITY_PROOF_STALE`)
- `gold_standard_identity_route_gate`: `fail` / `blocker` (`GOLD_STANDARD_IDENTITY_ROUTE_MISSING`)
- `image_qa_blocks_final_package`: `pass` / `blocker` (`IMAGE_QA_FAILED`)
- `final_package_has_illustration_proof`: `not_applicable` / `info`
- `final_package_not_started`: `pass` / `blocker`
- `accepted_candidate_filename_guard`: `not_applicable` / `info`
- `generation_stops_after_hard_reject`: `pass` / `blocker`
- `prompt_repair_reapproval`: `not_applicable` / `info`
- `trace_jsonl_valid`: `pass` / `blocker`
- `novelty_candidate_ledger`: `pass` / `blocker`
- `scene_landing_preview`: `pass` / `blocker`
- `source_winner_novelty_model`: `pass` / `blocker`
- `hitl_order_before_imagegen`: `pass` / `blocker`
- `agent_assignment_gate`: `pass` / `blocker`
- `approvals_cover_required_gates`: `pass` / `blocker`
- `local_identity_execution_report`: `not_applicable` / `info`
