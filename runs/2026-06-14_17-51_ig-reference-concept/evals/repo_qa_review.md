# A Story Repo QA Review

Run: `2026-06-14_17-51_ig-reference-concept`
Overall status: `blocked`

## Blocking Findings

- `reference_manifest_integrity` / `REFERENCE_MANIFEST_INVALID`: Selected reference manifest resolves to existing hashed references.
- `memory_recall` / `MEMORY_RECALL_TRACE_MISSING`: Memory recall contains cited findings, gaps, and usability notes.
- `prompt_story_contract` / `PROMPT_STORY_CONTRACT_MISMATCH`: Prompts preserve the run-specific locked story contract.
- `prompt_reference_gate` / `PROMPT_REFERENCE_GATE_MISSING`: Every prompt preserves the reference-image delivery gate.
- `prompt_canvas_size` / `PROMPT_CANVAS_SIZE_MISSING`: One or more imagegen prompts are missing the native 1080x1350 px portrait canvas gate.
- `gold_standard_identity_route_gate` / `GOLD_STANDARD_IDENTITY_ROUTE_MISSING`: Gold-standard identity route is incomplete; stop before imagegen/final progression.
- `image_qa_blocks_final_package` / `IMAGE_QA_BLOCKS_FINAL_PACKAGE_FAILED`: Image QA is blocking final packaging until creator approval.
- `final_package_has_illustration_proof` / `QUOTE_CARD_NOT_ILLUSTRATION`: Final packages must be A Story illustrations, not deterministic quote-card renders; require imagegen attempt, passing Image QA, and scene-proof artifacts.
- `final_package_not_started` / `FINAL_PACKAGE_STARTED_WHILE_BLOCKED`: Final Package gate remains not started while image QA is failed.
- `scene_landing_preview` / `SCENE_LANDING_MISSING`: Scene landing preview is missing or too abstract before idea lock.
- `hitl_order_before_imagegen` / `HITL_ORDER_BEFORE_IMAGEGEN_MISSING`: Idea, story, and prompt locks are recorded before image generation.
- `approvals_cover_required_gates` / `HITL_APPROVALS_INCOMPLETE`: Approvals file records required HITL gates and current stopped gates.

## Reference Summary

- `aachu_face_identity_count`: `4`
- `zuv_face_identity_count`: `4`
- `expression_support_count`: `4`
- `together_body_language_count`: `2`
- `style_reference_count`: `3`
- `text_and_brand_reference_count`: `4`
- `view_image_queue_count`: `12`
- `view_image_queue_actual_count`: `12`
- `prompt_only_allowed`: `False`

## Checks

- `skill_contract_present`: `pass` / `blocker`
- `master_prompt_present`: `pass` / `blocker`
- `required_templates_present`: `pass` / `blocker`
- `reference_manifest_integrity`: `fail` / `blocker`
- `reference_active_identity_inputs`: `pass` / `blocker`
- `memory_recall`: `fail` / `blocker` (`MEMORY_RECALL_TRACE_MISSING`)
- `prompt_story_contract`: `fail` / `blocker`
- `prompt_reference_gate`: `fail` / `blocker` (`PROMPT_REFERENCE_GATE_MISSING`)
- `prompt_forbidden_role_reversal`: `pass` / `blocker`
- `prompt_canvas_size`: `fail` / `blocker` (`PROMPT_CANVAS_SIZE_MISSING`)
- `prompt_brandmark_gate`: `pass` / `blocker`
- `prompt_palette_conflict`: `pass` / `blocker`
- `prompt_overload`: `pass` / `blocker`
- `reference_visibility_proof`: `pass` / `blocker`
- `gold_standard_identity_route_gate`: `fail` / `blocker` (`GOLD_STANDARD_IDENTITY_ROUTE_MISSING`)
- `image_qa_blocks_final_package`: `fail` / `blocker`
- `final_package_has_illustration_proof`: `fail` / `blocker` (`QUOTE_CARD_NOT_ILLUSTRATION`)
- `final_package_not_started`: `fail` / `blocker`
- `accepted_candidate_filename_guard`: `not_applicable` / `info`
- `generation_stops_after_hard_reject`: `not_applicable` / `info`
- `prompt_repair_reapproval`: `not_applicable` / `info`
- `trace_jsonl_valid`: `pass` / `blocker`
- `scene_landing_preview`: `fail` / `blocker` (`SCENE_LANDING_MISSING`)
- `hitl_order_before_imagegen`: `fail` / `blocker` (`HITL_ORDER_BEFORE_IMAGEGEN_MISSING`)
- `agent_assignment_gate`: `pass` / `blocker`
- `approvals_cover_required_gates`: `fail` / `blocker`
- `local_identity_execution_report`: `not_applicable` / `info`
