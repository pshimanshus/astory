# Memory Recall

## Cited Findings

- `references/brain/pages/run-lessons.md` records the 2026-06-18 lesson: contact sheets and a single best reference photo are not the identity mechanism; individual raw face anchors with multiple angles and expressions are.
- `.agents/skills/astory/references/master-prompt.md` records the gold-standard identity route: raw Aachu/Zuv anchors first, style refs second, and explicit blocking of single-anchor pose/expression copying.
- `.agents/skills/astory/references/imagegen-contract.md` requires `view_image` loading for every queued reference path and a current `imagegen_reference_visibility_proof.json` before imagegen.

## Gaps

- Generated image candidates are not yet face-match reviewed.
- The station source hides faces, so the test prompt must alter the pose enough to expose both identities.
- The standing source tempts copying posture and labels too literally, so the prompt must keep the joke while blocking source-pose cloning.

## Usability For This Run

Usable. The run has six raw Aachu face anchors and six raw Zuv face anchors across front, side, and three-quarter buckets, plus two current-request images and three style refs. This is sufficient for test generation after visibility proof and prompt QA pass.
