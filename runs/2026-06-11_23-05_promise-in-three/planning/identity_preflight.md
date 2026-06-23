# Identity Preflight

Run: `2026-06-11_23-05_promise-in-three`

## Status

Reference hard gate appears satisfiable for later final generation, but final imagegen has not started.

## Available Local References

- Aachu close face anchors exist under `references/identity/aachu/face/` with at least four curated files.
- Zuv close face anchors exist under `references/identity/zuv/face/` with at least four curated files.
- Couple/together references exist under `references/identity/together/`.
- Current-request identity folder exists but was not needed for this brief.

## Gate Notes

- Final Aachu/Zuv artwork cannot be generated from text-only identity descriptions.
- Before imagegen, `scripts/prepare_imagegen_reference_context.py --run-id 2026-06-11_23-05_promise-in-three` must create the selected reference manifest and load plan.
- Every queued reference image must be viewed with `view_image` and recorded in `evals/imagegen_reference_visibility_proof.json`.

## Current Limitation

The source screenshot is present in chat, not saved as a local project image. The creative brief records its observed concept, but final generation must rely on local Aachu/Zuv/style references rather than the competitor image.
