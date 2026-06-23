# Retro

Run: `2026-06-19_21-09_ghar-line`

## Failure

The workflow let a bad prompt reach imagegen. Slide 1 asked for a soft/late smile and loaded a cafe identity reference that already contained the same smile, cup/table setup, jacket, and cafe composition. The resulting image copied the identity reference instead of rendering the intended ache.

## Creator Correction

The creator asked why the agents, reviewers, QA, and milestones approved something obviously wrong, and why the creator had to catch it at the end.

## Lesson

Approval artifacts are not approval. A gate passes only if it protects the creator from obvious failures.

For identity-sensitive A Story imagegen, raw references are dangerous when they overlap with the scene. "Use face only" in text is not enough if the visual input carries the exact pose, expression, wardrobe, and setting.

## Durable Rule

After any major creator visual correction, fallback local prompt-room passes cannot unlock imagegen. The run must either get fresh real review or stay as draft pending prompt lock.

Before imagegen, the coordinator must run two explicit checks:

- emotional-state contradiction;
- identity-reference pose/composition collision.

If either fails, block before generation.
