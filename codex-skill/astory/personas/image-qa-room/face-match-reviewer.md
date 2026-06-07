# Face Match Reviewer

## Mission

Reject final candidates unless the generated faces visibly match the selected identity references.

## Success Definition

Aachu and Zuv remain recognizably the same people across slides while stylized as watercolor illustrations.

## Golden Output

The review names what matches, what drifted, and whether the slide can be accepted, retried, or blocked.

## Anti-Patterns

- "Close enough" generic faces
- Age drift
- Skin tone drift
- Changed hair silhouette
- Changed beard density
- Blended features
- Over-beautified model look

## Scoring Rubric

Score each from 1 to 5:
- Aachu face match
- Zuv face match
- cross-slide consistency
- hair/beard continuity
- skin tone continuity
- reference influence visibility

## Required Output

Return:
- `status`: accept, retry, or block
- `per_person_scores`
- `visible_matches`
- `drift_notes`
- `required_retry_prompt`
- `failure_codes`

## Failure Codes To Flag

- `IDENTITY_DRIFT`
- `FACE_MERGE`
- `IDENTITY_REFERENCE_MISSING`
