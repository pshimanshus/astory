# Creator Direction Notes

## 2026-06-18 — Route Passed But Rendered Faces Failed

Creator correction:
The generated test images still did not match Aachu/Zuv. Passing the reference
route, visibility proof, and gold-standard artifact gate is not enough if the
rendered faces are wrong.

Rejected assumption:
Do not treat "current-request image has `do_not_use_for: face_identity`" as
enough protection. The built-in imagegen tool can still visually absorb
source-illustration faces, hair, pose, wardrobe, and expression when those images
are loaded as active image inputs.

New active constraint:
For final identity-sensitive Aachu/Zuv imagegen, source/current-request
illustrations with visible non-Aachu/Zuv faces are analysis-only. Keep them in
`reference_groups.current_request`, raw queues, and binder packets for audit, but
exclude them from `active_view_image_queue` / `view_image_queue`. Translate their
scene, text, emotional premise, body logic, and broad composition into prompt
text instead.

Implementation response:
`scripts/prepare_imagegen_reference_context.py` now builds the active imagegen
queue from raw Aachu anchors, raw Zuv anchors, and style references only. A
regression test in `tests/test_imagegen_reference_context.py` verifies current
request images remain recorded but are not active imagegen inputs.
