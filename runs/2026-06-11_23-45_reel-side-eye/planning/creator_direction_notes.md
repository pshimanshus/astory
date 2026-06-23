# Creator Direction Notes

Run: `2026-06-11_23-45_reel-side-eye`
Timestamp: `2026-06-13T12:49:56+05:30`

These notes are creator corrections that must be treated as active constraints
before any further prompt repair, imagegen, image QA, or final packaging for
this run.

## Active Correction: Identity Gate Failure Is A Workflow Failure

The creator challenged the repeated identity-gate failure after seeing the
slide 1 reel-side-eye candidate. The issue is not just that the image model made
bad faces. The workflow allowed weak identity proof to reach imagegen, then
treated reference visibility as stronger evidence than the generated face match.
The later `slide_01_4x5_attempt_02_candidate.png` was created after raw
reference visibility proof, but it was not recorded in `generation_attempts.json`
or as a `GENERATE_IMAGES_WITH_IMAGEGEN` trace event. That means the repaired
reference path still did not prove identity preservation, and attempt logging
also failed.

Rejected assumption:
- If references are listed, loaded, or visible, identity preservation is likely
  handled well enough to proceed.

Active constraint:
- Identity gate must judge the rendered candidate against Aachu/Zuv's actual
  face anchors, not only whether reference artifacts exist.
- A generated candidate with generic pretty faces, softened invented features,
  anime/cartoon drift, or model-beautified faces is a hard reject even if scene,
  text, wardrobe, and composition are strong.
- After the first identity hard reject, stop the batch. Do not continue to later
  slides before the reference delivery and prompt weighting are repaired.
- Post-repair raw-reference visibility proof is not evidence that earlier failed
  images used that repaired path. Time order must be preserved in the audit.
- Raw-reference visibility is still only an input proof. A post-repair candidate
  must be logged and reviewed as its own output; if the rendered faces are
  generic, the identity gate failed regardless of the reference proof.

Evidence:
- `runs/2026-06-11_23-45_reel-side-eye/images/slide_01_4x5_attempt_01_candidate.png`
- `runs/2026-06-11_23-45_reel-side-eye/images/slide_01_4x5_attempt_02_candidate.png`
- `runs/2026-06-11_23-45_reel-side-eye/images/generation_attempts.json`
- `runs/2026-06-11_23-45_reel-side-eye/evals/image_quality_eval.json`
- `runs/2026-06-11_23-45_reel-side-eye/evals/image_quality_report.md`
- `runs/2026-06-11_23-45_reel-side-eye/logs/trace.jsonl`
