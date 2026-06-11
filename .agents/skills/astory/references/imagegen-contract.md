# Imagegen Contract

Use built-in Codex `imagegen` only. Do not ask for an OpenAI API key. Do not create a local image provider.

## Required Before Final Generation

1. Run `python3 scripts/prepare_imagegen_reference_context.py --run-id <run_id>` so the run has a machine-readable local reference manifest.
2. Make every local image in `evals/imagegen_reference_load_plan.json.view_image_queue` visible in the current conversation using `view_image`; the creator should not need to attach repo-local identity/style images manually.
3. Select style references or load the locked style rules.
4. Confirm exact on-image text.
5. Confirm native surface: 4:5 post or 9:16 story/reel.
6. Confirm prompt passed pre-generation QA.
7. Ask for HITL prompt approval.
8. Write `evals/imagegen_reference_visibility_proof.json` before calling `imagegen`.

If any queued local image cannot be read, or if the active generation path cannot use the loaded image context, mark the run blocked instead of generating final Aachu/Zuv artwork.

Before final imagegen, the Review Room must confirm:
- selected references are local, hashed, and role-separated;
- manual user attachment is not required for existing repo references;
- every face-visible prompt has Aachu and Zuv face identity references;
- every file in `view_image_queue` has been loaded through `view_image` in the current conversation.

## Generation Rhythm

- Generate one slide at a time.
- Save each candidate in `runs/<run_id>/images/`.
- Save accepted finals in `runs/<run_id>/exports/`.
- Log each generation attempt and decision.

## Retry Rule

Use targeted prompt repair. Do not rewrite the whole prompt randomly.

Retry up to 2 times per failure type. If identity cannot be preserved, mark blocked.
