# A Story Repo QA Review

Run: `2026-06-10_22-55_couple-banter`
Overall status: `blocked`

## Blocking Findings

- `memory_recall` / `MEMORY_RECALL_MISSING`: Memory recall artifact is missing for this run.
- `prompt_canvas_size` / `PROMPT_CANVAS_SIZE_MISSING`: One or more imagegen prompts are missing the native 1080x1350 px portrait canvas gate.
- `prompt_brandmark_gate` / `PROMPT_BRANDMARK_MISSING`: One or more imagegen prompts are missing the top-right @a.storyof.two brandmark gate.
- `prompt_overload` / `PROMPT_OVERLOAD`: Prompt instruction stack is overloaded with too many competing constraints.
- `reference_visibility_proof` / `REFERENCE_VISIBILITY_PROOF_STALE`: Reference visibility proof is stale for the current load plan.
- `gold_standard_identity_route_gate` / `GOLD_STANDARD_IDENTITY_ROUTE_MISSING`: Gold-standard identity route is incomplete; stop before imagegen/final progression.
- `scene_landing_preview` / `SCENE_LANDING_MISSING`: Scene landing preview is missing or too abstract before idea lock.

## Reference Summary

- `aachu_face_identity_count`: `6`
- `zuv_face_identity_count`: `6`
- `expression_support_count`: `4`
- `together_body_language_count`: `2`
- `style_reference_count`: `3`
- `text_and_brand_reference_count`: `4`
- `view_image_queue_count`: `17`
- `view_image_queue_actual_count`: `17`
- `prompt_only_allowed`: `False`

## Checks

- `skill_contract_present`: `pass` / `blocker`
- `master_prompt_present`: `pass` / `blocker`
- `required_templates_present`: `pass` / `blocker`
- `reference_manifest_integrity`: `pass` / `blocker`
- `reference_active_identity_inputs`: `pass` / `blocker`
- `memory_recall`: `blocked` / `blocker` (`MEMORY_RECALL_MISSING`)
- `prompt_story_contract`: `pass` / `blocker`
- `prompt_reference_gate`: `pass` / `blocker`
- `prompt_forbidden_role_reversal`: `pass` / `blocker`
- `prompt_canvas_size`: `fail` / `blocker` (`PROMPT_CANVAS_SIZE_MISSING`)
- `prompt_brandmark_gate`: `fail` / `blocker` (`PROMPT_BRANDMARK_MISSING`)
- `prompt_palette_conflict`: `pass` / `blocker`
- `prompt_overload`: `fail` / `blocker` (`PROMPT_OVERLOAD`)
- `reference_visibility_proof`: `fail` / `blocker` (`REFERENCE_VISIBILITY_PROOF_STALE`)
- `gold_standard_identity_route_gate`: `fail` / `blocker` (`GOLD_STANDARD_IDENTITY_ROUTE_MISSING`)
- `image_qa_blocks_final_package`: `pass` / `blocker` (`IMAGE_QA_FAILED`)
- `final_package_not_started`: `pass` / `blocker`
- `accepted_candidate_filename_guard`: `not_applicable` / `info`
- `generation_stops_after_hard_reject`: `not_applicable` / `info`
- `prompt_repair_reapproval`: `not_applicable` / `info`
- `trace_jsonl_valid`: `pass` / `blocker`
- `scene_landing_preview`: `fail` / `blocker` (`SCENE_LANDING_MISSING`)
- `hitl_order_before_imagegen`: `pass` / `blocker`
- `agent_assignment_gate`: `pass` / `blocker`
- `approvals_cover_required_gates`: `pass` / `blocker`
- `local_identity_execution_report`: `not_applicable` / `info`
