# A Story Repo QA Review

Run: `2026-06-10_22-22_heart-rent`
Overall status: `blocked`

## Blocking Findings

- `memory_recall` / `MEMORY_RECALL_INVALID`: Memory recall contains cited findings, gaps, and usability notes.
- `prompt_canvas_size` / `PROMPT_CANVAS_SIZE_MISSING`: One or more imagegen prompts are missing the native 1080x1350 px portrait canvas gate.
- `prompt_brandmark_gate` / `PROMPT_BRANDMARK_MISSING`: One or more imagegen prompts are missing the top-right @a.storyof.two brandmark gate.
- `prompt_overload` / `PROMPT_OVERLOAD`: Prompt instruction stack is overloaded with too many competing constraints.
- `pre_imagegen_blocker_check` / `PRE_IMAGEGEN_BLOCKER_CHECK_MISSING`: Pre-imagegen blocker check artifact is required before imagegen.
- `reference_visibility_proof` / `REFERENCE_VISIBILITY_PROOF_STALE`: Reference visibility proof is stale for the current load plan.
- `gold_standard_identity_route_gate` / `GOLD_STANDARD_IDENTITY_ROUTE_MISSING`: Gold-standard identity route is incomplete; stop before imagegen/final progression.
- `final_package_has_illustration_proof` / `QUOTE_CARD_NOT_ILLUSTRATION`: Final packages must be A Story illustrations, not deterministic quote-card renders; require imagegen attempt, passing Image QA, and scene-proof artifacts.
- `novelty_candidate_ledger` / `NOVELTY_CANDIDATE_LEDGER_MISSING`: Novelty candidate ledger is missing or too incomplete before idea lock.
- `scene_landing_preview` / `SCENE_LANDING_MISSING`: Scene landing preview is missing or too abstract before idea lock.
- `agent_assignment_gate` / `AGENT_ASSIGNMENT_MISSING`: Agent assignment proof is incomplete before prompt lock or imagegen.

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
- `memory_recall`: `fail` / `blocker` (`MEMORY_RECALL_INVALID`)
- `prompt_story_contract`: `pass` / `blocker`
- `prompt_reference_gate`: `pass` / `blocker`
- `prompt_forbidden_role_reversal`: `pass` / `blocker`
- `prompt_canvas_size`: `fail` / `blocker` (`PROMPT_CANVAS_SIZE_MISSING`)
- `prompt_brandmark_gate`: `fail` / `blocker` (`PROMPT_BRANDMARK_MISSING`)
- `prompt_palette_conflict`: `pass` / `blocker`
- `prompt_overload`: `fail` / `blocker` (`PROMPT_OVERLOAD`)
- `pre_imagegen_blocker_check`: `fail` / `blocker` (`PRE_IMAGEGEN_BLOCKER_CHECK_MISSING`)
- `reference_visibility_proof`: `fail` / `blocker` (`REFERENCE_VISIBILITY_PROOF_STALE`)
- `gold_standard_identity_route_gate`: `fail` / `blocker` (`GOLD_STANDARD_IDENTITY_ROUTE_MISSING`)
- `image_qa_blocks_final_package`: `pass` / `blocker` (`IMAGE_QA_PENDING_CREATOR_APPROVAL`)
- `final_package_has_illustration_proof`: `fail` / `blocker` (`QUOTE_CARD_NOT_ILLUSTRATION`)
- `final_package_not_started`: `pass` / `blocker`
- `accepted_candidate_filename_guard`: `pass` / `blocker`
- `generation_stops_after_hard_reject`: `not_applicable` / `info`
- `prompt_repair_reapproval`: `not_applicable` / `info`
- `trace_jsonl_valid`: `pass` / `blocker`
- `novelty_candidate_ledger`: `fail` / `blocker` (`NOVELTY_CANDIDATE_LEDGER_MISSING`)
- `scene_landing_preview`: `fail` / `blocker` (`SCENE_LANDING_MISSING`)
- `source_winner_novelty_model`: `not_applicable` / `info`
- `hitl_order_before_imagegen`: `pass` / `blocker`
- `agent_assignment_gate`: `fail` / `blocker` (`AGENT_ASSIGNMENT_MISSING`)
- `approvals_cover_required_gates`: `pass` / `blocker`
- `local_identity_execution_report`: `not_applicable` / `info`
