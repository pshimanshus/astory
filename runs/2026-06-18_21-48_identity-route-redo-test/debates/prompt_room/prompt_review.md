# Prompt Room Review

Run: `2026-06-18_21-48_identity-route-redo-test`

## Identity Guardian

Status before proof: `block`

The implementation route is correct: active imagegen inputs are raw individual Aachu/Zuv face anchors, not contact sheets or a single best image. The route was blocked until all queued references were loaded in the current conversation and a visibility proof existed.

Resolution: all 17 queued images were loaded with `view_image`, and `evals/imagegen_reference_visibility_proof.json` now records the exact load-plan hash and paths.

## Standing Banter

Status after revision: `pass_for_test_generation`

The standing source image is allowed only for story/composition essence: him listening, her mid-banter, labels, small speech bubbles. The prompt now explicitly prevents source-image identity, wardrobe, exact pose, head angle, expression lock, lighting, background, camera position, and scene composition from replacing raw anchors.

## Station Reunion

Status after revision: `pass_for_test_generation`

The original station source hides faces too much for this regression test. The prompt keeps the reunion premise but changes the action to the half-second after the first hug, with both faces open and front-three-quarter readable for identity comparison.

## Residual Risk

Imagegen can still drift after a valid route. Generated candidates must be reviewed for Aachu/Zuv face match, no feature merge, no single-anchor pose cloning, exact text, neutral paper, readable faces, natural hands, and top-right brandmark before any final package.
